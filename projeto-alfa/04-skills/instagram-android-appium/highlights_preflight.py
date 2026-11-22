#!/usr/bin/env python3
"""Read-only readiness check for applying Instagram Highlight cover images via Android UI."""
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "01-conteudo" / "destaques-20261118" / "out"
FILES = {
    "Orações": "destaque-1-oracoes.png",
    "Pregações": "destaque-2-pregacoes.png",
    "Estudos": "destaque-3-estudos.png",
    "Versículos": "destaque-4-versiculos.png",
    "Cultos": "destaque-5-cultos.png",
    "Contato": "destaque-6-contato.png",
    "Testemunhos": "destaque-7-testemunhos.png",
}
def main():
    adb = shutil.which("adb")
    found = []
    if adb:
        r = subprocess.run([adb, "devices", "-l"], capture_output=True, text=True, timeout=15)
        found = [line.strip() for line in r.stdout.splitlines()[1:] if "\tdevice" in line]
    assets = {title: {"file": str(IMAGES / filename), "exists": (IMAGES / filename).is_file()} for title, filename in FILES.items()}
    try:
        import appium
        client = True
    except ImportError:
        client = False
    appium_bin = ROOT / "04-skills" / "instagram-android-appium" / "node_modules" / ".bin" / "appium.cmd"
    result = {
        "account": "pastorrobsonalencar",
        "mode": "CHECK_ONLY_NO_PUBLICATION",
        "android_device_ready": bool(found),
        "android_devices": found,
        "adb_installed": bool(adb),
        "python_client_installed": client,
        "appium_executable_installed": appium_bin.exists(),
        "covers": assets,
        "all_covers_ready": all(x["exists"] for x in assets.values()),
        "can_run_ui_automation": bool(found) and client and appium_bin.exists(),
        "next_step": "Connect an unlocked Android phone with USB debugging and Instagram logged into @pastorrobsonalencar" if not found else "Inspect Android UI of each existing Highlight and adapt selectors before making changes",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["can_run_ui_automation"] and result["all_covers_ready"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
