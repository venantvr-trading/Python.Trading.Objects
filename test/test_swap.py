"""
Unit tests for the Swap classes (SwapRequest, SwapQuote, SwapResult).
"""

import time

import pytest

from python_trading_objects.quotes.swap import (SwapDirection, SwapQuote,
                                                SwapRequest, SwapResult,
                                                SwapType)


class TestSwapRequest:
    """Tests for SwapRequest class."""

    def test_swap_request_creation(self):
        """Test creating a basic swap request."""
        swap = SwapRequest(from_symbol="USDC", to_symbol="BTC", amount=1000.0)

        assert swap.from_symbol == "USDC"
        assert swap.to_symbol == "BTC"
        assert swap.amount == 1000.0
        assert swap.swap_type == SwapType.MARKET
        assert swap.pair == "USDC/BTC"
        assert swap.reverse_pair == "BTC/USDC"

    def test_swap_request_with_limit_type(self):
        """Test creating a limit swap request."""
        swap = SwapRequest(
            from_symbol="BTC", to_symbol="USDC", amount=0.5, swap_type=SwapType.LIMIT
        )

        assert swap.swap_type == SwapType.LIMIT

    def test_swap_direction_buy(self):
        """Test swap direction detection for buy (quote→base)."""
        # USD to BTC is a buy
        swap = SwapRequest("USD", "BTC", 50000)
        assert swap.direction == SwapDirection.BUY
        assert swap.is_buy() == True
        assert swap.is_sell() == False
        assert swap.is_swap() == False

        # USDC to ETH is a buy
        swap2 = SwapRequest("USDC", "ETH", 3000)
        assert swap2.direction == SwapDirection.BUY
        assert swap2.is_buy() == True

        # EUR to BTC is a buy
        swap3 = SwapRequest("EUR", "BTC", 45000)
        assert swap3.direction == SwapDirection.BUY
        assert swap3.is_buy() == True

    def test_swap_direction_sell(self):
        """Test swap direction detection for sell (base→quote)."""
        # BTC to USD is a sell
        swap = SwapRequest("BTC", "USD", 1.5)
        assert swap.direction == SwapDirection.SELL
        assert swap.is_sell() == True
        assert swap.is_buy() == False
        assert swap.is_swap() == False

        # ETH to USDC is a sell
        swap2 = SwapRequest("ETH", "USDC", 10)
        assert swap2.direction == SwapDirection.SELL
        assert swap2.is_sell() == True

    def test_swap_direction_generic(self):
        """Test swap direction for crypto-to-crypto swaps."""
        # BTC to ETH is a generic swap
        swap = SwapRequest("BTC", "ETH", 1.0)
        assert swap.direction == SwapDirection.SWAP
        assert swap.is_swap() == True
        assert swap.is_buy() == False
        assert swap.is_sell() == False

        # ETH to BTC is also a generic swap
        swap2 = SwapRequest("ETH", "BTC", 15.0)
        assert swap2.direction == SwapDirection.SWAP
        assert swap2.is_swap() == True

    def test_swap_request_to_dict(self):
        """Test converting swap request to dictionary."""
        swap = SwapRequest(
            from_symbol="USDT",
            to_symbol="BTC",
            amount=10000.0,
            swap_type=SwapType.LIMIT,
        )

        data = swap.to_dict()
        assert data["from"] == "USDT"
        assert data["to"] == "BTC"
        assert data["amount"] == 10000.0
        assert data["type"] == "limit"
        assert data["direction"] == "buy"
        assert data["pair"] == "USDT/BTC"


class TestSwapQuote:
    """Tests for SwapQuote class."""

    def test_swap_quote_creation(self):
        """Test creating a swap quote."""
        quote = SwapQuote(
            rate=25000.0,
            from_symbol="USDC",
            to_symbol="BTC",
            fees=0.001,  # 0.1%
            slippage=0.002,  # 0.2%
        )

        assert quote.rate == 25000.0
        assert quote.from_symbol == "USDC"
        assert quote.to_symbol == "BTC"
        assert quote.fees == 0.001
        assert quote.slippage == 0.002
        assert quote.gas_estimate is None

    def test_swap_quote_with_gas(self):
        """Test creating a DEX swap quote with gas estimate."""
        quote = SwapQuote(
            rate=0.06,  # 1 ETH = 0.06 BTC
            from_symbol="ETH",
            to_symbol="BTC",
            fees=0.003,  # 0.3% DEX fee
            slippage=0.005,  # 0.5% slippage
            gas_estimate=25.0,  # $25 in gas
        )

        assert quote.gas_estimate == 25.0

    def test_estimate_output(self):
        """Test estimating output amount from quote."""
        quote = SwapQuote(
            rate=1 / 25000.0,  # 1 USDC = 0.00004 BTC
            from_symbol="USDC",
            to_symbol="BTC",
            fees=0.001,  # 0.1% fee
            slippage=0.002,  # 0.2% slippage
        )

        # Input 10000 USDC
        output = quote.estimate_output(10000.0)

        # Expected: 10000 * (1/25000) * (1-0.001) * (1-0.002)
        # = 10000 * 0.00004 * 0.999 * 0.998
        # ≈ 0.3988
        assert abs(output - 0.3988) < 0.0001

    def test_swap_quote_to_dict(self):
        """Test converting swap quote to dictionary."""
        quote = SwapQuote(
            rate=3000.0,
            from_symbol="USDC",
            to_symbol="ETH",
            fees=0.0025,
            slippage=0.001,
            gas_estimate=15.0,
        )

        data = quote.to_dict()
        assert data["rate"] == 3000.0
        assert data["from"] == "USDC"
        assert data["to"] == "ETH"
        assert data["fees"] == 0.0025
        assert data["slippage"] == 0.001
        assert data["gas_estimate"] == 15.0


