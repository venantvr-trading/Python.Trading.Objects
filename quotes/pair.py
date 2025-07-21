# Suppression des imports directs de quotes.coin, quotes.price, quotes.usd
# Ces classes seront importées localement dans les méthodes de fabrique si nécessaire,
# ou leur instanciation sera gérée par un mécanisme interne à BotPair.

class BotPair:
    def __init__(self, pair: str):
        self.pair = pair
        self.base_symbol, self.quote_symbol = pair.split("/")
        # configure_pair n'est plus nécessaire car l'état global est retiré.
        # Les symboles sont stockés comme attributs d'instance.

    def create_token(self, amount: float):
        """Crée une instance de Token pour la devise de base de cette paire."""
        from quotes.coin import Token  # Importation locale
        return Token(amount, self.base_symbol)

    def create_price(self, value: float):
        """Crée une instance de Price pour cette paire."""
        from quotes.price import Price  # Importation locale
        return Price(value, self.base_symbol, self.quote_symbol)

    def create_usd(self, amount: float):
        """Crée une instance de USD pour la devise de cotation de cette paire."""
        from quotes.usd import USD  # Importation locale
        return USD(amount, self.quote_symbol)

    # Si vous voulez des zéros spécifiques à la paire, vous les créeriez ici
    def zero_token(self):
        from quotes.coin import Token
        return Token(0.0, self.base_symbol)

    def zero_usd(self):
        from quotes.usd import USD
        return USD(0.0, self.quote_symbol)

    def zero_price(self):
        from quotes.price import Price
        return Price(0.0, self.base_symbol, self.quote_symbol)