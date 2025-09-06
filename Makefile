.PHONY: help install install-dev test lint format type-check clean build upload upload-test all

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install package in production mode"
	@echo "  install-dev - Install package in development mode with dev dependencies"
	@echo "  test        - Run all tests with pytest"
	@echo "  lint        - Run flake8 linter"
	@echo "  format      - Format code with black"
	@echo "  type-check  - Run mypy type checker"
	@echo "  clean       - Clean build artifacts and cache files"
	@echo "  build       - Build the package"
	@echo "  upload-test - Upload to TestPyPI"
	@echo "  upload      - Upload to PyPI"
	@echo "  all         - Run test, lint, format, and type-check"

# Installation targets
install:
	pip install .

install-dev:
	pip install -e .[dev]

# Testing
test:
	python -m pytest -v

test-coverage:
	python -m pytest --cov=venantvr --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 venantvr/ test/

format:
	black venantvr/ test/

format-check:
	black --check venantvr/ test/

type-check:
	mypy venantvr/

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building and uploading
build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

# Composite targets
all: test lint format-check type-check

dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make all' to run all quality checks."