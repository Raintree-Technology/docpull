"""Site profiles for documentation scraping."""

from typing import Optional

from .base import SiteProfile
from .bun import BUN_PROFILE
from .d3 import D3_PROFILE
from .nextjs import NEXTJS_PROFILE
from .plaid import PLAID_PROFILE
from .react import REACT_PROFILE
from .stripe import STRIPE_PROFILE
from .tailwind import TAILWIND_PROFILE
from .turborepo import TURBOREPO_PROFILE

# Registry of all available profiles
PROFILES = {
    "stripe": STRIPE_PROFILE,
    "plaid": PLAID_PROFILE,
    "nextjs": NEXTJS_PROFILE,
    "react": REACT_PROFILE,
    "tailwind": TAILWIND_PROFILE,
    "bun": BUN_PROFILE,
    "d3": D3_PROFILE,
    "turborepo": TURBOREPO_PROFILE,
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
    "PLAID_PROFILE",
    "NEXTJS_PROFILE",
    "REACT_PROFILE",
    "TAILWIND_PROFILE",
    "BUN_PROFILE",
    "D3_PROFILE",
    "TURBOREPO_PROFILE",
]
