/**
 * Test Runner for md-spreadsheet-parser NPM Package E2E Tests
 * 
 * Runs all test modules and reports results.
 * Mirrors Python's pytest structure with individual test files.
 */

import { runParsingTests } from './parsing.test.mjs';
import { runTableTests } from './table.test.mjs';
import { runSheetTests } from './sheet.test.mjs';
import { runWorkbookTests } from './workbook.test.mjs';
import { runToModelsTests } from './tomodels.test.mjs';
import { getResults, resetCounters } from './helpers.mjs';

console.log("=".repeat(60));
console.log("  E2E Tests for md-spreadsheet-parser NPM Package");
console.log("=".repeat(60));

// Run all test modules (some are async)
await runParsingTests();
runTableTests();
runSheetTests();
runWorkbookTests();
runToModelsTests();

// Report results
const { passed, failed } = getResults();

console.log("\n" + "=".repeat(60));
console.log(`  Test Results: ${passed} passed, ${failed} failed`);
console.log("=".repeat(60));

if (failed > 0) {
    console.error("\n❌ Some tests failed!");
    process.exit(1);
} else {
    console.log("\n✅ All tests passed!");
    process.exit(0);
}
