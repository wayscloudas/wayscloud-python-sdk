"""IoT service -- device, group, rule, alarm, telemetry, and notification management."""

from __future__ import annotations

from typing import Optional


class IoTService:
    """Manage IoT devices, groups, rules, alarms, telemetry, and notifications.

    All methods use the public API at /v1/iot (API key auth).
    """

    def __init__(self, client):
        self._client = client

    # ── Devices ───────────────────────────────────────────────────

    def list(self) -> list[dict]:
        """List all IoT devices."""
        data = self._client.get("/v1/iot/devices")
        return data.get("devices", data) if isinstance(data, dict) else data

    # Alias
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
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Register a new IoT device."""
        body: dict = {"device_id": device_id, "name": name}
        if device_type:
            body["device_type"] = device_type
        if description:
            body["description"] = description
        if metadata:
            body["metadata"] = metadata
        return self._client.post("/v1/iot/devices", json=body)

    def update_device(self, device_id: str, **kwargs) -> dict:
        """Update a device. Pass name=, description=, device_type=, metadata=, is_active=."""
        body = {}
        for key in ("name", "description", "device_type", "metadata", "is_active"):
            if key in kwargs:
                body[key] = kwargs[key]
        return self._client.patch(f"/v1/iot/devices/{device_id}", json=body)

    def delete_device(self, device_id: str) -> dict:
        """Delete an IoT device."""
        return self._client.delete(f"/v1/iot/devices/{device_id}")

    def device_health(self, device_id: str) -> dict:
        """Get health score (0-100) with breakdown for a device."""
        return self._client.get(f"/v1/iot/devices/{device_id}/health")

    # ── Device Tags ──────────────────────────────────────────────

    def device_tags(self, device_id: str) -> list[str]:
        """List tags for a device."""
        data = self._client.get(f"/v1/iot/devices/{device_id}/tags")
        return data.get("tags", data) if isinstance(data, dict) else data

    def add_device_tags(self, device_id: str, tags: list[str]) -> dict:
        """Add tags to a device."""
        return self._client.post(
            f"/v1/iot/devices/{device_id}/tags", json={"tags": tags}
        )

    def remove_device_tag(self, device_id: str, tag: str) -> dict:
        """Remove a tag from a device."""
        return self._client.delete(f"/v1/iot/devices/{device_id}/tags/{tag}")

    # ── Telemetry ────────────────────────────────────────────────

    def device_telemetry(self, device_id: str) -> dict:
        """Get latest telemetry data for a device."""
        return self._client.get(f"/v1/iot/devices/{device_id}/telemetry/latest")

    def device_telemetry_history(
        self, device_id: str, datapoint_id: Optional[str] = None, hours: int = 24
    ) -> list[dict]:
        """Get historical telemetry for a device."""
        params: dict = {"hours": hours}
        if datapoint_id:
            params["datapoint_id"] = datapoint_id
        data = self._client.get(
            f"/v1/iot/devices/{device_id}/telemetry", params=params
        )
        return data if isinstance(data, list) else data.get("data", [])

    # ── Groups ────────────────────────────────────────────────────

    def groups(self) -> list[dict]:
        """List all device groups."""
        data = self._client.get("/v1/iot/groups")
        return data.get("groups", data) if isinstance(data, dict) else data

    def get_group(self, group_id: str) -> dict:
        """Get group details."""
        return self._client.get(f"/v1/iot/groups/{group_id}")

    def create_group(self, name: str, description: Optional[str] = None) -> dict:
        """Create a device group."""
        body: dict = {"name": name}
        if description:
            body["description"] = description
        return self._client.post("/v1/iot/groups", json=body)

    def update_group(self, group_id: str, name: Optional[str] = None, description: Optional[str] = None) -> dict:
        """Update a device group."""
        body: dict = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        return self._client.put(f"/v1/iot/groups/{group_id}", json=body)

    def delete_group(self, group_id: str) -> dict:
        """Delete a device group."""
        return self._client.delete(f"/v1/iot/groups/{group_id}")

    def add_devices_to_group(self, group_id: str, device_ids: list[str]) -> dict:
        """Add devices to a group."""
        return self._client.post(
            f"/v1/iot/groups/{group_id}/devices", json={"device_ids": device_ids}
        )

    def remove_device_from_group(self, group_id: str, device_id: str) -> dict:
        """Remove a device from a group."""
        return self._client.delete(f"/v1/iot/groups/{group_id}/devices/{device_id}")

    # ── Device Profiles ──────────────────────────────────────────

    def profiles(self) -> list[dict]:
        """List device profiles."""
        data = self._client.get("/v1/iot/profiles")
        return data if isinstance(data, list) else data.get("profiles", [])

    def get_profile(self, profile_id: str) -> dict:
        """Get profile details."""
        return self._client.get(f"/v1/iot/profiles/{profile_id}")

    def create_profile(self, name: str, **kwargs) -> dict:
        """Create a device profile. Optional kwargs: description, expected_topics, reporting_interval_seconds, metadata."""
        body: dict = {"name": name}
        for key in ("description", "expected_topics", "reporting_interval_seconds", "metadata"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.post("/v1/iot/profiles", json=body)

    def update_profile(self, profile_id: str, **kwargs) -> dict:
        """Update a device profile."""
        body: dict = {}
        for key in ("name", "description", "expected_topics", "reporting_interval_seconds", "metadata"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.put(f"/v1/iot/profiles/{profile_id}", json=body)

    def delete_profile(self, profile_id: str) -> dict:
        """Delete a device profile."""
        return self._client.delete(f"/v1/iot/profiles/{profile_id}")

    def apply_profile(self, profile_id: str, device_id: str) -> dict:
        """Apply a profile to a device."""
        return self._client.post(f"/v1/iot/profiles/{profile_id}/apply/{device_id}")

    # ── Rules ─────────────────────────────────────────────────────

    def rules(self, scope_type: Optional[str] = None) -> list[dict]:
        """List alarm rules. Optional scope_type filter."""
        params = {"scope_type": scope_type} if scope_type else None
        data = self._client.get("/v1/iot/rules", params=params)
        return data.get("rules", data) if isinstance(data, dict) else data

    def get_rule(self, rule_id: str) -> dict:
        """Get rule details."""
        return self._client.get(f"/v1/iot/rules/{rule_id}")

    def create_rule(self, name: str, rule_type: str, severity: str = "warning", **kwargs) -> dict:
        """Create an alarm rule. Optional kwargs: description, scope_type, scope_device_id, scope_group_id, config, actions, cooldown_seconds, is_enabled, auto_resolve."""
        body: dict = {"name": name, "rule_type": rule_type, "severity": severity}
        for key in ("description", "scope_type", "scope_device_id", "scope_group_id",
                     "scope_profile_id", "config", "actions", "cooldown_seconds",
                     "is_enabled", "auto_resolve"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.post("/v1/iot/rules", json=body)

    def update_rule(self, rule_id: str, **kwargs) -> dict:
        """Update an alarm rule."""
        body: dict = {}
        for key in ("name", "description", "config", "severity", "actions",
                     "cooldown_seconds", "is_enabled", "auto_resolve"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.put(f"/v1/iot/rules/{rule_id}", json=body)

    def delete_rule(self, rule_id: str) -> dict:
        """Delete an alarm rule."""
        return self._client.delete(f"/v1/iot/rules/{rule_id}")

    def enable_rule(self, rule_id: str) -> dict:
        """Enable an alarm rule."""
        return self._client.post(f"/v1/iot/rules/{rule_id}/enable")

    def disable_rule(self, rule_id: str) -> dict:
        """Disable an alarm rule."""
        return self._client.post(f"/v1/iot/rules/{rule_id}/disable")

    # ── Alarms ────────────────────────────────────────────────────

    def alarms(self, **kwargs) -> list[dict]:
        """List alarms. Optional kwargs: status, severity, device_id, rule_id, page, page_size."""
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self._client.get("/v1/iot/alarms", params=params or None)
        return data.get("alarms", data) if isinstance(data, dict) else data

    def alarm_summary(self) -> dict:
        """Get alarm counts by status and severity."""
        return self._client.get("/v1/iot/alarms/summary")

    def get_alarm(self, alarm_id: str) -> dict:
        """Get alarm details."""
        return self._client.get(f"/v1/iot/alarms/{alarm_id}")

    def alarm_timeline(self, alarm_id: str) -> list[dict]:
        """Get alarm event timeline."""
        data = self._client.get(f"/v1/iot/alarms/{alarm_id}/timeline")
        return data if isinstance(data, list) else data.get("events", [])

    def acknowledge_alarm(self, alarm_id: str, note: Optional[str] = None) -> dict:
        """Acknowledge an alarm."""
        body = {"note": note} if note else {}
        return self._client.post(f"/v1/iot/alarms/{alarm_id}/acknowledge", json=body)

    def resolve_alarm(self, alarm_id: str, note: Optional[str] = None) -> dict:
        """Resolve an alarm."""
        body = {"note": note} if note else {}
        return self._client.post(f"/v1/iot/alarms/{alarm_id}/resolve", json=body)

    def reopen_alarm(self, alarm_id: str, note: Optional[str] = None) -> dict:
        """Reopen a resolved alarm."""
        body = {"note": note} if note else {}
        return self._client.post(f"/v1/iot/alarms/{alarm_id}/reopen", json=body)

    # ── Datapoints ────────────────────────────────────────────────

    def datapoints(self) -> list[dict]:
        """List datapoint definitions."""
        data = self._client.get("/v1/iot/datapoints")
        return data if isinstance(data, list) else data.get("datapoints", [])

    def get_datapoint(self, datapoint_id: str) -> dict:
        """Get datapoint details."""
        return self._client.get(f"/v1/iot/datapoints/{datapoint_id}")

    def create_datapoint(self, key: str, label: str, unit: str = "", data_type: str = "number") -> dict:
        """Create a datapoint definition."""
        return self._client.post(
            "/v1/iot/datapoints",
            json={"key": key, "label": label, "unit": unit, "data_type": data_type},
        )

    def update_datapoint(self, datapoint_id: str, label: Optional[str] = None, unit: Optional[str] = None) -> dict:
        """Update a datapoint definition."""
        body: dict = {}
        if label is not None:
            body["label"] = label
        if unit is not None:
            body["unit"] = unit
        return self._client.put(f"/v1/iot/datapoints/{datapoint_id}", json=body)

    def delete_datapoint(self, datapoint_id: str) -> dict:
        """Delete a datapoint definition."""
        return self._client.delete(f"/v1/iot/datapoints/{datapoint_id}")

    # ── Notification Channels ────────────────────────────────────

    def notification_channels(self) -> list[dict]:
        """List notification channels."""
        data = self._client.get("/v1/iot/notifications/channels")
        return data if isinstance(data, list) else data.get("channels", [])

    def get_notification_channel(self, channel_id: str) -> dict:
        """Get notification channel details."""
        return self._client.get(f"/v1/iot/notifications/channels/{channel_id}")

    def create_notification_channel(self, name: str, channel_type: str, config: dict, is_enabled: bool = True) -> dict:
        """Create a notification channel (email, webhook, slack, teams, sms)."""
        return self._client.post(
            "/v1/iot/notifications/channels",
            json={"name": name, "channel_type": channel_type, "config": config, "is_enabled": is_enabled},
        )

    def update_notification_channel(self, channel_id: str, **kwargs) -> dict:
        """Update a notification channel."""
        body: dict = {}
        for key in ("name", "config", "is_enabled"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.put(f"/v1/iot/notifications/channels/{channel_id}", json=body)

    def delete_notification_channel(self, channel_id: str) -> dict:
        """Delete a notification channel."""
        return self._client.delete(f"/v1/iot/notifications/channels/{channel_id}")

    def test_notification_channel(self, channel_id: str) -> dict:
        """Send a test notification through a channel."""
        return self._client.post(f"/v1/iot/notifications/channels/{channel_id}/test")

    # ── Notification Policies ────────────────────────────────────

    def notification_policies(self) -> list[dict]:
        """List notification policies."""
        data = self._client.get("/v1/iot/notifications/policies")
        return data if isinstance(data, list) else data.get("policies", [])

    def get_notification_policy(self, policy_id: str) -> dict:
        """Get notification policy details."""
        return self._client.get(f"/v1/iot/notifications/policies/{policy_id}")

    def create_notification_policy(self, name: str, channel_ids: list[str], **kwargs) -> dict:
        """Create a notification policy. Optional: description, severity_filter, rule_ids, scope_type, scope_ids, event_types, cooldown_seconds, is_enabled."""
        body: dict = {"name": name, "channel_ids": channel_ids}
        for key in ("description", "severity_filter", "rule_ids", "scope_type",
                     "scope_ids", "event_types", "cooldown_seconds", "is_enabled"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.post("/v1/iot/notifications/policies", json=body)

    def update_notification_policy(self, policy_id: str, **kwargs) -> dict:
        """Update a notification policy."""
        body: dict = {}
        for key in ("name", "description", "severity_filter", "event_types",
                     "channel_ids", "cooldown_seconds", "is_enabled"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.put(f"/v1/iot/notifications/policies/{policy_id}", json=body)

    def delete_notification_policy(self, policy_id: str) -> dict:
        """Delete a notification policy."""
        return self._client.delete(f"/v1/iot/notifications/policies/{policy_id}")

    # ── Notification Deliveries ──────────────────────────────────

    def notification_deliveries(self, **kwargs) -> list[dict]:
        """List notification delivery history. Optional: channel_type, status, created_after, limit, offset."""
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = self._client.get("/v1/iot/notifications/deliveries", params=params or None)
        return data if isinstance(data, list) else data.get("deliveries", [])

    # ── MQTT & Subscription ──────────────────────────────────────

    def mqtt_credentials(self) -> dict:
        """Get MQTT broker connection details."""
        return self._client.get("/v1/iot/credentials")

    def subscription(self) -> dict:
        """Get current IoT plan, device limit, and usage."""
        return self._client.get("/v1/iot/subscription")

    def usage(self) -> dict:
        """Get message counts, data usage, and device activity."""
        return self._client.get("/v1/iot/usage")
