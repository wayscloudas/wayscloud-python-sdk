"""Account service -- profile and SSH key management."""

from __future__ import annotations


class AccountService:
    """Manage account profile and SSH keys."""

    def __init__(self, client):
        self._client = client

    def profile(self) -> dict:
        """Get the authenticated user's profile."""
        return self._client.get("/api/v1/dashboard/account/profile")

    def ssh_keys(self) -> list[dict]:
        """List SSH keys."""
        data = self._client.get("/api/v1/dashboard/account/ssh-keys")
        return data.get("ssh_keys", data) if isinstance(data, dict) else data

    def add_ssh_key(self, name: str, public_key: str) -> dict:
        """Add an SSH public key.

        Args:
            name: Human-readable key name.
            public_key: SSH public key string (e.g. ssh-ed25519 AAAA...).
        """
        return self._client.post(
            "/api/v1/dashboard/account/ssh-keys",
            json={"name": name, "public_key": public_key},
        )

    def delete_ssh_key(self, key_id: str) -> dict:
        """Delete an SSH key (permanent)."""
        return self._client.delete(f"/api/v1/dashboard/account/ssh-keys/{key_id}")
