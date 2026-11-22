# Exception fallback (errors are not silently skipped)

| Scenario | Handling |
|----------|----------|
| Target SKILL.md path does not exist | Abort the flow, print `[skill-checkup] ERROR: <path> not found`, ask the user to confirm the path |
| YAML frontmatter not parseable | Skip the description trigger-strength dimension, mark P1 must-fix: "YAML not parseable, fix the frontmatter before continuing" |
| Referenced references file missing | List as a P1 issue (resource integration), do not block diagnosis of other dimensions |
| a bundled script (`scripts/index.py` / `scripts/check_listing_budget.py` / `scripts/check_routes.py` / `scripts/check_script_safety.py` / `scripts/eval_retrieval.py` / `scripts/check_desc_slim.py` / `scripts/glm_blind_audit.py`) missing or exits 2 | Print `[skill-checkup] <script>: unavailable (<reason>)`, continue diagnosis without that verdict — never invent numbers (a missing safety scan = "Safety: unavailable", never "clean"). Two special cases: during a slimming pass, `check_desc_slim.py` unavailable = STOP the pass (the gate is the safety); `glm_blind_audit.py` unavailable = the same-model blind re-audit stands, receipt appends `(cross-model unavailable)` — not a reason to mark unverified |
| No write permission / file read-only | In Step 4, print the patch content instead, tell the user "apply manually, file not writable" |

Principle: announce the exception to the user first, then handle it per the rules; never silently skip.
