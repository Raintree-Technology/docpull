"""Generic documentation fetcher that works with any URL."""

import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .base import BaseFetcher


class GenericFetcher(BaseFetcher):
    """
    Generic fetcher that can scrape documentation from any URL.
    """

    def __init__(
        self,
        url: str,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
        max_pages: Optional[int] = None,
        max_depth: int = 5,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize generic fetcher.

        Args:
            url: URL to scrape
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            logger: Logger instance
            max_pages: Maximum pages to fetch
            max_depth: Maximum crawl depth
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
        """
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)

        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}. Must start with http:// or https://")

        self.start_url = url
        self.max_pages = max_pages
        self.max_depth = max_depth

        # Infer settings from URL
        self.sitemap_url = self._guess_sitemap_url(self.start_url)
        self.base_url = self._extract_base_url(self.start_url)
        self.include_patterns = include_patterns or [self.base_url]
        self.exclude_patterns = exclude_patterns or []
        self.output_subdir = urlparse(self.start_url).netloc.replace(".", "_")

    def _extract_base_url(self, url: str) -> str:
        """Extract base URL from a full URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/"

    def _guess_sitemap_url(self, url: str) -> Optional[str]:
        """
        Guess sitemap URL for a given domain.

        Args:
            url: URL to guess sitemap for

        Returns:
            Guessed sitemap URL or None
        """
        base = self._extract_base_url(url)
        common_paths = ["sitemap.xml", "sitemap_index.xml", "docs/sitemap.xml"]

        for path in common_paths:
            sitemap_url = urljoin(base, path)
            try:
                self.logger.debug(f"Trying sitemap: {sitemap_url}")
                response = self.session.head(sitemap_url, timeout=10)
                if response.status_code == 200:
                    self.logger.info(f"Found sitemap: {sitemap_url}")
                    return sitemap_url
            except Exception:
                continue

        return None

    def _crawl_links(self, start_urls: set[str], max_depth: int = 5) -> set[str]:
        """
        Crawl links from start URLs.

        Args:
            start_urls: URLs to start crawling from
            max_depth: Maximum depth to crawl

        Returns:
            Set of discovered URLs
        """
        discovered: set[str] = set()
        to_visit: set[tuple[str, int]] = {(url, 0) for url in start_urls}
        visited: set[str] = set()

        while to_visit:
            url, depth = to_visit.pop()

            if url in visited or depth > max_depth:
                continue

            if not self.validate_url(url):
                continue

            visited.add(url)
            discovered.add(url)

            if depth >= max_depth:
                continue

            try:
                self.logger.debug(f"Crawling: {url} (depth {depth})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if not isinstance(href, str):
                        continue

                    # Resolve relative URLs
                    absolute_url = urljoin(url, href)

                    # Remove fragments and query params
                    absolute_url = absolute_url.split("#")[0].split("?")[0]

                    # Check if URL matches patterns
                    if not any(pattern in absolute_url for pattern in self.include_patterns):
                        continue

                    if any(pattern in absolute_url for pattern in self.exclude_patterns):
                        continue

                    if absolute_url not in visited:
                        to_visit.add((absolute_url, depth + 1))

            except Exception as e:
                self.logger.debug(f"Error crawling {url}: {e}")
                continue

        return discovered

    def fetch(self) -> None:
        """Fetch documentation from the URL."""
        self.logger.info(f"Fetching documentation from {self.start_url}")

        urls: set[str] = set()

        # Try sitemap first
        if self.sitemap_url:
            sitemap_urls = self.fetch_sitemap(self.sitemap_url)
            if sitemap_urls:
                urls.update(sitemap_urls)
                self.logger.info(f"Found {len(sitemap_urls)} URLs in sitemap")

        # Crawl links if no sitemap found
        if not urls:
            start_urls = {self.start_url}
            self.logger.info(f"Crawling links from {len(start_urls)} start URL(s)")
            crawled_urls = self._crawl_links(start_urls, self.max_depth)
            urls.update(crawled_urls)
            self.logger.info(f"Discovered {len(crawled_urls)} URLs via crawling")

        if not urls:
            self.logger.error("No URLs found to fetch")
            return

        # Apply filters
        if self.include_patterns or self.exclude_patterns:
            filtered_urls = []
            for url in urls:
                if self.include_patterns and not any(pattern in url for pattern in self.include_patterns):
                    continue
                if self.exclude_patterns and any(pattern in url for pattern in self.exclude_patterns):
                    continue
                filtered_urls.append(url)
            urls = set(filtered_urls)

        urls_list = sorted(urls)

        # Apply max_pages limit
        if self.max_pages:
            urls_list = urls_list[: self.max_pages]
            self.logger.info(f"Limited to {self.max_pages} pages")

        self.logger.info(f"Processing {len(urls_list)} URLs")

        # Process each URL
        total = len(urls_list)
        for idx, url in enumerate(urls_list, 1):
            self.logger.info(f"[{idx}/{total}] Processing: {url}")

            # Generic path creation
            parsed = urlparse(url)
            path = parsed.path.strip("/")
            if not path:
                path = "index"
            filepath = self.output_dir / self.output_subdir / f"{path.replace('/', '_')}.md"

            self.process_url(url, filepath)

        self.logger.info("Fetch complete")
        self.print_stats()
