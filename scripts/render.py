"""Rewrite the generated resource blocks in docs/**/*.md from resources.yaml.

Usage:
    python scripts/render.py            # rewrite blocks in place
    python scripts/render.py --check    # exit 1 if any block is stale or unrenderable

A block is delimited by ``<!-- resources: KEY=VALUE -->`` and ``<!-- /resources -->``.
KEY is ``type`` (every renderable entry of that type, sorted by title) or ``ids`` (a
comma-separated list rendered in the given order). An entry is renderable only when it is
active, its URL check passed, and a skeptic signed it. An ``ids`` block that names a missing
or unrenderable id is an error, as is a module reference to a module page that does not exist.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "resources.yaml"
DOCS = ROOT / "docs"

BLOCK_RE = re.compile(
    r"<!-- resources: (?P<spec>[^>]+?) -->\n(?P<body>.*?)<!-- /resources -->",
    re.DOTALL,
)

TYPE_LABELS = {
    "podcast": "Podcast",
    "person": "Person",
    "tool": "Tool",
    "course": "Course",
    "reading": "Reading",
}


class RenderError(Exception):
    pass


def load_entries(ledger: Path) -> dict[str, dict]:
    data = yaml.safe_load(ledger.read_text(encoding="utf-8")) or {}
    entries = data.get("entries") or []
    by_id: dict[str, dict] = {}
    for entry in entries:
        entry_id = entry.get("id")
        if not entry_id:
            raise RenderError("an entry in resources.yaml has no id")
        if entry_id in by_id:
            raise RenderError(f"duplicate id in resources.yaml: {entry_id}")
        by_id[entry_id] = entry
    return by_id


def unrenderable_reason(entry: dict) -> str | None:
    if entry.get("status") != "active":
        return f"status is {entry.get('status')!r}, not 'active'"
    status = (entry.get("url_check") or {}).get("status")
    if not isinstance(status, int) or not 200 <= status < 400:
        return f"url_check.status is {status!r}, not in 200..399"
    verdict = (entry.get("skeptic") or {}).get("verdict")
    if verdict != "Signed":
        return f"skeptic.verdict is {verdict!r}, not 'Signed'"
    if not entry.get("annotation"):
        return "annotation is empty"
    if not entry.get("last_verified"):
        return "last_verified is empty"
    return None


def module_link(module: int, page: Path) -> str:
    target = DOCS / "path" / f"module-{module:02d}.md"
    if not target.exists():
        raise RenderError(
            f"{page.relative_to(ROOT)} references module {module}, but "
            f"{target.relative_to(ROOT)} does not exist"
        )
    rel = os.path.relpath(target, page.parent)
    return f"[Module {module}]({rel})"


def render_entry(entry: dict, page: Path) -> str:
    label = TYPE_LABELS.get(entry["type"], entry["type"].title())
    parts = [f"**{label}**, {entry['creator']}. {entry['annotation'].strip()}"]
    modules = [m for m in (entry.get("modules") or [])]
    links = []
    for module in modules:
        target = DOCS / "path" / f"module-{module:02d}.md"
        if target.resolve() == page.resolve():
            continue
        links.append(module_link(module, page))
    if links:
        parts.append("Featured in " + ", ".join(links) + ".")
    parts.append(f"*Last verified {entry['last_verified']}.*")
    return f"### [{entry['title']}]({entry['url']})\n\n" + " ".join(parts) + "\n"


def select_entries(spec: str, by_id: dict[str, dict], page: Path) -> list[dict]:
    key, _, value = spec.strip().partition("=")
    if key == "type":
        chosen = [e for e in by_id.values() if e.get("type") == value and not unrenderable_reason(e)]
        return sorted(chosen, key=lambda e: e["title"].lower())
    if key == "ids":
        chosen = []
        for entry_id in [s.strip() for s in value.split(",") if s.strip()]:
            entry = by_id.get(entry_id)
            if entry is None:
                raise RenderError(f"{page.relative_to(ROOT)}: id {entry_id!r} is not in resources.yaml")
            reason = unrenderable_reason(entry)
            if reason:
                raise RenderError(f"{page.relative_to(ROOT)}: id {entry_id!r} is not renderable ({reason})")
            chosen.append(entry)
        return chosen
    raise RenderError(f"{page.relative_to(ROOT)}: unknown block spec {spec!r}")


def render_page(text: str, by_id: dict[str, dict], page: Path) -> str:
    def replace(match: re.Match) -> str:
        spec = match.group("spec")
        entries = select_entries(spec, by_id, page)
        if entries:
            body = "\n".join(render_entry(e, page) for e in entries)
        else:
            body = "*No entries yet.*\n"
        return f"<!-- resources: {spec} -->\n{body}<!-- /resources -->"

    return BLOCK_RE.sub(replace, text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report stale blocks, change nothing")
    parser.add_argument("--ledger", type=Path, default=LEDGER, help="alternate resources.yaml")
    args = parser.parse_args()

    try:
        by_id = load_entries(args.ledger)
    except (RenderError, yaml.YAMLError) as exc:
        print(f"render: {exc}", file=sys.stderr)
        return 1

    stale: list[str] = []
    rewritten: list[str] = []
    errors: list[str] = []
    for page in sorted(DOCS.rglob("*.md")):
        original = page.read_text(encoding="utf-8")
        if "<!-- resources:" not in original:
            continue
        try:
            updated = render_page(original, by_id, page)
        except RenderError as exc:
            errors.append(str(exc))
            continue
        if updated != original:
            if args.check:
                stale.append(str(page.relative_to(ROOT)))
            else:
                page.write_text(updated, encoding="utf-8")
                rewritten.append(str(page.relative_to(ROOT)))

    for err in errors:
        print(f"render: {err}", file=sys.stderr)
    if args.check:
        for path in stale:
            print(f"render: stale generated block in {path} (run `pixi run render`)", file=sys.stderr)
        if not errors and not stale:
            print("render: all generated blocks are current")
        return 1 if (errors or stale) else 0
    for path in rewritten:
        print(f"render: rewrote {path}")
    if not rewritten and not errors:
        print("render: nothing to change")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
