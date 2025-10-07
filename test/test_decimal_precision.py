"""Test that Decimal types (not float) are used throughout calculations"""
from decimal import Decimal

import pytest

from python_trading_objects.domain.position_calculator import PositionCalculator
from python_trading_objects.domain.trading_position import TradingPosition
from python_trading_objects.quotes.pair import BotPair


class TestDecimalNotFloat:
    """
    Verify that calculations use Decimal types throughout.

    Note: Asset, Token, and Price classes automatically round to their
    configured precision (e.g., 2 decimals for USDT, 8 for BTC).
    These tests verify we're using Decimal (not float) for calculations.
    """

    @pytest.fixture
    def bot_pair(self):
        return BotPair("BTC/USDT")

    @pytest.fixture
    def positions(self, bot_pair):
        """Create sample positions for testing"""
        return [
            TradingPosition(
                id="p1",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(50000),
                number_of_tokens=bot_pair.create_token(Decimal("0.1")),
                expected_sale_price=bot_pair.create_price(51000),
                next_purchase_price=bot_pair.create_price(49000),
                variations={}
            ),
            TradingPosition(
                id="p2",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(51000),
                number_of_tokens=bot_pair.create_token(Decimal("0.05")),
                expected_sale_price=bot_pair.create_price(52000),
                next_purchase_price=bot_pair.create_price(50000),
                variations={}
            ),
        ]

    def test_position_calculator_total_value_uses_decimal(self, positions, bot_pair):
        """Verify total_value returns Decimal (not float)"""
        current_price = bot_pair.create_price(53000)
        total = PositionCalculator.total_value(positions, current_price)

        # Result must be Decimal
        assert isinstance(total.amount, Decimal)
        # Not float
        assert not isinstance(total.amount, float)

    def test_position_calculator_total_cost_uses_decimal(self, positions):
        """Verify total_cost_basis returns Decimal (not float)"""
        total_cost = PositionCalculator.total_cost_basis(positions)

        # Result must be Decimal
        assert isinstance(total_cost.amount, Decimal)
        # Not float
        assert not isinstance(total_cost.amount, float)

    def test_position_calculator_weighted_average_uses_decimal(self, positions):
        """Verify weighted_average_price returns Decimal (not float)"""
        avg_price = PositionCalculator.weighted_average_price(positions)

        # Result must be Decimal
        assert isinstance(avg_price.price, Decimal)
        # Not float
        assert not isinstance(avg_price.price, float)

    def test_position_calculator_aggregate_roi_calculates_correctly(self, positions, bot_pair):
        """Verify aggregate_roi uses Decimal internally (returns float is OK)"""
        current_price = bot_pair.create_price(53000)
        roi = PositionCalculator.aggregate_roi(positions, current_price)

        # ROI returns float (percentage) - that's expected
        assert isinstance(roi, float)

        # Verify calculation is reasonable
        assert 0 < roi < 100  # Should be positive profit

    def test_trailing_stop_uses_decimal(self, bot_pair):
        """Verify trailing stop uses Decimal math"""
        position = TradingPosition(
            id="p1",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(1),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={}
        )

        current_price = bot_pair.create_price(55000)
        updated = position.apply_trailing_stop(current_price, 0.02)

        # Result must be Decimal
        assert isinstance(updated.expected_sale_price.price, Decimal)
        # Not float
        assert not isinstance(updated.expected_sale_price.price, float)

    def test_position_cost_basis_uses_decimal(self, bot_pair):
        """Verify position cost_basis returns Decimal"""
        position = TradingPosition(
            id="p1",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(Decimal("0.5")),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={}
        )

        cost = position.cost_basis

        # Result must be Decimal
        assert isinstance(cost.amount, Decimal)
        # Not float
        assert not isinstance(cost.amount, float)

    def test_position_calculate_profit_uses_decimal(self, bot_pair):
        """Verify calculate_profit returns Decimal"""
        position = TradingPosition(
            id="p1",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(Decimal("0.5")),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={}
        )

        sale_price = bot_pair.create_price(55000)
        profit = position.calculate_profit(sale_price)

        # Result must be Decimal
        assert isinstance(profit.amount, Decimal)
        # Not float
        assert not isinstance(profit.amount, float)

    def test_price_operations_use_decimal(self, bot_pair):
        """Verify Price operations return Decimal"""
        price = bot_pair.create_price(50000)

        # Apply percentage
        increased = price.apply_percentage(0.05)

        # Result must be Decimal
        assert isinstance(increased.price, Decimal)
        # Not float
        assert not isinstance(increased.price, float)

    def test_token_split_uses_decimal(self, bot_pair):
        """Verify Token split returns Decimal"""
        token = bot_pair.create_token(Decimal("1.0"))

        first, second = token.split(0.6)

        # Results must be Decimal
        assert isinstance(first.amount, Decimal)
        assert isinstance(second.amount, Decimal)
        # Not float
        assert not isinstance(first.amount, float)
        assert not isinstance(second.amount, float)

    def test_no_float_in_intermediate_calculations(self, bot_pair):
        """
        Verify we don't convert to float for intermediate calculations.

        This test creates a scenario where float precision loss would
        be visible if we were using float internally.
        """
        # Create 100 small positions
        positions = [
            TradingPosition(
                id=f"p{i}",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(50000),
                number_of_tokens=bot_pair.create_token(Decimal("0.01")),
                expected_sale_price=bot_pair.create_price(51000),
                next_purchase_price=bot_pair.create_price(49000),
                variations={}
            )
            for i in range(100)
        ]

        # Calculate total
        total_cost = PositionCalculator.total_cost_basis(positions)

        # Result is Decimal
        assert isinstance(total_cost.amount, Decimal)

        # Value should be 100 * (50000 * 0.01) = 50000
        # With Asset rounding to 2 decimals for USDT
        expected = Decimal("50000.00")
        assert total_cost.amount == expected

    def test_decimal_types_preserved_through_chain(self, bot_pair):
        """Verify Decimal types are preserved through operation chains"""
        position = TradingPosition(
            id="p1",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(Decimal("0.1")),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={}
        )

        # Chain operations
        current_price = bot_pair.create_price(55000)
        updated = position.apply_trailing_stop(current_price, 0.02)
        profit = updated.calculate_profit(current_price)
        cost = updated.cost_basis

        # All results must be Decimal
        assert isinstance(updated.expected_sale_price.price, Decimal)
        assert isinstance(profit.amount, Decimal)
        assert isinstance(cost.amount, Decimal)

        # None should be float
        assert not isinstance(updated.expected_sale_price.price, float)
        assert not isinstance(profit.amount, float)
        assert not isinstance(cost.amount, float)
