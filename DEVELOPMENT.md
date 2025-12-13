# Development Guide

This document provides a comprehensive guide for developers contributing to `md-spreadsheet-parser`.
It focuses on maintaining code quality, ensuring type safety, and following a consistent development workflow.

## 1. Environment Setup

We use **[uv](https://github.com/astral-sh/uv)** for dependency management and virtual environments.

### Prerequisites
- Python 3.12+
- `uv` installed

### Setup Command
Clone the repository and sync dependencies:

```bash
git clone https://github.com/f-y/md-spreadsheet-parser.git
cd md-spreadsheet-parser
uv sync
```
This creates a virtual environment in `.venv` with all dev dependencies (`pytest`, `ruff`, `mypy`, `pandas-stubs` etc.).

## 2. Quality Assurance Tools

We enforce strict quality standards using the following tools.
**You must ensure all checks pass locally before opening a Pull Request.**

### Linting & Formatting (Ruff)
We use `ruff` (configured in `pyproject.toml`) for both linting and formatting.

```bash
# Check for lint errors
uv run ruff check .

# Auto-fix lint errors
uv run ruff check --fix .

# Check formatting
uv run ruff format --check .

# Auto-format code
uv run ruff format .
```

### Type Checking (Mypy)
We use `mypy` for static type checking. The codebase is fully typed.

```bash
uv run mypy .
```
> **Note**: If you encounter missing stubs errors, ensure `pandas-stubs` is installed (it is included in `dev` dependencies).

### Testing (Pytest)
We use `pytest` for unit and integration testing.

```bash
# Run all tests
uv run pytest

# Run with coverage (optional)
uv run pytest --cov=src
```

## 3. Development Workflow

### A. Implementing Features/Fixes
1.  **Branching**: Create a feature branch from `main`.
2.  **TDD**: Write a failing test case in `tests/` reproducing the bug or defining the new feature.
3.  **Implement**: Write code to pass the test.
4.  **Verify**: Run the full suite (`pytest`, `ruff`, `mypy`).

### B. Project Structure
- `src/md_spreadsheet_parser/`: Core library code.
    - `schemas.py`: Configuration schemas (Dataclasses).
    - `models.py`: Data structures (Table, Workbook).
    - `parser.py`: Core parsing logic.
    - `generator.py`: Markdown generation logic.
    - `validation.py`: Type validation and conversion logic.
- `tests/`: Test suite matching source structure.

## 4. Pull Request Checklist

When submitting a PR, please confirm:

- [ ] **Tests**: New tests added for new features? All existing tests pass?
- [ ] **Linting**: `uv run ruff check .` passes with no errors?
- [ ] **Formatting**: Code is formatted via `uv run ruff format .`?
- [ ] **Typing**: `uv run mypy .` passes with "Success: no issues found"?
- [ ] **Documentation**: `README.md` updated if public API changed?
