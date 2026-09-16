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
app = client.apps.create(name="my-app", region="no")

# Storage
client.storage.create_bucket("my-bucket")

# SMS
client.sms.send(to="+4712345678", message="Hello from WAYSCloud")

# Regions and the services available in each
for region in client.regions.list():
    print(region["code"], region["status"], region["available_services"])
```

## Regions

Region codes are lowercase country codes such as `no`, `se` and `dk`, and the
API accepts them in any letter case. `client.regions.list()` returns every
region with its `status` and `available_services`. It uses the public
`GET /v1/regions` endpoint, which needs no authentication.

VPS locations are not in that list. They are ISO 3166-1 country codes (`NO`,
`SE`, ...), there are more of them than `/v1/regions` lists, and no endpoint
lists them. `client.vps.plans(region="NO")` shows the plans in one location.
`client.vps.regions()` is deprecated: it never listed VPS locations.

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

## License

MIT — see [LICENSE](LICENSE).
