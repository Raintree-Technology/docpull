"""Stripe documentation fetcher."""

from pathlib import Path
from typing import Optional
import logging

from .base import BaseFetcher


class StripeFetcher(BaseFetcher):
    """Fetcher for Stripe documentation."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Stripe fetcher.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            logger: Logger instance
        """
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://docs.stripe.com/sitemap.xml"
        self.base_url = "https://docs.stripe.com/"

    def fetch(self) -> None:
        """Fetch all Stripe documentation."""
        self.logger.info("=" * 80)
        self.logger.info("FETCHING STRIPE DOCUMENTATION")
        self.logger.info("=" * 80)

        # Fetch sitemap
        urls = self.fetch_sitemap(self.sitemap_url)

        if not urls:
            self.logger.error("No URLs found in Stripe sitemap")
            return

        # Filter out changelog noise
        exclude_patterns = ["/changelog/", "/upgrades/"]
        urls = self.filter_urls(urls, [self.base_url], exclude_patterns)

        # Categorize URLs
        categories = self.categorize_urls(urls, self.base_url)

        self.logger.info(f"Found {len(categories)} categories:")
        for cat, cat_urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            self.logger.info(f"  {cat}: {len(cat_urls)} pages")

        # Fetch each page
        total = len(urls)
        for idx, url in enumerate(urls, 1):
            self.logger.info(f"[{idx}/{total}] Processing Stripe documentation...")

            # Determine category and subcategory
            path = url.replace(self.base_url, "").strip("/")
            parts = path.split("/")

            # Create organized directory structure
            if len(parts) >= 2:
                category_dir = self.output_dir / "stripe" / parts[0] / parts[1]
            elif len(parts) == 1:
                category_dir = self.output_dir / "stripe" / parts[0]
            else:
                category_dir = self.output_dir / "stripe" / "other"

            # Generate filename
            from ..utils.file_utils import clean_filename
            filename = clean_filename(url, self.base_url)
            filepath = category_dir / filename

            # Process the URL
            self.process_url(url, filepath)

        self.logger.info("Stripe documentation fetch complete!")
        self.print_stats()
