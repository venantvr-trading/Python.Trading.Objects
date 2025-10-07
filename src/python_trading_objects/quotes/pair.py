from decimal import Decimal
from typing import Union


class BotPair:
    """
    Factory class for creating Token, Price and Asset instances
    specific to a currency pair.
    """

    def __init__(self, pair: str):
        """
        Initializes a BotPair instance with a currency pair.

        Parameters:
        pair (str): The currency pair in "BASE/QUOTE" format (e.g., "BTC/USDC", "ETH/EUR").
        """
        self.pair = pair
        self.base_symbol, self.quote_symbol = pair.split("/")
        self.friendly_name = self.base_symbol + self.quote_symbol

    # Generic methods for any asset type
    def create_base_asset(self, amount: Union[Decimal, float, str, int]):
        """Creates an Asset instance for the base currency."""
        from python_trading_objects.quotes.asset import Asset

        return Asset(amount, self.base_symbol, _from_factory=True)

    def create_quote_asset(self, amount: Union[Decimal, float, str, int]):
        """Creates an Asset instance for the quote currency."""
        from python_trading_objects.quotes.asset import Asset

        return Asset(amount, self.quote_symbol, _from_factory=True)

    def zero_base(self):
        """Creates a base Asset instance with zero value."""
        return self.create_base_asset(Decimal("0"))

    def zero_quote(self):
        """Creates a quote Asset instance with zero value."""
        return self.create_quote_asset(Decimal("0"))

    # Legacy methods for backward compatibility
    def create_token(self, amount: Union[Decimal, float, str, int]):
        """Legacy: Creates a Token instance for the base currency of this pair."""
        from python_trading_objects.quotes.coin import Token

        return Token(amount, self.base_symbol, _from_factory=True)

    def create_price(self, value: Union[Decimal, float, str, int]):
        """Creates a Price instance for this pair."""
        from python_trading_objects.quotes.price import Price

        return Price(value, self.base_symbol, self.quote_symbol, _from_factory=True)

    def create_usd(self, amount: Union[Decimal, float, str, int]):
        """Legacy: Creates an instance for the quote currency (not necessarily USD!)."""
        from python_trading_objects.quotes.asset import USD

        return USD(amount, self.quote_symbol, _from_factory=True)

    def zero_token(self):
        """Legacy: Creates a Token instance with zero value."""
        from python_trading_objects.quotes.coin import Token

        return Token(Decimal("0"), self.base_symbol, _from_factory=True)

    def zero_usd(self):
        """Legacy: Creates a quote asset with zero value."""
        from python_trading_objects.quotes.asset import USD

        return USD(Decimal("0"), self.quote_symbol, _from_factory=True)

    def zero_price(self):
        """Creates a Price instance with zero value."""
        from python_trading_objects.quotes.price import Price

        return Price(Decimal("0"), self.base_symbol, self.quote_symbol, _from_factory=True)
