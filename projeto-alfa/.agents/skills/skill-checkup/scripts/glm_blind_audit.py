#!/usr/bin/env python3
"""glm_blind_audit.py - cross-model blind re-audit of a skill package via glm-5.2.

WHY: the self-review blind re-audit (runtime-contract.md §4) removes
seen-the-answer contamination by using a fresh agent, but a fresh agent on the
SAME model keeps the model's own bias - rules written by Claude tend to look
fine to Claude (LLM self-evaluation accuracy is poor; cross-provider blind
review is the community fix). This script bundles the target skill package
into ONE glm-5.2 call and returns an independent audit opinion.

It COMPLEMENTS the fresh Claude agent (which can run scripts and walk the
flow); it does not replace it. GLM sees a static snapshot only.

Bundle: SKILL.md + references/**/*.md + scripts code files, with printed
degradation if over --max-kb (scripts trimmed to heads first, then dropped -
never silently).

Key source: $GLM_API_KEY, else ~/.claude/secrets/glm.key. The key never
appears in output.

Usage: python3 glm_blind_audit.py "<skill_dir>" [--max-kb 200] [--max-tokens 4000]
Exit:  0 = GLM audit returned (opinion printed verbatim; merging is the
           main auditor's job)
       2 = unavailable (no key / network / unreadable target) - announce,
           fall back to same-model-only re-audit, note "cross-model unavailable"
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

GLM_ENDPOINT = "https://api.z.ai/api/anthropic/v1/messages"
GLM_MODEL = "glm-5.2"
KEY_FILE = Path.home() / ".claude" / "secrets" / "glm.key"
CODE_EXT = {".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".rb", ".pl", ".ps1"}
SCRIPT_HEAD_LINES = 40

AUDIT_PROMPT = """You are a fresh, independent auditor of an agent-skill package \
(SKILL.md + references/ + scripts/). You have never seen it before and you were \
given NO expected findings. Audit it adversarially:

- internal contradictions (SKILL.md vs references, reference vs reference)
- dangling pointers: files/sections/scripts/flags named but not present in the bundle
- script/doc mismatches: documented argv, exit codes, or print templates that the \
included script code does not implement
- broken workflow links: a step consuming input no prior step produces
- instructions a model would silently skip (no visible output required, vague \
completion criterion)
- stale or misleading claims

Severity: P0 effect-break / P1 hard-rule or structural violation / P2 specificity \
gap / P3 readability-with-consequence. Do not report pure style.

Reply format (mandatory):
Line 1: "VERDICT: clean" or "VERDICT: <N> finding(s), worst=P<k>"
Then one block per finding: severity, file:line (or file:section), one-sentence \
issue, one-line evidence quote. If clean, state briefly what you checked. Do not \
propose rewrites; report only.

The package bundle follows. File boundaries are marked "=== FILE: <path> ===".
"""


def read_glm_key() -> str:
    key = os.environ.get("GLM_API_KEY")
    if key:
        return key.strip()
    try:
        if KEY_FILE.is_file():
            key = KEY_FILE.read_text(encoding="utf-8").strip()
            if key:
                return key
    except OSError:
        pass
    return ""


def collect(root: Path) -> list:
    """[(relpath, text, kind)] - SKILL.md first, then references, then scripts."""
    out = [("SKILL.md", (root / "SKILL.md").read_text(encoding="utf-8", errors="replace"), "md")]
    refs = root / "references"
    if refs.is_dir():
        for f in sorted(refs.rglob("*.md")):
            out.append((str(f.relative_to(root)), f.read_text(encoding="utf-8", errors="replace"), "md"))
    scripts = root / "scripts"
    if scripts.is_dir():
        for f in sorted(scripts.rglob("*")):
            if f.is_file() and f.suffix in CODE_EXT and "__pycache__" not in f.parts:
                out.append((str(f.relative_to(root)), f.read_text(encoding="utf-8", errors="replace"), "code"))
    return out


def bundle(files: list, max_kb: int) -> str:
    cap = max_kb * 1024

    def total(fs):
        return sum(len(t) for _, t, _ in fs)

    if total(files) > cap:
        trimmed = []
        for rel, text, kind in files:
            if kind == "code":
                lines = text.splitlines()
                if len(lines) > SCRIPT_HEAD_LINES:
                    text = "\n".join(lines[:SCRIPT_HEAD_LINES]) + \
                        f"\n... [trimmed: {len(lines) - SCRIPT_HEAD_LINES} more lines]"
            trimmed.append((rel, text, kind))
        files = trimmed
        print(f"[glm_blind_audit] NOTE: bundle over {max_kb}KB - scripts trimmed to "
              f"first {SCRIPT_HEAD_LINES} lines each (docs kept in full)")
    if total(files) > cap:
        kept, dropped = [], []
        for rel, text, kind in files:
            (dropped if kind == "code" else kept).append((rel, text, kind))
        files = kept + [(rel, "[dropped to fit budget - code not included]", kind)
                        for rel, _, kind in dropped]
        print(f"[glm_blind_audit] NOTE: still over budget - {len(dropped)} script(s) "
              "dropped to name-only (findings cannot cover script internals)")
    return "\n".join(f"=== FILE: {rel} ===\n{text}" for rel, text, _ in files)


def main() -> int:
    args = sys.argv[1:]
    max_kb, max_tokens, pos = 200, 4000, []
    i = 0
    while i < len(args):
        if args[i] == "--max-kb" and i + 1 < len(args):
            max_kb, i = int(args[i + 1]), i + 2
        elif args[i] == "--max-tokens" and i + 1 < len(args):
            max_tokens, i = int(args[i + 1]), i + 2
        else:
            pos.append(args[i]); i += 1
    if not pos:
        print("usage: glm_blind_audit.py <skill_dir> [--max-kb 200] [--max-tokens 4000]",
              file=sys.stderr)
        return 2
    root = Path(pos[0]).expanduser().resolve()
    if not (root / "SKILL.md").is_file():
        print(f"[glm_blind_audit] ERROR: {root}/SKILL.md not found", file=sys.stderr)
        return 2
    key = read_glm_key()
    if not key:
        print("[glm_blind_audit] UNAVAILABLE: no GLM key (env GLM_API_KEY / "
              f"{KEY_FILE}) - cross-model audit did NOT run", file=sys.stderr)
        return 2
    files = collect(root)
    payload = bundle(files, max_kb)
    print(f"[glm_blind_audit] target: {root}")
    print(f"[glm_blind_audit] bundle: {len(files)} files, {len(payload) / 1024:.0f}KB "
          f"-> 1 {GLM_MODEL} call (max_tokens={max_tokens})")
    body = json.dumps({
        "model": GLM_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": AUDIT_PROMPT + "\n" + payload}],
    }).encode("utf-8")
    req = urllib.request.Request(GLM_ENDPOINT, data=body, method="POST")
    req.add_header("x-api-key", key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.loads(r.read().decode("utf-8"))
        text = "".join(b.get("text", "") for b in data.get("content", []))
    except Exception as e:
        print(f"[glm_blind_audit] UNAVAILABLE: call failed ({e.__class__.__name__}: {e}) "
              "- cross-model audit did NOT run", file=sys.stderr)
        return 2
    if not text.strip():
        print("[glm_blind_audit] UNAVAILABLE: empty response - cross-model audit did NOT run",
              file=sys.stderr)
        return 2
    print(f"--- {GLM_MODEL} independent opinion (verbatim; merge/judge is the auditor's job) ---")
    print(text.strip())
    print("--- end of cross-model opinion ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
