#!/usr/bin/env python3
"""Cria um destaque novo (se necessario) e aplica a capa.
Uso: --nome "Orações" --arquivo destaque-1-oracoes.png --celula 0
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

os.environ["ANDROID_SERIAL"] = "LNCQMVJJ4TQ8KNGU"
os.environ["IG_USERNAME"] = "pastorrobsonalencar"
sys.path.insert(0, str(SKILL))
import ig_appium as ig
from aplicar_capas_destaques import (bounds_of_text, wait_bounds_text, tap_text_gesture,
                                     shot, find_highlight_icon, scroll_highlights_until, STEP)


def set_name(d, nome):
    """Preenche o campo de nome do novo destaque via clipboard."""
    from appium.webdriver.common.appiumby import AppiumBy
    end = time.time() + 10
    el = None
    while time.time() < end and el is None:
        for e in d.find_elements(AppiumBy.XPATH, '//*[@class="android.widget.EditText"]'):
            el = e
            break
        time.sleep(0.5)
    if el is None:
        raise RuntimeError("campo de nome nao encontrado")
    ig.paste_into(d, el, nome)
    time.sleep(1)


def criar(d, nome):
    b = wait_bounds_text(d, "Criar destaque", 5) or wait_bounds_text(d, "Novo", 5)
    if not b:
        # rolar a linha ate o botao Novo aparecer
        for _ in range(6):
            ig.adb("shell", "input", "swipe", "950", "1950", "300", "1950", "400")
            time.sleep(1)
            b = wait_bounds_text(d, "Novo", 3)
            if b:
                break
    if not b:
        raise RuntimeError("botao Criar destaque nao encontrado")
    ig.gtap(d, b[0], b[1], 3.0)
    shot(d, f"criar-{nome}-galeria")
    # tentar avancar sem selecionar stories
    def avancar():
        b = wait_bounds_text(d, "Avançar", 5) or wait_bounds_text(d, "Concluir", 5)
        if not b:
            return False
        # botao padrao: click no elemento; fallback clickGesture
        if not ig.click_stale_safe(lambda: ig.by_text(d, "Avançar") or ig.by_text(d, "Concluir")):
            ig.gtap(d, b[0], b[1], 2.5)
        else:
            time.sleep(2.5)
        return True
    # selecionar o primeiro story (obrigatorio para criar destaque)
    ps = d.page_source
    cell = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*?content-desc="Story\.', ps, re.S) or \
           re.search(r'content-desc="Story\.[^"]*"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', ps, re.S)
    if not cell:
        raise RuntimeError("nenhum story na galeria de novo destaque")
    x1, y1, x2, y2 = map(int, cell.groups())
    ig.gtap(d, (x1 + x2) // 2, (y1 + y2) // 2, 1.5)
    shot(d, f"criar-{nome}-story-selecionado")
    if not avancar():
        raise RuntimeError("tela de novo destaque nao abriu galeria/avancar")
    shot(d, f"criar-{nome}-nome")
    if wait_bounds_text(d, "Adicionar ao destaque", 3):
        if not avancar():
            raise RuntimeError("nao conseguiu avancar da galeria de stories")
        shot(d, f"criar-{nome}-nome2")
    set_name(d, nome)
    shot(d, f"criar-{nome}-nome-preenchido")
    done = wait_bounds_text(d, "Concluir", 5) or wait_bounds_text(d, "Salvar", 5) or wait_bounds_text(d, "Done", 5)
    if not done:
        raise RuntimeError("botao concluir nao encontrado apos nomear")
    ig.gtap(d, done[0], done[1], 3.0)
    shot(d, f"criar-{nome}-criado")


def aplicar_capa(d, nome, celula):
    from aplicar_capas_destaques import edit_cover
    edit_cover(d, nome, None, celula)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", required=True)
    ap.add_argument("--celula", type=int, required=True)
    args = ap.parse_args()
    nome = args.nome
    cover = ASSETS / f"destaque-{args.celula + 1}-{'x'}.png"
    d = ig.driver()
    try:
        ig.return_to_own_profile()
        time.sleep(4)
        ig.dismiss(d)
        existe = scroll_highlights_until(d, nome, tries=6)
        if not existe:
            print(f"destaque {nome!r} nao existe; criando...", flush=True)
            criar(d, nome)
            ig.goto_profile(d)
            time.sleep(2)
        aplicar_capa(d, nome, args.celula)
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
