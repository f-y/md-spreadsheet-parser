import re
from dataclasses import replace

from .models import Table, Workbook, Sheet
from .schemas import ParsingSchema, MultiTableParsingSchema, DEFAULT_SCHEMA


def clean_cell(cell: str, schema: ParsingSchema) -> str:
    """
    Clean a cell value by stripping whitespace and unescaping the separator.
    """
    if schema.strip_whitespace:
        cell = cell.strip()

    # Unescape the column separator (e.g. \| -> |)
    # We also need to handle \\ -> \
    # Simple replacement for now: replace \<sep> with <sep>
    if "\\" in cell:
        cell = cell.replace(f"\\{schema.column_separator}", schema.column_separator)

    return cell


def parse_row(line: str, schema: ParsingSchema) -> list[str] | None:
    """
    Parse a single line into a list of cell values.
    Handles escaped separators.
    """
    line = line.strip()
    if not line:
        return None

    # Use regex to split by separator, but ignore escaped separators.
    # Pattern: (?<!\\)SEPARATOR
    # We must escape the separator itself for regex usage.
    sep_pattern = re.escape(schema.column_separator)
    pattern = f"(?<!\\\\){sep_pattern}"

    parts = re.split(pattern, line)

    # Handle outer pipes if present
    # If the line starts/ends with a separator (and it wasn't escaped),
    # split will produce empty strings at start/end.
    if len(parts) > 1:
        if parts[0].strip() == "":
            parts = parts[1:]
        if parts and parts[-1].strip() == "":
            parts = parts[:-1]

    # Clean cells
    cleaned_parts = [clean_cell(part, schema) for part in parts]
    return cleaned_parts


def is_separator_row(row: list[str], schema: ParsingSchema) -> bool:
    """
    Check if a row is a separator row (e.g. |---|---|).
    """
    # A separator row typically contains only hyphens, colons, and spaces.
    # It must have at least one hyphen.
    for cell in row:
        # Remove expected chars
        cleaned = (
            cell.replace(schema.header_separator_char, "").replace(":", "").strip()
        )
        if cleaned:
            return False
        # Must contain at least one separator char (usually '-')
        if schema.header_separator_char not in cell:
            return False
    return True


def parse_table(markdown: str, schema: ParsingSchema = DEFAULT_SCHEMA) -> Table:
    """
    Parse a markdown table into a Table object.

    Args:
        markdown: The markdown string containing the table.
        schema: Configuration for parsing.

    Returns:
        Table object with headers and rows.
    """
    lines = markdown.strip().split("\n")
    headers: list[str] | None = None
    rows: list[list[str]] = []

    # Buffer for potential header row until we confirm it's a header with a separator
    potential_header: list[str] | None = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parsed_row = parse_row(line, schema)

        if parsed_row is None:
            continue

        if headers is None and potential_header is not None:
            if is_separator_row(parsed_row, schema):
                headers = potential_header
                potential_header = None
                continue
            else:
                # Previous row was not a header, treat as data
                rows.append(potential_header)
                potential_header = parsed_row
        elif headers is None and potential_header is None:
            potential_header = parsed_row
        else:
            rows.append(parsed_row)

    if potential_header is not None:
        rows.append(potential_header)

    # Normalize rows to match header length
    if headers:
        header_len = len(headers)
        normalized_rows = []
        for row in rows:
            if len(row) < header_len:
                # Pad with empty strings
                row.extend([""] * (header_len - len(row)))
            elif len(row) > header_len:
                # Truncate
                row = row[:header_len]
            normalized_rows.append(row)
        rows = normalized_rows

    return Table(headers=headers, rows=rows, metadata={"schema_used": str(schema)})


