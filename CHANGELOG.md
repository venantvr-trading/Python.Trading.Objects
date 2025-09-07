# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Professional library structure with comprehensive documentation
- Makefile for common development tasks
- MIT license
- Enhanced .gitignore for Python projects
- Development dependencies in pyproject.toml
- Code quality tools configuration (black, flake8, mypy)

### Changed

- Updated README.md to English with comprehensive documentation
- Enhanced pyproject.toml with complete metadata and tool configurations
- Fixed failing test regex pattern in test_quote.py

### Fixed

- Test suite now passes all 73 tests

## [0.1.0] - 2024-08-11

### Added

- Initial release of Python.Trading.Objects
- Core classes: Quote, Token, USD, Price, BotPair
- Factory pattern for type-safe object creation
- Arithmetic operations with operator overloading
- JSON serialization support
- Precision control for different asset types
- Comprehensive test suite with 73 test cases
- Type assertions and error handling
- Support for comparison operations

### Features

- **BotPair Factory**: Create Token, Price, and USD objects for specific trading pairs
- **Type Safety**: Prevents mixing incompatible currency types
- **Precision Control**: Configurable decimal precision for tokens and USD amounts
- **Arithmetic Operations**: Full support for +, -, *, / operations with proper type checking
- **Zero Values**: Factory methods for creating zero-value objects
- **Serialization**: Built-in to_dict() and to_json() methods for all objects

### Technical Details

- Pure Python implementation with no external dependencies
- Python 3.8+ compatibility
- Abstract base class design with concrete implementations
- Comprehensive error handling with descriptive messages
- Factory pattern ensuring consistent object creation