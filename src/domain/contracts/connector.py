"""Domain contract for creating a connection/client to external systems."""

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Connector interface (Postgres/S3/Snowflake/etc.)."""

    @abstractmethod
    def connect(self) -> Any:
        """Return a client, engine, or connection object."""
        raise NotImplementedError
