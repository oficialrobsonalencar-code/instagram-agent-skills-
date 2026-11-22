# Runtime Contract (load floor · gate granularity · edit license)

Three checks on how the skill behaves when it actually runs inside a real session. A skill can be form-perfect — clean routing, compass-sized, well-triggered — and still fail all three invisibly: it fires, looks applied, and changes almost nothing. The owner's symptom is always the same sentence: *"it triggers, but the result feels shallow."*

Shared root cause: SKILL.md is a compass; the real rules live in `references/`. At run time the model weighs reading cost against the task and silently economizes, and the surrounding environment (global CLAUDE.md discipline, user feedback memories) pushes toward minimal diffs. Each check pins down one way that hollows out the skill's effect.

## 1. Load floor — the mandatory minimal read-set  `[no-floor]`

**Classify before you floor.** References are not all consumed the same way. Label each reference file — never the whole skill; hybrids are the norm — by one question: **if this file were skipped on a run where it mattered, would the failure be silent?**

| Mode | Skip test | Correct mechanism |
|------|-----------|-------------------|
| **Lookup** | relevance is decidable from the task before reading; a wrong skip is visible or harmless | routing: when-to-read + keywords + ≤2 hops (`structure-surgery.md`). Forcing a full read here is waste, not rigor. |
| **Checklist** | wrong skip = silent miss; content is discrete items (audit rules, review dimensions) | enumerated roster (script when the facts need measuring) + one-item-per-iteration receipts + rule-gated skips only — the §4 pattern. |
| **Immersion** | wrong skip = silent quality loss; content is holistic (voice samples, a spec held as background) | full read with a printed read-receipt; re-read on long tasks (context decay); post-hoc output-vs-material check where itemizable. Weakest standard of the three — absorption has no mechanical proof; prescribe these levers and say so. |

The risk is misclassification, not a missing mode — checklist/immersion content labeled lookup fails silently. Unsure → classify away from lookup.

A heavy-reference skill (> ~30 KB of rule references, or > ~4 rule files) must state which references are MANDATORY per task size — and the floor must respect each file's mode: lookup content scales with the task ("paragraph-level polish → read A §x + B §y"); checklist/immersion content is the FULL set on every run it fires. A size-scaled floor over exhaustive content is itself `[no-floor]`.

- Absent floor → the model picks a different subset each run → depth varies run to run. The greppable rules (cheap to verify) get applied; the judgment rules (expensive, need the full reference) silently don't → output looks compliant but is shallow.
- **Test:** take the smallest common task. From the SKILL.md alone, can you name exactly which files MUST be read for it? If not → **P2 `[no-floor]`**. A checklist/immersion file that drops out of the floor on small tasks is the same finding.
- Fix pattern — two tiers, chosen by where the deciding facts live:
  - **Facts already in the user's request** (task size / content type) → a static 2–4 row "task size → mandatory read-set" table in SKILL.md. No script — SKILL.md is guaranteed-visible after triggering; a static table there is the cheapest reliable roster.
  - **Facts that must be measured from files** (the target varies per run) → ship `scripts/index.py`, paired with `references/index.md`: it measures the target, evaluates each row's fire condition, prints the roster (FORCED / DEFAULT / SKIP + reasons) and a final `MODE=` line. The script is authoritative for firing; index.md stays the human-readable mirror. Prose like "if X then read Y" in SKILL.md does NOT substitute here — whether X gets measured, and measured honestly, is itself left to the model.

## 2. Gate granularity — do the quality gates fire on everyday tasks  `[gate-gap]`

List every hard gate the skill declares: script runs, checklists, review passes, cross-skill handoffs ("after writing, have X re-check"), anything "must run before declaring done". For each gate, name the task granularity that triggers it. Then check the most common SMALL task shape against that list.

- Typical failure: every gate is keyed to the big shape ("after finishing a chapter") → the everyday section-level edit passes through ZERO gates; silent cross-skill handoffs skip the same way (nothing prints, nothing enforces).
- **Test:** for the small-scope prompt from `effect-dry-run.md` §1, count the gates that fire. Zero → **P0 `[gate-gap]`** (quality machinery exists but never runs on the common path).
- Fix pattern: rescope gates to "any edit of kind K" (scripts are usually seconds — cost is not a reason to gate rarely) + one visible print line per gate so a skipped gate is visible.

## 3. Edit license — authority vs the environment's conservatism  `[missing-license]`

