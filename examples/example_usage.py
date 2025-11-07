#!/usr/bin/env python3
"""
Example usage of the doc_fetcher package.

This demonstrates different ways to use doc_fetcher programmatically.
"""

from pathlib import Path
from doc_fetcher import StripeFetcher, PlaidFetcher
from doc_fetcher.config import FetcherConfig
from doc_fetcher.utils.logging_config import setup_logging


def example1_basic():
    """Example 1: Basic usage with default settings."""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)

    logger = setup_logging("INFO")

    # Fetch Stripe docs
    stripe = StripeFetcher(
        output_dir=Path("./docs"),
        rate_limit=0.5,
        skip_existing=True,
        logger=logger
    )
    stripe.fetch()

    # Fetch Plaid docs
    plaid = PlaidFetcher(
        output_dir=Path("./docs"),
        rate_limit=0.5,
        skip_existing=True,
        logger=logger
    )
    plaid.fetch()


def example2_custom_settings():
    """Example 2: Custom settings and logging."""
    print("=" * 80)
    print("Example 2: Custom Settings")
    print("=" * 80)

    # Setup custom logging
    logger = setup_logging(
        level="DEBUG",
        log_file="doc_fetcher.log"
    )

    # Fetch with custom settings
    stripe = StripeFetcher(
        output_dir=Path("./my-custom-docs"),
        rate_limit=1.0,  # Slower to be more respectful
        skip_existing=False,  # Re-fetch everything
        logger=logger
    )
    stripe.fetch()

    # Print statistics
    print("\nStatistics:")
    print(f"  Fetched: {stripe.stats['fetched']}")
    print(f"  Skipped: {stripe.stats['skipped']}")
    print(f"  Errors: {stripe.stats['errors']}")


def example3_with_config():
    """Example 3: Using FetcherConfig."""
    print("=" * 80)
    print("Example 3: Using Config Object")
    print("=" * 80)

    # Create config
    config = FetcherConfig(
        output_dir="./docs",
        rate_limit=0.5,
        skip_existing=True,
        log_level="INFO",
        sources=["stripe"]
    )

    # Setup logging from config
    logger = setup_logging(
        level=config.log_level,
        log_file=config.log_file
    )

    # Create fetcher from config
    stripe = StripeFetcher(
        output_dir=config.output_dir,
        rate_limit=config.rate_limit,
        skip_existing=config.skip_existing,
        logger=logger
    )
    stripe.fetch()


def example4_from_config_file():
    """Example 4: Loading from config file."""
    print("=" * 80)
    print("Example 4: Loading from Config File")
    print("=" * 80)

    config_path = Path("config.yaml")

    # Check if config exists
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print("Generate one with: doc-fetcher --generate-config config.yaml")
        return

    # Load config from file
    config = FetcherConfig.from_file(config_path)

    # Setup logging
    logger = setup_logging(
        level=config.log_level,
        log_file=config.log_file
    )

    # Fetch all configured sources
    fetcher_map = {
        "stripe": StripeFetcher,
        "plaid": PlaidFetcher,
    }

    for source in config.sources:
        if source in fetcher_map:
            fetcher_class = fetcher_map[source]
            fetcher = fetcher_class(
                output_dir=config.output_dir,
                rate_limit=config.rate_limit,
                skip_existing=config.skip_existing,
                logger=logger
            )
            fetcher.fetch()
        else:
            print(f"Unknown source: {source}")


def main():
    """Run examples."""
    examples = {
        "1": ("Basic usage", example1_basic),
        "2": ("Custom settings", example2_custom_settings),
        "3": ("Using config object", example3_with_config),
        "4": ("From config file", example4_from_config_file),
    }

    print("\nAvailable Examples:")
    print("-" * 80)
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("-" * 80)

    choice = input("\nWhich example would you like to run? (1-4, or 'all'): ").strip()

    if choice == "all":
        for name, func in examples.values():
            print("\n\n")
            func()
            print("\n")
    elif choice in examples:
        examples[choice][1]()
    else:
        print(f"Invalid choice: {choice}")


if __name__ == "__main__":
    main()
