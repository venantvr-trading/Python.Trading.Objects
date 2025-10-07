"""Unit tests for enhanced Price methods"""
import pytest
from decimal import Decimal
from python_trading_objects.quotes.pair import BotPair
from python_trading_objects.quotes.price import Price


class TestPriceEnhancements:
    """Test suite for Price business logic enhancements"""

    @pytest.fixture
    def bot_pair(self):
        """Create a BotPair for testing"""
        return BotPair("BTC/USDT")

    def test_is_within_percentage(self, bot_pair):
        """Test percentage tolerance check"""
        price = bot_pair.create_price(100)
        target = bot_pair.create_price(102)

        # Within 5% tolerance
        assert price.is_within_percentage(target, 0.05) is True

        # Within 2% tolerance
        assert price.is_within_percentage(target, 0.02) is True

        # Not within 1% tolerance
        assert price.is_within_percentage(target, 0.01) is False

        # Test with lower target
        lower_target = bot_pair.create_price(98)
        assert price.is_within_percentage(lower_target, 0.05) is True
        assert price.is_within_percentage(lower_target, 0.01) is False

    def test_is_within_percentage_zero_target(self, bot_pair):
        """Test percentage check with zero target"""
        price = bot_pair.create_price(100)
        zero_target = bot_pair.create_price(0)

        # Should return False for zero target
        assert price.is_within_percentage(zero_target, 0.05) is False

    def test_apply_percentage(self, bot_pair):
        """Test applying percentage change"""
        price = bot_pair.create_price(100)

        # Apply +10%
        increased = price.apply_percentage(0.10)
        assert abs(float(increased.price) - 110) < 0.01

        # Apply -10%
        decreased = price.apply_percentage(-0.10)
        assert abs(float(decreased.price) - 90) < 0.01

        # Apply +2%
        small_increase = price.apply_percentage(0.02)
        assert abs(float(small_increase.price) - 102) < 0.01

        # Original price unchanged
        assert float(price.price) == 100

    def test_apply_percentage_preserves_symbols(self, bot_pair):
        """Test that apply_percentage preserves currency symbols"""
        price = bot_pair.create_price(50000)
        increased = price.apply_percentage(0.05)

        assert increased.base_symbol == "BTC"
        assert increased.quote_symbol == "USDT"

    def test_distance_from(self, bot_pair):
        """Test percentage distance calculation"""
        price = bot_pair.create_price(110)
        other = bot_pair.create_price(100)

        # Distance from lower price (positive)
        distance = price.distance_from(other)
        assert abs(distance - 10.0) < 0.01

        # Distance from higher price (negative)
        distance = other.distance_from(price)
        assert abs(distance - (-9.09)) < 0.1

        # Distance from same price (zero)
        same = bot_pair.create_price(100)
        distance = other.distance_from(same)
        assert abs(distance) < 0.01

    def test_distance_from_zero(self, bot_pair):
        """Test distance calculation with zero price"""
        price = bot_pair.create_price(100)
        zero = bot_pair.create_price(0)

        # Distance from zero is infinity
        distance = price.distance_from(zero)
        assert distance == float('inf')

    def test_midpoint(self, bot_pair):
        """Test midpoint calculation"""
        buy_price = bot_pair.create_price(100)
        sell_price = bot_pair.create_price(200)

        midpoint = Price.midpoint(buy_price, sell_price)
        assert abs(float(midpoint.price) - 150) < 0.01
        assert midpoint.base_symbol == "BTC"
        assert midpoint.quote_symbol == "USDT"

    def test_midpoint_same_prices(self, bot_pair):
        """Test midpoint with identical prices"""
        price = bot_pair.create_price(100)
        midpoint = Price.midpoint(price, price)
        assert abs(float(midpoint.price) - 100) < 0.01

    def test_midpoint_different_symbols_error(self, bot_pair):
        """Test midpoint with incompatible prices"""
        btc_price = bot_pair.create_price(50000)
        eth_pair = BotPair("ETH/USDT")
        eth_price = eth_pair.create_price(3000)

        with pytest.raises(ValueError, match="different symbols"):
            Price.midpoint(btc_price, eth_price)

    def test_chaining_operations(self, bot_pair):
        """Test chaining multiple operations"""
        price = bot_pair.create_price(100)

        # Apply multiple percentage changes
        result = price.apply_percentage(0.10).apply_percentage(0.05)
        expected = 100 * 1.10 * 1.05  # 115.5
        assert abs(float(result.price) - expected) < 0.01

    def test_precision_preservation(self, bot_pair):
        """Test that Decimal precision is preserved"""
        price = bot_pair.create_price(100.123456789)

        # Apply small percentage
        result = price.apply_percentage(0.001)

        # Check precision maintained
        assert isinstance(result.price, Decimal)
        assert float(result.price) > 100.123
