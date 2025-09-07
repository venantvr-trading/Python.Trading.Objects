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
from venantvr.quotes import BotPair

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