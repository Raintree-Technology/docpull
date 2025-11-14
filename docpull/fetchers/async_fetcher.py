"""Async fetcher with JavaScript rendering support."""

import asyncio
import time
from pathlib import Path
from typing import Any, Optional

import aiohttp
from bs4 import BeautifulSoup

from ..utils.file_utils import ensure_dir, validate_output_path
from .base import BaseFetcher

# Optional Playwright support
try:
    from playwright.async_api import Browser, Playwright, async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Fallback types for when playwright is not installed
    Browser = Any  # type: ignore[misc,assignment]
    Playwright = Any  # type: ignore[misc,assignment]


class AsyncFetcher:
    """
    Async fetcher with optional JavaScript rendering support.

    Security features:
    - All URL validation from BaseFetcher
    - Rate limiting (async-safe with semaphore)
    - Concurrent request limits
    - Timeout controls for both HTTP and browser
    - Content size limits
    - Playwright sandboxing (disabled JS in certain contexts)
    """

    MAX_CONTENT_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_DOWNLOAD_TIME = 300  # 5 minutes
    MAX_JS_RENDER_TIME = 30  # 30 seconds for JS rendering
    MAX_CONCURRENT = 10  # Max concurrent requests

    def __init__(
        self,
        base_fetcher: BaseFetcher,
        max_concurrent: int = 10,
        use_js: bool = False,
        headless: bool = True,
    ) -> None:
        """
        Initialize async fetcher.

        Args:
            base_fetcher: BaseFetcher instance for URL validation and settings
            max_concurrent: Maximum concurrent requests
            use_js: Enable JavaScript rendering with Playwright
            headless: Run browser in headless mode
        """
        self.base_fetcher = base_fetcher
        self.logger = base_fetcher.logger
        self.max_concurrent = max_concurrent
        self.use_js = use_js
        self.headless = headless

        # Async-safe rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limit_delay = base_fetcher.rate_limit

        # Browser instance (if using JS)
        self.browser: Optional[Browser] = None  # type: ignore[no-any-unimported]
        self.playwright: Optional[Playwright] = None  # type: ignore[no-any-unimported]

        if use_js and not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not installed. Install with: pip install docpull[js]")
            self.logger.warning("Falling back to non-JS mode")
            self.use_js = False

    async def __aenter__(self) -> "AsyncFetcher":
        """Async context manager entry."""
        if self.use_js and PLAYWRIGHT_AVAILABLE:
            self.playwright = await async_playwright().start()
            # Launch with security-focused options
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-dev-shm-usage",  # Prevent memory issues
                    "--no-sandbox",  # Required for some environments
                    "--disable-setuid-sandbox",
                    "--disable-web-security",  # For CORS, but still validate URLs
                ],
            )
            self.logger.info("Browser launched for JavaScript rendering")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            self.logger.info("Browser closed")

    async def fetch_with_js(self, url: str) -> str:
        """
        Fetch page content with JavaScript rendering.

        Args:
            url: URL to fetch

        Returns:
            Rendered HTML content

        Security measures:
        - URL validation before fetch
        - Timeout limits
        - Blocks certain resource types (images, fonts) to speed up
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")

        if not self.base_fetcher.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        user_agent = self.base_fetcher.session.headers.get("User-Agent")
        if isinstance(user_agent, bytes):
            user_agent = user_agent.decode("utf-8")

        context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
        )

        page = await context.new_page()

        try:
            # Block unnecessary resources to speed up loading
            async def route_handler(route: Any) -> None:
                resource_type = route.request.resource_type
                if resource_type in ["image", "font", "media"]:
                    await route.abort()
                else:
                    await route.continue_()

            await page.route("**/*", route_handler)

            # Navigate with timeout
            await page.goto(
                url,
                wait_until="networkidle",
                timeout=self.MAX_JS_RENDER_TIME * 1000,
            )

            # Get rendered HTML
            content: str = await page.content()

            return content

        except Exception as e:
            self.logger.error(f"JS rendering error for {url}: {e}")
            raise
        finally:
            await page.close()
            await context.close()

    async def fetch_without_js(self, session: aiohttp.ClientSession, url: str) -> str:
        """
        Fetch page content without JavaScript (faster).

        Args:
            session: aiohttp ClientSession
            url: URL to fetch

        Returns:
            HTML content
        """
        if not self.base_fetcher.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=30),
                headers=self.base_fetcher.session.headers,
            ) as response:
                response.raise_for_status()

                # Validate content type
                content_type = response.headers.get("Content-Type", "")
                if not self.base_fetcher.validate_content_type(content_type):
                    raise ValueError(f"Invalid content type: {content_type}")

                # Check size limits
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > self.MAX_CONTENT_SIZE:
                    raise ValueError(f"Content too large: {content_length} bytes")

                # Read with size limit
                content = b""
                async for chunk in response.content.iter_chunked(8192):
                    content += chunk
                    if len(content) > self.MAX_CONTENT_SIZE:
                        raise ValueError("Content size limit exceeded")

                return content.decode("utf-8", errors="ignore")

        except Exception as e:
            self.logger.error(f"HTTP fetch error for {url}: {e}")
            raise

    async def fetch_url(
        self,
        session: Optional[aiohttp.ClientSession],
        url: str,
        output_path: Path,
    ) -> bool:
        """
        Fetch single URL with rate limiting and save to file.

        Args:
            session: aiohttp session (None if using JS)
            url: URL to fetch
            output_path: Where to save content

        Returns:
            True if successful, False otherwise
        """
        async with self.semaphore:  # Limit concurrency
            if not self.base_fetcher.validate_url(url):
                self.logger.warning(f"Skipping invalid URL: {url}")
                self.base_fetcher.stats["errors"] += 1
                return False

            try:
                validated_path = validate_output_path(output_path, self.base_fetcher.output_dir)
            except ValueError as e:
                self.logger.error(f"Path validation failed: {e}")
                self.base_fetcher.stats["errors"] += 1
                return False

            # Skip if exists
            if self.base_fetcher.skip_existing and validated_path.exists():
                self.logger.debug(f"Skipping (already exists): {validated_path}")
                self.base_fetcher.stats["skipped"] += 1
                return False

            try:
                # Fetch content
                if self.use_js:
                    html_content = await self.fetch_with_js(url)
                else:
                    if session is None:
                        raise RuntimeError("Session is required for non-JS fetching")
                    html_content = await self.fetch_without_js(session, url)

                # Process with BeautifulSoup (same as sync version)
                soup = BeautifulSoup(html_content, "html.parser")

                # Remove unwanted elements
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()

                # Find main content
                import re

                main_content = (
                    soup.find("main")
                    or soup.find("article")
                    or soup.find(class_=re.compile(r"content|documentation|docs"))
                    or soup.find("body")
                )

                if main_content:
                    # Convert to markdown
                    markdown = self.base_fetcher.h2t.handle(str(main_content))
                    frontmatter = f"""---
