#!/usr/bin/env python3
"""check_listing_budget.py — sum installed skill descriptions vs Claude Code's listing budget.

The skills list injected into the system prompt shares one budget (≈1% of the
context window; CC issues #56710 / #47627). On overflow CC silently drops entire
descriptions and keeps names only — a name-only skill cannot auto-trigger.
This script measures the population so skill-checkup can judge one skill in context.

Usage: python3 check_listing_budget.py [project_root] [--target <skill>] [--threshold 0.40]
Exit:  0 = fits budget, OR budget skipped (non-CC harness) — overlap/cap still reported
       1 = OVERFLOW (this is a finding — use the printed numbers, do not treat as error)
       2 = nothing found / script error (only this exit means "budget unavailable")

Also prints pairwise description OVERLAP (routing distinctness): overlap
coefficient |A∩B|/min(|A|,|B|) over latin words + CJK bigrams, scaffolding
stopwords removed. Pairs >= threshold are the collision surface — the router
sees every description at once, so two descriptions sharing their distinctive
keywords are ambiguous even when each is individually well-written. Pairs
involving --target are the audited skill's P2 candidates; all other pairs are
population NOTICEs. Overlap never affects the exit code.

Harness gate: the budget estimate below is a Claude-Code-only mechanism. When
CLAUDECODE is unset (Codex, Gemini, other tools) the budget section is SKIPPED —
Codex enforces its own 2%/8000-char listing budget internally, other tools differ,
and neither exposes a window the way CC does. The per-description cap and the
description-overlap pass still run: routing distinctness is harness-independent.

Budget estimate (chars) =
  SLASH_COMMAND_TOOL_CHAR_BUDGET env var, if set (CC treats it as chars), else
  skillListingBudgetFraction (project settings.json > ~/.claude/settings.json,
  default 0.01) x CONTEXT_TOKENS (read from CC's CLAUDE_CODE_MAX_CONTEXT_TOKENS,
  else the 200k standard window) x CHARS_PER_TOKEN.
Estimate only: CC's exact drop order is undocumented (#31505) — fit with margin.
Counted pools: global skills, project skills (project shadows global on same
name, only one copy counted), plugin skills, and slash commands (~/.claude/commands
+ <project>/.claude/commands) which share the same listing pool.
"""
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
IN_CC = "CLAUDECODE" in os.environ   # harness gate — budget section runs only under CC
# CC's budget scales with the CURRENT model's context window (official docs:
# "the budget scales at 1% of the model's context window"), NOT a fixed ceiling.
# CC exports its active window as CLAUDE_CODE_MAX_CONTEXT_TOKENS when it can, but the
# var can be absent even on a 1M session (registry-stale bug, CC issues #23432/#58710);
# absent → fall back to the 200k standard window. Only read inside the IN_CC branch.
CONTEXT_TOKENS = int(os.environ.get("CLAUDE_CODE_MAX_CONTEXT_TOKENS", 200_000))
CHARS_PER_TOKEN = 4               # rough chars/token for budget conversion
DEFAULT_FRACTION = 0.01
PER_DESC_CAP_PORTABLE = 1024      # agentskills.io spec
PER_DESC_CAP_CC = 1536            # Claude Code >= 2.1.105
BAND = 300                        # everyday per-description target
BAND_CROWDED = 200                # target when 40+ skills installed

OVERLAP_THRESHOLD = 0.40          # overlap coefficient default (--threshold)
OVERLAP_MIN_TOKENS = 5            # skip near-empty descriptions in the overlap pass
# Scaffolding words present in nearly every description (Seleznov template,
# CRUD verbs, function words). Stripping them focuses the overlap measure on
# DOMAIN tokens — the part that actually disambiguates routing.
STOP_LATIN = frozenset("""
the and for with not this that these those from into when what how always
invoke invoked invoking use used using user users usage skill skills expert
asks ask asked mentions mention wants want says say said any all are you your
its also only them then such should must can will may etc via directly first
trigger triggers triggered triggering file files create creates creating edit
edits editing write writes writing writing review reviewing reviews modify
modifying fix fixing check checking generate generating make making read
reading new needs need
""".split())
STOP_CJK = frozenset(
    "触发 调用 用时 时调 用户 点名 明确 确要 使用 支持 相关 一下 帮我 所有 "
    "文件 生成 创建 修改 检查 编辑 项目 任务 需要 可以 进行 自动 工具 或明".split())
