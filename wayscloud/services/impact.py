"""Impact service — customer-funded reforestation contributions.

Maps 1:1 to /v1/impact/* endpoints. Mock provider only at MVP — every item
where `provider == 'mock'` carries `demo_data: True` from the server.
"""

from __future__ import annotations

import uuid as _uuid
from typing import Optional


class ImpactService:
    """Forests, tree commitments, items (seeds/sprouts/trees), and feed."""

    def __init__(self, client):
        self._client = client

    # ── Forests ───────────────────────────────────────────────────

    def create_forest(self, name: str) -> dict:
        return self._client.post("/v1/impact/forests", json={"name": name})

    def list_forests(self) -> list[dict]:
        data = self._client.get("/v1/impact/forests")
        return data.get("forests", data) if isinstance(data, dict) else data

    def forest_status(self, forest: str) -> dict:
        """Counts by stage + commitment buckets. `forest` may be UUID or name."""
        return self._client.get(f"/v1/impact/forests/{forest}")

    def forest_feed(self, forest: str, limit: int = 20) -> list[dict]:
        data = self._client.get(
            f"/v1/impact/forests/{forest}/feed", params={"limit": limit}
        )
        return data.get("feed", data) if isinstance(data, dict) else data

    # ── Tree commitments ──────────────────────────────────────────

    def commit_trees(
        self,
        forest: str,
        quantity: int,
        idempotency_key: Optional[str] = None,
    ) -> dict:
        """Commit N trees to a forest. Server returns the commitment + items.

        Idempotency: same idempotency_key returns the same commitment. If
        omitted, the SDK generates a UUID4 client-side so retries on transient
        network failures don't double-charge.
        """
        body = {
            "forest_id": forest,
            "quantity": quantity,
            "idempotency_key": idempotency_key or f"sdk_{_uuid.uuid4().hex}",
        }
        return self._client.post("/v1/impact/tree-commitments", json=body)

    def list_commitments(self, limit: int = 50) -> list[dict]:
        data = self._client.get(
            "/v1/impact/tree-commitments", params={"limit": limit}
        )
        return data.get("commitments", data) if isinstance(data, dict) else data

    def get_commitment(self, commitment_id: str) -> dict:
        return self._client.get(f"/v1/impact/tree-commitments/{commitment_id}")

    # ── Items (seeds / sprouts / trees) ───────────────────────────

    def get_tree(self, item_id: str) -> dict:
        """`item_id` may be a UUID or an external short id like 'seed_81ab1f2c93'."""
        return self._client.get(f"/v1/impact/trees/{item_id}")

    def water_tree(self, item_id: str) -> dict:
        """Cosmetic watering. Rate-limited server-side to once per 24h."""
        return self._client.post(f"/v1/impact/trees/{item_id}/water", json={})
