# Doc Fetcher - Quick Start

Get started with doc_fetcher in 60 seconds.

## Installation

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Install the package
pip install -e .

# Optional: Install YAML support
pip install pyyaml
```

## Basic Usage

### 1. Fetch All Documentation

```bash
doc-fetcher
```

This fetches both Stripe and Plaid documentation to `./docs/`.

### 2. Fetch Specific Source

```bash
# Stripe only
doc-fetcher --sources stripe

# Plaid only
doc-fetcher --sources plaid
```

### 3. Custom Output Directory

```bash
doc-fetcher --output-dir /path/to/my-docs
```

### 4. Use a Config File

```bash
# Generate config
doc-fetcher --generate-config config.json

# Edit the config file
vim config.json

# Use it
doc-fetcher --config config.json
```

## Configuration Options

| Option | CLI Flag | Config Key | Default | Description |
|--------|----------|------------|---------|-------------|
| Output Directory | `--output-dir` | `output_dir` | `./docs` | Where to save docs |
| Sources | `--sources` | `sources` | `all` | Which sources to fetch |
| Rate Limit | `--rate-limit` | `rate_limit` | `0.5` | Seconds between requests |
| Skip Existing | `--no-skip-existing` | `skip_existing` | `true` | Skip already-fetched files |
| Log Level | `--log-level` | `log_level` | `INFO` | Logging verbosity |
| Log File | `--log-file` | `log_file` | `null` | Optional log file path |

## Common Commands

```bash
# See all options
doc-fetcher --help

# Fetch with debug logging
doc-fetcher --log-level DEBUG

# Re-fetch everything (don't skip existing)
doc-fetcher --no-skip-existing

# Slower rate limit (be more respectful)
doc-fetcher --rate-limit 2.0

# Save logs to file
doc-fetcher --log-file fetcher.log
```

## Output Structure

```
docs/
├── stripe/
│   ├── api/
│   │   └── authentication/
│   │       └── api-authentication.md
│   ├── payments/
│   │   └── ...
│   └── ...
└── plaid/
    ├── api-reference/
    │   └── ...
    └── guides/
        └── ...
```

## Using as a Library

```python
from pathlib import Path
from doc_fetcher import StripeFetcher
from doc_fetcher.utils.logging_config import setup_logging

# Setup
logger = setup_logging("INFO")

# Fetch
fetcher = StripeFetcher(
    output_dir=Path("./docs"),
    rate_limit=0.5,
    logger=logger
)
fetcher.fetch()

# Stats
print(fetcher.stats)
```

## Next Steps

- Read [DOC_FETCHER_README.md](DOC_FETCHER_README.md) for full documentation
- See [example_usage.py](example_usage.py) for code examples
- Check [MIGRATION.md](MIGRATION.md) if migrating from `fetch_docs.py`
- Run `make help` to see available Makefile targets

## Troubleshooting

### ImportError: No module named 'doc_fetcher'

```bash
pip install -e .
```

### Rate limiting issues

Increase the delay:
```bash
doc-fetcher --rate-limit 2.0
```

### Need YAML support

```bash
pip install pyyaml
```

## Available Sources

Currently supported:
- `stripe` - Stripe API documentation
- `plaid` - Plaid API documentation

More sources can be easily added! See [DOC_FETCHER_README.md](DOC_FETCHER_README.md#adding-new-sources) for instructions.
