"""VPS service — Virtual Private Server management."""

from __future__ import annotations

from typing import Optional


class VPSService:
    """Manage VPS instances, plans, templates, firewall, and networking.

    All methods use the public API at /v1/vps (API key auth).
    """

    def __init__(self, client):
        self._client = client

    # ── Instances ─────────────────────────────────────────────────

    def list(self, status: Optional[str] = None, region: Optional[str] = None) -> list[dict]:
        """List VPS instances, optionally filtered by status and/or region."""
        params = {}
        if status:
            params["status"] = status
        if region:
            params["region"] = region
        data = self._client.get("/v1/vps/", params=params or None)
        return data.get("vps_instances", data) if isinstance(data, dict) else data

    def get(self, vps_id: str) -> dict:
        """Get details of a specific VPS instance."""
        return self._client.get(f"/v1/vps/{vps_id}")

    def create(
        self,
        hostname: str,
        plan: str,
        region: str,
        os_template: str,
        ssh_keys: Optional[list[str]] = None,
    ) -> dict:
        """Create a new VPS instance."""
        body: dict = {
            "hostname": hostname,
            "plan_code": plan,
            "region": region,
            "os_template": os_template,
        }
        if ssh_keys:
            body["ssh_keys"] = ssh_keys
        return self._client.post("/v1/vps", json=body)

    def delete(self, vps_id: str) -> dict:
        """Delete a VPS instance (permanent)."""
        return self._client.delete(f"/v1/vps/{vps_id}")

    def start(self, vps_id: str) -> dict:
        """Start a VPS instance."""
        return self._client.post(f"/v1/vps/{vps_id}/start")

    def stop(self, vps_id: str) -> dict:
        """Stop a VPS instance."""
        return self._client.post(f"/v1/vps/{vps_id}/stop")

    def reboot(self, vps_id: str) -> dict:
        """Reboot a VPS instance."""
        return self._client.post(f"/v1/vps/{vps_id}/reboot")

    def status(self, vps_id: str) -> dict:
        """Get real-time VPS status (power, CPU, memory)."""
        return self._client.get(f"/v1/vps/{vps_id}/status")

    # ── Plans & Discovery ────────────────────────────────────────

    def plans(self, region: Optional[str] = None) -> list[dict]:
        """List available VPS plans, optionally filtered by region."""
        if region:
            data = self._client.get(f"/v1/vps/plans/region/{region}")
        else:
            data = self._client.get("/v1/vps/plans/")
        return data if isinstance(data, list) else data.get("plans", [])

    def os_templates(self) -> list[dict]:
        """List available OS templates."""
        data = self._client.get("/v1/vps/os-templates/")
        return data if isinstance(data, list) else data.get("templates", [])

    def regions(self) -> list[dict]:
        """List available VPS regions."""
        data = self._client.get("/v1/vps/regions")
        return data if isinstance(data, list) else data.get("regions", [])

    # ── Snapshots ────────────────────────────────────────────────

    def snapshots(self, vps_id: str) -> list[dict]:
        """List snapshots for a VPS. Snapshots are same-node, not off-site backups."""
        data = self._client.get(f"/v1/vps/{vps_id}/snapshots")
        return data.get("snapshots", []) if isinstance(data, dict) else data

    def create_snapshot(self, vps_id: str, name: str, description: Optional[str] = None) -> dict:
        """Create a point-in-time snapshot. Max 10 per VPS. Requires qcow2 disk format."""
        body: dict = {"snapshot_name": name}
        if description:
            body["description"] = description
        return self._client.post(f"/v1/vps/{vps_id}/snapshots", json=body)

    def delete_snapshot(self, vps_id: str, snapshot_name: str) -> dict:
        """Delete a snapshot from hypervisor and database."""
        return self._client.delete(f"/v1/vps/{vps_id}/snapshots/{snapshot_name}")

    def rollback_snapshot(self, vps_id: str, snapshot_name: str) -> dict:
        """Rollback VPS to a snapshot. VPS must be stopped. DESTRUCTIVE — data after snapshot is lost."""
        return self._client.post(f"/v1/vps/{vps_id}/snapshots/{snapshot_name}/rollback")

    # ── Backups (off-site) ───────────────────────────────────────

    def backups(self, vps_id: str) -> list[dict]:
        """List off-site backups for a VPS."""
        data = self._client.get(f"/v1/vps/{vps_id}/backups")
        return data.get("backups", []) if isinstance(data, dict) else data

    def create_backup(self, vps_id: str) -> dict:
        """Trigger a manual off-site backup. Runs asynchronously."""
        return self._client.post(f"/v1/vps/{vps_id}/backups")

    def delete_backup(self, vps_id: str, backup_id: str) -> dict:
        """Delete a backup from off-site storage permanently."""
        return self._client.delete(f"/v1/vps/{vps_id}/backups/{backup_id}")

    def restore_backup(self, vps_id: str, backup_id: str) -> dict:
        """Restore VPS from backup. VPS must be stopped. DESTRUCTIVE.
        Note: Returns 501 until restore worker is implemented."""
        return self._client.post(f"/v1/vps/{vps_id}/backups/{backup_id}/restore")

    def backup_policy(self, vps_id: str) -> dict:
        """Get the automatic backup policy for a VPS."""
        return self._client.get(f"/v1/vps/{vps_id}/backup-policy")

    def set_backup_policy(
        self,
        vps_id: str,
        enabled: bool = True,
        frequency: str = "daily",
        time_of_day: str = "03:00",
        day_of_week: Optional[int] = None,
        retention_days: int = 7,
    ) -> dict:
        """Set or update the automatic backup policy."""
        body: dict = {
            "enabled": enabled,
            "frequency": frequency,
            "time_of_day": time_of_day,
            "retention_days": retention_days,
        }
        if day_of_week is not None:
            body["day_of_week"] = day_of_week
        return self._client.put(f"/v1/vps/{vps_id}/backup-policy", json=body)

    def delete_backup_policy(self, vps_id: str) -> dict:
        """Remove the automatic backup policy."""
        return self._client.delete(f"/v1/vps/{vps_id}/backup-policy")

    def backup_usage(self, vps_id: str) -> dict:
        """Get backup storage usage metrics for a VPS."""
        return self._client.get(f"/v1/vps/{vps_id}/backup-usage")

    def download_backup(self, vps_id: str, backup_id: str) -> dict:
        """Get download metadata for a backup. Returns dict with download info."""
        return self._client.get(f"/v1/vps/{vps_id}/backups/{backup_id}/download")

    # ── Firewall ─────────────────────────────────────────────────

    def firewall_rules(self, vps_id: str) -> list[dict]:
        """List firewall rules for a VPS instance."""
        data = self._client.get(f"/v1/vps/{vps_id}/firewall")
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
            f"/v1/vps/{vps_id}/firewall",
            json={"port": port, "protocol": protocol, "source": source},
        )

    def remove_firewall_rule(self, vps_id: str, rule_id: str) -> dict:
        """Remove a firewall rule from a VPS instance."""
        return self._client.delete(f"/v1/vps/{vps_id}/firewall/{rule_id}")
