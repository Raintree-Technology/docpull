# docpull

Pull documentation from the web and convert to clean markdown. Perfect for building AI training data, local documentation, or Claude Code skills.

[![PyPI version](https://badge.fury.io/py/docpull.svg)](https://badge.fury.io/py/docpull)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why docpull?

- 🚀 **Fast** - Parallel fetching with configurable workers
- 🎯 **Simple** - One command to pull entire documentation sites
- 🧹 **Clean** - Converts HTML to markdown with YAML frontmatter
- 🔧 **Flexible** - Easy to add new sources
- 💾 **Smart** - Skip already-fetched files on re-runs
- 📦 **Ready** - Pre-built fetchers for popular sites

## Quick Start

```bash
# Install
pip install docpull

# Pull documentation
docpull --source stripe --output ./docs/stripe
docpull --source nextjs --output ./docs/nextjs

# That's it!
```

## Supported Sources

| Source | Description | Content |
|--------|-------------|---------|
| **stripe** | Stripe API & Guides | Payment processing, billing, webhooks |
| **nextjs** | Next.js Docs | App Router, Server Components, API routes |
| **plaid** | Plaid API | Banking data, transactions, accounts |
| **bun** | Bun Runtime | Runtime, bundler, package manager |
| **d3** | D3.js | Data visualization library |
| **supabase** | Supabase | Database, auth, storage, edge functions |
| **tailwind** | Tailwind CSS | Utility-first CSS framework |
| **react** | React | JavaScript UI library |

## Installation

```bash
# From PyPI
pip install docpull

# With YAML config support
pip install docpull[yaml]

# From source
git clone https://github.com/zachshallbetter/docpull.git
cd docpull
pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage
docpull --source stripe --output ./docs/stripe

# With custom delay (be respectful!)
docpull --source nextjs --output ./docs/nextjs --delay 1.0

# Using config file
docpull --config config.yaml
```

### Python API

```python
from doc_fetcher.fetchers import StripeFetcher

# Pull Stripe docs
fetcher = StripeFetcher(
    output_dir="./docs/stripe",
    delay=0.5,
    skip_existing=True
)
fetcher.fetch()
```

### Configuration File

Create `docpull.yaml`:

```yaml
sources:
  stripe:
    output_dir: ./docs/stripe
    delay: 0.5
    skip_existing: true

  nextjs:
    output_dir: ./docs/nextjs
    delay: 0.3
    skip_existing: true
```

Run with:
```bash
docpull --config docpull.yaml
```

## Output Format

Each page is saved as markdown with YAML frontmatter:

```markdown
---
title: Getting Started with Stripe
url: https://stripe.com/docs/getting-started
fetched_at: 2025-11-06T12:00:00
---

# Getting Started with Stripe

Your documentation content here...
```

Files are organized by URL structure:

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
from doc_fetcher.fetchers import StripeFetcher
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
from doc_fetcher.fetchers.base import BaseFetcher

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
from doc_fetcher.fetchers.parallel_base import ParallelBaseFetcher

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
from doc_fetcher.fetchers import NextJSFetcher

fetcher = NextJSFetcher(
    output_dir="./docs/nextjs",
    max_workers=20  # Use 20 concurrent workers
)
fetcher.fetch()
```

## Development

### Setup

```bash
git clone https://github.com/zachshallbetter/docpull.git
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
black doc_fetcher/

# Lint
ruff check doc_fetcher/

# Type check
mypy doc_fetcher/
```

## Pair With

**[claude-starter](https://github.com/zachshallbetter/claude-starter)** - Complete Claude Code template with skills, agents, hooks, and commands. Use docpull to fetch docs, then reference them in your Claude skills!

## Contributing

Contributions welcome!

### Ideas

- New documentation sources
- Better HTML to Markdown conversion
- Performance improvements
- More comprehensive tests

### Adding a Source

1. Create `doc_fetcher/fetchers/your_source.py`
2. Extend `BaseFetcher` or `ParallelBaseFetcher`
3. Implement `fetch()` method
4. Register in `doc_fetcher/fetchers/__init__.py`
5. Add tests
6. Submit PR!

## License

MIT License - See LICENSE file

## Links

- **GitHub**: [zachshallbetter/docpull](https://github.com/zachshallbetter/docpull)
- **Issues**: [Report a bug](https://github.com/zachshallbetter/docpull/issues)
- **PyPI**: [docpull](https://pypi.org/project/docpull/)

---

**Pull docs. Build better.**
