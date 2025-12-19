# Changelog

## [0.3.2] - 2025-12-19

### 📚 Documentation

### Added Cookbook

Added a new `COOKBOOK.md` file with recipes for common tasks:
- Fast installation
- Reading tables from files (one-liner)
- Pandas integration (DataFrame <-> Markdown <-> Excel/TSV)
- Programmatic Editing (Excel-like calculations)
- Code Formatting & Linting for tables
- JSON Conversion
- Simple Type-Safe Validation examples

Also added a prominent link to the guide at the top of `README.md`.

## [0.3.1] - 2025-12-17

### 🚀 New Features

### CI/CD Implementation

- **Added**: GitHub Actions workflow (`.github/workflows/tests.yml`) to run unit tests (`pytest`) for `md-spreadsheet-parser` on push and pull request.
- **Added**: Build status badge to `md-spreadsheet-parser/README.md`.

### 🐛 Bug Fixes

### Fix CI/CD Workflow

- **Fixed**: Corrected `paths` and `working-directory` configuration in GitHub Actions workflow to run properly in the `md-spreadsheet-parser` repository root.