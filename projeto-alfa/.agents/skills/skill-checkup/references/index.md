# Skill-Checkup Reference Index

The router for every skill-checkup subdocument. Each entry carries `when-to-read:`
(the scenario that should fetch it, in the user's own words) and `keywords:` (the
searchable surface). Step 2 loads from **Dimensions** by condition; **Workflow &
policy** docs are pulled by the step or section that names them.

## Dimensions (Step 2 — firing decided by the roster script index.py under the skill's scripts dir; it measures the target and prints the roster + MODE)

**This section is the human-readable mirror and retrieval surface; the script is authoritative.** When adding or retiring a dimension, update BOTH: the entry here (when-to-read + keywords) and its fire condition in the script — a row in only one place will drift.

- [description-templates.md](description-templates.md) — trigger-strength template + distinctness (budget & slimming ops relocated to their own workflow doc).
  when-to-read: always; writing or fixing a description, or a skill that won't auto-fire.
  keywords: description, trigger, ALWAYS invoke, first-50-chars, negative constraint, third person, empty phrasing, overlap, distinctness, routing collision, sibling skill.
- [body-quality-checklist.md](body-quality-checklist.md) — when the body is too long and what to demote.
  when-to-read: body over ~100 lines or visibly bloated; deciding what moves from SKILL.md into references.
  keywords: body size, 500 lines, splitting decision, bloat, anti-patterns, when-to-use-in-body.
- [visible-output-rule.md](visible-output-rule.md) — every workflow step must print something.
  when-to-read: FORCED whenever the body has any ordered multi-step process (Step/Phase/station/pipeline/gate chain — wording irrelevant) OR the mission is exhaustive (per-item receipts required), per SKILL.md Step 2.
  keywords: visible output, print per step, silently skipped, Seleznov, confirmation line, status prefix, exhaustive, per-item receipt.
- [yaml-pitfalls.md](yaml-pitfalls.md) — frontmatter formatting traps.
  when-to-read: a multi-line description, special characters, or a Prettier project reflowing the frontmatter.
  keywords: YAML, frontmatter, Prettier reflow, multi-line description, special characters, single logical line.
- [hard-code-vs-llm-judgment.md](hard-code-vs-llm-judgment.md) — script it or leave it to the LLM.
  when-to-read: mechanical logic sitting in the body, or auditing a target that ships scripts/.
  keywords: script vs LLM, deterministic, intent drift, gate, regex, char count, semantic judgment.
- [assets-vs-references.md](assets-vs-references.md) — sorting templates vs reference docs.
  when-to-read: templates or samples scattered, or content miscategorized between assets/ and references/.
  keywords: assets, references, templates, boilerplate, sorting, miscategorized.
- [structure-surgery.md](structure-surgery.md) — how to split/restructure and route subdocuments.
  when-to-read: a reference too long, a file mixing topics, routing unclear, or orphan/dangling links.
  keywords: split skill, routing tiers, wiki-index, 2 hops, orphan, dangling, fission, conservation, restructure.
- [effect-dry-run.md](effect-dry-run.md) — walk one prompt per promised task shape through the workflow to see it connect.
  when-to-read: a body containing any ordered multi-step process (Step/Phase/station/pipeline/gates); checking input→instruction→output link and gates fire when run. The §negative half (should-NOT-trigger prompts) applies to EVERY audit, workflow or not.
  keywords: dry-run, walkthrough, broken link, effect coherence, task shape, small revise prompt, gates fired, P0, negative prompt, should-not-trigger, over-trigger, false fire.
- [runtime-contract.md](runtime-contract.md) — load floor, gate granularity, edit license: does the skill still bite when it actually runs.
  when-to-read: FORCED when references/ exceeds ~30 KB, the skill's mission is editing/rewriting or exhaustive (audit / checklist / style-imitation), or the skill declares hard gates; also when the owner says "it triggers but the edits feel shallow"; §4 whenever dispatching MODE=fanout.
  keywords: runtime contract, load floor, minimal read-set, consumption mode, lookup, checklist, immersion, exhaustive mission, skip-safety, full set, read-receipt, gate granularity, gate never fires, edit license, surgical-edit conflict, shallow edits, no-floor, gate-gap, missing-license, index.py, roster, MODE, dispatch, fanout, static table, receipt loop, self-review, blind re-audit, cross-model, glm, second opinion.
