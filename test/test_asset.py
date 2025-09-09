"""
Unit tests for the Asset class and its integration with BotPair.
"""
import pytest
from venantvr.quotes.asset import Asset, USD
from venantvr.quotes.pair import BotPair
from venantvr.quotes.price import Price
from venantvr.quotes.coin import Token


class TestAssetCreation:
    """Tests for Asset instantiation and factory methods."""
    
    def test_asset_requires_factory(self):
        """Test that Asset cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            Asset(100.0, "EUR")
        assert "Use BotPair.create_asset()" in str(exc_info.value)
    
    def test_create_asset_via_botpair(self):
        """Test creating assets through BotPair factory."""
        pair = BotPair("BTC/EUR")
        
        # Test base asset creation
        btc = pair.create_base_asset(1.5)
        assert btc.get_symbol() == "BTC"
        assert btc.amount == 1.5
        assert str(btc) == "1.50000000 BTC"
        
        # Test quote asset creation
        eur = pair.create_quote_asset(50000.0)
        assert eur.get_symbol() == "EUR"
        assert eur.amount == 50000.0
        assert str(eur) == "50000.00 EUR"
    
    def test_zero_assets(self):
        """Test creating zero-value assets."""
        pair = BotPair("ETH/USDC")
        
        zero_eth = pair.zero_base()
        assert zero_eth.amount == 0.0
        assert zero_eth.get_symbol() == "ETH"
        
        zero_usdc = pair.zero_quote()
        assert zero_usdc.amount == 0.0
        assert zero_usdc.get_symbol() == "USDC"
    
    def test_asset_type_detection(self):
        """Test stablecoin and fiat detection."""
        pair_usd = BotPair("BTC/USD")
        pair_usdc = BotPair("ETH/USDC")
        pair_eur = BotPair("BTC/EUR")
        pair_btc = BotPair("DOGE/BTC")
        
        usd = pair_usd.create_quote_asset(100)
        usdc = pair_usdc.create_quote_asset(100)
        eur = pair_eur.create_quote_asset(100)
        btc = pair_btc.create_quote_asset(1)
        
        # Test fiat detection
        assert usd.is_fiat() == True
        assert eur.is_fiat() == True
        assert usdc.is_fiat() == False
        assert btc.is_fiat() == False
        
        # Test stablecoin detection
        assert usd.is_stablecoin() == True  # USD is both fiat and stablecoin
        assert usdc.is_stablecoin() == True
        assert eur.is_stablecoin() == False
        assert btc.is_stablecoin() == False


class TestAssetArithmetic:
    """Tests for Asset arithmetic operations."""
    
    def test_asset_addition(self):
        """Test adding assets of the same type."""
        pair = BotPair("BTC/EUR")
        eur1 = pair.create_quote_asset(1000.0)
        eur2 = pair.create_quote_asset(500.0)
        
        result = eur1 + eur2
        assert result.amount == 1500.0
        assert result.get_symbol() == "EUR"
    
    def test_asset_addition_different_symbols_fails(self):
        """Test that adding different asset types fails."""
        pair1 = BotPair("BTC/EUR")
        pair2 = BotPair("BTC/USD")
        
        eur = pair1.create_quote_asset(1000.0)
        usd = pair2.create_quote_asset(1000.0)
        
        with pytest.raises(TypeError) as exc_info:
            eur + usd
        assert "Cannot add EUR with USD" in str(exc_info.value)
    
    def test_asset_subtraction(self):
        """Test subtracting assets of the same type."""
        pair = BotPair("ETH/USDC")
        usdc1 = pair.create_quote_asset(5000.0)
        usdc2 = pair.create_quote_asset(2000.0)
        
        result = usdc1 - usdc2
        assert result.amount == 3000.0
        assert result.get_symbol() == "USDC"
    
    def test_asset_multiplication(self):
        """Test multiplying asset by a float."""
        pair = BotPair("BTC/USD")
        usd = pair.create_quote_asset(1000.0)
        
        result = usd * 2.5
        assert result.amount == 2500.0
        assert result.get_symbol() == "USD"
    
    def test_asset_division_by_float(self):
        """Test dividing asset by a float."""
        pair = BotPair("ETH/EUR")
        eur = pair.create_quote_asset(5000.0)
        
        result = eur / 2.0
        assert result.amount == 2500.0
        assert result.get_symbol() == "EUR"
    
    def test_asset_division_by_price(self):
        """Test dividing asset by price to get tokens."""
        pair = BotPair("BTC/USD")
        usd = pair.create_quote_asset(50000.0)
        price = pair.create_price(25000.0)
        
        result = usd / price
        assert isinstance(result, Token)
        assert result.amount == 2.0
        assert result.get_base() == "BTC"
    
    def test_asset_negation(self):
        """Test negating an asset."""
        pair = BotPair("BTC/EUR")
        eur = pair.create_quote_asset(1000.0)
        
        result = -eur
        assert result.amount == -1000.0
        assert result.get_symbol() == "EUR"


class TestAssetComparison:
    """Tests for Asset comparison operations."""
    
    def test_asset_equality(self):
        """Test asset equality comparison."""
        pair = BotPair("BTC/USD")
        usd1 = pair.create_quote_asset(1000.0)
        usd2 = pair.create_quote_asset(1000.0)
        usd3 = pair.create_quote_asset(500.0)
        
        assert usd1 == usd2
        assert not (usd1 == usd3)
    
    def test_asset_less_than(self):
        """Test asset less than comparison."""
        pair = BotPair("ETH/USDC")
        usdc1 = pair.create_quote_asset(1000.0)
        usdc2 = pair.create_quote_asset(2000.0)
        
        assert usdc1 < usdc2
        assert not (usdc2 < usdc1)
        
        # Test comparison with float
        assert usdc1 < 1500.0
        assert not (usdc1 < 500.0)
    
    def test_asset_comparison_different_symbols_fails(self):
        """Test that comparing different asset types fails."""
        pair1 = BotPair("BTC/EUR")
        pair2 = BotPair("BTC/USD")
        
        eur = pair1.create_quote_asset(1000.0)
        usd = pair2.create_quote_asset(1000.0)
        
        with pytest.raises(TypeError) as exc_info:
            eur < usd
        assert "Cannot compare EUR with USD" in str(exc_info.value)


class TestAssetFormatting:
    """Tests for Asset string formatting."""
    
    def test_fiat_formatting(self):
        """Test that fiat currencies use 2 decimal places."""
        pair = BotPair("BTC/EUR")
        eur = pair.create_quote_asset(1234.56789)
        assert str(eur) == "1234.56 EUR"
        
        pair_usd = BotPair("ETH/USD")
        usd = pair_usd.create_quote_asset(9999.999)
        assert str(usd) == "9999.99 USD"
    
    def test_stablecoin_formatting(self):
        """Test that stablecoins use 2 decimal places."""
        pair = BotPair("BTC/USDC")
        usdc = pair.create_quote_asset(5000.123456)
        assert str(usdc) == "5000.12 USDC"
        
        pair_usdt = BotPair("ETH/USDT")
        usdt = pair_usdt.create_quote_asset(2500.999)
        assert str(usdt) == "2500.99 USDT"
    
    def test_crypto_formatting(self):
        """Test that crypto assets use 8 decimal places."""
        pair = BotPair("ETH/BTC")
        btc = pair.create_quote_asset(0.12345678901)
        assert str(btc) == "0.12345678 BTC"
        
        eth = pair.create_base_asset(10.0)
        assert str(eth) == "10.00000000 ETH"


class TestBackwardCompatibility:
    """Tests for backward compatibility with USD class."""
    
    def test_usd_import_works(self):
        """Test that importing USD from legacy module works."""
        from venantvr.quotes.usd import USD
        pair = BotPair("BTC/USDT")
        
        # Legacy create_usd method should work
        usdt = pair.create_usd(1000.0)
        assert usdt.get_symbol() == "USDT"
        assert str(usdt) == "1000.00 USDT"
    
    def test_usd_class_alias(self):
        """Test that USD class is properly aliased to Asset."""
        from venantvr.quotes.asset import USD as AssetUSD
        from venantvr.quotes.usd import USD as LegacyUSD
        
        # Both should be the same class
        assert AssetUSD == LegacyUSD
    
    def test_legacy_zero_usd(self):
        """Test legacy zero_usd method."""
        pair = BotPair("ETH/EUR")
        zero = pair.zero_usd()
        
        assert zero.amount == 0.0
        assert zero.get_symbol() == "EUR"
        assert str(zero) == "0.00 EUR"
    
    def test_usd_get_quote_method(self):
        """Test legacy get_quote method on USD."""
        pair = BotPair("BTC/USDC")
        usdc = pair.create_usd(1000.0)
        
        # USD class should have get_quote for compatibility
        if hasattr(usdc, 'get_quote'):
            assert usdc.get_quote() == "USDC"


class TestAssetSerialization:
    """Tests for Asset JSON serialization."""
    
    def test_asset_to_dict(self):
        """Test converting asset to dictionary."""
        pair = BotPair("BTC/EUR")
        eur = pair.create_quote_asset(1234.56)
        
        data = eur.to_dict()
        assert data['price'] == 1234.56
        assert data['symbol'] == 'EUR'
    
    def test_asset_to_json(self):
        """Test converting asset to JSON."""
        import json
        
        pair = BotPair("ETH/USDC")
        usdc = pair.create_quote_asset(5000.0)
        
        json_str = usdc.to_json()
        data = json.loads(json_str)
        
        assert data['price'] == 5000.0
        assert data['symbol'] == 'USDC'


class TestExoticPairs:
    """Tests for non-standard trading pairs."""
    
    def test_crypto_to_crypto_pair(self):
        """Test crypto-to-crypto pairs work correctly."""
        pair = BotPair("ETH/BTC")
        
        eth = pair.create_base_asset(10.0)
        btc = pair.create_quote_asset(0.5)
        
        assert eth.get_symbol() == "ETH"
        assert btc.get_symbol() == "BTC"
        assert str(eth) == "10.00000000 ETH"
        assert str(btc) == "0.50000000 BTC"
    
    def test_fiat_to_fiat_pair(self):
        """Test fiat-to-fiat pairs (forex)."""
        pair = BotPair("EUR/USD")
        
        eur = pair.create_base_asset(1000.0)
        usd = pair.create_quote_asset(1100.0)
        
        assert eur.is_fiat() == True
        assert usd.is_fiat() == True
        assert str(eur) == "1000.00 EUR"
        assert str(usd) == "1100.00 USD"
    
    def test_stablecoin_pair(self):
        """Test stablecoin pairs."""
        pair = BotPair("USDC/USDT")
        
        usdc = pair.create_base_asset(10000.0)
        usdt = pair.create_quote_asset(10000.0)
        
        assert usdc.is_stablecoin() == True
        assert usdt.is_stablecoin() == True
        assert str(usdc) == "10000.00 USDC"
        assert str(usdt) == "10000.00 USDT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])