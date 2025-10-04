import json
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer

from python_trading_objects.quotes.assertion import bot_assert


class Price(BaseModel):
    """
    Représente le prix d'une devise de base par rapport à une devise de cotation.

    Fournit des méthodes pour manipuler le prix et effectuer des opérations arithmétiques.
    """

    # Configuration Pydantic
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    price: float = Field(..., description="Le montant du prix")
    base_symbol: str = Field(..., description="Le symbole de la devise de base")
    quote_symbol: str = Field(..., description="Le symbole de la devise de cotation")

    def __init__(
        self,
        price: float,
        base_symbol: str,
        quote_symbol: str,
        _from_factory: bool = False,
    ):
        """
        Initialise une instance de Price.

        Paramètres:
        price (float): Le montant du prix.
        base_symbol (str): Le symbole de la devise de base (ex: BTC).
        quote_symbol (str): Le symbole de la devise de cotation (ex: USD).
        _from_factory (bool): Indique si l'instance est créée via une factory (interne).

        Exception:
        TypeError: Si l'instanciation n'est pas faite via BotPair.create_price().
        """
        if not _from_factory:
            raise TypeError("Use BotPair.create_price() to instantiate Price.")

        bot_assert(price, (float, int))

        super().__init__(
            price=float(price), base_symbol=base_symbol, quote_symbol=quote_symbol
        )

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        """Valide que le prix est un nombre."""
        if not isinstance(v, (float, int)):
            raise TypeError(f"Price must be float or int, got {type(v)}")
        return float(v)

    @field_validator("base_symbol", "quote_symbol")
    @classmethod
    def validate_symbols(cls, v):
        """Valide que les symboles sont des chaînes non vides."""
        if not isinstance(v, str) or not v:
            raise ValueError("Symbol must be a non-empty string")
        return v.upper()

    def get_base(self) -> str:
        """Retourne le symbole de la devise de base du prix."""
        return self.base_symbol

    def get_quote(self) -> str:
        """Retourne le symbole de la devise de cotation du prix."""
        return self.quote_symbol

    def __str__(self):
        """Retourne une représentation formatée du prix."""
        return f"{self.price:.2f} {self.base_symbol}/{self.quote_symbol}"

    def __add__(self, other):
        """
        Additionne deux instances de Price.

        Paramètres:
        other (Price): L'autre instance de Price à ajouter.

        Retourne:
        Price: Une nouvelle instance représentant la somme.

        Exception:
        TypeError: Si 'other' n'est pas une instance de Price.
        """
        bot_assert(other, Price)
        return Price(
            self.price + other.price,
            self.base_symbol,
            self.quote_symbol,
            _from_factory=True,
        )

    def __sub__(self, other):
        """
        Soustrait une instance de Price d'une autre.

        Paramètres:
        other (Price): L'instance à soustraire.

        Retourne:
        Price: Une nouvelle instance représentant la différence.

        Exception:
        TypeError: Si 'other' n'est pas de type Price.
        """
        bot_assert(other, Price)
        return Price(
            self.price - other.price,
            self.base_symbol,
            self.quote_symbol,
            _from_factory=True,
        )

    def __truediv__(self, other):
        """
        Divise un Price par un nombre ou un autre Price.

        Paramètres:
        other (float, int, Price): Le diviseur.

        Retourne:
        Price ou float: Si 'other' est un nombre, retourne un nouveau Price.
                        Si 'other' est un Price, retourne un float (le ratio).

        Exception:
        TypeError: Si 'other' n'est pas un float, int ou Price.
        ZeroDivisionError: Si la division par zéro est tentée.
        """
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return Price(
                self.price / other,
                self.base_symbol,
                self.quote_symbol,
                _from_factory=True,
            )
        if isinstance(other, Price):
            if other.price == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.price / other.price
        raise TypeError(f"L'opérande doit être un int, float ou Price")

    def __mul__(self, other):
        """
        Multiplie Price par un nombre ou une instance de Token.

        Paramètres:
        other (float, int, Token): Le multiplicateur.

        Retourne:
        Price ou Asset: Si 'other' est un nombre, retourne un nouveau Price.
                        Si 'other' est un Token, retourne un montant en Asset.

        Exception:
        TypeError: Si 'other' n'est pas un float, int ou Token.
        """
        from python_trading_objects.quotes.asset import USD, Asset
        from python_trading_objects.quotes.coin import Token

        bot_assert(other, (int, float, Token))

        if isinstance(other, (int, float)):
            return Price(
                self.price * other,
                self.base_symbol,
                self.quote_symbol,
                _from_factory=True,
            )
        if isinstance(other, Token):
            amount = self.price * other.amount
            # Return USD for backward compatibility when quote is USD
            if self.quote_symbol == "USD":
                return USD(amount, self.quote_symbol, _from_factory=True)
            return Asset(amount, self.quote_symbol, _from_factory=True)
        return NotImplemented

    def __eq__(self, other):
        """
        Vérifie si deux instances de Price sont égales.

        Paramètres:
        other (Price): L'autre instance de Price à comparer.

        Retourne:
        bool: True si les prix sont égaux, False sinon.
        """
        bot_assert(other, Price)
        return self.price == other.price

    def __ne__(self, other):
        """Vérifie si deux instances de Price ne sont pas égales."""
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        Vérifie si une instance de Price est inférieure à une autre.

        Paramètres:
        other (Price): L'autre instance de Price à comparer.

        Retourne:
        bool: True si le prix est inférieur, False sinon.
        """
        bot_assert(other, Price)
        return self.price < other.price

    def __le__(self, other):
        """Vérifie si une instance de Price est inférieure ou égale à une autre."""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        """
        Vérifie si une instance de Price est supérieure à une autre.

        Paramètres:
        other (Price): L'autre instance de Price à comparer.

        Retourne:
        bool: True si le prix est supérieur, False sinon.
        """
        bot_assert(other, Price)
        return self.price > other.price

    def __ge__(self, other):
        """Vérifie si une instance de Price est supérieure ou égale à une autre."""
        return self.__gt__(other) or self.__eq__(other)

    def __hash__(self):
        """Rend la classe hashable pour utilisation dans des sets/dicts."""
        return hash((self.price, self.base_symbol, self.quote_symbol))

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Sérialise le modèle avec les float en string pour préserver la précision."""
        return {
            "price": str(self.price),
            "base_symbol": self.base_symbol,
            "quote_symbol": self.quote_symbol,
        }

    def to_dict(self):
        """Convertit l'objet en dictionnaire avec les float en string pour préserver la précision."""
        return {"price": str(self.price)}

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())

    def is_positive(self) -> bool:
        """
        Vérifie si le prix est strictement positif.

        Retourne:
        bool: True si le prix est > 0, False sinon.
        """
        return self.price > 0

    def is_zero(self) -> bool:
        """
        Vérifie si le prix est égal à zéro.

        Retourne:
        bool: True si le prix est == 0, False sinon.
        """
        return self.price == 0

    def is_negative(self) -> bool:
        """
        Vérifie si le prix est strictement négatif.

        Retourne:
        bool: True si le prix est < 0, False sinon.
        """
        return self.price < 0
