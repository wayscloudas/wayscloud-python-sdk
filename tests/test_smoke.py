"""SDK smoke tests — verify public API surface, auth, lifecycle, and error handling."""

import os

import httpx
import pytest
import respx

from wayscloud import (
    WaysCloudClient,
    WaysCloudError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    __version__,
)


# ── Import & version ────────────────────────────────────────────

def test_version_is_string():
    assert isinstance(__version__, str)
    assert "." in __version__


# ── Auth: explicit args ─────────────────────────────────────────

def test_token_sets_bearer_header():
    c = WaysCloudClient(token="wayscloud_pat_test123")
    assert c._headers["Authorization"] == "Bearer wayscloud_pat_test123"
    c.close()


def test_api_key_token_sets_x_api_key():
    c = WaysCloudClient(token="wayscloud_api_test123")
    assert c._headers["X-API-Key"] == "wayscloud_api_test123"
    assert "Authorization" not in c._headers
    c.close()


def test_explicit_api_key_sets_header():
    c = WaysCloudClient(api_key="wayscloud_api_abc")
    assert c._headers["X-API-Key"] == "wayscloud_api_abc"
    c.close()


def test_both_token_and_api_key():
    c = WaysCloudClient(token="wayscloud_pat_x", api_key="wayscloud_api_y")
    assert c._headers["Authorization"] == "Bearer wayscloud_pat_x"
    assert c._headers["X-API-Key"] == "wayscloud_api_y"
    c.close()


# ── Auth: env var fallback ──────────────────────────────────────

def test_env_var_token(monkeypatch):
    monkeypatch.setenv("WAYSCLOUD_TOKEN", "wayscloud_pat_env")
    monkeypatch.delenv("WAYSCLOUD_API_KEY", raising=False)
    c = WaysCloudClient()
    assert c._headers["Authorization"] == "Bearer wayscloud_pat_env"
    c.close()


def test_env_var_api_key(monkeypatch):
    monkeypatch.delenv("WAYSCLOUD_TOKEN", raising=False)
    monkeypatch.setenv("WAYSCLOUD_API_KEY", "wayscloud_api_env")
    c = WaysCloudClient()
    assert c._headers["X-API-Key"] == "wayscloud_api_env"
    c.close()


def test_env_var_base_url(monkeypatch):
    monkeypatch.setenv("WAYSCLOUD_API_URL", "https://custom.example.com")
    c = WaysCloudClient(token="t")
    assert c.base_url == "https://custom.example.com"
    c.close()


def test_explicit_overrides_env(monkeypatch):
    monkeypatch.setenv("WAYSCLOUD_TOKEN", "wayscloud_pat_env")
    c = WaysCloudClient(token="wayscloud_pat_explicit")
    assert c._headers["Authorization"] == "Bearer wayscloud_pat_explicit"
    c.close()


# ── Client lifecycle ────────────────────────────────────────────

def test_context_manager():
    with WaysCloudClient(token="t") as c:
        assert c._http is not None
    assert c._http.is_closed


def test_close():
    c = WaysCloudClient(token="t")
    assert not c._http.is_closed
    c.close()
    assert c._http.is_closed


# ── Service properties ──────────────────────────────────────────

def test_all_services_instantiate():
    c = WaysCloudClient(token="t")
    services = [c.vps, c.dns, c.storage, c.database, c.redis, c.apps, c.iot, c.sms, c.account]
    assert len(services) == 9
    assert all(s is not None for s in services)
    # Lazy — same instance on second access
    assert c.vps is c.vps
    c.close()


# ── HTTP: success ───────────────────────────────────────────────

@respx.mock
def test_get_returns_json():
    respx.get("https://api.wayscloud.services/api/v1/dashboard/vps").mock(
        return_value=httpx.Response(200, json={"instances": []})
    )
    with WaysCloudClient(token="t") as c:
        result = c.vps.list()
    assert result == []


@respx.mock
def test_post_sends_json_body():
    route = respx.post("https://api.wayscloud.services/api/v1/dashboard/dns/zones").mock(
        return_value=httpx.Response(201, json={"id": "z1", "name": "example.com"})
    )
    with WaysCloudClient(token="t") as c:
        result = c.dns.create_zone("example.com")
    assert result["name"] == "example.com"
    assert route.calls[0].request.headers["content-type"] == "application/json"


@respx.mock
def test_get_does_not_send_content_type():
    route = respx.get("https://api.wayscloud.services/api/v1/dashboard/vps").mock(
        return_value=httpx.Response(200, json={"instances": []})
    )
    with WaysCloudClient(token="t") as c:
        c.vps.list()
    assert "content-type" not in route.calls[0].request.headers


@respx.mock
def test_204_returns_ok():
    respx.delete("https://api.wayscloud.services/api/v1/dashboard/vps/abc").mock(
        return_value=httpx.Response(204)
    )
    with WaysCloudClient(token="t") as c:
        result = c.vps.delete("abc")
    assert result == {"status": "ok"}


# ── HTTP: error mapping ────────────────────────────────────────

@respx.mock
def test_401_raises_authentication_error():
    respx.get("https://api.wayscloud.services/api/v1/dashboard/vps").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid token"})
    )
    with WaysCloudClient(token="t") as c:
        with pytest.raises(AuthenticationError) as exc:
            c.vps.list()
    assert exc.value.status_code == 401


@respx.mock
def test_404_raises_not_found():
    respx.get("https://api.wayscloud.services/api/v1/dashboard/vps/bad").mock(
        return_value=httpx.Response(404, json={"detail": "Not found"})
    )
    with WaysCloudClient(token="t") as c:
        with pytest.raises(NotFoundError):
            c.vps.get("bad")


@respx.mock
def test_422_raises_validation_error():
    respx.post("https://api.wayscloud.services/api/v1/dashboard/dns/zones").mock(
        return_value=httpx.Response(422, json={"detail": "Invalid zone name"})
    )
    with WaysCloudClient(token="t") as c:
        with pytest.raises(ValidationError):
            c.dns.create_zone("")


@respx.mock
def test_500_raises_server_error():
    respx.get("https://api.wayscloud.services/api/v1/dashboard/vps").mock(
        return_value=httpx.Response(500, json={"detail": "Internal error"})
    )
    with WaysCloudClient(token="t") as c:
        with pytest.raises(ServerError):
            c.vps.list()


# ── HTTP: retry ─────────────────────────────────────────────────

@respx.mock
def test_retries_on_429_then_succeeds():
    route = respx.get("https://api.wayscloud.services/api/v1/dashboard/vps").mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(200, json={"instances": [{"hostname": "ok"}]}),
        ]
    )
    with WaysCloudClient(token="t") as c:
        c.BACKOFF_FACTOR = 0.01  # Speed up test
        result = c.vps.list()
    assert len(result) == 1
    assert route.call_count == 2


# ── Service method signatures ───────────────────────────────────

def test_dns_create_record_uses_record_type():
    """Verify renamed param — no Python builtin shadow."""
    import inspect
    from wayscloud.services.dns import DNSService
    sig = inspect.signature(DNSService.create_record)
    assert "record_type" in sig.parameters
    assert "type" not in sig.parameters


def test_database_create_uses_db_type():
    import inspect
    from wayscloud.services.database import DatabaseService
    sig = inspect.signature(DatabaseService.create)
    assert "db_type" in sig.parameters
    assert "type" not in sig.parameters


def test_iot_create_rule_uses_rule_type():
    import inspect
    from wayscloud.services.iot import IoTService
    sig = inspect.signature(IoTService.create_rule)
    assert "rule_type" in sig.parameters
    assert "type" not in sig.parameters
