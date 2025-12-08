from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
import pytest
from md_spreadsheet_parser import parse_table, ConversionSchema

@dataclass
class User:
    name: str
    is_active: bool
    score: int
    price: Optional[Decimal] = None

def test_custom_boolean_pairs_japanese():
    """
    Test using Japanese boolean pairs (Hai/Iie).
    """
    markdown = """
| Name | Is Active | Score |
| --- | --- | --- |
| Tanaka | Hai | 100 |
| Suzuki | Iie | 50 |
"""
    # Define schema with ONLY japanese pairs
    schema = ConversionSchema(
        boolean_pairs=(("hai", "iie"),)
    )
    
    table = parse_table(markdown)
    users = table.to_models(User, conversion_schema=schema)
    
    assert users[0].is_active is True
    assert users[1].is_active is False

def test_strict_boolean_pairs_rejection():
    """
    Test that if we define specific pairs, other pairs (like yes/no) are rejected.
    """
    markdown = """
| Name | Is Active | Score |
| --- | --- | --- |
| Alice | Yes | 10 |
"""
    # Schema knowing only Hai/Iie
    schema = ConversionSchema(
        boolean_pairs=(("hai", "iie"),)
    )
    
    table = parse_table(markdown)
    
    with pytest.raises(Exception) as excinfo:
        table.to_models(User, conversion_schema=schema)
    
    # Validation error should mention invalid boolean
    assert "Invalid boolean value: 'Yes'" in str(excinfo.value)

def test_default_pairs_mixing():
    """
    Test that default schema allows mixing different standard pairs (yes/no, 1/0, true/false).
    """
    markdown = """
| Name | Is Active | Score |
| --- | --- | --- |
| A | Yes | 1 |
| B | 0   | 2 |
| C | True | 3 |
| D | off | 4 |
"""
    table = parse_table(markdown)
    # Default schema used implicitly
    users = table.to_models(User)
    
    assert users[0].is_active is True  # Yes
    assert users[1].is_active is False # 0
    assert users[2].is_active is True  # True
    assert users[3].is_active is False # off

def test_custom_type_converter():
    """
    Test registering a custom converter for Decimal.
    """
    markdown = """
| Name | Is Active | Score | Price |
| --- | --- | --- | --- |
| ItemA | yes | 1 | $10.50 |
| ItemB | yes | 1 | 2,000 |
"""
    
    def parse_currency(value: str) -> Decimal:
        clean = value.replace("$", "").replace(",", "").strip()
        return Decimal(clean)

    schema = ConversionSchema(
        custom_converters={Decimal: parse_currency}
    )
    
    table = parse_table(markdown)
    users = table.to_models(User, conversion_schema=schema)
    
    assert users[0].price == Decimal("10.50")
    assert users[1].price == Decimal("2000")

def test_case_insensitivity():
    """
    Test that boolean pairs are case insensitive.
    """
    markdown = """
| Name | Is Active | Score |
| --- | --- | --- |
| A | はい | 1 |
| B | いいえ | 0 |
"""
    schema = ConversionSchema(
        boolean_pairs=(("はい", "いいえ"),)
    )
    
    table = parse_table(markdown)
    users = table.to_models(User, conversion_schema=schema)
    
    assert users[0].is_active is True
    assert users[1].is_active is False

def test_field_specific_converter():
    """
    Test using different converters for different fields of the same type.
    """
    @dataclass
    class Product:
        price_usd: Decimal
        price_jpy: Decimal
        
    markdown = """
| Price USD | Price JPY |
| --- | --- |
| $10 | ¥1,000 |
"""
    
    def parse_usd(v: str) -> Decimal:
        return Decimal(v.replace("$", "").strip())
        
    def parse_jpy(v: str) -> Decimal:
        return Decimal(v.replace("¥", "").replace(",", "").strip())

    schema = ConversionSchema(
        field_converters={
            "price_usd": parse_usd,
            "price_jpy": parse_jpy
        }
    )
    
    table = parse_table(markdown)
    products = table.to_models(Product, conversion_schema=schema)
    
    assert products[0].price_usd == Decimal("10")
    assert products[0].price_jpy == Decimal("1000")

def test_field_converter_overrides_type_converter():
    """
    Test that a field-specific converter takes precedence over the type-based converter.
    """
    @dataclass
    class Item:
        val1: int
        val2: int # Special
        
    markdown = """
| Val1 | Val2 |
| --- | --- |
| 10 | 10 |
"""

    def parse_double(v: str) -> int:
        return int(v) * 2

    schema = ConversionSchema(
        custom_converters={int: lambda x: int(x)}, # Standard logic explicitly
        field_converters={
            "val2": parse_double
        }
    )
    
    table = parse_table(markdown)
    items = table.to_models(Item, conversion_schema=schema)
    
    assert items[0].val1 == 10 # Uses default/type converter (10)
    assert items[0].val2 == 20 # Uses field converter (10 * 2)
