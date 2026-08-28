"""Minimal retrying JSON HTTP client."""

from __future__ import annotations

import math
import time
from typing import Any

import httpx

RETRY_STATUS = frozenset({429, 502, 503, 504})
MAX_RETRY_DELAY = 60.0


def is_throttled(response: httpx.Response) -> bool:
    """Report whether a response is a rate limit rather than a refusal.

    GitHub answers its secondary rate limit with 403, the same status it uses
    for "you may not read this". Retrying every 403 would hammer a genuine
    permission failure, so only a 403 that carries throttling headers counts:
    a ``Retry-After``, or an exhausted rate-limit budget.
    """
    if response.status_code in RETRY_STATUS:
        return True
    if response.status_code != 403:
        return False
    headers = response.headers
    return "retry-after" in headers or headers.get("x-ratelimit-remaining") == "0"


class SourceError(RuntimeError):
    """A public metadata source returned an unusable response."""


class NotFoundError(SourceError):
    """The requested public record does not exist."""


class JsonClient:
    """Fetch JSON from one public source, pacing and retrying politely.

    ``min_interval`` spaces consecutive requests so a source is never sent a
    burst; ``max_attempts`` and ``backoff`` control how patiently throttled or
    temporarily unavailable responses are retried.
    """

    def __init__(
        self,
        *,
        base_url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        client: httpx.Client | None = None,
        min_interval: float = 0,
        max_attempts: int = 3,
        backoff: float = 15,
    ) -> None:
        assert max_attempts >= 1, "a request needs at least one attempt"
        self.base_url = base_url
        self._owns_client = client is None
        self.client = client or httpx.Client(
            base_url=base_url,
            headers=headers,
            params=params,
            follow_redirects=True,
            timeout=30,
        )
        self.min_interval = min_interval
        self.max_attempts = max_attempts
        self.backoff = backoff
        self._last_request_at = 0.0

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self) -> JsonClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _wait_for_slot(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

    def _backoff_delay(self, attempt: int) -> float:
        return min(self.backoff * (attempt + 1), MAX_RETRY_DELAY)

    @staticmethod
    def _reset_delay(response: httpx.Response) -> float | None:
        """Seconds until a rate-limit window reopens, if the source names one."""
        try:
            reset = float(response.headers["x-ratelimit-reset"])
        except (KeyError, ValueError):
            return None
        if not math.isfinite(reset):
            return None
        return max(reset - time.time(), 0.0)

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        """Seconds to wait before retrying, honouring a sane numeric Retry-After.

        A negative, non-finite, or non-numeric header value would either crash
        ``time.sleep`` or skip the wait entirely, so anything unusable falls
        back to the configured backoff. A rate-limit reset timestamp is used
        the same way when no Retry-After is offered, since sleeping the full
        backoff against a window that has already reopened wastes the run.
        """
        try:
            requested = float(response.headers["retry-after"])
        except (KeyError, ValueError):
            requested = self._reset_delay(response)
        if requested is None:
            return self._backoff_delay(attempt)
        if not math.isfinite(requested) or requested < 0:
            return self._backoff_delay(attempt)
        return min(requested, MAX_RETRY_DELAY)

    def get_response(
        self, path: str, *, params: dict[str, str | int] | None = None
    ) -> httpx.Response:
        for attempt in range(self.max_attempts):
            self._wait_for_slot()
            try:
                response = self.client.get(path, params=params)
            except httpx.RequestError as error:
                # Timeouts and connection resets are transient. Retrying them
                # here, and reporting them as a SourceError once the attempts
                # run out, keeps one network blip from ending the whole census.
                self._last_request_at = time.monotonic()
                if attempt == self.max_attempts - 1:
                    raise SourceError(f"{self.base_url}{path}: {error}") from error
                time.sleep(self._backoff_delay(attempt))
                continue
            self._last_request_at = time.monotonic()
            if response.status_code == 404:
                raise NotFoundError(str(response.url))
            if not is_throttled(response):
                try:
                    response.raise_for_status()
                except httpx.HTTPError as error:
                    raise SourceError(f"{response.url}: {error}") from error
                return response
            if attempt < self.max_attempts - 1:
                time.sleep(self._retry_delay(response, attempt))
        raise SourceError(f"{response.url}: repeated HTTP {response.status_code}")

    def get_json(self, path: str, *, params: dict[str, str | int] | None = None) -> Any:
        response = self.get_response(path, params=params)
        try:
            return response.json()
        except ValueError as error:
            raise SourceError(f"{response.url}: invalid JSON") from error
