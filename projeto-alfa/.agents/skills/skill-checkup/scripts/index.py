#!/usr/bin/env python3
"""index.py - dimension roster enumerator for skill-checkup.

Measures the audited skill package, evaluates every dimension's fire
condition MECHANICALLY, prints the roster (FORCED / DEFAULT / SKIP with
reasons) and a final MODE= dispatch line. This script is AUTHORITATIVE
for which dimension files load; references/index.md stays the
human-readable mirror (when-to-read prose + keywords for retrieval).

Rationale: relevance judgment over unread files is the one call the
model is systematically worst at; conditions that only need measurement
must not be left to it. Over-firing is safe (a few KB); under-firing is
the silent-skip failure this script exists to kill.

Usage: python3 index.py "<skill_dir>" ["<skill_dir2>" ...]
Exit:  0 = roster printed; 2 = a target is unreadable.
"""
import re
import subprocess
import sys
from pathlib import Path

THIS_SKILL_DIR = Path(__file__).resolve().parent.parent
REFS = THIS_SKILL_DIR / "references"
INLINE_KB_CAP = 45  # roster heavier than this -> fanout (3 spawns cost more than ~45KB of inline reads)

ORDERED_PATTERNS = [
    r"(?m)^#{2,4}\s*(?:Step|Phase|Stage)\b",
    r"[0-9]️?⃣",                      # emoji keycap digits 0-9
    r"(?i)apply in order",
    r"(?i)\bstation\b",
    r"(?m)^\d+\.\s+\*\*",                        # numbered bold flow items
]
GATE_PATTERN = r"(?i)check_\w+\.py|必跑|硬门|道门|\bgate|checklist|交接"
EDIT_MISSION = r"(?i)edit|rewrit|polish|revis|restructur|\bvoice\b|de-AI|writer|writing|prose|润色|改写|重组|修改|整理"
# exhaustive mission: every item must be walked each run - skipping = silent miss.
# Over-fire is safe (forces one extra reference); under-fire is the silent-skip disease.
EXHAUSTIVE_MISSION = (r"(?i)audit|review|check|verif|inspect|lint|proofread|exhaustive|comprehensive"
                      r"|every (?:rule|item|file)|item.by.item|imitat|style.match"
                      r"|仿写|审查|体检|核对|逐条|清单")


def measure(target: Path) -> dict:
    skill_md = target / "SKILL.md"
    raw = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body = "", raw
    m = re.match(r"(?s)^---\n(.*?)\n---\n?", raw)
    if m:
        fm, body = m.group(1), raw[m.end():]
    # capture the FULL description block: same-line value + indented
    # continuation lines (plain-scalar wrap or block-scalar content) — a
    # first-line-only match misclassifies editing/exhaustive missions whose
    # keywords sit past line 1, and the wrong verdict is un-overridable by
    # design. Value anchored to the description: line so an EMPTY value never
    # swallows the next key's block.
    dm = re.search(r"(?m)^description:[ \t]*(\S[^\n]*(?:\n[ \t]+\S[^\n]*)*)", fm)
    raw_desc = dm.group(1) if dm else ""
    desc = re.sub(r"\s+", " ", raw_desc).strip()
    cm = re.search(r"(?m)^\s*compass-cap:\s*(\d+)", fm)
    cap = int(cm.group(1)) if cm else 6000
    refs = target / "references"
    ref_md = sorted(refs.glob("**/*.md")) if refs.is_dir() else []
    ref_bytes = sum(f.stat().st_size for f in ref_md)
    nonmd_refs = [f for f in refs.glob("**/*") if f.is_file() and f.suffix != ".md"] if refs.is_dir() else []
    routes_rc = subprocess.run(
        [sys.executable, str(THIS_SKILL_DIR / "scripts" / "check_routes.py"), str(target)],
        capture_output=True, text=True).returncode
    ordered = any(re.search(p, body) for p in ORDERED_PATTERNS)
    gates = bool(re.search(GATE_PATTERN, body))
    return {
        "body_chars": len(body), "body_lines": body.count("\n") + 1,
        "cap": cap, "desc_chars": len(desc),
        "desc_multiline": "\n" in raw_desc or desc.startswith((">", "|")),
        "ref_count": len(ref_md), "ref_kb": ref_bytes / 1024,
        "max_ref_kb": max((f.stat().st_size for f in ref_md), default=0) / 1024,
        "nonmd_refs": len(nonmd_refs),
        "scripts": (target / "scripts").is_dir(), "assets": (target / "assets").is_dir(),
        "ordered": ordered or gates, "gates": gates,
        "editing": bool(re.search(EDIT_MISSION, desc)),
        "exhaustive": bool(re.search(EXHAUSTIVE_MISSION, desc)),
        "routes_bad": routes_rc != 0,
    }


