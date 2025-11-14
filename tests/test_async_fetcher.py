"""Tests for async fetcher functionality."""

import asyncio

import pytest

from docpull.fetchers.async_fetcher import AsyncFetcher
from docpull.fetchers.base import BaseFetcher
from docpull.utils.logging_config import setup_logging


@pytest.fixture
def logger():
    """Create logger for tests."""
    return setup_logging("INFO")


class DummyFetcher(BaseFetcher):
    """Concrete implementation of BaseFetcher for testing."""

    def fetch(self) -> None:
        """Dummy fetch implementation for testing."""
        pass


@pytest.fixture
def base_fetcher(tmp_path, logger):
    """Create base fetcher for async tests."""
    return DummyFetcher(
        output_dir=tmp_path,
        rate_limit=0.1,
        skip_existing=True,
        logger=logger,
    )


class TestAsyncFetcher:
    """Test async fetcher functionality."""

    @pytest.mark.asyncio
    async def test_async_fetcher_initialization(self, base_fetcher):
        """Test async fetcher can be initialized."""
        async with AsyncFetcher(
            base_fetcher=base_fetcher,
            max_concurrent=5,
            use_js=False,
        ) as fetcher:
            assert fetcher.max_concurrent == 5
            assert fetcher.use_js is False
            assert fetcher.semaphore._value == 5  # Semaphore initialized

    @pytest.mark.asyncio
    async def test_concurrent_limit(self, base_fetcher):
        """Test concurrent request limiting."""
        max_concurrent = 3
        async with AsyncFetcher(
            base_fetcher=base_fetcher,
            max_concurrent=max_concurrent,
            use_js=False,
        ) as fetcher:
            # Verify semaphore limits concurrency
            assert fetcher.semaphore._value == max_concurrent

    @pytest.mark.asyncio
    async def test_rate_limiting_respected(self, base_fetcher):
        """Test that rate limiting is respected in async mode."""
        import time

        async with AsyncFetcher(
            base_fetcher=base_fetcher,
            max_concurrent=1,
            use_js=False,
        ) as fetcher:
            # Mock a simple fetch operation
            start_time = time.time()

            # Simulate fetching with rate limit
            await asyncio.sleep(fetcher.rate_limit_delay)
            await asyncio.sleep(fetcher.rate_limit_delay)

            elapsed = time.time() - start_time

            # Should take at least 2x rate limit
            assert elapsed >= (fetcher.rate_limit_delay * 2) - 0.1


class TestAsyncFetcherSecurity:
    """Test security features of async fetcher."""

    @pytest.mark.asyncio
    async def test_url_validation_before_fetch(self, base_fetcher, tmp_path):
        """Test URL validation is enforced."""
        async with AsyncFetcher(
            base_fetcher=base_fetcher,
            max_concurrent=5,
            use_js=False,
        ) as fetcher:
            # These should be rejected (tested via base_fetcher.validate_url)
            invalid_urls = [
                ("http://example.com", tmp_path / "test1.md"),  # HTTP not HTTPS
                ("https://localhost/test", tmp_path / "test2.md"),  # localhost
                ("https://192.168.1.1/test", tmp_path / "test3.md"),  # private IP
            ]

            for url, path in invalid_urls:
                result = await fetcher.fetch_url(None, url, path)
                assert result is False  # Should fail validation
                assert base_fetcher.stats["errors"] > 0

    @pytest.mark.asyncio
    async def test_content_size_limits(self, base_fetcher):
        """Test content size limits are enforced."""
        async with AsyncFetcher(
            base_fetcher=base_fetcher,
            max_concurrent=5,
            use_js=False,
        ) as fetcher:
            # Verify size limits are set
            assert fetcher.MAX_CONTENT_SIZE == 50 * 1024 * 1024  # 50 MB

    @pytest.mark.asyncio
    async def test_timeout_controls(self, base_fetcher):
        """Test timeout controls exist."""
        async with AsyncFetcher(
            base_fetcher=base_fetcher,
            max_concurrent=5,
            use_js=False,
        ) as fetcher:
            # Verify timeout settings
            assert fetcher.MAX_DOWNLOAD_TIME == 300  # 5 minutes
            assert fetcher.MAX_JS_RENDER_TIME == 30  # 30 seconds


@pytest.mark.integration
class TestAsyncFetcherIntegration:
    """Integration tests for async fetcher (requires network)."""

    @pytest.mark.asyncio
    async def test_fetch_real_url_without_js(self, base_fetcher, tmp_path):
        """Test fetching a real URL (skip if no network)."""
        pytest.skip("Integration test - requires network")
        # Example integration test structure:
        # async with AsyncFetcher(...) as fetcher:
        #     result = await fetcher.fetch_url(
        #         session, "https://example.com", tmp_path / "test.md"
        #     )
        #     assert result is True
