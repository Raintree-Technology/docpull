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
        "Required dependencies not installed. " "Install with: pip install requests beautifulsoup4 html2text"
    ) from e

from ..utils.file_utils import ensure_dir, validate_output_path


class BaseFetcher(ABC):
    MAX_CONTENT_SIZE = 50 * 1024 * 1024
    MAX_REDIRECTS = 5
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
        allowed_domains: Optional[Set[str]] = None,
    ):
        self.output_dir = Path(output_dir).resolve()
        self.rate_limit = rate_limit
        self.skip_existing = skip_existing
        self.logger = logger or logging.getLogger("doc_fetcher")
        self.allowed_domains = allowed_domains
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0
        self.session = requests.Session()
        self.session.max_redirects = self.MAX_REDIRECTS
        if user_agent is None:
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        self.session.headers.update({"User-Agent": user_agent})
        self.stats = {
            "fetched": 0,
            "skipped": 0,
            "errors": 0,
        }

    def validate_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in self.ALLOWED_SCHEMES:
                self.logger.warning("Rejected non-HTTPS URL")
                return False
            if not parsed.netloc:
                self.logger.warning("Rejected URL with no domain")
                return False

            if self.allowed_domains is not None:
                if parsed.netloc not in self.allowed_domains:
                    self.logger.warning(f"Rejected domain not in allowlist: {parsed.netloc}")
                    return False

            if parsed.netloc.startswith("localhost") or parsed.netloc.startswith("127."):
                self.logger.warning("Rejected localhost URL")
                return False

            if any(parsed.netloc.startswith(prefix) for prefix in ["10.", "172.16.", "192.168."]):
                self.logger.warning("Rejected private IP address")
                return False

            return True
        except Exception:
            self.logger.warning("Invalid URL format")
            return False

    def fetch_sitemap(self, url: str) -> List[str]:
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
                parser = ET.XMLParser()
                parser.entity = {}
                root = ET.fromstring(content, parser=parser)
            except ET.ParseError as e:
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
        self, urls: List[str], include_patterns: List[str], exclude_patterns: Optional[List[str]] = None
    ) -> List[str]:
        exclude_patterns = exclude_patterns or []
        filtered = []

        for url in urls:
            if any(pattern in url for pattern in include_patterns):
                if not any(ex_pattern in url for ex_pattern in exclude_patterns):
                    filtered.append(url)

        self.logger.info(f"Filtered to {len(filtered)} URLs")
        return filtered

    def categorize_urls(self, urls: List[str], base_url: str) -> Dict[str, List[str]]:
        categories: Dict[str, List[str]] = {}

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

    def validate_content_type(self, content_type: str) -> bool:
        if not content_type:
            return True
        content_type_lower = content_type.lower().split(";")[0].strip()
        return content_type_lower in self.ALLOWED_CONTENT_TYPES

    def fetch_page_content(self, url: str) -> str:
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
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.MAX_CONTENT_SIZE:
                    return "# Error\n\nContent size limit exceeded"

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
        validated_path = validate_output_path(filepath, self.output_dir)
        ensure_dir(validated_path.parent)
        with open(validated_path, "w", encoding="utf-8") as f:
            f.write(content)

    def process_url(self, url: str, output_path: Path) -> bool:
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
        pass

    def print_stats(self) -> None:
        self.logger.info("=" * 80)
        self.logger.info("Fetching Statistics:")
        self.logger.info(f"  Fetched: {self.stats['fetched']}")
        self.logger.info(f"  Skipped: {self.stats['skipped']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")
        self.logger.info(f"  Total: {sum(self.stats.values())}")
        self.logger.info("=" * 80)
