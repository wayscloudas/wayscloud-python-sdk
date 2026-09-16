"""Regions service -- region codes and the services available in each."""

from __future__ import annotations


class RegionsService:
    """List WAYSCloud regions.

    All methods use the public API at /v1/regions (no authentication needed).
    """

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List regions, including regions that are not active.

        Each region has ``code`` (lowercase, e.g. ``"no"``), ``name``,
        ``city``, ``country`` (ISO 3166-1 alpha-2, e.g. ``"NO"``), ``status``
        and ``available_services`` (e.g. ``["storage", "apps"]``, empty unless
        ``status`` is ``"active"``). The code is the ``region`` that
        ``apps.create()`` and ``redis.create()`` take.
        """
        data = self._client.get("/v1/regions")
        return data.get("regions", []) if isinstance(data, dict) else data

    def get(self, code: str) -> dict:
        """Get one region by code. The code is matched in any letter case."""
        return self._client.get(f"/v1/regions/{code}")
