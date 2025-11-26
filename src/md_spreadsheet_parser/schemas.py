from dataclasses import dataclass, fields, is_dataclass
from typing import Any, TypedDict, Type, TypeVar, get_origin, get_args, Union

T = TypeVar("T")


class TableValidationError(Exception):
    """
    Exception raised when table validation fails.
    Contains a list of errors found during validation.
    """

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(
            f"Validation failed with {len(errors)} errors:\n" + "\n".join(errors)
        )


def _normalize_header(header: str) -> str:
    """
    Normalizes a header string to match field names (lowercase, snake_case).
    Example: "User Name" -> "user_name"
    """
    return header.lower().replace(" ", "_").strip()


def _convert_value(value: str, target_type: Type) -> Any:
    """
    Converts a string value to the target type.
    Supports int, float, bool, str, and Optional types.
    """
    origin = get_origin(target_type)
    args = get_args(target_type)

    # Handle Optional[T] (Union[T, None])
    # In Python 3.10+, X | Y is types.UnionType, not typing.Union
    is_union = origin is Union or str(origin) == "<class 'types.UnionType'>"

    if is_union and type(None) in args:
        if not value.strip():
            return None
        # Find the non-None type
        for arg in args:
            if arg is not type(None):
                return _convert_value(value, arg)

    # Handle basic types
    if target_type is int:
        if not value.strip():
            raise ValueError("Empty value for int field")
        return int(value)

    if target_type is float:
        if not value.strip():
            raise ValueError("Empty value for float field")
        return float(value)

    if target_type is bool:
        lower_val = value.lower().strip()
        if lower_val in ("true", "yes", "1", "on"):
            return True
        if lower_val in ("false", "no", "0", "off", ""):
            return False
        raise ValueError(f"Invalid boolean value: '{value}'")

    if target_type is str:
        return value

    # Fallback for other types (or if type hint is missing)
    return value


@dataclass(frozen=True)
class ParsingSchema:
    """
    Configuration for parsing markdown tables.
    Designed to be immutable and passed to pure functions.

    Attributes:
        column_separator (str): Character used to separate columns. Defaults to "|".
        header_separator_char (str): Character used in the separator row. Defaults to "-".
        require_outer_pipes (bool): Whether tables must have outer pipes (e.g. `| col |`). Defaults to False.
        strip_whitespace (bool): Whether to strip whitespace from cell values. Defaults to True.
    """

    column_separator: str = "|"
    header_separator_char: str = "-"
    require_outer_pipes: bool = False
    strip_whitespace: bool = True


# Default schema for standard Markdown tables (GFM style)
DEFAULT_SCHEMA = ParsingSchema()


class TableJSON(TypedDict):
    """
    JSON-compatible dictionary representation of a Table.
    """

    name: str | None
    description: str | None
    headers: list[str] | None
    rows: list[list[str]]
    metadata: dict[str, Any]


class SheetJSON(TypedDict):
    """
    JSON-compatible dictionary representation of a Sheet.
    """

    name: str
    tables: list[TableJSON]


class WorkbookJSON(TypedDict):
    """
    JSON-compatible dictionary representation of a Workbook.
    """

    sheets: list[SheetJSON]


