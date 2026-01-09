/**
 * Test Helper Functions for md-spreadsheet-parser NPM E2E Tests
 * 
 * These helpers mirror the assertion patterns used in Python tests,
 * providing consistent validation especially for metadata type safety.
 */

// Test results tracking
export let passed = 0;
export let failed = 0;

export function resetCounters() {
    passed = 0;
    failed = 0;
}

export function assert(condition, message) {
    if (!condition) {
        console.error(`   ❌ FAIL: ${message}`);
        failed++;
        return false;
    }
    passed++;
    return true;
}

export function assertType(value, expectedType, name) {
    const actualType = typeof value;
    return assert(actualType === expectedType,
        `${name} should be ${expectedType}, got ${actualType}`);
}

export function assertNotNull(value, name) {
    return assert(value !== null && value !== undefined,
        `${name} should not be null/undefined`);
}

export function assertInstanceOf(value, cls, name) {
    return assert(value instanceof cls,
        `${name} should be instance of ${cls.name}`);
}

export function assertEqual(actual, expected, name) {
    const actualStr = JSON.stringify(actual);
    const expectedStr = JSON.stringify(expected);
    return assert(actualStr === expectedStr,
        `${name} should be ${expectedStr}, got ${actualStr}`);
}

export function assertArrayEqual(actual, expected, name) {
    if (!Array.isArray(actual) || !Array.isArray(expected)) {
        return assert(false, `${name}: both values should be arrays`);
    }
    if (actual.length !== expected.length) {
        return assert(false, `${name}: length mismatch (${actual.length} vs ${expected.length})`);
    }
    for (let i = 0; i < actual.length; i++) {
        if (JSON.stringify(actual[i]) !== JSON.stringify(expected[i])) {
            return assert(false, `${name}[${i}] mismatch`);
        }
    }
    passed++;
    return true;
}

/**
 * Critical metadata validation - ensures metadata is object, NOT string.
 * This was a past bug where metadata came back as JSON string after operations.
 */
export function assertMetadataIsObject(metadata, name) {
    if (!assertType(metadata, "object", name)) return false;
    return assert(typeof metadata !== "string",
        `${name} should NOT be string (was serialized incorrectly)`);
}

/**
 * Assert that an async function throws an error with expected message pattern.
 */
export async function assertThrowsAsync(fn, messagePattern, name) {
    try {
        await fn();
        console.error(`   ❌ FAIL: ${name} should have thrown`);
        failed++;
        return false;
    } catch (e) {
        if (messagePattern && !e.message.includes(messagePattern)) {
            console.error(`   ❌ FAIL: ${name} error message should include "${messagePattern}", got "${e.message}"`);
            failed++;
            return false;
        }
        passed++;
        return true;
    }
}

export function getResults() {
    return { passed, failed };
}
