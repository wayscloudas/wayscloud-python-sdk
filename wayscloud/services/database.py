"""Database service -- Database-as-a-Service management."""

from __future__ import annotations

from typing import Optional


class DatabaseService:
    """Manage PostgreSQL and MariaDB databases.

    All methods use the public API at /v1/databases (PAT auth).
    """

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List all databases."""
        data = self._client.get("/v1/databases")
        return data if isinstance(data, list) else data.get("databases", [])

    def get(self, db_type: str, name: str) -> dict:
        """Get details of a specific database.

        Args:
            db_type: Database type (postgresql or mariadb).
            name: Database name.
        """
        return self._client.get(f"/v1/databases/{db_type}/{name}")

    def create(
        self,
        name: str,
        db_type: str = "postgresql",
        tier: str = "standard",
        description: Optional[str] = None,
    ) -> dict:
        """Create a new database. Returns credentials on success.

        Args:
            name: Database name.
            db_type: Database type (postgresql or mariadb).
            tier: Database tier (standard or encrypted).
            description: Optional description.
        """
        body: dict = {"name": name, "type": db_type, "tier": tier}
        if description is not None:
            body["description"] = description
        return self._client.post("/v1/databases", json=body)

    def delete(self, db_type: str, name: str) -> dict:
        """Delete a database (permanent)."""
        return self._client.delete(f"/v1/databases/{db_type}/{name}")

    # ── Firewall ─────────────────────────────────────────────────

    def firewall_rules(self, db_type: str, name: str) -> list[dict]:
        """List firewall rules for a database."""
        data = self._client.get(f"/v1/databases/{db_type}/{name}/firewall")
        return data if isinstance(data, list) else data.get("rules", [])

    def add_firewall_rule(self, db_type: str, name: str, source: str) -> dict:
        """Add a firewall rule to allow access from a CIDR."""
        return self._client.post(
            f"/v1/databases/{db_type}/{name}/firewall",
            json={"source": source},
        )

    def remove_firewall_rule(self, db_type: str, name: str, rule_id: str) -> dict:
        """Remove a firewall rule."""
        return self._client.delete(f"/v1/databases/{db_type}/{name}/firewall/{rule_id}")

    # credentials() removed — no public /v1/databases/.../credentials endpoint.
    # Connection credentials are returned in create() response.
    # tiers() removed — no public endpoint. Dashboard-only discovery.
