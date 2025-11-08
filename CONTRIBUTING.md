# Contributing to docpull

This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Adding New Fetchers](#adding-new-fetchers)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Security](#security)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Be respectful, considerate, and professional in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/docpull.git
   cd docpull
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/raintree-technology/docpull.git
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies (including dev dependencies):
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

3. Verify the installation:
   ```bash
   docpull --version
   ```

## Adding New Fetchers

Adding support for a new documentation source is straightforward. Follow these steps:

### 1. Create a New Fetcher Class

Create a new file in `docpull/fetchers/` (e.g., `your_source.py`):

```python
from .base import BaseFetcher

class YourSourceFetcher(BaseFetcher):
    """Fetcher for YourSource documentation."""

    def __init__(self, output_dir, rate_limit=0.5, skip_existing=True, logger=None):
        super().__init__(output_dir, rate_limit, skip_existing, logger)
        self.base_url = "https://docs.yoursource.com"
        self.sitemap_url = "https://docs.yoursource.com/sitemap.xml"

    def get_all_urls(self):
        """Extract all documentation URLs."""
        # Use self.extract_urls_from_sitemap() or implement custom logic
        return self.extract_urls_from_sitemap(self.sitemap_url)

    def get_output_path(self, url):
        """Determine output file path for a URL."""
        # Customize the directory structure
        path = url.replace(self.base_url, "").strip("/")
        return self.output_dir / "yoursource" / f"{path}.md"
```

### 2. Export the New Fetcher

Add your fetcher to `docpull/fetchers/__init__.py`:

```python
from .your_source import YourSourceFetcher

__all__ = [
    "BaseFetcher",
    "StripeFetcher",
    # ... other fetchers ...
    "YourSourceFetcher",
]
```

### 3. Update the CLI

Add your fetcher to the CLI in `docpull/cli.py`:

```python
FETCHER_MAP = {
    "stripe": StripeFetcher,
    # ... other fetchers ...
    "yoursource": YourSourceFetcher,
}
```

### 4. Add Tests

Create tests in `tests/test_fetchers.py`:

```python
class TestYourSourceFetcher:
    """Test YourSource-specific functionality."""

    def test_yoursource_fetcher_creation(self, tmp_path):
        """Test YourSource fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = YourSourceFetcher(
            output_dir=tmp_path,
            rate_limit=0.5,
            skip_existing=True,
            logger=logger
        )
        assert fetcher is not None
```

### 5. Update Documentation

- Add your fetcher to README.md
- Update examples if needed
- Add entry to CHANGELOG.md

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=docpull --cov-report=html

# Run specific test file
pytest tests/test_fetchers.py

# Run specific test
pytest tests/test_fetchers.py::TestBaseFetcher::test_fetcher_initialization
```

### Test Guidelines

- Write tests for all new functionality
- Aim for high test coverage (>80%)
- Use fixtures from `tests/conftest.py`
- Mark network-dependent tests with `@pytest.mark.integration`
- Use `tmp_path` fixture for file system tests

## Code Style

This project follows Python best practices:

### Formatting and Linting

```bash
# Format code with Black
black docpull tests

# Lint with Ruff
ruff check docpull tests

# Type check with mypy
mypy docpull

# Security scan with Bandit
bandit -r docpull
```

### Style Guidelines

- Follow PEP 8
- Use type hints for function signatures
- Write descriptive docstrings (Google style)
- Keep functions focused and single-purpose
- Maximum line length: 88 characters (Black default)

### Example Function

```python
def fetch_url(self, url: str) -> str:
    """
    Fetch and return content from a URL.

    Args:
        url: The URL to fetch

    Returns:
        The fetched content as a string

    Raises:
        requests.RequestException: If the request fails
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text
```

## Pull Request Process

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Write or update tests** for your changes

4. **Run the test suite** and ensure all tests pass:
   ```bash
   pytest
   black docpull tests
   ruff check docpull tests
   mypy docpull
   ```

5. **Commit your changes** with a descriptive message:
   ```bash
   git commit -m "Add: Support for YourSource documentation fetcher"
   ```

   Use conventional commit prefixes:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements to existing features
   - `Docs:` for documentation changes
   - `Test:` for test additions or changes
   - `Refactor:` for code refactoring

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub:
   - Provide a clear title and description
   - Reference any related issues
   - Describe what was changed and why
   - Include screenshots if relevant

8. **Respond to feedback** and make requested changes

9. **Wait for approval** from maintainers

## Security

### Reporting Security Issues

Do not open public issues for security vulnerabilities. Email security concerns to support@raintree.technology and review SECURITY.md for the full security policy.

### Security Best Practices

When contributing:
- No hardcoded credentials or secrets
- Proper input validation and sanitization
- Safe file path handling
- HTTPS enforcement for external requests
- Certificate verification enabled
- Request timeouts implemented
- File size limits respected

## Questions

Check existing issues and pull requests, review the documentation, or open a discussion on GitHub.
