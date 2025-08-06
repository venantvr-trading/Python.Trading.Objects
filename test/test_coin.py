import json

import pytest

from venantvr.quotes import Token
from venantvr.quotes import BotPair
from venantvr.quotes import USD


# Crée une instance de BotPair pour utiliser les factories
@pytest.fixture
def bot_pair():
    return BotPair("BTC/USD")


# Tests pour la classe Token
def test_token_creation_via_factory(bot_pair):
    """Test que Token ne peut être créé que via la factory."""
    token = bot_pair.create_token(10.0)
    assert isinstance(token, Token)
    assert token.amount == 10.0
    assert token.get_base() == "BTC"


def test_token_direct_instantiation_raises_error():
    """Test qu'une instanciation directe de Token lève une TypeError."""
    with pytest.raises(TypeError, match=r"Use BotPair\.create_token\(\) to instantiate Token\."):
        Token(10.0, "BTC")


def test_token_str_representation(bot_pair):
    """Test la représentation en chaîne de caractères de Token."""
    token = bot_pair.create_token(5.12345678)
    assert str(token) == "5.12345000 BTC"


def test_token_equality(bot_pair):
    """Test l'égalité entre deux instances de Token."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(10.0)
    token3 = bot_pair.create_token(5.0)
    assert token1 == token2
    assert token1 != token3


def test_token_less_than_other_token(bot_pair):
    """Test la comparaison 'inférieur à' entre deux instances de Token."""
    token1 = bot_pair.create_token(5.0)
    token2 = bot_pair.create_token(10.0)
    assert token1 < token2
    assert not (token2 < token1)


def test_token_less_than_float(bot_pair):
    """Test la comparaison 'inférieur à' entre Token et un float."""
    token = bot_pair.create_token(7.5)
    assert token < 10.0
    assert not (token < 5.0)


def test_token_add_tokens(bot_pair):
    """Test l'addition de deux instances de Token."""
    token1 = bot_pair.create_token(5.0)
    token2 = bot_pair.create_token(3.0)
    result = token1 + token2
    assert isinstance(result, Token)
    assert result.amount == 8.0
    assert result.get_base() == "BTC"


def test_token_radd_with_float(bot_pair):
    """Test l'addition inversée avec un float."""
    token = bot_pair.create_token(5.0)
    result = 3.0 + token
    assert isinstance(result, Token)
    assert result.amount == 8.0
    assert result.get_base() == "BTC"


def test_token_sub_tokens(bot_pair):
    """Test la soustraction de deux instances de Token."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(3.0)
    result = token1 - token2
    assert isinstance(result, Token)
    assert result.amount == 7.0
    assert result.get_base() == "BTC"


def test_token_negation(bot_pair):
    """Test la négation d'une instance de Token."""
    token = bot_pair.create_token(5.0)
    result = -token
    assert isinstance(result, Token)
    assert result.amount == -5.0
    assert result.get_base() == "BTC"


def test_token_mul_by_float(bot_pair):
    """Test la multiplication d'un Token par un float."""
    token = bot_pair.create_token(5.0)
    result = token * 2.5
    assert isinstance(result, Token)
    assert result.amount == 12.5
    assert result.get_base() == "BTC"


def test_token_mul_by_price(bot_pair):
    """Test la multiplication d'un Token par un Price."""
    token = bot_pair.create_token(2.0)
    price = bot_pair.create_price(20000.0)  # 20000 USD/BTC
    result = token * price
    assert isinstance(result, USD)
    assert result.amount == 40000.0
    assert result.get_quote() == "USD"


def test_token_truediv_by_float(bot_pair):
    """Test la division d'un Token par un float."""
    token = bot_pair.create_token(10.0)
    result = token / 2.0
    assert isinstance(result, Token)
    assert result.amount == 5.0
    assert result.get_base() == "BTC"


def test_token_truediv_by_token(bot_pair):
    """Test la division d'un Token par un autre Token."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(2.0)
    result = token1 / token2
    assert isinstance(result, float)
    assert result == 5.0


def test_token_division_by_zero_float_raises_error(bot_pair):
    """Test que la division d'un Token par zéro float lève une ZeroDivisionError."""
    token = bot_pair.create_token(10.0)
    with pytest.raises(ZeroDivisionError):
        _ = token / 0.0


def test_token_division_by_zero_token_raises_error(bot_pair):
    """Test que la division d'un Token par un Token de valeur zéro lève une ZeroDivisionError."""
    token1 = bot_pair.create_token(10.0)
    token2 = bot_pair.create_token(0.0)
    with pytest.raises(ZeroDivisionError):
        _ = token1 / token2


def test_token_to_dict(bot_pair):
    """Test la conversion de Token en dictionnaire."""
    token = bot_pair.create_token(1.23)
    assert token.to_dict() == {"price": 1.23}


def test_token_to_json(bot_pair):
    """Test la conversion de Token en JSON."""
    token = bot_pair.create_token(1.23)
    assert json.loads(token.to_json()) == {"price": 1.23}