A skill's instructions do not run in a vacuum. Global CLAUDE.md discipline (surgical edits only, no drive-by rewrites), "don't over-edit" feedback memories, and the model's own default timidity all pull toward MINIMAL token-level diffs. If the skill's mission requires more aggression than that default — recomposing sentences for voice, restructuring paragraphs, deep rewrites — the skill must EXPLICITLY grant the license and bound it: what may be rewritten, what is invariant (facts / symbols / content / citations), and what evidence to show per unit.

- Absent license → the environment wins every time; the model does token-level tweaks (swap a connector, delete a banned word) and reports success → the owner feels "it triggered but nothing really changed".
- **Test:** does any line grant rewrite authority stronger than the global default AND state its bounds? If the skill's whole point implies deep edits and no such line exists → **P2 `[missing-license]`**.
- Fix pattern: one blast-radius clause, e.g. "voice pass = sentence-level recomposition allowed; content, facts, symbols invariant; per paragraph, state what was recomposed or why the original was kept."

## 4. Dispatch modes — inline vs fanout (≤4 subagents)

- **MODE=inline** (roster ≤ ~45 KB, single target) — the main conversation loops the roster ONE file per iteration: Read → judge that dimension only → print the receipt → next. Just-in-time reading binds each rule while it is fresh; batch pre-loading lets early files decay into background noise by the time they are applied. Close the loop with a terminal receipt reconciled against the roster's own count — `[skill-checkup] roster complete: <N>/<N> dimensions judged` — a per-file loop without the closing count invites stopping early and calling it done.
- **MODE=fanout** (heavier roster, or multiple targets) — bundle dimensions by theme (or one bundle per target) into **≤3 subagents**, each given ONLY its bundle's reference files + the target path; the main conversation merges, dedups cross-bundle duplicates, reports. NEVER one agent per dimension — every spawn re-pays the system-prompt / tool-schema / skill-listing overhead, so bundles must be few and fat. Print one receipt per returned bundle — `[skill-checkup] bundle <name>: <N> findings` — and if a bundle errors, truncates, or returns nothing, announce it and re-run or mark its dimensions missing; a silently dropped bundle un-proves every dimension it carried.
- The **4th agent slot is the self-review blind re-check — MANDATORY** (owner decision 2026-07-02): whenever this session authored or edited the target, a fresh agent MUST re-run the audit before the work is declared done. Prompt it with **explicit file paths** (never rely on the sub-agent's own skill listing — it differs from the main session's) and NO expected findings. Many edited targets go into ONE blind agent, or a representative sample if the batch would blow its context — total agents stay ≤4. Receipt line in the main session: `[skill-checkup] self-review re-check: <agent> → <verdict>`. If it cannot run (no Agent tool, user vetoed the cost), print that explicitly and mark the work **unverified** — a silent skip of this gate is itself the disease this skill treats.
- **Cross-model second opinion — run alongside the fresh agent** (owner decision 2026-07-03): a fresh agent on the SAME model removes seen-the-answer contamination but not model bias — rules written by Claude tend to look fine to Claude. Run `python3 <this-skill-dir>/scripts/glm_blind_audit.py "<target_dir>"`: it bundles the package into one glm-5.2 call and prints an independent opinion verbatim. Merge its findings like any auditor's (dedup against the fresh agent's, tier per `priority-tiers.md` — GLM proposes, the main session convicts). Receipt becomes: `[skill-checkup] self-review re-check: <agent> + glm-5.2 → <verdicts>`. Script exit 2 (no key / network) → the same-model re-audit still stands; append `(cross-model unavailable)` to the receipt — this alone does NOT mark the work unverified.
- **When auditing OTHER skills, prescribe this same pattern.** A heavy-reference skill with neither tier (no static table, and no index.py where its deciding facts need measurement) is exactly the `[no-floor]` finding — recommend the tier matching where its facts live, plus the one-file-per-iteration receipt loop, plus these dispatch modes if it fans out subagents. An exhaustive-mission skill (audit / checklist / style-imitation — index.py prints `exhaustive=True`) needs the roster + receipts at ANY reference size, not just past 30 KB.

## Reporting

Prefix findings `[no-floor]` / `[gate-gap]` / `[missing-license]` (registered in `predictability-glossary.md`'s label list); assign tiers per `priority-tiers.md`. These are effect findings: the evidence is a SKILL.md line — or the absence of one (cite the section where it should live); the consequence is what the next run does wrong. Absence-of-a-line findings still get a location: the section that should carry the missing clause.
