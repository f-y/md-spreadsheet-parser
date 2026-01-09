/**
 * toModels Tests for md-spreadsheet-parser NPM Package
 * 
 * Tests toModels with Plain Object Schema and Zod Schema.
 */

import { parseTable, Table } from '../dist/index.js';
import { z } from 'zod';
import {
    assert,
    assertType,
    assertNotNull
} from './helpers.mjs';

export function runToModelsTests() {
    console.log("\n📦 toModels Tests");
    console.log("-".repeat(40));

    const tableMd = `
| id | name | active | score |
| --- | --- | --- | --- |
| 1 | Alice | yes | 95.5 |
| 2 | Bob | no | 80.0 |
`;

    // ============================================================
    // Plain Object Schema
    // ============================================================

    try {
        const raw = parseTable(tableMd);
        const table = new Table(Array.isArray(raw) ? raw[0] : raw);

        const schema = {
            id: (val) => parseInt(val, 10),
            name: (val) => val.trim(),
            active: (val) => val === 'yes',
            score: (val) => parseFloat(val)
        };

        const models = table.toModels(schema);

        assertNotNull(models, "toModels result");
        assert(Array.isArray(models), "toModels should return array");
        assert(models.length === 2, `Expected 2 models, got ${models.length}`);

        // Verify first model
        const alice = models[0];
        assert(alice.id === 1, `Alice.id should be 1, got ${alice.id}`);
        assertType(alice.id, "number", "id type");
        assert(alice.name === "Alice", `name should be 'Alice'`);
        assert(alice.active === true, `active should be true`);
        assertType(alice.active, "boolean", "active type");
        assert(alice.score === 95.5, `score should be 95.5`);
        assertType(alice.score, "number", "score type");

        // Verify second model
        const bob = models[1];
        assert(bob.id === 2, `Bob.id should be 2`);
        assert(bob.active === false, `Bob.active should be false`);

        console.log("   ✅ toModels (Plain Object) verified");
    } catch (e) {
        console.error("   ❌ toModels (Plain Object) failed:", e);
    }

    // ============================================================
    // Zod Schema
    // ============================================================

    try {
        const raw = parseTable(tableMd);
        const table = new Table(Array.isArray(raw) ? raw[0] : raw);

        const ZodSchema = z.object({
            id: z.coerce.number(),
            name: z.string(),
            active: z.string().transform(v => v === 'yes'),
            score: z.coerce.number()
        });

        const models = table.toModels(ZodSchema);

        assertNotNull(models, "Zod toModels result");
        assert(Array.isArray(models), "Zod toModels should return array");
        assert(models.length === 2, `Expected 2 models`);

        // Verify types
        const alice = models[0];
        assertType(alice.id, "number", "Zod id type");
        assertType(alice.active, "boolean", "Zod active type");
        assert(alice.active === true, `Zod active should be true`);

        console.log("   ✅ toModels (Zod) verified");
    } catch (e) {
        console.error("   ❌ toModels (Zod) failed:", e);
    }

    // ============================================================
    // Mutation API Return Values
    // ============================================================

    try {
        const raw = parseTable(`
| Name | Age |
| --- | --- |
| Alice | 30 |
| Bob | 25 |
`);
        const table = new Table(Array.isArray(raw) ? raw[0] : raw);

        // updateCell should return this
        const afterUpdate = table.updateCell(0, 0, "Updated");
        assert(afterUpdate === table, "updateCell should return this");
        assert(table.rows[0][0] === "Updated", "Cell should be updated");

        // Chaining works
        const chained = table.updateCell(0, 1, "40").updateCell(1, 0, "Charlie");
        assert(chained === table, "Chained calls should return same instance");
        assert(table.rows[0][1] === "40", "First chained update worked");
        assert(table.rows[1][0] === "Charlie", "Second chained update worked");

        assertType(table.metadata, "object", "metadata after chained mutations");

        console.log("   ✅ Mutation API verified");
    } catch (e) {
        console.error("   ❌ Mutation API failed:", e);
    }
}
