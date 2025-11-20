"""Site profiles for documentation scraping.

docpull includes a built-in Stripe profile as a reference implementation.
Users can create custom profiles for other sites or contribute to the community.
"""

from typing import Optional

from .base import SiteProfile
from .stripe import STRIPE_PROFILE

# Registry of all available profiles
PROFILES = {
    "stripe": STRIPE_PROFILE,
}


def get_profile_for_url(url: str) -> Optional[SiteProfile]:
    """
    Find a matching profile for a given URL.

    Args:
        url: URL to match against profiles

    Returns:
        Matching SiteProfile or None if no match
    """
    for profile in PROFILES.values():
        if profile.matches_url(url):
            return profile
    return None


def get_profile_by_name(name: str) -> Optional[SiteProfile]:
    """
    Get a profile by name.

    Args:
        name: Profile name (e.g., 'stripe', 'plaid')

    Returns:
        SiteProfile or None if not found
    """
    return PROFILES.get(name.lower())


__all__ = [
    "SiteProfile",
    "PROFILES",
    "get_profile_for_url",
    "get_profile_by_name",
    "STRIPE_PROFILE",
]
