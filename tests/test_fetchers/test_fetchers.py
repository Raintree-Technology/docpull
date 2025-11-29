"""Tests for fetcher classes."""

import pytest

from docpull import GenericFetcher
from docpull.logging_config import setup_logging


class TestGenericFetcher:
    """Test GenericFetcher functionality."""

    def test_fetcher_initialization(self, tmp_path):
        """Test fetcher can be initialized with a URL."""
        logger = setup_logging("INFO")
        fetcher = GenericFetcher(
            url="https://example.com/docs",
            output_dir=tmp_path,
            rate_limit=0.5,
            skip_existing=True,
            logger=logger,
        )
        assert fetcher.output_dir == tmp_path
        assert fetcher.rate_limit == 0.5
        assert fetcher.skip_existing is True
        assert fetcher.start_url == "https://example.com/docs"

    def test_stats_initialization(self, tmp_path):
        """Test stats are initialized correctly."""
        logger = setup_logging("INFO")
        fetcher = GenericFetcher(
            url="https://example.com/docs",
            output_dir=tmp_path,
            rate_limit=0.5,
            skip_existing=True,
            logger=logger,
        )
        assert fetcher.stats["fetched"] == 0
        assert fetcher.stats["skipped"] == 0
        assert fetcher.stats["errors"] == 0

    def test_invalid_url_raises_error(self, tmp_path):
        """Test that non-URL input raises an error."""
        logger = setup_logging("INFO")
        with pytest.raises(ValueError, match="Invalid URL"):
            GenericFetcher(
                url="not-a-url",
                output_dir=tmp_path,
                rate_limit=0.5,
                skip_existing=True,
                logger=logger,
            )
