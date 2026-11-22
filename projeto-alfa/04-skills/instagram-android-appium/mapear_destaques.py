#!/usr/bin/env python3
"""Mapeia todos os destaques do perfil ao vivo: scroll horizontal + dump UI."""
import json
import os
import re
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
SKILL = Path(__file__).resolve().parent
EVIDENCE = BASE / "debug" / "appium-destaques"

os.environ["ANDROID_SERIAL"] = "LNCQMVJJ4TQ8KNGU"
os.environ["IG_USERNAME"] = "pastorrobsonalencar"
sys.path.insert(0, str(SKILL))
import ig_appium as ig


def parse(ps):
    cols = {}
    pat = re.compile(r'<\w+(?:\.\w+)* [^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*?content-desc="Story do destaque[^"]*?coluna (\d+)"', re.S)
    for m in pat.finditer(ps):
        cols[int(m.group(5))] = [int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))]
    pat2 = re.compile(r'<\w+(?:\.\w+)* [^>]*?content-desc="Story do destaque[^"]*?coluna (\d+)"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', re.S)
    for m in pat2.finditer(ps):
        cols.setdefault(int(m.group(1)), [int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))])
    names = {}
    for m in re.finditer(r'<\w+(?:\.\w+)* [^>]*?text="([^"]+)"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', ps, re.S):
        t, x1, y1 = m.group(1), int(m.group(2)), int(m.group(3))
        if 2060 <= y1 <= 2160:
            names[(x1, y1)] = t
    for m in re.finditer(r'<\w+(?:\.\w+)* [^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*?text="([^"]+)"', ps, re.S):
        x1, y1, t = int(m.group(1)), int(m.group(2)), m.group(5)
        if 2060 <= y1 <= 2160:
            names.setdefault((x1, y1), t)
    out = []
    for c, (x1, y1, x2, y2) in sorted(cols.items()):
        nm = [t for (tx, ty), t in names.items() if x1 - 30 <= tx <= x2 + 30]
        out.append({"coluna": c, "nome": nm[0] if nm else None, "icon_bounds": [x1, y1, x2, y2]})
    return out


def main():
    d = ig.driver()
    try:
        ig.return_to_own_profile()
        time.sleep(4)
        ig.dismiss(d)
        ig.screenshot(d, str(EVIDENCE / "map-00-inicio.png"))
        merged = {}
        for i in range(8):
            ps = d.page_source
            (EVIDENCE / f"map-live-{i}.xml").write_text(ps, encoding="utf-8")
            for h in parse(ps):
                merged[h["coluna"]] = h
            ig.screenshot(d, str(EVIDENCE / f"map-live-{i}.png"))
            print(f"scroll {i}: {[(h['coluna'], h['nome']) for h in parse(ps)]}", flush=True)
            ig.adb("shell", "input", "swipe", "950", "1950", "120", "1950", "400")
            time.sleep(1.2)
        result = [merged[k] for k in sorted(merged)]
        (EVIDENCE / "map-live.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "OK", "destaques": result}, ensure_ascii=False, indent=2), flush=True)
        return 0
    finally:
        d.quit()


if __name__ == "__main__":
    raise SystemExit(main())
