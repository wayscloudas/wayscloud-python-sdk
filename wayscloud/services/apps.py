"""App Platform service -- container app management."""

from __future__ import annotations

from typing import Optional


class AppService:
    """Manage container apps on the WAYSCloud App Platform.

    All methods use the public API at /v1/apps (API key auth).
    """

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List all apps."""
        data = self._client.get("/v1/apps")
        return data.get("apps", data) if isinstance(data, dict) else data

    def get(self, app_id: str) -> dict:
        """Get details of a specific app."""
        return self._client.get(f"/v1/apps/{app_id}")

    def create(
        self,
        name: str,
        plan: str = "app-basic",
        region: str = "no",
        port: int = 8080,
    ) -> dict:
        """Create a new app."""
        return self._client.post(
            "/v1/apps",
            json={"name": name, "plan": plan, "region": region, "port": port},
        )

    def update(self, app_id: str, **kwargs) -> dict:
        """Update an app. Pass any updatable fields as kwargs."""
        return self._client.patch(f"/v1/apps/{app_id}", json=kwargs)

    def delete(self, app_id: str) -> dict:
        """Delete an app (permanent)."""
        return self._client.delete(f"/v1/apps/{app_id}")

    def deploy(self, app_id: str, image: str) -> dict:
        """Deploy an app from a container image URI."""
        return self._client.post(
            f"/v1/apps/{app_id}/deploy/image",
            json={"image_uri": image},
        )

    def start(self, app_id: str) -> dict:
        """Start an app."""
        return self._client.post(f"/v1/apps/{app_id}/start")

    def stop(self, app_id: str) -> dict:
        """Stop an app."""
        return self._client.post(f"/v1/apps/{app_id}/stop")

    def restart(self, app_id: str) -> dict:
        """Restart an app."""
        return self._client.post(f"/v1/apps/{app_id}/restart")

    def logs(self, app_id: str, lines: int = 100) -> list:
        """Get app logs."""
        data = self._client.get(
            f"/v1/apps/{app_id}/logs",
            params={"lines": lines},
        )
        if isinstance(data, dict):
            return data.get("logs", data.get("lines", []))
        return data

    def plans(self) -> list[dict]:
        """List available app plans."""
        data = self._client.get("/v1/apps/plans")
        return data if isinstance(data, list) else data.get("plans", [])

    def regions(self) -> list[dict]:
        """List available app regions."""
        data = self._client.get("/v1/apps/regions")
        return data if isinstance(data, list) else data.get("regions", [])

    # ── Environment variables ─────────────────────────────────────
    # env_vars are part of the app detail and updated via PATCH

    def env_vars(self, app_id: str) -> dict:
        """Get environment variables for an app (from app detail)."""
        data = self.get(app_id)
        return data.get("env_vars", {}) if isinstance(data, dict) else {}

    def set_env(self, app_id: str, key: str, value: str) -> dict:
        """Set an environment variable on an app."""
        return self.update(app_id, env_vars={key: value})

    def unset_env(self, app_id: str, key: str) -> dict:
        """Remove an environment variable from an app."""
        return self.update(app_id, env_vars={key: None})

    # domains(), add_domain(), remove_domain() removed.
    # No public /v1/apps/{id}/domains endpoint exists (404 verified).
    # Domain management is dashboard-only.
