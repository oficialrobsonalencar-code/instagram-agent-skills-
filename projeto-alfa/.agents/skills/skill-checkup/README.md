English | [简体中文](README.zh-CN.md)

<div align="center">

# skill-checkup

**Puts your skill's content where it belongs — split what should split, load on demand, keep the context lean.**

![Claude Skill](https://img.shields.io/badge/Claude-Skill-8A2BE2)
![Deterministic checks](https://img.shields.io/badge/checks-4%20deterministic-2ea44f)
![References](https://img.shields.io/badge/references-20%20on--demand-blue)
![Runtime deps](https://img.shields.io/badge/runtime%20deps-none-success)
![Python](https://img.shields.io/badge/python-3-3776AB)

A skill that audits other skills. It settles the things a machine can settle — character counts, broken routes, listing budget — with scripts and exit codes, and saves your attention for the calls that need judgment: dead instructions, bloat, exit conditions too vague to act on. Every defect it reports has a name and a line number.

[See it run](#see-it-run) · [Quick start](#quick-start) · [What it catches](#what-it-catches) · [What makes it different](#what-makes-it-different) · [How it works](#how-it-works) · [Reference](#reference)

</div>

---

## See It Run

A real diagnosis, lightly trimmed:

```text
$ "review my image-tool skill"

[skill-checkup] Auditing: ~/.claude/skills/image-tool  body=143 lines  description=52 chars
[skill-checkup] Budget: 32 skills installed, 11,515 chars vs ≈40,000 → fits
[skill-checkup] Dry-run prompt: "use image-tool to convert this"  broken links=1

[skill-checkup] Diagnosis

❌ Must fix (P0→P3)
  [P0 effect break]  Step 3 reads "the output file" but Step 2 never names one
                     → have Step 2 write a named artifact Step 3 can pick up
  [P1 structure]     description is first person ("I help you resize…")
                     → rewrite in third person ("Resizes and converts images…")
  [P2 specificity]   "process the image" has no command
                     → "convert to PNG with `sips -s format png`"

⚠️ Suggested
  - [no-op] "be careful and thorough" — the model already is → delete the line
  - [sprawl] body 143 lines; a 40-line example block → move to references/

✅ Passed
  - name regex, routing (0 orphans / 0 dangling), YAML, visible output per step
```

Here's the thing about a broken skill: nothing throws. It just doesn't fire, or Claude reads half of it and quietly moves on. You find out weeks later when the skill you wrote never once triggered. This is the pass that catches that before you ship.

---

## Quick Start

Point it at any skill — in a Claude session, just ask:

```
review this skill   ·   审查 / 体检 / 修复 this skill   ·   "check my-tool"
```

Or run one deterministic check straight from the shell, no Claude needed:

```bash
python3 scripts/check_routes.py ~/.claude/skills/my-tool
# exit 0 = clean · exit 1 = orphans / dangling links / over the size cap
```

It reads the target, runs the mechanical checks, walks one real prompt through the workflow, and prints a P0→P3 report. It does **not** touch your files until you say "fix it".

---

## What It Catches

The failures that don't announce themselves:

| Symptom you'd never notice | What it flags |
| :--- | :--- |
| Skill never auto-fires | description in first person, too weak, or over the listing budget (silently dropped to name-only) |
| Claude skips half your instructions | body past ~500 lines — `[sprawl]` |
| A reference file never gets read | orphan or dangling route, caught by `check_routes.py` |
| A workflow step gets skipped | the step prints nothing, so the model walks past it |
| The agent quits a step early | exit condition too vague — `[premature-completion]` |
| A line that does nothing | the model already obeyed it by default — `[no-op]` |

Every check, threshold, and rule is listed in full under [Reference](#reference).

---

## What Makes It Different

A real skill is a set of files: SKILL.md plus a references/ library plus scripts/. What this tool manages is where content lives — the main file holds the route, details split into references that say when to read them, and Claude loads a file only when the moment needs it, so the context never gets flooded. Bad placement fails silently: thousands of words dumped into the main file and re-read on every run, a reference that never gets loaded, a link pointing at a file that doesn't exist. Nothing errors. Format linters check one file; nobody covers content placement.

1. **Audits the whole set, not one file.** The SKILL.md router, every reference behind it, and the scripts it ships are one audit target — structure findings (orphans, dangling routes, over-cap bodies) are first-class.
2. **Routing is measured, not assumed.** Every reference carries a when-to-read scenario and keywords, everything must be reachable within 2 hops, and `eval_retrieval.py` tests whether the router can actually find each file from its scenario.
3. **References are classified by how they fail.** Lookup material, checklists, immersion reading — decided by one question: if this file were skipped, would the failure be silent? Each class gets a different enforcement.
4. **Splitting has a protocol.** Restructuring is verbatim relocation — never trim or paraphrase while moving — with a conservation check after and a rollback path. Your content survives the surgery.
5. **Bulk-payload skills get their own shape.** A three-tier catalog pattern for skills that carry hundreds of binaries or templates, production-tested on 187 + 112 payload files.
6. **The audit scales with the target.** A script measures the skill first and rosters only the dimensions that apply; heavy targets fan out across agents. A 5-line skill and a 90 KB reference library get the same rigor at different cost.

Format linters and this tool are complements, not rivals: run one for file hygiene, run this for the architecture.

---

## How It Works

```text
  your skill  (SKILL.md + references/ + scripts/)
        |
        v
  mechanical checks ........ char / line counts · listing budget
  (scripts, exit-coded)      routing reachability · retrieval eval
        |
        v
  judgment .................. bloat · no-op · sediment · vague exits
  (dimensions, on demand)    loaded only when their condition fires
        |
        v
  dry-run ................... walk one real prompt through the workflow
        |
        v
  P0 -> P3 report .......... must-fix / suggested / passed, each with a line number
        |
        v
  apply fixes .............. only after you confirm
```

Two design choices make the verdict worth trusting:

- **Deterministic where it can be.** Counts, routing, and budget are settled by scripts that return exit codes, not by an opinion that drifts between runs.
- **Honest where it can't.** If skill-checkup already edited your skill earlier in the same session, it stamps every line of its report `[self-review]` and tells you to re-check with a fresh agent. It discounts its own grade on purpose.

<!-- ============ Reference — skip unless you're looking something up ============ -->

---

## Reference

Everything below is lookup material. You don't need to read it to use the skill.

### Diagnosis flow

| Step | Does | Output |
| :--- | :--- | :--- |
| 1 | Read the target SKILL.md; run `check_listing_budget.py`, `check_routes.py` and `check_script_safety.py` | size + budget + routes + safety verdicts |
| 2 | `index.py` rosters every dimension (FORCED / DEFAULT / SKIP, plus a `MODE=` dispatch line); read the fired ones one file at a time | the roster + one receipt per dimension |
| 2.5 | Dry-run: walk one prompt per task shape (write / revise / check / restructure) through the body | broken links + gates fired per prompt (any break → P0) |
| 2.6 | Live-injection: is the target's description actually injected this session, or dropped name-only | injected / dropped / skipped |
| 3 | Print the P0→P3 diagnosis (❌ must fix · ⚠️ suggested · ✅ passed) | the report |
| 4 | Apply fixes with Edit — only after you confirm | applied-fixes line |

### Bundled scripts

No LLM and no third-party dependencies (except `eval_retrieval.py --glm` and `glm_blind_audit.py`, which call a model on request).

| Script | Checks | Command | Exit |
| :--- | :--- | :--- | :--- |
| `index.py` | measures the target and prints the dimension roster (FORCED / DEFAULT / SKIP with reasons) plus the `MODE=` dispatch line | `python3 scripts/index.py <skill_dir>` | 0 roster printed / 2 unreadable |
| `check_routes.py` | reachability, orphans, dangling links, the compass cap (6000 chars, overridable via a `compass-cap:` frontmatter field); `--before <snapshot>` adds a content-conservation check | `python3 scripts/check_routes.py <skill_dir>` | 0 clean / 1 issues / 2 unavailable |
| `check_script_safety.py` | scans bundled scripts and prose for risk patterns (exfiltration, destructive ops, persistence); detection is mechanical, conviction stays with the auditor | `python3 scripts/check_script_safety.py <skill_dir>` | 0 ran (hits are findings) / 2 unavailable |
| `check_listing_budget.py` | total description chars vs the ~1%-of-context listing pool; lists every description over the 300-char band | `python3 scripts/check_listing_budget.py <root>` | 0 fits / 1 overflow / 2 unavailable |
| `check_desc_slim.py` | flags descriptions that can be trimmed without losing trigger strength | `python3 scripts/check_desc_slim.py <skill_dir>` | 0 clean / 1 issues |
| `eval_retrieval.py` | asks a model (GLM, 3× majority vote) whether the router can find each reference by its `when-to-read` scenario | `python3 scripts/eval_retrieval.py <skill_dir> --glm` | 0 clean / 1 misses |
| `glm_blind_audit.py` | bundles the whole package into one cross-model (GLM) call for an independent blind second opinion | `python3 scripts/glm_blind_audit.py <skill_dir>` | 0 opinion printed / 2 no key or network |

### Hard rules

A violation here is an error, not a suggestion.

| Rule | Source |
| :--- | :--- |
| description ≤ 1024 chars (Claude Code ≥ 2.1.105 accepts 1536) | Anthropic spec / CC release notes |
| listing-budget overflow is always reported — it is a population fact, fixed by a global pass, never by editing one skill | CC issues #56710 / #47627 |
| description in third person | Anthropic best practices |
| name uses only lowercase letters, digits, hyphens | Anthropic spec |
| body < 500 lines | Anthropic / community consensus |
| routing depth ≤ 2 hops (SKILL.md → index.md → file); nested indexes forbidden | structure-surgery (hardened from practice) |
| zero dangling routes, zero orphan subdocuments | structure-surgery iron rule |
| description on a single logical YAML line (no `>` or `|`) | Prettier reflow breaks it |
| every workflow step produces visible output | Seleznov experiment |
| a skill's claim about its own performance must point to in-repo evidence, or be cut | evidence-gating |

### Failure modes it names

A defect gets a name so you can act on it precisely; the P-tier says how bad, the name says what kind.

- `[no-op]` — a line the model already obeys by default
- `[sediment]` — a stale line that drifted out of relevance
- `[sprawl]` — simply too long, even if every line is live
- `[duplication]` — the same meaning in more than one place
- `[premature-completion]` — an exit condition so vague the agent quits early
- `[weak-leading-word]` — an anchor word too weak to beat the model's default
- `[no-floor]` — no mandatory read-set, so audit depth varies run to run
- `[gate-gap]` — quality gates keyed only to big tasks; the everyday small edit passes zero gates
- `[missing-license]` — an editing skill that never grants rewrite authority, so the model's minimal-diff default wins

### Priority tiers

| Tier | Meaning | Enters ❌ |
| :--- | :--- | :--- |
| **P0** | effect break (the flow doesn't connect when run) | always |
| **P1** | violates a structural hard rule | always |
| **P2** | insufficient specificity (no command, no I/O spec) | always |
| **P3** | readability | only when it changes what the next run does; else ⚠️ |

### Dimensions (rostered on demand by `scripts/index.py`)

`scripts/index.py` decides which dimension files fire (FORCED / DEFAULT / SKIP); workflow docs load at the step that names them. `references/index.md` stays the human-readable mirror.

| Reference | Covers |
| :--- | :--- |
| `description-templates.md` | trigger-strength template + routing distinctness |
| `slimming-workflow.md` | global-pass slimming: budget ceiling, compression order, safety protocol |
| `catalog-skill-pattern.md` | three-tier structure for bulk-payload skills |
| `body-quality-checklist.md` | body size and what to demote into references |
| `visible-output-rule.md` | every workflow step must print something |
| `yaml-pitfalls.md` | frontmatter formatting traps |
| `hard-code-vs-llm-judgment.md` | script it, or leave it to the model |
| `assets-vs-references.md` | sorting templates vs reference docs |
| `structure-surgery.md` | splitting, routing tiers, the 2-hop cap |
| `effect-dry-run.md` | walking one prompt per task shape through the workflow |
| `runtime-contract.md` | load floor, gate granularity, edit license: whether the skill still takes effect when it actually runs |
| `priority-tiers.md` | P0–P3 definitions and placement |
| `predictability-glossary.md` | the failure-mode vocabulary |
| `hard-rules.md` | the quantified must-pass rules |
| `exception-fallback.md` | what to do when a path or script errors |
| `language-policy.md` | English-by-default and its exceptions |
| `output-format.md` | the layered shape of the Step 3 report |
| `apply-safety.md` | size gate, pre-deletion check, closing the loop |
| `live-injection-check.md` | is the description actually injected this session |
| `rationale.md` | why the skill exists at all |

### Repository structure

```text
skill-checkup/
├── SKILL.md                              # the compass: diagnosis flow + routing
├── references/
│   ├── index.md                          # routes to every dimension by when-to-read
│   ├── apply-safety.md
│   ├── assets-vs-references.md
│   ├── body-quality-checklist.md
│   ├── catalog-skill-pattern.md
│   ├── description-templates.md
│   ├── effect-dry-run.md
│   ├── exception-fallback.md
│   ├── hard-code-vs-llm-judgment.md
│   ├── hard-rules.md
│   ├── language-policy.md
│   ├── live-injection-check.md
│   ├── output-format.md
│   ├── predictability-glossary.md
│   ├── priority-tiers.md
│   ├── rationale.md
│   ├── runtime-contract.md
│   ├── slimming-workflow.md
│   ├── structure-surgery.md
│   ├── visible-output-rule.md
│   └── yaml-pitfalls.md
├── scripts/
│   ├── index.py                          # dimension roster: FORCED / DEFAULT / SKIP + MODE=
│   ├── check_routes.py                   # reachability / orphans / dangling / compass cap
│   ├── check_listing_budget.py           # description listing-budget
│   ├── check_desc_slim.py                # description slimming
│   ├── check_script_safety.py            # risk-pattern scan of bundled scripts
│   ├── eval_retrieval.py                 # retrieval eval (model-backed)
│   └── glm_blind_audit.py                # cross-model blind second opinion
├── README.md
├── README.zh-CN.md
└── LICENSE
```

---

<div align="center">

*Skills fail silently. This is the pass that makes them fail loudly first.*

**Author:** [Zane456](https://github.com/Zane456) · **License:** [MIT](LICENSE)

</div>
