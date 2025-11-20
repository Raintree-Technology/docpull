"""Tests for fetcher classes."""

from docpull import StripeFetcher
from docpull.utils.logging_config import setup_logging


class TestBaseFetcher:
    """Test BaseFetcher functionality."""

    def test_fetcher_initialization(self, tmp_path):
        """Test fetcher can be initialized."""
        logger = setup_logging("INFO")
        fetcher = StripeFetcher(output_dir=tmp_path, rate_limit=0.5, skip_existing=True, logger=logger)
        assert fetcher.output_dir == tmp_path
        assert fetcher.rate_limit == 0.5
        assert fetcher.skip_existing is True

    def test_stats_initialization(self, tmp_path):
        """Test stats are initialized correctly."""
        logger = setup_logging("INFO")
        fetcher = StripeFetcher(output_dir=tmp_path, rate_limit=0.5, skip_existing=True, logger=logger)
        assert fetcher.stats["fetched"] == 0
        assert fetcher.stats["skipped"] == 0
        assert fetcher.stats["errors"] == 0


class TestStripeFetcher:
    """Test Stripe-specific functionality."""

    def test_stripe_fetcher_creation(self, tmp_path):
        """Test Stripe fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = StripeFetcher(output_dir=tmp_path, rate_limit=0.5, skip_existing=True, logger=logger)
        assert fetcher is not None
