import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .config import FetcherConfig
from .fetchers import (
    BunFetcher,
    D3DevDocsFetcher,
    NextJSFetcher,
    PlaidFetcher,
    ReactFetcher,
    StripeFetcher,
    TailwindFetcher,
    TurborepoFetcher,
)
from .fetchers.generic_async import GenericAsyncFetcher
from .utils.logging_config import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="docpull",
        description="Fetch and convert documentation from any URL or known sources to markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch from any documentation URL
  docpull https://aptos.dev
  docpull https://docs.anthropic.com

  # Fetch using profile names (shortcuts)
  docpull stripe
  docpull nextjs plaid

  # Mix URLs and profiles
  docpull stripe https://newsite.com/docs

  # Control scraping depth and pages
  docpull https://example.com/docs --max-pages 100 --max-depth 3

  # Legacy syntax still works
  docpull --source stripe --source nextjs

  # Use a config file
  docpull --config config.yaml

  # Generate a sample config file
  docpull --generate-config config.yaml
        """,
    )

    # Positional arguments for URLs or profile names
    parser.add_argument(
        "targets",
        nargs="*",
        help="URLs or profile names to fetch (e.g., 'https://docs.site.com', 'stripe', 'nextjs')",
    )

    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        help="Path to config file (YAML or JSON)",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Directory to save documentation (default: ./docs)",
    )

    parser.add_argument(
        "--source",
        "-s",
        nargs="+",
        choices=["all", "bun", "d3", "nextjs", "plaid", "react", "stripe", "tailwind", "turborepo"],
        default=None,
        dest="sources",
        help="Documentation source(s) to fetch. Use 'all' for everything. (default: all)",
    )

    parser.add_argument(
        "--rate-limit",
        "-r",
        type=float,
        default=None,
        help="Seconds to wait between requests (default: 0.5)",
    )

    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Re-fetch files that already exist",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_const",
        const="DEBUG",
        dest="log_level_override",
        help="Enable verbose output (equivalent to --log-level DEBUG)",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_const",
        const="ERROR",
        dest="log_level_override",
        help="Suppress informational output (equivalent to --log-level ERROR)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fetched without actually downloading",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of pages to fetch (default: unlimited)",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum crawl depth when following links (default: 5)",
    )

    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=10,
        help="Maximum concurrent requests for async fetching (default: 10)",
    )

    parser.add_argument(
        "--js",
        "--javascript",
        action="store_true",
        dest="use_js",
        help="Enable JavaScript rendering with Playwright (slower but handles JS-heavy sites)",
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bars",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Path to log file (default: console only)",
    )

    parser.add_argument(
        "--generate-config",
        type=Path,
        metavar="PATH",
        help="Generate a sample config file and exit",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def generate_sample_config(output_path: Path) -> None:
    """
    Generate a sample configuration file.

    Args:
        output_path: Path to save the config file
    """
    config = FetcherConfig()

    # Determine format from extension
    suffix = output_path.suffix.lower()

    if suffix in [".yaml", ".yml"]:
        config.save_yaml(output_path)
        print(f"Sample YAML config generated: {output_path}")
    elif suffix == ".json":
        config.save_json(output_path)
        print(f"Sample JSON config generated: {output_path}")
    else:
        print(f"Warning: Unknown extension {suffix}, generating YAML")
        output_path = output_path.with_suffix(".yaml")
        config.save_yaml(output_path)
        print(f"Sample YAML config generated: {output_path}")


def get_config(args: argparse.Namespace) -> FetcherConfig:
    """
    Get configuration from args and config file.

    Args:
        args: Parsed command-line arguments

    Returns:
        FetcherConfig instance
    """
    # Load from config file if provided
    config = FetcherConfig.from_file(args.config) if args.config else FetcherConfig()

    # Override with command-line arguments
    if args.output_dir is not None:
        config.output_dir = args.output_dir

    if args.sources is not None:
        # Handle "all" keyword
        if "all" in args.sources:
            config.sources = ["bun", "d3", "nextjs", "plaid", "react", "stripe", "tailwind", "turborepo"]
        else:
            config.sources = args.sources

    if args.rate_limit is not None:
        config.rate_limit = args.rate_limit

    if args.no_skip_existing:
        config.skip_existing = False

    # Handle log level (verbose/quiet shortcuts override --log-level)
    if args.log_level_override is not None:
        config.log_level = args.log_level_override
    elif args.log_level is not None:
        config.log_level = args.log_level

    if args.log_file is not None:
        config.log_file = str(args.log_file)

    # Store dry-run flag in config
    config.dry_run = args.dry_run

    return config


def run_fetchers(config: FetcherConfig) -> int:
    """
    Run the fetchers based on configuration.

    Args:
        config: FetcherConfig instance

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Setup logging
    logger = setup_logging(
        level=config.log_level,
        log_file=config.log_file,
    )

    logger.info("docpull - Documentation Fetcher")
    logger.info(f"Mode: {'DRY RUN' if config.dry_run else 'FETCH'}")
    logger.info(f"Output directory: {config.output_dir}")
    logger.info(f"Rate limit: {config.rate_limit}s between requests")
    logger.info(f"Skip existing: {config.skip_existing}")
    logger.info(f"Sources: {', '.join(config.sources)}")
    logger.info("")

    if config.dry_run:
        logger.info("DRY RUN MODE: No files will be downloaded")
        logger.info("")

    # Map source names to fetcher classes
    fetcher_map = {
        "bun": BunFetcher,
        "d3": D3DevDocsFetcher,
        "nextjs": NextJSFetcher,
        "plaid": PlaidFetcher,
        "react": ReactFetcher,
        "stripe": StripeFetcher,
        "tailwind": TailwindFetcher,
        "turborepo": TurborepoFetcher,
    }

    # Run fetchers
    errors = 0
    for source in config.sources:
        if source not in fetcher_map:
            logger.error(f"Unknown source: {source}")
            errors += 1
            continue

        try:
            fetcher_class = fetcher_map[source]
            fetcher = fetcher_class(
                output_dir=config.output_dir,
                rate_limit=config.rate_limit,
                skip_existing=config.skip_existing,
                logger=logger,
            )
            fetcher.fetch()
        except Exception as e:
            logger.error(f"Error fetching {source}: {e}", exc_info=True)
            errors += 1

    logger.info("")
    if errors > 0:
        logger.error(f"Completed with {errors} error(s)")
        return 1
    else:
        logger.info("All documentation fetched successfully")
        return 0


