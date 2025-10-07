"""Unit tests for TradingPosition domain model"""
import pytest
from datetime import datetime
from decimal import Decimal
from python_trading_objects.quotes.pair import BotPair
from python_trading_objects.domain.trading_position import TradingPosition


class TestTradingPosition:
    """Test suite for TradingPosition"""

    @pytest.fixture
    def bot_pair(self):
        """Create a BotPair for testing"""
        return BotPair("BTC/USDT")

    @pytest.fixture
    def sample_position(self, bot_pair):
        """Create a sample trading position"""
        return TradingPosition(
            id="pos-123",
            short_id=1,
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(0.1),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={"buy": 0.02, "sell": 0.02},
            strategy_tag="momentum",
            notes="Test position"
        )

    def test_position_creation(self, bot_pair):
        """Test basic position creation"""
        position = TradingPosition(
            id="test-1",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(0.1),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={"buy": 0.02, "sell": 0.02}
        )

        assert position.id == "test-1"
        assert position.pair.pair == "BTC/USDT"
        assert float(position.purchase_price.price) == 50000
        assert float(position.number_of_tokens.amount) == 0.1

    def test_calculate_roi(self, sample_position, bot_pair):
        """Test ROI calculation"""
        # Sale at expected price (51000)
        roi = sample_position.calculate_roi(sample_position.expected_sale_price)
        assert abs(roi - 2.0) < 0.01  # 2% profit

        # Sale at higher price (55000)
        high_price = bot_pair.create_price(55000)
        roi = sample_position.calculate_roi(high_price)
        assert abs(roi - 10.0) < 0.01  # 10% profit

        # Sale at lower price (48000)
        low_price = bot_pair.create_price(48000)
        roi = sample_position.calculate_roi(low_price)
        assert abs(roi - (-4.0)) < 0.01  # -4% loss

    def test_calculate_profit(self, sample_position, bot_pair):
        """Test profit calculation"""
        # Profit at expected sale price
        profit = sample_position.calculate_profit(sample_position.expected_sale_price)
        expected_profit = 51000 * 0.1 - 50000 * 0.1
        assert abs(float(profit.amount) - expected_profit) < 0.01

        # Profit at higher price
        high_price = bot_pair.create_price(55000)
        profit = sample_position.calculate_profit(high_price)
        expected_profit = 55000 * 0.1 - 50000 * 0.1
        assert abs(float(profit.amount) - expected_profit) < 0.01

    def test_calculate_gross_value(self, sample_position, bot_pair):
        """Test gross value calculation"""
        current_price = bot_pair.create_price(52000)
        value = sample_position.calculate_gross_value(current_price)
        expected_value = 52000 * 0.1
        assert abs(float(value.amount) - expected_value) < 0.01

    def test_cost_basis(self, sample_position):
        """Test cost basis property"""
        cost = sample_position.cost_basis
        expected_cost = 50000 * 0.1
        assert abs(float(cost.amount) - expected_cost) < 0.01

    def test_potential_profit(self, sample_position):
        """Test potential profit property"""
        profit = sample_position.potential_profit
        expected_profit = (51000 - 50000) * 0.1
        assert abs(float(profit.amount) - expected_profit) < 0.01

    def test_potential_roi(self, sample_position):
        """Test potential ROI property"""
        roi = sample_position.potential_roi
        assert abs(roi - 2.0) < 0.01

    def test_should_sell_at(self, sample_position, bot_pair):
        """Test sell condition check"""
        # Price above expected sale price
        high_price = bot_pair.create_price(52000)
        assert sample_position.should_sell_at(high_price) is True

        # Price at expected sale price
        assert sample_position.should_sell_at(sample_position.expected_sale_price) is True

        # Price below expected sale price
        low_price = bot_pair.create_price(50000)
        assert sample_position.should_sell_at(low_price) is False

    def test_should_buy_dca_at(self, sample_position, bot_pair):
        """Test DCA buy condition check"""
        # Price below next purchase price
        low_price = bot_pair.create_price(48000)
        assert sample_position.should_buy_dca_at(low_price) is True

        # Price at next purchase price
        assert sample_position.should_buy_dca_at(sample_position.next_purchase_price) is True

        # Price above next purchase price
        high_price = bot_pair.create_price(50000)
        assert sample_position.should_buy_dca_at(high_price) is False

    def test_is_profitable_at(self, sample_position, bot_pair):
        """Test profitability check"""
        # Price above purchase price
        high_price = bot_pair.create_price(51000)
        assert sample_position.is_profitable_at(high_price) is True

        # Price at purchase price
        assert sample_position.is_profitable_at(sample_position.purchase_price) is False

        # Price below purchase price
        low_price = bot_pair.create_price(49000)
        assert sample_position.is_profitable_at(low_price) is False

    def test_adjust_expected_sale_price(self, sample_position, bot_pair):
        """Test adjusting expected sale price"""
        new_price = bot_pair.create_price(52000)
        updated_position = sample_position.adjust_expected_sale_price(new_price)

        # Original position unchanged
        assert float(sample_position.expected_sale_price.price) == 51000

        # New position has updated price
        assert float(updated_position.expected_sale_price.price) == 52000

        # Other attributes preserved
        assert updated_position.id == sample_position.id
        assert float(updated_position.purchase_price.price) == 50000

    def test_apply_trailing_stop(self, sample_position, bot_pair):
        """Test trailing stop logic"""
        # Current price higher, trailing stop should update
        high_price = bot_pair.create_price(55000)
        updated_position = sample_position.apply_trailing_stop(high_price, 0.02)

        expected_new_price = 55000 * (1 - 0.02)  # 53900
        assert float(updated_position.expected_sale_price.price) > 51000
        assert abs(float(updated_position.expected_sale_price.price) - expected_new_price) < 1

        # Current price lower, trailing stop should NOT update
        low_price = bot_pair.create_price(50000)
        same_position = sample_position.apply_trailing_stop(low_price, 0.02)
        assert float(same_position.expected_sale_price.price) == 51000

    def test_to_dict(self, sample_position):
        """Test serialization to dictionary"""
        data = sample_position.to_dict()

        assert data['id'] == "pos-123"
        assert data['short_id'] == 1
        assert data['pair'] == "BTC/USDT"
        assert data['purchase_price'] == 50000
        assert data['expected_sale_price'] == 51000
        assert data['next_purchase_price'] == 49000
        assert data['number_of_tokens'] == 0.1
        assert data['variations'] == {"buy": 0.02, "sell": 0.02}
        assert data['strategy_tag'] == "momentum"
        assert data['notes'] == "Test position"
        assert 'timestamp' in data

    def test_from_dict(self, bot_pair):
        """Test deserialization from dictionary"""
        data = {
            'id': 'pos-456',
            'short_id': 2,
            'pair': 'BTC/USDT',
            'purchase_price': 50000,
            'expected_sale_price': 51000,
            'next_purchase_price': 49000,
            'number_of_tokens': 0.1,
            'variations': {"buy": 0.02, "sell": 0.02},
            'strategy_tag': 'scalping',
            'timestamp': datetime.utcnow().isoformat(),
            'notes': 'Restored position'
        }

        position = TradingPosition.from_dict(data, bot_pair)

        assert position.id == 'pos-456'
        assert position.short_id == 2
        assert float(position.purchase_price.price) == 50000
        assert float(position.expected_sale_price.price) == 51000
        assert position.strategy_tag == 'scalping'

    def test_equality(self, sample_position, bot_pair):
        """Test position equality"""
        # Same ID = equal
        other = TradingPosition(
            id="pos-123",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(60000),  # Different values
            number_of_tokens=bot_pair.create_token(0.2),
            expected_sale_price=bot_pair.create_price(61000),
            next_purchase_price=bot_pair.create_price(59000),
            variations={}
        )
        assert sample_position == other

        # Different ID = not equal
        different = TradingPosition(
            id="pos-999",
            pair=bot_pair,
            purchase_price=bot_pair.create_price(50000),
            number_of_tokens=bot_pair.create_token(0.1),
            expected_sale_price=bot_pair.create_price(51000),
            next_purchase_price=bot_pair.create_price(49000),
            variations={}
        )
        assert sample_position != different

    def test_hash(self, sample_position):
        """Test position hashing"""
        # Can be used in sets/dicts
        positions = {sample_position}
        assert len(positions) == 1
        assert sample_position in positions

    def test_repr(self, sample_position):
        """Test string representation"""
        repr_str = repr(sample_position)
        assert "TradingPosition" in repr_str
        assert "pos-123" in repr_str
        assert "BTC/USDT" in repr_str
