import md_spreadsheet_parser.parsing
from spreadsheet_parser import exports


class SpreadsheetParser(exports.SpreadsheetParser):
    def parse(self, content: str) -> int:
        workbook = md_spreadsheet_parser.parsing.parse_workbook(content)
        return len(workbook.sheets)
