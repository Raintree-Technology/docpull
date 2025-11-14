"""Next.js documentation fetcher."""

import logging
from pathlib import Path
from typing import Optional

from .base import BaseFetcher


class NextJSFetcher(BaseFetcher):
    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://nextjs.org/sitemap.xml"
        self.base_url = "https://nextjs.org/"

    def fetch(self) -> None:
        self.logger.info("Fetching Next.js documentation")

        urls = self.fetch_sitemap(self.sitemap_url)

        if not urls:
            self.logger.error("No URLs found in Next.js sitemap")
            return

        doc_urls = self.filter_urls(
            urls, include_patterns=["/docs/"], exclude_patterns=["/blog/", "/showcase/", "/conf/", "/learn/"]
        )

        self.logger.info(f"Found {len(doc_urls)} documentation URLs")

        categories = self.categorize_urls(doc_urls, self.base_url)

        self.logger.info(f"Found {len(categories)} categories:")
        for cat, cat_urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            self.logger.info(f"  {cat}: {len(cat_urls)} pages")

        total = len(doc_urls)
        for idx, url in enumerate(doc_urls, 1):
            self.logger.info(f"[{idx}/{total}] Processing Next.js documentation")
            filepath = self.create_output_path(url, self.base_url, "next", strip_prefix="docs")
            self.process_url(url, filepath)

        self.logger.info("Next.js documentation fetch complete")
        self.print_stats()
