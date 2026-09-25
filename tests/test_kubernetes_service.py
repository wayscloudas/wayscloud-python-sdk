"""KubernetesService request shapes against a fake client (no HTTP)."""
import importlib.util
import os
import sys
import types
import unittest

HERE = os.path.dirname(__file__)
SDK = os.path.join(HERE, "..")

try:
    # Normal case (repo root on sys.path or package installed): use the real
    # package so later test modules can still import `wayscloud`.
    from wayscloud.exceptions import NotFoundError
    from wayscloud.services.kubernetes import KubernetesService
except ImportError:
    # Standalone fallback: load the service module without importing the
    # package __init__ (which needs httpx).
    pkg = types.ModuleType("wayscloud"); pkg.__path__ = [os.path.join(SDK, "wayscloud")]
    sys.modules.setdefault("wayscloud", pkg)
    exc_mod = types.ModuleType("wayscloud.exceptions")


    class WaysCloudError(Exception):
        pass


    class NotFoundError(WaysCloudError):
        pass


    exc_mod.WaysCloudError, exc_mod.NotFoundError = WaysCloudError, NotFoundError
    sys.modules["wayscloud.exceptions"] = exc_mod
    spec = importlib.util.spec_from_file_location("wayscloud.services.kubernetes", os.path.join(SDK, "wayscloud", "services", "kubernetes.py"))
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
    KubernetesService = mod.KubernetesService


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


if __name__ == "__main__":
    unittest.main()
