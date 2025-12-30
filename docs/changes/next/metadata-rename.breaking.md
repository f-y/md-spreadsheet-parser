### Metadata Tag Update (Breaking)

- **BREAKING**: Renamed `<!-- md-spreadsheet-metadata: ... -->` to `<!-- md-spreadsheet-table-metadata: ... -->` for consistency.
- Backward compatibility for the old tag has been dropped. Existing files with the old tag will still be parsed as tables, but the visual metadata (column widths, validation, etc.) will be ignored until manually updated.
