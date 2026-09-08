---
name: refresh-ai-resources
description: "Refreshes the AI resources site for MSBA students: re-checks every link and claim in resources.yaml, searches each category for new entries with researcher subagents, runs an adversarial skeptic on every new or changed entry, updates the ledger, re-renders the site pages, and builds strict. Use whenever the owner asks to refresh, update, re-verify, or add to the AI resources, check for dead links or expired student offers, add an entry, a category pass, or a module, or run the resource skill. Manual only; never commits."
disable-model-invocation: true
argument-hint: "[full | category:<podcast|person|tool|course|reading> | reverify | entry:<id>] [dry-run] [--ledger <path>]"
---

# refresh-ai-resources

Produces one reviewable diff: an updated `resources.yaml` and the re-rendered generated blocks in
`docs/`. The owner reviews and commits. Fan-out is the expected mode of this skill: it dispatches
researcher, verifier, skeptic, and compiler subagents as described below, and the main session
adjudicates rather than researches. Model tiers are fixed by role. Sonnet researches, Haiku retries
blocked URLs, Opus refutes and writes prose. The inclusion bar is not negotiable: an entry reaches the
site only if its URL loaded, every claim is Supported by a primary source, and a skeptic signed it.
`scripts/render.py` enforces this in code, so nothing in this skill can publish an unsigned entry.

Read `~/.claude/references/nick-voice.md` only if you write site prose yourself; the compiler brief
carries a condensed version and the compiler does that writing.

## Paths and helpers

- Repo root: the directory containing `resources.yaml` (run everything from there).
- Scratch: `<scratchpad>/refresh-<YYYY-MM-DD>/`, where `<scratchpad>` is the session scratchpad
  directory. Nothing under it is ever committed.
- `pixi run python scripts/ledger.py <subcommand>` does every mechanical edit to the ledger
  (`urls`, `select`, `apply-urls`, `validate`, `skeptic-input`, `add`, `apply-verdicts`,
  `annotate`, `retire`, `normalize`). Never edit `resources.yaml` by hand except to record an `owner_decision`. Pass
  `--ledger <copy> --out <copy>` to every call in a dry run.
- `pixi run check-urls -- --in <urls.txt> --out <urls.json>` is the liveness script.
- Briefs live in `.claude/skills/refresh-ai-resources/agents/`. Every subagent is told to read its
  brief at that absolute path, follow it exactly, write its output file, and reply in a few lines.
- Today is `date +%F`. Pass it to every helper as `--date` so a run that crosses midnight stays
  consistent.

## 0. Preconditions

`git status --porcelain` must be empty (one refresh, one diff; refuse otherwise and say why).
`pixi run build` must be green before anything changes. Create the scratch directory.

## 1. Intake and scope

Read `resources.yaml`. Parse the argument. Default scope is `reverify`.

| Scope | URL check | Researchers | Skeptic on |
|---|---|---|---|
| `full` | all active entries | all five categories | new entries, changed entries, `select --stale 90 --expiring 30` |
| `category:<type>` | that type | that category | same, within the type |
| `reverify` | all active entries | none | `select --stale 90 --expiring 30` |
| `entry:<id>` | that entry | none, unless its URL died | that entry |

`dry-run` may be combined with any scope: copy `resources.yaml` to `<scratch>/resources.yaml`,
pass `--ledger <scratch>/resources.yaml --out <scratch>/resources.yaml` to every helper call, skip
phase 9, and finish by showing `diff -u resources.yaml <scratch>/resources.yaml`. `--ledger <path>`
without `dry-run` runs against that file in place (used for tests on a scratch copy).

State the scope in one line with counts: entries in scope, categories to search, entries already
due for a skeptic pass.

## 2. URL check, existing entries

```bash
pixi run python scripts/ledger.py urls <selection> > <scratch>/urls-existing.txt
pixi run check-urls -- --in <scratch>/urls-existing.txt --out <scratch>/urls-existing.json
pixi run python scripts/ledger.py apply-urls --urls <scratch>/urls-existing.json
```

