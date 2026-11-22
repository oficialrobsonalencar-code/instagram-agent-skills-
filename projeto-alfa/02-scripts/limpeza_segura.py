# -*- coding: utf-8 -*-
"""Retencao restrita a ARTEFATOS TEMPORARIOS do projeto Instagram.
Sem --aplicar: somente relatorio. Com --aplicar: quarentena e exclusao apos carencia.
Nao altera imagens finais, backups comuns, credenciais, dados de publicacao ou Git.
"""
import argparse
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent
QUAR = ROOT / "03-agendamentos" / "limpeza" / "quarentena"
JOURNAL = ROOT / "03-agendamentos" / "limpeza" / "registro.jsonl"
SCOPES = [ROOT / "01-conteudo", ROOT / "04-skills" / "carrossel" / "templates"]
SKIP_NAMES = {".git", ".opencode", ".agents", "node_modules", "__pycache__",
              "out", "revisar", "processados", "fila", "perfil-instagram",
              "referencias", "references", "assets", "fonts", "fontes",
              "cenas", "cenas-originais", "saidas-referencia", "backups"}
# Limpeza somente destes nomes EXATOS. Outras pastas NAO entram.
QA_RE = re.compile(r"^(qa-(?:teste|final|atomic|bloqueio|rejeitado|temporario)[\w-]*|teste-auditoria)$", re.I)
STAGING_RE = re.compile(r"^.+\.validando-\d+$", re.I)

def is_inside(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False

def enumerate_candidates(now):
    for scope in SCOPES:
        if not scope.is_dir():
            continue
        for base, dirs, files in os.walk(scope, topdown=True, followlinks=False):
            basepath = Path(base)
            dirs[:] = [d for d in dirs if d not in SKIP_NAMES and not
                       (basepath / d).is_symlink() and not d.startswith(".")]
            for d in list(dirs):
                p = basepath / d
                if not p.is_dir() or p.is_symlink() or not is_inside(p, scope):
                    continue
                if STAGING_RE.fullmatch(d):
                    age = 3
                elif QA_RE.fullmatch(d):
                    age = 14
                else:
                    continue
                # O nome e o pai importam: nao aceitar uma pasta QA aninhada em outra QA.
                # Jamais tocar originais dentro do projeto.
                elapsed = (now - datetime.fromtimestamp(p.stat().st_mtime)).total_seconds() / 86400
                if elapsed >= age:
                    yield p, age, round(elapsed, 1)
                # Nunca percorrer o interior de um artefato candidato, mesmo recente.
                dirs.remove(d)

def log_action(obj):
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def run(apply):
    now = datetime.now()
    moved, purged, skipped = [], [], []
    for p, retention, elapsed in enumerate_candidates(now):
        rec = {"origem": str(p), "idade_dias": elapsed, "retencao_dias": retention}
        if apply:
            QUAR.mkdir(parents=True, exist_ok=True)
            target = QUAR / (now.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
            shutil.move(str(p), str(target))
            meta = target.with_suffix(".manifest.json")
            meta.write_text(json.dumps({"origem": str(p), "quarentena_em": now.isoformat(),
                                        "excluir_apos": (now + timedelta(days=14)).isoformat()},
                                       ensure_ascii=False, indent=2), encoding="utf-8")
            log_action({"acao": "quarentena", **rec, "destino": str(target)})
            rec["destino"] = str(target)
        moved.append(rec)
    # Deletar SOMENTE pastas colocadas pelo proprio script e marcadas em manifesto.
    if QUAR.is_dir():
        for manifest in QUAR.glob("*.manifest.json"):
            try:
                item = json.loads(manifest.read_text(encoding="utf-8"))
                folder = QUAR / manifest.name.removesuffix(".manifest.json")
                due = datetime.fromisoformat(item["excluir_apos"])
                if due <= now and folder.parent.resolve() == QUAR.resolve() and folder.is_dir() and not folder.is_symlink():
                    if apply:
                        shutil.rmtree(folder)
                        manifest.unlink()
                        log_action({"acao": "exclusao_definitiva", "origem": item["origem"],
                                    "em": now.isoformat()})
                    purged.append(str(folder))
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
                skipped.append({"manifesto": str(manifest), "erro": str(e)})
    report = {"modo": "APLICAR" if apply else "SIMULACAO",
              "politica": {"qa_dias": 14, "staging_dias": 3, "quarentena_dias": 14},
              "pastas_elegiveis": moved, "exclusoes_definitivas_elegiveis": purged,
              "manifestos_problematicos": skipped,
              "protecoes": ["out", ".git", ".opencode", "sessao-instagram",
                            "processados", "fila", "referencias", "originais", "backups"]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not skipped else 2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()
    sys.exit(run(args.aplicar))
