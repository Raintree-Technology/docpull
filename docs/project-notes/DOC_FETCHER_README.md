# Doc Fetcher

A flexible, extensible documentation fetching and conversion tool that downloads documentation from various sources and converts it to clean markdown.

## Features

- **Modular Architecture**: Easy to add new documentation sources
- **Sitemap Support**: Automatically discovers URLs from XML sitemaps
- **HTML to Markdown**: Clean conversion with frontmatter
- **Rate Limiting**: Respectful crawling with configurable delays
- **Skip Existing**: Efficient re-runs by skipping already fetched files
- **Configurable**: YAML/JSON config files or CLI arguments
- **Organized Output**: Automatic categorization by path structure
- **Comprehensive Logging**: Detailed progress and error tracking

## Installation

### From Source

```bash
# Clone or navigate to the repository
cd /Users/zach/Documents/cc-skills

# Install in development mode
pip install -e .

# Or install with YAML support
pip install -e ".[yaml]"
```

### Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage

Fetch all documentation with default settings:

```bash
# Using the CLI
doc-fetcher

# Or run as Python module
python -m doc_fetcher
```

### 2. Fetch Specific Sources

```bash
# Fetch only Stripe docs
doc-fetcher --sources stripe

# Fetch only Plaid docs
doc-fetcher --sources plaid

# Fetch both (explicit)
doc-fetcher --sources stripe plaid
```

### 3. Custom Output Directory

```bash
doc-fetcher --output-dir ./my-docs
```

### 4. Using a Config File

```bash
# Generate a sample config
doc-fetcher --generate-config config.yaml

# Edit the config file, then use it
doc-fetcher --config config.yaml
```

## Configuration

### Config File

Create a `config.yaml`:

```yaml
# Directory to save fetched documentation
output_dir: ./docs

# Seconds to wait between requests
rate_limit: 0.5

# Skip files that already exist
skip_existing: true

# Logging level
log_level: INFO

# Optional: Write logs to a file
log_file: ./doc_fetcher.log

# Sources to fetch
sources:
  - stripe
  - plaid
```

Or use JSON (`config.json`):

```json
{
  "output_dir": "./docs",
  "rate_limit": 0.5,
  "skip_existing": true,
  "log_level": "INFO",
  "sources": ["stripe", "plaid"]
}
```

### CLI Options

```
usage: doc-fetcher [-h] [--config CONFIG] [--output-dir OUTPUT_DIR]
                   [--sources {stripe,plaid,all} [{stripe,plaid,all} ...]]
                   [--rate-limit RATE_LIMIT] [--no-skip-existing]
                   [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                   [--log-file LOG_FILE] [--generate-config PATH]
                   [--version]

Options:
  -h, --help            Show help message and exit
  -c, --config CONFIG   Path to config file (YAML or JSON)
  -o, --output-dir DIR  Directory to save documentation
  -s, --sources SOURCES Sources to fetch (stripe, plaid, or all)
  -r, --rate-limit SEC  Seconds to wait between requests
  --no-skip-existing    Re-fetch files that already exist
  -l, --log-level LEVEL Logging level
  --log-file PATH       Path to log file
  --generate-config PATH Generate a sample config file
  --version             Show version
```

## Usage Examples

### Example 1: Development Setup

Fast fetching with detailed logging:

```bash
doc-fetcher \
  --output-dir ./docs \
  --sources stripe plaid \
  --rate-limit 0.3 \
  --log-level DEBUG \
  --log-file debug.log
```

### Example 2: Production Setup

Respectful crawling with config file:

```bash
# Create config
cat > config.yaml << EOF
output_dir: /var/www/docs
rate_limit: 1.0
skip_existing: true
log_level: INFO
log_file: /var/log/doc-fetcher.log
sources:
  - stripe
  - plaid
EOF

# Run fetcher
doc-fetcher --config config.yaml
```

### Example 3: Re-fetch Everything

```bash
doc-fetcher --no-skip-existing --sources all
```

## Output Structure

Documentation is organized by source and path:

```
docs/
├── stripe/
│   ├── api/
│   │   ├── authentication/
│   │   │   └── api-authentication.md
│   │   ├── errors/
│   │   │   └── api-errors.md
│   │   └── ...
│   ├── payments/
│   │   └── ...
│   └── ...
└── plaid/
    ├── api-reference/
    │   └── ...
    └── guides/
        └── ...
```

Each markdown file includes frontmatter:

