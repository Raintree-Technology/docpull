"""Turborepo documentation profile."""

from .base import SiteProfile

TURBOREPO_PROFILE = SiteProfile(
    name="turborepo",
    domains={"turborepo.com", "turbo.build"},
    sitemap_url="https://turbo.build/repo/sitemap.xml",
    base_url="https://turbo.build/repo/",
    include_patterns=["/docs/"],
    output_subdir="turborepo",
    strip_prefix="docs",
    rate_limit=0.2,
)
