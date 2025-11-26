from md_spreadsheet_parser import (
    parse_workbook,
    parse_table,
    MultiTableParsingSchema,
)


def test_workbook_end_boundary():
    """
    Test that workbook parsing stops when encountering a header that indicates
    the end of the workbook section (e.g. a higher-level header).
    """
    markdown = """
# Tables

## Sheet1
| A |
|---|
| 1 |

# Next Section
This is unrelated documentation.
| X |
|---|
| 9 |
"""
    schema = MultiTableParsingSchema(root_marker="# Tables", sheet_header_level=2)
    workbook = parse_workbook(markdown, schema)

    # Should have 1 sheet
    assert len(workbook.sheets) == 1
    sheet1 = workbook.sheets[0]
    assert sheet1.name == "Sheet1"

    # Sheet1 should have 1 table
    assert len(sheet1.tables) == 1
    table1 = sheet1.tables[0]
    assert table1.headers == ["A"]
    assert table1.rows == [["1"]]

    # The second table (X, 9) should NOT be in Sheet1
    # Currently, without the fix, it might be included.


def test_japanese_content():
    """
    Test parsing of Japanese content (headers, values, sheet names).
    """
    markdown = """
| 名前 | 年齢 | 職業 |
| --- | --- | --- |
| 田中 | 30 | エンジニア |
| 佐藤 | 25 | デザイナー |
"""
    table = parse_table(markdown)

    assert table.headers == ["名前", "年齢", "職業"]
    assert len(table.rows) == 2
    assert table.rows[0] == ["田中", "30", "エンジニア"]
    assert table.rows[1] == ["佐藤", "25", "デザイナー"]


def test_emoji_content():
    """
    Test parsing of content with Emojis.
    """
    markdown = """
| Status | Item |
| --- | --- |
| ✅ | Apple 🍎 |
| ❌ | Banana 🍌 |
"""
    table = parse_table(markdown)

    assert table.headers == ["Status", "Item"]
    assert len(table.rows) == 2
    assert table.rows[0] == ["✅", "Apple 🍎"]
    assert table.rows[1] == ["❌", "Banana 🍌"]


def test_workbook_japanese_sheet_names():
    markdown = """
# データ

## ユーザー一覧
| ID | 名前 |
| -- | -- |
| 1  | 太郎 |
"""
    schema = MultiTableParsingSchema(root_marker="# データ", sheet_header_level=2)
    workbook = parse_workbook(markdown, schema)

    assert len(workbook.sheets) == 1
    assert workbook.sheets[0].name == "ユーザー一覧"
    assert workbook.sheets[0].tables[0].rows[0] == ["1", "太郎"]
