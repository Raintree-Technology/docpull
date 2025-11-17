"""Next.js documentation fetcher."""

import logging
from pathlib import Path
from typing import Optional

from .parallel_base import ParallelFetcher


class NextJSFetcher(ParallelFetcher):
    """Fetcher for Next.js documentation."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.2,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
        max_workers: int = 15,
    ) -> None:
        """
        Initialize Next.js fetcher.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            logger: Logger instance
            max_workers: Number of concurrent workers
        """
        super().__init__(output_dir, rate_limit, skip_existing, logger, max_workers)
        self.sitemap_url = "https://nextjs.org/sitemap.xml"
        self.base_url = "https://nextjs.org/"

    def fetch(self) -> None:
        """Fetch all Next.js documentation."""
        self.logger.info("Fetching Next.js documentation")

        urls = self.fetch_sitemap(self.sitemap_url)

        if not urls:
            self.logger.error("No URLs found in Next.js sitemap")
            return

        doc_urls = self.filter_urls(
            urls, include_patterns=["/docs/"], exclude_patterns=["/blog/", "/showcase/", "/conf/", "/learn/"]
        )

        self.logger.info(f"Found {len(doc_urls)} documentation URLs")

        url_output_pairs = []
        for url in doc_urls:
            filepath = self.create_output_path(url, self.base_url, "next", strip_prefix="docs")
            url_output_pairs.append((url, filepath))

        self.fetch_urls_parallel(url_output_pairs)

        self.logger.info("Next.js documentation fetch complete")
        self.print_stats()
