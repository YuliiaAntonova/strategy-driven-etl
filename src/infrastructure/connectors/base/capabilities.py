from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorCapabilities:
    supports_extractor: bool = False
    supports_loader: bool = False