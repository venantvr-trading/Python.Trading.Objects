# 📚 TradingPosition Domain Model - Usage Guide

## Quick Start

```python
from python_trading_objects.quotes.pair import BotPair
from python_trading_objects.domain import TradingPosition, PositionCalculator

# Setup
pair = BotPair("BTC/USDT")

# Create a position
position = TradingPosition(
    id="pos-123",
    pair=pair,
    purchase_price=pair.create_price(50000),
    number_of_tokens=pair.create_token(0.1),
    expected_sale_price=pair.create_price(51000),
    next_purchase_price=pair.create_price(49000),
    variations={"buy": 0.02, "sell": 0.02},
    strategy_tag="momentum"
)

# Use it
current_price = pair.create_price(52000)

if position.should_sell_at(current_price):
    profit = position.calculate_profit(current_price)
    roi = position.calculate_roi(current_price)
    print(f"Sell! Profit: ${profit.amount}, ROI: {roi}%")
```

---

## 🎯 Core Concepts

### 1. TradingPosition - The Rich Domain Model

`TradingPosition` encapsulates **all** business logic related to a trading position.

**When to use:**

- Inside your application/agents for business logic
- When you need to make trading decisions
- When calculating profits, ROI, or position value

**Key principle:**
> TradingPosition = Data + Behavior (no anemic models!)

---

## 📖 API Reference

### Creating Positions

```python
position = TradingPosition(
    id="unique-id",              # Required: Unique identifier
    pair=bot_pair,               # Required: BotPair instance
    purchase_price=price,        # Required: Price object
    number_of_tokens=tokens,     # Required: Token object
    expected_sale_price=price,   # Required: Target sale price
    next_purchase_price=price,   # Required: Next DCA price
    variations={"buy": 0.02, "sell": 0.02},  # Required: Strategy params

    # Optional
    short_id=1,                  # Optional: Human-readable ID
    strategy_tag="momentum",     # Optional: Strategy name (default: "default")
    notes="My note",             # Optional: Free-form notes
    timestamp=datetime.now()     # Optional: Auto-set to now()
)
```

---

### Business Logic Methods

#### ROI & Profit Calculations

```python
# Calculate ROI at a given price
roi = position.calculate_roi(sale_price)  # Returns: float (percentage)
# Example: 5.2 (meaning 5.2%)

# Calculate profit in quote currency
profit = position.calculate_profit(sale_price)  # Returns: Asset
# Example: Asset(260, "USDT")

# Calculate current value
value = position.calculate_gross_value(current_price)  # Returns: Asset
```

#### Properties (Computed)

```python
# Total investment
cost = position.cost_basis  # Asset

# Expected profit at target price
expected_profit = position.potential_profit  # Asset

# Expected ROI at target price
expected_roi = position.potential_roi  # float
```

#### Trading Signals

```python
# Should we sell at this price?
if position.should_sell_at(current_price):
    execute_sell()

# Should we buy more (DCA)?
if position.should_buy_dca_at(current_price):
    execute_buy()

# Is position profitable at this price?
if position.is_profitable_at(current_price):
    print("In profit!")
```

#### Price Adjustments (Immutable)

```python
# Adjust expected sale price
new_position = position.adjust_expected_sale_price(new_price)
# Returns a NEW position, original unchanged

# Apply trailing stop
updated_position = position.apply_trailing_stop(current_price, trail_pct=0.02)
# Only updates if current price is higher
```

**Important:** These methods return **new** TradingPosition instances (immutable pattern).

---

### Serialization

```python
# To dictionary (for storage/events)
data = position.to_dict()
# Returns: dict with primitive types

# From dictionary (for restoration)
restored = TradingPosition.from_dict(data, bot_pair)
```

**Use cases:**

- Storing in database
- Publishing events
- API responses
- Inter-process communication

---

### Equality & Hashing

