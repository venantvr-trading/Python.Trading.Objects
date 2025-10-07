"""Unit tests for PositionCalculator"""
import pytest

from python_trading_objects.domain.position_calculator import PositionCalculator
from python_trading_objects.domain.trading_position import TradingPosition
from python_trading_objects.quotes.pair import BotPair


class TestPositionCalculator:
    """Test suite for PositionCalculator static methods"""

    @pytest.fixture
    def bot_pair(self):
        """Create a BotPair for testing"""
        return BotPair("BTC/USDT")

    @pytest.fixture
    def positions(self, bot_pair):
        """Create sample positions for testing"""
        return [
            TradingPosition(
                id="pos-1",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(50000),
                number_of_tokens=bot_pair.create_token(0.1),
                expected_sale_price=bot_pair.create_price(51000),
                next_purchase_price=bot_pair.create_price(49000),
                variations={"buy": 0.02, "sell": 0.02}
            ),
            TradingPosition(
                id="pos-2",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(52000),
                number_of_tokens=bot_pair.create_token(0.05),
                expected_sale_price=bot_pair.create_price(53000),
                next_purchase_price=bot_pair.create_price(51000),
                variations={"buy": 0.02, "sell": 0.02}
            ),
            TradingPosition(
                id="pos-3",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(48000),
                number_of_tokens=bot_pair.create_token(0.15),
                expected_sale_price=bot_pair.create_price(49000),
                next_purchase_price=bot_pair.create_price(47000),
                variations={"buy": 0.02, "sell": 0.02}
            )
        ]

    def test_total_value(self, positions, bot_pair):
        """Test calculating total value of positions"""
        current_price = bot_pair.create_price(51000)

        total = PositionCalculator.total_value(positions, current_price)

        # pos-1: 0.1 * 51000 = 5100
        # pos-2: 0.05 * 51000 = 2550
        # pos-3: 0.15 * 51000 = 7650
        # Total = 15300
        expected_total = (0.1 + 0.05 + 0.15) * 51000
        assert abs(float(total.amount) - expected_total) < 0.01
        assert total.symbol == "USDT"

    def test_total_value_empty_list(self, bot_pair):
        """Test total value with empty positions list"""
        current_price = bot_pair.create_price(50000)
        total = PositionCalculator.total_value([], current_price)

        assert float(total.amount) == 0
        assert total.symbol == "USDT"

    def test_total_cost_basis(self, positions):
        """Test calculating total cost basis"""
        total_cost = PositionCalculator.total_cost_basis(positions)

        # pos-1: 50000 * 0.1 = 5000
        # pos-2: 52000 * 0.05 = 2600
        # pos-3: 48000 * 0.15 = 7200
        # Total = 14800
        expected_cost = 50000 * 0.1 + 52000 * 0.05 + 48000 * 0.15
        assert abs(float(total_cost.amount) - expected_cost) < 0.01
        assert total_cost.symbol == "USDT"

    def test_total_cost_basis_empty_list(self):
        """Test total cost basis with empty positions list"""
        total_cost = PositionCalculator.total_cost_basis([])

        assert float(total_cost.amount) == 0
        assert total_cost.symbol == "USDT"

    def test_weighted_average_price(self, positions):
        """Test calculating weighted average purchase price"""
        avg_price = PositionCalculator.weighted_average_price(positions)

        # Total cost: 14800 (from previous test)
        # Total tokens: 0.1 + 0.05 + 0.15 = 0.3
        # Average: 14800 / 0.3 = 49333.33
        expected_avg = (50000 * 0.1 + 52000 * 0.05 + 48000 * 0.15) / 0.3
        assert abs(float(avg_price.price) - expected_avg) < 0.01
        assert avg_price.base_symbol == "BTC"
        assert avg_price.quote_symbol == "USDT"

    def test_weighted_average_price_empty_list(self):
        """Test weighted average with empty positions list"""
        with pytest.raises(ValueError, match="Cannot calculate average of empty positions"):
            PositionCalculator.weighted_average_price([])

    def test_weighted_average_price_zero_tokens(self, bot_pair):
        """Test weighted average with zero total tokens"""
        positions = [
            TradingPosition(
                id="pos-1",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(50000),
                number_of_tokens=bot_pair.create_token(0),
                expected_sale_price=bot_pair.create_price(51000),
                next_purchase_price=bot_pair.create_price(49000),
                variations={}
            )
        ]

        with pytest.raises(ValueError, match="Cannot calculate average: total tokens is zero"):
            PositionCalculator.weighted_average_price(positions)

    def test_aggregate_roi_profit(self, positions, bot_pair):
        """Test aggregate ROI calculation with profit"""
        current_price = bot_pair.create_price(51000)

        roi = PositionCalculator.aggregate_roi(positions, current_price)

        # Total cost: 14800
        # Total value: 15300 (at 51000)
        # ROI: (15300 - 14800) / 14800 * 100 = 3.378%
        expected_roi = ((15300 - 14800) / 14800) * 100
        assert abs(roi - expected_roi) < 0.1

    def test_aggregate_roi_loss(self, positions, bot_pair):
        """Test aggregate ROI calculation with loss"""
        current_price = bot_pair.create_price(45000)

        roi = PositionCalculator.aggregate_roi(positions, current_price)

        # Total cost: 14800
        # Total value: 0.3 * 45000 = 13500
        # ROI: (13500 - 14800) / 14800 * 100 = -8.78%
        total_tokens = 0.3
        total_value = total_tokens * 45000
        total_cost = 14800
        expected_roi = ((total_value - total_cost) / total_cost) * 100
        assert abs(roi - expected_roi) < 0.1

    def test_aggregate_roi_empty_list(self, bot_pair):
        """Test aggregate ROI with empty positions list"""
        current_price = bot_pair.create_price(50000)
        roi = PositionCalculator.aggregate_roi([], current_price)

        assert roi == 0.0

    def test_aggregate_roi_zero_cost(self, bot_pair):
        """Test aggregate ROI with zero cost basis (edge case)"""
        # Create position with zero cost
        positions = [
            TradingPosition(
                id="pos-1",
                pair=bot_pair,
                purchase_price=bot_pair.create_price(0),
                number_of_tokens=bot_pair.create_token(1),
                expected_sale_price=bot_pair.create_price(100),
                next_purchase_price=bot_pair.create_price(0),
                variations={}
            )
        ]

        current_price = bot_pair.create_price(50000)
        roi = PositionCalculator.aggregate_roi(positions, current_price)

        # Should return 0 to avoid division by zero
        assert roi == 0.0

    def test_single_position(self, bot_pair):
        """Test calculations with single position"""
        position = TradingPosition(
            id="pos-1",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(0.1),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={}
        )

        positions = [position]
        current_price = bot_pair.create_price(55000)

        # Total value
        total = PositionCalculator.total_value(positions, current_price)
        assert abs(float(total.amount) - 5500) < 0.01

        # Total cost
        cost = PositionCalculator.total_cost_basis(positions)
        assert abs(float(cost.amount) - 5000) < 0.01

        # Weighted average (should equal purchase price for single position)
        avg = PositionCalculator.weighted_average_price(positions)
        assert abs(float(avg.price) - 50000) < 0.01

        # ROI
        roi = PositionCalculator.aggregate_roi(positions, current_price)
        expected_roi = ((5500 - 5000) / 5000) * 100  # 10%
        assert abs(roi - expected_roi) < 0.01

    def test_consistency_across_methods(self, positions, bot_pair):
        """Test that methods are consistent with each other"""
        current_price = bot_pair.create_price(51000)

        # Calculate using aggregate methods
        total_value = PositionCalculator.total_value(positions, current_price)
        total_cost = PositionCalculator.total_cost_basis(positions)
        aggregate_roi = PositionCalculator.aggregate_roi(positions, current_price)

        # Calculate ROI manually from value and cost
        manual_roi = ((float(total_value.amount) - float(total_cost.amount)) / float(total_cost.amount)) * 100

        # Should match aggregate_roi
        assert abs(aggregate_roi - manual_roi) < 0.01
