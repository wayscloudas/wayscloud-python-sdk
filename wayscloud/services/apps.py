"""App Platform service -- container app management."""

from __future__ import annotations

from typing import Any, Optional


class AppService:
    """Manage container apps on the WAYSCloud App Platform."""

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List all apps."""
        data = self._client.get("/api/v1/dashboard/apps")
        return data.get("apps", data) if isinstance(data, dict) else data

    def get(self, app_id: str) -> dict:
        """Get details of a specific app."""
        return self._client.get(f"/api/v1/dashboard/apps/{app_id}")

    def create(
        self,
        name: str,
        plan: str = "app-basic",
        region: str = "no",
        port: int = 8080,
    ) -> dict:
        """Create a new app.

        Args:
            name: App name.
            plan: Plan code (default: app-basic).
            region: Region code (default: no).
            port: Application port (default: 8080).
        """
        return self._client.post(
            "/api/v1/dashboard/apps",
            json={"name": name, "plan": plan, "region": region, "port": port},
        )

    def update(self, app_id: str, **kwargs) -> dict:
        """Update an app. Pass any updatable fields as kwargs.

        Common fields: env_vars (dict), plan, port, etc.
        """
        return self._client.patch(f"/api/v1/dashboard/apps/{app_id}", json=kwargs)

    def delete(self, app_id: str) -> dict:
        """Delete an app (permanent)."""
        return self._client.delete(f"/api/v1/dashboard/apps/{app_id}")

    def deploy(self, app_id: str, image: str) -> dict:
        """Deploy an app from a container image URI."""
        return self._client.post(
            f"/api/v1/dashboard/apps/{app_id}/deploy/image",
            json={"image_uri": image},
        )

    def start(self, app_id: str) -> dict:
        """Start an app."""
        return self._client.post(f"/api/v1/dashboard/apps/{app_id}/start")

    def stop(self, app_id: str) -> dict:
        """Stop an app."""
        return self._client.post(f"/api/v1/dashboard/apps/{app_id}/stop")

    def restart(self, app_id: str) -> dict:
        """Restart an app."""
        return self._client.post(f"/api/v1/dashboard/apps/{app_id}/restart")

    def logs(self, app_id: str, lines: int = 100) -> list:
        """Get app logs.

        Args:
            app_id: App ID.
            lines: Number of log lines to retrieve (default: 100).
        """
        data = self._client.get(
            f"/api/v1/dashboard/apps/{app_id}/logs",
            params={"lines": lines},
        )
        if isinstance(data, dict):
            return data.get("logs", data.get("lines", []))
        return data

    def plans(self) -> list[dict]:
        """List available app plans."""
        data = self._client.get("/api/v1/dashboard/apps/plans")
        return data if isinstance(data, list) else data.get("plans", [])

    # ── Environment variables ─────────────────────────────────────

    def env_vars(self, app_id: str) -> dict:
        """Get environment variables for an app."""
        data = self._client.get(f"/api/v1/dashboard/apps/{app_id}")
        return data.get("env_vars", {}) if isinstance(data, dict) else {}

    def set_env(self, app_id: str, key: str, value: str) -> dict:
        """Set an environment variable on an app."""
        return self._client.patch(
            f"/api/v1/dashboard/apps/{app_id}",
            json={"env_vars": {key: value}},
        )

    def unset_env(self, app_id: str, key: str) -> dict:
        """Remove an environment variable from an app."""
        return self._client.patch(
            f"/api/v1/dashboard/apps/{app_id}",
            json={"env_vars": {key: None}},
        )

    # ── Custom domains ────────────────────────────────────────────

    def domains(self, app_id: str) -> list[dict]:
        """List custom domains for an app."""
        data = self._client.get(f"/api/v1/dashboard/apps/{app_id}/domains")
        return data.get("domains", data) if isinstance(data, dict) else data

    def add_domain(self, app_id: str, domain: str) -> dict:
        """Add a custom domain to an app."""
        return self._client.post(
            f"/api/v1/dashboard/apps/{app_id}/domains",
            json={"domain": domain},
        )

    def remove_domain(self, app_id: str, domain_id: str) -> dict:
        """Remove a custom domain from an app."""
        return self._client.delete(
            f"/api/v1/dashboard/apps/{app_id}/domains/{domain_id}"
        )
