# -*- coding: utf-8 -*-
"""Interface segura Instagram -> Editor Automatico, sem publicação ou geração implícita."""
import subprocess
import sys
from pathlib import Path

BRIDGE = Path(r"E:\EDITOR AUTOMATICO\VIDEO\integracoes\higgsfield_open_source\higgsfield_bridge.py")
ALLOWED = {"doctor", "plan", "validate"}

def main():
    if not BRIDGE.is_file():
        print("BLOQUEADO: integração do Editor não encontrada", file=sys.stderr)
        return 2
    argv = sys.argv[1:]
    if not argv or argv[0] not in ALLOWED:
        print("Uso: python higgsfield_editor.py doctor | plan --intent editar --description TEXTO | validate --file ARQUIVO",file=sys.stderr)
        return 2
    if argv[0] == "plan" and "--origin" not in argv:
        argv += ["--origin", "instagram"]
    return subprocess.run([sys.executable, str(BRIDGE), *argv], check=False).returncode

if __name__ == "__main__":
    raise SystemExit(main())