```markdown
---
url: https://docs.stripe.com/api/authentication
fetched: 2025-11-06
---

# Authentication

Your actual documentation content here...
```

## Adding New Sources

To add a new documentation source, create a new fetcher class:

```python
# doc_fetcher/fetchers/my_source.py
from pathlib import Path
from typing import Optional
import logging

from .base import BaseFetcher


class MySourceFetcher(BaseFetcher):
    """Fetcher for MySource documentation."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        super().__init__(output_dir, rate_limit, skip_existing, logger)
        self.sitemap_url = "https://docs.mysource.com/sitemap.xml"
        self.base_url = "https://docs.mysource.com/"

    def fetch(self) -> None:
        """Fetch all MySource documentation."""
        self.logger.info("Fetching MySource documentation...")

        # Fetch sitemap
        urls = self.fetch_sitemap(self.sitemap_url)

        # Filter URLs if needed
        urls = self.filter_urls(urls, [self.base_url])

        # Process each URL
        for url in urls:
            # Determine output path
            from ..utils.file_utils import clean_filename
            filename = clean_filename(url, self.base_url)
            filepath = self.output_dir / "mysource" / filename

            # Process the URL
            self.process_url(url, filepath)

        self.print_stats()
```

Then register it in `cli.py`:

```python
from .fetchers import MySourceFetcher

# In run_fetchers()
fetcher_map = {
    "stripe": StripeFetcher,
    "plaid": PlaidFetcher,
    "mysource": MySourceFetcher,  # Add your fetcher
}
```

## API Usage

You can also use doc_fetcher as a library:

```python
from pathlib import Path
from doc_fetcher import StripeFetcher, PlaidFetcher
from doc_fetcher.utils.logging_config import setup_logging

# Setup logging
logger = setup_logging(level="INFO")

# Fetch Stripe docs
stripe_fetcher = StripeFetcher(
    output_dir=Path("./docs"),
    rate_limit=0.5,
    skip_existing=True,
    logger=logger
)
stripe_fetcher.fetch()

# Fetch Plaid docs
plaid_fetcher = PlaidFetcher(
    output_dir=Path("./docs"),
    rate_limit=0.5,
    skip_existing=True,
    logger=logger
)
plaid_fetcher.fetch()

# Check statistics
print(f"Stripe: {stripe_fetcher.stats}")
print(f"Plaid: {plaid_fetcher.stats}")
```

## Architecture

### Package Structure

```
doc_fetcher/
├── __init__.py          # Package exports
├── __main__.py          # Entry point for python -m
├── cli.py               # Command-line interface
├── config.py            # Configuration management
├── fetchers/
│   ├── __init__.py
│   ├── base.py         # BaseFetcher abstract class
│   ├── stripe.py       # Stripe-specific fetcher
│   └── plaid.py        # Plaid-specific fetcher
└── utils/
    ├── __init__.py
    ├── file_utils.py    # File operations
    └── logging_config.py # Logging setup
```

### Base Fetcher

The `BaseFetcher` class provides:

- Sitemap fetching and parsing (including nested sitemaps)
- URL filtering by patterns
- URL categorization
- HTML to markdown conversion
- Content extraction from main content areas
- File saving with directory creation
- Rate limiting
- Statistics tracking
- Logging

### Extensibility

New sources only need to implement:

1. Set `sitemap_url` and `base_url`
2. Implement `fetch()` method
3. Optionally override content extraction for site-specific needs

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when implemented)
pytest
```

### Code Quality

```bash
# Format code
black doc_fetcher/

# Lint
ruff check doc_fetcher/

# Type check
mypy doc_fetcher/
```

## Troubleshooting

### Rate Limiting Issues

If you're being rate-limited, increase the delay:

```bash
doc-fetcher --rate-limit 2.0
```

### Missing Dependencies

```bash
# Install all dependencies including optional ones
pip install -r requirements.txt
```

### Permission Errors

Ensure the output directory is writable:

```bash
mkdir -p ./docs
chmod 755 ./docs
```

## License

MIT License

## Contributing

Contributions welcome! Areas for improvement:

- Additional documentation sources
- Better content extraction for specific sites
- Improved categorization logic
- Progress bars for long-running fetches
- Parallel fetching with worker pools
- Incremental updates (only fetch changed pages)

## Credits

Built using:
- [requests](https://requests.readthedocs.io/) - HTTP library
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [html2text](https://github.com/Alir3z4/html2text/) - HTML to Markdown conversion
