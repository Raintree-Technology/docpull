# docpull

Pull documentation from the web and convert to clean markdown. Perfect for building AI training data, local documentation, or Claude Code skills.

[![PyPI version](https://badge.fury.io/py/docpull.svg)](https://badge.fury.io/py/docpull)
[![Downloads](https://pepy.tech/badge/docpull)](https://pepy.tech/project/docpull)
[![Tests](https://github.com/raintree-technology/docpull/actions/workflows/test.yml/badge.svg)](https://github.com/raintree-technology/docpull/actions/workflows/test.yml)
[![Security](https://github.com/raintree-technology/docpull/actions/workflows/security.yml/badge.svg)](https://github.com/raintree-technology/docpull/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/raintree-technology/docpull/branch/main/graph/badge.svg)](https://codecov.io/gh/raintree-technology/docpull)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/github/license/raintree-technology/docpull)](https://github.com/raintree-technology/docpull/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub stars](https://img.shields.io/github/stars/raintree-technology/docpull?style=social)](https://github.com/raintree-technology/docpull)

## Why docpull?

- Fast - Parallel fetching with configurable workers
- Simple - One command to pull entire documentation sites
- Clean - Converts HTML to markdown with YAML frontmatter
- Flexible - Easy to add new sources
- Smart - Skip already-fetched files on re-runs
- Ready - Pre-built fetchers for popular sites

### Comparison

| Feature | docpull | wget/curl | scrapy | custom scripts |
|---------|---------|-----------|--------|----------------|
| One-line install | ✅ | ✅ | ✅ | ❌ |
| Markdown output | ✅ | ❌ | ❌ | Maybe |
| YAML frontmatter | ✅ | ❌ | ❌ | Maybe |
| Parallel fetching | ✅ | ❌ | ✅ | Maybe |
| Pre-built sources | ✅ | ❌ | ❌ | ❌ |
| Rate limiting | ✅ | ❌ | ✅ | Maybe |
| Skip existing files | ✅ | ❌ | ❌ | Maybe |
| Python API | ✅ | ❌ | ✅ | N/A |

## Quick Start

```bash
# Install
pip install docpull

# Pull documentation
docpull --source stripe --output-dir ./docs
docpull --source nextjs --output-dir ./docs
```

## Supported Sources

| Source | Description | Content |
|--------|-------------|---------|
| stripe | Stripe API & Guides | Payment processing, billing, webhooks |
| nextjs | Next.js Docs | App Router, Server Components, API routes |
| plaid | Plaid API | Banking data, transactions, accounts |
| bun | Bun Runtime | Runtime, bundler, package manager |
| d3 | D3.js | Data visualization library |
| tailwind | Tailwind CSS | Utility-first CSS framework |
| react | React | JavaScript UI library |

## Installation

```bash
# From PyPI
pip install docpull

# With YAML config support
pip install docpull[yaml]

# From source
git clone https://github.com/raintree-technology/docpull.git
cd docpull
pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage
docpull --source stripe --output-dir ./docs

# With custom rate limit (be respectful!)
docpull --source nextjs --output-dir ./docs --rate-limit 1.0

# Preview what would be fetched (dry run)
docpull --source react --dry-run

# Verbose output for debugging
docpull --source plaid --output-dir ./docs --verbose

# Using config file
docpull --config config.yaml
```

### Python API

```python
# Import docpull
from docpull import StripeFetcher

# Pull Stripe docs
fetcher = StripeFetcher(
    output_dir="./docs",
    rate_limit=0.5,
    skip_existing=True
)
fetcher.fetch()
```

### Configuration File

Generate a config file:
```bash
docpull --generate-config config.yaml
```

Or create `config.yaml` manually:

```yaml
# Output directory (source names will be appended automatically)
output_dir: ./docs

# Rate limiting (seconds between requests)
rate_limit: 0.5

# Skip already-downloaded files
skip_existing: true

# Logging level
log_level: INFO

# Sources to fetch
sources:
  - stripe
  - nextjs
  - react
```

Run with:
```bash
docpull --config config.yaml
```

## Output Format

docpull saves each page as clean markdown with YAML frontmatter metadata:

```markdown
---
title: Getting Started with Stripe
url: https://stripe.com/docs/getting-started
fetched_at: 2025-11-06T12:00:00
---

# Getting Started with Stripe

Your documentation content here...
```

docpull organizes files by URL structure, making them easy to navigate:

```
docs/
├── stripe/
│   ├── api/
│   │   ├── charges.md
│   │   └── customers.md
│   ├── billing/
│   │   └── subscriptions.md
│   └── payments/
│       └── payment-intents.md
└── nextjs/
    ├── app/
    │   └── routing.md
    └── pages/
        └── api-routes.md
```

## Use Cases

### Building Claude Code Skills

```bash
# Pull documentation
docpull --source stripe --output ./docs/stripe

# Use with claude-starter template
# Your skills can now reference local docs!
```

### Local Documentation

```bash
# Keep offline copies of important docs
docpull --source nextjs --output ~/docs/nextjs
docpull --source react --output ~/docs/react
```

### AI Training Data

```bash
# Build training datasets
docpull --source stripe --output ./training-data/stripe
docpull --source plaid --output ./training-data/plaid
```

### Documentation Analysis

```python
from docpull.fetchers import StripeFetcher
import os

# Fetch docs
fetcher = StripeFetcher(output_dir="./analysis")
fetcher.fetch()

# Analyze content
for root, dirs, files in os.walk("./analysis"):
    for file in files:
        if file.endswith('.md'):
            # Your analysis here
            pass
```

## Creating Custom Fetchers

### Basic Fetcher

```python
from docpull.fetchers.base import BaseFetcher

class MyDocsFetcher(BaseFetcher):
    def __init__(self, output_dir="./docs/mydocs", **kwargs):
        super().__init__(output_dir=output_dir, **kwargs)
        self.base_url = "https://docs.example.com"

    def fetch(self):
        # Get URLs from sitemap
        urls = self.get_urls_from_sitemap(f"{self.base_url}/sitemap.xml")

        # Fetch each page
        for url in urls:
            self.fetch_and_save(url)
```

### Parallel Fetcher (Faster)

```python
from docpull.fetchers.parallel_base import ParallelBaseFetcher

class MyFastFetcher(ParallelBaseFetcher):
    def __init__(self, output_dir="./docs/mydocs", max_workers=20, **kwargs):
        super().__init__(
            output_dir=output_dir,
            max_workers=max_workers,
            **kwargs
        )
        self.base_url = "https://docs.example.com"

    def fetch(self):
        urls = self.get_urls_from_sitemap(f"{self.base_url}/sitemap.xml")
        self.fetch_all_parallel(urls)
```

## Advanced Options

### Rate Limiting

```python
fetcher = StripeFetcher(
    output_dir="./docs/stripe",
    delay=1.0  # Wait 1 second between requests
)
```

### Skip Existing Files

```python
fetcher = StripeFetcher(
    output_dir="./docs/stripe",
    skip_existing=True  # Don't re-fetch existing files
)
```

### Custom Headers

```python
fetcher = StripeFetcher(
    output_dir="./docs/stripe",
    headers={
        "User-Agent": "MyBot/1.0 (contact@example.com)",
        "Accept-Language": "en-US"
    }
)
```

### Parallel Processing

```python
from docpull.fetchers import NextJSFetcher

fetcher = NextJSFetcher(
    output_dir="./docs/nextjs",
    max_workers=20  # Use 20 concurrent workers
)
fetcher.fetch()
```

## Development

### Setup

```bash
git clone https://github.com/raintree-technology/docpull.git
cd docpull
pip install -e ".[dev]"
```

### Tests

```bash
pytest
```

### Code Quality

```bash
# Format
black docpull/

# Lint
ruff check docpull/

# Type check
mypy docpull/
```

## Pair With

[claude-starter](https://github.com/raintree-technology/claude-starter) - Complete Claude Code template with skills, agents, hooks, and commands. Use docpull to fetch docs, then reference them in your Claude skills.

## Examples

See the `docs/examples/` directory for more examples:

- [basic_usage.py](docs/examples/basic_usage.py) - Simple examples and CLI wrapper
- [advanced_usage.py](docs/examples/advanced_usage.py) - Config files, error handling, and advanced patterns

Example config files:
- [config.example.yaml](docs/configs/config.example.yaml) - YAML configuration template
- [config.example.json](docs/configs/config.example.json) - JSON configuration template

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Contributors

1. Fork and clone the repository
2. Create a virtual environment and install dev dependencies
3. Make your changes and add tests
4. Run tests and linters
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on:
- Adding new documentation sources
- Writing tests
- Code style guidelines
- Development workflow

## Maintenance

This package is fully automated with minimal maintenance required:
- Automatic releases to PyPI when you push a tag
- Automatic dependency updates (Dependabot)
- Automatic issue labeling and stale issue closing
- Multi-platform CI/CD testing on every commit

See [MAINTENANCE.md](MAINTENANCE.md) for details on the automated workflows.

To release: `bump2version patch && git push origin --tags`

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## Support

Need help? See our [Support Guide](SUPPORT.md) for:
- Documentation and resources
- How to ask questions
- Reporting bugs and requesting features
- Community support options

## Community

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Guidelines for participation
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [SECURITY.md](SECURITY.md) - Security policy and reporting
- [SUPPORT.md](SUPPORT.md) - Getting help

## Featured In

Want to see docpull featured in awesome lists? Submit a PR to:
- [Awesome Claude](https://github.com/anthropics/awesome-claude-projects) - Claude AI tools and projects
- [Awesome Python](https://github.com/vinta/awesome-python) - Python frameworks and libraries
- [Awesome Web Scraping](https://github.com/lorien/awesome-web-scraping) - Web scraping tools
- [Awesome AI Tools](https://github.com/mahseema/awesome-ai-tools) - AI and machine learning tools

If you've featured docpull in a blog post, video, or list, [open an issue](https://github.com/raintree-technology/docpull/issues) and we'll add it here!

## License

MIT License - See [LICENSE](LICENSE) file

## Links

- GitHub: [raintree-technology/docpull](https://github.com/raintree-technology/docpull)
- PyPI: [docpull](https://pypi.org/project/docpull/)
- Issues: [Report a bug](https://github.com/raintree-technology/docpull/issues)
- Discussions: [GitHub Discussions](https://github.com/raintree-technology/docpull/discussions)
- Changelog: [Release Notes](https://github.com/raintree-technology/docpull/blob/main/CHANGELOG.md)
