import json

# noinspection PyPackageRequirements
import pytest

from python_trading_objects.quotes import USD, BotPair, Price


# Create a BotPair instance to use the factories
@pytest.fixture
def bot_pair():
    return BotPair("BTC/USD")


# Tests for the Price class
def test_price_creation_via_factory(bot_pair):
    """Test that Price can only be created via the factory."""
    price = bot_pair.create_price(25000.0)
    assert isinstance(price, Price)
    assert price.price == 25000.0
    assert price.get_base() == "BTC"
    assert price.get_quote() == "USD"


def test_price_direct_instantiation_raises_error():
    """Test that direct instantiation of Price raises a TypeError."""
    with pytest.raises(
            TypeError, match="Use BotPair\.create_price\(\) to instantiate Price\."
    ):
        Price(25000.0, "BTC", "USD")


def test_price_str_representation(bot_pair):
    """Test the string representation of Price."""
    price = bot_pair.create_price(25123.45)
    assert str(price) == "25123.45 BTC/USD"


def test_price_add(bot_pair):
    """Test addition of two Price instances."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(5000.0)
    result = price1 + price2
    assert isinstance(result, Price)
    assert result.price == 25000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_sub(bot_pair):
    """Test subtraction of two Price instances."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(5000.0)
    result = price1 - price2
    assert isinstance(result, Price)
    assert result.price == 15000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_truediv_by_float(bot_pair):
    """Test division of a Price by a float."""
    price = bot_pair.create_price(20000.0)
    result = price / 2.0
    assert isinstance(result, Price)
    assert result.price == 10000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_truediv_by_price(bot_pair):
    """Test division of a Price by another Price."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(5000.0)
    result = price1 / price2
    assert isinstance(result, float)
    assert result == 4.0


def test_price_division_by_zero_float_raises_error(bot_pair):
    """Test that division of a Price by zero float raises a ZeroDivisionError."""
    price = bot_pair.create_price(100.0)
    with pytest.raises(ZeroDivisionError):
        _ = price / 0.0


def test_price_division_by_zero_price_raises_error(bot_pair):
    """Test that division of a Price by a zero-value Price raises a ZeroDivisionError."""
    price1 = bot_pair.create_price(100.0)
    price2 = bot_pair.create_price(0.0)
    with pytest.raises(ZeroDivisionError):
        _ = price1 / price2


def test_price_mul_by_float(bot_pair):
    """Test multiplication of a Price by a float."""
    price = bot_pair.create_price(20000.0)
    result = price * 1.5
    assert isinstance(result, Price)
    assert result.price == 30000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_mul_by_token(bot_pair):
    """Test multiplication of a Price by a Token (quantity)."""
    price = bot_pair.create_price(20000.0)  # 20000 USD/BTC
    token = bot_pair.create_token(0.5)  # 0.5 BTC
    result = price * token
    assert isinstance(result, USD)
    assert result.amount == 10000.0  # 20000 * 0.5
    assert result.get_quote() == "USD"


def test_price_equality(bot_pair):
    """Test equality between two Price instances."""
    price1 = bot_pair.create_price(25000.0)
    price2 = bot_pair.create_price(25000.0)
    price3 = bot_pair.create_price(20000.0)
    assert price1 == price2
    assert price1 != price3


def test_price_less_than(bot_pair):
    """Test 'less than' comparison between two Price instances."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(25000.0)
    assert price1 < price2
    assert not (price2 < price1)


def test_price_less_than_or_equal(bot_pair):
    """Test 'less than or equal' comparison between two Price instances."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(20000.0)
    price3 = bot_pair.create_price(25000.0)
    assert price1 <= price2
    assert price1 <= price3
    assert not (price3 <= price1)


def test_price_greater_than(bot_pair):
    """Test 'greater than' comparison between two Price instances."""
    price1 = bot_pair.create_price(25000.0)
    price2 = bot_pair.create_price(20000.0)
    assert price1 > price2
    assert not (price2 > price1)


def test_price_greater_than_or_equal(bot_pair):
    """Test 'greater than or equal' comparison between two Price instances."""
    price1 = bot_pair.create_price(25000.0)
    price2 = bot_pair.create_price(25000.0)
    price3 = bot_pair.create_price(20000.0)
    assert price1 >= price2
    assert price1 >= price3
    assert not (price3 >= price1)


def test_price_to_dict(bot_pair):
    """Test conversion of Price to dictionary."""
    price = bot_pair.create_price(25000.0)
    assert price.to_dict() == {"price": 25000.0}


def test_price_to_json(bot_pair):
    """Test conversion of Price to JSON."""
    price = bot_pair.create_price(25000.0)
    assert json.loads(price.to_json()) == {"price": 25000.0}


def test_price_zero_constant(bot_pair):
    """Test that the zero constant is correctly initialized."""
    assert bot_pair.zero_price().price == 0.0
    assert bot_pair.zero_price().get_base() == "BTC"
    assert bot_pair.zero_price().get_quote() == "USD"
    # Ensure it's indeed a Price instance
    assert isinstance(bot_pair.zero_price(), Price)
