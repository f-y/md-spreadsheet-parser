# Markdown Spreadsheet Parser

A lightweight, pure Python library for parsing Markdown tables into structured data.
Designed to be portable and run in WebAssembly environments (like Pyodide in VS Code extensions).

## Features

- **Pure Python**: Zero dependencies, runs anywhere Python runs (including WASM).
- **Structured Output**: Converts Markdown tables into JSON-friendly objects with headers and rows.
- **Multi-Table Support**: Can parse multiple tables (sheets) from a single file using a specific structure.
- **Configurable**: Supports different table styles via schemas.

## Installation

```bash
pip install md-spreadsheet-parser
```

## Usage

### Single Table

Use `parse_table` to parse a standard Markdown table.

```python
from md_spreadsheet_parser import parse_table

markdown = """
| Name | Age |
| --- | --- |
| Alice | 30 |
| Bob | 25 |
"""

result = parse_table(markdown)

print(result.headers)
# ['Name', 'Age']

print(result.rows)
# [['Alice', '30'], ['Bob', '25']]
```

### Multiple Tables (Workbook)

Use `parse_workbook` to parse a file containing multiple sheets.
**Note**: The file must start with the root marker `# Tables` (configurable).

```python
from md_spreadsheet_parser import parse_workbook, MultiTableParsingSchema

markdown = """
# Tables

## Sheet 1

| ID | Item |
| -- | ---- |
| 1  | Apple|

## Sheet 2

| ID | User |
| -- | ---- |
| 99 | Bob  |
"""

# Default schema uses "# Tables" as root marker
schema = MultiTableParsingSchema()
workbook = parse_workbook(markdown, schema)

for sheet in workbook.sheets:
    print(f"Sheet: {sheet.name}")
    for table in sheet.tables:
        print(table.headers)
        print(table.rows)
```

## License

MIT