def run_generic_fetchers(args: argparse.Namespace) -> int:
    """
    Run generic fetchers for URLs or profile names.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Setup logging
    log_level = args.log_level_override or args.log_level or "INFO"
    logger = setup_logging(
        level=log_level,
        log_file=args.log_file,
    )

    output_dir = Path(args.output_dir) if args.output_dir else Path("./docs")
    rate_limit = args.rate_limit if args.rate_limit is not None else 0.5
    skip_existing = not args.no_skip_existing
    max_pages = args.max_pages
    max_depth = args.max_depth
    max_concurrent = args.max_concurrent
    use_js = args.use_js
    show_progress = not args.no_progress

    logger.info("docpull - Universal Documentation Fetcher")
    logger.info(f"Targets: {', '.join(args.targets)}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Rate limit: {rate_limit}s between requests")
    logger.info(f"Skip existing: {skip_existing}")
    logger.info(f"Max concurrent: {max_concurrent}")
    if max_pages:
        logger.info(f"Max pages: {max_pages}")
    logger.info(f"Max depth: {max_depth}")
    if use_js:
        logger.info("JavaScript rendering: ENABLED (slower but handles JS sites)")
    logger.info("")

    # Run async generic fetcher for each target
    errors = 0
    for target in args.targets:
        try:
            logger.info(f"Fetching: {target}")
            fetcher = GenericAsyncFetcher(
                url_or_profile=target,
                output_dir=output_dir,
                rate_limit=rate_limit,
                skip_existing=skip_existing,
                logger=logger,
                max_pages=max_pages,
                max_depth=max_depth,
                max_concurrent=max_concurrent,
                use_js=use_js,
                show_progress=show_progress,
            )
            fetcher.fetch()  # This calls asyncio.run() internally
        except Exception as e:
            logger.error(f"Error fetching {target}: {e}", exc_info=True)
            errors += 1

    logger.info("")
    if errors > 0:
        logger.error(f"Completed with {errors} error(s)")
        return 1
    else:
        logger.info("All documentation fetched successfully")
        return 0


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Handle --generate-config
    if args.generate_config:
        try:
            generate_sample_config(args.generate_config)
            return 0
        except Exception as e:
            print(f"Error generating config: {e}", file=sys.stderr)
            return 1

    # Determine if using new URL-based interface or legacy source-based
    use_generic = bool(args.targets)

    if use_generic:
        # New URL-based interface
        return run_generic_fetchers(args)
    else:
        # Legacy source-based interface
        try:
            config = get_config(args)
        except Exception as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            return 1
        return run_fetchers(config)


if __name__ == "__main__":
    sys.exit(main())
