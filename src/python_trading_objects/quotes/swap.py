"""
Unified swap/trade abstractions for CEX and DEX operations.
"""

from enum import Enum
from typing import Any, Dict, Optional


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


class SwapRequest:
    """Represents a swap request between two assets."""

    def __init__(
        self,
        from_symbol: str,
        to_symbol: str,
        amount: float,
        swap_type: SwapType = SwapType.MARKET,
    ):
        """
        Creates a swap request.

        Parameters:
        from_symbol: Symbol of the asset to swap from
        to_symbol: Symbol of the asset to swap to
        amount: Amount to swap
        swap_type: Type of swap (market, limit, etc.)
        """
        self.from_symbol = from_symbol
        self.to_symbol = to_symbol
        self.amount = amount
        self.swap_type = swap_type

        # Determine trading pair
        self.pair = f"{self.from_symbol}/{self.to_symbol}"
        self.reverse_pair = f"{self.to_symbol}/{self.from_symbol}"

        # Identify swap direction
        self.direction = self._determine_direction()

    def _determine_direction(self) -> SwapDirection:
        """Determines if this is a buy, sell, or generic swap."""
        stablecoins = ["USD", "USDC", "USDT", "DAI", "BUSD", "EUR", "GBP"]
        fiats = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
        quotes = stablecoins + fiats

        from_is_quote = self.from_symbol in quotes
        to_is_quote = self.to_symbol in quotes

        if from_is_quote and not to_is_quote:
            return SwapDirection.BUY  # Buying base with quote
        elif not from_is_quote and to_is_quote:
            return SwapDirection.SELL  # Selling base for quote
        else:
            return SwapDirection.SWAP  # Generic swap (crypto-to-crypto)

    def is_buy(self) -> bool:
        """Checks if this is a buy operation (quote → base)."""
        return self.direction == SwapDirection.BUY

    def is_sell(self) -> bool:
        """Checks if this is a sell operation (base → quote)."""
        return self.direction == SwapDirection.SELL

    def is_swap(self) -> bool:
        """Checks if this is a generic swap (any → any)."""
        return self.direction == SwapDirection.SWAP

    def to_dict(self) -> Dict[str, Any]:
        """Converts the swap request to a dictionary."""
        return {
            "from": self.from_symbol,
            "to": self.to_symbol,
            "amount": self.amount,
            "type": self.swap_type.value,
            "direction": self.direction.value,
            "pair": self.pair,
        }


class SwapQuote:
    """Represents a price quote for a swap."""

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
        self.rate = rate
        self.from_symbol = from_symbol
        self.to_symbol = to_symbol
        self.fees = fees
        self.slippage = slippage
        self.gas_estimate = gas_estimate

    def estimate_output(self, input_amount: float) -> float:
        """Estimates output amount for given input."""
        gross_output = input_amount * self.rate
        # Apply fees and slippage
        net_output = gross_output * (1 - self.fees) * (1 - self.slippage)
        return net_output

    def to_dict(self) -> Dict[str, Any]:
        """Converts the quote to a dictionary."""
        return {
            "rate": self.rate,
            "from": self.from_symbol,
            "to": self.to_symbol,
            "fees": self.fees,
            "slippage": self.slippage,
            "gas_estimate": self.gas_estimate,
        }


class SwapResult:
    """Represents the result of an executed swap."""

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
        self.request = request
        self.executed_rate = executed_rate
        self.from_amount = from_amount
        self.to_amount = to_amount
        self.fees_paid = fees_paid
        self.transaction_id = transaction_id
        self.timestamp = timestamp
        self.gas_used = gas_used

        # Calculate slippage from expected
        # The executed_rate is what we got, expected_rate is what we should have gotten
        self.expected_rate = to_amount / from_amount if from_amount > 0 else 0
        # Slippage is the percentage difference between expected and executed rates
        if self.expected_rate > 0 and executed_rate > 0:
            # For example: if we expected 0.4 BTC but got 0.395 BTC for 10000 USDC
            # expected_rate = 0.395/10000 = 0.0000395
            # executed_rate = 1/25316 = 0.0000395 (the actual rate we got)
            # slippage = difference between them
            self.slippage = abs((self.expected_rate - executed_rate) / executed_rate)
        else:
            self.slippage = 0

    def to_dict(self) -> Dict[str, Any]:
        """Converts the result to a dictionary."""
        return {
            "request": self.request.to_dict(),
            "executed_rate": self.executed_rate,
            "from_amount": self.from_amount,
            "to_amount": self.to_amount,
            "fees_paid": self.fees_paid,
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp,
            "gas_used": self.gas_used,
            "slippage": self.slippage,
        }
