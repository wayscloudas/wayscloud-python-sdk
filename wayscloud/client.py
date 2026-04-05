"""
WAYSCloud API client.

Single HTTP client with unified auth, retry logic, and error handling.
This is the single source of truth for all API interactions.
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from ._version import __version__
from .exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    NotImplementedError_,
    RateLimitError,
    ServerError,
    ValidationError,
    WaysCloudError,
)


class WaysCloudClient:
    """WAYSCloud API client.

    Usage:
        client = WaysCloudClient(token="wayscloud_pat_...")
        instances = client.vps.list()

        client = WaysCloudClient(api_key="wayscloud_api_...")
        zones = client.dns.zones()
    """

    DEFAULT_BASE_URL = "https://api.wayscloud.services"
    MAX_RETRIES = 3
    RETRY_STATUS_CODES = {429, 502, 503, 504}
    BACKOFF_FACTOR = 0.5  # 0.5s, 1s, 2s

    def __init__(
        self,
        token: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        import os

        # Env var fallback: explicit args take precedence
        if token is None:
            token = os.environ.get("WAYSCLOUD_TOKEN")
        if api_key is None:
            api_key = os.environ.get("WAYSCLOUD_API_KEY")
        if base_url is None:
            base_url = os.environ.get("WAYSCLOUD_API_URL")

        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

        # Build auth headers
        self._headers: dict[str, str] = {
            "User-Agent": f"wayscloud-sdk-python/{__version__}",
            "Accept": "application/json",
        }

        # Auto-detect token type from prefix
        if token:
            if token.startswith("wayscloud_api_"):
                self._headers["X-API-Key"] = token
            else:
                # PAT tokens and any other token format use Bearer
                self._headers["Authorization"] = f"Bearer {token}"
        if api_key:
            self._headers["X-API-Key"] = api_key

        # Persistent HTTP client for connection pooling
        self._http = httpx.Client(timeout=self.timeout, follow_redirects=True)

        # Lazy service instances
        self._vps: Optional[Any] = None
        self._dns: Optional[Any] = None
        self._storage: Optional[Any] = None
        self._database: Optional[Any] = None
        self._redis: Optional[Any] = None
        self._apps: Optional[Any] = None
        self._iot: Optional[Any] = None
        self._sms: Optional[Any] = None
        self._account: Optional[Any] = None

    # ── Lifecycle ─────────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ── HTTP methods ──────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        json: Any = None,
        params: Optional[dict] = None,
    ) -> Any:
        """Execute HTTP request with retry and error mapping.

        Retries up to MAX_RETRIES times on 429/502/503/504 with exponential
        backoff. Maps HTTP error codes to typed exceptions.
        """
        url = f"{self.base_url}{path}"
        last_exc: Optional[Exception] = None

        for attempt in range(self.MAX_RETRIES):
            try:
                headers = dict(self._headers)
                if json is not None:
                    headers["Content-Type"] = "application/json"

                response = self._http.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                )

                # Success
                if response.status_code in (200, 201):
                    try:
                        return response.json()
                    except Exception:
                        return {"status": "ok"}

                if response.status_code == 204:
                    return {"status": "ok"}

                # Retryable status codes
                if response.status_code in self.RETRY_STATUS_CODES and attempt < self.MAX_RETRIES - 1:
                    delay = self.BACKOFF_FACTOR * (2 ** attempt)
                    # Respect Retry-After header if present
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = max(delay, float(retry_after))
                        except ValueError:
                            pass
                    time.sleep(delay)
                    continue

                # Non-retryable error — raise immediately
                self._raise_for_status(response)

            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BACKOFF_FACTOR * (2 ** attempt))
                    continue
                raise WaysCloudError(
                    message=f"Connection failed after {self.MAX_RETRIES} attempts: {exc}",
                    status_code=0,
                    detail=str(exc),
                )

        # Should not reach here, but just in case
        raise WaysCloudError(
            message=f"Request failed after {self.MAX_RETRIES} attempts",
            status_code=0,
            detail=str(last_exc) if last_exc else "",
        )

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Map HTTP error response to typed exception."""
        # Parse error detail from response body
        detail = ""
        try:
            body = response.json()
            raw_detail = body.get("detail", body.get("error", body.get("message", "")))
            if isinstance(raw_detail, dict):
                detail = raw_detail.get("error", str(raw_detail))
            elif isinstance(raw_detail, list):
                detail = "; ".join(
                    d.get("msg", str(d)) if isinstance(d, dict) else str(d)
                    for d in raw_detail
                )
            else:
                detail = str(raw_detail)
        except Exception:
            detail = response.text[:500] if response.text else "Unknown error"

        status = response.status_code
        message = f"HTTP {status}: {detail}" if detail else f"HTTP {status}"

        if status in (401, 403):
            raise AuthenticationError(message=message, status_code=status, detail=detail)
        elif status == 404:
            raise NotFoundError(message=message, status_code=status, detail=detail)
        elif status in (400, 422):
            raise ValidationError(message=message, status_code=status, detail=detail)
        elif status == 409:
            raise ConflictError(message=message, status_code=status, detail=detail)
        elif status == 429:
            raise RateLimitError(message=message, status_code=status, detail=detail)
        elif status == 501:
            raise NotImplementedError_(message=message, status_code=status, detail=detail)
        elif status >= 500:
            raise ServerError(message=message, status_code=status, detail=detail)
        else:
            raise WaysCloudError(message=message, status_code=status, detail=detail)

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        """Execute GET request."""
        return self._request("GET", path, params=params)

    def post(self, path: str, json: Any = None) -> Any:
        """Execute POST request."""
        return self._request("POST", path, json=json)

    def put(self, path: str, json: Any = None) -> Any:
        """Execute PUT request."""
        return self._request("PUT", path, json=json)

    def patch(self, path: str, json: Any = None) -> Any:
        """Execute PATCH request."""
        return self._request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        """Execute DELETE request."""
        return self._request("DELETE", path)

    # ── Lazy service properties ───────────────────────────────────

    @property
    def vps(self):
        """VPS service."""
        if self._vps is None:
            from .services.vps import VPSService
            self._vps = VPSService(self)
        return self._vps

    @property
    def dns(self):
        """DNS service."""
        if self._dns is None:
            from .services.dns import DNSService
            self._dns = DNSService(self)
        return self._dns

    @property
    def storage(self):
        """S3-compatible storage service."""
        if self._storage is None:
            from .services.storage import StorageService
            self._storage = StorageService(self)
        return self._storage

    @property
    def database(self):
        """Database-as-a-Service."""
        if self._database is None:
            from .services.database import DatabaseService
            self._database = DatabaseService(self)
        return self._database

    @property
    def redis(self):
        """Redis-as-a-Service."""
        if self._redis is None:
            from .services.redis import RedisService
            self._redis = RedisService(self)
        return self._redis

    @property
    def apps(self):
        """App Platform service."""
        if self._apps is None:
            from .services.apps import AppService
            self._apps = AppService(self)
        return self._apps

    @property
    def iot(self):
        """IoT Platform service."""
        if self._iot is None:
            from .services.iot import IoTService
            self._iot = IoTService(self)
        return self._iot

    @property
    def sms(self):
        """SMS service."""
        if self._sms is None:
            from .services.sms import SMSService
            self._sms = SMSService(self)
        return self._sms

    @property
    def account(self):
        """Account service."""
        if self._account is None:
            from .services.account import AccountService
            self._account = AccountService(self)
        return self._account
