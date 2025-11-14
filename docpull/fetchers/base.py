import ipaddress
import logging
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, TypedDict
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup
from defusedxml import ElementTree

from ..utils.file_utils import clean_filename, ensure_dir, validate_output_path

# Validate dependencies at module load
try:
    # Validate BeautifulSoup parser is available
    BeautifulSoup("<html></html>", "html.parser")
except Exception as e:
    raise ImportError(f"html.parser not available for BeautifulSoup: {e}") from e


class FetcherStats(TypedDict):
    """Statistics for documentation fetching operations."""

    fetched: int
    skipped: int
    errors: int


class BaseFetcher(ABC):
    """
    Abstract base class for documentation fetchers.

    Provides common functionality for fetching, validating, and converting
    documentation from various sources to markdown format.
    """

    MAX_CONTENT_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_REDIRECTS = 5
    MAX_DOWNLOAD_TIME = 300  # 5 minutes
    ALLOWED_SCHEMES = {"https"}
    ALLOWED_CONTENT_TYPES = {
        "text/html",
        "application/xhtml+xml",
        "text/xml",
        "application/xml",
        "application/atom+xml",
        "application/rss+xml",
    }

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        user_agent: Optional[str] = None,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
        allowed_domains: Optional[set[str]] = None,
    ) -> None:
        self.output_dir = Path(output_dir).resolve()
        self.rate_limit = rate_limit
        self.skip_existing = skip_existing
        self.logger = logger or logging.getLogger("docpull")
        self.allowed_domains = allowed_domains
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0
        self.session = requests.Session()
        self.session.max_redirects = self.MAX_REDIRECTS

        # Configure custom adapter to validate redirect URLs
        from typing import Any, Callable

        from requests.adapters import HTTPAdapter
        from requests.models import PreparedRequest, Response

        class SafeHTTPAdapter(HTTPAdapter):
            def __init__(self, validator_func: Callable[[str], bool], *args: Any, **kwargs: Any) -> None:
                self.validator_func = validator_func
                super().__init__(*args, **kwargs)

            def send(self, request: PreparedRequest, **kwargs: Any) -> Response:  # type: ignore[override]
                if request.url is None:
                    raise ValueError("Request URL is None")
                if not self.validator_func(request.url):
                    raise ValueError(f"Redirect to unsafe URL blocked: {request.url}")
                return super().send(request, **kwargs)

        adapter = SafeHTTPAdapter(self.validate_url)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        if user_agent is None:
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        self.session.headers.update({"User-Agent": user_agent})
        self.stats: FetcherStats = {
            "fetched": 0,
            "skipped": 0,
            "errors": 0,
        }

    def validate_url(self, url: str) -> bool:
        """
        Validate URL for security and allowed schemes.

        Args:
            url: URL to validate

        Returns:
            True if URL is safe to fetch, False otherwise
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in self.ALLOWED_SCHEMES:
                self.logger.warning("Rejected non-HTTPS URL")
                return False
            if not parsed.netloc:
                self.logger.warning("Rejected URL with no domain")
                return False

            if self.allowed_domains is not None and parsed.netloc not in self.allowed_domains:
                self.logger.warning(f"Rejected domain not in allowlist: {parsed.netloc}")
                return False

            # Extract hostname (remove port if present)
            hostname = parsed.netloc.split(":")[0]

            # Check for localhost
            if hostname.lower() in ["localhost", "localhost.localdomain"]:
                self.logger.warning("Rejected localhost URL")
                return False

            # Check for internal domain suffixes
            if hostname.lower().endswith(".internal") or hostname.lower().endswith(".local"):
                self.logger.warning("Rejected internal domain")
                return False

            # Try to parse as IP address
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    self.logger.warning(f"Rejected private/internal IP: {hostname}")
                    return False
            except ValueError:
                # Not an IP address, it's a domain name - this is fine
                pass

            return True
        except Exception:
            self.logger.warning("Invalid URL format")
            return False

    def fetch_sitemap(self, url: str) -> list[str]:
        self.logger.info(f"Fetching sitemap: {url}")
        if not self.validate_url(url):
            return []

        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_CONTENT_SIZE:
                self.logger.error(f"Sitemap too large: {content_length} bytes")
                return []

            content = response.content
            if len(content) > self.MAX_CONTENT_SIZE:
                self.logger.error(f"Sitemap exceeded size limit: {len(content)} bytes")
                return []

            try:
                # Parse XML (limited by MAX_CONTENT_SIZE for security)
                root = ElementTree.fromstring(content)
            except ElementTree.ParseError as e:
                self.logger.error(f"XML parsing error (possible XXE/bomb): {e}")
                return []
            namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = []
            for url_elem in root.findall(".//ns:url/ns:loc", namespace):
                if url_elem.text:
                    urls.append(url_elem.text)

            if not urls:
                for url_elem in root.findall(".//url/loc"):
                    if url_elem.text:
                        urls.append(url_elem.text)

            sitemap_urls = []
            for sitemap_elem in root.findall(".//ns:sitemap/ns:loc", namespace):
                if sitemap_elem.text:
                    sitemap_urls.append(sitemap_elem.text)

            if not sitemap_urls:
                for sitemap_elem in root.findall(".//sitemap/loc"):
                    if sitemap_elem.text:
                        sitemap_urls.append(sitemap_elem.text)

            for sitemap_url in sitemap_urls:
                self.logger.info(f"Found sub-sitemap: {sitemap_url}")
                urls.extend(self.fetch_sitemap(sitemap_url))

            self.logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls

        except Exception as e:
            self.logger.error(f"Error fetching sitemap {url}: {e}")
            return []

    def filter_urls(
        self, urls: list[str], include_patterns: list[str], exclude_patterns: Optional[list[str]] = None
    ) -> list[str]:
        """
        Filter URLs based on include and exclude patterns.

        Args:
            urls: List of URLs to filter
            include_patterns: Patterns that URLs must contain
            exclude_patterns: Patterns that URLs must not contain

        Returns:
            Filtered list of URLs
        """
        exclude_patterns = exclude_patterns or []
        filtered = []

        for url in urls:
            if any(pattern in url for pattern in include_patterns) and not any(
                ex_pattern in url for ex_pattern in exclude_patterns
            ):
                filtered.append(url)

        self.logger.info(f"Filtered to {len(filtered)} URLs")
        return filtered

    def categorize_urls(self, urls: list[str], base_url: str) -> dict[str, list[str]]:
        """
        Categorize URLs by their first path segment.

        Args:
            urls: List of URLs to categorize
            base_url: Base URL to strip from paths

        Returns:
            Dictionary mapping category names to lists of URLs
        """
        categories: dict[str, list[str]] = {}

        for url in urls:
            path = url.replace(base_url, "").strip("/")

            if not path:
                continue

            parts = path.split("/")
            if len(parts) > 0:
                category = parts[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(url)

        return categories

    def create_output_path(
        self, url: str, base_url: str, output_subdir: str, strip_prefix: Optional[str] = None
    ) -> Path:
        """
        Create standardized output path for a documentation URL.

        Args:
            url: The URL to process
            base_url: Base URL to strip from the path
            output_subdir: Subdirectory name (e.g., 'react', 'nextjs')
            strip_prefix: Optional prefix to remove (e.g., 'docs')

        Returns:
            Path object for where to save the content
        """
        # Remove base URL and create path structure
        path = url.replace(base_url, "").strip("/")
        parts = path.split("/")

        # Remove prefix if specified
        if strip_prefix and parts and parts[0] == strip_prefix:
            parts = parts[1:]

        # Create directory structure
        if len(parts) >= 2:
            category_dir = self.output_dir / output_subdir / "/".join(parts[:-1])
        elif len(parts) == 1:
            category_dir = self.output_dir / output_subdir
        else:
            category_dir = self.output_dir / output_subdir / "other"

        # Generate filename
        filename = clean_filename(url, base_url)
        filepath = category_dir / filename

        return filepath

    def validate_content_type(self, content_type: str) -> bool:
        """
        Validate HTTP content type header.

        Args:
            content_type: Content-Type header value

        Returns:
            True if content type is allowed, False otherwise
        """
        if not content_type:
            return True
        content_type_lower = content_type.lower().split(";")[0].strip()
        return content_type_lower in self.ALLOWED_CONTENT_TYPES

    def fetch_page_content(self, url: str) -> str:
        """
        Fetch and convert a webpage to markdown.

        Args:
            url: URL to fetch

        Returns:
            Markdown content with frontmatter, or error message
        """
        if not self.validate_url(url):
            return "# Error\n\nInvalid URL"

        try:
            self.logger.debug(f"Fetching: {url}")
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if not self.validate_content_type(content_type):
                self.logger.warning(f"Invalid content-type: {content_type}")
                return "# Error\n\nInvalid content type"

            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_CONTENT_SIZE:
                return "# Error\n\nContent too large"

            content = b""
            download_start = time.time()

            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.MAX_CONTENT_SIZE:
                    return "# Error\n\nContent size limit exceeded"
                if time.time() - download_start > self.MAX_DOWNLOAD_TIME:
                    return "# Error\n\nDownload timeout exceeded"

            soup = BeautifulSoup(content, "html.parser")

            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find(class_=re.compile(r"content|documentation|docs"))
                or soup.find("body")
            )

            if main_content:
                markdown = self.h2t.handle(str(main_content))
                frontmatter = f"""---
