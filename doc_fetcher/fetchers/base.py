"""Base documentation fetcher class."""

import logging
import re
import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    import html2text
except ImportError as e:
    raise ImportError(
        "Required dependencies not installed. "
        "Install with: pip install requests beautifulsoup4 html2text"
    ) from e

from ..utils.file_utils import clean_filename, ensure_dir


class BaseFetcher(ABC):
    """
    Base class for documentation fetchers.

    Provides common functionality for fetching sitemaps, converting HTML to markdown,
    and organizing documentation files.
    """

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        user_agent: Optional[str] = None,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the fetcher.

        Args:
            output_dir: Directory to save fetched documentation
            rate_limit: Seconds to wait between requests
            user_agent: Custom user agent string
            skip_existing: Skip files that already exist
            logger: Logger instance (creates one if not provided)
        """
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.skip_existing = skip_existing
        self.logger = logger or logging.getLogger("doc_fetcher")

        # Setup HTML to markdown converter
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # Don't wrap text

        # Setup HTTP session
        self.session = requests.Session()
        if user_agent is None:
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        # Ensure user_agent is a string
        if isinstance(user_agent, str):
            self.session.headers.update({"User-Agent": user_agent})

        # Statistics
        self.stats = {
            "fetched": 0,
            "skipped": 0,
            "errors": 0,
        }

    def fetch_sitemap(self, url: str) -> List[str]:
        """
        Fetch and parse XML sitemap.

        Args:
            url: Sitemap URL

        Returns:
            List of URLs from sitemap
        """
        self.logger.info(f"Fetching sitemap: {url}")
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Handle namespace
            namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Extract all URLs
            urls = []
            for url_elem in root.findall(".//ns:url/ns:loc", namespace):
                if url_elem.text:
                    urls.append(url_elem.text)

            # If no namespace, try without
            if not urls:
                for url_elem in root.findall(".//url/loc"):
                    if url_elem.text:
                        urls.append(url_elem.text)

            # Check for sitemap index (recursive sitemaps)
            sitemap_urls = []
            for sitemap_elem in root.findall(".//ns:sitemap/ns:loc", namespace):
                if sitemap_elem.text:
                    sitemap_urls.append(sitemap_elem.text)

            if not sitemap_urls:
                for sitemap_elem in root.findall(".//sitemap/loc"):
                    if sitemap_elem.text:
                        sitemap_urls.append(sitemap_elem.text)

            # Recursively fetch sub-sitemaps
            for sitemap_url in sitemap_urls:
                self.logger.info(f"Found sub-sitemap: {sitemap_url}")
                urls.extend(self.fetch_sitemap(sitemap_url))

            self.logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls

        except Exception as e:
            self.logger.error(f"Error fetching sitemap {url}: {e}")
            return []

    def filter_urls(
        self, urls: List[str], include_patterns: List[str], exclude_patterns: Optional[List[str]] = None
    ) -> List[str]:
        """
        Filter URLs by patterns.

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
            # Check if URL matches any include pattern
            if any(pattern in url for pattern in include_patterns):
                # Check if URL doesn't match any exclude pattern
                if not any(ex_pattern in url for ex_pattern in exclude_patterns):
                    filtered.append(url)

        self.logger.info(f"Filtered to {len(filtered)} URLs")
        return filtered

    def categorize_urls(self, urls: List[str], base_url: str) -> Dict[str, List[str]]:
        """
        Categorize URLs based on their path structure.

        Args:
            urls: List of URLs
            base_url: Base URL to strip

        Returns:
            Dictionary mapping categories to URL lists
        """
        categories = {}

        for url in urls:
            # Remove base URL and parse path
            path = url.replace(base_url, "").strip("/")

            if not path:
                continue

            # Get the first path segment as category
            parts = path.split("/")
            if len(parts) > 0:
                category = parts[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(url)

        return categories

    def fetch_page_content(self, url: str) -> str:
        """
        Fetch a single page and convert to markdown.

        Args:
            url: Page URL

        Returns:
            Markdown content with frontmatter
        """
        try:
            self.logger.debug(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Try to find main content area
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find(class_=re.compile(r"content|documentation|docs"))
                or soup.find("body")
            )

            if main_content:
                # Convert to markdown
                markdown = self.h2t.handle(str(main_content))

                # Add frontmatter
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
        Save content to file.

        Args:
            content: Content to save
            filepath: File path
        """
        ensure_dir(filepath.parent)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def process_url(self, url: str, output_path: Path) -> bool:
        """
        Process a single URL: fetch, convert, and save.

        Args:
            url: URL to process
            output_path: Path to save the file

        Returns:
            True if processed successfully, False if skipped or error
        """
        # Skip if already exists
        if self.skip_existing and output_path.exists():
            self.logger.debug(f"Skipping (already exists): {output_path}")
            self.stats["skipped"] += 1
            return False

        # Fetch and save
        content = self.fetch_page_content(url)
        self.save_content(content, output_path)

        self.logger.info(f"Saved: {output_path}")
        self.stats["fetched"] += 1

        # Rate limiting
        time.sleep(self.rate_limit)

        return True

    @abstractmethod
    def fetch(self) -> None:
        """
        Fetch all documentation for this source.

        Must be implemented by subclasses.
        """
        pass

    def print_stats(self) -> None:
        """Print fetching statistics."""
        self.logger.info("=" * 80)
        self.logger.info("Fetching Statistics:")
        self.logger.info(f"  Fetched: {self.stats['fetched']}")
        self.logger.info(f"  Skipped: {self.stats['skipped']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")
        self.logger.info(f"  Total: {sum(self.stats.values())}")
        self.logger.info("=" * 80)
