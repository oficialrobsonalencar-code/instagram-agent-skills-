#!/usr/bin/env python3
"""check_script_safety.py - mechanical risk-pattern scan of a skill package.

Layer 1 of a two-layer safety check: DETECTION is mechanical (this script),
CONVICTION is semantic (the auditing LLM judges each hit in context, per
references/hard-code-vs-llm-judgment.md). A hit is a finding PENDING that
judgment - a documented `rm -rf` example in prose is legitimate (note-only);
the same pattern in a bundled script, or prose instructing the model to run
it, is real. Never auto-delete a flagged line.

Threat model: the skill AUTHOR slipped, not an adversary shipping malware.
Patterns are chosen for what a well-meaning author writes by accident -
a script that wipes the worktree, a SKILL.md line telling the model to skip
confirmation, a hardcoded token left in an example.

Scans:
  code  - scripts/**/* and other code files (full pattern set; `\\`-continued
          lines are folded before matching, reported at the opening line)
  prose - SKILL.md + references/**/*.md and other .md files (prompt-risk
          subset: dangerous-command instructions, injected directives,
          hidden-unicode). Prose hits inside a ``` fence are marked `fenced`
          - a fenced hit is usually documentation, an unfenced one is usually
          an instruction. The marker is context for the auditor, not a verdict.

Severity ranks findings only; every hit still needs the auditor's judgment.
  CRIT - irreversible, or a live secret is already exposed
  HIGH - destructive / exfiltrating / steers the model past a safety gate
  MED  - risky construct that has legitimate uses
  LOW  - smell

Self-exclusion: a file named check_script_safety.py is skipped (its own
pattern table would flag itself forever). The LLM layer still reads it.

Usage: python3 check_script_safety.py "<skill_dir>"
Exit:  0 = clean, 1 = hits printed (findings, not an error), 2 = unreadable
"""
import re
import sys
from pathlib import Path

