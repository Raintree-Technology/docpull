"""Plaid documentation fetcher."""

import logging
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from ..utils.file_utils import clean_filename
from .base import BaseFetcher


class PlaidFetcher(BaseFetcher):
    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://plaid.com/sitemap.xml"
        self.docs_url = "https://plaid.com/docs/"
        self.base_url = "https://plaid.com/"

    def fetch(self) -> None:
        self.logger.info("Fetching Plaid documentation")

        doc_urls: set[str] = set()

        self.logger.info(f"Fetching Plaid docs index from {self.docs_url}")

        try:
            response = self.session.get(self.docs_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            for link in soup.find_all("a", href=True):
                href = link["href"]
                if not isinstance(href, str):
                    continue

                if href.startswith("/docs/") or href.startswith("/api/"):
                    href = "https://plaid.com" + href

                # Validate URL before adding
                if not self.validate_url(href):
                    continue

                if "plaid.com/docs/" in href or "plaid.com/api/" in href:
                    href = href.split("#")[0].split("?")[0]
                    doc_urls.add(href)

        except Exception as e:
            self.logger.error(f"Error fetching Plaid docs index: {e}")

        sitemap_urls = self.fetch_sitemap(self.sitemap_url)

        for url in sitemap_urls:
            if ("/docs/" in url or "/api/" in url) and not any(
                x in url for x in ["/blog/", "/resources/", "/company/", "/customers/"]
            ):
                doc_urls.add(url.split("#")[0].split("?")[0])

        doc_urls_list = sorted(doc_urls)

        self.logger.info(f"Found {len(doc_urls_list)} Plaid documentation URLs")

        total = len(doc_urls_list)
        for idx, url in enumerate(doc_urls_list, 1):
            self.logger.info(f"[{idx}/{total}] Processing Plaid documentation")

            if "/api/" in url:
                path = url.replace("https://plaid.com/api/", "").strip("/")
                category_dir = self.output_dir / "plaid" / "api-reference"
            elif "/docs/" in url:
                path = url.replace("https://plaid.com/docs/", "").strip("/")
                category_dir = self.output_dir / "plaid" / "guides"
            else:
                path = ""
                category_dir = self.output_dir / "plaid" / "other"

            if "/" in path:
                parts = path.split("/")
                category_dir = category_dir / parts[0]

            filename = clean_filename(url, self.base_url)
            filepath = category_dir / filename
            self.process_url(url, filepath)

        self.logger.info("Plaid documentation fetch complete")
        self.print_stats()
