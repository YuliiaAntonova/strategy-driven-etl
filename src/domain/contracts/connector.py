from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    @abstractmethod
    def connect(self) -> Any:
        """Return a client, engine, or connection object."""
        raise NotImplementedError
