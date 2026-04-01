"""IoT service -- device, group, and rule management."""

from __future__ import annotations

from typing import Optional


class IoTService:
    """Manage IoT devices, groups, rules, and telemetry."""

    def __init__(self, client):
        self._client = client

    # ── Devices ───────────────────────────────────────────────────

    def devices(self) -> list[dict]:
        """List all IoT devices."""
        data = self._client.get("/api/v1/dashboard/iot/devices")
        return data.get("devices", data) if isinstance(data, dict) else data

    def get_device(self, device_id: str) -> dict:
        """Get details of a specific device."""
        return self._client.get(f"/api/v1/dashboard/iot/devices/{device_id}")

    def create_device(
        self,
        device_id: str,
        name: str,
        device_type: Optional[str] = None,
    ) -> dict:
        """Register a new IoT device.

        Args:
            device_id: Unique device identifier.
            name: Human-readable device name.
            device_type: Optional device type classification.
        """
        body: dict = {"device_id": device_id, "name": name}
        if device_type:
            body["device_type"] = device_type
        return self._client.post("/api/v1/dashboard/iot/devices", json=body)

    def update_device(self, device_id: str, **kwargs) -> dict:
        """Update a device. Pass name=, device_type=, and/or is_active= as kwargs."""
        body = {}
        if "name" in kwargs:
            body["name"] = kwargs["name"]
        if "device_type" in kwargs:
            body["device_type"] = kwargs["device_type"]
        if "is_active" in kwargs:
            body["is_active"] = kwargs["is_active"]
        return self._client.patch(
            f"/api/v1/dashboard/iot/devices/{device_id}",
            json=body,
        )

    def delete_device(self, device_id: str) -> dict:
        """Delete an IoT device."""
        return self._client.delete(f"/api/v1/dashboard/iot/devices/{device_id}")

    def device_credentials(self, device_id: str) -> dict:
        """Get MQTT credentials for a device.

        Returns username, password, client_id, broker_url, and port.
        """
        return self._client.get(
            f"/api/v1/dashboard/iot/devices/{device_id}/credentials"
        )

    def device_telemetry(self, device_id: str) -> dict:
        """Get latest telemetry data for a device."""
        return self._client.get(
            f"/api/v1/dashboard/iot/devices/{device_id}/telemetry/latest"
        )

    # ── Groups ────────────────────────────────────────────────────

    def groups(self) -> list[dict]:
        """List all device groups."""
        data = self._client.get("/api/v1/dashboard/iot/groups")
        return data.get("groups", data) if isinstance(data, dict) else data

    def create_group(self, name: str, description: Optional[str] = None) -> dict:
        """Create a device group."""
        body: dict = {"name": name}
        if description:
            body["description"] = description
        return self._client.post("/api/v1/dashboard/iot/groups", json=body)

    def delete_group(self, group_id: str) -> dict:
        """Delete a device group."""
        return self._client.delete(f"/api/v1/dashboard/iot/groups/{group_id}")

    # ── Rules ─────────────────────────────────────────────────────

    def rules(self) -> list[dict]:
        """List all IoT rules."""
        data = self._client.get("/api/v1/dashboard/iot/rules")
        return data.get("rules", data) if isinstance(data, dict) else data

    def create_rule(
        self,
        name: str,
        rule_type: str,
        severity: str = "warning",
    ) -> dict:
        """Create an IoT rule.

        Args:
            name: Rule name.
            rule_type: Rule type.
            severity: Severity level (default: warning).
        """
        return self._client.post(
            "/api/v1/dashboard/iot/rules",
            json={"name": name, "type": rule_type, "severity": severity},
        )

    def delete_rule(self, rule_id: str) -> dict:
        """Delete an IoT rule."""
        return self._client.delete(f"/api/v1/dashboard/iot/rules/{rule_id}")

    # ── Overview & Subscription ───────────────────────────────────

    def overview(self) -> dict:
        """Get IoT fleet overview."""
        return self._client.get("/api/v1/dashboard/iot/overview")

    def subscription(self) -> dict:
        """Get IoT subscription info."""
        return self._client.get("/api/v1/dashboard/iot/subscription")
