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
    def create_base_asset(self, amount: float):
        """Creates an Asset instance for the base currency."""
        from venantvr.quotes.asset import Asset

        return Asset(amount, self.base_symbol, _from_factory=True)

    def create_quote_asset(self, amount: float):
        """Creates an Asset instance for the quote currency."""
        from venantvr.quotes.asset import Asset

        return Asset(amount, self.quote_symbol, _from_factory=True)

    def zero_base(self):
        """Creates a base Asset instance with zero value."""
        return self.create_base_asset(0.0)

    def zero_quote(self):
        """Creates a quote Asset instance with zero value."""
        return self.create_quote_asset(0.0)

    # Legacy methods for backward compatibility
    def create_token(self, amount: float):
        """Legacy: Creates a Token instance for the base currency of this pair."""
        from venantvr.quotes.coin import Token

        return Token(amount, self.base_symbol, _from_factory=True)

    def create_price(self, value: float):
        """Creates a Price instance for this pair."""
        from venantvr.quotes.price import Price

        return Price(value, self.base_symbol, self.quote_symbol, _from_factory=True)

    def create_usd(self, amount: float):
        """Legacy: Creates an instance for the quote currency (not necessarily USD!)."""
        from venantvr.quotes.asset import USD

        return USD(amount, self.quote_symbol, _from_factory=True)

    def zero_token(self):
        """Legacy: Creates a Token instance with zero value."""
        from venantvr.quotes.coin import Token

        return Token(0.0, self.base_symbol, _from_factory=True)

    def zero_usd(self):
        """Legacy: Creates a quote asset with zero value."""
        from venantvr.quotes.asset import USD

        return USD(0.0, self.quote_symbol, _from_factory=True)

    def zero_price(self):
        """Creates a Price instance with zero value."""
        from venantvr.quotes.price import Price

        return Price(0.0, self.base_symbol, self.quote_symbol, _from_factory=True)
