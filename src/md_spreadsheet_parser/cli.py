import argparse
import json
import sys
from pathlib import Path

from .core import parse_workbook, scan_tables
from .schemas import MultiTableParsingSchema


def main():
    parser = argparse.ArgumentParser(
        description="Parse Markdown tables to JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        help="Path to Markdown file. If omitted or '-', reads from stdin.",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for all tables ignoring workbook structure (uses scan_tables).",
    )
    parser.add_argument(
        "--root-marker",
        type=str,
        default="# Tables",
        help="Marker indicating start of data section (for workbook mode).",
    )
    parser.add_argument(
        "--sheet-header-level",
        type=int,
        default=2,
        help="Header level for sheets (for workbook mode).",
    )
    parser.add_argument(
        "--table-header-level",
        type=int,
        default=None,
        help="Header level for tables.",
    )
    parser.add_argument(
        "--capture-description",
        action="store_true",
        help="Capture text between header and table as description. Requires --table-header-level.",
    )

    args = parser.parse_args()

    # Validate configuration
    if args.capture_description and args.table_header_level is None:
        print(
            "Error: --capture-description requires --table-header-level to be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read input
    if args.file and args.file != "-":
        try:
            content = Path(args.file).read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
    else:
        content = sys.stdin.read()

    # Configure schema
    schema = MultiTableParsingSchema(
        root_marker=args.root_marker,
        sheet_header_level=args.sheet_header_level,
        table_header_level=args.table_header_level,
        capture_description=args.capture_description,
    )

    # Parse
    try:
        if args.scan:
            tables = scan_tables(content, schema)
            # Output list of tables
            print(json.dumps([t.json for t in tables], indent=2, ensure_ascii=False))
        else:
            workbook = parse_workbook(content, schema)
            print(json.dumps(workbook.json, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error parsing content: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
