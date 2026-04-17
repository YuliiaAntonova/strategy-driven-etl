from __future__ import annotations


class SecretResolver:
    """Resolves credentials before runtime wiring.

    MVP behavior keeps credentials as-is. The class exists so the project can
    later support env refs / secret managers without changing the public SDK.
    """

    def resolve(self, credentials: dict) -> dict:
        return dict(credentials)