- [priority-tiers.md](priority-tiers.md) — P0–P3 definitions and where a finding goes.
  when-to-read: deciding a finding's severity, or whether a P3 is a real Code-layer finding or merely cosmetic (Low).
  keywords: P0, P1, P2, P3, priority tier, severity, placement rule, affects execution.
- [hard-rules.md](hard-rules.md) — the quantified must-pass rules (spine, FORCED every audit).
  when-to-read: always; the hard caps and format laws (char/line limits, third person, name regex, evidence-gating) checked on every audit.
  keywords: hard rules, 1024 chars, 500 lines, third person, name regex, routing depth, evidence-gating.
- [predictability-glossary.md](predictability-glossary.md) — quality vocabulary beyond form: the failure modes.
  when-to-read: always; judging quality past form, or naming a defect (no-op, sediment, completion criterion, leading word).
  keywords: predictability, no-op, sediment, sprawl, duplication, premature completion, completion criterion, leading word.

## Workflow & policy (pulled by the step or section that names them)

- [catalog-skill-pattern.md](catalog-skill-pattern.md) — recommended three-tier structure for bulk-payload skills (many files the model should not read inline).
  when-to-read: the audited skill's payload is many files / binaries / template packs (> ~20 selected per task); pulled by assets-vs-references.md when recommending a catalog structure.
  keywords: catalog skill, bulk payload, by-keyword index, cards, token budget, lookup workflow, binary payload, template pack, directory scan.
- [exception-fallback.md](exception-fallback.md) — what to do when something errors.
  when-to-read: target path missing, YAML unparseable, a bundled script failed, or the file is read-only.
  keywords: exception, error handling, missing path, unparseable YAML, script unavailable, read-only.
- [language-policy.md](language-policy.md) — English-by-default policy and its exceptions.
  when-to-read: body or references in a non-English language; judging whether that non-English is justified.
  keywords: language, default English, non-English, bilingual triggers, translate.
- [output-format.md](output-format.md) — Step 3 detail: the layered report shape (lesstoken, language-matched).
  when-to-read: presenting the Step 3 diagnosis report; laying out verdict → scores → code layer → ✅/🤔 decision split.
  keywords: output format, layered report, lesstoken, code layer, decision layer, safe to fix, needs decision, altitude, colon align, closing question.
- [apply-safety.md](apply-safety.md) — Step 4 detail: size gate, pre-deletion check, close the loop.
  when-to-read: applying a fix; a size gate; deleting a rule/branch; the post-fix handoff line.
  keywords: size gate, pre-deletion check, deletion, dead branch, close the loop, apply with Edit.
- [live-injection-check.md](live-injection-check.md) — Step 2.6 detail: is the description actually injected.
  when-to-read: checking if the target skill shows its description this session, or is dropped name-only.
  keywords: live injection, name-only, budget drop, available-skills list, session scope, population notice.
- [slimming-workflow.md](slimming-workflow.md) — global-pass operation: budget ceiling, compression order, slimming safety protocol.
  when-to-read: a user-initiated GLOBAL slimming pass, or population listing-overflow remediation across installed skills; never during a single-skill audit (overflow is notify-only there).
  keywords: slimming, global pass, character budget, listing budget, skillListingBudgetFraction, compression order, deletion-only, check_desc_slim, target band, 300 chars, name-only drop.
- [rationale.md](rationale.md) — why this skill exists at all.
  when-to-read: background on why the skill exists — the LLM habit of writing a SKILL.md as a manual.
  keywords: rationale, why this skill exists, treats SKILL.md as a manual, long narration, background, philosophy.