@dataclass(frozen=True)
class Table:
    """
    Represents a parsed table with optional metadata.

    Attributes:
        headers (list[str] | None): List of column headers, or None if the table has no headers.
        rows (list[list[str]]): List of data rows.
        name (str | None): Name of the table (e.g. from a header). Defaults to None.
        description (str | None): Description of the table. Defaults to None.
        metadata (dict[str, Any] | None): Arbitrary metadata. Defaults to None.
    """

    headers: list[str] | None
    rows: list[list[str]]
    name: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metadata is None:
            # Hack to allow default value for mutable type in frozen dataclass
            object.__setattr__(self, "metadata", {})

    @property
    def json(self) -> TableJSON:
        """
        Returns a JSON-compatible dictionary representation of the table.

        Returns:
            TableJSON: A dictionary containing the table data.
        """
        return {
            "name": self.name,
            "description": self.description,
            "headers": self.headers,
            "rows": self.rows,
            "metadata": self.metadata if self.metadata is not None else {},
        }

    def to_models(self, schema_cls: Type[T]) -> list[T]:
        """
        Converts the table rows into a list of dataclass instances, performing validation and type conversion.

        Args:
            schema_cls (Type[T]): The dataclass type to validate against.

        Returns:
            list[T]: A list of validated dataclass instances.

        Raises:
            ValueError: If schema_cls is not a dataclass.
            TableValidationError: If validation fails for any row or if the table has no headers.
        """
        if not is_dataclass(schema_cls):
            raise ValueError(f"{schema_cls.__name__} must be a dataclass")

        if not self.headers:
            raise TableValidationError(["Table has no headers"])

        # Map headers to fields
        cls_fields = {f.name: f for f in fields(schema_cls)}
        header_map: dict[int, str] = {}  # column_index -> field_name

        normalized_headers = [_normalize_header(h) for h in self.headers]

        for idx, header in enumerate(normalized_headers):
            if header in cls_fields:
                header_map[idx] = header

        # Process rows
        results: list[T] = []
        errors: list[str] = []

        for row_idx, row in enumerate(self.rows):
            row_data = {}
            row_errors = []

            for col_idx, cell_value in enumerate(row):
                if col_idx in header_map:
                    field_name = header_map[col_idx]
                    field_def = cls_fields[field_name]

                    try:
                        converted_value = _convert_value(cell_value, field_def.type)
                        row_data[field_name] = converted_value
                    except ValueError as e:
                        row_errors.append(f"Column '{field_name}': {str(e)}")
                    except Exception:
                        row_errors.append(
                            f"Column '{field_name}': Failed to convert '{cell_value}' to {field_def.type}"
                        )

            if row_errors:
                for err in row_errors:
                    errors.append(f"Row {row_idx + 1}: {err}")
                continue

            try:
                obj = schema_cls(**row_data)
                results.append(obj)
            except TypeError as e:
                # This catches missing required arguments
                errors.append(f"Row {row_idx + 1}: {str(e)}")

        if errors:
            raise TableValidationError(errors)

        return results


@dataclass(frozen=True)
class Sheet:
    """
    Represents a single sheet containing tables.

    Attributes:
        name (str): Name of the sheet.
        tables (list[Table]): List of tables contained in this sheet.
    """

    name: str
    tables: list[Table]

    @property
    def json(self) -> SheetJSON:
        """
        Returns a JSON-compatible dictionary representation of the sheet.

        Returns:
            SheetJSON: A dictionary containing the sheet data.
        """
        return {"name": self.name, "tables": [t.json for t in self.tables]}

    def get_table(self, name: str) -> Table | None:
        """
        Retrieve a table by its name.

        Args:
            name (str): The name of the table to retrieve.

        Returns:
            Table | None: The table object if found, otherwise None.
        """
        for table in self.tables:
            if table.name == name:
                return table
        return None


@dataclass(frozen=True)
class Workbook:
    """
    Represents a collection of sheets (multi-table output).

    Attributes:
        sheets (list[Sheet]): List of sheets in the workbook.
    """

    sheets: list[Sheet]

    @property
    def json(self) -> WorkbookJSON:
        """
        Returns a JSON-compatible dictionary representation of the workbook.

        Returns:
            WorkbookJSON: A dictionary containing the workbook data.
        """
        return {"sheets": [s.json for s in self.sheets]}

    def get_sheet(self, name: str) -> Sheet | None:
        """
        Retrieve a sheet by its name.

        Args:
            name (str): The name of the sheet to retrieve.

        Returns:
            Sheet | None: The sheet object if found, otherwise None.
        """
        for sheet in self.sheets:
            if sheet.name == name:
                return sheet
        return None


@dataclass(frozen=True)
class MultiTableParsingSchema(ParsingSchema):
    """
    Configuration for parsing multiple tables (workbook mode).
    Inherits from ParsingSchema.

    Attributes:
        root_marker (str): The marker indicating the start of the data section. Defaults to "# Tables".
        sheet_header_level (int): The markdown header level for sheets. Defaults to 2 (e.g. `## Sheet`).
        table_header_level (int | None): The markdown header level for tables. If None, table names are not extracted. Defaults to None.
        capture_description (bool): Whether to capture text between the table header and the table as a description. Defaults to False.
    """

    root_marker: str = "# Tables"
    sheet_header_level: int = 2
    table_header_level: int | None = None
    capture_description: bool = False
