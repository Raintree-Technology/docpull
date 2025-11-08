"""React documentation fetcher."""

from pathlib import Path
from typing import Optional
import logging

from .parallel_base import ParallelFetcher


class ReactFetcher(ParallelFetcher):
    """Fetcher for React documentation."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.2,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
        max_workers: int = 15,
    ):
        """
        Initialize React fetcher.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            logger: Logger instance
            max_workers: Number of concurrent workers
        """
        super().__init__(output_dir, rate_limit, skip_existing, logger, max_workers)
        self.sitemap_url = "https://react.dev/sitemap.xml"
        self.base_url = "https://react.dev/"

    def fetch(self) -> None:
        """Fetch all React documentation."""
        self.logger.info("=" * 80)
        self.logger.info("FETCHING REACT DOCUMENTATION (PARALLEL)")
        self.logger.info("=" * 80)

        # Fetch sitemap
        urls = self.fetch_sitemap(self.sitemap_url)

        if not urls:
            self.logger.error("No URLs found in React sitemap")
            return

        # Filter for documentation and reference only
        doc_urls = self.filter_urls(
            urls, include_patterns=["/reference/", "/learn/"], exclude_patterns=["/blog/", "/community/"]
        )

        self.logger.info(f"Found {len(doc_urls)} documentation URLs")

        # Prepare URL paths for parallel fetching
        url_paths = []
        for url in doc_urls:
            # Remove base URL and create path structure
            path = url.replace(self.base_url, "").strip("/")
            parts = path.split("/")

            # Create directory structure
            if len(parts) >= 2:
                category_dir = self.output_dir / "react" / "/".join(parts[:-1])
            elif len(parts) == 1:
                category_dir = self.output_dir / "react"
            else:
                category_dir = self.output_dir / "react" / "other"

            # Generate filename
            from ..utils.file_utils import clean_filename

            filename = clean_filename(url, self.base_url)
            filepath = category_dir / filename

            url_paths.append((url, filepath))

        # Fetch in parallel
        self.fetch_urls_parallel(url_paths)

        self.logger.info("React documentation fetch complete!")
        self.print_stats()
