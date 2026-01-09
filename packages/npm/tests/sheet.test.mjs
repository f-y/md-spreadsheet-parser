/**
 * Sheet Class Tests for md-spreadsheet-parser NPM Package
 * 
 * Mirrors Python tests/core/test_models.py Sheet section.
 * All tests verify metadata preservation as object type.
 */

import { parseWorkbook, Sheet, Table, Workbook } from '../dist/index.js';
import {
    assert,
    assertType,
    assertNotNull,
    assertInstanceOf,
    assertEqual,
    assertArrayEqual,
    assertMetadataIsObject
} from './helpers.mjs';

export function runSheetTests() {
    console.log("\n📦 Sheet Class Tests");
    console.log("-".repeat(40));

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

    try {
        const raw = parseWorkbook(simpleWorkbookMd);
        const wb = new Workbook(raw);
        const sheet = wb.sheets[0];

        assertInstanceOf(sheet, Sheet, "sheet");

        // json getter
        const json = sheet.json;
        assertNotNull(json, "Sheet.json");
        assertType(json, "object", "Sheet.json");
        assert(json.name === "Sheet1", "json.name should be Sheet1");
        assert(Array.isArray(json.tables), "json.tables should be array");

        // toMarkdown
        const md = sheet.toMarkdown();
        assertType(md, "string", "Sheet.toMarkdown");
        assert(md.includes("| A | B |"), "toMarkdown should contain table headers");

        // Access tables
        assert(sheet.tables.length > 0, "sheet should have tables");
        assertInstanceOf(sheet.tables[0], Table, "tables[0] type");

        // getTable - test with a sheet that has explicitly named tables
        const sheetForGetTable = new Sheet({
            name: "TestSheet",
            tables: [
                { headers: ["A"], rows: [["1"]], name: "Table1" },
                { headers: ["B"], rows: [["2"]], name: "Table2" }
            ]
        });

        const foundTable = sheetForGetTable.getTable("Table1");
        assertNotNull(foundTable, "getTable should find table by name");
        assertInstanceOf(foundTable, Table, "getTable result type");
        assert(foundTable.name === "Table1", "getTable should return correct table");

        const foundTable2 = sheetForGetTable.getTable("Table2");
        assertNotNull(foundTable2, "getTable should find second table");

        const notFoundTable = sheetForGetTable.getTable("NonExistent");
        assert(notFoundTable === undefined, "getTable should return undefined for missing table");

        // ============================================================
        // rename - Mirrors Python test_sheet_rename
        // ============================================================

        const sheetForRename = new Sheet({
            name: "Old",
            tables: [{
                headers: ["H1"],
                rows: [["data"]],
                name: "T1",
                metadata: { table_key: "table_value" }
            }],
            metadata: { sheet_key: "sheet_value" }
        });

        const renamedSheet = sheetForRename.rename("New");

        // Verify name changed
        assert(renamedSheet.name === "New", "rename should change name");

        // Verify metadata preserved (type and value)
        assertMetadataIsObject(renamedSheet.metadata, "metadata after rename");
        assertEqual(renamedSheet.metadata, { sheet_key: "sheet_value" }, "metadata value after rename");

        // Verify tables preserved
        assert(renamedSheet.tables.length === 1, "tables count after rename");
        assert(renamedSheet.tables[0].name === "T1", "table name after rename");
        assertMetadataIsObject(renamedSheet.tables[0].metadata, "table metadata after rename");

        // ============================================================
        // addTable - Mirrors Python test_sheet_add_table
        // ============================================================

        const sheetForAdd = new Sheet({
            name: "S",
            tables: [{
                headers: ["H1", "H2"],
                rows: [["a", "b"]],
                name: "Existing",
                metadata: { existing_key: "existing_value" }
            }],
            metadata: { sheet_key: "sheet_value" }
        });

        const afterAdd = sheetForAdd.addTable("MyTable");

        // Verify table added
        assert(afterAdd.tables.length === 2, "tables count after addTable");
        assert(afterAdd.tables[1].name === "MyTable", "new table name");
        assertArrayEqual(afterAdd.tables[1].headers, ["A", "B", "C"], "new table default headers");

        // Verify sheet metadata preserved
        assertMetadataIsObject(afterAdd.metadata, "metadata after addTable");
        assertEqual(afterAdd.metadata, { sheet_key: "sheet_value" }, "metadata value after addTable");

        // Verify existing table unchanged
        assert(afterAdd.tables[0].name === "Existing", "existing table name");
        assertMetadataIsObject(afterAdd.tables[0].metadata, "existing table metadata");

        // ============================================================
        // deleteTable - Mirrors Python test_sheet_delete_table
        // ============================================================

        const sheetForDelete = new Sheet({
            name: "S",
            tables: [
                { headers: ["A"], rows: [["1"]], name: "T1", metadata: { t1_key: "t1_value" }, description: "Table 1 description" },
                { headers: ["B"], rows: [["2"]], name: "T2", metadata: { t2_key: "t2_value" }, description: "Table 2 description" }
            ],
            metadata: { sheet_key: "sheet_value" }
        });

        const afterDelete = sheetForDelete.deleteTable(0);

        // Verify deletion
        assert(afterDelete.tables.length === 1, "tables count after deleteTable");
        assert(afterDelete.tables[0].name === "T2", "remaining table name");

        // Verify sheet metadata preserved
        assertMetadataIsObject(afterDelete.metadata, "metadata after deleteTable");

        // Verify remaining table fully preserved
        assertMetadataIsObject(afterDelete.tables[0].metadata, "remaining table metadata");
        assertEqual(afterDelete.tables[0].metadata, { t2_key: "t2_value" }, "remaining table metadata value");
        assert(afterDelete.tables[0].description === "Table 2 description", "remaining table description");

        // ============================================================
        // replaceTable - Mirrors Python test_sheet_replace_table
        // ============================================================

        const sheetForReplace = new Sheet({
            name: "S",
            tables: [
                { headers: ["A"], rows: [], name: "T1", metadata: { t1_key: "t1_value" } },
                { headers: ["B"], rows: [], name: "T2", metadata: { t2_key: "t2_value" } }
            ],
            metadata: { sheet_key: "sheet_value" }
        });

        const replacement = new Table({
            headers: ["X", "Y"],
            rows: [["x1", "y1"]],
            name: "Replaced",
            metadata: { new_key: "new_value" },
            description: "New description"
        });

        const afterReplace = sheetForReplace.replaceTable(0, replacement);

        // Verify replacement
        assert(afterReplace.tables[0].name === "Replaced", "replaced table name");
        assertEqual(afterReplace.tables[0].metadata, { new_key: "new_value" }, "replaced table metadata");
        assert(afterReplace.tables[0].description === "New description", "replaced table description");
        assertArrayEqual(afterReplace.tables[0].headers, ["X", "Y"], "replaced table headers");

        // Verify sheet metadata preserved
        assertMetadataIsObject(afterReplace.metadata, "metadata after replaceTable");

        // Verify other table unchanged
        assert(afterReplace.tables[1].name === "T2", "other table name");
        assertEqual(afterReplace.tables[1].metadata, { t2_key: "t2_value" }, "other table metadata");

        // ============================================================
        // moveTable - Mirrors Python test_sheet_move_table
        // ============================================================

        const sheetForMove = new Sheet({
            name: "S",
            tables: [
                { headers: ["A"], rows: [["1"]], name: "T1", metadata: { t1_key: "t1_value" }, alignments: ["left"] },
                { headers: ["B"], rows: [["2"]], name: "T2", metadata: { t2_key: "t2_value" }, alignments: ["center"] },
                { headers: ["C"], rows: [["3"]], name: "T3", metadata: { t3_key: "t3_value" }, alignments: ["right"] }
            ],
            metadata: { sheet_key: "sheet_value" }
        });

        const afterMove = sheetForMove.moveTable(0, 2);

        // Verify order changed
        const tableNames = afterMove.tables.map(t => t.name);
        assertArrayEqual(tableNames, ["T2", "T3", "T1"], "table order after moveTable");

        // Verify sheet metadata preserved
        assertMetadataIsObject(afterMove.metadata, "metadata after moveTable");
        assertEqual(afterMove.metadata, { sheet_key: "sheet_value" }, "metadata value after moveTable");

        // Verify all table properties preserved after move
        const movedTable = afterMove.tables[2]; // T1 is now at index 2
        assertMetadataIsObject(movedTable.metadata, "moved table metadata");
        assertEqual(movedTable.metadata, { t1_key: "t1_value" }, "moved table metadata value");
        assertArrayEqual(movedTable.alignments, ["left"], "moved table alignments");
        assertArrayEqual(movedTable.rows, [["1"]], "moved table rows");

        console.log("   ✅ Sheet tests verified");
    } catch (e) {
        console.error("   ❌ Sheet tests failed:", e);
    }
}
