#!/usr/bin/env python3
"""Conta SKILL.md por area (numero unico para os documentos). Somente leitura."""
import sys
from pathlib import Path
raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
areas = {"designer-skills": "06-referencias/designer-skills", ".opencode": ".opencode/skills",
         ".agents": ".agents/skills", "04-skills": "04-skills"}
total = 0
for nome, rel in areas.items():
    d = raiz / rel
    n = sum(1 for p in d.rglob("SKILL.md") if "node_modules" not in p.parts) if d.exists() else 0
    total += n
    print(f"{nome:16s} {n}")
print(f"{'TOTAL':16s} {total}")
