import types
from dataclasses import fields, is_dataclass
from typing import Any, Type, TypeVar, get_origin, get_args, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Table

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


from .schemas import ConversionSchema, DEFAULT_CONVERSION_SCHEMA

def _convert_value(
    value: str, target_type: Type, schema: ConversionSchema = DEFAULT_CONVERSION_SCHEMA
) -> Any:
    """
    Converts a string value to the target type.
    Supports int, float, bool, str, and Optional types.
    """
    # Check custom converters first
    if target_type in schema.custom_converters:
        return schema.custom_converters[target_type](value)

    origin = get_origin(target_type)
    args = get_args(target_type)

    # Handle Optional[T] (Union[T, None])
    # Robust check for Union-like types
    if origin is not None and (origin is types.UnionType or "Union" in str(origin)):
        if type(None) in args:
            if not value.strip():
                return None
            # Find the non-None type
            for arg in args:
                if arg is not type(None):
                    return _convert_value(value, arg, schema)

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
        for true_val, false_val in schema.boolean_pairs:
            if lower_val == true_val.lower():
                return True
            if lower_val == false_val.lower():
                return False
                
        raise ValueError(f"Invalid boolean value: '{value}'")

    if target_type is str:
        return value

    # Fallback for other types (or if type hint is missing)
    return value


def validate_table(
    table: "Table",
    schema_cls: Type[T],
    conversion_schema: ConversionSchema = DEFAULT_CONVERSION_SCHEMA,
) -> list[T]:
    """
    Validates a Table object against a dataclass schema.

    Args:
        table: The Table object to validate.
        schema_cls: The dataclass type to validate against.
        conversion_schema: Configuration for type conversion.

    Returns:
        list[T]: A list of validated dataclass instances.

    Raises:
        ValueError: If schema_cls is not a dataclass.
        TableValidationError: If validation fails.
    """
    return results


# --- Pydantic Support (Optional) ---

try:
    from pydantic import BaseModel, ValidationError as PydanticValidationError
    HAS_PYDANTIC = True
except ImportError:
    BaseModel = None
    PydanticValidationError = None
    HAS_PYDANTIC = False


def _validate_table_pydantic(
    table: "Table",
    schema_cls: Type[BaseModel],
    conversion_schema: ConversionSchema,
) -> list[BaseModel]:
    """
    Validates a Table using Pydantic.
    """
    # Map headers to fields (checking aliases)
    model_fields = schema_cls.model_fields
    
    # helper: find field name by alias or name
    # Pydantic v2 stores alias in FieldInfo
    header_map: dict[int, str] = {}  # column_index -> field_name
    
    # Pre-calculate normalized map of field names/aliases
    # We map normalized_string -> key_to_use_in_dict
    lookup_map = {}
    
    for name, field_info in model_fields.items():
        # By default Pydantic expects the alias if it exists
        # UNLESS populate_by_name=True is set.
        # To be safe and support common case (headers match alias), we prioritize alias.
        
        # If alias is defined, map its normalized version to the ALIAS string
        if field_info.alias:
            lookup_map[_normalize_header(field_info.alias)] = field_info.alias
            
            # Also allow mapping field name if populate_by_name is likely?
            # But we can't easily know the config.
            # Let's support both: normalized(name) -> name 
            # But if collision? Alias usually wins in user intent.
            if _normalize_header(name) not in lookup_map:
                lookup_map[_normalize_header(name)] = name
        else:
            lookup_map[_normalize_header(name)] = name

    normalized_headers = [_normalize_header(h) for h in table.headers]

    for idx, header in enumerate(normalized_headers):
        if header in lookup_map:
            header_map[idx] = lookup_map[header]

    results = []
    errors = []

    for row_idx, row in enumerate(table.rows):
        row_data = {}
        for col_idx, cell_value in enumerate(row):
            if col_idx in header_map:
                target_key = header_map[col_idx]
                
                # Check for field-specific converter first (Library specific override)
                # But wait, field_converters uses field names? or aliases?
                # The user configures field_converters={"field_name": ...} or {"User Name": ...}?
                # existing validation.py logic uses `field_name` (the struct field).
                # But here `target_key` might be "User Name".
                # We should find the underlying field name for the converter check.
                
                # Reverse lookup for field name? 
                # This is getting complex. Simple solution:
                # If target_key matches a key in field_converters, use it.
                
                if target_key in conversion_schema.field_converters:
                    converter = conversion_schema.field_converters[target_key]
                    try:
                        val = converter(cell_value)
                        row_data[target_key] = val
                    except Exception as e:
                         errors.append(f"Row {row_idx + 1}: Column '{target_key}' conversion failed: {e}")
                else:
                    if cell_value.strip() == "":
                        row_data[target_key] = None
                    else:
                        row_data[target_key] = cell_value

        try:
            obj = schema_cls(**row_data)
            results.append(obj)
        except PydanticValidationError as e:
            # Format Pydantic errors nicely
            for err in e.errors():
                loc = ".".join(map(str, err["loc"]))
                msg = err["msg"]
                errors.append(f"Row {row_idx + 1}: Field '{loc}' - {msg}")

    if errors:
        raise TableValidationError(errors)

    return results


def _validate_table_dataclass(
    table: "Table",
    schema_cls: Type[T],
    conversion_schema: ConversionSchema,
) -> list[T]:
    """
    Validates a Table using standard dataclasses.
    """
    # Map headers to fields
    cls_fields = {f.name: f for f in fields(schema_cls)}
    header_map: dict[int, str] = {}  # column_index -> field_name

    normalized_headers = [_normalize_header(h) for h in table.headers]

    for idx, header in enumerate(normalized_headers):
        if header in cls_fields:
            header_map[idx] = header

    # Process rows
    results: list[T] = []
    errors: list[str] = []

    for row_idx, row in enumerate(table.rows):
        row_data = {}
        row_errors = []

        for col_idx, cell_value in enumerate(row):
            if col_idx in header_map:
                field_name = header_map[col_idx]
                field_def = cls_fields[field_name]

                try:
                    # Check for field-specific converter first
                    if field_name in conversion_schema.field_converters:
                        converter = conversion_schema.field_converters[field_name]
                        converted_value = converter(cell_value)
                    else:
                        converted_value = _convert_value(
                            cell_value, field_def.type, conversion_schema
                        )
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


def validate_table(
    table: "Table",
    schema_cls: Type[T],
    conversion_schema: ConversionSchema = DEFAULT_CONVERSION_SCHEMA,
) -> list[T]:
    """
    Validates a Table object against a dataclass OR Pydantic schema.

    Args:
        table: The Table object to validate.
        schema_cls: The dataclass or Pydantic model type to validate against.
        conversion_schema: Configuration for type conversion.

    Returns:
        list[T]: A list of validated instances.

    Raises:
        ValueError: If schema_cls is not a valid schema.
        TableValidationError: If validation fails.
    """
    # Check for Pydantic Model
    if HAS_PYDANTIC and issubclass(schema_cls, BaseModel):
        if not table.headers:
             raise TableValidationError(["Table has no headers"])
        return _validate_table_pydantic(table, schema_cls, conversion_schema)

    # Check for Dataclass
    if is_dataclass(schema_cls):
        if not table.headers:
             raise TableValidationError(["Table has no headers"])
        return _validate_table_dataclass(table, schema_cls, conversion_schema)

    raise ValueError(f"{schema_cls.__name__} must be a dataclass or Pydantic model")
