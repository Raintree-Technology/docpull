# docpull

Pull documentation from the web and convert to clean markdown. Perfect for building AI training data, local docs, or Claude Code skills.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/docpull.svg)](https://badge.fury.io/py/docpull)
[![Downloads](https://pepy.tech/badge/docpull)](https://pepy.tech/project/docpull)
[![Tests](https://github.com/raintree-technology/docpull/actions/workflows/test.yml/badge.svg)](https://github.com/raintree-technology/docpull/actions/workflows/test.yml)
[![Security](https://github.com/raintree-technology/docpull/actions/workflows/security.yml/badge.svg)](https://github.com/raintree-technology/docpull/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/raintree-technology/docpull/branch/main/graph/badge.svg)](https://codecov.io/gh/raintree-technology/docpull)
[![License: MIT](https://img.shields.io/github/license/raintree-technology/docpull)](https://github.com/raintree-technology/docpull/blob/main/LICENSE)

## Features

- **Fast** - Parallel fetching with configurable workers
- **Simple** - One command to pull entire documentation sites
- **Clean** - Converts HTML to markdown with YAML frontmatter
- **Smart** - Skips already-fetched files on re-runs
- **Ready** - Pre-built fetchers for popular documentation sites

## Quick Start

```bash
# Install
pip install docpull

# Pull documentation
docpull --source stripe --output-dir ./docs
docpull --source nextjs --output-dir ./docs
```

## Supported Sources

| Source | Description |
|--------|-------------|
| `stripe` | Stripe API & payment documentation |
| `nextjs` | Next.js framework documentation |
| `plaid` | Plaid banking API documentation |
| `bun` | Bun runtime documentation |
| `d3` | D3.js data visualization library |
| `tailwind` | Tailwind CSS framework |
| `react` | React JavaScript library |

## Installation

```bash
# Basic installation
pip install docpull

# With YAML config support
pip install docpull[yaml]
```

## Usage

### Command Line

```bash
# Basic usage
docpull --source stripe --output-dir ./docs

# Multiple sources with config file
docpull --config config.yaml

# Custom rate limit (seconds between requests)
docpull --source nextjs --rate-limit 1.0

# Preview without downloading
docpull --source react --dry-run
```

### Python API

```python
from docpull import StripeFetcher

fetcher = StripeFetcher(
    output_dir="./docs",
    rate_limit=0.5,
    skip_existing=True
)
fetcher.fetch()
```

### Configuration File

Create `config.yaml`:

```yaml
output_dir: ./docs
rate_limit: 0.5
skip_existing: true
log_level: INFO

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

Each page is saved as markdown with YAML frontmatter:

```markdown
---
url: https://stripe.com/docs/payments
fetched: 2025-11-07
---

# Payment Intents

Your documentation content here...
```

Files are organized by URL structure:

```
docs/
├── stripe/
│   ├── api/
│   │   ├── charges.md
│   │   └── customers.md
│   └── payments/
│       └── payment-intents.md
└── nextjs/
    ├── app/
    │   └── routing.md
    └── pages/
        └── api-routes.md
```

## Creating Custom Fetchers

```python
from docpull.fetchers.base import BaseFetcher

class MyDocsFetcher(BaseFetcher):
    def __init__(self, output_dir="./docs/mydocs", **kwargs):
        super().__init__(output_dir=output_dir, **kwargs)
        self.base_url = "https://docs.example.com"

    def fetch(self):
        urls = self.fetch_sitemap(f"{self.base_url}/sitemap.xml")
        for url in urls:
            output_path = self.url_to_filepath(url)
            self.process_url(url, output_path)
```

For parallel fetching, extend `ParallelBaseFetcher` instead. See [examples](docs/examples/) for more.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding new documentation sources
- Reporting bugs and requesting features
- Development setup and workflow

## Documentation

- [Changelog](CHANGELOG.md) - Version history
- [Security Policy](SECURITY.md) - Reporting vulnerabilities
- [Support Guide](SUPPORT.md) - Getting help
- [Maintenance](MAINTENANCE.md) - Automated workflows

## License

MIT License - see [LICENSE](LICENSE) file for details

## Links

- **PyPI**: [pypi.org/project/docpull](https://pypi.org/project/docpull/)
- **GitHub**: [github.com/raintree-technology/docpull](https://github.com/raintree-technology/docpull)
- **Issues**: [Report a bug](https://github.com/raintree-technology/docpull/issues)
- **Pair with**: [claude-starter](https://github.com/raintree-technology/claude-starter) - Claude Code template for building AI skills with docpull
