"""DNS service -- zone and record management."""

from __future__ import annotations

from typing import Optional


class DNSService:
    """Manage DNS zones, records, and DNSSEC."""

    def __init__(self, client):
        self._client = client

    # ── Zones ─────────────────────────────────────────────────────

    def zones(self) -> list[dict]:
        """List all DNS zones."""
        data = self._client.get("/api/v1/dashboard/dns/zones")
        return data.get("zones", data) if isinstance(data, dict) else data

    def get_zone(self, zone_name: str) -> dict:
        """Get details of a specific DNS zone."""
        return self._client.get(f"/api/v1/dashboard/dns/zones/{zone_name}")

    def create_zone(self, name: str, zone_type: str = "master") -> dict:
        """Create a new DNS zone."""
        return self._client.post(
            "/api/v1/dashboard/dns/zones",
            json={"zone_name": name, "zone_type": zone_type},
        )

    def delete_zone(self, zone_name: str) -> dict:
        """Delete a DNS zone and all its records (permanent)."""
        return self._client.delete(f"/api/v1/dashboard/dns/zones/{zone_name}")

    # ── Records ───────────────────────────────────────────────────

    def records(self, zone_name: str) -> list[dict]:
        """List all records in a DNS zone."""
        data = self._client.get(f"/api/v1/dashboard/dns/zones/{zone_name}/records")
        return data.get("records", data) if isinstance(data, dict) else data

    def create_record(
        self,
        zone_name: str,
        record_type: str,
        value: str,
        name: str = "",
        ttl: int = 3600,
        priority: Optional[int] = None,
    ) -> dict:
        """Create a DNS record in a zone."""
        body: dict = {
            "type": record_type,
            "name": name,
            "content": value,
            "ttl": ttl,
        }
        if priority is not None:
            body["priority"] = priority
        return self._client.post(
            f"/api/v1/dashboard/dns/zones/{zone_name}/records",
            json=body,
        )

    def update_record(self, zone_name: str, record_id: str, **kwargs) -> dict:
        """Update a DNS record. Pass value=, ttl=, and/or priority= as kwargs."""
        body = {}
        if "value" in kwargs and kwargs["value"] is not None:
            body["content"] = kwargs["value"]
        for key in ("ttl", "priority"):
            if key in kwargs and kwargs[key] is not None:
                body[key] = kwargs[key]
        return self._client.patch(
            f"/api/v1/dashboard/dns/zones/{zone_name}/records/{record_id}",
            json=body,
        )

    def delete_record(self, zone_name: str, record_id: str) -> dict:
        """Delete a DNS record (permanent)."""
        return self._client.delete(
            f"/api/v1/dashboard/dns/zones/{zone_name}/records/{record_id}"
        )

    # ── DNSSEC ────────────────────────────────────────────────────

    def dnssec_status(self, zone_name: str) -> dict:
        """Get DNSSEC status for a zone."""
        return self._client.get(f"/api/v1/dashboard/dns/zones/{zone_name}/dnssec")

    def dnssec_activate(self, zone_name: str) -> dict:
        """Activate DNSSEC for a zone."""
        return self._client.post(f"/api/v1/dashboard/dns/zones/{zone_name}/dnssec/activate")

    def dnssec_deactivate(self, zone_name: str) -> dict:
        """Deactivate DNSSEC for a zone."""
        return self._client.post(f"/api/v1/dashboard/dns/zones/{zone_name}/dnssec/deactivate")
