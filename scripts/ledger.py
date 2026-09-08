"""Mechanical edits to resources.yaml for the refresh skill.

Every subcommand reads ``--ledger`` (default resources.yaml) and, when it writes, writes to
``--out`` (default: the same file). Pass both to work on a scratch copy for a dry run.

Subcommands:
    urls            print entry URLs and claim source URLs for a selection (one per line)
    select          print the ids of entries that need a skeptic pass (stale or expiring)
    apply-urls      copy results from check_urls.py JSON into each entry's url_check
    skeptic-input   write the blind input file for the skeptic (no reasoning fields)
    add             append candidate entries from a researcher output file (skips known ids)
    apply-verdicts  merge a skeptic output file into the ledger
    annotate        apply compiler annotations (and nothing else)
    retire          mark one entry retired with a reason
    normalize       rewrite the ledger in canonical order and layout
    validate        filter researcher outputs into candidate files (fetched, on-domain, unique)

Selection flags (shared by urls, select, skeptic-input): ``--all``, ``--ids a,b``,
``--type podcast``, ``--stale DAYS``, ``--expiring DAYS``. Flags combine as a union.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "resources.yaml"
TYPES = ("podcast", "person", "tool", "course", "reading")
TYPE_ORDER = {t: i for i, t in enumerate(TYPES)}


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("version", 1)
    data.setdefault("entries", [])
    return data


def dump(data: dict, path: Path) -> None:
    data["entries"].sort(key=lambda e: (TYPE_ORDER.get(e.get("type"), 99), e.get("id", "")))
    text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )
    path.write_text(text, encoding="utf-8")


def parse_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def selected(entries: list[dict], args, today: date) -> list[dict]:
    if args.all:
        return list(entries)
    ids = set(s.strip() for s in (args.ids or "").split(",") if s.strip())
    chosen: dict[str, dict] = {}
    for entry in entries:
        if entry.get("status") != "active" and not ids:
            continue
        if entry["id"] in ids:
            chosen[entry["id"]] = entry
        if args.type and entry.get("type") == args.type:
            chosen[entry["id"]] = entry
        if args.stale is not None:
            lv = parse_date(entry.get("last_verified"))
            if lv is None or (today - lv).days > args.stale:
                chosen[entry["id"]] = entry
        if args.expiring is not None:
            for claim in entry.get("claims") or []:
                exp = parse_date(claim.get("expires"))
                if exp is not None and (exp - today).days <= args.expiring:
                    chosen[entry["id"]] = entry
    missing = ids - set(chosen)
    if missing:
        sys.exit(f"ledger: unknown id(s): {', '.join(sorted(missing))}")
    return list(chosen.values())


def add_selection_flags(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--all", action="store_true")
    sub.add_argument("--ids")
    sub.add_argument("--type", choices=TYPES)
    sub.add_argument("--stale", type=int, help="last_verified older than DAYS (or never)")
    sub.add_argument("--expiring", type=int, help="any claim expiring within DAYS")


def cmd_urls(args, data, today):
    seen: list[str] = []
    for entry in selected(data["entries"], args, today):
        for url in [entry.get("url")] + [c.get("source_url") for c in entry.get("claims") or []]:
            if url and url not in seen:
                seen.append(url)
    print("\n".join(seen))


def cmd_select(args, data, today):
    for entry in selected(data["entries"], args, today):
        print(entry["id"])


def cmd_apply_urls(args, data, today):
    results = {r["url"]: r for r in json.loads(Path(args.urls).read_text(encoding="utf-8"))}
    touched = 0
    for entry in data["entries"]:
        r = results.get(entry.get("url"))
        if r:
            entry["url_check"] = {"status": r["status"], "final_url": r["final_url"], "checked": r["checked"]}
            touched += 1
    for cand_file in args.candidates or []:
        path = Path(cand_file)
        cands = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        n = 0
        for c in cands.get("candidates") or []:
            r = results.get(c.get("url"))
            if r:
                c["url_check"] = {"status": r["status"], "final_url": r["final_url"], "checked": r["checked"]}
                n += 1
        path.write_text(yaml.safe_dump(cands, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
        print(f"ledger: url_check attached to {n} candidates in {path}")
    if not args.candidates:
        dump(data, args.out)
        print(f"ledger: url_check updated on {touched} entries -> {args.out}")


def blind_view(entry: dict) -> dict:
    return {
        "id": entry["id"],
        "type": entry.get("type"),
        "title": entry.get("title"),
        "url": entry.get("url"),
        "creator": entry.get("creator"),
        "annotation": entry.get("annotation"),
        "claims": [
            {"text": c.get("text"), "source_url": c.get("source_url")}
            for c in entry.get("claims") or []
        ],
        "url_check": entry.get("url_check"),
    }


def cmd_skeptic_input(args, data, today):
    entries = selected(data["entries"], args, today) if (args.all or args.ids or args.type or args.stale is not None or args.expiring is not None) else []
    views = [blind_view(e) for e in entries]
    for cand_file in args.candidates or []:
        cands = yaml.safe_load(Path(cand_file).read_text(encoding="utf-8")) or {}
        for c in cands.get("candidates") or []:
            views.append(blind_view({**c, "annotation": None}))
    Path(args.out).write_text(
        yaml.safe_dump({"today": today.isoformat(), "entries": views}, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    print(f"ledger: wrote blind skeptic input with {len(views)} entries -> {args.out}")


def new_entry(cand: dict, model: str, today: date) -> dict:
    return {
        "id": cand["id"],
        "type": cand["type"],
        "title": cand["title"],
        "url": cand["url"],
        "creator": cand.get("creator"),
        "annotation": None,
        "modules": list(cand.get("modules") or []),
        "status": "active",
        "first_added": today.isoformat(),
        "last_verified": None,
        "retired": None,
        "claims": [
            {"text": c["text"], "source_url": c["source_url"], "verdict": None, "checked": None, "expires": None, "quote": None}
            for c in cand.get("claims") or []
        ],
        "url_check": cand.get("url_check"),
        "researcher": {"model": model, "date": today.isoformat(), "origin": cand.get("origin") or "web search"},
        "skeptic": {"verdict": None, "reason": None, "model": None, "date": None},
        "owner_decision": None,
    }


def cmd_add(args, data, today):
    known = {e["id"] for e in data["entries"]}
    cands = yaml.safe_load(Path(args.candidates).read_text(encoding="utf-8")) or {}
    added, skipped = [], []
    for c in cands.get("candidates") or []:
        if c["id"] in known:
            skipped.append(c["id"])
            continue
        if c.get("type") not in TYPES:
            sys.exit(f"ledger: candidate {c['id']} has unknown type {c.get('type')!r}")
        data["entries"].append(new_entry(c, args.model, today))
        known.add(c["id"])
        added.append(c["id"])
    dump(data, args.out)
    print(f"ledger: added {len(added)} ({', '.join(added) or 'none'}); skipped known {len(skipped)} ({', '.join(skipped) or 'none'}) -> {args.out}")


def cmd_apply_verdicts(args, data, today):
    verdicts = yaml.safe_load(Path(args.verdicts).read_text(encoding="utf-8")) or {}
    by_id = {e["id"]: e for e in data["entries"]}
    applied, unknown = [], []
    for v in verdicts.get("verdicts") or []:
        entry = by_id.get(v["id"])
        if entry is None:
            unknown.append(v["id"])
            continue
        claims_by_text = {c["text"]: c for c in entry.get("claims") or []}
        for vc in v.get("claims") or []:
            claim = claims_by_text.get(vc.get("text"))
            if claim is None:
                continue
            claim["verdict"] = vc.get("verdict")
            if vc.get("source_url") and vc.get("verdict") == "Supported":
                claim["source_url"] = vc["source_url"]
            claim["checked"] = vc.get("checked") or today.isoformat()
            claim["expires"] = vc.get("expires")
            claim["quote"] = vc.get("quote")
        entry["skeptic"] = {
            "verdict": v.get("entry_verdict"),
            "reason": v.get("reason"),
            "model": args.model,
            "date": today.isoformat(),
        }
        if v.get("entry_verdict") == "Signed":
            entry["last_verified"] = today.isoformat()
        elif str(entry.get("last_verified")) == today.isoformat():
            entry["last_verified"] = None  # a same-day signature superseded by a later verdict
        applied.append(f"{v['id']}={v.get('entry_verdict')}")
    dump(data, args.out)
    print(f"ledger: applied {len(applied)} verdict(s): {', '.join(applied) or 'none'}; unknown ids: {', '.join(unknown) or 'none'} -> {args.out}")


def cmd_annotate(args, data, today):
    ann = yaml.safe_load(Path(args.annotations).read_text(encoding="utf-8")) or {}
    by_id = {e["id"]: e for e in data["entries"]}
    done, unknown = [], []
    for a in ann.get("annotations") or []:
        entry = by_id.get(a["id"])
        if entry is None:
            unknown.append(a["id"])
            continue
        entry["annotation"] = a["annotation"].strip()
        done.append(a["id"])
    dump(data, args.out)
    print(f"ledger: annotated {len(done)} ({', '.join(done) or 'none'}); unknown ids: {', '.join(unknown) or 'none'} -> {args.out}")


def cmd_retire(args, data, today):
    by_id = {e["id"]: e for e in data["entries"]}
    entry = by_id.get(args.id)
    if entry is None:
        sys.exit(f"ledger: unknown id {args.id}")
    entry["status"] = "retired"
    entry["retired"] = {"date": today.isoformat(), "reason": args.reason}
    dump(data, args.out)
    print(f"ledger: retired {args.id} -> {args.out}")


def registrable(url: str) -> str:
    host = (url or "").split("//", 1)[-1].split("/", 1)[0].lower()
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def cmd_validate(args, data, today):
    known = {e["id"] for e in data["entries"]}
    seen_ids: set[str] = set()
    seen_urls = {e.get("url") for e in data["entries"]}
    dropped: list[str] = []
    warnings: list[str] = []
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for research_file in args.research:
        research = yaml.safe_load(Path(research_file).read_text(encoding="utf-8")) or {}
        category = research.get("category")
        kept = []
        for c in research.get("candidates") or []:
            cid = c.get("id", "?")
            fetched = set(c.get("fetched") or [])
            urls = [c.get("url")] + [cl.get("source_url") for cl in c.get("claims") or []]
            reason = None
            if cid in known:
                reason = "id already in ledger"
            elif cid in seen_ids or c.get("url") in seen_urls:
                reason = "duplicate of another candidate or entry (same id or url)"
            elif c.get("type") != category:
                reason = f"type {c.get('type')!r} does not match category {category!r}"
            elif not c.get("claims"):
                reason = "no claims"
            elif any(u not in fetched for u in urls):
                reason = "url or source_url not in the researcher's own fetched list"
            if reason:
                dropped.append(f"{cid}: {reason}")
                continue
            off_domain = [u for u in urls[1:] if registrable(u) != registrable(c.get("url"))]
            if off_domain:
                warnings.append(f"{cid}: source host differs from entry host, skeptic decides primacy: {', '.join(off_domain)}")
            seen_ids.add(cid)
            seen_urls.add(c.get("url"))
            c.pop("notes", None)
            c.pop("draft_annotation", None)
            c.pop("fetched", None)
            kept.append(c)
        out = out_dir / f"candidates-{category}.yaml"
        out.write_text(yaml.safe_dump({"category": category, "candidates": kept}, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
        print(f"ledger: {category}: kept {len(kept)} -> {out}")
    for d in dropped:
        print(f"ledger: dropped {d}")
    for w in warnings:
        print(f"ledger: warning {w}")


def cmd_normalize(args, data, today):
    dump(data, args.out)
    print(f"ledger: normalized {len(data['entries'])} entries -> {args.out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--out", type=Path, help="write here instead of --ledger")
    parser.add_argument("--date", help="override today (YYYY-MM-DD)")
    subs = parser.add_subparsers(dest="cmd", required=True)

    s = subs.add_parser("urls"); add_selection_flags(s); s.set_defaults(fn=cmd_urls)
    s = subs.add_parser("select"); add_selection_flags(s); s.set_defaults(fn=cmd_select)
    s = subs.add_parser("apply-urls"); s.add_argument("--urls", required=True)
    s.add_argument("--candidates", nargs="*", help="attach to candidate files instead of the ledger"); s.set_defaults(fn=cmd_apply_urls)
    s = subs.add_parser("skeptic-input"); add_selection_flags(s)
    s.add_argument("--candidates", nargs="*"); s.add_argument("--out-file", dest="out", required=True); s.set_defaults(fn=cmd_skeptic_input)
    s = subs.add_parser("add"); s.add_argument("--candidates", required=True); s.add_argument("--model", default="sonnet"); s.set_defaults(fn=cmd_add)
    s = subs.add_parser("apply-verdicts"); s.add_argument("--verdicts", required=True); s.add_argument("--model", default="opus"); s.set_defaults(fn=cmd_apply_verdicts)
    s = subs.add_parser("annotate"); s.add_argument("--annotations", required=True); s.set_defaults(fn=cmd_annotate)
    s = subs.add_parser("retire"); s.add_argument("--id", required=True); s.add_argument("--reason", required=True); s.set_defaults(fn=cmd_retire)
    s = subs.add_parser("normalize"); s.set_defaults(fn=cmd_normalize)
    s = subs.add_parser("validate"); s.add_argument("--research", nargs="+", required=True); s.add_argument("--out-dir", required=True); s.set_defaults(fn=cmd_validate)

    args = parser.parse_args()
    if args.cmd not in ("skeptic-input", "validate") and args.out is None:
        args.out = args.ledger
    today = parse_date(args.date) or date.today()
    data = load(args.ledger)
    args.fn(args, data, today)
    return 0


if __name__ == "__main__":
    sys.exit(main())
