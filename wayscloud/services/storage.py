"""Storage service -- S3-compatible bucket and key management."""

from __future__ import annotations


class StorageService:
    """Manage S3-compatible storage buckets and access keys.

    All methods use the public API at /v1/storage (API key auth).
    """

    def __init__(self, client):
        self._client = client

    def list(self) -> list[dict]:
        """List all storage buckets."""
        data = self._client.get("/v1/storage/buckets")
        return data if isinstance(data, list) else data.get("buckets", [])

    # Alias for backward compatibility
    buckets = list

    def get(self, bucket_name: str) -> dict:
        """Get bucket details."""
        return self._client.get(f"/v1/storage/buckets/{bucket_name}")

    # Alias
    get_bucket = get

    def create_bucket(self, name: str, tier: str = "standard") -> dict:
        """Create a storage bucket."""
        return self._client.post(
            "/v1/storage/buckets",
            json={"bucket_name": name, "tier": tier},
        )

    def delete_bucket(self, bucket_name: str) -> dict:
        """Delete a storage bucket and all its contents (permanent)."""
        return self._client.delete(f"/v1/storage/buckets/{bucket_name}")

    # ── Bucket keys ───────────────────────────────────────────────

    def bucket_keys(self, bucket_name: str) -> list[dict]:
        """List API keys for a bucket."""
        data = self._client.get(f"/v1/storage/buckets/{bucket_name}/keys")
        return data if isinstance(data, list) else data.get("keys", [])

    def create_bucket_key(self, bucket_name: str, name: str) -> dict:
        """Create an API key for a bucket. Returns access_key and secret_key."""
        return self._client.post(
            f"/v1/storage/buckets/{bucket_name}/keys",
            json={"name": name},
        )

    def delete_bucket_key(self, bucket_name: str, key_id: str) -> dict:
        """Delete a bucket API key (permanent)."""
        return self._client.delete(
            f"/v1/storage/buckets/{bucket_name}/keys/{key_id}"
        )

    # credentials() and quota() removed — no public /v1/storage equivalent.
    # S3 credentials are returned in create_bucket_key() response.
    # Quota is a dashboard-only feature.
