"""Fetch every URL in config/probe_urls.txt and save status + body under data/raw/_probe/.

Runs on a GitHub runner (open internet). Stdlib only so it works before `make setup`.
Usage: python scripts/probe.py [urls_file] [out_dir]
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

MAX_BYTES = 3_000_000
UA = "Mozilla/5.0 (compatible; sovereign-debt-monitor/0.1; +https://github.com/hdcapital)"


def slug(url: str) -> str:
    host = re.sub(r"^https?://", "", url).split("/")[0].replace(".", "_")
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    return f"{host}__{h}"


def fetch(url: str) -> tuple[int, bytes, dict[str, str], str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
            body = resp.read(MAX_BYTES + 1)
            return resp.status, body, dict(resp.headers), resp.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read(MAX_BYTES + 1) if e.fp else b"", dict(e.headers or {}), url
    except Exception as e:  # noqa: BLE001
        return -1, repr(e).encode(), {}, url


def main() -> int:
    urls_file = Path(sys.argv[1] if len(sys.argv) > 1 else "config/probe_urls.txt")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "data/raw/_probe")
    out.mkdir(parents=True, exist_ok=True)
    urls = [
        line.strip()
        for line in urls_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    index: list[dict[str, object]] = []
    for url in urls:
        t0 = time.time()
        status, body, headers, final = fetch(url)
        truncated = len(body) > MAX_BYTES
        body = body[:MAX_BYTES]
        ctype = headers.get("Content-Type", headers.get("content-type", ""))
        ext = "json" if "json" in ctype else "csv" if "csv" in ctype else "html" if "html" in ctype else "bin"
        if ext == "bin" and body[:5] in (b"<!DOC", b"<html", b"<?xml"):
            ext = "html"
        name = slug(url)
        (out / f"{name}.{ext}").write_bytes(body)
        entry = {
            "url": url,
            "final_url": final,
            "status": status,
            "bytes": len(body),
            "truncated": truncated,
            "content_type": ctype,
            "file": f"{name}.{ext}",
            "seconds": round(time.time() - t0, 2),
            "head": body[:200].decode("utf-8", "replace"),
        }
        index.append(entry)
        print(f"{status:>4} {len(body):>9} {entry['seconds']:>6}s {url}")
    (out / "_index.json").write_text(
        json.dumps({"fetched_at": datetime.now(UTC).isoformat(), "results": index}, indent=1)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
