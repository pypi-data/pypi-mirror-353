"""Configuration management for Momentum SDK."""

# Removing unused os import
# import os
from pathlib import Path
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SDK configuration loaded from environment variables and config files."""

    model_config = SettingsConfigDict(
        env_prefix="MOMENTUM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core settings
    api_key: str
    mode: Literal["local", "remote"] = "remote"

    # API settings
    api_base_url: str = "https://api.momentum.ai"
    api_version: str = "v1"
    timeout_seconds: float = 30.0
    max_retries: int = 3

    # Telemetry settings
    telemetry: Literal["enabled", "disabled"] = "disabled"
    telemetry_endpoint: Optional[str] = None

    # Local mode settings
    engine_lib_path: Optional[Path] = None

    # Cache settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600

    @property
    def api_url(self) -> str:
        """Full API URL with version."""
        return f"{self.api_base_url.rstrip('/')}/{self.api_version}"

    def load_config_file(self, path: Path) -> None:
        """Load additional configuration from a file."""
        if path.suffix == ".json":
            import json

            with open(path) as f:
                config = json.load(f)
                for key, value in config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        elif path.suffix in {".yaml", ".yml"}:
            import yaml

            with open(path) as f:
                config = yaml.safe_load(f)
                for key, value in config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Try to load from config file if exists
        config_paths = [
            Path.home() / ".momentum" / "config.json",
            Path.home() / ".momentum" / "config.yaml",
            Path.cwd() / ".momentum.json",
            Path.cwd() / ".momentum.yaml",
        ]

        for path in config_paths:
            if path.exists():
                self.load_config_file(path)
                break


# Global settings instance
settings = Settings()
