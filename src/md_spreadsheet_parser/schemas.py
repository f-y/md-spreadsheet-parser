from dataclasses import dataclass
from typing import Any, TypedDict


@dataclass(frozen=True)
class ParsingSchema:
    """
    Configuration for parsing markdown tables.
    Designed to be immutable and passed to pure functions.
    """

    column_separator: str = "|"
    header_separator_char: str = "-"
    require_outer_pipes: bool = False
    strip_whitespace: bool = True

    # Future extensibility:
    # quote_char: str | None = None
    # escape_char: str | None = "\\"


@dataclass(frozen=True)
class ParseResult:
    """
    Structured result of the parsing operation.
    """

    headers: list[str] | None
    rows: list[list[str]]
    metadata: dict[str, Any]


# Default schema for standard Markdown tables (GFM style)
DEFAULT_SCHEMA = ParsingSchema()


class TableJSON(TypedDict):
    name: str | None
    description: str | None
    headers: list[str] | None
    rows: list[list[str]]
    metadata: dict[str, Any]


class SheetJSON(TypedDict):
    name: str
    tables: list[TableJSON]


class WorkbookJSON(TypedDict):
    sheets: list[SheetJSON]


@dataclass(frozen=True)
class Table:
    """
    Represents a parsed table with optional metadata.
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
        return {
            "name": self.name,
            "description": self.description,
            "headers": self.headers,
            "rows": self.rows,
            "metadata": self.metadata if self.metadata is not None else {},
        }


@dataclass(frozen=True)
class Sheet:
    """
    Represents a single sheet containing tables.
    """

    name: str
    tables: list[Table]

    @property
    def json(self) -> SheetJSON:
        return {"name": self.name, "tables": [t.json for t in self.tables]}

    def get_table(self, name: str) -> Table | None:
        """
        Retrieve a table by its name. Returns None if not found.
        """
        for table in self.tables:
            if table.name == name:
                return table
        return None


@dataclass(frozen=True)
class Workbook:
    """
    Represents a collection of sheets (multi-table output).
    """

    sheets: list[Sheet]

    @property
    def json(self) -> WorkbookJSON:
        return {"sheets": [s.json for s in self.sheets]}

    def get_sheet(self, name: str) -> Sheet | None:
        """
        Retrieve a sheet by its name. Returns None if not found.
        """
        for sheet in self.sheets:
            if sheet.name == name:
                return sheet
        return None


@dataclass(frozen=True)
class MultiTableParsingSchema(ParsingSchema):
    """
    Configuration for parsing multiple tables (workbook mode).
    """

    root_marker: str = "# Tables"
    sheet_header_level: int = 2  # e.g. ## SheetName
    table_header_level: int | None = None  # e.g. ### TableName
    capture_description: bool = False
