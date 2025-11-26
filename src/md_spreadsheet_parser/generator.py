from typing import TYPE_CHECKING
from .schemas import ParsingSchema, MultiTableParsingSchema, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from .models import Table, Sheet, Workbook


def generate_table_markdown(
    table: "Table", schema: ParsingSchema = DEFAULT_SCHEMA
) -> str:
    """
    Generates a Markdown string representation of the table.

    Args:
        table: The Table object.
        schema (ParsingSchema, optional): Configuration for formatting.

    Returns:
        str: The Markdown string.
    """
    lines = []

    # Handle metadata (name and description) if MultiTableParsingSchema
    if isinstance(schema, MultiTableParsingSchema):
        if table.name and schema.table_header_level is not None:
            lines.append(f"{'#' * schema.table_header_level} {table.name}")

        if table.description and schema.capture_description:
            lines.append(table.description)
            lines.append("")  # Empty line after description

    # Build table
    sep = f" {schema.column_separator} "

    # Headers
    if table.headers:
        # Add outer pipes if required
        header_row = sep.join(table.headers)
        if schema.require_outer_pipes:
            header_row = (
                f"{schema.column_separator} {header_row} {schema.column_separator}"
            )
        lines.append(header_row)

        # Separator row
        # Simple separator: ---
        # We could try to match column widths but for now simple is fine.
        separator_cells = [schema.header_separator_char * 3] * len(table.headers)
        separator_row = sep.join(separator_cells)
        if schema.require_outer_pipes:
            separator_row = (
                f"{schema.column_separator} {separator_row} {schema.column_separator}"
            )
        lines.append(separator_row)

    # Rows
    for row in table.rows:
        row_str = sep.join(row)
        if schema.require_outer_pipes:
            row_str = f"{schema.column_separator} {row_str} {schema.column_separator}"
        lines.append(row_str)

    return "\n".join(lines)


def generate_sheet_markdown(
    sheet: "Sheet", schema: ParsingSchema = DEFAULT_SCHEMA
) -> str:
    """
    Generates a Markdown string representation of the sheet.

    Args:
        sheet: The Sheet object.
        schema (ParsingSchema, optional): Configuration for formatting.

    Returns:
        str: The Markdown string.
    """
    lines = []

    if isinstance(schema, MultiTableParsingSchema):
        lines.append(f"{'#' * schema.sheet_header_level} {sheet.name}")
        lines.append("")

    for i, table in enumerate(sheet.tables):
        lines.append(generate_table_markdown(table, schema))
        if i < len(sheet.tables) - 1:
            lines.append("")  # Empty line between tables

    return "\n".join(lines)


def generate_workbook_markdown(
    workbook: "Workbook", schema: MultiTableParsingSchema
) -> str:
    """
    Generates a Markdown string representation of the workbook.

    Args:
        workbook: The Workbook object.
        schema (MultiTableParsingSchema): Configuration for formatting.

    Returns:
        str: The Markdown string.
    """
    lines = []

    if schema.root_marker:
        lines.append(schema.root_marker)
        lines.append("")

    for i, sheet in enumerate(workbook.sheets):
        lines.append(generate_sheet_markdown(sheet, schema))
        if i < len(workbook.sheets) - 1:
            lines.append("")  # Empty line between sheets
            lines.append("")

    return "\n".join(lines)
