"""Database service -- Database-as-a-Service management."""

from __future__ import annotations

from typing import Optional


class DatabaseService:
    """Manage PostgreSQL and MariaDB databases."""

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List all databases."""
        data = self._client.get("/api/v1/dashboard/databases")
        return data.get("databases", data) if isinstance(data, dict) else data

    def get(self, db_type: str, name: str) -> dict:
        """Get details of a specific database.

        Args:
            db_type: Database type (postgresql or mariadb).
            name: Database name.
        """
        return self._client.get(f"/api/v1/dashboard/databases/{db_type}/{name}")

    def create(
        self,
        name: str,
        db_type: str = "postgresql",
        tier: str = "standard",
        description: Optional[str] = None,
    ) -> dict:
        """Create a new database.

        Args:
            name: Database name.
            db_type: Database type (postgresql or mariadb).
            tier: Database tier (standard or encrypted).
            description: Optional description.
        """
        body: dict = {"name": name, "type": db_type, "tier": tier}
        if description is not None:
            body["description"] = description
        return self._client.post("/api/v1/dashboard/databases", json=body)

    def delete(self, db_type: str, name: str) -> dict:
        """Delete a database (permanent).

        Args:
            db_type: Database type (postgresql or mariadb).
            name: Database name.
        """
        return self._client.delete(f"/api/v1/dashboard/databases/{db_type}/{name}")

    def credentials(self, db_type: str, name: str) -> dict:
        """Get connection credentials for a database.

        Returns host, port, username, password, database name, and connection string.
        """
        return self._client.get(
            f"/api/v1/dashboard/databases/{db_type}/{name}/credentials"
        )

    def tiers(self) -> list[dict]:
        """List available database tiers."""
        data = self._client.get("/api/v1/dashboard/databases/tiers")
        return data.get("tiers", data) if isinstance(data, dict) else data
