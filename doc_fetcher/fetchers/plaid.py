"""Plaid documentation fetcher."""

from pathlib import Path
from typing import Optional, Set
import logging

from bs4 import BeautifulSoup

from .base import BaseFetcher


class PlaidFetcher(BaseFetcher):
    """Fetcher for Plaid documentation."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Plaid fetcher.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            logger: Logger instance
        """
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://plaid.com/sitemap.xml"
        self.docs_url = "https://plaid.com/docs/"
        self.base_url = "https://plaid.com/"

    def fetch(self) -> None:
        """Fetch all Plaid documentation."""
        self.logger.info("=" * 80)
        self.logger.info("FETCHING PLAID DOCUMENTATION")
        self.logger.info("=" * 80)

        doc_urls: Set[str] = set()

        # Method 1: Crawl from main docs page
        self.logger.info(f"Fetching Plaid docs index from {self.docs_url}")

        try:
            response = self.session.get(self.docs_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all links to documentation pages
            for link in soup.find_all("a", href=True):
                href = link["href"]

                # Convert relative URLs to absolute
                if href.startswith("/docs/"):
                    href = "https://plaid.com" + href
                elif href.startswith("/api/"):
                    href = "https://plaid.com" + href

                # Only include docs and api pages
                if "plaid.com/docs/" in href or "plaid.com/api/" in href:
                    # Remove anchors and query params
                    href = href.split("#")[0].split("?")[0]
                    doc_urls.add(href)

        except Exception as e:
            self.logger.error(f"Error fetching Plaid docs index: {e}")

        # Method 2: Fetch sitemap
        sitemap_urls = self.fetch_sitemap(self.sitemap_url)

        # Filter sitemap for docs and API pages
        for url in sitemap_urls:
            if "/docs/" in url or "/api/" in url:
                # Exclude blog, marketing
                if not any(x in url for x in ["/blog/", "/resources/", "/company/", "/customers/"]):
                    doc_urls.add(url.split("#")[0].split("?")[0])

        doc_urls = sorted(list(doc_urls))

        self.logger.info(f"Found {len(doc_urls)} Plaid documentation URLs")

        # Fetch each page
        total = len(doc_urls)
        for idx, url in enumerate(doc_urls, 1):
            self.logger.info(f"[{idx}/{total}] Processing Plaid documentation...")

            # Determine directory structure
            if "/api/" in url:
                path = url.replace("https://plaid.com/api/", "").strip("/")
                category_dir = self.output_dir / "plaid" / "api-reference"
            elif "/docs/" in url:
                path = url.replace("https://plaid.com/docs/", "").strip("/")
                category_dir = self.output_dir / "plaid" / "guides"
            else:
                path = ""
                category_dir = self.output_dir / "plaid" / "other"

            # Create subdirectories based on path
            if "/" in path:
                parts = path.split("/")
                category_dir = category_dir / parts[0]

            # Generate filename
            from ..utils.file_utils import clean_filename
            filename = clean_filename(url, self.base_url)
            filepath = category_dir / filename

            # Process the URL
            self.process_url(url, filepath)

        self.logger.info("Plaid documentation fetch complete!")
        self.print_stats()
