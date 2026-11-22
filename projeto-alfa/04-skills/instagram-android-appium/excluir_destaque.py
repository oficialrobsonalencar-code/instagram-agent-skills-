#!/usr/bin/env python3
"""Exclui um destaque duplicado pelo menu de long-press. Uso: --nome X --ocorrencia 2"""
import argparse
import json
import os
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
from aplicar_capas_destaques import (bounds_of_text, wait_bounds_text, tap_text_gesture,
                                     shot, find_highlight_icon, scroll_highlights_until)


def all_icons(d, nome):
    import re
    ps = d.page_source
    cols = {}
    for pat in (r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*?content-desc="Story do destaque[^"]*?coluna (\d+)"',
                r'content-desc="Story do destaque[^"]*?coluna (\d+)"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'):
        for m in re.finditer(pat, ps, re.S):
            g = list(map(int, m.groups()))
            if pat.startswith('bounds'):
                cols[g[4]] = g[:4]
            else:
                cols.setdefault(g[0], g[1:5])
    labels = {}
    for m in re.finditer(r'<\w[\w.]* ([^>]*)>', ps, re.S):
        tag = m.group(1)
        b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', tag)
        t = re.search(r'text="([^"]*)"', tag)
        if b and t and t.group(1) and 2060 <= int(b.group(2)) <= 2160:
            labels[(int(b.group(1)), int(b.group(2)))] = t.group(1)
    out = []
    for c, (x1, y1, x2, y2) in sorted(cols.items()):
        icx = (x1 + x2) // 2
        for (tx, ty), t in labels.items():
            if abs(tx - icx) <= 160 and t.casefold() == nome.casefold():
                out.append(((x1 + x2) // 2, (y1 + y2) // 2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", required=True)
    ap.add_argument("--ocorrencia", type=int, default=1)
    args = ap.parse_args()
    d = ig.driver()
    try:
        ig.return_to_own_profile()
        time.sleep(4)
        ig.dismiss(d)
        for _ in range(10):
            icons = all_icons(d, args.nome)
            if len(icons) >= args.ocorrencia:
                break
            ig.adb("shell", "input", "swipe", "950", "1950", "120", "1950", "400")
            time.sleep(1.2)
        icons = all_icons(d, args.nome)
        if len(icons) < args.ocorrencia:
            raise RuntimeError(f"{args.nome}: so encontrei {len(icons)} ocorrencias")
        ic = icons[args.ocorrencia - 1]
        shot(d, f"del-alvo-{args.nome}")
        el = None
        for e in d.find_elements("xpath", f'//*[contains(@content-desc,"Story do destaque")]'):
            r = e.rect
            if abs((r["x"] + r["width"] / 2) - ic[0]) < 60 and abs((r["y"] + r["height"] / 2) - ic[1]) < 60:
                el = e
        d.execute_script("mobile: longClickGesture", {"x": ic[0], "y": ic[1], "duration": 1500})
        time.sleep(2)
        if not wait_bounds_text(d, "Editar destaque", 3) and el is not None:
            d.execute_script("mobile: longClickGesture", {"elementId": el.id, "duration": 1500})
            time.sleep(2)
        shot(d, f"del-menu-{args.nome}")
        tap_text_gesture(d, "Excluir destaque", 2.5)
        shot(d, f"del-confirma-{args.nome}")
        tap_text_gesture(d, "Excluir", 3.0)
        shot(d, f"del-excluido-{args.nome}")
        ig.goto_profile(d)
        time.sleep(2)
        shot(d, "perfil-apos-exclusao")
        print(json.dumps({"status": "OK", "excluido": args.nome, "ocorrencia": args.ocorrencia}, ensure_ascii=False), flush=True)
        return 0
    except Exception as ex:
        try:
            shot(d, "bloqueio")
        except Exception:
            pass
        print(json.dumps({"status": "BLOCKED", "motivo": str(ex)}, ensure_ascii=False), flush=True)
        return 2
    finally:
        d.quit()


if __name__ == "__main__":
    raise SystemExit(main())
