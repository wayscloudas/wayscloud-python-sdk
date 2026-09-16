"""Regions: GET /v1/regions, and the deprecated vps.regions() that delegates to it."""

import warnings

import httpx
import pytest
import respx

from wayscloud import WaysCloudClient, NotFoundError

# Body shape of GET /v1/regions in wayscloud-provision-api (app/api_regions_public.py).
REGIONS_BODY = {
    "regions": [
        {"code": "no", "name": "Norge", "city": "Oslo", "country": "NO", "status": "active",
         "available_services": ["storage", "databases", "redis", "apps", "llm"]},
        {"code": "fi", "name": "Finland", "city": "Helsinki", "country": "FI", "status": "maintenance",
         "available_services": []},
    ],
    "total": 2,
}


@pytest.fixture(autouse=True)
def _no_env_config(monkeypatch):
    """Credentials or a base URL in the environment would change the requests."""
    for name in ("WAYSCLOUD_TOKEN", "WAYSCLOUD_API_KEY", "WAYSCLOUD_API_URL"):
        monkeypatch.delenv(name, raising=False)


@respx.mock
def test_regions_list_reads_public_endpoint():
    route = respx.get("https://api.wayscloud.services/v1/regions").mock(
        return_value=httpx.Response(200, json=REGIONS_BODY)
    )
    with WaysCloudClient() as c:
        regions = c.regions.list()
    assert [r["code"] for r in regions] == ["no", "fi"]
    assert regions[0]["available_services"] == ["storage", "databases", "redis", "apps", "llm"]
    # Public endpoint: a client without credentials sends no auth headers.
    request = route.calls[0].request
    assert "x-api-key" not in request.headers
    assert "authorization" not in request.headers


@respx.mock
def test_regions_get_by_code():
    respx.get("https://api.wayscloud.services/v1/regions/NO").mock(
        return_value=httpx.Response(200, json=REGIONS_BODY["regions"][0])
    )
    with WaysCloudClient() as c:
        assert c.regions.get("NO")["code"] == "no"


@respx.mock
def test_regions_get_unknown_code_raises_not_found():
    respx.get("https://api.wayscloud.services/v1/regions/oslo").mock(
        return_value=httpx.Response(404, json={"detail": "Region 'oslo' not found"})
    )
    with WaysCloudClient() as c:
        with pytest.raises(NotFoundError):
            c.regions.get("oslo")


@respx.mock
def test_vps_regions_is_deprecated_and_delegates_to_v1_regions():
    regions_route = respx.get("https://api.wayscloud.services/v1/regions").mock(
        return_value=httpx.Response(200, json=REGIONS_BODY)
    )
    # respx fails the test on any request that is not mocked, so this also
    # proves nothing is sent to /v1/vps/regions (which reached /v1/vps/{vps_id}).
    with WaysCloudClient(api_key="wayscloud_api_test") as c:
        with pytest.warns(DeprecationWarning, match="client.regions.list"):
            regions = c.vps.regions()
    assert regions == REGIONS_BODY["regions"]
    assert regions_route.call_count == 1


def test_vps_regions_warning_points_at_the_caller():
    with WaysCloudClient() as c:
        c._regions = type("StubRegions", (), {"list": lambda self: []})()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            c.vps.regions()
    assert caught[0].category is DeprecationWarning
    assert caught[0].filename == __file__
