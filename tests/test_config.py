"""Tests for configuration management."""

from pathlib import Path

from docpull.config import FetcherConfig


class TestFetcherConfig:
    """Test FetcherConfig class."""

    def test_config_initialization(self):
        """Test config can be initialized with defaults."""
        config = FetcherConfig()
        assert config.output_dir == Path("./docs")
        assert config.rate_limit == 0.5
        assert config.skip_existing is True
        assert config.log_level == "INFO"
        assert config.sources == ["plaid", "stripe"]  # Default sources

    def test_config_with_custom_values(self):
        """Test config with custom values."""
        config = FetcherConfig(
            output_dir="./custom-docs",
            rate_limit=1.0,
            skip_existing=False,
            log_level="DEBUG",
            sources=["plaid", "stripe"],
        )
        assert config.output_dir == Path("./custom-docs")
        assert config.rate_limit == 1.0
        assert config.skip_existing is False
        assert config.log_level == "DEBUG"
        assert config.sources == ["plaid", "stripe"]

    def test_config_to_dict(self):
        """Test config can be converted to dict."""
        config = FetcherConfig(output_dir="./docs", rate_limit=0.5, sources=["stripe"])
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["output_dir"] == "docs"  # Path normalizes ./docs to docs
        assert config_dict["rate_limit"] == 0.5
        assert config_dict["sources"] == ["stripe"]
        assert config_dict["dry_run"] is False


# Config file operations tests can be added in future versions
