"""Next.js documentation fetcher."""

from pathlib import Path
from typing import Optional
import logging

from .base import BaseFetcher


class NextJSFetcher(BaseFetcher):
    """Fetcher for Next.js documentation."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Next.js fetcher.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            logger: Logger instance
        """
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://nextjs.org/sitemap.xml"
        self.base_url = "https://nextjs.org/"

    def fetch(self) -> None:
        """Fetch all Next.js documentation."""
        self.logger.info("=" * 80)
        self.logger.info("FETCHING NEXT.JS DOCUMENTATION")
        self.logger.info("=" * 80)

        # Fetch sitemap
        urls = self.fetch_sitemap(self.sitemap_url)

        if not urls:
            self.logger.error("No URLs found in Next.js sitemap")
            return

        # Filter for documentation only (exclude blog, showcase, etc.)
        doc_urls = self.filter_urls(
            urls,
            include_patterns=["/docs/"],
            exclude_patterns=["/blog/", "/showcase/", "/conf/", "/learn/"]
        )

        self.logger.info(f"Found {len(doc_urls)} documentation URLs")

        # Categorize URLs
        categories = self.categorize_urls(doc_urls, self.base_url)

        self.logger.info(f"Found {len(categories)} categories:")
        for cat, cat_urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            self.logger.info(f"  {cat}: {len(cat_urls)} pages")

        # Fetch each page
        total = len(doc_urls)
        for idx, url in enumerate(doc_urls, 1):
            self.logger.info(f"[{idx}/{total}] Processing Next.js documentation...")

            # Determine directory structure
            # URLs look like: https://nextjs.org/docs/app/api-reference/...
            path = url.replace(self.base_url, "").strip("/")
            parts = path.split("/")

            # Remove 'docs' from path parts
            if parts and parts[0] == "docs":
                parts = parts[1:]

            # Create directory structure
            if len(parts) >= 2:
                # e.g., app/api-reference/cli
                category_dir = self.output_dir / "next" / "/".join(parts[:-1])
            elif len(parts) == 1:
                category_dir = self.output_dir / "next"
            else:
                category_dir = self.output_dir / "next" / "other"

            # Generate filename
            from ..utils.file_utils import clean_filename
            filename = clean_filename(url, self.base_url)
            filepath = category_dir / filename

            # Process the URL
            self.process_url(url, filepath)

        self.logger.info("Next.js documentation fetch complete!")
        self.print_stats()