```python
# Positions are equal if they have the same ID
pos1 = TradingPosition(id="pos-1", ...)
pos2 = TradingPosition(id="pos-1", ...)  # Different data
pos3 = TradingPosition(id="pos-2", ...)

pos1 == pos2  # True (same ID)
pos1 == pos3  # False (different ID)

# Can be used in sets/dicts
positions = {pos1, pos2, pos3}  # Only pos1 and pos3 in set
```

---

## 💰 Price Enhancements

New methods added to `Price` class:

### Tolerance Checking

```python
price = pair.create_price(50000)
target = pair.create_price(51000)

# Is price within X% of target?
within = price.is_within_percentage(target, tolerance_pct=0.02)
# Returns: bool
```

### Percentage Operations

```python
# Apply percentage change
increased = price.apply_percentage(0.10)  # +10%
decreased = price.apply_percentage(-0.05)  # -5%
# Returns: new Price (original unchanged)

# Calculate distance
distance = price.distance_from(other_price)
# Returns: float (percentage)
# Example: -2.5 means price is 2.5% below other_price
```

### Midpoint

```python
# Calculate midpoint between two prices
buy_price = pair.create_price(49000)
sell_price = pair.create_price(51000)
mid = Price.midpoint(buy_price, sell_price)
# Returns: Price(50000, ...)
```

---

## 🪙 Token Enhancements

New methods added to `Token` class:

### Value Calculation

```python
tokens = pair.create_token(1.5)
price = pair.create_price(50000)

# Calculate value at given price
value = tokens.value_at(price)
# Returns: Asset (1.5 * 50000 = 75000 USDT)
```

### Splitting

```python
tokens = pair.create_token(1.0)

# Split 60/40
first, second = tokens.split(0.6)
# Returns: (Token(0.6, ...), Token(0.4, ...))

# Use cases:
# - Partial profit taking
# - Portfolio rebalancing
# - Risk management
```

---

## 📊 PositionCalculator - Portfolio Operations

Static helper class for aggregating multiple positions.

### Total Values

```python
positions = [pos1, pos2, pos3]
current_price = pair.create_price(53000)

# Total value of all positions
total_value = PositionCalculator.total_value(positions, current_price)
# Returns: Asset

# Total cost basis
total_cost = PositionCalculator.total_cost_basis(positions)
# Returns: Asset
```

### Weighted Average

```python
# Calculate weighted average purchase price
avg_price = PositionCalculator.weighted_average_price(positions)
# Returns: Price

# Useful for:
# - Portfolio reporting
# - Tax calculations
# - Performance analysis
```

### Aggregate ROI

```python
# Calculate overall portfolio ROI
roi = PositionCalculator.aggregate_roi(positions, current_price)
# Returns: float (percentage)

# Takes into account different purchase prices and amounts
```

---

## 🎯 Real-World Usage Patterns

### Pattern 1: Trading Decision Agent

```python
class TradingAgent:
    def evaluate_position(self, position: TradingPosition, market_price: Price):
        # Use domain model for decisions
        if position.should_sell_at(market_price):
            profit = position.calculate_profit(market_price)
            roi = position.calculate_roi(market_price)

            if roi > 5.0:  # Custom business rule
                self.execute_sell(position, market_price)
                self.publish_event(PositionSold(
                    position_id=position.id,
                    roi_percentage=roi,
                    profit_amount=float(profit.amount)
                ))
```

### Pattern 2: Trailing Stop Strategy

```python
class TrailingStopStrategy:
    def __init__(self, trail_percentage: float = 0.02):
        self.trail_pct = trail_percentage

    def update_position(self, position: TradingPosition, current_price: Price):
        # Domain model handles logic
        updated = position.apply_trailing_stop(current_price, self.trail_pct)

        # Only save if changed
        if updated.expected_sale_price != position.expected_sale_price:
            self.save_position(updated)
            return updated

        return position
```

### Pattern 3: Portfolio Dashboard

```python
class PortfolioDashboard:
    def get_summary(self, positions: List[TradingPosition], current_price: Price):
        # Use PositionCalculator for aggregations
        return {
            "total_cost": PositionCalculator.total_cost_basis(positions),
            "total_value": PositionCalculator.total_value(positions, current_price),
            "avg_price": PositionCalculator.weighted_average_price(positions),
            "overall_roi": PositionCalculator.aggregate_roi(positions, current_price),
            "positions_count": len(positions)
        }
```

