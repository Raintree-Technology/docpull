"""Stripe documentation fetcher."""

import logging
from pathlib import Path
from typing import Optional

from .base import BaseFetcher


class StripeFetcher(BaseFetcher):
    """Fetcher for Stripe documentation."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://docs.stripe.com/sitemap.xml"
        self.base_url = "https://docs.stripe.com/"

    def fetch(self) -> None:
        self.logger.info("Fetching Stripe documentation")

        urls = self.fetch_sitemap(self.sitemap_url)

        if not urls:
            self.logger.error("No URLs found in Stripe sitemap")
            return

        exclude_patterns = ["/changelog/", "/upgrades/"]
        urls = self.filter_urls(urls, [self.base_url], exclude_patterns)

        categories = self.categorize_urls(urls, self.base_url)

        self.logger.info(f"Found {len(categories)} categories:")
        for cat, cat_urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            self.logger.info(f"  {cat}: {len(cat_urls)} pages")

        total = len(urls)
        for idx, url in enumerate(urls, 1):
            self.logger.info(f"[{idx}/{total}] Processing Stripe documentation")
            filepath = self.create_output_path(url, self.base_url, "stripe")
            self.process_url(url, filepath)

        self.logger.info("Stripe documentation fetch complete")
        self.print_stats()
