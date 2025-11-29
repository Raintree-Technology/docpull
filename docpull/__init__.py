__version__ = "1.5.0"

from .fetchers.base import BaseFetcher
from .fetchers.generic import GenericFetcher
from .fetchers.generic_async import GenericAsyncFetcher
from .fetchers.parallel_base import ParallelFetcher

__all__ = [
    "BaseFetcher",
    "GenericFetcher",
    "GenericAsyncFetcher",
    "ParallelFetcher",
]
