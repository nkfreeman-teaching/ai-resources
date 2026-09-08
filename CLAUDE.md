# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

A public MkDocs Material site of verified AI learning resources for MSBA students, plus the Claude Code skill (`.claude/skills/refresh-ai-resources/`) that refreshes it. `resources.yaml` is the single source of truth for every entry and its verification record; the generated blocks in `docs/**/*.md` are rewritten from it by `scripts/render.py` and are never edited by hand. The site is deployed by `.github/workflows/deploy.yml` on push to `main`.

## Environment and commands

Use pixi for every Python operation. Never call bare `python` or `mkdocs`. Add dependencies in `pixi.toml`, not via pip.

```bash
pixi run serve        # live preview
pixi run render       # rewrite generated blocks from resources.yaml
pixi run check        # render --check, then mkdocs build --strict
pixi run build        # mkdocs build --strict
pixi run check-urls -- --in <urls.txt> --out <result.json>
```

There are no tests beyond `pixi run check`. CI installs mkdocs and mkdocs-material via pip and runs `mkdocs build --strict` only; rendering happens locally before commit so that the reviewed diff is what deploys.

## Rules for content

- Content changes go through `/refresh-ai-resources`. Do not add, edit, or remove entries in `resources.yaml` by hand except to record an owner decision the skill asked for.
- An entry renders only when `status: active`, `url_check.status` is 200..399, and `skeptic.verdict: Signed`. `render.py --check` fails by name when a module page references an unrenderable id.
- Every factual claim in an annotation must appear in that entry's `claims` with `verdict: Supported` and a primary `source_url` (the vendor's or the author's own domain).
- Prose on the site is in Nick's voice, general-audience register: formal "we", no contractions, no em dashes, no first-person singular, no second person (write "students", not "you"), `i.e.,` not `that is,`, `Thus,` not `Therefore,`, jargon named then glossed in parentheses on first use.
- Never commit from the skill. The owner reviews the diff and commits.
- No run logs, session notes, or changelog files. Git history is the changelog; the ledger keeps retired entries.

## File naming

Entry ids are kebab-case slugs (`ai-daily-brief`, `openai-chatgpt-plus-students`) and are never reused after retirement. Module pages are `docs/path/module-NN.md` with a two-digit number.
