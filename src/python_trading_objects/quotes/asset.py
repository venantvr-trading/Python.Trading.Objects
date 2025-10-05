import json
from decimal import Decimal
from typing import Any, Dict, Union

from pydantic import Field, field_validator, model_serializer

from python_trading_objects.quotes.assertion import bot_assert
from python_trading_objects.quotes.quote import Quote


class Asset(Quote):
    """
    Represents an amount of any asset (USD, USDC, EUR, etc.).
    Generic class that replaces the old USD-specific class.
    """

    symbol: str = Field(..., description="Le symbole de l'actif")

    def __init__(self, amount: Union[Decimal, float, int, str], symbol: str, _from_factory: bool = False):
        """
        Initializes an Asset instance.

        Parameters:
        amount (Decimal|float|int|str): The asset amount.
        symbol (str): The asset symbol (USD, USDC, EUR, etc.).
        _from_factory (bool): Indicates if instance is created via factory.

        Raises:
        TypeError: If not instantiated via BotPair factory methods.
        """
        if not _from_factory:
            raise TypeError(
                f"Use BotPair.create_asset() or create_{symbol.lower()}() to instantiate Asset."
            )

        bot_assert(amount, (Decimal, float, int, str))

        # Determine precision based on asset type
        is_stablecoin = symbol in [
            "USD",
            "USDC",
            "USDT",
            "DAI",
            "BUSD",
            "TUSD",
            "USDP",
        ]
        is_fiat = symbol in ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
        precision_value = 2 if (is_fiat or is_stablecoin) else 8

        # Tronque le montant avec la précision correcte
        truncated_amount = Quote._truncate_to_precision_static(amount, precision_value)

        # Call parent constructor
        super().__init__(
            amount=truncated_amount,
            _from_factory=_from_factory,
            symbol=symbol,
            precision=precision_value,
        )

        # Store private attributes AFTER calling super().__init__
        object.__setattr__(self, "_Asset__is_stablecoin", is_stablecoin)
        object.__setattr__(self, "_Asset__is_fiat", is_fiat)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v):
        """Valide que le symbole est une chaîne non vide."""
        if not isinstance(v, str) or not v:
            raise ValueError("Symbol must be a non-empty string")
        return v.upper()

    def get_symbol(self) -> str:
        """Returns the asset symbol."""
        return self.symbol

    def get_quote(self) -> str:
        """Returns the asset symbol (alias for backward compatibility)."""
        return self.symbol

    def is_stablecoin(self) -> bool:
        """Checks if the asset is a stablecoin."""
        return self.__is_stablecoin

    def is_fiat(self) -> bool:
        """Checks if the asset is a fiat currency."""
        return self.__is_fiat

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Sérialise le modèle avec les float en string pour préserver la précision."""
        return {
            "amount": str(self.amount),
            "precision": self.precision,
            "symbol": self.symbol,
        }

    def __str__(self):
        """Returns a formatted string representation of the amount."""
        decimals = 2 if self.__is_fiat or self.__is_stablecoin else 8
        return f"{self.amount:.{decimals}f} {self.symbol}"

    def __lt__(self, other):
        """
        Compares if current instance is less than another Asset or number.

        Parameters:
        other (Asset or float): The amount to compare.

        Returns:
        bool: True if instance is less, False otherwise.

        Raises:
        TypeError: If 'other' is not an Asset or number.
        """
        if isinstance(other, Asset):
            if other.get_symbol() != self.symbol:
                raise TypeError(f"Cannot compare {self.symbol} with {other.symbol}")
            return self.amount < other.amount
        elif isinstance(other, float):
            return self.amount < other
        raise TypeError(
            f"Operand must be an instance of {self.symbol} or a number (float)"
        )

    def __add__(self, other):
        """
        Adds two Asset instances.

        Parameters:
        other (Asset): The other Asset instance to add.

        Returns:
        Asset: A new instance representing the sum.

        Raises:
        TypeError: If 'other' is not an Asset instance or has different symbol.
        """
        if isinstance(other, Asset):
            if other.get_symbol() != self.symbol:
                raise TypeError(f"Cannot add {self.symbol} with {other.get_symbol()}")
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(self.amount + other.amount, self.symbol, _from_factory=True)
            return Asset(self.amount + other.amount, self.symbol, _from_factory=True)
        raise TypeError(f"Operand must be an instance of {self.symbol}")

    def __radd__(self, other):
        """
        Handles addition when Asset is on the right side of the operator.

        Parameters:
        other (Decimal, int, float): The other operand.

        Returns:
        Asset: A new instance representing the sum.
        """
        if isinstance(other, (Decimal, int, float)):
            other_decimal = other if isinstance(other, Decimal) else Decimal(str(other))
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(self.amount + other_decimal, self.symbol, _from_factory=True)
            return Asset(self.amount + other_decimal, self.symbol, _from_factory=True)
        return NotImplemented

    def __sub__(self, other):
        """
        Subtracts one Asset instance from another.

        Parameters:
        other (Asset): The instance to subtract.

        Returns:
        Asset: A new instance representing the difference.

        Raises:
        TypeError: If 'other' is not an Asset instance or has different symbol.
        """
        if isinstance(other, Asset):
            if other.get_symbol() != self.symbol:
                raise TypeError(
                    f"Cannot subtract {other.get_symbol()} from {self.symbol}"
                )
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(self.amount - other.amount, self.symbol, _from_factory=True)
            return Asset(self.amount - other.amount, self.symbol, _from_factory=True)
        raise TypeError(f"Operand must be an instance of {self.symbol}")

    def __neg__(self):
        """
        Returns the negative amount of the current Asset instance.

        Returns:
        Asset: A new instance representing the negative amount.
        """
        # Return USD instance if self is USD
        if isinstance(self, USD):
            return USD(-self.amount, self.symbol, _from_factory=True)
        return Asset(-self.amount, self.symbol, _from_factory=True)

    def __mul__(self, other):
        """
        Multiplies the Asset instance by a number.

        Parameters:
        other (Decimal, float, int): The number to multiply by.

        Returns:
        Asset: A new instance representing the result.

        Raises:
        TypeError: If 'other' is not a number.
        """
        bot_assert(other, (Decimal, float, int))
        other_decimal = other if isinstance(other, Decimal) else Decimal(str(other))
        # Return USD instance if self is USD
        if isinstance(self, USD):
            return USD(self.amount * other_decimal, self.symbol, _from_factory=True)
        return Asset(self.amount * other_decimal, self.symbol, _from_factory=True)

    def __truediv__(self, other):
        """
        Divides the Asset instance by a number, another Asset, or a Price.

        Parameters:
        other (Decimal, int, float, Asset, or Price): The divisor.

        Returns:
        Asset, Decimal, or Token: Depending on the type of 'other'.

        Raises:
        TypeError: If 'other' is not a valid type.
        ZeroDivisionError: If division by zero is attempted.
        """
        from python_trading_objects.quotes.coin import Token
        from python_trading_objects.quotes.price import Price

        if isinstance(other, (Decimal, int, float)):
            other_decimal = other if isinstance(other, Decimal) else Decimal(str(other))
            if other_decimal == 0:
                raise ZeroDivisionError("Division by zero not allowed")
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(self.amount / other_decimal, self.symbol, _from_factory=True)
            return Asset(self.amount / other_decimal, self.symbol, _from_factory=True)

        if isinstance(other, Asset):
            if other.amount == 0:
                raise ZeroDivisionError("Division by zero not allowed")
            if other.get_symbol() != self.symbol:
                # Division between different assets gives an exchange rate
                return self.amount / other.amount
            return self.amount / other.amount

        if isinstance(other, Price):
            # Convert price to Decimal if it's a float
            price_decimal = other.price if isinstance(other.price, Decimal) else Decimal(str(other.price))
            if price_decimal == 0:
                raise ZeroDivisionError("Division by zero not allowed")
            # Division Asset / Price gives tokens
            return Token(
                self.amount / price_decimal, other.get_base(), _from_factory=True
            )

        raise TypeError(f"Operand must be a number, {self.symbol} or Price")

    def to_dict(self):
        """Converts the object to a dictionary with float as string for precision."""
        return {"price": str(self.amount), "symbol": self.symbol}

    def to_json(self):
        """Converts the object to JSON."""
        return json.dumps(self.to_dict())


# For backward compatibility, create USD alias
class USD(Asset):
    """Alias for compatibility with legacy code."""

    def __init__(
            self, amount: Union[Decimal, float, int, str], quote_symbol: str = "USD", _from_factory: bool = False
    ):
        """
        Initializes a USD instance (legacy compatibility).

        Parameters:
        amount (Decimal|float|int|str): The USD amount.
        quote_symbol (str): The quote symbol (default: USD).
        _from_factory (bool): Indicates if instance is created via factory.
        """
        if not _from_factory:
            raise TypeError("Use BotPair.create_usd() to instantiate USD.")
        super().__init__(amount, quote_symbol, _from_factory=_from_factory)

    def get_quote(self) -> str:
        """Legacy method for compatibility."""
        return self.get_symbol()

    def to_dict(self):
        """Converts the object to a dictionary (legacy format) with float as string for precision."""
        return {"price": str(self.amount)}

    def to_json(self):
        """Converts the object to JSON (legacy format)."""
        return json.dumps(self.to_dict())