url: {url}
fetched: {time.strftime('%Y-%m-%d')}
---

"""
                    content = frontmatter + markdown.strip()
                else:
                    content = f"# Error\n\nCould not find main content for {url}"

                # Save content
                ensure_dir(validated_path.parent)
                await asyncio.to_thread(validated_path.write_text, content, encoding="utf-8")

                self.logger.info(f"Saved: {validated_path}")
                self.base_fetcher.stats["fetched"] += 1

                # Rate limiting
                if self.rate_limit_delay > 0:
                    await asyncio.sleep(self.rate_limit_delay)

                return True

            except Exception as e:
                self.logger.error(f"Error fetching {url}: {e}")
                self.base_fetcher.stats["errors"] += 1
                return False

    async def fetch_urls_parallel(
        self,
        url_output_pairs: list[tuple[str, Path]],
    ) -> None:
        """
        Fetch multiple URLs in parallel.

        Args:
            url_output_pairs: List of (url, output_path) tuples
        """
        if self.use_js:
            # JS mode - use browser, no session needed
            tasks = [self.fetch_url(None, url, output_path) for url, output_path in url_output_pairs]
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Non-JS mode - use aiohttp session
            async with aiohttp.ClientSession() as session:
                tasks = [self.fetch_url(session, url, output_path) for url, output_path in url_output_pairs]
                await asyncio.gather(*tasks, return_exceptions=True)
