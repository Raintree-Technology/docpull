"""Base class for site profiles."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SiteProfile:
    """
    Configuration profile for a documentation site.

    Defines site-specific settings for optimal scraping.
    """

    # Identification
    name: str
    domains: set[str]  # Domains this profile applies to

    # URL discovery
    sitemap_url: Optional[str] = None
    base_url: Optional[str] = None
    start_urls: list[str] = field(default_factory=list)  # Alternative to sitemap

    # URL filtering
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)

    # Content extraction
    content_selectors: list[str] = field(default_factory=lambda: ["main", "article", ".content"])
    remove_selectors: list[str] = field(
        default_factory=lambda: ["script", "style", "nav", "footer", "header"]
    )

    # File organization
    output_subdir: Optional[str] = None  # Subdirectory name (defaults to name)
    strip_prefix: Optional[str] = None  # URL prefix to remove from paths

    # Rate limiting
    rate_limit: float = 0.5  # Seconds between requests

    # Crawling behavior
    max_depth: int = 5  # Maximum link depth from start URLs
    max_pages: Optional[int] = None  # Maximum pages to fetch
    follow_links: bool = False  # Whether to follow links (vs sitemap only)

    def __post_init__(self) -> None:
        """Set defaults after initialization."""
        if self.output_subdir is None:
            self.output_subdir = self.name

    def matches_url(self, url: str) -> bool:
        """
        Check if this profile matches a given URL.

        Args:
            url: URL to check

        Returns:
            True if profile matches, False otherwise
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return parsed.netloc in self.domains
