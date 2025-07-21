import json

from quotes.quote import Quote, bot_assert


class USD(Quote):
    """
    Représente un montant en dollars américains ($QUOTE).

    Fournit des méthodes pour manipuler et comparer des montants.
    """

    def __init__(self, amount: float, quote_symbol: str, _from_factory: bool = False):
        """
        Initialise une instance de USD.

        Paramètres:
        amount (float): Le montant en USD.
        quote_symbol (str): Le symbole de la devise de cotation (ex: USD).
        _from_factory (bool): Indique si l'instance est créée via une factory (interne).

        Exception:
        TypeError: Si l'instanciation n'est pas faite via BotPair.create_usd().
        """
        if not _from_factory:
            raise TypeError("Use BotPair.create_usd() to instantiate USD.")

        super().__init__(amount, _from_factory=_from_factory)
        bot_assert(amount, (float, int))

        self.__quote = quote_symbol

    def get_quote(self) -> str:
        """Retourne le symbole de la devise de cotation (USD)."""
        return self.__quote

    def __str__(self):
        """Retourne une représentation formatée du montant en USD."""
        return f"{self.amount:.2f} {self.__quote}"

    def __lt__(self, other):
        """
        Compare si l'instance actuelle est inférieure à une autre instance de USD ou un nombre.

        Paramètres:
        other (USD ou float): L'autre montant à comparer.

        Retourne:
        bool: True si l'instance est inférieure, False sinon.

        Exception:
        TypeError: Si 'other' n'est pas un USD ou un nombre.
        """
        if isinstance(other, USD):
            return self.amount < other.amount
        elif isinstance(other, float):
            return self.amount < other
        raise TypeError(f"L'opérande doit être une instance de {self.__quote} ou un nombre (float)")

    def __add__(self, other):
        """
        Additionne deux instances de USD.

        Paramètres:
        other (USD): L'autre instance de USD à ajouter.

        Retourne:
        USD: Une nouvelle instance représentant la somme.

        Exception:
        TypeError: Si 'other' n'est pas une instance de USD.
        """
        bot_assert(other, USD)
        return USD(self.amount + other.amount, self.__quote, _from_factory=True)

    def __radd__(self, other):
        """
        Gère l'addition lorsque USD est à droite de l'opérateur (+).

        Paramètres:
        other (int, float): L'autre opérande.

        Retourne:
        USD: Une nouvelle instance représentant la somme.
        """
        if isinstance(other, (int, float)):
            return USD(self.amount + other, self.__quote, _from_factory=True)
        return NotImplemented

    def __sub__(self, other):
        """
        Soustrait une instance de USD d'une autre.

        Paramètres:
        other (USD): L'instance à soustraire.

        Retourne:
        USD: Une nouvelle instance représentant la différence.

        Exception:
        TypeError: Si 'other' n'est pas une instance de USD.
        """
        bot_assert(other, USD)
        return USD(self.amount - other.amount, self.__quote, _from_factory=True)

    def __neg__(self):
        """
        Retourne le montant négatif de l'instance courante de USD.

        Retourne:
        USD: Une nouvelle instance représentant le montant négatif.
        """
        return USD(-self.amount, self.__quote, _from_factory=True)

    def __mul__(self, other):
        """
        Multiplie l'instance de USD par un nombre.

        Paramètres:
        other (float): Le nombre à multiplier.

        Retourne:
        USD: Une nouvelle instance représentant le résultat.

        Exception:
        TypeError: Si 'other' n'est pas un float.
        """
        bot_assert(other, float)
        return USD(self.amount * other, self.__quote, _from_factory=True)

    def __truediv__(self, other):
        """
        Divise l'instance de USD par un nombre, une autre instance de USD, ou un Price.

        Paramètres:
        other (int, float, USD ou Price): Le diviseur.

        Retourne:
        USD ou float ou Token: Si 'other' est un nombre, retourne un nouveau USD.
                               Si 'other' est un USD, retourne un float (le ratio).
                               Si 'other' est un Price, retourne un Token.

        Exception:
        TypeError: Si 'other' n'est pas un type valide.
        ZeroDivisionError: Si une division par zéro est tentée.
        """
        from quotes.price import Price
        from quotes.coin import Token

        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return USD(self.amount / other, self.__quote, _from_factory=True)
        if isinstance(other, USD):
            if other.amount == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.amount / other.amount
        if isinstance(other, Price):
            if other.price == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            # Division USD / Price (ex: 100 USD / 20000 USD/BTC) donne une quantité de BTC
            return Token(self.amount / other.price, other.get_base(), _from_factory=True)
        raise TypeError(f"L'opérande doit être un int, float, {self.__quote} ou Price")

    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return dict(price=self.amount)

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())