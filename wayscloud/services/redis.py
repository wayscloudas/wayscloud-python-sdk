"""Redis service -- Redis-as-a-Service management."""

from __future__ import annotations

from typing import Optional


class RedisService:
    """Manage Redis instances."""

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List all Redis instances."""
        data = self._client.get("/api/v1/dashboard/databases/redis/instances")
        return data.get("instances", data) if isinstance(data, dict) else data

    def get(self, instance_id: str) -> dict:
        """Get details of a specific Redis instance."""
        return self._client.get(
            f"/api/v1/dashboard/databases/redis/instances/{instance_id}"
        )

    def create(
        self,
        name: str,
        plan: str = "redis-starter",
        region: str = "no",
    ) -> dict:
        """Create a new Redis instance.

        Args:
            name: Instance name.
            plan: Redis plan code (default: redis-starter).
            region: Region code (default: no).
        """
        return self._client.post(
            "/api/v1/dashboard/databases/redis/instances",
            json={"name": name, "plan": plan, "region": region},
        )

    def delete(self, instance_id: str) -> dict:
        """Delete a Redis instance (permanent)."""
        return self._client.delete(
            f"/api/v1/dashboard/databases/redis/instances/{instance_id}"
        )

    def credentials(self, instance_id: str) -> dict:
        """Get connection credentials for a Redis instance.

        Returns host, port, password, and connection string.
        """
        return self._client.get(
            f"/api/v1/dashboard/databases/redis/instances/{instance_id}/credentials"
        )

    def restart(self, instance_id: str) -> dict:
        """Restart a Redis instance."""
        return self._client.post(
            f"/api/v1/dashboard/databases/redis/instances/{instance_id}/restart"
        )

    def plans(self) -> list[dict]:
        """List available Redis plans."""
        data = self._client.get("/api/v1/dashboard/databases/redis/plans")
        return data.get("plans", data) if isinstance(data, dict) else data
