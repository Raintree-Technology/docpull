#!/usr/bin/env python3
"""
Basic usage examples for docpull.

This demonstrates simple ways to use docpull programmatically.
"""

import sys
from pathlib import Path
from docpull import StripeFetcher, PlaidFetcher, NextJSFetcher
from docpull.utils.logging_config import setup_logging


def example_single_source():
    """Fetch documentation from a single source."""
    logger = setup_logging("INFO")

    # Fetch Stripe docs
    stripe = StripeFetcher(output_dir=Path("./docs"), rate_limit=0.5, skip_existing=True, logger=logger)
    stripe.fetch()

    # Print statistics
    print(f"\nFetched: {stripe.stats['fetched']}")
    print(f"Skipped: {stripe.stats['skipped']}")
    print(f"Errors: {stripe.stats['errors']}")


def example_multiple_sources():
    """Fetch documentation from multiple sources."""
    logger = setup_logging("INFO")
    output_dir = Path("./docs")

    sources = {
        "stripe": StripeFetcher,
        "plaid": PlaidFetcher,
        "nextjs": NextJSFetcher,
    }

    for name, fetcher_class in sources.items():
        print(f"\nFetching {name}...")
        fetcher = fetcher_class(output_dir=output_dir, rate_limit=0.5, skip_existing=True, logger=logger)
        fetcher.fetch()


def example_custom_settings():
    """Fetch with custom settings."""
    # Setup custom logging
    logger = setup_logging(level="DEBUG", log_file="doc_fetcher.log")

    # Fetch with custom settings
    stripe = StripeFetcher(
        output_dir=Path("./my-custom-docs"),
        rate_limit=1.0,  # Slower to be more respectful
        skip_existing=False,  # Re-fetch everything
        logger=logger,
    )
    stripe.fetch()


def simple_cli():
    """Simple command-line interface for quick usage."""
    if len(sys.argv) < 2:
        print("Usage: python basic_usage.py <source> [source2 ...]")
        print("\nAvailable sources:")
        print("  stripe  - Stripe API documentation")
        print("  plaid   - Plaid API documentation")
        print("  nextjs  - Next.js documentation")
        print("  all     - All sources")
        print("\nExamples:")
        print("  python basic_usage.py nextjs")
        print("  python basic_usage.py stripe plaid")
        print("  python basic_usage.py all")
        sys.exit(1)

    # Parse sources
    sources = sys.argv[1:]
    if "all" in sources:
        sources = ["stripe", "plaid", "nextjs"]

    # Setup
    logger = setup_logging("INFO")
    output_dir = Path("./docs")

    # Map sources to fetchers
    fetchers = {
        "stripe": StripeFetcher,
        "plaid": PlaidFetcher,
        "nextjs": NextJSFetcher,
    }

    # Fetch
    for source in sources:
        if source not in fetchers:
            print(f"Unknown source: {source}")
            continue

        fetcher_class = fetchers[source]
        fetcher = fetcher_class(output_dir=output_dir, rate_limit=0.5, skip_existing=True, logger=logger)
        fetcher.fetch()


if __name__ == "__main__":
    # When run as script, use simple CLI
    simple_cli()
