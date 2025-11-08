#!/usr/bin/env python3
"""
Advanced usage examples for docpull.

This demonstrates advanced features including config files, custom logging,
and programmatic usage patterns.
"""

from pathlib import Path
from docpull import (
    StripeFetcher,
    PlaidFetcher,
    NextJSFetcher,
    D3DevDocsFetcher,
    BunFetcher,
    TailwindFetcher,
    ReactFetcher,
)
from docpull.config import FetcherConfig
from docpull.utils.logging_config import setup_logging


def example_with_config_object():
    """Example using FetcherConfig object."""
    print("=" * 80)
    print("Example: Using Config Object")
    print("=" * 80)

    # Create config
    config = FetcherConfig(
        output_dir="./docs", rate_limit=0.5, skip_existing=True, log_level="INFO", sources=["stripe", "plaid"]
    )

    # Setup logging from config
    logger = setup_logging(level=config.log_level, log_file=config.log_file)

    # Create fetcher from config
    stripe = StripeFetcher(
        output_dir=config.output_dir,
        rate_limit=config.rate_limit,
        skip_existing=config.skip_existing,
        logger=logger,
    )
    stripe.fetch()


def example_from_config_file():
    """Example loading from config file."""
    print("=" * 80)
    print("Example: Loading from Config File")
    print("=" * 80)

    config_path = Path("config.yaml")

    # Check if config exists
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print("Generate one with: docpull --generate-config config.yaml")
        return

    # Load config from file
    config = FetcherConfig.from_file(config_path)

    # Setup logging
    logger = setup_logging(level=config.log_level, log_file=config.log_file)

    # Fetch all configured sources
    fetcher_map = {
        "stripe": StripeFetcher,
        "plaid": PlaidFetcher,
        "nextjs": NextJSFetcher,
        "d3": D3DevDocsFetcher,
        "bun": BunFetcher,
        "tailwind": TailwindFetcher,
        "react": ReactFetcher,
    }

    for source in config.sources:
        if source in fetcher_map:
            print(f"\nFetching {source}...")
            fetcher_class = fetcher_map[source]
            fetcher = fetcher_class(
                output_dir=config.output_dir,
                rate_limit=config.rate_limit,
                skip_existing=config.skip_existing,
                logger=logger,
            )
            fetcher.fetch()
        else:
            print(f"Unknown source: {source}")


def example_all_fetchers():
    """Example showing all available fetchers."""
    print("=" * 80)
    print("Example: All Available Fetchers")
    print("=" * 80)

    logger = setup_logging("INFO")
    output_dir = Path("./docs")

    fetchers = {
        "stripe": StripeFetcher,
        "plaid": PlaidFetcher,
        "nextjs": NextJSFetcher,
        "d3": D3DevDocsFetcher,
        "bun": BunFetcher,
        "tailwind": TailwindFetcher,
        "react": ReactFetcher,
    }

    print(f"Available fetchers: {', '.join(fetchers.keys())}\n")

    # Fetch from each source
    for name, fetcher_class in fetchers.items():
        print(f"Fetching {name}...")
        fetcher = fetcher_class(output_dir=output_dir, rate_limit=0.5, skip_existing=True, logger=logger)
        fetcher.fetch()

        # Print stats
        print(f"  Fetched: {fetcher.stats['fetched']}")
        print(f"  Skipped: {fetcher.stats['skipped']}")
        print(f"  Errors: {fetcher.stats['errors']}\n")


def example_custom_error_handling():
    """Example with custom error handling."""
    print("=" * 80)
    print("Example: Custom Error Handling")
    print("=" * 80)

    logger = setup_logging("DEBUG")

    try:
        stripe = StripeFetcher(output_dir=Path("./docs"), rate_limit=0.5, skip_existing=True, logger=logger)
        stripe.fetch()

        # Check for errors
        if stripe.stats["errors"] > 0:
            print(f"\nWarning: {stripe.stats['errors']} errors occurred during fetch")
        else:
            print("\nFetch completed successfully!")

    except Exception as e:
        print(f"Error during fetch: {e}")
        raise


def main():
    """Run examples."""
    examples = {
        "1": ("Using config object", example_with_config_object),
        "2": ("Loading from config file", example_from_config_file),
        "3": ("All available fetchers", example_all_fetchers),
        "4": ("Custom error handling", example_custom_error_handling),
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
