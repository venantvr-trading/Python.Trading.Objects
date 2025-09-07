.PHONY: help install install-dev test lint format type-check clean build upload upload-test all pre-commit test-coverage

# Project name without dots/dashes for consistency
PROJECT_NAME = Python_Trading_Objects
PACKAGE_NAME = venantvr

# Default target
help:
	@echo "Available commands for $(PROJECT_NAME):"
	@echo "  install         - Install package in production mode"
	@echo "  install-dev     - Install package in development mode with dev dependencies"
	@echo "  test            - Run all tests with pytest"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  lint            - Run flake8 linter"
	@echo "  format          - Format code with black"
	@echo "  format-check    - Check code formatting without changes"
	@echo "  type-check      - Run mypy type checker"
	@echo "  pre-commit      - Install and run pre-commit hooks"
	@echo "  clean           - Clean build artifacts and cache files"
	@echo "  build           - Build the package"
	@echo "  upload-test     - Upload to TestPyPI"
	@echo "  upload          - Upload to PyPI"
	@echo "  all             - Run test, lint, format-check, and type-check"

# Installation targets
install:
	pip install .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

# Testing
test:
	python -m pytest -v

test-coverage:
	python -m pytest --cov=$(PACKAGE_NAME) --cov-report=html --cov-report=term --cov-report=term-missing

# Code quality
lint:
	flake8 $(PACKAGE_NAME)/ test/

format:
	black $(PACKAGE_NAME)/ test/
	isort $(PACKAGE_NAME)/ test/ --profile black

format-check:
	black --check $(PACKAGE_NAME)/ test/
	isort --check-only $(PACKAGE_NAME)/ test/ --profile black

type-check:
	mypy $(PACKAGE_NAME)/

# Pre-commit
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(PROJECT_NAME).egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage*" -delete

# Building and uploading
build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

# Composite targets
all: test lint format-check type-check

# Development setup
dev-setup: install-dev
	@echo "======================================"
	@echo "Development environment setup complete for $(PROJECT_NAME)!"
	@echo "Pre-commit hooks have been installed."
	@echo "Run 'make all' to run all quality checks."
	@echo "======================================"

# Quick validation before push
validate: format test lint type-check
	@echo "======================================"
	@echo "Validation complete for $(PROJECT_NAME)!"
	@echo "Ready to commit and push."
	@echo "======================================="