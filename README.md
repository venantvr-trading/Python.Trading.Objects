# Python Trading Objects

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-73%20passed-brightgreen.svg)](#testing)

## Description

`Python Trading Objects` is a Python library for managing trading objects, including representations of amounts (tokens, USD), prices, and a factory pattern for creating
these objects based on currency pairs.

The library provides type-safe, precision-controlled financial objects with arithmetic operations, making it ideal for trading applications, financial calculations, and
cryptocurrency projects.

## Features

- **Type Safety**: Factory pattern ensures consistent types and currency symbols
- **Precision Control**: Configurable decimal precision for different asset types
- **Arithmetic Operations**: Intuitive operator overloading for financial calculations
- **JSON Serialization**: Built-in support for data interchange
- **Complete Test Suite**: 73 test cases for all functionality
- **Zero Dependencies**: Pure Python implementation

## Installation

### From Source

```bash
pip install .
```

For development installation with testing capabilities:

```bash
pip install -e .[dev]
```

### Requirements

- Python >= 3.8

## Quick Start

### Creating Objects with the `BotPair` Factory

The `BotPair` class acts as a factory to ensure consistency of types and currency symbols.

```python
from python_trading_objects.quotes import BotPair

# Create a factory for the Bitcoin/US Dollar pair
bot_pair = BotPair("BTC/USD")

# Create a Token for the base currency (BTC)
btc_amount = bot_pair.create_token(1.5)
print(f"Token created: {btc_amount}")  # Output: "1.50000000 BTC"

# Create a Price for the pair
btc_price = bot_pair.create_price(25000.0)
print(f"Price created: {btc_price}")  # Output: "25000.00 BTC/USD"

# Create a USD object for the quote currency
usd_amount = bot_pair.create_usd(100.0)
print(f"USD amount created: {usd_amount}")  # Output: "100.00 USD"
```

### Arithmetic Operations

Objects in the library overload operators to allow intuitive calculations.

#### Token Operations

```python
token1 = bot_pair.create_token(5.0)
token2 = bot_pair.create_token(3.0)

# Addition
result_add = token1 + token2
print(f"Addition: {result_add}")  # Output: "8.00000000 BTC"

# Subtraction
result_sub = token1 - token2
print(f"Subtraction: {result_sub}")  # Output: "2.00000000 BTC"

# Multiplication by float
result_mul_float = token1 * 2.5
print(f"Multiplication by float: {result_mul_float}")  # Output: "12.50000000 BTC"

# Division by float
result_div_float = token1 / 2.0
print(f"Division by float: {result_div_float}")  # Output: "2.50000000 BTC"
```

#### USD Operations

```python
usd1 = bot_pair.create_usd(50.0)
usd2 = bot_pair.create_usd(30.0)

# Addition
result_add = usd1 + usd2
print(f"Addition: {result_add}")  # Output: "80.00 USD"

# Multiplication by float
result_mul_float = usd1 * 2.5
print(f"Multiplication by float: {result_mul_float}")  # Output: "125.00 USD"

# Division by Price to get Token
price = bot_pair.create_price(20000.0)
result_div_price = usd1 / price
print(f"Division by Price: {result_div_price}")  # Output: "0.00250000 BTC"
```

#### Price Operations

```python
price = bot_pair.create_price(20000.0)
token = bot_pair.create_token(0.5)

# Multiply Price by Token to get USD
result = price * token
print(f"Price * Token: {result}")  # Output: "10000.00 USD"
```

## Core Classes

- **`Quote`**: Abstract base class for currencies, managing amount precision
- **`BotPair`**: Factory class for creating `Token`, `Price`, and `USD` instances safely for a given currency pair
- **`Token`**: Represents an amount of base currency (e.g., 1.5 BTC)
- **`USD`**: Represents an amount of quote currency (e.g., 100 USD). Despite the name, it can represent any quote currency (JPY, EUR, etc.)
- **`Price`**: Represents the price of a base currency relative to a quote currency (e.g., 25000 BTC/USD)

## Testing

The library uses `pytest` for unit testing. Tests validate object creation, arithmetic operations, comparisons, and error handling.

### Run Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest test/test_coin.py -v
```

### Test Suite

The library includes complete testing with 73 test cases validating:

- Factory pattern object creation
- Arithmetic operations and operator overloading
- Type safety and error handling
- JSON serialization and deserialization
- Precision control and truncation
- Edge cases and error conditions

## Development

### Setup Development Environment

```bash
make install
```

### Code Quality Tools

```bash
# Run format and tests together
make check

# Individual commands
make format        # Format code with black and isort
make test          # Run pytest tests

# Clean up generated files
make clean

# Update dependencies
make update
```

## API Reference

### BotPair Factory Methods

- `create_token(amount: float) -> Token`: Create a token for the base currency
- `create_price(amount: float) -> Price`: Create a price for the currency pair
- `create_usd(amount: float) -> USD`: Create a USD amount for the quote currency
- `zero_token() -> Token`: Create a zero-value token
- `zero_price() -> Price`: Create a zero-value price
- `zero_usd() -> USD`: Create a zero-value USD amount

### Arithmetic Operations Support

| Operation            | Token              | USD                    | Price              |
|----------------------|--------------------|------------------------|--------------------|
| Addition (`+`)       | ✓                  | ✓                      | ✓                  |
| Subtraction (`-`)    | ✓                  | ✓                      | ✓                  |
| Multiplication (`*`) | ✓ (by float)       | ✓ (by float)           | ✓ (by float/Token) |
| Division (`/`)       | ✓ (by float/Token) | ✓ (by float/USD/Price) | ✓ (by float/Price) |
| Comparison           | ✓                  | ✓                      | ✓                  |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the test suite (`make all`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**venantvr** - [venantvr@gmail.com](mailto:venantvr@gmail.com)

Project Link: [https://github.com/venantvr/Python.Trading.Objects](https://github.com/venantvr/Python.Trading.Objects)

---

## 🚀 ADDENDUM: Generic Asset Architecture (v2.0)

### **Major Refactoring: From USD-centric to Asset-generic**

**Date**: January 2025  
**Motivation**: Enable support for DEX (Decentralized Exchanges) alongside CEX (Centralized Exchanges) with a unified swap/trade interface.

### **The Problem**

The original architecture was USD-centric:

- The `USD` class was hardcoded for US Dollar operations
- Trading pairs were limited to USD-based quotes (BTC/USD, ETH/USD)
- CEX-specific concepts (buy/sell orders) didn't translate well to DEX swaps
- No abstraction for generic asset-to-asset swaps (e.g., BTC→ETH, EUR→GBP)

### **The Solution: Generic Asset System**

#### **1. New `Asset` Class** (`python_trading_objects/quotes/asset.py`)

A generic asset representation that works with ANY currency or token:

```python
from python_trading_objects.quotes.asset import Asset
from python_trading_objects.quotes.pair import BotPair

# Works with any pair now!
pair_eur = BotPair("BTC/EUR")
pair_eth = BotPair("ETH/USDC")
pair_doge = BotPair("DOGE/BTC")

# Create assets for any currency
btc = pair_eur.create_base_asset(1.5)  # 1.5 BTC
eur = pair_eur.create_quote_asset(50000)  # 50000 EUR
eth = pair_eth.create_base_asset(10)  # 10 ETH
usdc = pair_eth.create_quote_asset(25000)  # 25000 USDC
```

**Features**:

- ✅ Automatic detection of stablecoins and fiats
- ✅ Adaptive formatting (2 decimals for fiat/stable, 8 for crypto)
- ✅ Type-safe operations (can't add EUR to USD)
- ✅ Complete arithmetic operations support

#### **2. Enhanced `BotPair` Factory**

New generic methods alongside legacy ones for backward compatibility:

```python
# New generic methods
pair = BotPair("ETH/EUR")
base = pair.create_base_asset(10)  # 10 ETH
quote = pair.create_quote_asset(5000)  # 5000 EUR
zero_base = pair.zero_base()  # 0 ETH
zero_quote = pair.zero_quote()  # 0 EUR

# Legacy methods still work (backward compatibility)
usd = pair.create_usd(100)  # Actually creates 100 EUR!
token = pair.create_token(1)  # Creates 1 ETH
```

#### **3. Unified Swap Interface** (`python_trading_objects/quotes/swap.py`)

Abstract away CEX/DEX differences with a unified swap concept:

```python
from python_trading_objects.quotes.swap import SwapRequest, SwapType

# Everything is a swap!
# CEX "buy order" = swap quote→base
swap1 = SwapRequest(
    from_symbol="USDC",
    to_symbol="BTC",
    amount=1000.0,
    swap_type=SwapType.MARKET
)
print(swap1.is_buy())  # True - buying BTC with USDC

# CEX "sell order" = swap base→quote  
swap2 = SwapRequest(
    from_symbol="BTC",
    to_symbol="USDC",
    amount=0.5,
    swap_type=SwapType.LIMIT
)
print(swap2.is_sell())  # True - selling BTC for USDC

# DEX direct swap = swap any→any
swap3 = SwapRequest(
    from_symbol="ETH",
    to_symbol="BTC",
    amount=10.0,
    swap_type=SwapType.MARKET
)
print(swap3.is_swap())  # True - generic crypto-to-crypto swap
```

### **Migration Guide**

#### **For Existing Code (100% Backward Compatible)**

No changes needed! The legacy `USD` class is now an alias to `Asset`:

```python
# Old code still works
from python_trading_objects.quotes.usd import USD
from python_trading_objects.quotes.pair import BotPair

pair = BotPair("BTC/USDT")
usd = pair.create_usd(1000)  # Still works!
```

#### **For New Code (Recommended)**

Use the new generic methods:

```python
# New recommended approach
from python_trading_objects.quotes.asset import Asset
from python_trading_objects.quotes.pair import BotPair

pair = BotPair("BTC/EUR")
quote_asset = pair.create_quote_asset(1000)  # 1000 EUR
base_asset = pair.create_base_asset(0.5)  # 0.5 BTC
```

### **Benefits of the New Architecture**

1. **🌍 Universal Currency Support**
    - Trade any pair: BTC/EUR, ETH/USDC, DOGE/BTC, etc.
    - No hardcoded USD dependency

2. **🔄 CEX/DEX Unified**
    - Same interface for centralized and decentralized exchanges
    - Swap abstraction works for both order books and AMMs

3. **⚡ Zero Breaking Changes**
    - 100% backward compatible
    - Existing code continues to work
    - Gradual migration possible

4. **🔒 Type Safety Enhanced**
    - Can't accidentally mix different assets
    - Operations validated at runtime

5. **🚀 Future Ready**
    - Easy to add bridges, aggregators, cross-chain swaps
    - Prepared for DeFi integrations

### **Testing the New Features**

```python
# Test multi-currency support
from python_trading_objects.quotes.pair import BotPair
from python_trading_objects.quotes.swap import SwapRequest

# EUR pair
pair_eur = BotPair("BTC/EUR")
eur = pair_eur.create_quote_asset(50000)
print(f"EUR amount: {eur}")  # "50000.00 EUR"

# Crypto-to-crypto pair
pair_eth_btc = BotPair("ETH/BTC")
eth = pair_eth_btc.create_base_asset(10)
btc = pair_eth_btc.create_quote_asset(0.5)
print(f"ETH: {eth}, BTC: {btc}")  # "10.00000000 ETH, 0.50000000 BTC"

# Unified swaps
swap = SwapRequest("ETH", "BTC", 5.0)
print(f"Swap type: {swap.direction}")  # SwapDirection.SWAP
```

### **Roadmap**

- [x] Generic `Asset` class implementation
- [x] Enhanced `BotPair` with backward compatibility
- [x] Unified `SwapRequest` interface
- [ ] DEX adapter implementation
- [ ] Cross-chain bridge support
- [ ] Liquidity aggregator interface

### **Breaking Changes**

**None!** This refactoring maintains 100% backward compatibility. All existing code continues to work without modification.