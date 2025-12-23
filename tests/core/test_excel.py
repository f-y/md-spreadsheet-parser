"""Tests for Excel/TSV/CSV parsing module."""

import pytest

from md_spreadsheet_parser import (
    parse_excel,
    parse_excel_text,
    ExcelParsingSchema,
)


class TestParseExcelText:
    """Tests for parse_excel_text with list[list[str]] input."""

    def test_single_header_row_basic(self):
        """Basic parsing with 1-row header."""
        rows = [
            ["Name", "Age", "City"],
            ["Alice", "30", "Tokyo"],
            ["Bob", "25", "Osaka"],
        ]
        table = parse_excel_text(rows)

        assert table.headers == ["Name", "Age", "City"]
        assert len(table.rows) == 2
        assert table.rows[0] == ["Alice", "30", "Tokyo"]
        assert table.rows[1] == ["Bob", "25", "Osaka"]

    def test_single_header_with_merged_cells(self):
        """Forward-fill empty header cells (merged cell simulation)."""
        rows = [
            ["Category", "", "", "Info"],
            ["A", "B", "C", "D"],
        ]
        table = parse_excel_text(rows)

        # Empty cells should be filled with previous value
        assert table.headers == ["Category", "Category", "Category", "Info"]
        assert table.rows[0] == ["A", "B", "C", "D"]

    def test_single_header_no_fill(self):
        """Disable forward-fill."""
        rows = [
            ["Category", "", "", "Info"],
            ["A", "B", "C", "D"],
        ]
        schema = ExcelParsingSchema(fill_merged_headers=False)
        table = parse_excel_text(rows, schema)

        # Empty cells should remain empty
        assert table.headers == ["Category", "", "", "Info"]

    def test_two_row_header_flattening(self):
        """Flatten 2-row hierarchical headers."""
        rows = [
            ["Info", "", "Metrics", ""],
            ["Name", "ID", "Score", "Rank"],
            ["Alice", "001", "95", "1"],
        ]
        schema = ExcelParsingSchema(header_rows=2)
        table = parse_excel_text(rows, schema)

        # Parent merged cells should be forward-filled, then combined
        assert table.headers == [
            "Info - Name",
            "Info - ID",
            "Metrics - Score",
            "Metrics - Rank",
        ]
        assert len(table.rows) == 1
        assert table.rows[0] == ["Alice", "001", "95", "1"]

    def test_two_row_header_same_parent_child(self):
        """When parent and child are the same, use child only."""
        rows = [
            ["Name", "Age"],
            ["Name", "Age"],
            ["Alice", "30"],
        ]
        schema = ExcelParsingSchema(header_rows=2)
        table = parse_excel_text(rows, schema)

        # Same parent/child should result in just the child value
        assert table.headers == ["Name", "Age"]

    def test_custom_header_separator(self):
        """Custom separator for flattened headers."""
        rows = [
            ["Parent", ""],
            ["Child1", "Child2"],
            ["A", "B"],
        ]
        schema = ExcelParsingSchema(header_rows=2, header_separator="/")
        table = parse_excel_text(rows, schema)

        assert table.headers == ["Parent/Child1", "Parent/Child2"]

    def test_empty_rows(self):
        """Handle empty input."""
        table = parse_excel_text([])
        assert table.headers is None
        assert table.rows == []


class TestParseExcel:
    """Tests for parse_excel with various input types."""

    def test_string_input_tsv(self):
        """Parse TSV string."""
        tsv = "Name\tAge\nAlice\t30\nBob\t25"
        table = parse_excel(tsv)

        assert table.headers == ["Name", "Age"]
        assert table.rows == [["Alice", "30"], ["Bob", "25"]]

    def test_string_input_csv(self):
        """Parse CSV string with custom delimiter."""
        csv_text = "Name,Age\nAlice,30\nBob,25"
        schema = ExcelParsingSchema(delimiter=",")
        table = parse_excel(csv_text, schema)

        assert table.headers == ["Name", "Age"]
        assert table.rows == [["Alice", "30"], ["Bob", "25"]]

    def test_list_input(self):
        """Parse pre-parsed 2D array."""
        rows = [
            ["Name", "Age"],
            ["Alice", "30"],
        ]
        table = parse_excel(rows)

        assert table.headers == ["Name", "Age"]
        assert table.rows == [["Alice", "30"]]

    def test_tsv_with_quoted_values(self):
        """TSV with quoted values containing delimiters."""
        tsv = 'Name\tNotes\nAlice\t"Line1\nLine2"\nBob\tSimple'
        table = parse_excel(tsv)

        assert table.headers == ["Name", "Notes"]
        assert table.rows[0] == ["Alice", "Line1\nLine2"]
        assert table.rows[1] == ["Bob", "Simple"]

    def test_unsupported_input_type(self):
        """Raise TypeError for unsupported input."""
        with pytest.raises(TypeError) as exc_info:
            parse_excel(12345)  # type: ignore

        assert "Unsupported source type" in str(exc_info.value)


class TestExcelParsingSchema:
    """Tests for schema validation."""

    def test_valid_header_rows(self):
        """Valid header_rows values."""
        ExcelParsingSchema(header_rows=1)
        ExcelParsingSchema(header_rows=2)

    def test_invalid_header_rows(self):
        """Invalid header_rows should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ExcelParsingSchema(header_rows=3)

        assert "header_rows must be 1 or 2" in str(exc_info.value)


class TestToMarkdown:
    """Test round-trip from Excel to Markdown."""

    def test_excel_to_markdown(self):
        """Parse Excel TSV and generate Markdown."""
        tsv = "Name\tAge\nAlice\t30\nBob\t25"
        table = parse_excel(tsv)

        markdown = table.to_markdown()

        assert "| Name | Age |" in markdown
        assert "| Alice | 30 |" in markdown
        assert "| Bob | 25 |" in markdown
