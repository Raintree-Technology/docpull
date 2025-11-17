"""Tests for fetcher classes."""

from docpull import NextJSFetcher, PlaidFetcher, StripeFetcher
from docpull.fetchers.bun import BunFetcher
from docpull.fetchers.d3 import D3DevDocsFetcher
from docpull.fetchers.react import ReactFetcher
from docpull.fetchers.tailwind import TailwindFetcher
from docpull.fetchers.turborepo import TurborepoFetcher
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


class TestPlaidFetcher:
    """Test Plaid-specific functionality."""

    def test_plaid_fetcher_creation(self, tmp_path):
        """Test Plaid fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = PlaidFetcher(output_dir=tmp_path, rate_limit=0.5, skip_existing=True, logger=logger)
        assert fetcher is not None


class TestNextJSFetcher:
    """Test Next.js-specific functionality."""

    def test_nextjs_fetcher_creation(self, tmp_path):
        """Test Next.js fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = NextJSFetcher(
            output_dir=tmp_path, rate_limit=0.2, skip_existing=True, logger=logger, max_workers=15
        )
        assert fetcher is not None
        assert fetcher.max_workers == 15


class TestReactFetcher:
    """Test React-specific functionality."""

    def test_react_fetcher_creation(self, tmp_path):
        """Test React fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = ReactFetcher(
            output_dir=tmp_path, rate_limit=0.2, skip_existing=True, logger=logger, max_workers=15
        )
        assert fetcher is not None
        assert fetcher.max_workers == 15


class TestTailwindFetcher:
    """Test Tailwind-specific functionality."""

    def test_tailwind_fetcher_creation(self, tmp_path):
        """Test Tailwind fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = TailwindFetcher(
            output_dir=tmp_path, rate_limit=0.2, skip_existing=True, logger=logger, max_workers=15
        )
        assert fetcher is not None
        assert fetcher.max_workers == 15


class TestBunFetcher:
    """Test Bun-specific functionality."""

    def test_bun_fetcher_creation(self, tmp_path):
        """Test Bun fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = BunFetcher(
            output_dir=tmp_path, rate_limit=0.2, skip_existing=True, logger=logger, max_workers=15
        )
        assert fetcher is not None
        assert fetcher.max_workers == 15


class TestTurborepoFetcher:
    """Test Turborepo-specific functionality."""

    def test_turborepo_fetcher_creation(self, tmp_path):
        """Test Turborepo fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = TurborepoFetcher(
            output_dir=tmp_path, rate_limit=0.2, skip_existing=True, logger=logger, max_workers=15
        )
        assert fetcher is not None
        assert fetcher.max_workers == 15


class TestD3DevDocsFetcher:
    """Test D3 DevDocs-specific functionality."""

    def test_d3_fetcher_creation(self, tmp_path):
        """Test D3 fetcher can be created."""
        logger = setup_logging("INFO")
        fetcher = D3DevDocsFetcher(
            output_dir=tmp_path, rate_limit=0.2, skip_existing=True, logger=logger, max_workers=15
        )
        assert fetcher is not None
        assert fetcher.max_workers == 15
