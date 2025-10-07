"""Unit tests for enhanced Token methods"""
import pytest
from decimal import Decimal
from python_trading_objects.quotes.pair import BotPair
from python_trading_objects.quotes.coin import Token
from python_trading_objects.quotes.asset import Asset


class TestTokenEnhancements:
    """Test suite for Token business logic enhancements"""

    @pytest.fixture
    def bot_pair(self):
        """Create a BotPair for testing"""
        return BotPair("BTC/USDT")

    def test_value_at(self, bot_pair):
        """Test calculating token value at given price"""
        token = bot_pair.create_token(0.5)
        price = bot_pair.create_price(50000)

        value = token.value_at(price)

        assert isinstance(value, Asset)
        assert abs(float(value.amount) - 25000) < 0.01
        assert value.symbol == "USDT"

    def test_value_at_zero_tokens(self, bot_pair):
        """Test value calculation with zero tokens"""
        token = bot_pair.create_token(0)
        price = bot_pair.create_price(50000)

        value = token.value_at(price)
        assert float(value.amount) == 0

    def test_value_at_zero_price(self, bot_pair):
        """Test value calculation with zero price"""
        token = bot_pair.create_token(1)
        price = bot_pair.create_price(0)

        value = token.value_at(price)
        assert float(value.amount) == 0

    def test_value_at_invalid_type(self, bot_pair):
        """Test value_at with invalid price type"""
        token = bot_pair.create_token(1)

        with pytest.raises(TypeError, match="must be an instance of Price"):
            token.value_at(50000)  # Passing number instead of Price

    def test_split_equal(self, bot_pair):
        """Test splitting tokens equally"""
        token = bot_pair.create_token(1.0)

        first, second = token.split(0.5)

        assert abs(float(first.amount) - 0.5) < 0.0001
        assert abs(float(second.amount) - 0.5) < 0.0001
        assert first.base_symbol == "BTC"
        assert second.base_symbol == "BTC"

    def test_split_unequal(self, bot_pair):
        """Test splitting tokens unequally"""
        token = bot_pair.create_token(1.0)

        # 30% / 70% split
        first, second = token.split(0.3)

        assert abs(float(first.amount) - 0.3) < 0.0001
        assert abs(float(second.amount) - 0.7) < 0.0001

        # Verify sum equals original
        total = float(first.amount) + float(second.amount)
        assert abs(total - 1.0) < 0.0001

    def test_split_all_to_first(self, bot_pair):
        """Test split with ratio 1.0 (all to first)"""
        token = bot_pair.create_token(1.0)

        first, second = token.split(1.0)

        assert abs(float(first.amount) - 1.0) < 0.0001
        assert abs(float(second.amount) - 0.0) < 0.0001

    def test_split_all_to_second(self, bot_pair):
        """Test split with ratio 0.0 (all to second)"""
        token = bot_pair.create_token(1.0)

        first, second = token.split(0.0)

        assert abs(float(first.amount) - 0.0) < 0.0001
        assert abs(float(second.amount) - 1.0) < 0.0001

    def test_split_invalid_ratio_above(self, bot_pair):
        """Test split with invalid ratio > 1"""
        token = bot_pair.create_token(1.0)

        with pytest.raises(ValueError, match="ratio must be between 0 and 1"):
            token.split(1.5)

    def test_split_invalid_ratio_below(self, bot_pair):
        """Test split with invalid ratio < 0"""
        token = bot_pair.create_token(1.0)

        with pytest.raises(ValueError, match="ratio must be between 0 and 1"):
            token.split(-0.1)

    def test_split_preserves_type(self, bot_pair):
        """Test that split preserves Token type"""
        token = bot_pair.create_token(1.0)

        first, second = token.split(0.6)

        assert isinstance(first, Token)
        assert isinstance(second, Token)

    def test_split_large_amount(self, bot_pair):
        """Test split with large token amount"""
        token = bot_pair.create_token(1000.123456)

        first, second = token.split(0.25)

        expected_first = 1000.123456 * 0.25
        expected_second = 1000.123456 * 0.75

        assert abs(float(first.amount) - expected_first) < 0.01
        assert abs(float(second.amount) - expected_second) < 0.01

    def test_split_precision(self, bot_pair):
        """Test that split maintains Decimal precision"""
        token = bot_pair.create_token(0.123456789)

        first, second = token.split(0.333333)

        # Check precision maintained with Decimal
        assert isinstance(first.amount, Decimal)
        assert isinstance(second.amount, Decimal)

    def test_value_at_and_split_combined(self, bot_pair):
        """Test combining value_at and split operations"""
        token = bot_pair.create_token(1.0)
        price = bot_pair.create_price(50000)

        # Split tokens
        first, second = token.split(0.6)

        # Calculate values
        first_value = first.value_at(price)
        second_value = second.value_at(price)

        # Verify total value equals original
        total_value = float(first_value.amount) + float(second_value.amount)
        expected_total = 50000
        assert abs(total_value - expected_total) < 0.01
