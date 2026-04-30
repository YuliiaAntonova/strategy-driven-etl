from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


class ProfileLoader:
    """Loads ``config/connectors.yml`` (sources + destinations) and ``options.yml``."""

    ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}")

    def __init__(self, config_dir: str | Path = "config"):
        self.config_dir = Path(config_dir)

    def load_connector(self, profile_name: str) -> dict[str, Any]:
        """Resolve a named connector profile (extract-only, load-only, or both)."""
        return self._load_profile("connectors.yml", "connectors", profile_name)

    def load_options(self, profile_name: str) -> dict[str, Any]:
        return self._load_profile("options.yml", "options", profile_name)

    def _load_profile(self, filename: str, section: str, profile_name: str) -> dict[str, Any]:
        data = self._load_yaml(filename)
        profiles = data.get(section, {})

        if profile_name not in profiles:
            available = ", ".join(sorted(profiles)) or "<none>"
            raise ValueError(
                f"Unknown {section[:-1]} profile '{profile_name}' in {filename}. "
                f"Available profiles: {available}"
            )

        profile = profiles[profile_name]

        if not isinstance(profile, dict):
            raise ValueError(f"Profile '{profile_name}' in {filename} must be a mapping")

        return self._resolve_env_vars(profile)

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        path = self.config_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}

        if not isinstance(data, dict):
            raise ValueError(f"Config file must contain a YAML mapping: {path}")

        return data

    def _resolve_env_vars(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._resolve_env_vars(item) for key, item in value.items()}

        if isinstance(value, list):
            return [self._resolve_env_vars(item) for item in value]

        if not isinstance(value, str):
            return value

        def replace(match: re.Match[str]) -> str:
            env_name = match.group(1)
            default = match.group(2)
            env_value = os.getenv(env_name)

            if env_value is not None:
                return env_value

            if default is not None:
                return default

            raise ValueError(f"Environment variable '{env_name}' is required but not set")

        return self.ENV_PATTERN.sub(replace, value)