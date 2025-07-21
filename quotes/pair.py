class BotPair:
    """
    Classe factory pour créer des instances de Token, Price et USD
    spécifiques à une paire de devises.
    """

    def __init__(self, pair: str):
        """
        Initialise une instance de BotPair avec une paire de devises.

        Paramètres:
        pair (str): La paire de devises sous forme "BASE/QUOTE" (ex: "BTC/USD").
        """
        self.pair = pair
        self.base_symbol, self.quote_symbol = pair.split("/")

    def create_token(self, amount: float):
        """Crée une instance de Token pour la devise de base de cette paire."""
        from quotes.coin import Token
        return Token(amount, self.base_symbol, _from_factory=True)

    def create_price(self, value: float):
        """Crée une instance de Price pour cette paire."""
        from quotes.price import Price
        return Price(value, self.base_symbol, self.quote_symbol, _from_factory=True)

    def create_usd(self, amount: float):
        """Crée une instance de USD pour la devise de cotation de cette paire."""
        from quotes.usd import USD
        return USD(amount, self.quote_symbol, _from_factory=True)

    def zero_token(self):
        """Crée une instance de Token avec une valeur de zéro."""
        from quotes.coin import Token
        return Token(0.0, self.base_symbol, _from_factory=True)

    def zero_usd(self):
        """Crée une instance de USD avec une valeur de zéro."""
        from quotes.usd import USD
        return USD(0.0, self.quote_symbol, _from_factory=True)

    def zero_price(self):
        """Crée une instance de Price avec une valeur de zéro."""
        from quotes.price import Price
        return Price(0.0, self.base_symbol, self.quote_symbol, _from_factory=True)