# Migration Guide: fetch_docs.py → doc_fetcher

The old `fetch_docs.py` script has been replaced with a proper Python package called `doc_fetcher`.

## What Changed?

### Before (fetch_docs.py)

```bash
python fetch_docs.py
```

### After (doc_fetcher)

```bash
# Install the package
pip install -e .

# Use the CLI
doc-fetcher

# Or use as a module
python -m doc_fetcher
```

## Benefits of the New Module

1. **Modular Architecture**: Easy to extend with new sources
2. **Configuration Files**: YAML/JSON config support
3. **Better CLI**: More options and better help
4. **Proper Package**: Installable with pip
5. **Better Logging**: Structured, configurable logging
6. **API Usage**: Can be imported and used in other Python code
7. **Type Hints**: Better IDE support and type checking
8. **Statistics**: Track fetching stats (fetched, skipped, errors)

## Migration Steps

### Step 1: Install the Package

```bash
cd /Users/zach/Documents/cc-skills
pip install -e .
```

### Step 2: Update Your Usage

#### If you ran fetch_docs.py directly:

**Before:**
```bash
python fetch_docs.py
```

**After:**
```bash
doc-fetcher
```

#### If you imported DocFetcher class:

**Before:**
```python
from fetch_docs import DocFetcher

fetcher = DocFetcher('./docs', rate_limit=0.5)
fetcher.fetch_stripe_docs()
fetcher.fetch_plaid_docs()
```

**After:**
```python
from doc_fetcher import StripeFetcher, PlaidFetcher
from doc_fetcher.utils.logging_config import setup_logging
from pathlib import Path

logger = setup_logging("INFO")

stripe = StripeFetcher(Path('./docs'), rate_limit=0.5, logger=logger)
stripe.fetch()

plaid = PlaidFetcher(Path('./docs'), rate_limit=0.5, logger=logger)
plaid.fetch()
```

### Step 3: Create a Config File (Optional but Recommended)

```bash
# Generate a sample config
doc-fetcher --generate-config config.yaml

# Edit it
vim config.yaml

# Use it
doc-fetcher --config config.yaml
```

## Feature Comparison

| Feature | fetch_docs.py | doc_fetcher |
|---------|---------------|-------------|
| Stripe docs | ✅ | ✅ |
| Plaid docs | ✅ | ✅ |
| Config files | ❌ | ✅ YAML/JSON |
| CLI options | ❌ | ✅ Full argparse |
| Modular design | ❌ | ✅ |
| Logging | Basic prints | ✅ Structured logging |
| Rate limiting | ✅ | ✅ |
| Skip existing | ✅ | ✅ |
| Statistics | ❌ | ✅ |
| API usage | Limited | ✅ Full API |
| Add new sources | Hard | ✅ Easy |
| Type hints | ❌ | ✅ |
| Package install | ❌ | ✅ pip install |

## Advanced Usage Examples

### Example 1: Fetch Only Stripe

```bash
doc-fetcher --sources stripe
```

### Example 2: Custom Output Directory

```bash
doc-fetcher --output-dir /path/to/docs
```

### Example 3: Slower Rate Limit

```bash
doc-fetcher --rate-limit 2.0
```

### Example 4: Debug Logging

```bash
doc-fetcher --log-level DEBUG --log-file debug.log
```

### Example 5: Re-fetch Everything

```bash
doc-fetcher --no-skip-existing
```

## Backward Compatibility

The old `fetch_docs.py` file is kept for reference, but you should migrate to the new package.

If you need to maintain the old script for some reason, it's still in the repository, but it won't receive updates.

## Need Help?

- See `DOC_FETCHER_README.md` for full documentation
- Run `doc-fetcher --help` for CLI options
- Check example configs: `config.example.yaml` and `config.example.json`

## Adding New Sources

With the new architecture, adding sources is much easier. See the "Adding New Sources" section in `DOC_FETCHER_README.md`.
