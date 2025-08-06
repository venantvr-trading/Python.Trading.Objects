from business.quotes import Token
from business.quotes import BotPair
from business.quotes import Price
from business.quotes import USD


# Tests pour la classe BotPair
def test_bot_pair_initialization():
    """Test l'initialisation de BotPair et l'extraction des symboles."""
    pair = BotPair("ETH/DAI")
    assert pair.pair == "ETH/DAI"
    assert pair.base_symbol == "ETH"
    assert pair.quote_symbol == "DAI"


def test_bot_pair_create_token():
    """Test la création d'un Token via BotPair."""
    pair = BotPair("XRP/EUR")
    token = pair.create_token(100.0)
    assert isinstance(token, Token)
    assert token.amount == 100.0
    assert token.get_base() == "XRP"


def test_bot_pair_create_price():
    """Test la création d'un Price via BotPair."""
    pair = BotPair("LTC/USDT")
    price = pair.create_price(80.50)
    assert isinstance(price, Price)
    assert price.price == 80.50
    assert price.get_base() == "LTC"
    assert price.get_quote() == "USDT"


def test_bot_pair_create_usd():
    """Test la création d'un USD via BotPair."""
    pair = BotPair("ADA/JPY")  # Même si c'est JPY, la classe USD est utilisée pour la devise de cotation
    usd = pair.create_usd(500.75)
    assert isinstance(usd, USD)
    assert usd.amount == 500.75
    assert usd.get_quote() == "JPY"  # Le symbole de cotation doit être celui de la paire


def test_bot_pair_zero_token():
    """Test la création d'un Token de zéro via BotPair."""
    pair = BotPair("DOGE/USD")
    zero_token = pair.zero_token()
    assert isinstance(zero_token, Token)
    assert zero_token.amount == 0.0
    assert zero_token.get_base() == "DOGE"


def test_bot_pair_zero_usd():
    """Test la création d'un USD de zéro via BotPair."""
    pair = BotPair("SHIB/EUR")
    zero_usd = pair.zero_usd()
    assert isinstance(zero_usd, USD)
    assert zero_usd.amount == 0.0
    assert zero_usd.get_quote() == "EUR"


def test_bot_pair_zero_price():
    """Test la création d'un Price de zéro via BotPair."""
    pair = BotPair("SOL/CAD")
    zero_price = pair.zero_price()
    assert isinstance(zero_price, Price)
    assert zero_price.price == 0.0
    assert zero_price.get_base() == "SOL"
    assert zero_price.get_quote() == "CAD"
