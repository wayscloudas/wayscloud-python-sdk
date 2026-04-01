"""Storage service -- S3-compatible bucket and key management."""

from __future__ import annotations


class StorageService:
    """Manage S3-compatible storage buckets, credentials, and access keys."""

    def __init__(self, client):
        self._client = client

    def buckets(self) -> list[dict]:
        """List all storage buckets."""
        data = self._client.get("/api/v1/dashboard/storage/buckets")
        return data.get("buckets", data) if isinstance(data, dict) else data

    def get_bucket(self, bucket_name: str) -> dict:
        """Get bucket details and stats."""
        return self._client.get(f"/api/v1/dashboard/storage/buckets/{bucket_name}/stats")

    def create_bucket(self, name: str, tier: str = "standard") -> dict:
        """Create a storage bucket."""
        return self._client.post(
            "/api/v1/dashboard/storage/buckets",
            json={"bucket_name": name, "tier": tier},
        )

    def delete_bucket(self, bucket_name: str) -> dict:
        """Delete a storage bucket and all its contents (permanent)."""
        return self._client.delete(f"/api/v1/dashboard/storage/buckets/{bucket_name}")

    def credentials(self) -> dict:
        """Get S3 credentials (access key, secret key, endpoint)."""
        return self._client.get("/api/v1/dashboard/storage/credentials")

    def quota(self) -> dict:
        """Get storage quota usage."""
        return self._client.get("/api/v1/dashboard/storage/quota")

    # ── Bucket keys ───────────────────────────────────────────────

    def bucket_keys(self, bucket_name: str) -> list[dict]:
        """List API keys for a bucket."""
        data = self._client.get(f"/api/v1/dashboard/storage/buckets/{bucket_name}/keys")
        return data.get("keys", data) if isinstance(data, dict) else data

    def create_bucket_key(self, bucket_name: str, name: str) -> dict:
        """Create an API key for a bucket. Returns access_key and secret_key."""
        return self._client.post(
            f"/api/v1/dashboard/storage/buckets/{bucket_name}/keys",
            json={"name": name},
        )

    def delete_bucket_key(self, bucket_name: str, key_id: str) -> dict:
        """Delete a bucket API key (permanent)."""
        return self._client.delete(
            f"/api/v1/dashboard/storage/buckets/{bucket_name}/keys/{key_id}"
        )
