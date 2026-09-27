"""Kubernetes service -- Managed Kubernetes clusters."""

from __future__ import annotations

import time
from typing import Optional


class KubernetesService:
    """Manage Kubernetes clusters.

    All methods use the public API at /v1/kubernetes (PAT with the
    ``kubernetes:read`` / ``kubernetes:write`` scopes, or API key auth).
    Create and delete are asynchronous: the API answers 202 with the cluster
    in status ``provisioning`` / ``deleting``; use :meth:`wait` to block.
    """

    TERMINAL = {"running", "error", "deleted"}

    def __init__(self, client):
        self._client = client

    # -- catalogue -----------------------------------------------------------
    def plans(self, region: str = "no", kind: Optional[str] = None) -> list[dict]:
        """List cluster and node plans (``kind``: controlplane, node, ip, lb, storage, backup)."""
        params = {"region": region}
        if kind:
            params["kind"] = kind
        data = self._client.get("/v1/kubernetes/plans", params=params)
        return data.get("plans", []) if isinstance(data, dict) else data

    def regions(self) -> list[dict]:
        data = self._client.get("/v1/kubernetes/regions")
        return data.get("regions", []) if isinstance(data, dict) else data

    def versions(self) -> dict:
        return self._client.get("/v1/kubernetes/versions")

    def estimate(self, plan_code: str, node_pools: list[dict], currency: str = "NOK", region: str = "no") -> dict:
        return self._client.post("/v1/kubernetes/estimate",
                                 json={"plan_code": plan_code, "node_pools": node_pools, "currency": currency, "region": region})

    # -- clusters ------------------------------------------------------------
    def list(self) -> list[dict]:
        data = self._client.get("/v1/kubernetes/clusters")
        return data.get("clusters", []) if isinstance(data, dict) else data

    def get(self, cluster_id: str) -> dict:
        return self._client.get(f"/v1/kubernetes/clusters/{cluster_id}")

    def create(
        self,
        name: str,
        node_pools: list[dict],
        plan_code: str = "k8s-cluster-dev",
        region: str = "no",
        version: str = "1.35",
        api_ip_filter: Optional[list[str]] = None,
        ssh_key_ids: Optional[list[str]] = None,
    ) -> dict:
        """Create a cluster. ``node_pools``: ``[{"name": "default", "plan_code": "k8s-node-2c4g", "count": 2}]``.
        ``version`` defaults to the current default offered version (1.35; see :meth:`versions`)."""
        return self._client.post("/v1/kubernetes/clusters", json={
            "name": name, "region": region, "plan_code": plan_code, "version": version,
            "node_pools": node_pools, "api_ip_filter": api_ip_filter or [], "ssh_key_ids": ssh_key_ids or [],
        })

    def delete(self, cluster_id: str, confirm_name: str) -> dict:
        """Delete a cluster. ``confirm_name`` must equal the cluster's name."""
        return self._client.delete(f"/v1/kubernetes/clusters/{cluster_id}", json={"confirm_name": confirm_name})

    def wait(self, cluster_id: str, timeout: int = 1800, interval: int = 15) -> dict:
        """Poll until the cluster reaches running/error (or is gone after a delete)."""
        from ..exceptions import NotFoundError

        deadline = time.time() + timeout
        while True:
            try:
                c = self.get(cluster_id)
            except NotFoundError:  # gone after a delete: terminal
                return {"id": cluster_id, "status": "deleted"}
            if c.get("status") in self.TERMINAL:
                return c
            if time.time() > deadline:
                raise TimeoutError(f"cluster {cluster_id} still {c.get('status')} after {timeout}s")
            time.sleep(interval)

    def history(self, cluster_id: str) -> list[dict]:
        data = self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/history")
        return data.get("events", []) if isinstance(data, dict) else data

    # -- node pools ----------------------------------------------------------
    def add_node_pool(self, cluster_id: str, name: str, plan_code: str, count: int,
                      labels: Optional[dict] = None, taints: Optional[list[dict]] = None,
                      ssh_key_ids: Optional[list[str]] = None) -> dict:
        """Add a node pool. ``count`` must be 1-16; ``taints`` entries are
        ``{"key": ..., "value": ..., "effect": ...}``. ``ssh_key_ids`` must be
        SSH key ids on the account (ownership is validated by the API)."""
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/node-pools",
                                 json={"name": name, "plan_code": plan_code, "count": count, "labels": labels or {},
                                       "taints": taints or [], "ssh_key_ids": ssh_key_ids or []})

    def scale_node_pool(self, cluster_id: str, pool_name: str, count: int) -> dict:
        """Scale a node pool. ``count`` must be between 1 and 16; scale-to-zero is not supported."""
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/node-pools/{pool_name}/scale", json={"count": count})

    def delete_node_pool(self, cluster_id: str, pool_name: str) -> dict:
        return self._client.delete(f"/v1/kubernetes/clusters/{cluster_id}/node-pools/{pool_name}")

    def upgrade_node_pool(self, cluster_id: str, pool_name: str) -> dict:
        """Converge a pool's nodes to the cluster's current Kubernetes version
        (surge capacity, drain, recreate under the same name). Runs in the
        background; poll the cluster until the pool status is running again."""
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/node-pools/{pool_name}/upgrade")

    # -- access --------------------------------------------------------------
    def kubeconfig(self, cluster_id: str) -> str:
        """Admin kubeconfig as YAML text. Treat as a secret."""
        return self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/kubeconfig", raw=True)

    def set_api_access(self, cluster_id: str, cidrs: list[str]) -> dict:
        """Set the CIDRs allowed to reach the Kubernetes API. An empty list means the API is
        only reachable from WAYSCloud infrastructure; add the client CIDR for external
        kubectl/API access."""
        return self._client.put(f"/v1/kubernetes/clusters/{cluster_id}/api-access", json={"cidrs": cidrs})

    # -- public IPs ----------------------------------------------------------
    def allocate_ip(self, cluster_id: str) -> dict:
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/ips")

    def release_ip(self, cluster_id: str, address: str) -> dict:
        return self._client.delete(f"/v1/kubernetes/clusters/{cluster_id}/ips/{address}")

    def set_ptr(self, cluster_id: str, address: str, ptr_record: str) -> dict:
        """Set reverse DNS. The name must already resolve to the address."""
        return self._client.put(f"/v1/kubernetes/clusters/{cluster_id}/ips/{address}/ptr", json={"ptr_record": ptr_record})

    # -- backups -------------------------------------------------------------
    def backup_policy(self, cluster_id: str) -> dict:
        return self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/backup-policy")

    def set_backup_policy(self, cluster_id: str, *, enabled: bool = True, schedule_cron: str = "0 3 * * *",
                          retention_days: int = 14, include_volumes: bool = True, namespaces: Optional[list[str]] = None) -> dict:
        return self._client.put(f"/v1/kubernetes/clusters/{cluster_id}/backup-policy", json={
            "enabled": enabled, "schedule_cron": schedule_cron, "retention_days": retention_days,
            "include_volumes": include_volumes, "namespaces": namespaces})

    def backups(self, cluster_id: str) -> list[dict]:
        data = self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/backups")
        return data.get("backups", []) if isinstance(data, dict) else data

    def backup_now(self, cluster_id: str, namespaces: Optional[list[str]] = None) -> dict:
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/backups", json={"namespaces": namespaces})

    def restore(self, cluster_id: str, backup_id: str, namespaces: Optional[list[str]] = None) -> dict:
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/backups/{backup_id}/restore", json={"namespaces": namespaces})

    # -- upgrades ------------------------------------------------------------
    def available_upgrades(self, cluster_id: str) -> list[str]:
        data = self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/upgrade")
        return data.get("versions", []) if isinstance(data, dict) else data

    def upgrade(self, cluster_id: str, version: str, *, mode: str = "immediate", scheduled_at=None,
                strategy: Optional[str] = "rolling-update", backup_before_upgrade: bool = False) -> dict:
        """Request an upgrade.

        ``mode``: immediate | next_maintenance_window | scheduled (``scheduled_at``
        required, ISO-8601 with offset, inside a configured maintenance window).
        ``strategy``: rolling-update (default since the #1176 qualification) or
        manual; direct API calls that omit the field still mean manual. With
        ``backup_before_upgrade`` the upgrade waits for a fresh backup first.
        Immediate upgrades without a backup return the cluster record (historical
        behaviour); all other requests return ``{"job": ..., "cluster": ...}``."""
        body = {"version": version, "mode": mode, "backup_before_upgrade": backup_before_upgrade}
        if scheduled_at is not None:
            body["scheduled_at"] = scheduled_at.isoformat() if hasattr(scheduled_at, "isoformat") else scheduled_at
        if strategy:
            body["strategy"] = strategy
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/upgrade", json=body)

    def upgrade_preflight(self, cluster_id: str, version: str, *, mode: str = "immediate", scheduled_at=None,
                          strategy: Optional[str] = "rolling-update",
                          backup_before_upgrade: bool = False) -> dict:
        """Run the pre-upgrade check and return the structured result.

        Same input model as :meth:`upgrade`. The response carries ``errors``
        (blockers — the upgrade is refused while any is present) and
        ``warnings`` (advisory, the caller decides), plus facts such as the
        latest completed backup age and the computed schedule occurrence. The
        call is read-only apart from the server-side audit record."""
        body = {"version": version, "mode": mode, "backup_before_upgrade": backup_before_upgrade}
        if scheduled_at is not None:
            body["scheduled_at"] = scheduled_at.isoformat() if hasattr(scheduled_at, "isoformat") else scheduled_at
        if strategy:
            body["strategy"] = strategy
        return self._client.post(f"/v1/kubernetes/clusters/{cluster_id}/upgrade-preflight", json=body)

    def upgrade_jobs(self, cluster_id: str) -> list[dict]:
        """Upgrade requests for the cluster, newest first."""
        data = self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/upgrade-jobs")
        return data.get("jobs", []) if isinstance(data, dict) else data

    def upgrade_job(self, cluster_id: str, job_id: str) -> dict:
        return self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/upgrade-jobs/{job_id}")

    def cancel_upgrade_job(self, cluster_id: str, job_id: str) -> dict:
        """Cancel an upgrade that has not started yet (queued or preflight)."""
        return self._client.delete(f"/v1/kubernetes/clusters/{cluster_id}/upgrade-jobs/{job_id}")

    # -- maintenance window --------------------------------------------------
    def get_maintenance_window(self, cluster_id: str) -> dict:
        """The cluster's recurring upgrade window with the next occurrence computed."""
        return self._client.get(f"/v1/kubernetes/clusters/{cluster_id}/maintenance-window")

    def set_maintenance_window(self, cluster_id: str, *, timezone: str, days: list[str], start: str,
                               duration_minutes: int, enabled: bool = True) -> dict:
        """Create or replace the recurring window. ``days`` are MON..SUN (full names
        accepted), ``start`` is HH:MM in ``timezone``, ``duration_minutes`` is 30–480."""
        return self._client.put(f"/v1/kubernetes/clusters/{cluster_id}/maintenance-window",
                                json={"enabled": enabled, "timezone": timezone, "days": days,
                                      "start": start, "duration_minutes": duration_minutes})

    def delete_maintenance_window(self, cluster_id: str) -> dict:
        """Remove the recurring maintenance window."""
        return self._client.delete(f"/v1/kubernetes/clusters/{cluster_id}/maintenance-window")