CODE_EXT = {".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".rb", ".pl", ".ps1"}
EXCLUDE = {"check_script_safety.py"}
EXCERPT = 90
FENCE = re.compile(r"^\s{0,3}(```|~~~)")
SEV_RANK = {"CRIT": 0, "HIGH": 1, "MED": 2, "LOW": 3}

# (class, id, regex, scope, severity)  scope: code | prose | both
PATTERNS = [
    # --- remote code execution -------------------------------------------
    ("exec-remote", "pipe-to-shell",
     re.compile(r"(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b"), "both", "HIGH"),
    ("exec-remote", "proc-subst-remote",
     re.compile(r"\b(sh|bash|zsh|source|\.)\s+<\(\s*(curl|wget)\b"), "both", "CRIT"),
    ("exec-remote", "eval-remote",
     re.compile(r"eval\s+[\"']?(\$\(|`)\s*(curl|wget)\b"), "both", "CRIT"),
    ("exec-remote", "powershell-iex",
     re.compile(r"(?i)\biwr\b[^\n]*\|\s*iex|Invoke-Expression"), "both", "HIGH"),
    ("exec-remote", "pip-install-vcs",
     re.compile(r"\bpip3?\s+install\b[^\n]*\bgit\+https?://"), "both", "MED"),

    # --- destructive to the user's machine / repo ------------------------
    ("destructive", "rm-abs-or-home",
     re.compile(r"\brm\s+(-[A-Za-z]+\s+)*-[A-Za-z]*[rR][A-Za-z]*\s+[\"']?"
                r"(~|/(?!tmp/|tmp\b|private/tmp)|\$HOME|\$\{HOME)"), "both", "CRIT"),
    ("destructive", "rm-variable-path",
     re.compile(r"\brm\s+-[A-Za-z]*r[A-Za-z]*f[A-Za-z]*\s+[\"']?\$(?!TMPDIR|TMP\b|\{?SCRATCH)"), "both", "HIGH"),
    ("destructive", "disk-overwrite",
     re.compile(r"\bdd\b[^\n]*\bof=/dev/|\bmkfs(\.\w+)?\b|\bshred\b"), "both", "CRIT"),
    ("destructive", "git-force-push",
     re.compile(r"git\s+push\b[^\n]*(\s--force\b|\s-f\b)"), "both", "HIGH"),
    ("destructive", "git-reset-hard",
     re.compile(r"git\s+reset\s+--hard"), "both", "HIGH"),
    ("destructive", "git-clean-force",
     re.compile(r"git\s+clean\b[^\n]*\s-[A-Za-z]*f"), "both", "HIGH"),
    ("destructive", "git-discard-worktree",
     re.compile(r"git\s+(checkout|restore)\s+(--\s+)?(\.|\*)(\s|$)"), "both", "HIGH"),
    ("destructive", "git-history-rewrite",
     re.compile(r"git\s+filter-(branch|repo)\b|git\s+reflog\s+expire\b[^\n]*--expire=now"
                r"|git\s+gc\b[^\n]*--prune=now"), "both", "HIGH"),
    ("destructive", "find-delete",
     re.compile(r"\bfind\b[^\n]*(\s-delete\b|-exec\s+rm\b)"), "both", "HIGH"),
    ("destructive", "sql-drop",
     re.compile(r"(?i)\b(drop\s+(table|database|schema)|truncate\s+table)\b"), "both", "HIGH"),
    ("destructive", "chmod-777",
     re.compile(r"chmod\s+(-R\s+)?0?777\b"), "both", "MED"),

    # --- privilege / agent guardrails ------------------------------------
    ("privilege", "sudo",
     re.compile(r"(^|[;&|`(]\s*)sudo\s+"), "code", "MED"),
    ("privilege", "agent-permission-bypass",
     re.compile(r"--dangerously-skip-permissions|--yolo\b|bypassPermissions|autoApprove"), "both", "HIGH"),

    # --- credentials ------------------------------------------------------
    ("credential", "ssh-material",
     re.compile(r"~/\.ssh/|\bid_rsa\b|\bid_ed25519\b"), "both", "HIGH"),
    ("credential", "private-key-block",
     re.compile(r"-----BEGIN ([A-Z]+ )*PRIVATE KEY-----"), "both", "CRIT"),
    ("credential", "cloud-creds",
     re.compile(r"~/\.aws/|\.netrc\b|\.config/gh/hosts|~/\.config/gcloud"
                r"|~/\.kube/config|~/\.docker/config\.json|\.npmrc\b|\.pypirc\b"), "both", "HIGH"),
    ("credential", "keychain",
     re.compile(r"security\s+find-(generic|internet)-password"), "both", "HIGH"),
    ("credential", "shell-history",
     re.compile(r"~/\.(bash|zsh)_history"), "both", "HIGH"),
    ("credential", "plist-env-read",
     re.compile(r"PlistBuddy[^\n]*:EnvironmentVariables:|defaults\s+read\b[^\n]*\b(key|token|secret)"), "both", "MED"),
    ("credential", "token-literal",
     re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|gh[posu]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}"
                r"|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}"
                r"|hf_[A-Za-z0-9]{30,}|glpat-[A-Za-z0-9_-]{20,})\b"), "both", "CRIT"),
    ("credential", "env-file-read",
     re.compile(r"\b(cat|source)\s+[^\n]*\.env\b"), "code", "MED"),

    # --- exfiltration -----------------------------------------------------
    ("exfil", "post-file-out",
     re.compile(r"curl\b[^\n]*(\s-d\s*@|--data-binary\s*@|\s-F\s)[^\n]*https?://"), "both", "HIGH"),
    ("exfil", "upload-file",
     re.compile(r"curl\b[^\n]*(\s-T\s|--upload-file)|wget\b[^\n]*--post-(file|data)"), "both", "HIGH"),
    ("exfil", "webhook-sink",
     re.compile(r"(?i)hooks\.slack\.com|discord(app)?\.com/api/webhooks|webhook\.site"
                r"|requestbin|pipedream\.net|\bngrok\.(io|app)\b|oast\.(fun|site|pro)"
                r"|burpcollaborator|interact\.sh"), "both", "HIGH"),
    ("exfil", "reverse-shell",
     re.compile(r"\bn(c|cat)\b[^\n]*(\s-e\s|--exec)|(ba)?sh\s+-i\s*>&\s*/dev/tcp/"), "both", "CRIT"),

    # --- obfuscation / dynamic execution ---------------------------------
    ("obfuscation", "base64-exec",
     re.compile(r"base64\s+(-d|-D|--decode)\b[^\n]*\|\s*(ba|z)?sh\b"), "both", "CRIT"),
    ("obfuscation", "py-eval-exec",
     re.compile(r"(?<![\w.])(eval|exec)\s*\("), "code", "HIGH"),
    ("obfuscation", "reflective-exec",
     re.compile(r"getattr\s*\(\s*(os|sys|builtins|__builtins__)\b"), "code", "HIGH"),
    ("obfuscation", "dynamic-import",
     re.compile(r"(?<![\w.])__import__\s*\("), "code", "MED"),
    ("obfuscation", "compile-call",
     re.compile(r"(?<![\w.])compile\s*\("), "code", "MED"),
    ("obfuscation", "deserialize-exec",
     re.compile(r"\b(pickle|marshal|dill)\.loads?\s*\("), "code", "MED"),
    ("obfuscation", "codec-decode",
     re.compile(r"codecs\.decode\s*\([^)]*[\"'](rot13|hex|base64)"), "code", "MED"),
    ("obfuscation", "encoded-literal",
     re.compile(r"(?:\\x[0-9a-fA-F]{2}){8,}"), "code", "MED"),
    ("obfuscation", "subprocess-shell-true",
     re.compile(r"shell\s*=\s*True"), "code", "MED"),

    # --- persistence beyond the session -----------------------------------
    ("persistence", "shell-rc-append",
     re.compile(r">>\s*[\"']?(~|\$HOME|\$\{HOME\})[^\n]*/\.(zsh|bash)(rc|_profile|_login|env)"), "both", "HIGH"),
    ("persistence", "cron-install",
     re.compile(r"\bcrontab\s+(-e\b|-\s*$|[^\n]*\.cron)"), "both", "HIGH"),
    ("persistence", "launchctl-install",
     re.compile(r"launchctl\s+(load|unload|bootstrap|bootout|enable)\b"), "both", "HIGH"),
    ("persistence", "launch-agent-path",
     re.compile(r"Library/Launch(Agents|Daemons)"), "both", "MED"),
    ("persistence", "systemd-enable",
     re.compile(r"systemctl\s+(--user\s+)?enable\b"), "both", "MED"),

    # --- prompt risk: prose that steers the model --------------------------
    ("prompt-injection", "instruction-override",
     re.compile(r"(?i)\b(ignore|disregard)\s+(all\s+)?(the\s+)?(previous|prior|above|earlier|preceding)"
                r"\s+(instruction|prompt|rule|direction)"), "prose", "HIGH"),
    ("prompt-injection", "refusal-suppression",
     re.compile(r"(?i)\bnever\s+refuse\b|\balways\s+comply\b|\bdo\s+anything\s+now\b"
                r"|\byou\s+have\s+no\s+(restriction|limit|limitation|guideline)"
                r"|\bignore\s+your\s+(guideline|safety|rule)"), "prose", "HIGH"),
    ("prompt-injection", "confirmation-bypass",
     re.compile(r"(?i)\b(never|do\s+not|don'?t|no\s+need\s+to)\s+"
                r"(ask|prompt|confirm|wait\s+for\s+(the\s+)?(user|confirmation|approval))\b"
                r"|\bskip\s+(the\s+)?(confirmation|approval|permission)\b"), "prose", "HIGH"),
    ("prompt-injection", "system-prompt-leak",
     re.compile(r"(?i)\b(reveal|print|output|repeat|disclose|show)\s+(me\s+)?(your|the)\s+"
                r"(full\s+|entire\s+|complete\s+)?(system\s+)?(prompt|instructions)\b"), "prose", "MED"),
    ("prompt-injection", "hidden-directive",
     re.compile(r"(?i)<!--[^>]*?\b(ignore|disregard|override|always|never|must|execute"
                r"|run\s+this|send|delete|exfil)\b[^>]*?-->"), "prose", "MED"),

    # --- hidden / deceptive characters ------------------------------------
    ("hidden-unicode", "zero-width",
     re.compile("[\\u200b\\u200c\\u200d\\u200e\\u200f\\u2060\\ufeff]"), "both", "HIGH"),
    ("hidden-unicode", "bidi-override",
     re.compile("[\\u202a-\\u202e\\u2066-\\u2069]"), "both", "HIGH"),
    ("hidden-unicode", "mixed-script",
     re.compile("[A-Za-z][\\u0400-\\u04ff]|[\\u0400-\\u04ff][A-Za-z]"), "both", "HIGH"),
]


