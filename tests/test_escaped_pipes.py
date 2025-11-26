from md_spreadsheet_parser import parse_table


def test_escaped_pipes():
    """
    Test that escaped pipes are treated as content, not separators.
    """
    markdown = r"""
| Col 1 | Col 2 |
|---|---|
| A | B \| C |
"""
    table = parse_table(markdown)

    assert table.rows[0][1] == "B | C"
    assert len(table.rows[0]) == 2
