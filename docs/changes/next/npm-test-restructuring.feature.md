## NPM Package E2E Test Restructuring and Coverage Expansion

Comprehensive improvements to the NPM package testing infrastructure:

### Test Restructuring
- Migrated from monolithic `scripts/test.mjs` to modular `tests/` directory
- Split tests into dedicated files: `parsing.test.mjs`, `table.test.mjs`, `sheet.test.mjs`, `workbook.test.mjs`, `tomodels.test.mjs`
- Added shared `helpers.mjs` with assertion utilities and `runner.mjs` test orchestrator

### API Improvements
- `replaceTable` and `replaceSheet` now auto-convert model instances to DTO (no explicit `.toDTO()` required)
- Full API parity with Python: users can pass `Table`/`Sheet` instances directly

### Test Coverage Expansion (204 → 235 assertions)
- Added tests for: `deleteRow`, `deleteColumn`, `insertRow`, `insertColumn`, `clearColumnData`
- Added `Sheet.getTable` tests
- Added `parseTableFromFile`, `parseWorkbookFromFile`, `scanTablesFromFile` function verification

### Documentation
- Created `DEVELOPMENT.md` documenting the Python-to-NPM workflow
