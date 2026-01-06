---
title: Fix WASI File Access
type: fix
---

Fixed an issue where `parseWorkbookFromFile` failed with `FileNotFoundError` in the NPM package environment.

- Configured WASI preopens to map the system root (e.g., `/` on macOS, `C:\` on Windows) to the Guest root.
- Implemented `resolveToVirtualPath` to automatically resolve relative paths against the Host's CWD and absolute paths against the system root.
- `parseWorkbookFromFile` now correctly handles both relative and absolute paths in Node.js environments.
