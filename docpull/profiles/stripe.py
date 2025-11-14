"""Stripe documentation profile."""

from .base import SiteProfile

STRIPE_PROFILE = SiteProfile(
    name="stripe",
    domains={"docs.stripe.com", "stripe.com"},
    sitemap_url="https://docs.stripe.com/sitemap.xml",
    base_url="https://docs.stripe.com/",
    include_patterns=["https://docs.stripe.com/"],
    exclude_patterns=["/changelog/", "/upgrades/"],
    output_subdir="stripe",
    rate_limit=0.5,
)
