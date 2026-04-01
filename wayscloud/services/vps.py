"""VPS service — Virtual Private Server management."""

from __future__ import annotations

from typing import Optional


class VPSService:
    """Manage VPS instances, plans, templates, firewall, and networking."""

    def __init__(self, client):
        self._client = client

    def list(self, status: Optional[str] = None, region: Optional[str] = None) -> list[dict]:
        """List VPS instances, optionally filtered by status and/or region."""
        params = {}
        if status:
            params["status"] = status
        if region:
            params["region"] = region
        data = self._client.get("/api/v1/dashboard/vps", params=params or None)
        return data.get("instances", data) if isinstance(data, dict) else data

    def get(self, vps_id: str) -> dict:
        """Get details of a specific VPS instance."""
        return self._client.get(f"/api/v1/dashboard/vps/{vps_id}")

    def create(
        self,
        hostname: str,
        plan: str,
        region: str,
        os_template: str,
        ssh_keys: Optional[list[str]] = None,
    ) -> dict:
        """Create a new VPS instance."""
        body = {
            "hostname": hostname,
            "plan_code": plan,
            "region": region,
            "os_template": os_template,
        }
        if ssh_keys:
            body["ssh_keys"] = ssh_keys
        return self._client.post("/api/v1/dashboard/vps", json=body)

    def delete(self, vps_id: str) -> dict:
        """Delete a VPS instance (permanent)."""
        return self._client.delete(f"/api/v1/dashboard/vps/{vps_id}")

    def start(self, vps_id: str) -> dict:
        """Start a VPS instance."""
        return self._client.post(f"/api/v1/dashboard/vps/{vps_id}/start")

    def stop(self, vps_id: str) -> dict:
        """Stop a VPS instance."""
        return self._client.post(f"/api/v1/dashboard/vps/{vps_id}/stop")

    def reboot(self, vps_id: str) -> dict:
        """Reboot a VPS instance."""
        return self._client.post(f"/api/v1/dashboard/vps/{vps_id}/reboot")

    def rebuild(self, vps_id: str, os_template: str) -> dict:
        """Rebuild a VPS with a new OS (destroys all data)."""
        return self._client.post(
            f"/api/v1/dashboard/vps/{vps_id}/rebuild",
            json={"os_template": os_template},
        )

    def status(self, vps_id: str) -> dict:
        """Get real-time VPS status (power, CPU, memory)."""
        return self._client.get(f"/api/v1/dashboard/vps/{vps_id}/status")

    def credentials(self, vps_id: str) -> dict:
        """Get root credentials for a VPS instance."""
        return self._client.get(f"/api/v1/dashboard/vps/{vps_id}/credentials")

    def console(self, vps_id: str) -> dict:
        """Get console access URL for a VPS instance."""
        return self._client.get(f"/api/v1/dashboard/vps/{vps_id}/console")

    def plans(self, region: Optional[str] = None) -> list[dict]:
        """List available VPS plans, optionally filtered by region."""
        params = {"region": region} if region else None
        data = self._client.get("/api/v1/dashboard/vps/plans", params=params)
        return data if isinstance(data, list) else data.get("plans", [])

    def os_templates(self) -> list[dict]:
        """List available OS templates."""
        data = self._client.get("/api/v1/dashboard/vps/os-templates")
        return data if isinstance(data, list) else data.get("templates", [])

    def regions(self) -> list[dict]:
        """List available VPS regions."""
        data = self._client.get("/api/v1/dashboard/vps/regions")
        return data if isinstance(data, list) else data.get("regions", [])

    # ── Firewall ──────────────────────────────────────────────────

    def firewall_rules(self, vps_id: str) -> list[dict]:
        """List firewall rules for a VPS instance."""
        data = self._client.get(f"/api/v1/dashboard/vps/{vps_id}/firewall")
        return data.get("rules", data) if isinstance(data, dict) else data

    def add_firewall_rule(
        self,
        vps_id: str,
        port: int,
        protocol: str = "tcp",
        source: str = "0.0.0.0/0",
    ) -> dict:
        """Add a firewall rule to a VPS instance."""
        return self._client.post(
            f"/api/v1/dashboard/vps/{vps_id}/firewall",
            json={"port": port, "protocol": protocol, "source": source},
        )

    def remove_firewall_rule(self, vps_id: str, rule_id: str) -> dict:
        """Remove a firewall rule from a VPS instance."""
        return self._client.delete(f"/api/v1/dashboard/vps/{vps_id}/firewall/{rule_id}")

    # ── Networking ────────────────────────────────────────────────

    def ips(self, vps_id: str) -> list[dict]:
        """List IP addresses assigned to a VPS instance."""
        data = self._client.get(f"/api/v1/dashboard/vps/{vps_id}/network/ips")
        return data.get("ips", data) if isinstance(data, dict) else data
