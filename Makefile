.PHONY: help install install-dev clean test test-cov format lint type-check security check all build example

help:
	@echo "docpull - Pull documentation from the web"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install package"
	@echo "  install-dev   - Install package with dev dependencies"
	@echo "  clean         - Remove build artifacts and cache files"
	@echo "  test          - Run tests"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  format        - Format code with black"
	@echo "  lint          - Lint code with ruff"
	@echo "  type-check    - Type check with mypy"
	@echo "  security      - Run security scans (bandit, pip-audit)"
	@echo "  check         - Run all checks (format, lint, type-check, security)"
	@echo "  all           - Run all checks and tests"
	@echo "  build         - Build distribution packages"
	@echo "  example       - Run example scripts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,yaml]"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

test:
	pytest tests/

test-cov:
	pytest --cov=docpull --cov-report=html --cov-report=term

format:
	black docpull/ tests/ docs/examples/

lint:
	ruff check docpull/ tests/ docs/examples/

type-check:
	mypy docpull/

security:
	@echo "Running security scans..."
	bandit -r docpull/
	pip-audit

check: format lint type-check security
	@echo "All checks passed!"

all: check test
	@echo "All checks and tests passed!"

build:
	python -m build

example:
	@echo "Running basic example:"
	python docs/examples/basic_usage.py --help
