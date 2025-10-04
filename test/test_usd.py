import json
from decimal import Decimal

# noinspection PyPackageRequirements
import pytest

from python_trading_objects.quotes import USD, BotPair, Token


# Create a BotPair instance to use the factories
@pytest.fixture
def bot_pair():
    return BotPair("BTC/USD")


# Tests for the USD class
def test_usd_creation_via_factory(bot_pair):
    """Test that USD can only be created via the factory."""
    usd = bot_pair.create_usd(100.0)
    assert isinstance(usd, USD)
    assert usd.amount == 100.0
    assert usd.get_quote() == "USD"


def test_usd_direct_instantiation_raises_error():
    """Test that direct instantiation of USD raises a TypeError."""
    # Manually escape parentheses for regex matching
    with pytest.raises(
            TypeError, match=r"Use BotPair\.create_usd\(\) to instantiate USD\."
    ):
        USD(100.0, "USD")


def test_usd_str_representation(bot_pair):
    """Test the string representation of USD."""
    usd = bot_pair.create_usd(123.45)
    assert str(usd) == "123.45 USD"


def test_usd_equality(bot_pair):
    """Test equality between two USD instances."""
    usd1 = bot_pair.create_usd(100.0)
    usd2 = bot_pair.create_usd(100.0)
    usd3 = bot_pair.create_usd(50.0)
    assert usd1 == usd2
    assert usd1 != usd3


def test_usd_less_than_other_usd(bot_pair):
    """Test 'less than' comparison between two USD instances."""
    usd1 = bot_pair.create_usd(50.0)
    usd2 = bot_pair.create_usd(100.0)
    assert usd1 < usd2
    assert not (usd2 < usd1)


def test_usd_less_than_float(bot_pair):
    """Test 'less than' comparison between USD and a float."""
    usd = bot_pair.create_usd(75.0)
    assert usd < 100.0
    assert not (usd < 50.0)


def test_usd_add_usds(bot_pair):
    """Test addition of two USD instances."""
    usd1 = bot_pair.create_usd(50.0)
    usd2 = bot_pair.create_usd(30.0)
    result = usd1 + usd2
    assert isinstance(result, USD)
    assert result.amount == 80.0
    assert result.get_quote() == "USD"


def test_usd_radd_with_float(bot_pair):
    """Test reverse addition with a float."""
    usd = bot_pair.create_usd(50.0)
    result = 30.0 + usd
    assert isinstance(result, USD)
    assert result.amount == 80.0
    assert result.get_quote() == "USD"


def test_usd_sub_usds(bot_pair):
    """Test subtraction of two USD instances."""
    usd1 = bot_pair.create_usd(100.0)
    usd2 = bot_pair.create_usd(30.0)
    result = usd1 - usd2
    assert isinstance(result, USD)
    assert result.amount == 70.0
    assert result.get_quote() == "USD"


def test_usd_negation(bot_pair):
    """Test negation of a USD instance."""
    usd = bot_pair.create_usd(50.0)
    result = -usd
    assert isinstance(result, USD)
    assert result.amount == -50.0
    assert result.get_quote() == "USD"


def test_usd_mul_by_float(bot_pair):
    """Test multiplication of a USD by a float."""
    usd = bot_pair.create_usd(50.0)
    result = usd * 2.5
    assert isinstance(result, USD)
    assert result.amount == 125.0
    assert result.get_quote() == "USD"


def test_usd_truediv_by_float(bot_pair):
    """Test division of a USD by a float."""
    usd = bot_pair.create_usd(100.0)
    result = usd / 2.0
    assert isinstance(result, USD)
    assert result.amount == 50.0
    assert result.get_quote() == "USD"


def test_usd_truediv_by_usd(bot_pair):
    """Test division of a USD by another USD."""
    usd1 = bot_pair.create_usd(100.0)
    usd2 = bot_pair.create_usd(20.0)
    result = usd1 / usd2
    assert isinstance(result, Decimal)
    assert result == Decimal("5.0")


def test_usd_truediv_by_price(bot_pair):
    """Test division of a USD by a Price."""
    usd = bot_pair.create_usd(10000.0)
    price = bot_pair.create_price(20000.0)  # 20000 USD/BTC
    result = usd / price
    assert isinstance(result, Token)
    assert result.amount == 0.5  # 10000 / 20000
    assert result.get_base() == "BTC"


def test_usd_division_by_zero_float_raises_error(bot_pair):
    """Test that division of a USD by zero float raises a ZeroDivisionError."""
    usd = bot_pair.create_usd(100.0)
    with pytest.raises(ZeroDivisionError):
        _ = usd / 0.0


def test_usd_division_by_zero_usd_raises_error(bot_pair):
    """Test that division of a USD by a zero-value USD raises a ZeroDivisionError."""
    usd1 = bot_pair.create_usd(100.0)
    usd2 = bot_pair.create_usd(0.0)
    with pytest.raises(ZeroDivisionError):
        _ = usd1 / usd2


def test_usd_division_by_zero_price_raises_error(bot_pair):
    """Test that division of a USD by a zero-value Price raises a ZeroDivisionError."""
    usd = bot_pair.create_usd(100.0)
    price_zero = bot_pair.create_price(0.0)
    with pytest.raises(ZeroDivisionError):
        _ = usd / price_zero


def test_usd_to_dict(bot_pair):
    """Test conversion of USD to dictionary."""
    usd = bot_pair.create_usd(42.50)
    assert usd.to_dict() == {"price": "42.50"}


def test_usd_to_json(bot_pair):
    """Test conversion of USD to JSON."""
    usd = bot_pair.create_usd(42.50)
    assert json.loads(usd.to_json()) == {"price": "42.50"}


def test_usd_zero_constant(bot_pair):
    """Test that the zero constant is correctly initialized."""
    assert bot_pair.zero_usd().amount == 0.0
    assert bot_pair.zero_usd().get_quote() == "USD"
    # Ensure it's indeed a USD instance
    assert isinstance(bot_pair.zero_usd(), USD)
