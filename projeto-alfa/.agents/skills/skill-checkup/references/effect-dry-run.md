# Effect Dry-Run (Effect Coherence Walkthrough)

An ailment that pure structural review cannot catch: the format is all correct, but the flow does not connect when it runs. The dry-run is a low-cost backstop — it does not actually spawn a sub-agent, it just simulates one run in your head.

## When to do it

- Any SKILL.md containing an ordered multi-step process. **Wording is irrelevant**: Step, Phase, station, numbered pipeline, gate chain, "apply in order" all count. Do NOT classify a body as "pure reference type" just because it avoids the word Step — that exact misclassification once let a silent 7-station writing pipeline escape audit.
- When the trigger words clearly mismatch the body workflow
- After a round of fixes, to confirm "the form is right and the effect connects too"
- The **negative half** (§negative below) runs on EVERY audit, workflow or not — over-trigger needs no body to happen.

## Procedure

### 1. Take one typical prompt per task shape (one per shape the description promises)

List the task shapes the description promises (write/create, revise/polish, check/audit …). For each shape, take the first sentence the user would **most likely** say — not an edge case.

The **small-scope revise prompt is mandatory** whenever the skill serves editing tasks: pipelines and gates are usually keyed to the big write shape ("finish a chapter"), and quietly never fire for the everyday small edit — only the small prompt exposes that. Cap at one prompt per promised shape — a description promising four shapes gets four walks, never fewer; an exhaustive prompt matrix is skill-creator's `evals/evals.json`.

Example: skill-checkup itself → "help me review this SKILL.md"
Example: proofreading → "proofread this text" (write shape) + "fix just this paragraph" (small revise shape)
Example: skill-creator → "help me create a new skill"

### 2. Walk through the body once per prompt

Following the SKILL.md's Step / Phase order, ask 4 questions at each step:

1. **Can the input be obtained from the previous step?** — no source to find = broken link
2. **Is the instruction specific enough to execute?** — "process the image" does not count, "convert to PNG with sips" does
3. **Can the output feed the next step?** — the output format of step N must be acceptable to step N+1
4. **Do the hard gates fire at this prompt's granularity?** — count every declared gate (script, checklist, cross-skill handoff) that actually triggers for this prompt; a gate that no common task shape triggers is a P0 `[gate-gap]` (see `runtime-contract.md` §2)

### 3. Mark the problems

If you find any broken link / ambiguity / mismatch, mark P0 (effect problem, must fix).

Walking through successfully is not proof of correctness, only "no problem spotted so far".

## Negative prompts (should-NOT-trigger) — every audit, workflow or not

The positive walk tests under-trigger and flow coherence; this tests **over-trigger**. It needs no workflow, so it runs even when the positive walk is skipped.

1. Craft 1–2 prompts that should NOT invoke the skill, from two sources:
   - the skill's own trigger words appearing in an **adjacent domain** with different intent (skill-checkup example: "review my Python script quality" — script quality, not a skill package);
   - the home prompt of any **sibling flagged by the Step-1 overlap check** — the most probable real-world collision.
2. Judge each against the **description alone** — the router never sees the body. Would a reasonable router plausibly fire? Base the call on the description's actual trigger surface (keywords, first-50-chars), not on charitable reading.
3. Captured → **P2 `[over-trigger]`**: name the trigger word/phrase doing the over-capture and propose the narrowing (qualify the noun, add a negative constraint, or add priority prose naming the sibling).
4. This stays a judgment dry-run — no real `claude -p` runs here. Ground-truth trigger testing is skill-creator's `run_eval.py` against should/should-not cases in `evals/evals.json` (real `claude -p` calls — quote the run count first); point the user there when stakes warrant it.

Print one aggregate line: `[skill-checkup] Dry-run negative: <K> prompts, false-fire=<J>`

## What not to do

- Do not actually spawn a sub-agent to run it — real with/without-skill runs are skill-creator's `run_eval.py` job, skill-checkup only does the dry-run
- Do not exceed one prompt per promised task shape — but never drop a promised shape either; an exhaustive matrix is skill-creator's `evals/evals.json`
- Do not use dry-run results for scoring — skill-checkup does not score, it only marks P0/P1/P2/P3

## Example: running a dry-run on skill-checkup

prompt: "help me review this SKILL.md, path is ~/x/SKILL.md"

- Step 1 reads and prints the body line count → ✅ input is clear, body line count feeds the Step 4 size gate
- Step 2 selects references by the index.py roster → ✅ fire conditions are measured and printed
- Step 2.5 dry-run (this step itself) → ✅ stops at 1 level of recursion, no further nesting
- Step 3 outputs the diagnosis (with P0-P3 priorities) → ✅ template is strict
- Step 4 size gate + Edit → ✅ waits for user confirmation

Connects. If Step 2's roster only said "select as appropriate", it would break the link at that step — that is a P0.
