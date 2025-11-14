"""Parallel/concurrent base fetcher for faster downloads."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from .base import BaseFetcher


class ParallelFetcher(BaseFetcher):
    """
    Enhanced fetcher with parallel/concurrent downloads.

    Uses ThreadPoolExecutor for concurrent HTTP requests.
    Much faster than sequential fetching.
    """

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
        max_workers: int = 10,
    ) -> None:
        """
        Initialize parallel fetcher.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests (per worker)
            skip_existing: Skip existing files
            logger: Logger instance
            max_workers: Number of concurrent workers (default: 10)
        """
        super().__init__(output_dir, rate_limit, None, skip_existing, logger)
        self.max_workers = max_workers

    def process_url_with_metadata(self, url_data: tuple[str, Path]) -> tuple[bool, str]:
        """
        Process a single URL with metadata.

        Args:
            url_data: Tuple of (url, output_path)

        Returns:
            Tuple of (success, url)
        """
        url, output_path = url_data
        try:
            success = self.process_url(url, output_path)
            return (success, url)
        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
            self.stats["errors"] += 1
            return (False, url)

    def fetch_urls_parallel(self, url_output_pairs: list[tuple[str, Path]]) -> None:
        """
        Fetch URLs in parallel.

        Args:
            url_output_pairs: List of (url, output_path) tuples
        """
        total = len(url_output_pairs)
        self.logger.info(f"Fetching {total} URLs with {self.max_workers} workers...")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.process_url_with_metadata, url_data): url_data
                for url_data in url_output_pairs
            }

            # Process as they complete
            for completed, future in enumerate(as_completed(futures), start=1):
                success, url = future.result()

                if completed % 10 == 0 or completed == total:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    self.logger.info(
                        f"Progress: {completed}/{total} "
                        f"({completed*100//total}%) "
                        f"- {rate:.1f} docs/sec"
                    )

        elapsed = time.time() - start_time
        self.logger.info(f"Completed in {elapsed:.1f}s " f"({total/elapsed:.1f} docs/sec average)")
