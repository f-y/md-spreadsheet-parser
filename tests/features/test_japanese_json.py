import json
import subprocess
import textwrap

from md_spreadsheet_parser import (
    MultiTableParsingSchema,
    Sheet,
    Table,
    Workbook,
)

CLI_CMD = ["uv", "run", "md-spreadsheet-parser"]


def test_generator_unicode_metadata():
    """
    Verify that Japanese characters in metadata are not escaped in the generated Markdown/JSON comments.
    """
    # 1. Table with Japanese metadata
    table = Table(
        name="テストテーブル",
        description="これはテストです。",
        headers=["項目A", "項目B"],
        rows=[["値1", "値2"]],
        metadata={"visual": {"layout": "日本語レイアウト", "color": "赤"}},
    )

    schema = MultiTableParsingSchema(
        table_header_level=3, capture_description=True, require_outer_pipes=True
    )

    markdown = table.to_markdown(schema)

    # Verify Table Name and Description appear correctly
    assert "### テストテーブル" in markdown
    assert "これはテストです。" in markdown

    # Verify Metadata JSON is not escaped
    # We expect: <!-- md-spreadsheet-table-metadata: {"layout": "日本語レイアウト", "color": "赤"} -->
    # Escaped would look like: \u65e5\u672c\u8a9e...
    expected_json_part = '"layout": "日本語レイアウト"'
    assert expected_json_part in markdown
    assert "\\u" not in markdown  # valid assumption if we use only simple Japanese

    # 2. Sheet with Japanese metadata
    sheet = Sheet(
        name="シート1", tables=[table], metadata={"owner": "管理者", "tag": "重要"}
    )

    sheet_markdown = sheet.to_markdown(schema)

    # Verify Sheet Name
    assert "## シート1" in sheet_markdown

    # Verify Sheet Metadata
    expected_sheet_json = '"owner": "管理者"'
    assert expected_sheet_json in sheet_markdown

    # 3. Workbook with Japanese metadata
    workbook = Workbook(
        sheets=[sheet], metadata={"project": "プロジェクトX", "status": "進行中"}
    )

    workbook_markdown = workbook.to_markdown(schema)

    # Verify Workbook Metadata
    expected_workbook_json = '"project": "プロジェクトX"'
    assert expected_workbook_json in workbook_markdown


def test_cli_unicode_output(tmp_path):
    """
    Verify that the CLI output (JSON) preserves Japanese characters (ensure_ascii=False).
    """
    markdown = textwrap.dedent("""
# Tables

## シート1

| 項目 | 値 |
| --- | --- |
| テスト | データ |
""")
    file_path = tmp_path / "test_jp.md"
    file_path.write_text(markdown, encoding="utf-8")

    result = subprocess.run(
        CLI_CMD + [str(file_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    # 1. Check raw stdout string contains Japanese (not escaped)
    assert "シート1" in result.stdout
    assert "項目" in result.stdout
    assert "データ" in result.stdout
    assert "\\u" not in result.stdout

    # 2. Parse JSON and verify content
    data = json.loads(result.stdout)
    # The default behavior of MultiTableParsingSchema usually picks up "Sheet1" unless specified otherwise,
    # but here we proivded ## シート1, so the sheet name should be シート1
    assert data["sheets"][0]["name"] == "シート1"

    table = data["sheets"][0]["tables"][0]
    assert table["headers"] == ["項目", "値"]
    assert table["rows"] == [["テスト", "データ"]]
