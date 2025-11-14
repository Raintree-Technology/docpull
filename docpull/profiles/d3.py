"""D3.js documentation profile."""

from .base import SiteProfile

# Note: D3 fetcher uses devdocs.io API, not sitemap
# This profile is for generic URL scraping of D3 docs
D3_PROFILE = SiteProfile(
    name="d3",
    domains={"d3js.org", "devdocs.io"},
    base_url="https://d3js.org/",
    start_urls=["https://d3js.org/getting-started"],
    include_patterns=["/getting-started", "/d3-"],
    output_subdir="d3",
    rate_limit=0.5,
    follow_links=True,
    max_depth=3,
)
