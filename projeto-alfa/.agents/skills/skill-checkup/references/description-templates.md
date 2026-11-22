# Description Templates and Trigger Strength

The description is the **only mechanism** for triggering — the body's content is loaded only after triggering. If the description is written badly, no matter how good the body is, it does not matter.

## Empirical comparison of three schools of templates

The community has done empirical testing (Seleznov, 650-trial experiment, 2026):

| School | Template | Measured trigger rate |
|--------|----------|----------------------|
| Anthropic official | "[What it does]. Use when [when]." | ~50% |
| Superpowers | "Use when [when]" (no workflow summary) | not tested separately, roughly the same |
| **Seleznov experimental** | **"[Domain] expert. ALWAYS invoke this skill when [trigger]. Do not [alternative] directly. Use this skill first."** | **~100%** |

> Data source: [Marc Bara — Claude Skills Have Two Reliability Problems](https://medium.com/@marc.bara.iniesta/claude-skills-have-two-reliability-problems-not-one-299401842ca8)

## Recommended: the Seleznov three-part template

```yaml
description: <Domain> expert. ALWAYS invoke this skill when <trigger conditions>.
  Do not <competing default action> directly. Use this skill first.
```

None of the three components can be omitted:

1. **Domain identifier** — lets Claude know what domain of expert this is
   - ✅ "SKILL.md quality expert"
   - ✅ "PostgreSQL performance optimizer"
   - ❌ "Helper for skills" (too weak)

2. **Directive keyword** — use "ALWAYS invoke this skill when...", **not** "Use when..."
   - "Use when" is a suggestive tone, Claude weighs it against its own priorities
   - "ALWAYS invoke" is a command, the trigger rate jumps from 50% to 100%

3. **Negative constraint** — blocks Claude's "detour default behavior"
   - e.g. "Do not modify SKILL.md directly without consulting this skill first."
   - e.g. "Do not write SQL queries directly—use this skill first."
   - This is the **most counterintuitive but most critical** item in the Seleznov experiment. Without it, the trigger rate collapses.

## The first 50 characters are prime real estate

Claude weights the front of the description heavily when scanning. **The most important keywords / trigger scenarios must be within the first 50 characters.**

```yaml
# ❌ keywords buried too deep
description: This skill provides comprehensive guidance and tooling support for
  the workflow of editing SKILL.md files...

# ✅ keywords up front
description: SKILL.md quality expert. ALWAYS invoke when editing any SKILL.md...
```

## Budget & slimming → moved

The character budget, the compression order, and the slimming safety protocol
are a global-pass OPERATION, not an audit dimension — relocated verbatim to
`slimming-workflow.md`. During a single-skill audit, budget overflow stays
notify-only; open that file only for a user-initiated global slimming pass or
when writing a brand-new description.

## Routing distinctness — overlap across installed skills

Trigger failure has a second axis besides this skill's own text: **collision with sibling descriptions**. The router sees every installed description at once, so two descriptions sharing their distinctive keywords are ambiguous even when each is individually well-written (community data: lov-alt/skill-distill reports routing accuracy ~49% under overlapping descriptions, ~74% after differentiation — their own benchmark, treat as indicative).

- Measured mechanically on every audit: `scripts/check_listing_budget.py "<project_root>" --target <name>` prints pairwise overlap coefficient (|A∩B|/min(|A|,|B|), latin words + CJK bigrams, scaffolding stopwords removed; default threshold 0.40, `--threshold` to tune).
- **Pairs involving the audited skill = P2.** Fix by sharpening each side's first-50-chars distinctive keywords, or by an explicit priority clause naming the sibling ("prefer X for domain Y" prose in whichever description should win).
- **Pairs not involving it = population NOTICE** — report, never edit either side on this audit's initiative.
- **Intentional siblings are legitimate** (paired tools, families with declared priority prose). Overlap is a collision *surface*, not a verdict — judge intent before tiering. A flagged sibling also supplies the best should-NOT-trigger prompt for the negative dry-run (`effect-dry-run.md` §negative).

## Third person is a hard rule

The description is injected into the system prompt. First/second person breaks discovery:

```yaml
# ❌ first person
description: I help you write better SKILL.md files...
# ❌ second person
description: You can use this to review SKILL.md...
# ✅ third person
description: SKILL.md quality expert. ALWAYS invoke when...
```

## Keyword coverage

The description should pack in the words the user **actually says**, including synonyms and both languages:

- Mixed languages (if the user switches between them): "SKILL.md quality expert. ALWAYS invoke when editing/modifying/reviewing any SKILL.md, or when the user asks to audit/fix/improve a skill."
- Synonym family: "edit / write / modify / fix / review / audit / improve / check"
- Error messages (if the skill handles a specific error): "ENOENT", "permission denied"
- Specific tool names / file names / commands

## Anti-example collection

```yaml
# ❌ too vague
description: Helps with skills

# ❌ summarizes the workflow (Claude reads the description, takes a shortcut, never enters the body)
description: SKILL.md reviewer that reads the file, scans frontmatter, checks
  body length, validates references, and suggests fixes for each issue found.

# ❌ no negative constraint
description: SKILL.md expert. ALWAYS invoke when editing SKILL.md.
# the trigger rate drops back from 100% to 50% — Claude thinks it can edit too

# ✅ standard form
description: SKILL.md quality expert. ALWAYS invoke this skill when editing
  or writing any SKILL.md file. Do not modify SKILL.md directly without
  consulting this skill first. Use this skill first.
```

## Empty-phrasing check (a standalone hard fault)

Any of the following "filler words" in a description dilutes keyword weight — especially fatal in the first 50 characters:

| Empty word | Why it is bad |
|------------|---------------|
| various / many / multiple / several | conveys no domain information |
| useful / helpful / handy | every skill claims to be useful, no distinction |
| general / generic / all-purpose | negates specialization (the antonym of an expert description) |
| things / tasks / stuff / items | no concrete noun, no trigger scenario to extract |
| comprehensive / robust / powerful | marketing speak, zero contribution to the discovery mechanism |

Anti-example:
```yaml
# ❌ all 5 empty words present
description: A comprehensive skill for various useful tasks including many helpful operations.

# ✅ replaced with a concrete domain + trigger verbs
description: PostgreSQL query optimizer. ALWAYS invoke when writing or reviewing SQL...
```

## Diagnostic checklist (check the target against this when reading this reference)

- [ ] Do the first 50 characters contain the core trigger keywords?
- [ ] Does it use "ALWAYS invoke" (not "Use when")?
- [ ] Is there a negative constraint ("Do not X directly")?
- [ ] Is it third person?
- [ ] Within the per-description cap (1024 portable / 1536 CC)? (the ≤300/≤200 band is guidance for NEW or user-requested rewrites — never a standalone must-fix on an existing skill)
- [ ] Population fits the shared listing budget? (`scripts/check_listing_budget.py` — **notify-only**, report the verdict and move on)
- [ ] Live-injection: does the **current session's** available-skills list show this skill's description (not name-only)?
- [ ] No overlap pair ≥ threshold with a sibling it doesn't intentionally pair with (`check_listing_budget.py --target`)?
- [ ] Does it cover the synonyms / both languages the user actually says (trimmed per the reconciliation rule — `slimming-workflow.md`)?
- [ ] Does it **not** summarize the workflow (it should only say "when to use" + "what expert it is")?
- [ ] Does it have **no** empty phrasing (various / many / useful / general / things / comprehensive, etc.)?
