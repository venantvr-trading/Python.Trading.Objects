import json

from python_trading_objects.quotes.assertion import bot_assert
from python_trading_objects.quotes.quote import Quote


class Asset(Quote):
    """
    Represents an amount of any asset (USD, USDC, EUR, etc.).
    Generic class that replaces the old USD-specific class.
    """

    def __init__(self, amount: float, symbol: str, _from_factory: bool = False):
        """
        Initializes an Asset instance.

        Parameters:
        amount (float): The asset amount.
        symbol (str): The asset symbol (USD, USDC, EUR, etc.).
        _from_factory (bool): Indicates if instance is created via factory.

        Raises:
        TypeError: If not instantiated via BotPair factory methods.
        """
        if not _from_factory:
            raise TypeError(
                f"Use BotPair.create_asset() or create_{symbol.lower()}() to instantiate Asset."
            )

        bot_assert(amount, (float, int))

        # Must set symbol before calling super().__init__
        self.__symbol = symbol
        self.__is_stablecoin = symbol in [
            "USD",
            "USDC",
            "USDT",
            "DAI",
            "BUSD",
            "TUSD",
            "USDP",
        ]
        self.__is_fiat = symbol in ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]

        super().__init__(amount, _from_factory=_from_factory)

        # Override precision after super().__init__ based on asset type
        if self.__is_fiat or self.__is_stablecoin:
            self.precision = 2
        else:
            self.precision = 8

        # Re-truncate with correct precision
        self.amount = self.truncate_to_precision(amount)

    def get_symbol(self) -> str:
        """Returns the asset symbol."""
        return self.__symbol

    def get_quote(self) -> str:
        """Returns the asset symbol (alias for backward compatibility)."""
        return self.__symbol

    def is_stablecoin(self) -> bool:
        """Checks if the asset is a stablecoin."""
        return self.__is_stablecoin

    def is_fiat(self) -> bool:
        """Checks if the asset is a fiat currency."""
        return self.__is_fiat

    def __str__(self):
        """Returns a formatted string representation of the amount."""
        decimals = 2 if self.__is_fiat or self.__is_stablecoin else 8
        return f"{self.amount:.{decimals}f} {self.__symbol}"

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
            if other.get_symbol() != self.__symbol:
                raise TypeError(f"Cannot compare {self.__symbol} with {other.__symbol}")
            return self.amount < other.amount
        elif isinstance(other, float):
            return self.amount < other
        raise TypeError(
            f"Operand must be an instance of {self.__symbol} or a number (float)"
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
            if other.get_symbol() != self.__symbol:
                raise TypeError(f"Cannot add {self.__symbol} with {other.get_symbol()}")
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(
                    self.amount + other.amount, self.__symbol, _from_factory=True
                )
            return Asset(self.amount + other.amount, self.__symbol, _from_factory=True)
        raise TypeError(f"Operand must be an instance of {self.__symbol}")

    def __radd__(self, other):
        """
        Handles addition when Asset is on the right side of the operator.

        Parameters:
        other (int, float): The other operand.

        Returns:
        Asset: A new instance representing the sum.
        """
        if isinstance(other, (int, float)):
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(self.amount + other, self.__symbol, _from_factory=True)
            return Asset(self.amount + other, self.__symbol, _from_factory=True)
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
            if other.get_symbol() != self.__symbol:
                raise TypeError(
                    f"Cannot subtract {other.get_symbol()} from {self.__symbol}"
                )
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(
                    self.amount - other.amount, self.__symbol, _from_factory=True
                )
            return Asset(self.amount - other.amount, self.__symbol, _from_factory=True)
        raise TypeError(f"Operand must be an instance of {self.__symbol}")

    def __neg__(self):
        """
        Returns the negative amount of the current Asset instance.

        Returns:
        Asset: A new instance representing the negative amount.
        """
        # Return USD instance if self is USD
        if isinstance(self, USD):
            return USD(-self.amount, self.__symbol, _from_factory=True)
        return Asset(-self.amount, self.__symbol, _from_factory=True)

    def __mul__(self, other):
        """
        Multiplies the Asset instance by a number.

        Parameters:
        other (float): The number to multiply by.

        Returns:
        Asset: A new instance representing the result.

        Raises:
        TypeError: If 'other' is not a float.
        """
        bot_assert(other, float)
        # Return USD instance if self is USD
        if isinstance(self, USD):
            return USD(self.amount * other, self.__symbol, _from_factory=True)
        return Asset(self.amount * other, self.__symbol, _from_factory=True)

    def __truediv__(self, other):
        """
        Divides the Asset instance by a number, another Asset, or a Price.

        Parameters:
        other (int, float, Asset, or Price): The divisor.

        Returns:
        Asset, float, or Token: Depending on the type of 'other'.

        Raises:
        TypeError: If 'other' is not a valid type.
        ZeroDivisionError: If division by zero is attempted.
        """
        from python_trading_objects.quotes.coin import Token
        from python_trading_objects.quotes.price import Price

        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division by zero not allowed")
            # Return USD instance if self is USD
            if isinstance(self, USD):
                return USD(self.amount / other, self.__symbol, _from_factory=True)
            return Asset(self.amount / other, self.__symbol, _from_factory=True)

        if isinstance(other, Asset):
            if other.amount == 0:
                raise ZeroDivisionError("Division by zero not allowed")
            if other.get_symbol() != self.__symbol:
                # Division between different assets gives an exchange rate
                return self.amount / other.amount
            return self.amount / other.amount

        if isinstance(other, Price):
            if other.price == 0:
                raise ZeroDivisionError("Division by zero not allowed")
            # Division Asset / Price gives tokens
            return Token(
                self.amount / other.price, other.get_base(), _from_factory=True
            )

        raise TypeError(f"Operand must be a number, {self.__symbol} or Price")

    def to_dict(self):
        """Converts the object to a dictionary."""
        return dict(price=self.amount, symbol=self.__symbol)

    def to_json(self):
        """Converts the object to JSON."""
        return json.dumps(self.to_dict())


# For backward compatibility, create USD alias
class USD(Asset):
    """Alias for compatibility with legacy code."""

    def __init__(
        self, amount: float, quote_symbol: str = "USD", _from_factory: bool = False
    ):
        """
        Initializes a USD instance (legacy compatibility).

        Parameters:
        amount (float): The USD amount.
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
        """Converts the object to a dictionary (legacy format)."""
        return dict(price=self.amount)

    def to_json(self):
        """Converts the object to JSON (legacy format)."""
        return json.dumps(self.to_dict())
