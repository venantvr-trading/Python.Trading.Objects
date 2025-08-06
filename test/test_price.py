import json

import pytest

from venantvr.quotes import BotPair
from venantvr.quotes import Price
from venantvr.quotes import USD


# Crée une instance de BotPair pour utiliser les factories
@pytest.fixture
def bot_pair():
    return BotPair("BTC/USD")


# Tests pour la classe Price
def test_price_creation_via_factory(bot_pair):
    """Test que Price ne peut être créé que via la factory."""
    price = bot_pair.create_price(25000.0)
    assert isinstance(price, Price)
    assert price.price == 25000.0
    assert price.get_base() == "BTC"
    assert price.get_quote() == "USD"


def test_price_direct_instantiation_raises_error():
    """Test qu'une instanciation directe de Price lève une TypeError."""
    with pytest.raises(TypeError, match="Use BotPair\.create_price\(\) to instantiate Price\."):
        Price(25000.0, "BTC", "USD")


def test_price_str_representation(bot_pair):
    """Test la représentation en chaîne de caractères de Price."""
    price = bot_pair.create_price(25123.45)
    assert str(price) == "25123.45 BTC/USD"


def test_price_add(bot_pair):
    """Test l'addition de deux instances de Price."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(5000.0)
    result = price1 + price2
    assert isinstance(result, Price)
    assert result.price == 25000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_sub(bot_pair):
    """Test la soustraction de deux instances de Price."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(5000.0)
    result = price1 - price2
    assert isinstance(result, Price)
    assert result.price == 15000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_truediv_by_float(bot_pair):
    """Test la division d'un Price par un float."""
    price = bot_pair.create_price(20000.0)
    result = price / 2.0
    assert isinstance(result, Price)
    assert result.price == 10000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_truediv_by_price(bot_pair):
    """Test la division d'un Price par un autre Price."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(5000.0)
    result = price1 / price2
    assert isinstance(result, float)
    assert result == 4.0


def test_price_division_by_zero_float_raises_error(bot_pair):
    """Test que la division d'un Price par zéro float lève une ZeroDivisionError."""
    price = bot_pair.create_price(100.0)
    with pytest.raises(ZeroDivisionError):
        _ = price / 0.0


def test_price_division_by_zero_price_raises_error(bot_pair):
    """Test que la division d'un Price par un Price de valeur zéro lève une ZeroDivisionError."""
    price1 = bot_pair.create_price(100.0)
    price2 = bot_pair.create_price(0.0)
    with pytest.raises(ZeroDivisionError):
        _ = price1 / price2


def test_price_mul_by_float(bot_pair):
    """Test la multiplication d'un Price par un float."""
    price = bot_pair.create_price(20000.0)
    result = price * 1.5
    assert isinstance(result, Price)
    assert result.price == 30000.0
    assert result.get_base() == "BTC"
    assert result.get_quote() == "USD"


def test_price_mul_by_token(bot_pair):
    """Test la multiplication d'un Price par un Token (quantité)."""
    price = bot_pair.create_price(20000.0)  # 20000 USD/BTC
    token = bot_pair.create_token(0.5)  # 0.5 BTC
    result = price * token
    assert isinstance(result, USD)
    assert result.amount == 10000.0  # 20000 * 0.5
    assert result.get_quote() == "USD"


def test_price_equality(bot_pair):
    """Test l'égalité entre deux instances de Price."""
    price1 = bot_pair.create_price(25000.0)
    price2 = bot_pair.create_price(25000.0)
    price3 = bot_pair.create_price(20000.0)
    assert price1 == price2
    assert price1 != price3


def test_price_less_than(bot_pair):
    """Test la comparaison 'inférieur à' entre deux instances de Price."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(25000.0)
    assert price1 < price2
    assert not (price2 < price1)


def test_price_less_than_or_equal(bot_pair):
    """Test la comparaison 'inférieur ou égal à' entre deux instances de Price."""
    price1 = bot_pair.create_price(20000.0)
    price2 = bot_pair.create_price(20000.0)
    price3 = bot_pair.create_price(25000.0)
    assert price1 <= price2
    assert price1 <= price3
    assert not (price3 <= price1)


def test_price_greater_than(bot_pair):
    """Test la comparaison 'supérieur à' entre deux instances de Price."""
    price1 = bot_pair.create_price(25000.0)
    price2 = bot_pair.create_price(20000.0)
    assert price1 > price2
    assert not (price2 > price1)


def test_price_greater_than_or_equal(bot_pair):
    """Test la comparaison 'supérieur ou égal à' entre deux instances de Price."""
    price1 = bot_pair.create_price(25000.0)
    price2 = bot_pair.create_price(25000.0)
    price3 = bot_pair.create_price(20000.0)
    assert price1 >= price2
    assert price1 >= price3
    assert not (price3 >= price1)


def test_price_to_dict(bot_pair):
    """Test la conversion de Price en dictionnaire."""
    price = bot_pair.create_price(25000.0)
    assert price.to_dict() == {"price": 25000.0}


def test_price_to_json(bot_pair):
    """Test la conversion de Price en JSON."""
    price = bot_pair.create_price(25000.0)
    assert json.loads(price.to_json()) == {"price": 25000.0}


def test_price_zero_constant(bot_pair):
    """Test que la constante zero est correctement initialisée."""
    assert bot_pair.zero_price().price == 0.0
    assert bot_pair.zero_price().get_base() == "BTC"
    assert bot_pair.zero_price().get_quote() == "USD"
    # S'assurer qu'il s'agit bien d'une instance de Price
    assert isinstance(bot_pair.zero_price(), Price)
