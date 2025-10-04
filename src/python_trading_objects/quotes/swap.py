"""
Unified swap/trade abstractions for CEX and DEX operations.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer


class SwapType(Enum):
    """Types of swaps available across exchanges."""

    MARKET = "market"  # CEX market order / DEX instant swap
    LIMIT = "limit"  # CEX limit order / DEX limit order (1inch, etc)
    TWAP = "twap"  # Time-weighted average price (both)
    STOP = "stop"  # Stop order (mainly CEX)


class SwapDirection(Enum):
    """Direction of the swap operation."""

    BUY = "buy"  # Swap quote → base (USDC → BTC)
    SELL = "sell"  # Swap base → quote (BTC → USDC)
    SWAP = "swap"  # Generic swap (any → any)


class SwapRequest(BaseModel):
    """Represents a swap request between two assets."""

    # Configuration Pydantic
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False,  # Keep enum instances
        extra="forbid",
    )

    from_symbol: str = Field(..., description="Symbol of the asset to swap from")
    to_symbol: str = Field(..., description="Symbol of the asset to swap to")
    amount: float = Field(..., description="Amount to swap", ge=0)
    swap_type: SwapType = Field(
        default=SwapType.MARKET, description="Type of swap (market, limit, etc.)"
    )
    pair: str = Field(default="", description="Trading pair")
    reverse_pair: str = Field(default="", description="Reverse trading pair")
    direction: SwapDirection = Field(
        default=SwapDirection.SWAP, description="Direction of swap"
    )

    def __init__(
        self,
        from_symbol: str,
        to_symbol: str,
        amount: float,
        swap_type: SwapType = SwapType.MARKET,
        **data
    ):
        """
        Creates a swap request.

        Parameters:
        from_symbol: Symbol of the asset to swap from
        to_symbol: Symbol of the asset to swap to
        amount: Amount to swap
        swap_type: Type of swap (market, limit, etc.)
        """
        # Determine trading pair
        pair = f"{from_symbol}/{to_symbol}"
        reverse_pair = f"{to_symbol}/{from_symbol}"

        # Identify swap direction
        direction = SwapRequest._determine_direction_static(from_symbol, to_symbol)

        super().__init__(
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            amount=amount,
            swap_type=swap_type,
            pair=pair,
            reverse_pair=reverse_pair,
            direction=direction,
            **data
        )

    @staticmethod
    def _determine_direction_static(
        from_symbol: str, to_symbol: str
    ) -> SwapDirection:
        """Determines if this is a buy, sell, or generic swap."""
        stablecoins = ["USD", "USDC", "USDT", "DAI", "BUSD", "EUR", "GBP"]
        fiats = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
        quotes = stablecoins + fiats

        from_is_quote = from_symbol in quotes
        to_is_quote = to_symbol in quotes

        if from_is_quote and not to_is_quote:
            return SwapDirection.BUY  # Buying base with quote
        elif not from_is_quote and to_is_quote:
            return SwapDirection.SELL  # Selling base for quote
        else:
            return SwapDirection.SWAP  # Generic swap (crypto-to-crypto)

    @field_validator("from_symbol", "to_symbol")
    @classmethod
    def validate_symbols(cls, v):
        """Valide que les symboles sont des chaînes non vides."""
        if not isinstance(v, str) or not v:
            raise ValueError("Symbol must be a non-empty string")
        return v.upper()

    def is_buy(self) -> bool:
        """Checks if this is a buy operation (quote → base)."""
        return self.direction == SwapDirection.BUY

    def is_sell(self) -> bool:
        """Checks if this is a sell operation (base → quote)."""
        return self.direction == SwapDirection.SELL

    def is_swap(self) -> bool:
        """Checks if this is a generic swap (any → any)."""
        return self.direction == SwapDirection.SWAP

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Sérialise le modèle avec les float en string pour préserver la précision."""
        return {
            "from_symbol": self.from_symbol,
            "to_symbol": self.to_symbol,
            "amount": str(self.amount),
            "swap_type": self.swap_type.value,
            "pair": self.pair,
            "reverse_pair": self.reverse_pair,
            "direction": self.direction.value,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converts the swap request to a dictionary with float as string for precision."""
        return {
            "from": self.from_symbol,
            "to": self.to_symbol,
            "amount": str(self.amount),
            "type": self.swap_type.value,
            "direction": self.direction.value,
            "pair": self.pair,
        }


class SwapQuote(BaseModel):
    """Represents a price quote for a swap."""

    # Configuration Pydantic
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    rate: float = Field(
        ..., description="Exchange rate (how many 'to' assets per 'from' asset)"
    )
    from_symbol: str = Field(..., description="Symbol of the asset to swap from")
    to_symbol: str = Field(..., description="Symbol of the asset to swap to")
    fees: float = Field(default=0.0, description="Total fees (percentage or absolute)")
    slippage: float = Field(default=0.0, description="Expected slippage (DEX)")
    gas_estimate: Optional[float] = Field(
        default=None, description="Estimated gas cost (DEX only)"
    )

    def __init__(
        self,
        rate: float,
        from_symbol: str,
        to_symbol: str,
        fees: float = 0.0,
        slippage: float = 0.0,
        gas_estimate: Optional[float] = None,
    ):
        """
        Creates a swap quote.

        Parameters:
        rate: Exchange rate (how many 'to' assets per 'from' asset)
        from_symbol: Symbol of the asset to swap from
        to_symbol: Symbol of the asset to swap to
        fees: Total fees (percentage or absolute)
        slippage: Expected slippage (DEX)
        gas_estimate: Estimated gas cost (DEX only)
        """
        super().__init__(
            rate=rate,
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            fees=fees,
            slippage=slippage,
            gas_estimate=gas_estimate,
        )

    @field_validator("from_symbol", "to_symbol")
    @classmethod
    def validate_symbols(cls, v):
        """Valide que les symboles sont des chaînes non vides."""
        if not isinstance(v, str) or not v:
            raise ValueError("Symbol must be a non-empty string")
        return v.upper()

    @field_validator("rate", "fees", "slippage")
    @classmethod
    def validate_positive(cls, v):
        """Valide que les valeurs sont positives ou nulles."""
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v

    def estimate_output(self, input_amount: float) -> float:
        """Estimates output amount for given input."""
        gross_output = input_amount * self.rate
        # Apply fees and slippage
        net_output = gross_output * (1 - self.fees) * (1 - self.slippage)
        return net_output

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Sérialise le modèle avec les float en string pour préserver la précision."""
        return {
            "rate": str(self.rate),
            "from_symbol": self.from_symbol,
            "to_symbol": self.to_symbol,
            "fees": str(self.fees),
            "slippage": str(self.slippage),
            "gas_estimate": str(self.gas_estimate) if self.gas_estimate is not None else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converts the quote to a dictionary with float as string for precision."""
        return {
            "rate": str(self.rate),
            "from": self.from_symbol,
            "to": self.to_symbol,
            "fees": str(self.fees),
            "slippage": str(self.slippage),
            "gas_estimate": str(self.gas_estimate) if self.gas_estimate is not None else None,
        }


class SwapResult(BaseModel):
    """Represents the result of an executed swap."""

    # Configuration Pydantic
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    request: SwapRequest = Field(..., description="Original swap request")
    executed_rate: float = Field(..., description="Actual execution rate")
    from_amount: float = Field(..., description="Amount swapped from")
    to_amount: float = Field(..., description="Amount received")
    fees_paid: float = Field(..., description="Total fees paid")
    transaction_id: str = Field(
        ..., description="Exchange order ID or blockchain tx hash"
    )
    timestamp: float = Field(..., description="Execution timestamp")
    gas_used: Optional[float] = Field(
        default=None, description="Actual gas used (DEX only)"
    )
    expected_rate: float = Field(default=0.0, description="Expected rate")
    slippage: float = Field(default=0.0, description="Calculated slippage")

    def __init__(
        self,
        request: SwapRequest,
        executed_rate: float,
        from_amount: float,
        to_amount: float,
        fees_paid: float,
        transaction_id: str,
        timestamp: float,
        gas_used: Optional[float] = None,
        **data
    ):
        """
        Creates a swap result.

        Parameters:
        request: Original swap request
        executed_rate: Actual execution rate
        from_amount: Amount swapped from
        to_amount: Amount received
        fees_paid: Total fees paid
        transaction_id: Exchange order ID or blockchain tx hash
        timestamp: Execution timestamp
        gas_used: Actual gas used (DEX only)
        """
        # Calculate slippage from expected
        expected_rate = to_amount / from_amount if from_amount > 0 else 0
        if expected_rate > 0 and executed_rate > 0:
            slippage = abs((expected_rate - executed_rate) / executed_rate)
        else:
            slippage = 0

        super().__init__(
            request=request,
            executed_rate=executed_rate,
            from_amount=from_amount,
            to_amount=to_amount,
            fees_paid=fees_paid,
            transaction_id=transaction_id,
            timestamp=timestamp,
            gas_used=gas_used,
            expected_rate=expected_rate,
            slippage=slippage,
            **data
        )

    @field_validator("from_amount", "to_amount", "fees_paid")
    @classmethod
    def validate_positive(cls, v):
        """Valide que les montants sont positifs ou nuls."""
        if v < 0:
            raise ValueError("Amount must be non-negative")
        return v

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Sérialise le modèle avec les float en string pour préserver la précision."""
        return {
            "request": self.request.model_dump(),
            "executed_rate": str(self.executed_rate),
            "from_amount": str(self.from_amount),
            "to_amount": str(self.to_amount),
            "fees_paid": str(self.fees_paid),
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp,
            "gas_used": str(self.gas_used) if self.gas_used is not None else None,
            "expected_rate": str(self.expected_rate),
            "slippage": str(self.slippage),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converts the result to a dictionary with float as string for precision."""
        return {
            "request": self.request.to_dict(),
            "executed_rate": str(self.executed_rate),
            "from_amount": str(self.from_amount),
            "to_amount": str(self.to_amount),
            "fees_paid": str(self.fees_paid),
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp,
            "gas_used": str(self.gas_used) if self.gas_used is not None else None,
            "slippage": str(self.slippage),
        }