def roster(m: dict) -> list:
    """Return [(tier, filename, reason)] for every dimension."""
    rows = []

    def add(tier, name, why):
        rows.append((tier, name, why))

    add("DEFAULT", "description-templates.md",
        "desc is the trigger surface; skip ONLY if: desc unchanged since a prior audit this session")
    add("FORCED" if m["body_chars"] > m["cap"] or m["body_lines"] > 100 else "SKIP",
        "body-quality-checklist.md",
        f"body {m['body_chars']} chars / {m['body_lines']} lines vs caps {m['cap']}/100")
    add("FORCED" if m["ordered"] or m["exhaustive"] else "SKIP", "visible-output-rule.md",
        "ordered multi-step body / gate chain detected" if m["ordered"]
        else ("exhaustive mission - per-item receipts required" if m["exhaustive"]
              else "no ordered process detected"))
    add("FORCED" if m["ordered"] else "DEFAULT", "effect-dry-run.md",
        "walk one prompt per task shape; count gates fired" if m["ordered"]
        else "no ordered process - positive walk skipped, but §negative (should-NOT-trigger) is mandatory on EVERY audit")
    add("FORCED" if m["desc_multiline"] else "SKIP", "yaml-pitfalls.md",
        "multi-line / block-scalar description" if m["desc_multiline"] else "single-line description")
    add("FORCED" if m["scripts"] else "SKIP", "hard-code-vs-llm-judgment.md",
        "target ships scripts/" if m["scripts"] else "no scripts/")
    add("FORCED" if m["assets"] or m["nonmd_refs"] else "SKIP", "assets-vs-references.md",
        "assets/ or non-md files under references/" if m["assets"] or m["nonmd_refs"] else "no assets, refs all .md")
    body_over = m["body_chars"] > m["cap"] or m["body_lines"] > 100
    surgery = m["routes_bad"] or m["ref_count"] > 10 or m["max_ref_kb"] > 12 or body_over
    add("FORCED" if surgery else "SKIP",
        "structure-surgery.md",
        "check_routes issues / >10 refs / a ref >12KB / body over cap (a split needs the routing + conservation rules)"
        if surgery else "routes clean, ref sizes sane, body within cap")
    add("FORCED", "priority-tiers.md", "spine - tiering needed on every audit")
    add("FORCED", "predictability-glossary.md", "spine - failure-mode labels needed on every audit")
    add("FORCED", "hard-rules.md", "spine - quantified must-pass rules consulted on every audit")
    rc_why = [w for w, hit in ((f"refs {m['ref_kb']:.0f}KB>30", m["ref_kb"] > 30),
                               ("editing mission", m["editing"]), ("declared gates", m["gates"]),
                               ("exhaustive mission", m["exhaustive"])) if hit]
    add("FORCED" if rc_why else "SKIP", "runtime-contract.md",
        " + ".join(rc_why) if rc_why else "light refs, no editing/exhaustive mission, no gates")
    return rows


BUNDLES = {
    "form": ["description-templates.md", "body-quality-checklist.md", "yaml-pitfalls.md",
             "assets-vs-references.md", "structure-surgery.md", "hard-rules.md"],
    "predictability": ["predictability-glossary.md", "visible-output-rule.md",
                       "hard-code-vs-llm-judgment.md", "priority-tiers.md"],
    "effect": ["effect-dry-run.md", "runtime-contract.md"],
}


def main() -> int:
    targets = [Path(a).expanduser() for a in sys.argv[1:]]
    if not targets:
        print("usage: index.py <skill_dir> [more ...]", file=sys.stderr)
        return 2
    all_loads = []
    for t in targets:
        if not (t / "SKILL.md").is_file():
            print(f"[index.py] ERROR: {t}/SKILL.md unreadable", file=sys.stderr)
            return 2
        m = measure(t)
        print(f"[index.py] target: {t}")
        print(f"[index.py] measured: body={m['body_chars']}c/{m['body_lines']}l  desc={m['desc_chars']}c  "
              f"refs={m['ref_count']}f/{m['ref_kb']:.0f}KB  scripts={m['scripts']}  assets={m['assets']}  "
              f"ordered-steps={m['ordered']}  editing={m['editing']}  exhaustive={m['exhaustive']}  "
              f"routes_bad={m['routes_bad']}")
        rows = roster(m)
        for tier in ("FORCED", "DEFAULT", "SKIP"):
            for tr, name, why in rows:
                if tr == tier:
                    print(f"[index.py] {tier:<7} {name} — {why}")
        loads = [n for tr, n, _ in rows if tr in ("FORCED", "DEFAULT")]
        all_loads.append(loads)
        kb = sum((REFS / n).stat().st_size for n in loads if (REFS / n).is_file()) / 1024
        print(f"[index.py] roster load: {kb:.0f}KB across {len(loads)} files")
    if len(targets) > 1:
        print(f"[index.py] MODE=fanout ({len(targets)} targets -> one bundle-agent per target, "
              f"<=3 audit agents + 1 reserved self-review slot; procedure: runtime-contract.md §4)")
    elif kb > INLINE_KB_CAP:
        fired = set(all_loads[0])
        parts = [f"{k}[{', '.join(f for f in v if f in fired)}]" for k, v in BUNDLES.items()
                 if any(f in fired for f in v)]
        print(f"[index.py] MODE=fanout (roster {kb:.0f}KB > {INLINE_KB_CAP}KB; {len(parts)} theme bundles: "
              f"{'; '.join(parts)}; + 1 reserved self-review slot)")
    else:
        print(f"[index.py] MODE=inline (roster {kb:.0f}KB <= {INLINE_KB_CAP}KB; "
              f"loop: Read one file -> judge that dimension only -> print receipt -> next; "
              f"close with '[skill-checkup] roster complete: {len(loads)}/{len(loads)} dimensions judged')")
    return 0


if __name__ == "__main__":
    sys.exit(main())
