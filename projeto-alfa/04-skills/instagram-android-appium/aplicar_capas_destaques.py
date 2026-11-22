#!/usr/bin/env python3
"""Aplica capas aos destaques do perfil @pastorrobsonalencar.
Sem taps cegos: cada etapa verifica texto/bounds no page_source e salva screenshot.
Uso: --alvo testemunhos | --criar "Orações" ...
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
SKILL = Path(__file__).resolve().parent
ASSETS = BASE / "01-conteudo" / "destaques-20261118" / "out"
EVIDENCE = BASE / "debug" / "appium-destaques"
ALBUM = "CapasDestaques"

COVERS = {
    "Orações": "destaque-1-oracoes.png",
    "Pregações": "destaque-2-pregacoes.png",
    "Estudos": "destaque-3-estudos.png",
    "Versículos": "destaque-4-versiculos.png",
    "Cultos": "destaque-5-cultos.png",
    "Contato": "destaque-6-contato.png",
    "Testemunhos": "destaque-7-testemunhos.png",
}

os.environ["ANDROID_SERIAL"] = "LNCQMVJJ4TQ8KNGU"
os.environ["IG_USERNAME"] = "pastorrobsonalencar"
sys.path.insert(0, str(SKILL))
import ig_appium as ig

STEP = [0]


def shot(d, tag):
    STEP[0] += 1
    p = EVIDENCE / f"{STEP[0]:02d}-{tag}.png"
    ig.screenshot(d, str(p))
    (EVIDENCE / f"{STEP[0]:02d}-{tag}.xml").write_text(d.page_source, encoding="utf-8")
    print(f"  [evidencia] {p.name}", flush=True)
    return str(p)


def bounds_of_text(d, txt):
    ps = d.page_source
    e = re.escape(txt)
    for attr in ("text", "content-desc"):
        for pat in (rf'{attr}="{e}"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
                    rf'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*{attr}="{e}"'):
            m = re.search(pat, ps, re.S)
            if m:
                x1, y1, x2, y2 = map(int, m.groups())
                return (x1 + x2) // 2, (y1 + y2) // 2
    return None
    for pat in ():
        m = re.search(pat, ps, re.S)
        if m:
            x1, y1, x2, y2 = map(int, m.groups())
            return (x1 + x2) // 2, (y1 + y2) // 2
    return None


def wait_bounds_text(d, txt, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        b = bounds_of_text(d, txt)
        if b:
            return b
        time.sleep(0.6)
    return None


def tap_text_gesture(d, txt, settle=2.0):
    b = wait_bounds_text(d, txt, 10)
    if not b:
        raise RuntimeError(f"texto nao encontrado: {txt!r}")
    ig.gtap(d, b[0], b[1], settle)
    return True


def find_highlight_icon(d, nome):
    """Retorna centro do icone do destaque com esse nome na linha de destaques."""
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
    for c, (x1, y1, x2, y2) in cols.items():
        icx = (x1 + x2) // 2
        for (tx, ty), t in labels.items():
            if abs(tx - icx) <= 160 and t.casefold() == nome.casefold():
                return (icx, (y1 + y2) // 2)
    return None


def scroll_highlights_until(d, nome, tries=10):
    for i in range(tries):
        ic = find_highlight_icon(d, nome)
        if ic:
            return ic
        if i % 2 == 0:
            ig.adb("shell", "input", "swipe", "950", "1950", "120", "1950", "400")
        else:
            ig.adb("shell", "input", "swipe", "120", "1950", "950", "1950", "400")
        time.sleep(1.2)
    return find_highlight_icon(d, nome)


def edit_cover(d, nome, cover_file, cell_index):
    """Fluxo: long-press no destaque -> Editar destaque -> Editar capa -> galeria -> imagem -> Concluir."""
    ic = scroll_highlights_until(d, nome)
    if not ic:
        raise RuntimeError(f"destaque {nome!r} nao encontrado na linha")
    shot(d, f"alvo-{nome}")
    # long-press nativo do Appium abre o menu do destaque
    d.execute_script("mobile: longClickGesture", {"x": ic[0], "y": ic[1], "duration": 1500})
    time.sleep(2)
    shot(d, f"menu-{nome}")
    if not wait_bounds_text(d, "Editar destaque", 3):
        # fallback: long-press direto no elemento
        el = ig.by_desc_contains(d, f"coluna ")
        els = [e for e in d.find_elements("xpath", '//*[contains(@content-desc,"Story do destaque")]')]
        target = None
        for e in els:
            r = e.rect
            if abs((r["x"] + r["width"] / 2) - ic[0]) < 60 and abs((r["y"] + r["height"] / 2) - ic[1]) < 60:
                target = e
        if target is not None:
            from appium.webdriver.webelement import WebElement
            d.execute_script("mobile: longClickGesture", {"elementId": target.id, "duration": 1500})
            time.sleep(2)
            shot(d, f"menu2-{nome}")
    tap_text_gesture(d, "Editar destaque", 2.5)
    shot(d, f"editar-{nome}")
    tap_text_gesture(d, "Editar capa", 2.5)
    shot(d, f"capa-{nome}")
    if not wait_bounds_text(d, "Abrir galeria", 8):
        raise RuntimeError("tela de capa nao abriu a opcao Abrir galeria")
    tap_text_gesture(d, "Abrir galeria", 3.0)
    shot(d, f"galeria-{nome}")
    # trocar para o album CapasDestaques se houver seletor
    ps = d.page_source
    if ALBUM in ps:
        b = bounds_of_text(d, ALBUM)
        if b:
            ig.gtap(d, b[0], b[1], 2.0)
            shot(d, f"album-{nome}")
    time.sleep(2)
    # selecionar a celula cell_index (0-based) da galeria: celulas clicaveis com thumbnail
    ps = d.page_source
    cells = []
    for m in re.finditer(r'<\w[\w.]* ([^>]*)>', ps, re.S):
        tag = m.group(1)
        if 'clickable="true"' not in tag:
            continue
        dsc = re.search(r'content-desc="([^"]*)"', tag)
        b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', tag)
        if dsc and b and ('thumbnail' in dsc.group(1).lower() or 'foto' in dsc.group(1).lower() or 'imagem' in dsc.group(1).lower()):
            x1, y1, x2, y2 = map(int, b.groups())
            if y1 > 400:
                cells.append(((x1 + x2) // 2, (y1 + y2) // 2))
    cells = sorted(set(cells), key=lambda c: (c[1], c[0]))
    print(f"  celulas galeria: {len(cells)}", flush=True)
    if len(cells) <= cell_index:
        raise RuntimeError(f"galeria tem {len(cells)} celulas; indice {cell_index} indisponivel")
    ig.gtap(d, cells[cell_index][0], cells[cell_index][1], 2.5)
    shot(d, f"selecionada-{nome}")
    if not wait_bounds_text(d, "Concluir", 8):
        raise RuntimeError("botao Concluir nao apareceu apos selecionar imagem")
    tap_text_gesture(d, "Concluir", 3.0)
    shot(d, f"concluido-{nome}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo", required=True, help="nome do destaque existente")
    args = ap.parse_args()
    nome = args.alvo
    cover = ASSETS / COVERS[nome]
    if not cover.is_file():
        raise RuntimeError(f"capa ausente: {cover}")
    cell_index = sorted(COVERS).index(nome)
    ig.push_images_to_album([str(ASSETS / v) for v in COVERS.values()], album=ALBUM)
    print("imagens enviadas ao album", ALBUM, flush=True)
    d = ig.driver()
    try:
        ig.return_to_own_profile()
        time.sleep(4)
        ig.dismiss(d)
        edit_cover(d, nome, cover.name, cell_index)
        ig.return_to_own_profile()
        time.sleep(3)
        shot(d, "perfil-final")
        print(json.dumps({"status": "OK", "destaque": nome}, ensure_ascii=False), flush=True)
        return 0
    except Exception as ex:
        try:
            shot(d, "bloqueio")
        except Exception:
            pass
        print(json.dumps({"status": "BLOCKED", "alvo": nome, "motivo": str(ex)}, ensure_ascii=False), flush=True)
        return 2
    finally:
        d.quit()


if __name__ == "__main__":
    raise SystemExit(main())
