"""Static helper functions for position calculations"""
from __future__ import annotations

from decimal import Decimal
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from python_trading_objects.domain.trading_position import TradingPosition
    from python_trading_objects.quotes.asset import Asset
    from python_trading_objects.quotes.price import Price


class PositionCalculator:
    """Static utility methods for position calculations"""

    @staticmethod
    def total_value(positions: List[TradingPosition], current_price: Price) -> Asset:
        """Calculate total value of multiple positions"""
        from python_trading_objects.quotes.asset import Asset

        if not positions:
            # Return zero asset with quote symbol from price
            return Asset(0, current_price.quote_symbol, _from_factory=True)

        total = sum(
            pos.calculate_gross_value(current_price).amount
            for pos in positions
        )
        quote_symbol = current_price.quote_symbol
        return Asset(total, quote_symbol, _from_factory=True)

    @staticmethod
    def total_cost_basis(positions: List[TradingPosition]) -> Asset:
        """Calculate total cost basis of positions"""
        from python_trading_objects.quotes.asset import Asset

        if not positions:
            return Asset(0, "USDT", _from_factory=True)

        total = sum(pos.cost_basis.amount for pos in positions)
        quote_symbol = positions[0].pair.quote_symbol
        return Asset(total, quote_symbol, _from_factory=True)

    @staticmethod
    def weighted_average_price(positions: List[TradingPosition]) -> Price:
        """Calculate weighted average purchase price"""
        from python_trading_objects.quotes.price import Price

        if not positions:
            raise ValueError("Cannot calculate average of empty positions")

        total_cost = Decimal("0")
        total_tokens = Decimal("0")

        for pos in positions:
            total_cost += pos.cost_basis.amount
            total_tokens += pos.number_of_tokens.amount

        if total_tokens == 0:
            raise ValueError("Cannot calculate average: total tokens is zero")

        avg_price = total_cost / total_tokens
        first_pos = positions[0]
        return Price(
            avg_price,
            first_pos.pair.base_symbol,
            first_pos.pair.quote_symbol,
            _from_factory=True
        )

    @staticmethod
    def aggregate_roi(positions: List[TradingPosition], current_price: Price) -> float:
        """Calculate aggregate ROI for multiple positions"""
        if not positions:
            return 0.0

        total_cost = PositionCalculator.total_cost_basis(positions).amount
        total_value = PositionCalculator.total_value(positions, current_price).amount

        if total_cost == 0:
            return 0.0

        return float(((total_value - total_cost) / total_cost) * 100)
