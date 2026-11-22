#!/usr/bin/env python3
"""Android Appium: inspect real Instagram Highlights and apply approved covers.
No blind taps, no Stories or feed posting. Exits safely when device/UI is unavailable.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
SKILL = Path(__file__).resolve().parent
ASSETS = BASE / "01-conteudo" / "destaques-20261118" / "out"
EVIDENCE = BASE / "debug" / "appium-destaques"
COVERS = {
    "Orações": "destaque-1-oracoes.png",
    "Pregações": "destaque-2-pregacoes.png",
    "Estudos": "destaque-3-estudos.png",
    "Versículos": "destaque-4-versiculos.png",
    "Cultos": "destaque-5-cultos.png",
    "Contato": "destaque-6-contato.png",
    "Testemunhos": "destaque-7-testemunhos.png",
}

def devices():
    res = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True, timeout=15, check=True)
    return [x.split()[0] for x in res.stdout.splitlines()[1:] if len(x.split()) >= 2 and x.split()[1] == "device"]

def snapshot(d, name):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    p = EVIDENCE / (name + ".png")
    d.save_screenshot(str(p))
    return str(p)

def candidates(d, tokens):
    from appium.webdriver.common.appiumby import AppiumBy
    out = []
    for token in tokens:
        literal = token.replace('"', "")
        for xp in (f'//*[@text="{literal}"]', f'//*[contains(@content-desc,"{literal}")]'):
            try:
                matches = d.find_elements(AppiumBy.XPATH, xp)
                out += [x for x in matches if x.is_displayed()]
            except Exception:
                pass
    seen = set()
    unique = []
    for el in out:
        try:
            b = el.rect
            k = (b["x"], b["y"], b["width"], b["height"])
            if k not in seen and b["width"] > 0 and b["height"] > 0:
                seen.add(k)
                unique.append(el)
        except Exception:
            pass
    return unique

def tap_unique(d, texts, phase):
    found = candidates(d, texts)
    if len(found) != 1:
        raise RuntimeError(f"{phase}: expected exactly one visible target; found {len(found)}")
    el = found[0]
    b = el.rect
    d.execute_script("mobile: clickGesture", {"x": int(b["x"] + b["width"]/2),
                                                "y": int(b["y"] + b["height"]/2)})
    time.sleep(1.5)

def run(args):
    missing = [str(ASSETS / v) for v in COVERS.values() if not (ASSETS / v).is_file()]
    if missing:
        raise RuntimeError("Missing approved images: " + ", ".join(missing))
    connected = devices()
    if not connected:
        print(json.dumps({"status":"ANDROID_NAO_CONECTADO","capas":len(COVERS),
                          "script":"READY_FOR_REAL_UI_INSPECTION","published":False},ensure_ascii=False))
        return 2
    if len(connected) != 1:
        raise RuntimeError("More than one Android device: select one explicitly before proceeding")
    serial = connected[0]
    packages = subprocess.run(["adb","-s",serial,"shell","pm","list","packages","com.instagram.android"],
                              capture_output=True,text=True,timeout=20,check=True)
    if "package:com.instagram.android" not in packages.stdout:
        raise RuntimeError("Instagram Android is not installed on the selected phone")
    os.environ["ANDROID_SERIAL"] = serial
    os.environ["IG_USERNAME"] = "pastorrobsonalencar"
    os.environ.setdefault("ANDROID_HOME", str(Path(os.environ["LOCALAPPDATA"]) / "Android" / "Sdk"))
    sys.path.insert(0, str(SKILL))
    import ig_appium as ig
    d = ig.driver()
    try:
        if not ig.goto_profile(d):
            snapshot(d,"01-profile-navigation-failed")
            raise RuntimeError("Could not find own profile; no content changed")
        snapshot(d,"01-profile")
        source = d.page_source
        (EVIDENCE / "01-profile.xml").write_text(source, encoding="utf-8")
        # Inspect first. This upstream repository does not implement Highlight cover editing.
        # Avoid blind clicks, unintended story uploads, or inconsistent account changes.
        print(json.dumps({"status":"PROFILE_INSPECTED","device":serial,
                          "account_expected":"pastorrobsonalencar",
                          "highlight_names_visible":[k for k in COVERS if k.casefold() in source.casefold()],
                          "screenshot":str(EVIDENCE / "01-profile.png"),
                          "next_step":"Validate target UI and implement Edit Highlight > Edit Cover after inspection",
                          "published":False},ensure_ascii=False))
        return 0
    finally:
        d.quit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", action="store_true", help="Safely inspect profile, never edit")
    args = parser.parse_args()
    if not args.inspect:
        print("Use --inspect first. No automated Highlight editing is allowed without validated selectors.")
        return 2
    try:
        return run(args)
    except Exception as ex:
        print(json.dumps({"status":"BLOCKED","reason":str(ex),"published":False},ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