Classes: `ok` (200..399), `blocked` (401, 403, 429), `dead` (404, 410, DNS failure, timeout after
the script's retry). Quote the summary line the script prints.

If any URL is `blocked`, write those URLs to `<scratch>/blocked.txt` and dispatch one verifier:

```
Agent(subagent_type: "general-purpose", model: "haiku", description: "Retry blocked URLs",
      prompt: "Read <abs>/agents/verifier.md and follow it exactly.
               urls_file: <scratch>/blocked.txt. output_file: <scratch>/verifier.yaml.")
```

A URL the verifier loaded is treated as live for the skeptic pass, with a note in the report that
the script was blocked. A URL neither could load is passed to the skeptic flagged as blocked; if the
skeptic cannot load it either, the entry is Unverifiable, never dead.

`dead` existing entries are listed by id for phase 3 (dead-link replacement) and, if unresolved
there, retired in phase 7.

## 3. Researchers (Sonnet), blind, one per category, one turn

Skip in `reverify` scope, and in `entry:` scope unless the entry's URL died. For each category in
scope, write `<scratch>/existing-<type>.yaml` (the active entries of that type: id, title, url,
creator) and dispatch all researchers in a single message so they run concurrently. No researcher
prompt mentions another researcher, the seeds of another category, or your own views.

```
Agent(subagent_type: "general-purpose", model: "sonnet", description: "Research <type>",
      prompt: "Read <abs>/agents/researcher.md and follow it exactly.
               category: <type>. existing_file: <scratch>/existing-<type>.yaml.
               seeds: <titles the owner named for this type, or none>.
               dead_links: <id, title, creator of dead entries of this type, or none>.
               output_file: <scratch>/research-<type>.yaml. today: <date>.")
```

When they return, validate every output file in one call:

```bash
pixi run python scripts/ledger.py validate --research <scratch>/research-*.yaml --out-dir <scratch>
```

It drops any candidate whose `url` or any `source_url` is absent from its own `fetched` list, whose
id or url already exists in the ledger or in another researcher's output, whose type does not match
its category, or that has no claims, and it writes the survivors to
`<scratch>/candidates-<type>.yaml` with `notes` and `draft_annotation` removed. A source on a
different host from the entry is a warning only, because a vendor's support site or a person's
newsletter platform is still primary and the skeptic decides primacy. Keep the dropped lines for the
final report. A researcher that returns `search_status: unavailable` or zero candidates is
re-dispatched once; if it is empty again, the category is reported as "not searched this run" and
its existing entries are left untouched.

## 4. URL check, candidates

Collect every candidate `url` and `source_url` into `<scratch>/urls-candidates.txt`, run the
liveness script, then the verifier on any `blocked` result, and attach the results:

```bash
pixi run check-urls -- --in <scratch>/urls-candidates.txt --out <scratch>/urls-candidates.json
pixi run python scripts/ledger.py apply-urls --urls <scratch>/urls-candidates.json --candidates <scratch>/candidates-*.yaml
```

Remove `dead` candidates from their candidates file with a one-line reason for the report.

## 5. Skeptics (Opus), blind, one per category, one turn

Build the blind input per category. It contains only id, type, title, url, creator, current
annotation (null for candidates), claim text and source URL, and url_check. No researcher notes, no
quotes, no prior skeptic reasoning.

```bash
pixi run python scripts/ledger.py skeptic-input <selection for existing entries due> \
    --candidates <scratch>/candidates-<type>.yaml --out-file <scratch>/skeptic-in-<type>.yaml
```

Batch at most eight entries per skeptic; split a large category into `-a`, `-b` files. Dispatch all
skeptics in one message:

```
Agent(subagent_type: "general-purpose", model: "opus", description: "Skeptic <type>",
      prompt: "Read <abs>/agents/skeptic.md and follow it exactly.
               input_file: <scratch>/skeptic-in-<type>.yaml. output_file: <scratch>/skeptic-<type>.yaml.")
```

A skeptic that errors or writes malformed YAML is re-dispatched once. If it fails again, its entries
are marked Unverifiable for this run with reason "skeptic pass failed", nothing is published or
retired on that basis, and the owner is told.

## 6. Adjudication, main session, at most two rounds

Follow this order and do not skip the first step.

1. **Verify before accepting.** For every `Refuted` and every `Unverifiable` verdict, fetch the
   cited source yourself with WebFetch and state in chat what the page says. Never accept a
   refutation you have not read. A skeptic that is right is confirmed in one line; a skeptic that is
   wrong gets round two.
2. **Agreement ledger in chat.** One table: id, skeptic verdict, your check, disposition. Signed
   entries you did not re-check are listed as "accepted on the skeptic's evidence".
3. **Round two.** Where your check contradicts the skeptic, re-dispatch that one skeptic with the
   same input plus `evidence: <what you found, with the URL>`. Its second verdict stands. There is
   no round three, and there is no publishing a Refuted entry.
4. **One owner question batch.** Use a single AskUserQuestion for everything that needs the owner:
   an owner-named seed that is Refuted or Unverifiable (options: apply the skeptic's proposed fix,
   supply a different primary URL and rerun that entry, retire it), each proposed retirement of an
   existing entry, and each category not searched this run. Every option states its concrete
   consequence on the site. Ask nothing else.

Apply skeptic fixes of kind `reword`, `add_condition`, `replace_source`, and `drop_claim` to the
candidates or entries, then re-run the skeptic on the fixed entries (this is the round-two dispatch;
fixed entries and contradicted verdicts go in the same batch).

## 7. Write the ledger

```bash
pixi run python scripts/ledger.py add --candidates <scratch>/candidates-<type>.yaml      # new entries
pixi run python scripts/ledger.py apply-verdicts --verdicts <scratch>/skeptic-<type>.yaml
pixi run python scripts/ledger.py retire --id <id> --reason "<reason>"                   # per retirement
```

`apply-verdicts` writes each claim's verdict, checked date, expiry, and quote, the skeptic block,
and sets `last_verified` only on Signed entries. An Unverifiable entry keeps its old `last_verified`
(the site shows the older date, which is honest). Record any owner decision by editing that entry's
`owner_decision` field with date, decision, and reason, then run `normalize`.

## 8. Compiler (Opus), one agent

Collect every entry that is Signed and has no annotation, or whose set of Supported claims changed
this run. Write `<scratch>/compile-in.yaml` with, per entry, id, type, title, creator, modules, and
only the Supported claims (text, expires). Add a `module` block only when the owner asked for module
prose. Dispatch:

```
Agent(subagent_type: "general-purpose", model: "opus", description: "Compile prose",
      prompt: "Read <abs>/agents/compiler.md and follow it exactly.
               input_file: <scratch>/compile-in.yaml. output_file: <scratch>/compile-out.yaml.")
```

Check every annotation against the voice rules in the brief (no em dash, no contraction, no second
person, at most 40 words) and against the claims, then:

```bash
pixi run python scripts/ledger.py annotate --annotations <scratch>/compile-out.yaml
```

Module prose, when produced, is pasted by you into `docs/path/module-NN.md` above the generated
block, and the page is added to `mkdocs.yml` nav and to `docs/path/index.md`.

## 9. Render and build

```bash
pixi run render && pixi run check
```

A red result stops the skill. Quote the failure, propose the fix, and do nothing else until the
owner or the fix resolves it. The usual causes are an id in a module block that is no longer
renderable (retired or unsigned) and a module reference to a page that does not exist; both are
named in the failure.

## 10. Present

Show `git diff --stat` and one table: added (id, type), retired (id, reason), changed (id, what),
Unverifiable (id, reason), categories not searched, candidates dropped before the skeptic (id,
reason). End with "Review the diff and commit." The skill never commits and never pushes.

## Edge cases

- **Existing entry, link dead.** Phase 2 marks it. Its category's researcher is asked to locate the
  current primary URL (`dead_links`). If found, the entry's `url` is updated and it goes to the
  skeptic as changed. If not, it is retired with reason "url dead on <date> after retry"; the
  renderer drops it from the site, and the ledger keeps it. If the id sits in a module block, phase
  9 fails by name and the owner batch asks whether to drop it from the module page.
- **Offer expired or terms changed.** The skeptic marks the claim Unsupported with a `reword` or
  `drop_claim` fix. If the entry keeps at least one Supported claim that justifies inclusion, the
  fix is applied, the entry is re-skepticked, and the compiler rewrites the annotation. Otherwise it
  is retired. A seed goes to the owner batch first.
- **Skeptic refutes an owner-named seed.** Never overridden silently. Verify the skeptic's evidence
  yourself, then put it to the owner with the proposed fix. Publishing the refuted claim is not
  offered; a change of claim wording the owner chooses is recorded in `owner_decision`.
- **Blocked pages (403, 429).** Script, then Haiku verifier, then the skeptic's own fetch. Three
  failures make the entry Unverifiable, never dead, and it keeps its old `last_verified`. The
  owner may paste page text into the session; record it in `owner_decision` as owner-supplied, which
  is weaker than a fetch and never counts as Supported.
- **Rate limits.** Dispatch fewer agents per message (three at a time) and continue. Never skip the
  skeptic to save time; skip the researchers instead and say so.
