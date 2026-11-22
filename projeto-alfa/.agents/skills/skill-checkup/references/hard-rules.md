# Hard rules quick reference (a violation is an error, not a suggestion)

| Rule | Source |
|------|--------|
| description ≤ 1024 chars (portable spec; Claude Code ≥ 2.1.105 accepts 1536) | Anthropic spec / CC v2.1.105 release notes |
| listing-budget overflow (shared pool ≈ 1% of context; overflow = silent name-only truncation, auto-trigger dies) is always **reported** — population-level fact; remedied only by a user-initiated global pass, never by editing the audited skill | CC issues #56710 / #47627 |
| description in third person | Anthropic best-practices |
| name uses only lowercase letters + digits + hyphens | Anthropic spec |
| body < 500 lines | Anthropic / community consensus |
| routing depth ≤ 2 hops (SKILL.md → index.md → file); nested indexes forbidden — the third hop is where LLM recall dies | structure-surgery.md (hardened from practice) |
| zero dangling routes / zero orphan subdocuments (verify with `scripts/check_routes.py`) | structure-surgery.md iron rule 3 |
| YAML description on a single logical line (no `>` `|`) | Prettier reflow will break it |
| every step of a multi-step workflow must produce visible output | Seleznov's second problem |
| `check_routes.py` runs on EVERY audit (Step 1), never only when a structure dimension fires; its compass-cap / dangling / orphan hits are P1 findings | hardened 2026-07-02: three writing skills carried 9 route issues through repeated audits because the script was conditionally routed |
| dry-run = one prompt per task shape the description promises (never drop a promised shape), small-scope revise prompt mandatory for editing skills; a hard gate no common shape triggers = P0; plus 1–2 should-NOT-trigger prompts judged against the description alone on EVERY audit (workflow or not) — capture = P2 `[over-trigger]` | hardened 2026-07-02; negative half added 2026-07-03: positive-only dry-runs never test the over-trigger side |
| description overlap check runs with the budget check on EVERY audit (`check_listing_budget.py --target`); pairs involving the audited skill = P2, all other pairs = population notice — never edit either side uninvited, intentional siblings judged for intent | added 2026-07-03: routing collisions are population-level, invisible to single-skill review (skill-distill: overlap → routing ~49%) |
| `check_script_safety.py` runs on EVERY audit; hits = P0 when CRIT, else P1, pending legitimacy judgment (mechanical detection, semantic conviction — `hard-code-vs-llm-judgment.md`); never auto-delete a flagged line | added 2026-07-03: bundled-script & prose injection surface (Snyk: 36.82% of public skills carry injection patterns) |
| dimension firing = `scripts/index.py` output (mechanical measurement), never re-judged from index.md prose; DEFAULT skips must cite the roster's printed skip condition | hardened 2026-07-02: when-to-read judgment loading silently skipped dimensions — even an `always` entry — whenever the task felt fuzzy |
| a session that Edited/Wrote the target MUST run the fresh-agent blind re-audit before declaring done (receipt: `self-review re-check:` line; explicit paths, no expected findings); cannot-run → state it and mark unverified; when the GLM channel is available, ALSO run the cross-model second opinion (`scripts/glm_blind_audit.py`, procedure `runtime-contract.md` §4) — its unavailability (exit 2) appends `(cross-model unavailable)` to the receipt, it never alone marks the work unverified | owner decision 2026-07-02 (fresh agent) + 2026-07-03 (cross-model): same-model review keeps model bias — Claude-written rules look fine to Claude |
| prefer `references/` `scripts/` `assets/`; custom dirs (`agents/`, `evals/`) also allowed | agentskills.io spec (`...` = any additional files/dirs) |
| a skill's claim about its **own** performance/validation (verified / tested / "N% accurate" / "N iterations") must point to in-repo evidence (`evals/` or `reports/`) or be cut/softened; plain functional descriptions (creates / measures / optimizes X) are exempt — the anchor is *asserting the skill's own validated status*, not the presence of a performance word | evidence-gating (best-practices) |
