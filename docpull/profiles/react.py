"""React documentation profile."""

from .base import SiteProfile

REACT_PROFILE = SiteProfile(
    name="react",
    domains={"react.dev"},
    sitemap_url="https://react.dev/sitemap.xml",
    base_url="https://react.dev/",
    include_patterns=["/reference/", "/learn/"],
    exclude_patterns=["/blog/", "/community/"],
    output_subdir="react",
    rate_limit=0.2,  # React docs can handle faster requests
)
