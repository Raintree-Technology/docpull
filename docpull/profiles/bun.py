"""Bun documentation profile."""

from .base import SiteProfile

BUN_PROFILE = SiteProfile(
    name="bun",
    domains={"bun.sh"},
    sitemap_url="https://bun.sh/sitemap.xml",
    base_url="https://bun.sh/",
    include_patterns=["/docs/"],
    output_subdir="bun",
    strip_prefix="docs",
    rate_limit=0.2,
)
