from python_trading_objects.quotes import USD, BotPair, Price, Token


# Tests for the BotPair class
def test_bot_pair_initialization():
    """Test BotPair initialization and symbol extraction."""
    pair = BotPair("ETH/DAI")
    assert pair.pair == "ETH/DAI"
    assert pair.base_symbol == "ETH"
    assert pair.quote_symbol == "DAI"


def test_bot_pair_create_token():
    """Test creation of a Token via BotPair."""
    pair = BotPair("XRP/EUR")
    token = pair.create_token(100.0)
    assert isinstance(token, Token)
    assert token.amount == 100.0
    assert token.get_base() == "XRP"


def test_bot_pair_create_price():
    """Test creation of a Price via BotPair."""
    pair = BotPair("LTC/USDT")
    price = pair.create_price(80.50)
    assert isinstance(price, Price)
    assert price.price == 80.50
    assert price.get_base() == "LTC"
    assert price.get_quote() == "USDT"


def test_bot_pair_create_usd():
    """Test creation of a USD via BotPair."""
    pair = BotPair(
        "ADA/JPY"
    )  # Even though it's JPY, the USD class is used for the quote currency
    usd = pair.create_usd(500.75)
    assert isinstance(usd, USD)
    assert usd.amount == 500.75
    assert usd.get_quote() == "JPY"  # The quote symbol should be that of the pair


def test_bot_pair_zero_token():
    """Test creation of a zero Token via BotPair."""
    pair = BotPair("DOGE/USD")
    zero_token = pair.zero_token()
    assert isinstance(zero_token, Token)
    assert zero_token.amount == 0.0
    assert zero_token.get_base() == "DOGE"


def test_bot_pair_zero_usd():
    """Test creation of a zero USD via BotPair."""
    pair = BotPair("SHIB/EUR")
    zero_usd = pair.zero_usd()
    assert isinstance(zero_usd, USD)
    assert zero_usd.amount == 0.0
    assert zero_usd.get_quote() == "EUR"


def test_bot_pair_zero_price():
    """Test creation of a zero Price via BotPair."""
    pair = BotPair("SOL/CAD")
    zero_price = pair.zero_price()
    assert isinstance(zero_price, Price)
    assert zero_price.price == 0.0
    assert zero_price.get_base() == "SOL"
    assert zero_price.get_quote() == "CAD"