def _extract_tables(text: str, schema: MultiTableParsingSchema) -> list[Table]:
    """
    Extract tables from text.
    If table_header_level is set, splits by that header.
    Otherwise, splits by blank lines.
    """
    tables: list[Table] = []

    if schema.table_header_level is not None:
        # Split by table header
        header_prefix = "#" * schema.table_header_level + " "
        lines = text.split("\n")

        current_table_lines: list[str] = []
        current_table_name: str | None = None
        current_description_lines: list[str] = []

        def process_table_block():
            if current_table_name and current_table_lines:
                # Try to separate description from table content
                # Simple heuristic: find the first line that looks like a table row
                table_start_idx = -1
                for idx, line in enumerate(current_table_lines):
                    if schema.column_separator in line:
                        table_start_idx = idx
                        break

                if table_start_idx != -1:
                    # Description is everything before table start
                    desc_lines = (
                        current_description_lines
                        + current_table_lines[:table_start_idx]
                    )
                    table_content = "\n".join(current_table_lines[table_start_idx:])

                    description = (
                        "\n".join(line.strip() for line in desc_lines if line.strip())
                        if schema.capture_description
                        else None
                    )
                    if description == "":
                        description = None

                    table = parse_table(table_content, schema)
                    table = replace(
                        table, name=current_table_name, description=description
                    )
                    tables.append(table)

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(header_prefix):
                process_table_block()
                current_table_name = stripped[len(header_prefix) :].strip()
                current_table_lines = []
                current_description_lines = []
            else:
                if current_table_name is not None:
                    current_table_lines.append(line)

        process_table_block()

    else:
        # Legacy/Simple mode: Split by blank lines, try to parse each block
        blocks = text.split("\n\n")
        for block in blocks:
            if not block.strip():
                continue
            # Heuristic: must contain separator
            if schema.column_separator in block:
                table = parse_table(block, schema)
                if table.rows or table.headers:
                    tables.append(table)

    return tables


def parse_sheet(markdown: str, name: str, schema: MultiTableParsingSchema) -> Sheet:
    """
    Parse a sheet (section) containing one or more tables.
    """
    tables = _extract_tables(markdown, schema)
    return Sheet(name=name, tables=tables)


def parse_workbook(
    markdown: str, schema: MultiTableParsingSchema = MultiTableParsingSchema()
) -> Workbook:
    """
    Parse a markdown document into a Workbook.
    """
    lines = markdown.split("\n")
    sheets: list[Sheet] = []

    # Find root marker
    start_index = 0
    if schema.root_marker:
        found = False
        for i, line in enumerate(lines):
            if line.strip() == schema.root_marker:
                start_index = i + 1
                found = True
                break
        if not found:
            return Workbook(sheets=[])

    # Split by sheet headers
    header_prefix = "#" * schema.sheet_header_level + " "

    current_sheet_name: str | None = None
    current_sheet_lines: list[str] = []

    for line in lines[start_index:]:
        stripped = line.strip()

        # Check if line is a header
        if stripped.startswith("#"):
            # Count header level
            level = 0
            for char in stripped:
                if char == "#":
                    level += 1
                else:
                    break

            # If header level is less than sheet_header_level (e.g. # vs ##),
            # it indicates a higher-level section, so we stop parsing the workbook.
            if level < schema.sheet_header_level:
                break

        if stripped.startswith(header_prefix):
            if current_sheet_name:
                sheet_content = "\n".join(current_sheet_lines)
                sheets.append(parse_sheet(sheet_content, current_sheet_name, schema))

            current_sheet_name = stripped[len(header_prefix) :].strip()
            current_sheet_lines = []
        else:
            if current_sheet_name:
                current_sheet_lines.append(line)

    if current_sheet_name:
        sheet_content = "\n".join(current_sheet_lines)
        sheets.append(parse_sheet(sheet_content, current_sheet_name, schema))

    return Workbook(sheets=sheets)


def scan_tables(
    markdown: str, schema: MultiTableParsingSchema | None = None
) -> list[Table]:
    """
    Scan a markdown document for all tables, ignoring sheet structure.

    Args:
        markdown: The markdown text.
        schema: Optional schema. If None, uses default MultiTableParsingSchema.

    Returns:
        List of found Table objects.
    """
    if schema is None:
        schema = MultiTableParsingSchema()

    return _extract_tables(markdown, schema)
