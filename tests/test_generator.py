from md_spreadsheet_parser import (
    Table,
    Sheet,
    Workbook,
    ParsingSchema,
    MultiTableParsingSchema,
)


def test_table_to_markdown_basic():
    table = Table(
        headers=["Name", "Age"],
        rows=[["Alice", "30"], ["Bob", "25"]],
    )
    schema = ParsingSchema(require_outer_pipes=True)
    markdown = table.to_markdown(schema)

    expected = """| Name | Age |
| --- | --- |
| Alice | 30 |
| Bob | 25 |"""

    assert markdown.strip() == expected.strip()


def test_table_to_markdown_no_headers():
    table = Table(
        headers=None,
        rows=[["A", "1"], ["B", "2"]],
    )
    schema = ParsingSchema(require_outer_pipes=True)
    markdown = table.to_markdown(schema)

    expected = """| A | 1 |
| B | 2 |"""

    assert markdown.strip() == expected.strip()


def test_table_to_markdown_with_metadata():
    table = Table(
        headers=["Col1"],
        rows=[["Val1"]],
        name="MyTable",
        description="This is a description.",
    )
    schema = MultiTableParsingSchema(
        table_header_level=3, capture_description=True, require_outer_pipes=True
    )
    markdown = table.to_markdown(schema)

    expected = """### MyTable
This is a description.

| Col1 |
| --- |
| Val1 |"""

    assert markdown.strip() == expected.strip()


def test_sheet_to_markdown():
    table1 = Table(headers=["A"], rows=[["1"]])
    sheet = Sheet(name="Sheet1", tables=[table1])

    schema = MultiTableParsingSchema(sheet_header_level=2, require_outer_pipes=True)
    markdown = sheet.to_markdown(schema)

    expected = """## Sheet1

| A |
| --- |
| 1 |"""

    assert markdown.strip() == expected.strip()


def test_workbook_to_markdown():
    table1 = Table(headers=["A"], rows=[["1"]])
    sheet1 = Sheet(name="Sheet1", tables=[table1])
    workbook = Workbook(sheets=[sheet1])

    schema = MultiTableParsingSchema(root_marker="# Tables", require_outer_pipes=True)
    markdown = workbook.to_markdown(schema)

    expected = """# Tables

## Sheet1

| A |
| --- |
| 1 |"""

    assert markdown.strip() == expected.strip()
