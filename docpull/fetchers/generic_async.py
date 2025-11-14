"""Async generic fetcher with progress bars and JS support."""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from ..profiles import SiteProfile, get_profile_by_name, get_profile_for_url
from .async_fetcher import PLAYWRIGHT_AVAILABLE, AsyncFetcher
from .base import BaseFetcher


class GenericAsyncFetcher(BaseFetcher):
    """
    Async generic fetcher with progress bars and optional JS rendering.

    Features:
    - Async/parallel fetching (10x+ faster)
    - Progress bars with rich
    - Optional JavaScript rendering
    - All security features from BaseFetcher
    """

    def __init__(
        self,
        url_or_profile: str,
        output_dir: Path,
        profile: Optional[SiteProfile] = None,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
        max_pages: Optional[int] = None,
        max_depth: int = 5,
        max_concurrent: int = 10,
        use_js: bool = False,
        show_progress: bool = True,
    ) -> None:
        """
        Initialize async generic fetcher.

        Args:
            url_or_profile: URL to scrape or profile name
            output_dir: Directory to save documentation
            profile: Optional SiteProfile
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            logger: Logger instance
            max_pages: Maximum pages to fetch
            max_depth: Maximum crawl depth
            max_concurrent: Maximum concurrent requests
            use_js: Enable JavaScript rendering (requires playwright)
            show_progress: Show progress bars
        """
        super().__init__(output_dir, rate_limit, skip_existing=skip_existing, logger=logger)

        # Determine if input is a URL or profile name
        if url_or_profile.startswith(("http://", "https://")):
            self.start_url = url_or_profile
            if profile is None:
                profile = get_profile_for_url(url_or_profile)
                if profile:
                    self.logger.info(f"Auto-detected profile: {profile.name}")
        else:
            profile = get_profile_by_name(url_or_profile)
            if profile is None:
                raise ValueError(f"Unknown profile: {url_or_profile}")
            start_url_candidate = profile.base_url or (profile.start_urls[0] if profile.start_urls else None)
            if not start_url_candidate:
                raise ValueError(f"Profile {url_or_profile} has no start URL")
            self.start_url = start_url_candidate
            self.logger.info(f"Using profile: {profile.name}")

        self.profile = profile
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.max_concurrent = max_concurrent
        self.use_js = use_js
        self.show_progress = show_progress

        # Set defaults from profile
        if profile:
            self.rate_limit = profile.rate_limit
            self.sitemap_url = profile.sitemap_url
            self.base_url = profile.base_url or self._extract_base_url(self.start_url)
            self.include_patterns = profile.include_patterns
            self.exclude_patterns = profile.exclude_patterns
            self.output_subdir = profile.output_subdir or urlparse(self.start_url).netloc.replace(".", "_")
            self.strip_prefix = profile.strip_prefix
            self.follow_links = profile.follow_links
        else:
            self.sitemap_url = self._guess_sitemap_url(self.start_url)
            self.base_url = self._extract_base_url(self.start_url)
            self.include_patterns = [self.base_url]
            self.exclude_patterns = []
            self.output_subdir = urlparse(self.start_url).netloc.replace(".", "_")
            self.strip_prefix = None
            self.follow_links = False

        if use_js and not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not installed. JS rendering disabled.")
            self.logger.warning(
                "Install with: pip install 'docpull[js]' && python -m playwright install chromium"
            )
            self.use_js = False

    def _extract_base_url(self, url: str) -> str:
        """Extract base URL from a full URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/"

    def _guess_sitemap_url(self, url: str) -> Optional[str]:
        """Guess sitemap URL for a given domain."""
        base = self._extract_base_url(url)
        common_paths = ["sitemap.xml", "sitemap_index.xml", "docs/sitemap.xml"]

        for path in common_paths:
            sitemap_url = urljoin(base, path)
            try:
                response = self.session.head(sitemap_url, timeout=10)
                if response.status_code == 200:
                    self.logger.info(f"Found sitemap: {sitemap_url}")
                    return sitemap_url
            except Exception:
                continue
        return None

    def _crawl_links(self, start_urls: set[str], max_depth: int = 5) -> set[str]:
        """Crawl links from start URLs (sync version for discovery)."""
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
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if not isinstance(href, str):
                        continue

                    absolute_url = urljoin(url, href)
                    absolute_url = absolute_url.split("#")[0].split("?")[0]

                    if not any(pattern in absolute_url for pattern in self.include_patterns):
                        continue
                    if any(pattern in absolute_url for pattern in self.exclude_patterns):
                        continue

                    if absolute_url not in visited:
                        to_visit.add((absolute_url, depth + 1))

            except Exception:
                continue

        return discovered

    def fetch(self) -> None:
        """Fetch documentation (sync wrapper for async method)."""
        asyncio.run(self.fetch_async())

    async def fetch_async(self) -> None:
        """Fetch documentation asynchronously with progress bars."""
        self.logger.info(f"Fetching documentation from {self.start_url}")

        urls: set[str] = set()

        # Discover URLs
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Discovering URLs...", total=None)

            # Try sitemap
            if self.sitemap_url:
                sitemap_urls = self.fetch_sitemap(self.sitemap_url)
                if sitemap_urls:
                    urls.update(sitemap_urls)
                    progress.update(task, description=f"Found {len(sitemap_urls)} URLs in sitemap")

            # Add start URLs
            if self.profile and self.profile.start_urls:
                urls.update(self.profile.start_urls)

            # Crawl links if needed
            if self.follow_links or (not urls and not self.sitemap_url):
                start_urls = {self.start_url}
                if self.profile and self.profile.start_urls:
                    start_urls.update(self.profile.start_urls)

                progress.update(task, description=f"Crawling links from {len(start_urls)} URL(s)...")
                crawled_urls = self._crawl_links(start_urls, self.max_depth)
                urls.update(crawled_urls)
                progress.update(task, description=f"Discovered {len(crawled_urls)} URLs via crawling")

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

        self.logger.info(f"Processing {len(urls_list)} URLs")

        # Prepare URL/path pairs
        url_output_pairs = []
        for url in urls_list:
            if self.profile and self.base_url:
                filepath = self.create_output_path(url, self.base_url, self.output_subdir, self.strip_prefix)
            else:
                parsed = urlparse(url)
                path = parsed.path.strip("/")
                if not path:
                    path = "index"
                filepath = self.output_dir / self.output_subdir / f"{path.replace('/', '_')}.md"
            url_output_pairs.append((url, filepath))

        # Fetch URLs with progress bar
        async with AsyncFetcher(
            base_fetcher=self,
            max_concurrent=self.max_concurrent,
            use_js=self.use_js,
        ) as async_fetcher:
            if self.show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                ) as progress:
                    task = progress.add_task(
                        f"Fetching {len(url_output_pairs)} pages...", total=len(url_output_pairs)
                    )

                    # Fetch with progress updates
                    for i in range(0, len(url_output_pairs), self.max_concurrent):
                        batch = url_output_pairs[i : i + self.max_concurrent]
                        await async_fetcher.fetch_urls_parallel(batch)
                        progress.update(task, completed=min(i + self.max_concurrent, len(url_output_pairs)))
            else:
                # Fetch without progress
                await async_fetcher.fetch_urls_parallel(url_output_pairs)

        self.logger.info("Fetch complete")
        self.print_stats()
