# Changelog

All notable changes to the `wayscloud` Python SDK. Version numbers match the
PyPI releases.

## 0.4.0 — 2026-09-25

### Added

- **Managed Kubernetes** — `client.kubernetes`: catalogue (`plans`, `regions`,
  `versions`, `estimate`), clusters (`list`, `get`, `create`, `wait`, `delete`,
  `history`), node pools (`add_node_pool`, `scale_node_pool`,
  `delete_node_pool`; labels, taints and per-pool SSH keys), `kubeconfig`,
  API-access CIDRs (`set_api_access`), public IPs (`allocate_ip`,
  `release_ip`, `set_ptr`), backups (`backup_policy`, `set_backup_policy`,
  `backups`, `backup_now`, `restore`) and upgrades (`available_upgrades`,
  `upgrade`).
- **Impact Trees** — `client.impact`.
- **GitHub auto-deploy** for App Platform — `client.apps.auto_deploy_get`,
  `auto_deploy_configure`, `auto_deploy_rotate_secret`.

### Changed

- HTTP client accepts `202 Accepted` (asynchronous operations).
- `client.get(..., raw=True)` returns the body as text (used by `kubeconfig`).
- `client.delete(..., json=...)` can send a JSON body (cluster delete
  confirmation).
- CI: pytest workflow (`.github/workflows/test.yml`).

## 0.3.0 — 2026-04-14

Published to PyPI from the monorepo; no matching tag in this repository.
Relative to 0.2.3:

- Database: tiers, IP-based firewall rules (`add_firewall_rule(ip_address=...)`).
- DNS: zone statistics.
- IoT: device tags/health/telemetry history, groups, profiles, alarms,
  datapoints, notification channels and policies.
- Redis: IP-based firewall rules.
- Storage: bucket visibility, tiers.
- VPS: `update()`, `upgrade()`, `addons()`.

## 0.2.3 — 2026-04-05

- Simplified publish workflow (PyPI trusted publishing).
