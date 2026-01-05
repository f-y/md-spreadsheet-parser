Fixed a critical bug in the NPM package where `Workbook.getSheet()` and `Sheet.getTable()` returned plain objects instead of class instances. Now verifies that proper `Sheet` and `Table` instances are returned, restoring API compatibility.
Also fixed an issue where optional return types (like `optional<Sheet>`) were not correctly handled in the wrapper.
