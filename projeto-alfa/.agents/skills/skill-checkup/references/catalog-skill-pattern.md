# Catalog-Skill Pattern (recommended structure for bulk-payload skills)

When a skill's payload is **many files the model cannot or should not read inline**
(binaries, big data, template packs — roughly > 20 items selected per task), do not
list them in SKILL.md and do not make the model scan the directory. Use this
pattern. Validated in production on two MATLAB template libraries (187 + 112
binary `.slx` payloads); as of 2026-07 no public skill ships this shape at that
scale — the closest prior art is `anthropics/skills` `theme-factory` (10 text
themes, inline list) and `canvas-design` (bare directory scan — the naive
baseline this pattern replaces).

## Structure — three tiers, budget declared

```
SKILL.md                     compass: lookup workflow + declared token budget (e.g. "≤3K tokens")
references/
  by-keyword.md              grep-able inverted keyword index → card links
  by-<axis>.md               optional grouped views (topology / purpose / …)
  index.md                   full-scan view (one row per item)
  cards/<Name>.md            one card per item: semantic metadata + payload path
  _data/<source>.yaml        SINGLE SOURCE OF TRUTH (all views generated from it)
scripts/build_catalog.py     regenerates every view from the source file
assets/<Item>/...            read-only payload
```

Lookup flow the SKILL.md must spell out: translate query → grep the inverted
index → Read 1–3 cards → payload path. Never "scan assets/".

## Iron rules

1. **Single source of truth.** All views (indexes + cards) are machine-generated
   from one data file; every generated file carries a "Do not hand-edit" header.
   Hand-added knowledge goes into the source file (e.g. a `card_notes` field the
   builder renders) — writing into a generated card is a drift bomb: the next
   rebuild silently reverts it.
2. **Skill-root-relative real paths.** Cards carry `assets/<Item>/<file>.<ext>` —
   no placeholders (`${VAR}`), no absolute paths. The reader prepends the skill
   directory it already knows. Portable with zero edits; checker-verifiable.
3. **Build-time drift gate, both directions.** The builder FAILS if a card's
   payload file is missing on disk (forward audit), and WARNS on payload dirs
   with no catalog record (reverse audit — items invisible to lookup). This is
   the only reliable drift defense: generated views cannot be audited by eye.
4. **Declare `routes-exempt` for bulk payload.** Frontmatter
   `metadata: routes-exempt: assets/**, references/_data/**` keeps
   check_routes.py's orphan walk honest (skip count is printed). Never exempt
   rule references or scripts the model must find.
5. **Payload read-only; customize on a copy** (copy to workdir first).
6. **Document the depth deviation.** This chain is 2 routing hops
   (SKILL.md → index → card) — the hard cap, and deeper than agentskills.io's
   "one level deep" advice. State in the skill's maintenance doc that the
   deviation is intentional, with the token math (flat listing cost vs indexed
   lookup budget). The card → payload hop is data addressing, not a doc route.

## When NOT to use

- Few items (≤ ~10): an inline list in SKILL.md is cheaper (theme-factory shape).
- Payload is readable text the model should just Read: normal references/ routing.
- Items are never selected individually (always used together): one asset bundle.

## Audit hooks

When auditing a skill of this shape: run its builder (must exit 0), check rule 1's
headers exist, spot-check one card's payload path resolves, and confirm the
declared token budget is honest (grep + 1–3 cards actually fits it).
