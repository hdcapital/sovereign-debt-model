"""Small HTTP helper shared by every collector: one session, retries, a polite UA, and
an optional on-disk replay cache so tests never touch the network."""

from __future__ import annotations

import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger(__name__)

UA = "sovereign-debt-monitor/0.1 (+https://github.com/hdcapital/sovereign-debt-model)"
DEFAULT_TIMEOUT = 60
RETRY_STATUSES = {429, 500, 502, 503, 504}


class HttpError(RuntimeError):
    def __init__(self, url: str, status: int, body: str) -> None:
        super().__init__(f"HTTP {status} for {url}: {body[:300]}")
        self.url = url
        self.status = status
        self.body = body


class Http:
    """requests.Session wrapper. If ``SDM_HTTP_REPLAY_DIR`` is set, responses are read from
    (and never written to) that directory, keyed by URL hash; used by the test suite."""

    def __init__(self, replay_dir: Path | None = None, retries: int = 3) -> None:
        env_dir = os.environ.get("SDM_HTTP_REPLAY_DIR")
        self.replay_dir = replay_dir or (Path(env_dir) if env_dir else None)
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Accept": "*/*"})

    @staticmethod
    def key(url: str) -> str:
        return hashlib.sha1(url.encode()).hexdigest()[:16]

    def get_bytes(
        self, url: str, params: dict[str, Any] | None = None, timeout: int = DEFAULT_TIMEOUT
    ) -> bytes:
        full = url if not params else requests.Request("GET", url, params=params).prepare().url or url
        if self.replay_dir is not None:
            path = self.replay_dir / self.key(full)
            if not path.exists():
                raise FileNotFoundError(f"no replay fixture for {full} (key {self.key(full)})")
            return path.read_bytes()
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                resp = self.session.get(full, timeout=timeout)
                if resp.status_code in RETRY_STATUSES and attempt < self.retries:
                    time.sleep(2**attempt)
                    continue
                if resp.status_code >= 400:
                    raise HttpError(full, resp.status_code, resp.text)
                return resp.content
            except (requests.ConnectionError, requests.Timeout) as e:
                last = e
                time.sleep(2**attempt)
        raise RuntimeError(f"failed after retries: {full}: {last}")

    def get_text(self, url: str, params: dict[str, Any] | None = None, encoding: str = "utf-8") -> str:
        return self.get_bytes(url, params).decode(encoding, errors="replace")

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        import json

        return json.loads(self.get_text(url, params))
