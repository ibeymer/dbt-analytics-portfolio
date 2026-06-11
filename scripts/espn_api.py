"""Minimal HTTP client for ESPN's public JSON API.

ESPN exposes undocumented but stable JSON endpoints that need no API key. This
module centralizes the request logic — a browser-like User-Agent, a timeout, and
simple exponential-backoff retries — so the extract scripts stay focused on
shaping data. Standard library only.
"""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request

_CTX = ssl.create_default_context()
_HEADERS = {"User-Agent": "Mozilla/5.0 (dbt-analytics-portfolio extract)"}


def get_json(url: str, *, retries: int = 3, timeout: int = 25) -> dict:
    """GET a URL and parse JSON, retrying transient failures with backoff."""
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError) as err:
            last_err = err
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
    raise RuntimeError(f"GET failed after {retries} attempts: {url} ({last_err})")
