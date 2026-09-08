# AI Resources for MSBA Students

A verified, periodically refreshed guide to learning about AI for business analytics students, built with MkDocs Material.

**Live site:** https://nkfreeman-teaching.github.io/ai-resources/

## What this is

The site collects podcasts, people, tools with student offers, courses, and readings that we recommend to MSBA students, organized as a sequenced learning path (biweekly enrichment modules) plus a reference catalog by resource type. Every entry clears the same bar before it is published. The link was fetched and found live, every factual claim cites a primary source (the vendor's or the author's own page) or was dropped, and an adversarial skeptic review attempted to refute the entry and failed. Each entry on the site shows the date it was last verified, and the complete verification record lives in `resources.yaml`.

## Repository structure

```
ai-resources/
├── resources.yaml                  Source of truth for every entry and its verification record
├── docs/                           Site source; generated blocks are rewritten from resources.yaml
│   ├── index.md
│   ├── path/                       Learning path (module pages)
│   └── catalog/                    Catalog pages by resource type
├── scripts/
│   ├── render.py                   Rewrites the generated blocks in docs/ (and checks them)
│   └── check_urls.py               URL liveness check used by the refresh skill
├── .claude/skills/refresh-ai-resources/   Claude Code skill that refreshes the content
├── mkdocs.yml
├── pixi.toml
└── .github/workflows/deploy.yml    Builds and deploys the site on push to main
```

## Environment

The project uses [pixi](https://pixi.sh). Install the environment once, then use the tasks below.

```bash
pixi install
pixi run serve      # live preview at http://127.0.0.1:8000
pixi run render     # rewrite generated blocks in docs/ from resources.yaml
pixi run check      # fail on stale or unrenderable blocks, then build strict
pixi run build      # build the static site (strict)
```

## Updating the content

Content changes go through the refresh skill rather than by hand, so that every entry carries a verification record. From Claude Code in this repository, run `/refresh-ai-resources` with one of the scopes listed in the skill (a full refresh, one category, a re-verification pass, or a single entry). The skill re-checks links, searches for new entries, runs a skeptic review on every new or changed entry, updates `resources.yaml`, re-renders the pages, and builds the site. It never commits. Review the diff, then commit and push.

Hand edits are appropriate for the prose on the module and catalog pages outside the generated blocks (the blocks are delimited by `<!-- resources: ... -->` and `<!-- /resources -->` markers and are overwritten on every render).

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the site (`mkdocs build --strict`) and deploys it to GitHub Pages.

**One-time repo setting:** GitHub → Settings → Pages → **Source: GitHub Actions**.
