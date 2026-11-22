---
name: skill-checkup
description: Skill quality + package structure expert. ALWAYS invoke when creating, editing, reviewing, or restructuring any skill (SKILL.md, references/, scripts/, routing, indexes), when a skill won't trigger or is bloated, or on 审查/体检/修复/重构/拆分 skill、skill 不触发、太臃肿. Do not modify or split a skill directly — use this skill first.
metadata:
  compass-cap: 7500
---

# Skill Checkup

Diagnose and improve any SKILL.md. **A compass, not a manual** — standards live in `references/`.

**Role — delivery auditor.** A skill is not its text; it is the probability that each rule reaches the model's attention at the moment it applies. Every finding serves that quantity, through four lenses: **harness** (what is injected when: desc every turn, body on trigger, references only via Read), **model** (economizing bias, context decay, silent skips), **hard code** (scripts enforce what prose cannot), **structure** (routing, roster, receipts).

## Diagnosis flow (each step must print)

> Silent steps get skipped (Seleznov, 2026) — print one confirmation line per step.
> **Self-review flag**: if this session already Edited/Written the target SKILL.md, **prefix every skill-checkup print line with `[self-review]`**, and a fresh sub-agent blind re-audit **MUST run before the work is declared done** — spawn it with explicit file paths and NO expected findings (procedure + multi-target scaling: `runtime-contract.md` §4), then print:
> `[skill-checkup] self-review re-check: <agent> → <verdict summary>`
> If it cannot run, say so explicitly and mark the work **unverified** — silence is not an option.

### Step 1: Read the target, run the three checkers

**Create shape (no target exists yet)** → hand drafting to `skill-creator`, print `[skill-checkup] create: no target — drafting → skill-creator, checkup resumes on the draft`, and resume here once the draft lands.
Read the target SKILL.md in full, then run the three checkers via `python3 <this-skill-dir>/scripts/…` (quote paths — spaces are common): `check_listing_budget.py "<project_root>" --target "<skill_name>"`, `check_routes.py "<skill_dir>"`, `check_script_safety.py "<skill_dir>"`. All three run EVERY audit; compass-cap/dangling/orphan hits = P1. Print five lines:
```
[skill-checkup] Auditing: <path>  body=<N> lines  description=<M> chars
[skill-checkup] Budget: <K> skills installed, descriptions <T> chars vs ≈<B> → <fits | OVERFLOW ×N.N>
[skill-checkup] Overlap: <clean | N pair(s), M with target>
[skill-checkup] Routes: <PASS | N issue(s): compass-over/dangling/orphan>
[skill-checkup] Safety: <clean | N hit(s): <classes>>
```
Budget exit 2 = unavailable → fallback row. Tiering: overflow & non-target overlap = NOTICE only; target overlap = P2 (`description-templates.md` §distinctness); safety hits = P0 when CRIT, else P1, pending legitimacy (`hard-code-vs-llm-judgment.md`); Safety clean → receipt line only, never a report line. **Never edit the audited skill for a population notice; never auto-delete a safety hit** (slimming = user-run global pass).

### Step 2: Roster the dimensions, then read ONE at a time

Run `python3 <this-skill-dir>/scripts/index.py "<skill_dir>"` — it measures the target and prints the dimension roster (FORCED / DEFAULT / SKIP + reasons) plus a `MODE=` line. The script is authoritative for firing; `references/index.md` is its human-readable mirror — don't re-judge firing from prose.
MODE=inline → loop the roster one file per iteration: Read it → judge the target against ONLY that dimension → print a receipt → next file. DEFAULT skips must cite the roster's printed skip condition. MODE=fanout → `runtime-contract.md` §4.
```
[skill-checkup] <dimension>: <N> findings
```

### Step 2.5: Dry-run walkthrough (positive walk when ordered-steps=True; negative ALWAYS)

Following `references/effect-dry-run.md`, take one typical prompt PER task shape the description promises (write / revise / check / restructure — one per promised shape; small-scope revise prompt mandatory for editing skills). Walk each through the body steps: input/instruction/output connect, AND which hard gates fire at that granularity.
Any broken link / ambiguity / gate no common shape triggers → **P0**, into Step 3's Code layer.
Print one line per prompt:
```
[skill-checkup] Dry-run "<prompt>" (shape: <write|revise|check|restructure>)  broken links=<N>  gates fired=<M>/<total>
```
No ordered process at all (pure rule / reference skill) → print:
```
[skill-checkup] Dry-run: positive walk skipped (no workflow)
```
ALWAYS (workflow or not): judge 1–2 should-NOT-trigger prompts against the description alone, per `effect-dry-run.md` §negative. Captured → **P2 `[over-trigger]`**. Print:
```
[skill-checkup] Dry-run negative: <K> prompts, false-fire=<J>
```

### Step 2.6: Live-injection check (when the target is in this session's scope)

Does the target appear in this session's available-skills list **with its description** (not name-only)? 3 cases + population-notice rule → `references/live-injection-check.md`. Print one line:
```
[skill-checkup] Live-injection: <injected | DROPPED (name-only) | skipped (<reason>)>
```

### Step 3: Output the diagnosis report

Present per `references/output-format.md` — a **layered report in lesstoken style, in the user's reply language**: verdict → quality scores → **Code layer** (P0→P3, file:line evidence) → **Decision layer** split **✅ Safe to fix now** vs **🤔 Needs your decision** → closing question.

Substance that fills the layers:
- Each finding: stable ID (`P0-1` …), specific line/field, risk 🟢/🟡/🔴, sorted P0→P3 (`references/priority-tiers.md`); same violation in N places = N findings; the same defect from two dimensions = dedup to one before tiering.
- **Name the failure mode** when one applies — a `predictability-glossary.md` label: `[no-op]`/`[sediment]`/`[premature-completion]`/`[weak-leading-word]`/`[duplication]`/`[sprawl]`/`[over-trigger]`/`[no-floor]`/`[gate-gap]`/`[missing-license]`. Prefix = what kind, P-tier = how bad.
- Each 🤔 item separates **mechanism** (behavior now) from **consequence** (what the next LLM does wrong), then options + rec.

### Step 4: Apply with Edit after user confirmation

**Never** Edit without confirmation — wait for the user's "fix it".

Before acting: **size gate** + **pre-deletion check**; afterwards **close the loop** — procedure in `references/apply-safety.md`.
After fixing, print one line:
```
[skill-checkup] Applied <N> fixes to <path>  body: <old>→<new> lines (<+X%>)
```

## Hard rules quick reference

Quantified hard rules (violation = error) → `references/hard-rules.md`, consult every audit.

## Exception fallback

When a path is missing, YAML won't parse, or any bundled script under `scripts/` is missing or exits 2 — handle per `references/exception-fallback.md` (authoritative script list lives there); announce first, never silently skip.

## Language

Default English; flag unjustified non-English ⚠️; policy + 2 exceptions → `references/language-policy.md`.

## Out of scope

Domain correctness of content (logic bug, not form — runtime *behavior* IS in scope → `runtime-contract.md`); project conventions (→ CLAUDE.md); one-off fix scripts.

## Why it exists

LLMs write manuals; the mechanical-vs-judgment split: `references/rationale.md`.
