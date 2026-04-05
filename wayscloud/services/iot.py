"""IoT service -- device, group, and rule management."""

from __future__ import annotations

from typing import Optional


class IoTService:
    """Manage IoT devices, groups, rules, and telemetry.

    All methods use the public API at /v1/iot (API key auth).
    """

    def __init__(self, client):
        self._client = client

    # ── Devices ───────────────────────────────────────────────────

    def list(self) -> list[dict]:
        """List all IoT devices."""
        data = self._client.get("/v1/iot/devices")
        return data.get("devices", data) if isinstance(data, dict) else data

    # Alias for backward compatibility
    devices = list

    def get(self, device_id: str) -> dict:
        """Get details of a specific device."""
        return self._client.get(f"/v1/iot/devices/{device_id}")

    # Alias
    get_device = get

    def create_device(
        self,
        device_id: str,
        name: str,
        device_type: Optional[str] = None,
    ) -> dict:
        """Register a new IoT device."""
        body: dict = {"device_id": device_id, "name": name}
        if device_type:
            body["device_type"] = device_type
        return self._client.post("/v1/iot/devices", json=body)

    def update_device(self, device_id: str, **kwargs) -> dict:
        """Update a device. Pass name=, device_type=, and/or is_active= as kwargs."""
        body = {}
        for key in ("name", "device_type", "is_active"):
            if key in kwargs:
                body[key] = kwargs[key]
        return self._client.patch(f"/v1/iot/devices/{device_id}", json=body)

    def delete_device(self, device_id: str) -> dict:
        """Delete an IoT device."""
        return self._client.delete(f"/v1/iot/devices/{device_id}")

    # device_credentials() removed — no public /v1/iot endpoint.
    # MQTT credentials are returned in the create_device() response.

    def device_telemetry(self, device_id: str) -> dict:
        """Get latest telemetry data for a device."""
        return self._client.get(f"/v1/iot/devices/{device_id}/telemetry/latest")

    # ── Groups ────────────────────────────────────────────────────

    def groups(self) -> list[dict]:
        """List all device groups."""
        data = self._client.get("/v1/iot/groups")
        return data.get("groups", data) if isinstance(data, dict) else data

    def create_group(self, name: str, description: Optional[str] = None) -> dict:
        """Create a device group."""
        body: dict = {"name": name}
        if description:
            body["description"] = description
        return self._client.post("/v1/iot/groups", json=body)

    def delete_group(self, group_id: str) -> dict:
        """Delete a device group."""
        return self._client.delete(f"/v1/iot/groups/{group_id}")

    # ── Rules ─────────────────────────────────────────────────────

    def rules(self) -> list[dict]:
        """List all IoT rules."""
        data = self._client.get("/v1/iot/rules")
        return data.get("rules", data) if isinstance(data, dict) else data

    def create_rule(
        self,
        name: str,
        rule_type: str,
        severity: str = "warning",
    ) -> dict:
        """Create an IoT rule."""
        return self._client.post(
            "/v1/iot/rules",
            json={"name": name, "type": rule_type, "severity": severity},
        )

    def delete_rule(self, rule_id: str) -> dict:
        """Delete an IoT rule."""
        return self._client.delete(f"/v1/iot/rules/{rule_id}")

    # overview() and subscription() removed — no public /v1/iot equivalent.
    # These are dashboard-only features.
