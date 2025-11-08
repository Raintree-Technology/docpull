from pathlib import Path
from typing import Optional, Set
import logging

from bs4 import BeautifulSoup

from .base import BaseFetcher


class PlaidFetcher(BaseFetcher):
    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://plaid.com/sitemap.xml"
        self.docs_url = "https://plaid.com/docs/"
        self.base_url = "https://plaid.com/"

    def fetch(self) -> None:
        self.logger.info("=" * 80)
        self.logger.info("FETCHING PLAID DOCUMENTATION")
        self.logger.info("=" * 80)

        doc_urls: Set[str] = set()

        self.logger.info(f"Fetching Plaid docs index from {self.docs_url}")

        try:
            response = self.session.get(self.docs_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            for link in soup.find_all("a", href=True):
                href_raw = link["href"]
                if not isinstance(href_raw, str):
                    continue
                href = href_raw

                if href.startswith("/docs/"):
                    href = "https://plaid.com" + href
                elif href.startswith("/api/"):
                    href = "https://plaid.com" + href

                if "plaid.com/docs/" in href or "plaid.com/api/" in href:
                    href = href.split("#")[0].split("?")[0]
                    doc_urls.add(href)

        except Exception as e:
            self.logger.error(f"Error fetching Plaid docs index: {e}")

        sitemap_urls = self.fetch_sitemap(self.sitemap_url)

        for url in sitemap_urls:
            if "/docs/" in url or "/api/" in url:
                if not any(x in url for x in ["/blog/", "/resources/", "/company/", "/customers/"]):
                    doc_urls.add(url.split("#")[0].split("?")[0])

        doc_urls_list = sorted(list(doc_urls))

        self.logger.info(f"Found {len(doc_urls_list)} Plaid documentation URLs")

        total = len(doc_urls_list)
        for idx, url in enumerate(doc_urls_list, 1):
            self.logger.info(f"[{idx}/{total}] Processing Plaid documentation...")

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

            from ..utils.file_utils import clean_filename

            filename = clean_filename(url, self.base_url)
            filepath = category_dir / filename
            self.process_url(url, filepath)

        self.logger.info("Plaid documentation fetch complete!")
        self.print_stats()
