import pytest
from dataclasses import dataclass
from md_spreadsheet_parser import parse_table, TableValidationError


@dataclass
class User:
    id: int
    name: str
    is_active: bool
    score: float
    email: str | None = None


def test_basic_validation():
    markdown = """
| ID | Name  | Is Active | Score | Email          |
| -- | ----- | --------- | ----- | -------------- |
| 1  | Alice | true      | 95.5  | alice@test.com |
| 2  | Bob   | 0         | 80.0  |                |
"""
    # Use parse_table to get a Table object, then call to_models
    table = parse_table(markdown)
    users = table.to_models(User)

    assert len(users) == 2

    u1 = users[0]
    assert u1.id == 1
    assert u1.name == "Alice"
    assert u1.is_active is True
    assert u1.score == 95.5
    assert u1.email == "alice@test.com"

    u2 = users[1]
    assert u2.id == 2
    assert u2.name == "Bob"
    assert u2.is_active is False
    assert u2.score == 80.0
    assert u2.email is None


def test_validation_error_types():
    markdown = """
| ID | Name | Is Active | Score |
| -- | ---- | --------- | ----- |
| 1  | Alice| not_bool  | 95.5  |
| X  | Bob  | true      | 80.0  |
"""
    table = parse_table(markdown)
    with pytest.raises(TableValidationError) as excinfo:
        table.to_models(User)

    errors = excinfo.value.errors
    assert len(errors) == 2
    assert "Row 1: Column 'is_active': Invalid boolean value: 'not_bool'" in errors[0]
    assert (
        "Row 2: Column 'id': invalid literal for int()" in errors[1]
        or "Row 2: Column 'id': Failed to convert" in errors[1]
    )


def test_missing_required_field():
    # 'score' is required but missing from header
    markdown = """
| ID | Name | Is Active |
| -- | ---- | --------- |
| 1  | Alice| true      |
"""
    table = parse_table(markdown)
    with pytest.raises(TableValidationError) as excinfo:
        table.to_models(User)

    assert "missing 1 required positional argument: 'score'" in excinfo.value.errors[0]


def test_not_a_dataclass():
    class NotDataclass:
        pass

    table = parse_table("| A |")
    with pytest.raises(ValueError, match="must be a dataclass"):
        table.to_models(NotDataclass)


def test_header_normalization():
    @dataclass
    class Config:
        api_key: str
        max_retries: int

    markdown = """
| API Key | Max Retries |
| ------- | ----------- |
| abc     | 3           |
"""
    table = parse_table(markdown)
    configs = table.to_models(Config)
    assert configs[0].api_key == "abc"
    assert configs[0].max_retries == 3
