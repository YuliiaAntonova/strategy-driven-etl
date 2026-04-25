from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


class ProfileLoader:
    """Loads source, destination and options profiles from YAML files.

    The SDK keeps only profile names in client code. All operational details
    live in config files, so new sources/destinations/options can be added
    without changing the public pipeline invocation.
    """

    ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}")

    def __init__(self, config_dir: str | Path = "config"):
        self.config_dir = Path(config_dir)

    def load_source(self, profile_name: str) -> dict[str, Any]:
        return self._load_profile("sources.yml", "sources", profile_name)

    def load_destination(self, profile_name: str) -> dict[str, Any]:
        return self._load_profile("destinations.yml", "destinations", profile_name)

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
        return profile

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        path = self.config_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        content = self._resolve_env_vars(path.read_text(encoding="utf-8"))
        data = yaml.safe_load(content) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Config file must contain a YAML mapping: {path}")
        return data

    def _resolve_env_vars(self, value: str) -> str:
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
