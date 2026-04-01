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
