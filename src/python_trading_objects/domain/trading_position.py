"""Rich domain model for trading positions"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from python_trading_objects.quotes.pair import BotPair
    from python_trading_objects.quotes.price import Price
    from python_trading_objects.quotes.coin import Token
    from python_trading_objects.quotes.asset import Asset


@dataclass
class TradingPosition:
    """
    Complete trading position with business logic.

    Represents a position in a trading strategy with all calculations
    and business rules for entering/exiting trades.
    """
    # Identity
    id: str
    pair: BotPair

    # Core data
    purchase_price: Price
    number_of_tokens: Token
    expected_sale_price: Price
    next_purchase_price: Price

    # Strategy metadata
    variations: Dict[str, float]  # {"buy": 0.02, "sell": 0.02}
    strategy_tag: str = "default"  # Generic tag (not "use_case")

    # Optional metadata
    short_id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

    # === Business Logic (Universal) ===

    def calculate_roi(self, sale_price: Price) -> float:
        """
        Calculate Return on Investment percentage.

        Args:
            sale_price: Price at which position would be sold

        Returns:
            ROI as percentage (e.g., 2.5 for 2.5%)
        """
        return float(((sale_price.price - self.purchase_price.price) / self.purchase_price.price) * 100)

    def calculate_profit(self, sale_price: Price) -> Asset:
        """
        Calculate profit in quote currency.

        Args:
            sale_price: Price at which position would be sold

        Returns:
            Profit as Asset object
        """
        sale_value = sale_price * self.number_of_tokens
        cost_value = self.purchase_price * self.number_of_tokens
        return sale_value - cost_value

    def calculate_gross_value(self, current_price: Price) -> Asset:
        """
        Calculate current gross value of position.

        Args:
            current_price: Current market price

        Returns:
            Total value in quote currency
        """
        return current_price * self.number_of_tokens

    @property
    def cost_basis(self) -> Asset:
        """Total amount invested in this position"""
        return self.purchase_price * self.number_of_tokens

    @property
    def potential_profit(self) -> Asset:
        """Profit if sold at expected sale price"""
        return self.calculate_profit(self.expected_sale_price)

    @property
    def potential_roi(self) -> float:
        """ROI if sold at expected sale price"""
        return self.calculate_roi(self.expected_sale_price)

    # === Business Rules (Universal) ===

    def should_sell_at(self, current_price: Price) -> bool:
        """Check if current price meets sell condition"""
        return current_price >= self.expected_sale_price

    def should_buy_dca_at(self, current_price: Price) -> bool:
        """Check if current price meets DCA (Dollar Cost Average) buy condition"""
        return current_price <= self.next_purchase_price

    def is_profitable_at(self, current_price: Price) -> bool:
        """Check if position would be profitable at given price"""
        return current_price > self.purchase_price

    # === Price Adjustments (Universal) ===

    def adjust_expected_sale_price(self, new_price: Price) -> TradingPosition:
        """
        Create new position with adjusted expected sale price.
        Immutable pattern.
        """
        return TradingPosition(
            id=self.id,
            pair=self.pair,
            purchase_price=self.purchase_price,
            number_of_tokens=self.number_of_tokens,
            expected_sale_price=new_price,
            next_purchase_price=self.next_purchase_price,
            variations=self.variations,
            strategy_tag=self.strategy_tag,
            short_id=self.short_id,
            timestamp=self.timestamp,
            notes=self.notes
        )

    def apply_trailing_stop(self, current_price: Price, trail_pct: float) -> TradingPosition:
        """
        Adjust expected sale price based on trailing stop logic.

        Args:
            current_price: Current market price
            trail_pct: Trailing percentage (e.g., 0.02 for 2%)

        Returns:
            New position with updated expected sale price
        """
        from decimal import Decimal

        # Keep Decimal precision throughout
        new_expected = self.pair.create_price(current_price.price * Decimal(str(1 - trail_pct)))

        # Only adjust if new price is higher (trailing up)
        if new_expected > self.expected_sale_price:
            return self.adjust_expected_sale_price(new_expected)

        return self

    # === Serialization (Universal) ===

    def to_dict(self) -> Dict:
        """
        Convert to dictionary with primitives.
        Suitable for JSON serialization or event publishing.
        """
        return {
            'id': self.id,
            'short_id': self.short_id,
            'pair': self.pair.pair,
            'purchase_price': float(self.purchase_price.price),
            'expected_sale_price': float(self.expected_sale_price.price),
            'next_purchase_price': float(self.next_purchase_price.price),
            'number_of_tokens': float(self.number_of_tokens.amount),
            'variations': self.variations,
            'strategy_tag': self.strategy_tag,
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict, bot_pair: BotPair) -> TradingPosition:
        """
        Create TradingPosition from dictionary.

        Args:
            data: Dictionary with position data
            bot_pair: BotPair for creating Price/Token objects

        Returns:
            TradingPosition instance
        """
        return cls(
            id=data['id'],
            short_id=data.get('short_id'),
            pair=bot_pair,
            purchase_price=bot_pair.create_price(float(data['purchase_price'])),
            number_of_tokens=bot_pair.create_token(float(data['number_of_tokens'])),
            expected_sale_price=bot_pair.create_price(float(data['expected_sale_price'])),
            next_purchase_price=bot_pair.create_price(float(data['next_purchase_price'])),
            variations=data['variations'],
            strategy_tag=data.get('strategy_tag', 'default'),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow(),
            notes=data.get('notes')
        )

    # === Comparison & Equality ===

    def __eq__(self, other) -> bool:
        """Positions are equal if they have the same ID"""
        if not isinstance(other, TradingPosition):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (f"TradingPosition(id={self.id}, pair={self.pair.pair}, "
                f"tokens={self.number_of_tokens.amount}, "
                f"purchase={self.purchase_price.price}, "
                f"expected_sale={self.expected_sale_price.price})")
