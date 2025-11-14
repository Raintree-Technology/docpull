"""D3.js documentation fetcher from DevDocs.io."""

import logging
import re
import time
from pathlib import Path
from typing import Any, Optional, cast

from .parallel_base import ParallelFetcher


class D3DevDocsFetcher(ParallelFetcher):
    """Fetcher for D3.js documentation from DevDocs.io."""

    def __init__(
        self,
        output_dir: Path,
        rate_limit: float = 0.05,  # DevDocs can handle faster requests
        skip_existing: bool = True,
        logger: Optional[logging.Logger] = None,
        max_workers: int = 20,  # More workers for DevDocs
        version: str = "7",  # D3 version
    ) -> None:
        """
        Initialize D3 DevDocs fetcher.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests (per worker)
            skip_existing: Skip existing files
            logger: Logger instance
            max_workers: Number of concurrent workers
            version: D3 version (default: 7 for latest)
        """
        super().__init__(output_dir, rate_limit, skip_existing, logger, max_workers)
        self.version = version
        self.doc_slug = f"d3~{version}"
        self.base_url = "https://devdocs.io/"
        self.api_base = "https://documents.devdocs.io/"
        self.index_url = f"{self.api_base}{self.doc_slug}/index.json"

    def fetch_index(self) -> list[dict[Any, Any]]:
        """
        Fetch the documentation index from DevDocs API.

        Returns:
            List of entry dictionaries
        """
        self.logger.info(f"Fetching D3 v{self.version} index from DevDocs")

        try:
            response = self.session.get(self.index_url, timeout=30)
            response.raise_for_status()

            data = response.json()
            entries = cast(list[dict[Any, Any]], data.get("entries", []))

            self.logger.info(f"Found {len(entries)} D3 documentation entries")
            return entries

        except Exception as e:
            self.logger.error(f"Error fetching index: {e}")
            return []

    def fetch_entry_content(self, entry: dict) -> str:
        """
        Fetch content for a single entry from DevDocs.

        Args:
            entry: Entry dictionary with 'path' key

        Returns:
            Markdown content with frontmatter
        """
        path = entry["path"]
        url = f"{self.api_base}{self.doc_slug}/{path}.html"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # DevDocs returns HTML, convert to markdown
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.content, "html.parser")

            # Convert to markdown
            markdown = self.h2t.handle(str(soup))

            # Add frontmatter
            frontmatter = f"""---
name: {entry.get('name', '')}
type: {entry.get('type', '')}
path: {path}
source: DevDocs.io - D3.js v{self.version}
url: {self.base_url}d3~{self.version}/{path}
fetched: {time.strftime('%Y-%m-%d')}
---

"""
            return frontmatter + markdown.strip()

        except Exception as e:
            self.logger.error(f"Error fetching {path}: {e}")
            self.stats["errors"] += 1
            return f"# Error\n\nFailed to fetch {path}\n\nError: {str(e)}"

    def process_entry(self, entry_data: tuple[dict, Path]) -> tuple[bool, str]:
        """
        Process a single entry.

        Args:
            entry_data: Tuple of (entry, output_path)

        Returns:
            Tuple of (success, entry_name)
        """
        entry, output_path = entry_data

        # Skip if exists
        if self.skip_existing and output_path.exists():
            self.logger.debug(f"Skipping (already exists): {entry['name']}")
            self.stats["skipped"] += 1
            return (True, entry["name"])

        # Fetch content
        content = self.fetch_entry_content(entry)

        # Save
        self.save_content(content, output_path)
        self.stats["fetched"] += 1

        # Rate limiting
        time.sleep(self.rate_limit)

        return (True, entry["name"])

    def fetch(self) -> None:
        """Fetch all D3.js documentation from DevDocs."""
        self.logger.info(f"Fetching D3.js v{self.version} documentation from DevDocs")

        entries = self.fetch_index()

        if not entries:
            self.logger.error("No entries found")
            return

        # Group by type for organization
        by_type: dict[str, list[dict[Any, Any]]] = {}
        for entry in entries:
            entry_type = entry.get("type", "Other")
            if entry_type not in by_type:
                by_type[entry_type] = []
            by_type[entry_type].append(entry)

        self.logger.info(f"Found {len(by_type)} categories:")
        for cat, cat_entries in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            self.logger.info(f"  {cat}: {len(cat_entries)} entries")

        # Prepare URL paths
        entry_paths = []
        for entry in entries:
            # Organize by type
            entry_type = entry.get("type", "Other")
            # Clean type name for directory - sanitize to prevent path traversal
            type_dir = entry_type.lower().replace(" ", "-")
            type_dir = re.sub(r"[^\w\-]", "-", type_dir)
            type_dir = type_dir.strip("-").strip(".")

            # Generate filename from path
            path = entry["path"]
            filename = path.replace("/", "-") + ".md"

            output_path = self.output_dir / "d3" / type_dir / filename

            # Validate output path to prevent path traversal
            try:
                from ..utils.file_utils import validate_output_path

                output_path = validate_output_path(output_path, self.output_dir)
            except ValueError as e:
                self.logger.error(f"Invalid output path for entry {entry.get('name', 'unknown')}: {e}")
                continue

            entry_paths.append(((entry, output_path), entry))

        self.logger.info(f"Fetching with {self.max_workers} concurrent workers")
        start_time = time.time()

        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_entry, ep[0]): ep[1] for ep in entry_paths}

            total = len(futures)

            for completed, future in enumerate(as_completed(futures), start=1):
                success, name = future.result()

                if completed % 50 == 0 or completed == total:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    self.logger.info(
                        f"[{completed}/{total}] " f"({completed*100//total}%) " f"- {rate:.1f} docs/sec"
                    )

        elapsed = time.time() - start_time
        self.logger.info(f"Completed in {elapsed:.1f}s ({total/elapsed:.1f} docs/sec)")

        self.logger.info("D3.js documentation fetch complete")
        self.print_stats()