class TestSwapResult:
    """Tests for SwapResult class."""

    def test_swap_result_creation(self):
        """Test creating a swap result."""
        request = SwapRequest("USDC", "BTC", 10000.0)

        result = SwapResult(
            request=request,
            executed_rate=1 / 24950.0,  # Slightly better than expected
            from_amount=10000.0,
            to_amount=0.4008,
            fees_paid=10.0,  # $10 in fees
            transaction_id="0x123abc",
            timestamp=time.time(),
        )

        assert result.request == request
        assert result.executed_rate == 1 / 24950.0
        assert result.from_amount == 10000.0
        assert result.to_amount == 0.4008
        assert result.fees_paid == 10.0
        assert result.transaction_id == "0x123abc"
        assert result.gas_used is None

    def test_swap_result_with_gas(self):
        """Test creating a DEX swap result with gas used."""
        request = SwapRequest("ETH", "USDC", 5.0)

        result = SwapResult(
            request=request,
            executed_rate=3000.0,
            from_amount=5.0,
            to_amount=14985.0,  # After fees
            fees_paid=15.0,
            transaction_id="0xdef456",
            timestamp=time.time(),
            gas_used=0.005,  # 0.005 ETH in gas
        )

        assert result.gas_used == 0.005

    def test_slippage_calculation(self):
        """Test that slippage is calculated correctly."""
        request = SwapRequest("USDC", "BTC", 10000.0)

        # Scenario: We expected to get 0.4 BTC for 10000 USDC (rate = 0.00004)
        # But we actually got 0.395 BTC for 10000 USDC (rate = 0.0000395)
        # This is 1.25% less than expected
        result = SwapResult(
            request=request,
            executed_rate=0.00004,  # The rate we expected (0.4 BTC / 10000 USDC)
            from_amount=10000.0,
            to_amount=0.395,  # What we actually got
            fees_paid=10.0,
            transaction_id="abc123",
            timestamp=time.time(),
        )

        # Actual rate = 0.395/10000 = 0.0000395
        # Expected rate = 0.00004
        # Slippage = (0.0000395 - 0.00004) / 0.00004 = -0.0125 = 1.25%
        assert abs(result.slippage - 0.0125) < 0.001

    def test_swap_result_to_dict(self):
        """Test converting swap result to dictionary."""
        request = SwapRequest("BTC", "USDC", 2.0, SwapType.MARKET)

        result = SwapResult(
            request=request,
            executed_rate=25000.0,
            from_amount=2.0,
            to_amount=49950.0,
            fees_paid=50.0,
            transaction_id="order_12345",
            timestamp=1234567890.0,
            gas_used=None,
        )

        data = result.to_dict()
        assert data["executed_rate"] == 25000.0
        assert data["from_amount"] == 2.0
        assert data["to_amount"] == 49950.0
        assert data["fees_paid"] == 50.0
        assert data["transaction_id"] == "order_12345"
        assert data["timestamp"] == 1234567890.0
        assert data["gas_used"] is None
        assert "slippage" in data
        assert "request" in data
        assert data["request"]["from"] == "BTC"
        assert data["request"]["to"] == "USDC"


class TestSwapTypes:
    """Tests for SwapType enum."""

    def test_swap_type_values(self):
        """Test SwapType enum values."""
        assert SwapType.MARKET.value == "market"
        assert SwapType.LIMIT.value == "limit"
        assert SwapType.TWAP.value == "twap"
        assert SwapType.STOP.value == "stop"

    def test_swap_direction_values(self):
        """Test SwapDirection enum values."""
        assert SwapDirection.BUY.value == "buy"
        assert SwapDirection.SELL.value == "sell"
        assert SwapDirection.SWAP.value == "swap"


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_stablecoin_to_stablecoin_swap(self):
        """Test swapping between stablecoins."""
        swap = SwapRequest("USDC", "USDT", 10000.0)
        assert swap.direction == SwapDirection.SWAP  # Generic swap
        assert swap.is_swap() == True

    def test_fiat_to_fiat_swap(self):
        """Test forex-like swaps."""
        swap = SwapRequest("EUR", "USD", 1000.0)
        assert swap.direction == SwapDirection.SWAP
        assert swap.is_swap() == True

    def test_zero_amount_swap(self):
        """Test swap with zero amount."""
        swap = SwapRequest("BTC", "USDC", 0.0)
        assert swap.amount == 0.0

        quote = SwapQuote(25000.0, "BTC", "USDC", 0.001, 0.0)
        output = quote.estimate_output(0.0)
        assert output == 0.0

    def test_very_small_amounts(self):
        """Test swaps with very small amounts."""
        swap = SwapRequest("BTC", "USDC", 0.00000001)  # 1 satoshi
        assert swap.amount == 0.00000001

        quote = SwapQuote(25000.0, "BTC", "USDC", 0.001, 0.0)
        output = quote.estimate_output(0.00000001)
        assert output > 0

    def test_very_large_amounts(self):
        """Test swaps with very large amounts."""
        swap = SwapRequest("USDC", "BTC", 1000000000.0)  # 1 billion
        assert swap.amount == 1000000000.0

        quote = SwapQuote(1 / 25000.0, "USDC", "BTC", 0.001, 0.01)
        output = quote.estimate_output(1000000000.0)
        assert output > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