LATIN_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.+#_-]{2,}")
CJK_RUN_RE = re.compile(r"[぀-ヿ一-鿿]+")

DESC_RE = re.compile(r"^description:\s*(.*?)(?=^[A-Za-z_-]+:|^---\s*$)", re.S | re.M)


def desc_tokens(desc: str) -> set:
    toks = {t for t in (raw.rstrip(".+#_-") for raw in LATIN_TOKEN_RE.findall(desc.lower()))
            if len(t) >= 3 and t not in STOP_LATIN}
    for run in CJK_RUN_RE.findall(desc):
        toks.update(b for b in (run[i:i + 2] for i in range(len(run) - 1))
                    if b not in STOP_CJK)
    return toks


def report_overlap(every: list, target: str | None, threshold: float) -> None:
    print(f"\n== description overlap (routing distinctness) ==")
    entries = [(n, s, t) for n, s, t in
               ((name, src, desc_tokens(d)) for name, src, d in every)
               if len(t) >= OVERLAP_MIN_TOKENS]
    pairs = []
    for i, (n1, s1, t1) in enumerate(entries):
        for n2, s2, t2 in entries[i + 1:]:
            inter = t1 & t2
            if not inter:
                continue
            coeff = len(inter) / min(len(t1), len(t2))
            if coeff >= threshold:
                pairs.append((coeff, n1, s1, n2, s2, inter))
    if not pairs:
        print(f"clean: no pairs >= {threshold:.2f} "
              "(overlap coefficient; latin words + CJK bigrams, scaffolding stopwords removed)")
    else:
        n_target = 0
        for coeff, n1, s1, n2, s2, inter in sorted(pairs, key=lambda p: (-p[0], p[1], p[3])):
            mark = ""
            if target and target in (n1, n2):
                mark, n_target = "  *TARGET*", n_target + 1
            shared = ", ".join(sorted(inter)[:8])
            print(f"  {coeff:.2f}  {n1} ({s1}) <-> {n2} ({s2}){mark}   shared: {shared}")
        print(f"pairs >= {threshold:.2f}: {len(pairs)}"
              + (f" ({n_target} involving target {target})" if target else ""))
    print("note: overlap = collision surface, not a verdict - intentional siblings are judged for intent;")
    print("      pairs involving the audited target = P2 candidates, all others = population NOTICE (never auto-edit)")


def read_desc(md_file: Path) -> str | None:
    try:
        text = md_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return None
    d = DESC_RE.search(m.group(1) + "\n---")
    if not d:
        return None
    val = d.group(1).strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        val = val[1:-1]
    # CC injects a space-joined single line; collapse whitespace before counting
    return re.sub(r"\s+", " ", val).strip()


