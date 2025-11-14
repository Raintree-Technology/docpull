import json
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore


class FetcherConfig:
    """Configuration for documentation fetchers."""

    def __init__(
        self,
        output_dir: str = "./docs",
        rate_limit: float = 0.5,
        skip_existing: bool = True,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        sources: Optional[list[str]] = None,
        dry_run: bool = False,
    ):
        """
        Initialize configuration.

        Args:
            output_dir: Directory to save documentation
            rate_limit: Seconds between requests
            skip_existing: Skip existing files
            log_level: Logging level
            log_file: Optional log file path
            sources: List of sources to fetch (e.g., ['stripe', 'plaid'])
            dry_run: Dry run mode (don't download files)
        """
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.skip_existing = skip_existing
        self.log_level = log_level
        self.log_file = log_file
        self.sources = sources or ["plaid", "stripe"]
        self.dry_run = dry_run

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "FetcherConfig":
        """
        Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            FetcherConfig instance

        Raises:
            ValueError: If configuration values are invalid
        """
        # Validate output_dir doesn't contain path traversal
        output_dir = str(config_dict.get("output_dir", "./docs"))
        if ".." in output_dir or output_dir.startswith("/etc") or output_dir.startswith("/sys"):
            raise ValueError("Invalid output directory path")

        # Validate rate_limit is reasonable
        rate_limit = config_dict.get("rate_limit", 0.5)
        if not isinstance(rate_limit, (int, float)) or rate_limit < 0 or rate_limit > 60:
            raise ValueError("rate_limit must be between 0 and 60")

        # Validate sources
        valid_sources = {"bun", "d3", "nextjs", "plaid", "react", "stripe", "tailwind", "turborepo"}
        sources = config_dict.get("sources", ["plaid", "stripe"])
        if not all(s in valid_sources for s in sources):
            raise ValueError(f"Invalid sources. Must be from: {valid_sources}")

        # Validate log_level
        log_level = config_dict.get("log_level", "INFO")
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if log_level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log_level. Must be one of: {valid_log_levels}")

        return cls(
            output_dir=output_dir,
            rate_limit=rate_limit,
            skip_existing=config_dict.get("skip_existing", True),
            log_level=log_level,
            log_file=config_dict.get("log_file"),
            sources=sources,
            dry_run=config_dict.get("dry_run", False),
        )

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "FetcherConfig":
        """
        Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML config file

        Returns:
            FetcherConfig instance

        Raises:
            ImportError: If pyyaml is not installed
            FileNotFoundError: If config file doesn't exist
        """
        if yaml is None:
            raise ImportError("PyYAML is required for YAML config. Install with: pip install pyyaml")

        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(yaml_path) as f:
            config_dict = yaml.safe_load(f)

        return cls.from_dict(config_dict)

    @classmethod
    def from_json(cls, json_path: Path) -> "FetcherConfig":
        """
        Load configuration from JSON file.

        Args:
            json_path: Path to JSON config file

        Returns:
            FetcherConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if not json_path.exists():
            raise FileNotFoundError(f"Config file not found: {json_path}")

        with open(json_path) as f:
            config_dict = json.load(f)

        return cls.from_dict(config_dict)

    @classmethod
    def from_file(cls, config_path: Path) -> "FetcherConfig":
        """
        Load configuration from file (auto-detect format).

        Args:
            config_path: Path to config file

        Returns:
            FetcherConfig instance
        """
        suffix = config_path.suffix.lower()

        if suffix in [".yaml", ".yml"]:
            return cls.from_yaml(config_path)
        elif suffix == ".json":
            return cls.from_json(config_path)
        else:
            raise ValueError(f"Unsupported config file format: {suffix}")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return {
            "output_dir": str(self.output_dir),
            "rate_limit": self.rate_limit,
            "skip_existing": self.skip_existing,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "sources": self.sources,
            "dry_run": self.dry_run,
        }

    def save_yaml(self, yaml_path: Path) -> None:
        """
        Save configuration to YAML file.

        Args:
            yaml_path: Path to save YAML config

        Raises:
            ImportError: If pyyaml is not installed
        """
        if yaml is None:
            raise ImportError("PyYAML is required for YAML config. Install with: pip install pyyaml")

        with open(yaml_path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def save_json(self, json_path: Path) -> None:
        """
        Save configuration to JSON file.

        Args:
            json_path: Path to save JSON config
        """
        with open(json_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
