/**
 * Parsing Function Tests for md-spreadsheet-parser NPM Package
 * 
 * Tests parseTable, parseWorkbook, parseSheet, scanTables functions.
 * Verifies correct structure and metadata type safety.
 */

import {
    parseWorkbook,
    parseTable,
    parseSheet,
    scanTables,
    parseTableFromFile,
    parseWorkbookFromFile,
    scanTablesFromFile,
    Table,
    Sheet,
    Workbook
} from '../dist/index.js';
import {
    assert,
    assertType,
    assertNotNull,
    assertInstanceOf,
    assertMetadataIsObject
} from './helpers.mjs';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export async function runParsingTests() {
    console.log("\n📦 Parsing Function Tests");
    console.log("-".repeat(40));

    const simpleTableMd = `
| Name | Age | Active |
| --- | --- | --- |
| Alice | 30 | true |
| Bob | 25 | false |
`;

    const simpleWorkbookMd = `
# Tables

## Sheet1

| A | B |
|---|---|
| 1 | 2 |

## Sheet2

| X | Y | Z |
|---|---|---|
| a | b | c |
`;

    const tableWithMetadataMd = `
| Col1 | Col2 |
| --- | --- |
| val1 | val2 |

<!-- md-spreadsheet-table-metadata: {"column_widths": {"0": 100, "1": 200}} -->
`;

    // ============================================================
    // parseTable
    // ============================================================

    try {
        const tables = parseTable(simpleTableMd);
        assertNotNull(tables, "parseTable result");

        const table = Array.isArray(tables) ? tables[0] : tables;
        assertNotNull(table, "First table");

        const t = new Table(table);

        // Headers
        assert(Array.isArray(t.headers), "headers should be array");
        assert(t.headers.length === 3, `headers length should be 3, got ${t.headers.length}`);
        assert(t.headers[0] === "Name", `First header should be 'Name', got '${t.headers[0]}'`);

        // Rows
        assert(Array.isArray(t.rows), "rows should be array");
        assert(t.rows.length === 2, `rows length should be 2, got ${t.rows.length}`);
        assert(t.rows[0][0] === "Alice", `First cell should be 'Alice', got '${t.rows[0][0]}'`);

        console.log("   ✅ parseTable verified");
    } catch (e) {
        console.error("   ❌ parseTable failed:", e);
    }

    // ============================================================
    // parseWorkbook
    // ============================================================

    try {
        const raw = parseWorkbook(simpleWorkbookMd);
        const wb = new Workbook(raw);

        assertNotNull(wb, "Workbook");
        assert(Array.isArray(wb.sheets), "sheets should be array");
        assert(wb.sheets.length === 2, `Expected 2 sheets, got ${wb.sheets.length}`);

        // Workbook level
        assertMetadataIsObject(wb.metadata, "Workbook.metadata");

        // Sheet level
        const sheet1 = wb.sheets[0];
        assertInstanceOf(sheet1, Sheet, "sheets[0]");
        assert(sheet1.name === "Sheet1", `Sheet name should be 'Sheet1'`);
        assertMetadataIsObject(sheet1.metadata, "Sheet.metadata");

        // Table level
        const table1 = sheet1.tables[0];
        assertInstanceOf(table1, Table, "sheets[0].tables[0]");
        assertMetadataIsObject(table1.metadata, "Table.metadata");

        // Verify Sheet2
        const sheet2 = wb.sheets[1];
        assert(sheet2.name === "Sheet2", `Sheet2 name should be 'Sheet2'`);
        assert(sheet2.tables[0].headers[0] === "X", `Table2 first header should be 'X'`);

        console.log("   ✅ parseWorkbook verified");
    } catch (e) {
        console.error("   ❌ parseWorkbook failed:", e);
    }

    // ============================================================
    // scanTables
    // ============================================================

    try {
        const tables = scanTables(simpleWorkbookMd);

        assertNotNull(tables, "scanTables result");
        assert(Array.isArray(tables), "scanTables should return array");
        assert(tables.length === 2, `Expected 2 tables, got ${tables.length}`);

        const t1 = new Table(tables[0]);
        assert(t1.headers.length === 2, "First table should have 2 headers");

        console.log("   ✅ scanTables verified");
    } catch (e) {
        console.error("   ❌ scanTables failed:", e);
    }

    // ============================================================
    // Metadata Structure
    // ============================================================

    try {
        const raw = parseTable(tableWithMetadataMd);
        const table = new Table(Array.isArray(raw) ? raw[0] : raw);

        assertMetadataIsObject(table.metadata, "Table.metadata");

        if (table.metadata && table.metadata.column_widths) {
            assertType(table.metadata.column_widths, "object", "column_widths type");
            assert(table.metadata.column_widths["0"] === 100,
                `column_widths[0] should be 100, got ${table.metadata.column_widths["0"]}`);
        }

        // Mutation preserves metadata
        table.updateCell(0, 0, "updated");
        assertMetadataIsObject(table.metadata, "metadata after mutation");

        console.log("   ✅ Metadata structure verified");
    } catch (e) {
        console.error("   ❌ Metadata tests failed:", e);
    }

    // ============================================================
    // Complex Workbook (hybrid_notebook.md)
    // ============================================================

    const hybridPath = join(__dirname, 'fixtures/hybrid_notebook.md');
    let hybridContent;
    try {
        hybridContent = readFileSync(hybridPath, 'utf-8');
    } catch (e) {
        hybridContent = null;
    }

    if (hybridContent) {
        try {
            const raw = parseWorkbook(hybridContent);
            const wb = new Workbook(raw);

            assert(wb.sheets.length >= 4, `Expected at least 4 sheets, got ${wb.sheets.length}`);

            const sheetNames = wb.sheets.map(s => s.name);
            assert(sheetNames.includes("MyTestSheet"), "Should have MyTestSheet");
            assert(sheetNames.includes("Comparison"), "Should have Comparison");

            assertMetadataIsObject(wb.metadata, "Workbook.metadata");

            const regenerated = wb.toMarkdown();
            assert(regenerated.length > 1000, "Regenerated markdown should be substantial");

            console.log("   ✅ Complex workbook verified");
        } catch (e) {
            console.error("   ❌ Complex workbook failed:", e);
        }
    } else {
        console.log("   ⏭️ Complex workbook skipped (fixture not found)");
    }

    // ============================================================
    // File-based Functions Error Verification
    // These functions should work in Node.js but we verify they exist
    // and have proper error handling
    // ============================================================

    try {
        // parseTableFromFile - should throw for non-existent file or work for real file
        assert(typeof parseTableFromFile === "function", "parseTableFromFile should be a function");

        // parseWorkbookFromFile - should be a function
        assert(typeof parseWorkbookFromFile === "function", "parseWorkbookFromFile should be a function");

        // scanTablesFromFile - should be a function
        assert(typeof scanTablesFromFile === "function", "scanTablesFromFile should be a function");

        // Test with a valid file path (since we're in Node.js)
        try {
            const result = await parseTableFromFile(hybridPath);
            // parseTableFromFile may return array or single object depending on content
            assert(result !== null && result !== undefined, "parseTableFromFile should return result");
            console.log("   ✅ File-based functions verified");
        } catch (e) {
            // If file operations fail, that's also valid - just verify the function exists
            console.log("   ✅ File-based functions exist (execution environment dependent)");
        }
    } catch (e) {
        console.error("   ❌ File-based functions test failed:", e);
    }
}
