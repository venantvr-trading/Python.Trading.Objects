import json
from decimal import Decimal

# noinspection PyPackageRequirements
import pytest

from python_trading_objects.quotes import USD, BotPair, Token


# Create a BotPair instance to use the factories
@pytest.fixture
def bot_pair():
    return BotPair("BTC/USD")


# Tests for the Token class
def test_token_creation_via_factory(bot_pair):
    """Test that Token can only be created via the factory."""
    token = bot_pair.create_token(10.0)
    assert isinstance(token, Token)
    assert token.amount == 10.0
    assert token.get_base() == "BTC"


def test_token_direct_instantiation_raises_error():
    """Test that direct instantiation of Token raises a TypeError."""
    with pytest.raises(
            TypeError, match=r"Use BotPair\.create_token\(\) to instantiate Token\."
    ):
        Token(10.0, "BTC")


def test_token_str_representation(bot_pair):
    """Test the string representation of Token."""
    token = bot_pair.create_token(5.12345678)
    assert str(token) == "5.12345000 BTC"


def test_token_equality(bot_pair):
    """Test equality between two Token instances."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(10.0)
    token3 = bot_pair.create_token(5.0)
    assert token1 == token2
    assert token1 != token3


def test_token_less_than_other_token(bot_pair):
    """Test 'less than' comparison between two Token instances."""
    token1 = bot_pair.create_token(5.0)
    token2 = bot_pair.create_token(10.0)
    assert token1 < token2
    assert not (token2 < token1)


def test_token_less_than_float(bot_pair):
    """Test 'less than' comparison between Token and a float."""
    token = bot_pair.create_token(7.5)
    assert token < 10.0
    assert not (token < 5.0)


def test_token_add_tokens(bot_pair):
    """Test addition of two Token instances."""
    token1 = bot_pair.create_token(5.0)
    token2 = bot_pair.create_token(3.0)
    result = token1 + token2
    assert isinstance(result, Token)
    assert result.amount == 8.0
    assert result.get_base() == "BTC"


def test_token_radd_with_float(bot_pair):
    """Test reverse addition with a float."""
    token = bot_pair.create_token(5.0)
    result = 3.0 + token
    assert isinstance(result, Token)
    assert result.amount == 8.0
    assert result.get_base() == "BTC"


def test_token_sub_tokens(bot_pair):
    """Test subtraction of two Token instances."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(3.0)
    result = token1 - token2
    assert isinstance(result, Token)
    assert result.amount == 7.0
    assert result.get_base() == "BTC"


def test_token_negation(bot_pair):
    """Test negation of a Token instance."""
    token = bot_pair.create_token(5.0)
    result = -token
    assert isinstance(result, Token)
    assert result.amount == -5.0
    assert result.get_base() == "BTC"


def test_token_mul_by_float(bot_pair):
    """Test multiplication of a Token by a float."""
    token = bot_pair.create_token(5.0)
    result = token * 2.5
    assert isinstance(result, Token)
    assert result.amount == 12.5
    assert result.get_base() == "BTC"


def test_token_mul_by_price(bot_pair):
    """Test multiplication of a Token by a Price."""
    token = bot_pair.create_token(2.0)
    price = bot_pair.create_price(20000.0)  # 20000 USD/BTC
    result = token * price
    assert isinstance(result, USD)
    assert isinstance(result.amount, Decimal)
    assert result.amount == Decimal("40000.00")
    assert result.get_quote() == "USD"


def test_token_truediv_by_float(bot_pair):
    """Test division of a Token by a float."""
    token = bot_pair.create_token(10.0)
    result = token / 2.0
    assert isinstance(result, Token)
    assert result.amount == 5.0
    assert result.get_base() == "BTC"


def test_token_truediv_by_token(bot_pair):
    """Test division of a Token by another Token."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(2.0)
    result = token1 / token2
    assert isinstance(result, Decimal)
    assert result == Decimal("5")


def test_token_division_by_zero_float_raises_error(bot_pair):
    """Test that division of a Token by zero float raises a ZeroDivisionError."""
    token = bot_pair.create_token(10.0)
    with pytest.raises(ZeroDivisionError):
        _ = token / 0.0


def test_token_division_by_zero_token_raises_error(bot_pair):
    """Test that division of a Token by a zero-value Token raises a ZeroDivisionError."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(0.0)
    with pytest.raises(ZeroDivisionError):
        _ = token1 / token2


def test_token_to_dict(bot_pair):
    """Test conversion of Token to dictionary."""
    token = bot_pair.create_token(1.23)
    result = token.to_dict()
    assert isinstance(result["price"], str)
    assert result["price"] == "1.23000"  # Tronqué à précision 5


def test_token_to_json(bot_pair):
    """Test conversion of Token to JSON."""
    token = bot_pair.create_token(1.23)
    result = json.loads(token.to_json())
    assert isinstance(result["price"], str)
    assert result["price"] == "1.23000"
