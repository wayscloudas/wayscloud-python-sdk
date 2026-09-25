# WAYSCloud Python SDK

Official Python SDK for the [WAYSCloud](https://wayscloud.services) API.

## Installation

```bash
pip install wayscloud
```

## Authentication

```python
from wayscloud import WaysCloudClient

# Personal Access Token
client = WaysCloudClient(token="wayscloud_pat_...")

# API key
client = WaysCloudClient(api_key="wayscloud_api_...")

# Environment variables (WAYSCLOUD_TOKEN or WAYSCLOUD_API_KEY)
client = WaysCloudClient()
```

Priority: explicit arguments > environment variables.

## Usage

```python
# VPS
for vm in client.vps.list():
    print(vm["hostname"], vm["status"])

# DNS
client.dns.create_record(
    "example.com",
    record_type="A",
    name="www",
    value="192.0.2.1",
)

# Database
db = client.database.create(name="prod", db_type="postgresql")

# Apps
app = client.apps.create(name="my-app", region="eu")

# Storage
client.storage.create_bucket("my-bucket")

# SMS
client.sms.send(to="+4712345678", message="Hello from WAYSCloud")
```

## Kubernetes

`client.kubernetes` manages Managed Kubernetes clusters (PAT scopes
`kubernetes:read` / `kubernetes:write`). Create and delete are asynchronous:
the API answers `202` with status `provisioning` / `deleting`, and `wait()`
blocks until the cluster is `running`, `error`, or gone.

```python
# Catalogue
client.kubernetes.plans(region="no", kind="node")
client.kubernetes.regions()
client.kubernetes.versions()
client.kubernetes.estimate(
    plan_code="k8s-cluster-dev",
    node_pools=[{"name": "default", "plan_code": "k8s-node-2c4g", "count": 2}],
)

# Clusters
cluster = client.kubernetes.create(
    "shop",
    node_pools=[{"name": "default", "plan_code": "k8s-node-2c4g", "count": 2}],
    ssh_key_ids=["<ssh-key-id>"],
)
cluster = client.kubernetes.wait(cluster["id"])

client.kubernetes.list()
client.kubernetes.get(cluster["id"])
client.kubernetes.history(cluster["id"])
client.kubernetes.delete(cluster["id"], confirm_name="shop")

# Node pools (labels, taints, per-pool SSH keys)
client.kubernetes.add_node_pool(
    cluster["id"], "workers", "k8s-node-2c4g", 3,
    labels={"role": "worker"},
    taints=[{"key": "dedicated", "value": "gpu", "effect": "NoSchedule"}],
    ssh_key_ids=["<ssh-key-id>"],
)
client.kubernetes.scale_node_pool(cluster["id"], "workers", 5)
client.kubernetes.delete_node_pool(cluster["id"], "workers")

# Access — the kubeconfig is a secret; restrict the API to your CIDRs
client.kubernetes.kubeconfig(cluster["id"])  # YAML text
client.kubernetes.set_api_access(cluster["id"], ["203.0.113.7/32"])

# Public IPs and reverse DNS (allocate/release return the updated cluster)
cluster = client.kubernetes.allocate_ip(cluster["id"])
address = cluster["public_ips"][-1]["address"]
client.kubernetes.set_ptr(cluster["id"], address, "shop.example.com")
client.kubernetes.release_ip(cluster["id"], address)

# Backups
client.kubernetes.backup_policy(cluster["id"])
client.kubernetes.set_backup_policy(cluster["id"], schedule_cron="0 3 * * *", retention_days=14)
client.kubernetes.backups(cluster["id"])
client.kubernetes.backup_now(cluster["id"])
client.kubernetes.restore(cluster["id"], "<backup-id>")

# Upgrades — no backup is taken automatically, create one first
client.kubernetes.available_upgrades(cluster["id"])
client.kubernetes.upgrade(cluster["id"], "1.34")
```

## Error handling

```python
from wayscloud import NotFoundError, AuthenticationError

try:
    client.vps.get("id")
except NotFoundError:
    print("Not found")
except AuthenticationError:
    print("Invalid credentials")
```

All exceptions inherit from `WaysCloudError`.

## Configuration

| Parameter | Environment variable | Default |
|-----------|---------------------|---------|
| `token` | `WAYSCLOUD_TOKEN` | — |
| `api_key` | `WAYSCLOUD_API_KEY` | — |
| `base_url` | `WAYSCLOUD_API_URL` | `https://api.wayscloud.services` |
| `timeout` | — | `30.0` |

## Retries

Automatic retries on 429, 502, 503, 504 with exponential backoff. Respects `Retry-After` headers.

## Requirements

- Python 3.10+
- httpx

## Changelog

See [CHANGELOG.md](https://github.com/wayscloudas/wayscloud-python-sdk/blob/main/CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE).
