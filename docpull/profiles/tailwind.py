"""Tailwind CSS documentation profile."""

from .base import SiteProfile

TAILWIND_PROFILE = SiteProfile(
    name="tailwind",
    domains={"tailwindcss.com"},
    sitemap_url="https://tailwindcss.com/sitemap.xml",
    base_url="https://tailwindcss.com/",
    include_patterns=["/docs/"],
    output_subdir="tailwind",
    strip_prefix="docs",
    rate_limit=0.2,
)