### Pattern 4: Event Sourcing

```python
class PositionEventStore:
    def save_position_created(self, position: TradingPosition):
        # Serialize to event
        event = PositionCreatedEvent(
            position_id=position.id,
            data=position.to_dict(),
            timestamp=position.timestamp
        )
        self.publish(event)

    def restore_position(self, event_data: dict) -> TradingPosition:
        # Deserialize from event
        return TradingPosition.from_dict(event_data, self.bot_pair)
```

---

## 🔧 Integration with Pydantic (Application Layer)

If you need Pydantic models for API/Events:

```python
from pydantic import BaseModel
from decimal import Decimal
from python_trading_objects.domain import TradingPosition

class PositionDTO(BaseModel):
    """Pydantic adapter for serialization"""
    id: str
    pair: str
    purchase_price: Decimal
    expected_sale_price: Decimal
    number_of_tokens: Decimal
    # ... other fields

    @classmethod
    def from_trading_position(cls, tp: TradingPosition) -> 'PositionDTO':
        return cls(
            id=tp.id,
            pair=tp.pair.pair,
            purchase_price=tp.purchase_price.price,
            # ... map all fields
        )

    def to_trading_position(self, bot_pair: BotPair) -> TradingPosition:
        return TradingPosition(
            id=self.id,
            pair=bot_pair,
            purchase_price=bot_pair.create_price(float(self.purchase_price)),
            # ... map all fields
        )
```

**Separation of concerns:**

- `TradingPosition` = Domain logic (business rules, calculations)
- `PositionDTO` = Infrastructure (serialization, API, events)

---

## ⚠️ Important Notes

### Immutability

TradingPosition follows **immutable pattern** for state changes:

```python
# ❌ BAD - trying to mutate
position.expected_sale_price = new_price  # Won't work (dataclass)

# ✅ GOOD - create new instance
updated_position = position.adjust_expected_sale_price(new_price)
```

**Why?**

- Prevents accidental mutations
- Makes code more predictable
- Enables event sourcing
- Thread-safe

### Factory Pattern

Always use `BotPair` factories, never instantiate directly:

```python
# ❌ BAD
price = Price(50000, "BTC", "USDT")  # TypeError!

# ✅ GOOD
pair = BotPair("BTC/USDT")
price = pair.create_price(50000)
```

### Type Annotations

Code uses modern forward annotations:

```python
from __future__ import annotations  # At top of file

def my_function(position: TradingPosition) -> Asset:
    # No need for string quotes in type hints
    ...
```

---

## 🧪 Testing

The domain model is **easy to test** (no mocks needed):

```python
def test_position_profitability():
    # Arrange
    pair = BotPair("BTC/USDT")
    position = TradingPosition(
        id="test-1",
        pair=pair,
        purchase_price=pair.create_price(50000),
        number_of_tokens=pair.create_token(0.1),
        expected_sale_price=pair.create_price(51000),
        next_purchase_price=pair.create_price(49000),
        variations={"buy": 0.02, "sell": 0.02}
    )

    # Act
    roi = position.calculate_roi(pair.create_price(55000))

    # Assert
    assert roi == 10.0  # 10% profit
```

No mocks, no infrastructure, just pure business logic!

---

## 📚 Additional Resources

- **Full API Tests:** See `test/test_trading_position.py`
- **Integration Examples:** See `test_integration_manual.py`
- **Migration Guide:** See `MIGRATION_VALIDATION.md`
- **Original Spec:** See your migration document

---

## 🤝 Contributing

When adding new domain logic:

1. ✅ Add to `TradingPosition` if position-specific
2. ✅ Add to `Price`/`Token` if universal calculation
3. ✅ Add to `PositionCalculator` if portfolio-level
4. ✅ Write tests first (TDD)
5. ✅ Keep it pure (no side effects)
6. ✅ Document with examples

---

**Happy Trading! 🚀**
