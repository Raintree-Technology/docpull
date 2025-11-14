"""Plaid documentation profile."""

from .base import SiteProfile

PLAID_PROFILE = SiteProfile(
    name="plaid",
    domains={"plaid.com"},
    sitemap_url="https://plaid.com/sitemap.xml",
    base_url="https://plaid.com/",
    start_urls=["https://plaid.com/docs/"],
    include_patterns=["/docs/", "/api/"],
    exclude_patterns=["/blog/", "/resources/", "/company/", "/customers/"],
    output_subdir="plaid",
    rate_limit=0.5,
    follow_links=True,  # Crawls links from start_urls in addition to sitemap
)
