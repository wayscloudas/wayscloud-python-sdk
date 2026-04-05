"""Redis service -- Redis-as-a-Service management."""

from __future__ import annotations

from typing import Optional


class RedisService:
    """Manage Redis instances.

    All methods use the public API at /v1/redis (API key auth).
    """

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List all Redis instances."""
        data = self._client.get("/v1/redis/instances")
        return data if isinstance(data, list) else data.get("instances", [])

    def get(self, instance_id: str) -> dict:
        """Get details of a specific Redis instance (includes connection info)."""
        return self._client.get(f"/v1/redis/instances/{instance_id}")

    def create(
        self,
        name: str,
        plan: str = "redis-starter",
        region: str = "no",
    ) -> dict:
        """Create a new Redis instance."""
        return self._client.post(
            "/v1/redis/instances",
            json={"name": name, "plan": plan, "region": region},
        )

    def delete(self, instance_id: str) -> dict:
        """Delete a Redis instance (permanent)."""
        return self._client.delete(f"/v1/redis/instances/{instance_id}")

    def restart(self, instance_id: str) -> dict:
        """Restart a Redis instance."""
        return self._client.post(f"/v1/redis/instances/{instance_id}:restart")

    def plans(self) -> list[dict]:
        """List available Redis plans."""
        data = self._client.get("/v1/redis/plans")
        return data if isinstance(data, list) else data.get("plans", [])

    def regions(self) -> list[dict]:
        """List available Redis regions."""
        data = self._client.get("/v1/redis/regions")
        return data if isinstance(data, list) else data.get("regions", [])

    # credentials() removed — GET /instances/{id} includes connection info.
    # Use rotate_credentials() to get new password.

    def rotate_credentials(self, instance_id: str) -> dict:
        """Rotate Redis credentials. Returns new password."""
        return self._client.post(f"/v1/redis/instances/{instance_id}:rotate-credentials")

    def firewall_rules(self, instance_id: str) -> list[dict]:
        """List firewall rules for a Redis instance."""
        data = self._client.get(f"/v1/redis/instances/{instance_id}/firewall")
        return data if isinstance(data, list) else data.get("rules", [])

    def add_firewall_rule(self, instance_id: str, source: str, description: str = "") -> dict:
        """Add a firewall rule to allow access from a CIDR."""
        return self._client.post(
            f"/v1/redis/instances/{instance_id}/firewall",
            json={"source": source, "description": description},
        )

    def remove_firewall_rule(self, instance_id: str, rule_id: str) -> dict:
        """Remove a firewall rule."""
        return self._client.delete(f"/v1/redis/instances/{instance_id}/firewall/{rule_id}")
