from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Dict, Union, TYPE_CHECKING

from pydantic import Field, model_serializer

from python_trading_objects.quotes.assertion import bot_assert
from python_trading_objects.quotes.quote import Quote

if TYPE_CHECKING:
    from python_trading_objects.quotes.price import Price
    from python_trading_objects.quotes.asset import Asset


class Token(Quote):
    """
    Représente un montant d'une devise de base ($TOKEN).

    Fournit des méthodes pour manipuler et comparer des montants,
    assurant la cohérence dans les opérations.
    """

    base_symbol: str = Field(..., description="Le symbole de la devise de base")

    def __init__(self, amount: Union[Decimal, float, int, str], base_symbol: str, _from_factory: bool = False):
        """
        Initialise une instance de Token.

        Paramètres:
        amount (Decimal|float|int|str): Le montant du token.
        base_symbol (str): Le symbole de la devise de base (ex: BTC).
        _from_factory (bool): Indique si l'instance est créée via une factory (interne).

        Exception:
        TypeError: Si l'instanciation n'est pas faite via BotPair.create_token().
        """
        if not _from_factory:
            raise TypeError("Use BotPair.create_token() to instantiate Token.")

        bot_assert(amount, (Decimal, float, int, str))

        # Appelle le constructeur parent avec base_symbol
        super().__init__(amount, _from_factory=_from_factory, base_symbol=base_symbol)

    def get_base(self) -> str:
        """Retourne le symbole de la devise de base du token."""
        return self.base_symbol

    def get_child_class(self):
        """Retourne le type de la classe fille de l'instance courante."""
        return self.__class__

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Sérialise le modèle avec les float en string pour préserver la précision."""
        return {
            "amount": str(self.amount),
            "precision": self.precision,
            "base_symbol": self.base_symbol,
        }

    def __str__(self):
        """Retourne une représentation formatée du montant du token."""
        return f"{self.amount:.8f} {self.base_symbol}"  # Formatage à 8 décimales

    def __lt__(self, other):
        """
        Compare si l'instance actuelle est inférieure à une autre instance de Token ou un nombre.

        Paramètres:
        other (Token ou Decimal|float|int): L'autre montant à comparer.

        Retourne:
        bool: True si l'instance est inférieure, False sinon.

        Exception:
        TypeError: Si 'other' n'est pas un Token ou un nombre.
        """
        if isinstance(other, Token):
            return self.amount < other.amount
        elif isinstance(other, (Decimal, float, int)):
            return self.amount < Decimal(str(other))
        raise TypeError(
            f"L'opérande doit être une instance de {self.base_symbol} ou un nombre"
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
        return Token(self.amount + other.amount, self.base_symbol, _from_factory=True)

    def __radd__(self, other):
        """
        Gère l'addition lorsque Token est à droite de l'opérateur (+).

        Paramètres:
        other (Decimal|int|float): L'autre opérande.

        Retourne:
        Token: Une nouvelle instance représentant la somme.
        """
        if isinstance(other, (Decimal, int, float)):
            other_decimal = other if isinstance(other, Decimal) else Decimal(str(other))
            return Token(self.amount + other_decimal, self.base_symbol, _from_factory=True)
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
        return Token(self.amount - other.amount, self.base_symbol, _from_factory=True)

    def __neg__(self):
        """
        Retourne le montant négatif de l'instance courante de Token.

        Retourne:
        Token: Une nouvelle instance représentant le montant négatif.
        """
        return Token(-self.amount, self.base_symbol, _from_factory=True)

    def __mul__(self, other: Decimal | float | int | Price) -> Token | Asset:
        """
        Multiplie l'instance de Token par un nombre ou une instance de Price.

        Paramètres:
        other (Decimal|float|int ou Price): L'opérande à multiplier.

        Retourne:
        Token ou Asset: Si 'other' est un nombre, retourne un Token.
                        Si 'other' est un Price, retourne un montant en Asset.

        Exception:
        TypeError: Si 'other' n'est ni un nombre ni une instance de Price.
        """
        from python_trading_objects.quotes.asset import USD, Asset
        from python_trading_objects.quotes.price import Price

        bot_assert(other, (Decimal, float, int, Price))

        if isinstance(other, (Decimal, float, int)):
            if not isinstance(other, Decimal):
                other = Decimal(str(other))
            return Token(self.amount * other, self.base_symbol, _from_factory=True)
        if isinstance(other, Price):
            # Convert price to Decimal if it's a float
            price_decimal = other.price if isinstance(other.price, Decimal) else Decimal(str(other.price))
            # Return USD for backward compatibility when quote is USD
            if other.get_quote() == "USD":
                return USD(
                    self.amount * price_decimal, other.get_quote(), _from_factory=True
                )
            return Asset(
                self.amount * price_decimal, other.get_quote(), _from_factory=True
            )
        return NotImplemented

    def __truediv__(self, other):
        """
        Divise l'instance de Token par un nombre ou une autre instance de Token.

        Paramètres:
        other (Decimal|int|float ou Token): Le diviseur.

        Retourne:
        Token ou Decimal: Si 'other' est un nombre, retourne un nouveau Token.
                          Si 'other' est un Token, retourne un Decimal (le ratio).

        Exception:
        TypeError: Si 'other' n'est pas un nombre ou Token.
        ZeroDivisionError: Si une division par zéro est tentée.
        """
        if isinstance(other, (Decimal, float, int)):
            other_decimal = other if isinstance(other, Decimal) else Decimal(str(other))
            if other_decimal == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return Token(self.amount / other_decimal, self.base_symbol, _from_factory=True)
        if isinstance(other, Token):
            if other.amount == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.amount / other.amount
        raise TypeError(f"L'opérande doit être un nombre ou {self.base_symbol}")

    def to_dict(self):
        """Convertit l'objet en dictionnaire avec les float en string pour préserver la précision."""
        return {"price": str(self.amount)}

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())

    def value_at(self, price: Price) -> Asset:
        """
        Calculate value of tokens at given price.

        Args:
            price: Price per token

        Returns:
            Asset representing total value
        """
        from python_trading_objects.quotes.price import Price

        if not isinstance(price, Price):
            raise TypeError("price must be an instance of Price")

        # Use existing multiplication logic
        return self * price

    def split(self, ratio: float) -> tuple[Token, Token]:
        """
        Split tokens into two parts by ratio.

        Args:
            ratio: Ratio for first part (0.3 = 30%)

        Returns:
            Tuple of (first_part, second_part)
        """
        if not 0 <= ratio <= 1:
            raise ValueError("ratio must be between 0 and 1")

        first_amount = self.amount * Decimal(str(ratio))
        second_amount = self.amount * Decimal(str(1 - ratio))
        return (
            Token(first_amount, self.base_symbol, _from_factory=True),
            Token(second_amount, self.base_symbol, _from_factory=True)
        )
