from md_spreadsheet_parser.parsing import parse_sheet, parse_table
from md_spreadsheet_parser.schemas import MultiTableParsingSchema


def test_parse_metadata_with_empty_lines():
    markdown = """
| A |
|---|
| 1 |


<!-- md-spreadsheet-metadata: {"columnWidths": [100]} -->
""".strip()

    table = parse_table(markdown)
    assert table.rows == [["1"]]
    assert "visual" in table.metadata
    assert table.metadata["visual"]["columnWidths"] == [100]


def test_sheet_parsing_with_gapped_metadata():
    markdown = """# Sheet

| A |
|---|
| 1 |


<!-- md-spreadsheet-metadata: {"test": true} -->

# Next Section
"""
    sheet = parse_sheet(markdown, "Sheet", MultiTableParsingSchema())
    assert len(sheet.tables) == 1
    assert "visual" in sheet.tables[0].metadata
    assert sheet.tables[0].metadata["visual"]["test"] is True


def test_simple_parsing_with_gapped_metadata():
    # Test without headers (Simple extraction)
    markdown = """
| A |
|---|
| 1 |


<!-- md-spreadsheet-metadata: {"columnWidths": [100]} -->
""".strip()

    schema = MultiTableParsingSchema(table_header_level=None, capture_description=False)
    sheet = parse_sheet(markdown, "Sheet", schema)

    assert len(sheet.tables) == 1
    assert "visual" in sheet.tables[0].metadata
    assert sheet.tables[0].metadata["visual"]["columnWidths"] == [100]
