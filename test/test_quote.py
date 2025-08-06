import json

import pytest

from venantvr.quotes.assertion import bot_assert
from venantvr.quotes import Token  # Pour tester les classes filles concrètes
from venantvr.quotes import BotPair
from venantvr.quotes import Quote


# from typing import re # Removed as re.escape is no longer used directly


# Crée une instance de BotPair pour utiliser les factories
@pytest.fixture
def bot_pair():
    return BotPair("BTC/USD")


# Tests pour la fonction bot_assert
def test_bot_assert_valid_type():
    """Test que bot_assert ne lève pas d'erreur pour un type valide."""
    bot_assert(10.0, float)
    bot_assert("hello", str)
    bot_assert(1, (int, float))


def test_bot_assert_invalid_type_raises_error():
    """Test que bot_assert lève une TypeError pour un type invalide."""
    # Manually escape special characters for regex matching
    with pytest.raises(TypeError, match="Le paramètre doit être de type <class 'float'>"):
        bot_assert(10, float)  # 10 is an int, not a float (strict check for float)
    with pytest.raises(TypeError, match="Le paramètre doit être de type <class 'str'>"):
        bot_assert(123, str)  # 123 is an int, not a string
    # Escape parentheses, angle brackets, and periods for the tuple representation
    with pytest.raises(TypeError, match=r"Le paramètre doit être de type \(<class 'int'>, <class 'float'>\)"):
        bot_assert("not a number", (int, float))  # "not a number" is a string, not int or float


# Tests pour la classe Quote (via une classe concrète si nécessaire, car Quote est abstraite)
def test_quote_set_precision():
    """Test la méthode statique set_precision."""
    initial_precision_token = Quote.precisions.get("Token")
    initial_precision_usd = Quote.precisions.get("USD")

    Quote.set_precision("Token", 6)
    Quote.set_precision("USD", 3)

    assert Quote.precisions["Token"] == 6
    assert Quote.precisions["USD"] == 3

    # Restaurer les précisions par défaut pour ne pas affecter d'autres tests
    Quote.set_precision("Token", initial_precision_token)
    Quote.set_precision("USD", initial_precision_usd)


def test_quote_truncate_to_precision_token(bot_pair):
    """Test la troncature de valeur pour une précision de Token."""
    # Temporairement définir une précision pour le test de troncature spécifique
    original_precision = Quote.precisions.get("Token")
    Quote.set_precision("Token", 5)

    token = bot_pair.create_token(123.456789123)
    assert token.amount == 123.45678

    Quote.set_precision("Token", original_precision)  # Restaurer


def test_quote_truncate_to_precision_usd(bot_pair):
    """Test la troncature de valeur pour une précision de USD."""
    # Temporairement définir une précision pour le test de troncature spécifique
    original_precision = Quote.precisions.get("USD")
    Quote.set_precision("USD", 2)

    usd = bot_pair.create_usd(123.456789)
    assert usd.amount == 123.45

    Quote.set_precision("USD", original_precision)  # Restaurer


def test_quote_equality_different_types_raises_error(bot_pair):
    """Test que la comparaison d'égalité entre Quote et un type non-Quote lève une TypeError."""
    token = bot_pair.create_token(10.0)
    # Manually escape special characters for regex matching
    expected_error_message_regex = r"Le paramètre doit être de type <class 'quotes\.quote\.Quote'>"
    with pytest.raises(TypeError, match=expected_error_message_regex):
        _ = token == 10.0  # Comparaison avec un float, pas une instance de Quote


def test_quote_get_child_class(bot_pair):
    """Test que get_child_class retourne la classe concrète."""
    token = bot_pair.create_token(1.0)
    assert token.get_child_class() == Token


def test_quote_to_dict(bot_pair):
    """Test la conversion de Quote (via Token) en dictionnaire."""
    token = bot_pair.create_token(1.234)
    assert token.to_dict() == {"price": 1.234}


def test_quote_to_json(bot_pair):
    """Test la conversion de Quote (via Token) en JSON."""
    token = bot_pair.create_token(1.234)
    assert json.loads(token.to_json()) == {"price": 1.234}
