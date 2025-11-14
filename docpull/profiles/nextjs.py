"""Next.js documentation profile."""

from .base import SiteProfile

NEXTJS_PROFILE = SiteProfile(
    name="nextjs",
    domains={"nextjs.org"},
    sitemap_url="https://nextjs.org/sitemap.xml",
    base_url="https://nextjs.org/",
    include_patterns=["/docs/"],
    exclude_patterns=["/blog/", "/showcase/", "/conf/", "/learn/"],
    output_subdir="next",
    strip_prefix="docs",
    rate_limit=0.5,
)
