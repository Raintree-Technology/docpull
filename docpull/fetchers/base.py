import hashlib
import ipaddress
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, TypedDict
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import html2text
import requests
from bs4 import BeautifulSoup
from defusedxml import ElementTree

from ..file_utils import clean_filename, ensure_dir, validate_output_path

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
        use_rich_metadata: bool = False,
        proxy: Optional[str] = None,
    ) -> None:
        self.output_dir = Path(output_dir).resolve()
        self.rate_limit = rate_limit
        self.skip_existing = skip_existing
        self.use_rich_metadata = use_rich_metadata
        # robots.txt is always respected (mandatory for TOS compliance)
        self.respect_robots = True
        self.proxy = proxy
        self.logger = logger or logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.allowed_domains = allowed_domains
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0
        self.session = requests.Session()
        self.session.max_redirects = self.MAX_REDIRECTS

        # Configure proxy if provided
        if self.proxy:
            self.session.proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            self.logger.info(f"Using proxy: {self.proxy}")

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
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (docpull/1.5)"
        self.user_agent = user_agent
        self.session.headers.update({"User-Agent": user_agent})

        # robots.txt cache: domain -> RobotFileParser
        self._robots_cache: dict[str, Optional[RobotFileParser]] = {}

        # Initialize rich metadata extractor if enabled
        self.rich_metadata_extractor = None
        if self.use_rich_metadata:
            from ..metadata_extractor import RichMetadataExtractor

            self.rich_metadata_extractor = RichMetadataExtractor()

        self.stats: FetcherStats = {
            "fetched": 0,
            "skipped": 0,
            "errors": 0,
        }

        # Content hash cache for change detection
        self._hash_cache_path = self.output_dir / ".docpull-hashes.json"
        self._content_hashes: dict[str, str] = self._load_hash_cache()

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

    def _load_hash_cache(self) -> dict[str, str]:
        """Load content hashes from cache file."""
        if self._hash_cache_path.exists():
            try:
                with open(self._hash_cache_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                self.logger.debug(f"Could not load hash cache: {e}")
        return {}

    def _save_hash_cache(self) -> None:
        """Save content hashes to cache file."""
        try:
            ensure_dir(self._hash_cache_path.parent)
            with open(self._hash_cache_path, "w", encoding="utf-8") as f:
                json.dump(self._content_hashes, f, indent=2)
            self.logger.debug(f"Saved hash cache with {len(self._content_hashes)} entries")
        except Exception as e:
            self.logger.warning(f"Could not save hash cache: {e}")

    def compute_content_hash(self, content: str) -> str:
        """
        Compute a SHA-256 hash of content for change detection.

        Args:
            content: String content to hash

        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def is_content_unchanged(self, url: str, content: str) -> bool:
        """
        Check if content has changed since last fetch.

        Args:
            url: URL that was fetched
            content: Current content

        Returns:
            True if content is unchanged, False if changed or new
        """
        current_hash = self.compute_content_hash(content)
        cached_hash = self._content_hashes.get(url)

        if cached_hash == current_hash:
            return True

        # Update hash cache
        self._content_hashes[url] = current_hash
        return False

    def _get_robots_parser(self, url: str) -> Optional[RobotFileParser]:
        """
        Get or create a RobotFileParser for the given URL's domain.

        Args:
            url: URL to get robots.txt parser for

        Returns:
            RobotFileParser instance or None if robots.txt couldn't be fetched
        """
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain in self._robots_cache:
            return self._robots_cache[domain]

        robots_url = f"{domain}/robots.txt"
        try:
            rp = RobotFileParser()
            rp.set_url(robots_url)

            # Fetch robots.txt with timeout
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                rp.parse(response.text.splitlines())
                self._robots_cache[domain] = rp
                self.logger.debug(f"Loaded robots.txt from {robots_url}")

                # Check for Crawl-delay directive
                crawl_delay = rp.crawl_delay(self.user_agent)
                if crawl_delay is not None:
                    delay_value = float(crawl_delay)
                    if delay_value > self.rate_limit:
                        self.logger.info(f"Respecting Crawl-delay: {delay_value}s (was {self.rate_limit}s)")
                        self.rate_limit = delay_value

                return rp
            else:
                # No robots.txt or error - allow everything
                self._robots_cache[domain] = None
                self.logger.debug(f"No robots.txt at {robots_url} (status {response.status_code})")
                return None

        except Exception as e:
            self.logger.debug(f"Could not fetch robots.txt from {robots_url}: {e}")
            self._robots_cache[domain] = None
            return None

    def is_allowed_by_robots(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt.

        robots.txt compliance is mandatory for TOS compliance.

        Args:
            url: URL to check

        Returns:
            True if URL is allowed, False if disallowed by robots.txt
        """
        rp = self._get_robots_parser(url)
        if rp is None:
            # No robots.txt or couldn't fetch it - allow everything
            return True

        allowed = rp.can_fetch(self.user_agent, url)
        if not allowed:
            self.logger.debug(f"Blocked by robots.txt: {url}")
        return allowed

    def get_sitemaps_from_robots(self, url: str) -> list[str]:
        """
        Extract sitemap URLs from robots.txt.

        Args:
            url: Any URL from the domain to check

        Returns:
            List of sitemap URLs found in robots.txt
        """
        rp = self._get_robots_parser(url)
        if rp is None:
            return []

        # RobotFileParser stores sitemaps
        sitemaps = list(rp.site_maps() or [])
        if sitemaps:
            self.logger.info(f"Found {len(sitemaps)} sitemap(s) in robots.txt")
        return sitemaps

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
            self.stats["errors"] += 1
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

            # Extract rich metadata if enabled
            rich_meta = None
            if self.use_rich_metadata and self.rich_metadata_extractor:
                try:
                    rich_meta = self.rich_metadata_extractor.extract(content.decode("utf-8"), url)
                except Exception as e:
                    self.logger.debug(f"Rich metadata extraction failed for {url}: {e}")

            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
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
                markdown = self.h2t.handle(str(main_content))

                # Build frontmatter with optional rich metadata
                frontmatter_parts = [
                    "---",
                    f"url: {url}",
                    f"fetched: {time.strftime('%Y-%m-%d')}",
                ]

                if rich_meta:
                    # Add rich metadata fields if available
                    if rich_meta.get("title"):
                        frontmatter_parts.append(f"title: {rich_meta['title']}")
                    if rich_meta.get("description"):
                        # Escape any colons in description
                        desc = str(rich_meta["description"]).replace(":", "\\:")
                        frontmatter_parts.append(f"description: {desc}")
                    if rich_meta.get("author"):
                        frontmatter_parts.append(f"author: {rich_meta['author']}")
                    if rich_meta.get("keywords"):
                        keywords = rich_meta["keywords"]
                        if keywords:
                            keywords_str = ", ".join(keywords)
                            frontmatter_parts.append(f"keywords: [{keywords_str}]")
                    if rich_meta.get("image"):
                        frontmatter_parts.append(f"image: {rich_meta['image']}")
                    if rich_meta.get("type"):
                        frontmatter_parts.append(f"type: {rich_meta['type']}")
                    if rich_meta.get("site_name"):
                        frontmatter_parts.append(f"site_name: {rich_meta['site_name']}")
                    if rich_meta.get("published_time"):
                        frontmatter_parts.append(f"published_time: {rich_meta['published_time']}")
                    if rich_meta.get("modified_time"):
                        frontmatter_parts.append(f"modified_time: {rich_meta['modified_time']}")
                    if rich_meta.get("section"):
                        frontmatter_parts.append(f"section: {rich_meta['section']}")
                    if rich_meta.get("tags"):
                        tags = rich_meta["tags"]
                        if tags:
                            tags_str = ", ".join(tags)
                            frontmatter_parts.append(f"tags: [{tags_str}]")

                frontmatter_parts.append("---")
                frontmatter_parts.append("")  # Empty line after frontmatter

                frontmatter = "\n".join(frontmatter_parts)
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

        # Check robots.txt
        if not self.is_allowed_by_robots(url):
            self.logger.info(f"Skipping (blocked by robots.txt): {url}")
            self.stats["skipped"] += 1
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
        """Print fetching statistics to log and save hash cache."""
        # Save hash cache for change detection
        self._save_hash_cache()

        self.logger.info("Fetching Statistics:")
        self.logger.info(f"  Fetched: {self.stats['fetched']}")
        self.logger.info(f"  Skipped: {self.stats['skipped']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")
        total = self.stats["fetched"] + self.stats["skipped"] + self.stats["errors"]
        self.logger.info(f"  Total: {total}")
