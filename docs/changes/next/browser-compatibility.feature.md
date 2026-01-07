NPM package now builds and works correctly in browser environments (Vite, Webpack, etc.).

- Core APIs (`parseTable`, `parseWorkbook`, `scanTables`, etc.) work seamlessly in both Node.js and browser environments
- File-based APIs (`parseTableFromFile`, `parseWorkbookFromFile`, `scanTablesFromFile`) are now async functions that:
  - Work correctly in Node.js with lazy WASI filesystem initialization
  - Throw a clear error message in browser environments with guidance to use string-based alternatives
- Fixed `_addPreopen is not exported` error when using Vite or other browser bundlers
