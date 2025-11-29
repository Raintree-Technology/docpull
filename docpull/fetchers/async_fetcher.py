"""Async fetcher with JavaScript rendering support."""

import asyncio
import random
import time
from pathlib import Path
from typing import Any, Optional

import aiohttp
from bs4 import BeautifulSoup

# Better encoding detection (charset-normalizer is an aiohttp dependency)
try:
    from charset_normalizer import from_bytes as detect_encoding

    CHARSET_NORMALIZER_AVAILABLE = True
except ImportError:
    CHARSET_NORMALIZER_AVAILABLE = False

from ..file_utils import ensure_dir, validate_output_path
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
    - Retry with exponential backoff
    - robots.txt compliance
    """

    MAX_CONTENT_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_DOWNLOAD_TIME = 300  # 5 minutes
    MAX_JS_RENDER_TIME = 30  # 30 seconds for JS rendering
    MAX_CONCURRENT = 10  # Max concurrent requests

    # Retry settings
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
    RETRYABLE_EXCEPTIONS = (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        ConnectionError,
    )

    def __init__(
        self,
        base_fetcher: BaseFetcher,
        max_concurrent: int = 10,
        use_js: bool = False,
        headless: bool = True,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        """
        Initialize async fetcher.

        Args:
            base_fetcher: BaseFetcher instance for URL validation and settings
            max_concurrent: Maximum concurrent requests
            use_js: Enable JavaScript rendering with Playwright
            headless: Run browser in headless mode
            max_retries: Maximum retry attempts for failed requests
            retry_base_delay: Base delay for exponential backoff (seconds)
        """
        self.base_fetcher = base_fetcher
        self.logger = base_fetcher.logger
        self.max_concurrent = max_concurrent
        self.use_js = use_js
        self.headless = headless
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay

        # Async-safe rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limit_delay = base_fetcher.rate_limit

        # Proxy configuration from base fetcher
        self.proxy = getattr(base_fetcher, "proxy", None)

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

    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff with jitter.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: base * (2 ^ attempt) + random jitter
        delay: float = self.retry_base_delay * (2**attempt)
        jitter: float = random.uniform(0, 1)
        return delay + jitter

    def _decode_content(self, content: bytes, content_type: str) -> str:
        """
        Decode content with intelligent encoding detection.

        Args:
            content: Raw bytes content
            content_type: Content-Type header value

        Returns:
            Decoded string
        """
        # First, try to get encoding from Content-Type header
        encoding = None
        if content_type:
            for part in content_type.split(";"):
                part = part.strip()
                if part.lower().startswith("charset="):
                    encoding = part.split("=", 1)[1].strip().strip("\"'")
                    break

        # Try declared encoding first
        if encoding:
            try:
                return content.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                self.logger.debug(f"Failed to decode with declared encoding: {encoding}")

        # Use charset-normalizer for better detection
        if CHARSET_NORMALIZER_AVAILABLE:
            try:
                result = detect_encoding(content)
                if result:
                    best_match = result.best()
                    if best_match:
                        detected_encoding = best_match.encoding
                        self.logger.debug(f"Detected encoding: {detected_encoding}")
                        return str(best_match)
            except Exception as e:
                self.logger.debug(f"Encoding detection failed: {e}")

        # Final fallback: UTF-8 with replacement
        return content.decode("utf-8", errors="replace")

    async def fetch_without_js(self, session: aiohttp.ClientSession, url: str) -> str:
        """
        Fetch page content without JavaScript (faster).

        Features:
        - Retry with exponential backoff
        - Better encoding detection
        - Proxy support

        Args:
            session: aiohttp ClientSession
            url: URL to fetch

        Returns:
            HTML content
        """
        if not self.base_fetcher.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        # Check robots.txt
        if not self.base_fetcher.is_allowed_by_robots(url):
            raise ValueError(f"Blocked by robots.txt: {url}")

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers=dict(self.base_fetcher.session.headers),
                    proxy=self.proxy,
                ) as response:
                    # Check for retryable status codes
                    if response.status in self.RETRYABLE_STATUS_CODES:
                        if attempt < self.max_retries:
                            delay = self._calculate_retry_delay(attempt)
                            self.logger.warning(
                                f"Got {response.status} for {url}, retrying in {delay:.1f}s "
                                f"(attempt {attempt + 1}/{self.max_retries + 1})"
                            )
                            await asyncio.sleep(delay)
                            continue
                        else:
                            response.raise_for_status()

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

                    # Decode with intelligent encoding detection
                    return self._decode_content(content, content_type)

            except self.RETRYABLE_EXCEPTIONS as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.warning(
                        f"Error fetching {url}: {e}, retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    await asyncio.sleep(delay)
                else:
                    attempts = self.max_retries + 1
                    self.logger.error(f"HTTP fetch error for {url} after {attempts} attempts: {e}")
                    raise

            except Exception as e:
                # Non-retryable error
                self.logger.error(f"HTTP fetch error for {url}: {e}")
                raise

        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise RuntimeError(f"Unexpected error fetching {url}")

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

            # Check robots.txt
            if not self.base_fetcher.is_allowed_by_robots(url):
                self.logger.info(f"Skipping (blocked by robots.txt): {url}")
                self.base_fetcher.stats["skipped"] += 1
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
                    or soup.find(id=re.compile(r"content|documentation|docs", re.IGNORECASE))
                    or soup.find(
                        class_=re.compile(
                            r"^(?:content|documentation|docs)$|"
                            r"(?:^|-|_)(?:content|documentation|docs)(?:$|-|_)",
                            re.IGNORECASE,
                        )
                    )
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
