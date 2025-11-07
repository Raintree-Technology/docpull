.PHONY: help install install-dev clean test format lint type-check docs run example config

help:
	@echo "doc_fetcher - Documentation Fetcher"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install package"
	@echo "  install-dev   - Install package with dev dependencies"
	@echo "  clean         - Remove build artifacts and cache files"
	@echo "  test          - Run tests (when implemented)"
	@echo "  format        - Format code with black"
	@echo "  lint          - Lint code with ruff"
	@echo "  type-check    - Type check with mypy"
	@echo "  run           - Run doc-fetcher"
	@echo "  example       - Run example usage script"
	@echo "  config        - Generate sample config file"
	@echo "  docs          - Generate documentation (when implemented)"

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
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

test:
	@echo "Tests not yet implemented"
	@echo "Run: pytest tests/"

format:
	black doc_fetcher/ example_usage.py

lint:
	ruff check doc_fetcher/ example_usage.py

type-check:
	mypy doc_fetcher/

run:
	doc-fetcher

example:
	python example_usage.py

config:
	doc-fetcher --generate-config config.yaml
	@echo ""
	@echo "Sample config generated: config.yaml"
	@echo "Edit it and run: doc-fetcher --config config.yaml"

docs:
	@echo "See DOC_FETCHER_README.md for documentation"
