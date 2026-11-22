# -*- coding: utf-8 -*-
"""Portao deterministico de tipografia para carrosseis.
Consulta somente fontes registradas no Windows; NAO copia nem distribui arquivos de fonte.
Uma fonte instalada nao significa que a referencia visual foi reproduzida.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(r"I:\Projetos\Instagram-RobsonAlencar")
CATALOG = ROOT / "debug" / "catalogo-fontes-windows.json"
GENERIC = {"arial", "helvetica", "helvetica neue", "times", "times new roman", "sans-serif", "serif", "system-ui"}

def normalize(s):
    return re.sub(r"\s+", " ", str(s).strip(" \"'")).casefold()

def loaded_fonts():
    entries = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    return {normalize(x["nome"]) for x in entries if x.get("existe")}

def registered(name, entries):
    n = normalize(name)
    if n in {"serif", "sans-serif", "monospace", "system-ui", "cursive", "fantasy"}:
        return True
    return any(e == n or e.startswith(n + " ") or n.startswith(e + " ") for e in entries)

def check(src, manifest=None):
    errors, warnings, found = [], [], []
    css_list = re.findall(r"<style[^>]*>([\s\S]*?)</style>", src, re.IGNORECASE)
    styles = "\n".join(css_list)
    imports = re.findall(r"@import\s+[^;]+;", styles, re.IGNORECASE)
    for css in css_list:
        without_comments = re.sub(r"/\*[\s\S]*?\*/", "", css)
        m = re.search(r"@import\s+[^;]+;", without_comments, re.IGNORECASE)
        if m and re.search(r"\{[^}]*\}", without_comments[:m.start()]):
            errors.append("@import depois de regra CSS: navegador ignora o import de fontes")
    if imports:
        errors.append("Fonte remota via @import: use as fontes instaladas no Windows, sem dependencia externa")
    entries = loaded_fonts()
    families = re.findall(r"font-family\s*:\s*([^;}{]+)", styles, re.IGNORECASE)
    for raw in families:
        first = raw.strip().split(",")[0].strip().strip("\"'")
        if not first:
            continue
        found.append(first)
        if first.lower().startswith("var("):
            warnings.append(f"Familia definida por variavel CSS ({first}); verificar no navegador")
        elif not registered(first, entries):
            errors.append(f"Fonte principal nao registrada neste Windows: {first}")
        elif normalize(first) in GENERIC:
            errors.append(f"Fonte generica principal nao aprovada: {first}")
    if not families:
        errors.append("Nenhuma familia de fonte declarada no CSS")
    if manifest is None:
        errors.append("Manifesto tipografico deste trabalho ausente: falta vincular fontes a referencia atual")
    else:
        info = json.loads(manifest.read_text(encoding="utf-8-sig"))
        approved = info.get("aprovado_pelo_usuario") is True
        ref = info.get("referencia_do_pedido")
        allowed = [normalize(x) for x in info.get("familias_permitidas", [])]
        if not approved or not ref or not allowed:
            errors.append("Manifesto incompleto ou nao aprovado: sem confirmacao explicita da referencia e das familias")
        else:
            for first in found:
                if not first.lower().startswith("var(") and normalize(first) not in allowed:
                    errors.append(f"Familia nao aprovada no manifesto: {first}")
    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))
    return {"aprovado_para_entrega": not errors, "referencia_tipografica_confirmada": bool(manifest),
            "familias_detectadas": list(dict.fromkeys(found)), "erros": errors, "avisos": warnings}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("--manifesto", type=Path)
    ap.add_argument("--relatorio", type=Path)
    args = ap.parse_args()
    if not args.html.is_file():
        ap.error("HTML nao encontrado")
    result = check(args.html.read_text(encoding="utf-8-sig"), args.manifesto)
    result["arquivo"] = str(args.html)
    if args.relatorio:
        args.relatorio.parent.mkdir(parents=True, exist_ok=True)
        args.relatorio.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["aprovado_para_entrega"] else 4)

if __name__ == "__main__":
    main()
