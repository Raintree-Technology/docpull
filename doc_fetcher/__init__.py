"""
Doc Fetcher - A flexible documentation fetching and conversion tool.

Supports fetching documentation from various sources via sitemaps,
converting HTML to markdown, and organizing content by category.
"""

__version__ = "1.0.0"

from .fetchers.base import BaseFetcher
from .fetchers.parallel_base import ParallelFetcher
from .fetchers.stripe import StripeFetcher
from .fetchers.plaid import PlaidFetcher
from .fetchers.nextjs import NextJSFetcher
from .fetchers.d3_devdocs import D3DevDocsFetcher
from .fetchers.bun import BunFetcher
from .fetchers.tailwind import TailwindFetcher
from .fetchers.react import ReactFetcher

__all__ = [
    "BaseFetcher",
    "ParallelFetcher",
    "StripeFetcher",
    "PlaidFetcher",
    "NextJSFetcher",
    "D3DevDocsFetcher",
    "BunFetcher",
    "TailwindFetcher",
    "ReactFetcher",
]
