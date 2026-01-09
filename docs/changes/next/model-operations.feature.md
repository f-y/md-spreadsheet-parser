Added consistent CRUD operation methods to Workbook, Sheet, and Table models:

**Workbook**:
- `move_sheet(from_index, to_index)` - reorder sheets
- `replace_sheet(index, sheet)` - replace sheet at index
- `rename_sheet(index, new_name)` - rename sheet at index

**Sheet**:
- `rename(new_name)` - rename the sheet
- `add_table(name?)` - append a new empty table
- `delete_table(index)` - remove table at index
- `replace_table(index, table)` - replace table at index
- `move_table(from_index, to_index)` - reorder tables

**Table**:
- `rename(new_name)` - rename the table
- `move_row(from_index, to_index)` - reorder rows
- `move_column(from_index, to_index)` - reorder columns
