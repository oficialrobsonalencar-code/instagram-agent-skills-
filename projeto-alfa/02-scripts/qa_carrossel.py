# -*- coding: utf-8 -*-
"""Auditoria objetiva de PNGs de carrossel. Sem publicar ou alterar mídia."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from PIL import Image, ImageStat


def compare_hash(im):
    im = im.convert("L").resize((17, 16))
    pixels = list(im.get_flattened_data())
    bits = []
    for y in range(16):
        for x in range(16):
            bits.append(pixels[y * 17 + x] > pixels[y * 17 + x + 1])
    return sum(1 << k for k, bit in enumerate(bits) if bit)


def run(folder, expected=None, strict=False):
    paths = sorted(folder.glob("slide-*.png"))
    errors, warnings, records = [], [], []
    if not paths:
        errors.append("Nenhum PNG slide-XX.png encontrado")
    if expected and len(paths) != expected:
        errors.append(f"Quantidade {len(paths)} difere dos {expected} slides solicitados")
    if not 2 <= len(paths) <= 20:
        warnings.append(f"Quantidade fora do intervalo editorial usual: {len(paths)}")
    hashes = {}
    prior_visuals = []
    for number, path in enumerate(paths, 1):
        correct = f"slide-{number:02d}.png"
        if path.name != correct:
            errors.append(f"Sequencia quebrada: {path.name}; esperado {correct}")
        try:
            with Image.open(path) as opened:
                opened.load()
                if opened.size != (1080, 1350):
                    errors.append(f"{path.name}: {opened.size}, esperado 1080x1350")
                im = opened.convert("RGB")
                full_hash = hashlib.sha256(im.tobytes()).hexdigest()
                if full_hash in hashes:
                    errors.append(f"{path.name}: duplicata exata do {hashes[full_hash]}")
                hashes[full_hash] = path.name
                stage = im.crop((80, 170, 1000, 740))
                stage_stats = ImageStat.Stat(stage.convert("L"))
                stage_stddev = round(stage_stats.stddev[0], 2)
                stage_entropy = round(stage.entropy(), 2)
                stage_hash = compare_hash(stage)
                if strict and stage_stddev < 9 and stage_entropy < 4.2:
                    errors.append(f"{path.name}: regiao de arte quase vazia (desvio={stage_stddev}, entropia={stage_entropy})")
                prior_visuals.append((path.name, stage_hash))
                records.append({"arquivo": path.name, "dimensoes": list(im.size),
                                "regiao_arte_desvio": stage_stddev, "regiao_arte_entropia": stage_entropy})
        except Exception as exc:
            errors.append(f"{path.name}: PNG invalido: {type(exc).__name__}: {str(exc)[:150]}")
    if strict and len(prior_visuals) >= 4:
        similar = []
        for i, (name, fingerprint) in enumerate(prior_visuals):
            for old_name, old_hash in prior_visuals[:i]:
                if (fingerprint ^ old_hash).bit_count() <= 4:
                    similar.append((old_name, name))
                    break
        if len(similar) >= max(2, len(prior_visuals) // 2):
            errors.append(f"Regioes de arte quase identicas em varios slides: {similar[:6]}")
    # A grade 1:1 e verificada como recorte CONSERVADOR de 1080x1080, y=135:1215.
    # O exportador ja confere os bounding boxes de textos; este preview permite revisao visual real.
    if not errors:
        previews = folder / "previews-grade-1x1"
        previews.mkdir(exist_ok=True)
        for slide_path in paths:
            with Image.open(slide_path) as source:
                if source.size == (1080, 1350):
                    source.convert("RGB").crop((0, 135, 1080, 1215)).save(previews / slide_path.name)
    # Auditoria visual somente pode ser preservada com assinatura Ed25519
    # valida sobre o pacote exato. NUNCA inferir revisao de um JSON simples.
    kept = False
    if not errors:
        try:
            from verificar_aprovacao_visual import verify_visual_receipt
            proof = json.loads((folder / "aprovacao-visual.json").read_text(encoding="utf-8-sig"))
            cap_path = folder.parent / "legenda.txt" if folder.name == "out" else folder / "legenda.txt"
            kept = verify_visual_receipt(proof, paths, cap_path.read_text(encoding="utf-8-sig"),
                                         proof.get("job_id"), "pastorrobsonalencar")
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, PermissionError):
            kept = False
    report = {"aprovado_tecnicamente": not errors, "aprovado_visualmente": kept, "tipografia_confirmada": kept, "publicavel": kept, "escopo_da_auditoria": "tecnico; nao atesta tipografia nem fidelidade visual", "modo_cenas_exigidas": strict,
              "resolucao_post": [1080, 1350], "recorte_grade_simulado": [0, 135, 1080, 1215],
              "previews_grade": "previews-grade-1x1" if not errors else None,
              "slides": len(paths), "erros": errors, "avisos": warnings, "arquivos": records}
    try:
        (folder / "qa-relatorio.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 4


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pasta")
    parser.add_argument("--expected", type=int, default=None)
    parser.add_argument("--exigir-cenas", action="store_true")
    args = parser.parse_args()
    sys.exit(run(Path(args.pasta).resolve(), args.expected, args.exigir_cenas))
