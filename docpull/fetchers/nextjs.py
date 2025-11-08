from pathlib import Path
from typing import Optional
import logging

from .base import BaseFetcher


class NextJSFetcher(BaseFetcher):
    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)
        self.sitemap_url = "https://nextjs.org/sitemap.xml"
        self.base_url = "https://nextjs.org/"

    def fetch(self) -> None:
        self.logger.info("=" * 80)
        self.logger.info("FETCHING NEXT.JS DOCUMENTATION")
        self.logger.info("=" * 80)

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
            self.logger.info(f"[{idx}/{total}] Processing Next.js documentation...")

            path = url.replace(self.base_url, "").strip("/")
            parts = path.split("/")

            if parts and parts[0] == "docs":
                parts = parts[1:]

            if len(parts) >= 2:
                category_dir = self.output_dir / "next" / "/".join(parts[:-1])
            elif len(parts) == 1:
                category_dir = self.output_dir / "next"
            else:
                category_dir = self.output_dir / "next" / "other"

            from ..utils.file_utils import clean_filename

            filename = clean_filename(url, self.base_url)
            filepath = category_dir / filename
            self.process_url(url, filepath)

        self.logger.info("Next.js documentation fetch complete!")
        self.print_stats()
