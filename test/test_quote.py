import json
from decimal import Decimal

# noinspection PyPackageRequirements
import pytest

from python_trading_objects.quotes import (  # Pour tester les classes filles concrètes
    BotPair, Quote, Token)
from python_trading_objects.quotes.assertion import bot_assert


# from typing import re # Removed as re.escape is no longer used directly


# Create a BotPair instance to use the factories
@pytest.fixture
def bot_pair():
    return BotPair("BTC/USD")


# Tests for the bot_assert function
def test_bot_assert_valid_type():
    """Test that bot_assert does not raise an error for a valid type."""
    bot_assert(10.0, float)
    bot_assert("hello", str)
    bot_assert(1, (int, float))


def test_bot_assert_invalid_type_raises_error():
    """Test that bot_assert raises a TypeError for an invalid type."""
    # Manually escape special characters for regex matching
    with pytest.raises(
        TypeError, match="Le paramètre doit être de type <class 'float'>"
    ):
        bot_assert(10, float)  # 10 is an int, not a float (strict check for float)
    with pytest.raises(TypeError, match="Le paramètre doit être de type <class 'str'>"):
        bot_assert(123, str)  # 123 is an int, not a string
    # Escape parentheses, angle brackets, and periods for the tuple representation
    with pytest.raises(
        TypeError,
        match=r"Le paramètre doit être de type \(<class 'int'>, <class 'float'>\)",
    ):
        bot_assert(
            "not a number", (int, float)
        )  # "not a number" is a string, not int or float


# Tests for the Quote class (via a concrete class if necessary, as Quote is abstract)
def test_quote_set_precision():
    """Test the static method set_precision."""
    initial_precision_token = Quote.precisions.get("Token")
    initial_precision_usd = Quote.precisions.get("USD")

    Quote.set_precision("Token", 6)
    Quote.set_precision("USD", 3)

    assert Quote.precisions["Token"] == 6
    assert Quote.precisions["USD"] == 3

    # Restore default precisions to not affect other tests
    Quote.set_precision("Token", initial_precision_token)
    Quote.set_precision("USD", initial_precision_usd)


def test_quote_truncate_to_precision_token(bot_pair):
    """Test value truncation for Token precision."""
    # Temporarily set precision for the specific truncation test
    original_precision = Quote.precisions.get("Token")
    Quote.set_precision("Token", 5)

    token = bot_pair.create_token(123.456789123)
    assert token.amount == Decimal("123.45678")

    Quote.set_precision("Token", original_precision)  # Restore


def test_quote_truncate_to_precision_usd(bot_pair):
    """Test value truncation for USD precision."""
    # Temporarily set precision for the specific truncation test
    original_precision = Quote.precisions.get("USD")
    Quote.set_precision("USD", 2)

    usd = bot_pair.create_usd(123.456789)
    assert usd.amount == Decimal("123.45")

    Quote.set_precision("USD", original_precision)  # Restore


def test_quote_equality_different_types_raises_error(bot_pair):
    """Test that equality comparison between Quote and non-Quote type raises a TypeError."""
    token = bot_pair.create_token(10.0)
    # Manually escape special characters for regex matching
    expected_error_message_regex = r"Le paramètre doit être de type <class 'python_trading_objects\.quotes\.quote\.Quote'>"
    with pytest.raises(TypeError, match=expected_error_message_regex):
        _ = token == 10.0  # Comparison with a float, not a Quote instance


def test_quote_get_child_class(bot_pair):
    """Test that get_child_class returns the concrete class."""
    token = bot_pair.create_token(1.0)
    assert token.get_child_class() == Token


def test_quote_to_dict(bot_pair):
    """Test conversion of Quote (via Token) to dictionary."""
    token = bot_pair.create_token(1.234)
    assert token.to_dict() == {"price": "1.23400"}


def test_quote_to_json(bot_pair):
    """Test conversion of Quote (via Token) to JSON."""
    token = bot_pair.create_token(1.234)
    assert json.loads(token.to_json()) == {"price": "1.23400"}