def iter_files(root: Path):
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.name in EXCLUDE:
            continue
        rel = f.relative_to(root)
        if any(p.startswith(".") or p == "__pycache__" for p in rel.parts):
            continue
        if f.suffix == ".md":
            yield f, "prose"
        elif f.suffix in CODE_EXT or (f.parent.name == "scripts" and f.suffix == ""):
            yield f, "code"


def code_lines(text: str):
    """Yield (lineno, text) with backslash-continued lines folded onto the opener."""
    buf, start = "", None
    for lineno, line in enumerate(text.splitlines(), 1):
        if start is None:
            start = lineno
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            buf += stripped[:-1] + " "
            continue
        yield start, buf + line
        buf, start = "", None
    if start is not None:
        yield start, buf


def prose_lines(text: str):
    """Yield (lineno, text, fenced) - fenced marks lines inside a ``` block."""
    inside = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            yield lineno, line, True
            continue
        yield lineno, line, inside


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_script_safety.py <skill_dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    if not (root / "SKILL.md").is_file():
        print(f"[check_script_safety] ERROR: {root}/SKILL.md not found", file=sys.stderr)
        return 2

    hits, by_class, by_sev = [], {}, {}
    for f, kind in iter_files(root):
        try:
            text = f.read_text(encoding="utf-8", errors="replace").lstrip("﻿")
        except OSError:
            continue
        rel = str(f.relative_to(root))
        rows = ((n, t, False) for n, t in code_lines(text)) if kind == "code" else prose_lines(text)
        for lineno, line, fenced in rows:
            for cls, pid, rx, scope, sev in PATTERNS:
                if scope != "both" and scope != kind:
                    continue
                if rx.search(line):
                    hits.append((sev, rel, lineno, cls, pid, fenced, line.strip()[:EXCERPT]))
                    by_class[cls] = by_class.get(cls, 0) + 1
                    by_sev[sev] = by_sev.get(sev, 0) + 1

    print(f"[check_script_safety] {root}")
    if not hits:
        print("[check_script_safety] PASS - no risk patterns")
        return 0

    hits.sort(key=lambda h: (SEV_RANK[h[0]], h[1], h[2]))
    for sev, rel, lineno, cls, pid, fenced, excerpt in hits:
        mark = " (fenced)" if fenced else ""
        print(f"  [{sev:<4}] {rel}:{lineno}  [{cls}] {pid}{mark}   {excerpt}")

    sev_line = " ".join(f"{s}={by_sev[s]}" for s in ("CRIT", "HIGH", "MED", "LOW") if s in by_sev)
    cls_line = "  ".join(f"{k}={v}" for k, v in sorted(by_class.items()))
    print(f"[check_script_safety] {len(hits)} hit(s) - {sev_line}")
    print(f"[check_script_safety] classes: {cls_line}")
    print("[check_script_safety] detection is mechanical; conviction is the auditor's job "
          "(hard-code-vs-llm-judgment.md) - never auto-delete a flagged line")
    print("[check_script_safety] `fenced` = inside a ``` block, usually documentation; "
          "an unfenced prose hit is usually an instruction to the model")
    return 1


if __name__ == "__main__":
    sys.exit(main())
