#!/usr/bin/env python3
"""
Simplified interface for doc_fetcher.

Usage:
    python fetch.py nextjs
    python fetch.py stripe plaid
    python fetch.py all
"""

import sys
from pathlib import Path
from doc_fetcher import StripeFetcher, PlaidFetcher, NextJSFetcher
from doc_fetcher.utils.logging_config import setup_logging


def main():
    """Simple command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python fetch.py <source> [source2 ...]")
        print("\nAvailable sources:")
        print("  stripe  - Stripe API documentation")
        print("  plaid   - Plaid API documentation")
        print("  nextjs  - Next.js documentation")
        print("  all     - All sources")
        print("\nExamples:")
        print("  python fetch.py nextjs")
        print("  python fetch.py stripe plaid")
        print("  python fetch.py all")
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
        fetcher = fetcher_class(
            output_dir=output_dir,
            rate_limit=0.5,
            skip_existing=True,
            logger=logger
        )
        fetcher.fetch()


if __name__ == "__main__":
    main()