url: {url}
fetched: {time.strftime('%Y-%m-%d')}
---

"""
                return frontmatter + markdown.strip()
            else:
                return f"# Error\n\nCould not find main content for {url}"

        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            self.stats["errors"] += 1
            return f"# Error\n\nFailed to fetch {url}\n\nError: {str(e)}"

    def save_content(self, content: str, filepath: Path) -> None:
        """
        Save content to a file after validation.

        Args:
            content: The content to write
            filepath: Path where content should be saved
        """
        validated_path = validate_output_path(filepath, self.output_dir)
        ensure_dir(validated_path.parent)
        with open(validated_path, "w", encoding="utf-8") as f:
            f.write(content)

    def process_url(self, url: str, output_path: Path) -> bool:
        """
        Process a single URL: fetch, convert, and save.

        Args:
            url: URL to process
            output_path: Path where content should be saved

        Returns:
            True if successful, False otherwise
        """
        if not self.validate_url(url):
            self.logger.warning(f"Skipping invalid URL: {url}")
            self.stats["errors"] += 1
            return False

        try:
            validated_path = validate_output_path(output_path, self.output_dir)
        except ValueError as e:
            self.logger.error(f"Path validation failed: {e}")
            self.stats["errors"] += 1
            return False

        if self.skip_existing and validated_path.exists():
            self.logger.debug(f"Skipping (already exists): {validated_path}")
            self.stats["skipped"] += 1
            return False

        content = self.fetch_page_content(url)
        self.save_content(content, validated_path)

        self.logger.info(f"Saved: {validated_path}")
        self.stats["fetched"] += 1
        time.sleep(self.rate_limit)

        return True

    @abstractmethod
    def fetch(self) -> None:
        """Fetch all documentation for this source."""
        pass

    def print_stats(self) -> None:
        """Print fetching statistics to log."""
        self.logger.info("Fetching Statistics:")
        self.logger.info(f"  Fetched: {self.stats['fetched']}")
        self.logger.info(f"  Skipped: {self.stats['skipped']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")
        total = self.stats["fetched"] + self.stats["skipped"] + self.stats["errors"]
        self.logger.info(f"  Total: {total}")
