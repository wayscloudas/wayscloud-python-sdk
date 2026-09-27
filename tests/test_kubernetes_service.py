"""KubernetesService request shapes against a fake client (no HTTP)."""
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from wayscloud.exceptions import NotFoundError
from wayscloud.services.kubernetes import KubernetesService


class FakeClient:
    def __init__(self, responses=None):
        self.calls, self.responses = [], list(responses or [])

    def _rec(self, method, path, **kw):
        self.calls.append((method, path, kw))
        return self.responses.pop(0) if self.responses else {}

    def get(self, path, params=None, raw=False):
        return self._rec("GET", path, params=params, raw=raw)

    def post(self, path, json=None):
        return self._rec("POST", path, json=json)

    def put(self, path, json=None):
        return self._rec("PUT", path, json=json)

    def delete(self, path, json=None):
        return self._rec("DELETE", path, json=json)


class ServiceTests(unittest.TestCase):
    def test_create_payload(self):
        c = FakeClient([{"id": "c1", "status": "provisioning"}])
        out = KubernetesService(c).create("shop", [{"name": "default", "plan_code": "k8s-node-2c4g", "count": 2}], api_ip_filter=["1.2.3.0/24"])
        self.assertEqual(out["id"], "c1")
        m, p, kw = c.calls[0]
        self.assertEqual((m, p), ("POST", "/v1/kubernetes/clusters"))
        self.assertEqual(kw["json"]["node_pools"][0]["count"], 2)
        self.assertEqual(kw["json"]["plan_code"], "k8s-cluster-dev")
        self.assertEqual(kw["json"]["ssh_key_ids"], [])
        self.assertEqual(kw["json"]["version"], "1.35")

    def test_add_node_pool_sends_labels_taints_and_ssh_keys(self):
        c = FakeClient([{"id": "c1"}])
        KubernetesService(c).add_node_pool(
            "c1", "workers", "k8s-node-2c4g", 2,
            labels={"role": "worker"},
            taints=[{"key": "dedicated", "value": "gpu", "effect": "NoSchedule"}],
            ssh_key_ids=["11111111-1111-1111-1111-111111111111"])
        m, p, kw = c.calls[0]
        self.assertEqual((m, p), ("POST", "/v1/kubernetes/clusters/c1/node-pools"))
        self.assertEqual(kw["json"]["labels"], {"role": "worker"})
        self.assertEqual(kw["json"]["taints"], [{"key": "dedicated", "value": "gpu", "effect": "NoSchedule"}])
        self.assertEqual(kw["json"]["ssh_key_ids"], ["11111111-1111-1111-1111-111111111111"])
        self.assertEqual(kw["json"]["count"], 2)

    def test_add_node_pool_defaults_are_empty(self):
        c = FakeClient([{"id": "c1"}])
        KubernetesService(c).add_node_pool("c1", "workers", "k8s-node-2c4g", 1)
        self.assertEqual(c.calls[0][2]["json"], {"name": "workers", "plan_code": "k8s-node-2c4g", "count": 1,
                                                 "labels": {}, "taints": [], "ssh_key_ids": []})

    def test_delete_sends_confirmation_body(self):
        c = FakeClient([{"status": "deleting"}])
        KubernetesService(c).delete("c1", "shop")
        self.assertEqual(c.calls[0], ("DELETE", "/v1/kubernetes/clusters/c1", {"json": {"confirm_name": "shop"}}))

    def test_kubeconfig_is_raw_text(self):
        c = FakeClient(["apiVersion: v1"])
        self.assertEqual(KubernetesService(c).kubeconfig("c1"), "apiVersion: v1")
        self.assertTrue(c.calls[0][2]["raw"])

    def test_list_unwraps_envelope(self):
        c = FakeClient([{"clusters": [{"id": "a"}], "total": 1}])
        self.assertEqual(KubernetesService(c).list(), [{"id": "a"}])

    def test_wait_returns_on_running_and_on_404(self):
        c = FakeClient([{"status": "provisioning"}, {"status": "running", "id": "c1"}])
        svc = KubernetesService(c)
        self.assertEqual(svc.wait("c1", timeout=5, interval=0)["status"], "running")

        class Gone(FakeClient):
            def get(self, *a, **k):
                raise NotFoundError("404")
        self.assertEqual(KubernetesService(Gone()).wait("c1", timeout=5, interval=0)["status"], "deleted")

    def test_maintenance_window_payloads(self):
        c = FakeClient([{"timezone": "Europe/Oslo"}, {"enabled": True}, {"enabled": False}])
        svc = KubernetesService(c)
        self.assertEqual(svc.get_maintenance_window("c1")["timezone"], "Europe/Oslo")
        svc.set_maintenance_window("c1", timezone="Europe/Oslo", days=["SAT", "SUN"],
                                   start="02:00", duration_minutes=120)
        svc.delete_maintenance_window("c1")
        self.assertEqual(c.calls[0][:2], ("GET", "/v1/kubernetes/clusters/c1/maintenance-window"))
        self.assertEqual(c.calls[1][:2], ("PUT", "/v1/kubernetes/clusters/c1/maintenance-window"))
        self.assertEqual(c.calls[1][2]["json"], {"enabled": True, "timezone": "Europe/Oslo",
                                                 "days": ["SAT", "SUN"], "start": "02:00", "duration_minutes": 120})
        self.assertEqual(c.calls[2][:2], ("DELETE", "/v1/kubernetes/clusters/c1/maintenance-window"))

    def test_upgrade_node_pool_payload(self):
        c = FakeClient([{"id": "c1"}])
        KubernetesService(c).upgrade_node_pool("c1", "default")
        self.assertEqual(c.calls[0][:2], ("POST", "/v1/kubernetes/clusters/c1/node-pools/default/upgrade"))

    def test_upgrade_payload_modes_and_jobs(self):
        c = FakeClient([{"job": {"id": "j1"}}, {"job": {"id": "j2"}}, {"jobs": [{"id": "j1"}]}, {"id": "j1"}, {"status": "cancelled"}])
        svc = KubernetesService(c)
        svc.upgrade("c1", "1.35", mode="next_maintenance_window", strategy="rolling-update", backup_before_upgrade=True)
        svc.upgrade("c1", "1.35", mode="scheduled", scheduled_at="2026-10-03T02:30:00+02:00")
        self.assertEqual(c.calls[0][2]["json"], {"version": "1.35", "mode": "next_maintenance_window",
                                                 "strategy": "rolling-update", "backup_before_upgrade": True})
        self.assertEqual(c.calls[1][2]["json"], {"version": "1.35", "mode": "scheduled",
                                                 "scheduled_at": "2026-10-03T02:30:00+02:00",
                                                 "strategy": "rolling-update", "backup_before_upgrade": False})
        self.assertEqual(svc.upgrade_jobs("c1"), [{"id": "j1"}])
        svc.upgrade_job("c1", "j1")
        svc.cancel_upgrade_job("c1", "j1")
        self.assertEqual(c.calls[2][:2], ("GET", "/v1/kubernetes/clusters/c1/upgrade-jobs"))
        self.assertEqual(c.calls[3][:2], ("GET", "/v1/kubernetes/clusters/c1/upgrade-jobs/j1"))
        self.assertEqual(c.calls[4][:2], ("DELETE", "/v1/kubernetes/clusters/c1/upgrade-jobs/j1"))

    def test_upgrade_preflight_payload_and_shape(self):
        response = {"ok": False, "cluster_version": "1.34", "target_version": "1.35",
                    "errors": [{"code": "node_pool_not_ready", "message": "pool not ready"}],
                    "warnings": [{"code": "no_recent_backup", "message": "old"}],
                    "backup": {"latest_completed_at": None, "age_hours": None}}
        c = FakeClient([response, response])
        svc = KubernetesService(c)
        out = svc.upgrade_preflight("c1", "1.35", mode="next_maintenance_window",
                                    strategy="rolling-update", backup_before_upgrade=True)
        svc.upgrade_preflight("c1", "1.35", mode="scheduled", scheduled_at="2026-10-03T02:30:00+02:00")
        self.assertIs(out, response)
        m, p, kw = c.calls[0]
        self.assertEqual((m, p), ("POST", "/v1/kubernetes/clusters/c1/upgrade-preflight"))
        self.assertEqual(kw["json"], {"version": "1.35", "mode": "next_maintenance_window",
                                      "strategy": "rolling-update", "backup_before_upgrade": True})
        self.assertEqual(c.calls[1][2]["json"]["scheduled_at"], "2026-10-03T02:30:00+02:00")
        # errors/warnings pass through untouched — callers render them
        self.assertEqual(out["errors"][0]["code"], "node_pool_not_ready")
        self.assertEqual(out["warnings"][0]["code"], "no_recent_backup")


if __name__ == "__main__":
    unittest.main()
