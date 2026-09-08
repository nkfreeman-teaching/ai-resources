"""URL liveness check for the refresh skill.

Usage:
    python scripts/check_urls.py --in <urls.txt> --out <result.json> [--retry-delay 30]

Reads one URL per line (blank lines and lines starting with ``#`` are ignored), fetches each
with a browser-like User-Agent following redirects, and writes a JSON list of records:

    {"url", "status", "final_url", "title", "checked", "error", "retried", "class"}

``class`` is ``ok`` (200..399), ``blocked`` (401, 403, 429), or ``dead`` (anything else,
including DNS failure and timeouts). Records with status 0, 429, or 5xx are retried once after
``--retry-delay`` seconds. The script always exits 0; the caller decides what a result means.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import httpx

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0 Safari/537.36"
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
MAX_BODY = 200_000


def classify(status: int) -> str:
    if 200 <= status < 400:
        return "ok"
    if status in (401, 403, 429):
        return "blocked"
    return "dead"


def fetch(client: httpx.Client, url: str) -> dict:
    record = {
        "url": url,
        "status": 0,
        "final_url": None,
        "title": None,
        "checked": date.today().isoformat(),
        "error": None,
        "retried": False,
    }
    try:
        with client.stream("GET", url) as response:
            record["status"] = response.status_code
            record["final_url"] = str(response.url)
            content_type = response.headers.get("content-type", "")
            if "html" in content_type or "xml" in content_type or not content_type:
                body = b""
                for chunk in response.iter_bytes():
                    body += chunk
                    if len(body) >= MAX_BODY:
                        break
                match = TITLE_RE.search(body.decode(response.encoding or "utf-8", errors="replace"))
                if match:
                    record["title"] = html.unescape(re.sub(r"\s+", " ", match.group(1)).strip())
    except httpx.HTTPError as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="infile", type=Path, required=True)
    parser.add_argument("--out", dest="outfile", type=Path, required=True)
    parser.add_argument("--retry-delay", type=float, default=30.0)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    urls = []
    for line in args.infile.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line not in urls:
            urls.append(line)

    with httpx.Client(
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
        follow_redirects=True,
        timeout=args.timeout,
    ) as client:
        records = [fetch(client, url) for url in urls]
        to_retry = [i for i, r in enumerate(records) if r["status"] == 0 or r["status"] == 429 or r["status"] >= 500]
        if to_retry:
            print(f"check_urls: retrying {len(to_retry)} URL(s) after {args.retry_delay:.0f}s", file=sys.stderr)
            time.sleep(args.retry_delay)
            for i in to_retry:
                again = fetch(client, records[i]["url"])
                again["retried"] = True
                records[i] = again

    for record in records:
        record["class"] = classify(record["status"])

    args.outfile.parent.mkdir(parents=True, exist_ok=True)
    args.outfile.write_text(json.dumps(records, indent=2), encoding="utf-8")
    counts = {c: sum(1 for r in records if r["class"] == c) for c in ("ok", "blocked", "dead")}
    print(f"check_urls: {len(records)} URL(s) checked; ok={counts['ok']} blocked={counts['blocked']} dead={counts['dead']}; wrote {args.outfile}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
