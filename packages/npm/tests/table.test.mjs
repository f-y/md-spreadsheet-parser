/**
 * Table Class Tests for md-spreadsheet-parser NPM Package
 * 
 * Mirrors Python tests/core/test_models.py Table section.
 * All tests verify metadata preservation as object type.
 */

import { parseTable, Table } from '../dist/index.js';
import {
    assert,
    assertType,
    assertNotNull,
    assertEqual,
    assertArrayEqual,
    assertMetadataIsObject
} from './helpers.mjs';

export function runTableTests() {
    console.log("\n📦 Table Class Tests");
    console.log("-".repeat(40));

    const simpleTableMd = `
| Name | Age | Active |
| --- | --- | --- |
| Alice | 30 | true |
| Bob | 25 | false |
`;

    try {
        // ============================================================
        // Basic Table Operations
        // ============================================================

        const raw = parseTable(simpleTableMd);
        const table = new Table(Array.isArray(raw) ? raw[0] : raw);

        // toDTO
        const dto = table.toDTO();
        assertNotNull(dto, "toDTO result");
        assert(dto.headers !== undefined, "DTO should have headers");

        // json getter
        const json = table.json;
        assertNotNull(json, "json getter result");
        assertType(json, "object", "json getter");
        assert(Array.isArray(json.headers), "json.headers should be array");
        assert(Array.isArray(json.rows), "json.rows should be array");

        // toMarkdown
        const md = table.toMarkdown();
        assertType(md, "string", "toMarkdown result");
        assert(md.includes("| Name |"), "toMarkdown should contain headers");
        assert(md.includes("| Alice |"), "toMarkdown should contain row data");

        // updateCell
        const afterUpdate = table.updateCell(0, 1, "31");
        assert(afterUpdate === table, "updateCell should return this");
        assert(table.rows[0][1] === "31", `Cell should be updated to '31'`);
        assertMetadataIsObject(table.metadata, "metadata after updateCell");

        // ============================================================
        // rename - Mirrors Python test_table_rename
        // ============================================================

        const tableForRename = new Table({
            headers: ["H1", "H2"],
            rows: [["a", "b"], ["c", "d"]],
            name: "Old",
            description: "Original description",
            metadata: { key1: "value1", nested: { inner: "data" } },
            alignments: ["left", "right"],
            startLine: 10,
            endLine: 15
        });

        const renamedTable = tableForRename.rename("New");

        // Verify name changed
        assert(renamedTable.name === "New", "rename should change name");

        // Verify all properties preserved
        assertArrayEqual(renamedTable.headers, ["H1", "H2"], "headers after rename");
        assertArrayEqual(renamedTable.rows, [["a", "b"], ["c", "d"]], "rows after rename");
        assert(renamedTable.description === "Original description", "description after rename");
        assertArrayEqual(renamedTable.alignments, ["left", "right"], "alignments after rename");

        // Verify metadata preserved (type, value, and nested structure)
        assertMetadataIsObject(renamedTable.metadata, "metadata after rename");
        assertEqual(renamedTable.metadata, { key1: "value1", nested: { inner: "data" } }, "metadata value after rename");
        assertType(renamedTable.metadata.nested, "object", "nested metadata after rename");

        // ============================================================  
        // moveRow - Mirrors Python test_table_move_row
        // ============================================================

        const tableForMoveRow = new Table({
            headers: ["H1", "H2"],
            rows: [["a1", "a2"], ["b1", "b2"], ["c1", "c2"]],
            name: "TestTable",
            description: "Test description",
            metadata: { key: "value" },
            alignments: ["left", "center"]
        });

        const afterMoveRow = tableForMoveRow.moveRow(0, 2);

        // Verify row order changed
        assertArrayEqual(afterMoveRow.rows, [["b1", "b2"], ["c1", "c2"], ["a1", "a2"]], "rows after moveRow");

        // Verify all other properties preserved
        assertArrayEqual(afterMoveRow.headers, ["H1", "H2"], "headers after moveRow");
        assert(afterMoveRow.name === "TestTable", "name after moveRow");
        assert(afterMoveRow.description === "Test description", "description after moveRow");
        assertArrayEqual(afterMoveRow.alignments, ["left", "center"], "alignments after moveRow");

        // Verify metadata preserved
        assertMetadataIsObject(afterMoveRow.metadata, "metadata after moveRow");
        assertEqual(afterMoveRow.metadata, { key: "value" }, "metadata value after moveRow");

        // ============================================================
        // moveColumn - Mirrors Python test_table_move_column
        // ============================================================

        const tableForMoveCol = new Table({
            headers: ["A", "B", "C"],
            rows: [["1", "2", "3"], ["4", "5", "6"]],
            name: "TestTable",
            description: "Test description",
            metadata: { key: "value", array: [1, 2, 3] },
            alignments: ["left", "center", "right"]
        });

        const afterMoveCol = tableForMoveCol.moveColumn(0, 2);

        // Verify column order changed in headers and all rows
        assertArrayEqual(afterMoveCol.headers, ["B", "C", "A"], "headers after moveColumn");
        assertArrayEqual(afterMoveCol.rows, [["2", "3", "1"], ["5", "6", "4"]], "rows after moveColumn");

        // Verify alignments moved with columns
        assertArrayEqual(afterMoveCol.alignments, ["center", "right", "left"], "alignments after moveColumn");

        // Verify all other properties preserved
        assert(afterMoveCol.name === "TestTable", "name after moveColumn");
        assert(afterMoveCol.description === "Test description", "description after moveColumn");

        // Verify metadata preserved (type, value, and array)
        assertMetadataIsObject(afterMoveCol.metadata, "metadata after moveColumn");
        assertEqual(afterMoveCol.metadata, { key: "value", array: [1, 2, 3] }, "metadata value after moveColumn");
        assert(Array.isArray(afterMoveCol.metadata.array), "metadata.array should be array after moveColumn");

        // ============================================================
        // deleteRow - Mirrors Python test_table_delete_row
        // ============================================================

        const tableForDeleteRow = new Table({
            headers: ["H1", "H2"],
            rows: [["a1", "a2"], ["b1", "b2"], ["c1", "c2"]],
            name: "TestTable",
            metadata: { key: "value" },
            alignments: ["left", "center"]
        });

        const afterDeleteRow = tableForDeleteRow.deleteRow(1);

        // Verify row deleted
        assert(afterDeleteRow.rows.length === 2, "should have 2 rows after deleteRow");
        assertArrayEqual(afterDeleteRow.rows, [["a1", "a2"], ["c1", "c2"]], "rows after deleteRow");

        // Verify metadata preserved
        assertMetadataIsObject(afterDeleteRow.metadata, "metadata after deleteRow");
        assertEqual(afterDeleteRow.metadata, { key: "value" }, "metadata value after deleteRow");

        // ============================================================
        // deleteColumn - Mirrors Python test_table_delete_column
        // ============================================================

        const tableForDeleteCol = new Table({
            headers: ["A", "B", "C"],
            rows: [["1", "2", "3"], ["4", "5", "6"]],
            name: "TestTable",
            metadata: { key: "value" },
            alignments: ["left", "center", "right"]
        });

        const afterDeleteCol = tableForDeleteCol.deleteColumn(1);

        // Verify column deleted
        assertArrayEqual(afterDeleteCol.headers, ["A", "C"], "headers after deleteColumn");
        assertArrayEqual(afterDeleteCol.rows, [["1", "3"], ["4", "6"]], "rows after deleteColumn");
        assertArrayEqual(afterDeleteCol.alignments, ["left", "right"], "alignments after deleteColumn");

        // Verify metadata preserved
        assertMetadataIsObject(afterDeleteCol.metadata, "metadata after deleteColumn");

        // ============================================================
        // insertRow - Mirrors Python test_insert_row
        // ============================================================

        const tableForInsertRow = new Table({
            headers: ["H1", "H2"],
            rows: [["a1", "a2"], ["b1", "b2"]],
            name: "TestTable",
            metadata: { key: "value" },
            alignments: ["left", "center"]
        });

        const afterInsertRow = tableForInsertRow.insertRow(1);

        // Verify row inserted
        assert(afterInsertRow.rows.length === 3, "should have 3 rows after insertRow");
        assertArrayEqual(afterInsertRow.rows[1], ["", ""], "inserted row should be empty");

        // Verify metadata preserved
        assertMetadataIsObject(afterInsertRow.metadata, "metadata after insertRow");

        // ============================================================
        // insertColumn - Mirrors Python test_insert_column
        // ============================================================

        const tableForInsertCol = new Table({
            headers: ["A", "B"],
            rows: [["1", "2"], ["3", "4"]],
            name: "TestTable",
            metadata: { key: "value" },
            alignments: ["left", "center"]
        });

        const afterInsertCol = tableForInsertCol.insertColumn(1);

        // Verify column inserted
        assert(afterInsertCol.headers.length === 3, "should have 3 headers after insertColumn");
        assertArrayEqual(afterInsertCol.rows[0], ["1", "", "2"], "first row after insertColumn");

        // Verify metadata preserved
        assertMetadataIsObject(afterInsertCol.metadata, "metadata after insertColumn");

        // ============================================================
        // clearColumnData - Mirrors Python test_clear_column_data
        // ============================================================

        const tableForClearCol = new Table({
            headers: ["A", "B", "C"],
            rows: [["1", "2", "3"], ["4", "5", "6"]],
            name: "TestTable",
            metadata: { key: "value" }
        });

        const afterClearCol = tableForClearCol.clearColumnData(1);

        // Verify column data cleared
        assertArrayEqual(afterClearCol.rows, [["1", "", "3"], ["4", "", "6"]], "rows after clearColumnData");

        // Verify headers unchanged
        assertArrayEqual(afterClearCol.headers, ["A", "B", "C"], "headers after clearColumnData");

        // Verify metadata preserved
        assertMetadataIsObject(afterClearCol.metadata, "metadata after clearColumnData");

        console.log("   ✅ Table tests verified");
    } catch (e) {
        console.error("   ❌ Table tests failed:", e);
    }
}
