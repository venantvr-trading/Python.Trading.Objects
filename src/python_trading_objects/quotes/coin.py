import json

from python_trading_objects.quotes.assertion import bot_assert
from python_trading_objects.quotes.quote import Quote


class Token(Quote):
    """
    Représente un montant d'une devise de base ($TOKEN).

    Fournit des méthodes pour manipuler et comparer des montants,
    assurant la cohérence dans les opérations.
    """

    def __init__(self, amount: float, base_symbol: str, _from_factory: bool = False):
        """
        Initialise une instance de Token.

        Paramètres:
        amount (float): Le montant du token.
        base_symbol (str): Le symbole de la devise de base (ex: BTC).
        _from_factory (bool): Indique si l'instance est créée via une factory (interne).

        Exception:
        TypeError: Si l'instanciation n'est pas faite via BotPair.create_token().
        """
        if not _from_factory:
            raise TypeError("Use BotPair.create_token() to instantiate Token.")

        super().__init__(amount, _from_factory=_from_factory)
        bot_assert(amount, float)

        self._Token__base = base_symbol

    def get_base(self) -> str:
        """Retourne le symbole de la devise de base du token."""
        return self._Token__base

    def __str__(self):
        """Retourne une représentation formatée du montant du token."""
        return f"{self.amount:.8f} {self._Token__base}"  # Formatage à 8 décimales

    def __lt__(self, other):
        """
        Compare si l'instance actuelle est inférieure à une autre instance de Token ou un nombre.

        Paramètres:
        other (Token ou float): L'autre montant à comparer.

        Retourne:
        bool: True si l'instance est inférieure, False sinon.

        Exception:
        TypeError: Si 'other' n'est pas un Token ou un nombre.
        """
        if isinstance(other, Token):
            return self.amount < other.amount
        elif isinstance(other, float):
            return self.amount < other
        raise TypeError(
            f"L'opérande doit être une instance de {self._Token__base} ou un nombre (float)"
        )

    def __add__(self, other):
        """
        Additionne deux instances de Token.

        Paramètres:
        other (Token): L'autre instance de Token à ajouter.

        Retourne:
        Token: Une nouvelle instance représentant la somme.

        Exception:
        TypeError: Si 'other' n'est pas une instance de Token.
        """
        bot_assert(other, Token)
        return Token(self.amount + other.amount, self._Token__base, _from_factory=True)

    def __radd__(self, other):
        """
        Gère l'addition lorsque Token est à droite de l'opérateur (+).

        Paramètres:
        other (int, float): L'autre opérande.

        Retourne:
        Token: Une nouvelle instance représentant la somme.
        """
        if isinstance(other, (int, float)):
            return Token(self.amount + other, self._Token__base, _from_factory=True)
        return NotImplemented

    def __sub__(self, other):
        """
        Soustrait une instance de Token d'une autre.

        Paramètres:
        other (Token): L'instance à soustraire.

        Retourne:
        Token: Une nouvelle instance représentant la différence.

        Exception:
        TypeError: Si 'other' n'est pas une instance de Token.
        """
        bot_assert(other, Token)
        return Token(self.amount - other.amount, self._Token__base, _from_factory=True)

    def __neg__(self):
        """
        Retourne le montant négatif de l'instance courante de Token.

        Retourne:
        Token: Une nouvelle instance représentant le montant négatif.
        """
        return Token(-self.amount, self._Token__base, _from_factory=True)

    def __mul__(self, other):
        """
        Multiplie l'instance de Token par un nombre ou une instance de Price.

        Paramètres:
        other (float ou Price): L'opérande à multiplier.

        Retourne:
        Token ou Asset: Si 'other' est un float, retourne un Token.
                        Si 'other' est un Price, retourne un montant en Asset.

        Exception:
        TypeError: Si 'other' n'est ni un float ni une instance de Price.
        """
        from python_trading_objects.quotes.asset import USD, Asset
        from python_trading_objects.quotes.price import Price

        bot_assert(other, (float, Price))

        if isinstance(other, float):
            return Token(self.amount * other, self._Token__base, _from_factory=True)
        if isinstance(other, Price):
            # Return USD for backward compatibility when quote is USD
            if other.get_quote() == "USD":
                return USD(
                    self.amount * other.price, other.get_quote(), _from_factory=True
                )
            return Asset(
                self.amount * other.price, other.get_quote(), _from_factory=True
            )
        return NotImplemented

    def __truediv__(self, other):
        """
        Divise l'instance de Token par un nombre ou une autre instance de Token.

        Paramètres:
        other (int, float ou Token): Le diviseur.

        Retourne:
        Token ou float: Si 'other' est un nombre, retourne un nouveau Token.
                        Si 'other' est un Token, retourne un float (le ratio).

        Exception:
        TypeError: Si 'other' n'est pas un int, float ou Token.
        ZeroDivisionError: Si une division par zéro est tentée.
        """
        if isinstance(other, float):
            if other == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return Token(self.amount / other, self._Token__base, _from_factory=True)
        if isinstance(other, Token):
            if other.amount == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.amount / other.amount
        raise TypeError(f"L'opérande doit être un int, float ou {self._Token__base}")

    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return dict(price=self.amount)

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())
