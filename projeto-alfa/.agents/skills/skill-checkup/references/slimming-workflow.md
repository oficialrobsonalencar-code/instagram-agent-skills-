# Slimming Workflow (global-pass operation — budget ceiling, compression order, safety protocol)

Operation doc, not an audit dimension: everything here applies to a **user-initiated
GLOBAL slimming pass** (or writing a brand-new description) — never to a single-skill
audit, where budget overflow is notify-only. Relocated verbatim from
`description-templates.md` (2026-07-15); the template/trigger dimensions stay there.

## The character budget: a shared, silent ceiling

Two independent limits (Claude Code; sources: issues #56710, #47627, v2.1.105 release notes):

- **Per description**: 1024 chars (portable agentskills.io spec); Claude Code ≥ 2.1.105 accepts up to 1536.
- **Whole listing, all sources combined** (global + project + plugin skills, plus slash commands): budget = **`skillListingBudgetFraction` (default 1%) × the CURRENT MODEL's context window**, converted to chars (≈ ×4). It is **dynamic, not a fixed char ceiling** — it scales with whatever model you are actually running (official docs: "the budget scales at 1% of the model's context window"). Rough sizes: a 200k-context model ≈ 8k chars at 1% / 16k at 2%; a **1M-context model ≈ 40k at 1% / 80k at 2%**. The old "≈8–16k absolute" figure is the 200k-era value baked into early versions (the fraction setting shipped in v2.1.129) — do not treat it as a frozen cap. On overflow Claude Code **drops entire descriptions and keeps names only** — no error, no warning; a name-only skill cannot auto-trigger. ⚠️ The budget tracks the *live* model, so a 200k-context sub-agent shrinks it back to the 8–16k band even if the main session is on 1M.
- Which skills keep their descriptions is **undocumented and not user-controllable** (#31505). Do not bet on priority — fit the budget with margin.

Measure before judging: `scripts/check_listing_budget.py [project_root]` sums every installed description and compares against the estimated budget.

Levers, in order of preference:
1. **Shorten descriptions** (free, robust — see the reconciliation rule below).
2. **Uninstall or merge** skills that rarely trigger.
3. **Raise the budget**: `{"skillListingBudgetFraction": 0.02}` in settings.json (v2.1.129+; costs ~11k extra tokens every session) or `SLASH_COMMAND_TOOL_CHAR_BUDGET=<chars>` env var.

Target bands: **≤ 300 chars** as the everyday default; **≤ 200 chars when ~40+ skills are installed**.

## When keyword coverage conflicts with the budget — budget wins

**Scope: this compression rule applies only to a user-initiated GLOBAL slimming pass, or when writing a brand-new description.** During a single-skill audit, budget overflow is notify-only — never shorten the audited skill's existing description on your own initiative (length is a population matter, not a single-skill defect).

The Seleznov template plus wide keyword coverage inflates descriptions toward 600–1000 chars. Over budget this self-defeats: a dropped description triggers at 0%, template or not. Compress in this order; the last item is untouchable:

1. Cut workflow hints, justifications, scope essays ("Out of scope: …" prose) — that is the body's job.
2. Cut synonym families down to the 2–3 forms the user actually types; keep bilingual triggers only for words the user really uses in both languages.
3. Shorten the negative constraint to one short clause.
4. Never cut: first-50-chars domain + core trigger keywords, "ALWAYS invoke", one negative constraint.

Compact Seleznov form (~150–250 chars, trigger power preserved):

```yaml
description: <Domain> expert. ALWAYS invoke when <2–3 concrete triggers, incl. the user's own words>. Do not <competing default> directly.
```

## Slimming safety protocol (mandatory during a global pass — machine-gated, no per-skill user confirmation)

The silent failure mode of slimming is identical to budget truncation: a cut trigger
word the user actually types → that phrasing never triggers again, no error. The user
is NOT asked to confirm each cut; safety comes from restricting what slimming is
allowed to be, then verifying it deterministically:

1. **Deletion-only, whole sentences.** Slimming = removing complete sentences of the
   safe class (provenance "Cloned from…", scope essays "Out of scope: …", workflow
   summaries, justification prose). Kept text stays verbatim — no rewriting, no
   paraphrasing, no merging. Trigger material (Triggers: lists, quoted phrasings,
   backticked tokens, "ALWAYS invoke", the negative constraint) is never touched.
2. **Deterministic gate, every skill.** Back up first (`cp SKILL.md SKILL.md.bak`),
   edit, then run `python3 <this-skill-dir>/scripts/check_desc_slim.py SKILL.md.bak SKILL.md`.
   Exit 1 (a kept sentence was rewritten, or a protected trigger span vanished) →
   restore the backup, do not negotiate with the gate. Exit 0 → keep; the removed
   sentences print as a log for later review, no approval needed.
3. **If the target band is unreachable by sentence-deletion alone, STOP** and report
   that skill to the user instead of escalating to rewrites — rewriting trigger
   sentences is exactly the risk this protocol exists to exclude.
4. **Post-batch verification.** Restart the session, re-run
   `scripts/check_listing_budget.py`, and confirm Step 2.6 shows descriptions injected.
5. **Ground-truth trigger regression (optional, costs real Claude runs).** For skills
   whose triggering matters most, use skill-creator's `scripts/run_eval.py` — it spawns
   real `claude -p "<query>"` subprocesses against the slimmed description and measures
   the actual trigger rate (queries live in an explicit evals.json the user can edit).
   That is the end-to-end test this protocol's static checks approximate; quote the run
   count before launching.