def collect_skills(root: Path, patterns: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for pat in patterns:
        try:
            for f in root.glob(pat):
                desc = read_desc(f)
                if desc is not None:
                    out[f.parent.name] = desc
        except OSError:
            continue
    return out


def collect_commands(cmd_dir: Path) -> dict[str, str]:
    """Slash commands (*.md) share the listing pool; description frontmatter optional."""
    out: dict[str, str] = {}
    if not cmd_dir.is_dir():
        return out
    for f in cmd_dir.rglob("*.md"):
        desc = read_desc(f)
        if desc:
            out[f.stem] = desc
    return out


def load_fraction(project_root: Path | None) -> float:
    candidates = []
    if project_root:
        candidates.append(project_root / ".claude" / "settings.json")
    candidates.append(HOME / ".claude" / "settings.json")
    for p in candidates:
        try:
            v = json.loads(p.read_text(encoding="utf-8")).get("skillListingBudgetFraction")
            if isinstance(v, (int, float)) and v > 0:
                return float(v)
        except (OSError, ValueError):
            continue
    return DEFAULT_FRACTION


def main() -> int:
    argv, target, threshold, pos = sys.argv[1:], None, OVERLAP_THRESHOLD, []
    i = 0
    while i < len(argv):
        if argv[i] == "--target" and i + 1 < len(argv):
            target, i = argv[i + 1], i + 2
        elif argv[i] == "--threshold" and i + 1 < len(argv):
            try:
                threshold = float(argv[i + 1])
            except ValueError:
                print(f"WARNING: bad --threshold {argv[i + 1]!r}, using {OVERLAP_THRESHOLD}", file=sys.stderr)
            i += 2
        else:
            pos.append(argv[i])
            i += 1
    # project_root is kept for settings lookup even when it has no .claude/skills
    project_root = Path(pos[0]).resolve() if pos else Path.cwd()

    glob_skills = collect_skills(HOME / ".claude" / "skills", ["*/SKILL.md"])
    proj_skills = collect_skills(project_root / ".claude" / "skills", ["*/SKILL.md"])
    if not (project_root / ".claude" / "skills").is_dir():
        print(f"WARNING: no .claude/skills under {project_root} - project pool counted as 0 "
              "(mistyped path? verdict below may undercount)", file=sys.stderr)
    plugin_cache = HOME / ".claude" / "plugins" / "cache"
    plug_skills = collect_skills(plugin_cache,
                                 ["*/skills/*/SKILL.md", "*/*/skills/*/SKILL.md",
                                  "*/*/*/skills/*/SKILL.md", "*/*/*/*/skills/*/SKILL.md"])
    if plugin_cache.is_dir() and any(plugin_cache.iterdir()) and not plug_skills:
        print("WARNING: plugin cache is non-empty but 0 plugin SKILL.md matched - layout changed, plugin pool uncounted", file=sys.stderr)

    # project shadows global on the same skill name: count one copy only
    shadowed = set(glob_skills) & set(proj_skills)
    for name in shadowed:
        del glob_skills[name]

    cmds = {**collect_commands(HOME / ".claude" / "commands"),
            **collect_commands(project_root / ".claude" / "commands")}

    groups = {"global": glob_skills, "project": proj_skills,
              "plugin": plug_skills, "commands": cmds}
    every = [(name, src, desc) for src, g in groups.items() for name, desc in g.items()]
    if not every:
        print("no SKILL.md / command descriptions found in any source")
        return 2

    total = sum(len(d) for _, _, d in every)
    n_skills = len(every) - len(cmds)
    band = BAND_CROWDED if n_skills >= 40 else BAND
    print(f"== skill listing budget ==")
    print(f"sources: " + "  ".join(f"{k}={len(v)}" for k, v in groups.items())
          + (f"   (shadowed dupes dropped: {len(shadowed)})" if shadowed else ""))

    overflow = False
    if IN_CC:
        env = os.environ.get("SLASH_COMMAND_TOOL_CHAR_BUDGET")
        if env and env.isdigit():
            budget, basis = int(env), "SLASH_COMMAND_TOOL_CHAR_BUDGET env"
        else:
            frac = load_fraction(project_root)
            budget = int(frac * CONTEXT_TOKENS * CHARS_PER_TOKEN)
            basis = f"{frac:.0%} x {CONTEXT_TOKENS // 1000}k ctx x ~{CHARS_PER_TOKEN} chars/token"
        print(f"descriptions total: {total:,} chars   budget ~= {budget:,} chars ({basis})")
        overflow = total > budget
        verdict = "fits" if not overflow else f"OVERFLOW x{total / budget:.1f} - expect silent name-only truncation"
        print(f"verdict: {verdict}")
        print(f"note: drop order is undocumented (#31505) - fit with margin; context window assumed {CONTEXT_TOKENS // 1000}k")
    else:
        print(f"descriptions total: {total:,} chars   budget: SKIPPED (non-CC harness, CLAUDECODE unset)")
        print("verdict: budget check skipped - the 1%-of-context listing budget is a Claude Code")
        print("         mechanism; Codex enforces its own 2%/8000-char budget internally, other")
        print("         tools differ. Per-description cap and overlap are still checked below.")

    over_band = [(len(d), name, src) for name, src, d in every if len(d) > band]
    over_cap = [(len(d), name, src) for name, src, d in every if len(d) > PER_DESC_CAP_PORTABLE]
    print(f"\nover {band}-char band ({len(over_band)} entries, top 15):")
    for length, name, src in sorted(over_band, reverse=True)[:15]:
        print(f"  {length:5d}  {name}  ({src})")
    if over_cap:
        print(f"over per-description cap {PER_DESC_CAP_PORTABLE} (portable) / {PER_DESC_CAP_CC} (CC):")
        for length, name, src in sorted(over_cap, reverse=True):
            print(f"  {length:5d}  {name}  ({src})")
    report_overlap(every, target, threshold)
    return 1 if overflow else 0


if __name__ == "__main__":
    sys.exit(main())
