#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA do padrao OFICIAL do usuario: terceira imagem do print, fundo claro.
Valida fonte HTML, PNG real e referencia imutavel. Nao publica nem edita arquivos.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageChops
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ID = ROOT / "07-identidade-visual" / "padrao-oficial"
SPECPATH = ID / "mapeamento.json"
SPEC = json.loads(SPECPATH.read_text(encoding="utf-8"))
EXPECTED = SPEC["elementos"]

def css_declarations(text, selector):
    m = re.search(r"(?<![\w-])" + re.escape(selector) + r"\s*\{([^}]+)\}", text, flags=re.S)
    if not m:
        return None
    return {k.strip().lower(): v.strip() for k, v in
            (part.split(":",1) for part in m.group(1).split(";") if ":" in part)}

def norm(value):
    return re.sub(r"\s+", "", str(value)).lower().replace('"', "'")

def html_issues(html_file, expected_occurrences=1):
    text = html_file.read_text(encoding="utf-8-sig")
    # CSS pode estar em arquivo anexo, mas deve existir no proprio projeto de origem.
    styles = [text]
    for candidate in html_file.parent.glob("*.css"):
        if candidate.stat().st_size < 150000:
            styles.append(candidate.read_text(encoding="utf-8-sig"))
    css = "\n".join(styles)
    issues = []
    for selector, required in EXPECTED["css"].items():
        found = css_declarations(css, selector)
        if found is None:
            issues.append(f"{html_file.name}: seletor {selector} ausente")
            continue
        for prop, correct in required.items():
            value = found.get(prop)
            if value is None or norm(value) != norm(correct):
                issues.append(f"{html_file.name}: {selector} {prop}={value!r}, esperado {correct!r}")
    for token in EXPECTED["svg_must_include"]:
        if token not in text:
            issues.append(f"{html_file.name}: SVG difere da referencia: {token}")
    for token in ("@pastor", "robsonalencar"):
        if text.count(token) < expected_occurrences:
            issues.append(f"{html_file.name}: assinatura textual {token} ausente")
    for classname in ("seta","assinatura"):
        occurrences = sum(text.count("class=" + chr(q) + classname + chr(q)) for q in (34,39))
        if occurrences < expected_occurrences:
            issues.append(f"{html_file.name}: elemento .{classname}: {occurrences}, esperado {expected_occurrences}")
    if not re.search(r"1080px\s*;\s*height\s*:\s*1350px",text):
        issues.append(f"{html_file.name}: HTML sem largura 1080 e altura 1350")
    return issues

def feature_bbox(im, region):
    crop = im.crop(tuple(region))
    diff = ImageChops.difference(crop,crop.filter(ImageFilter.GaussianBlur(5))).convert("L")
    array = np.asarray(diff)
    ys,xs = np.where(array > 17)
    if len(xs)<500:
        return None
    return [int(xs.min()+region[0]),int(ys.min()+region[1]),
            int(xs.max()+region[0]),int(ys.max()+region[1])]

def signature_f1(image):
    roi=tuple(EXPECTED["pixel_bbox"]["assinatura"]["roi"])
    source=ROOT/SPEC["arquivo_referencia"]
    def edges(im):
        crop=im.crop(roi)
        return np.asarray(ImageChops.difference(crop,crop.filter(ImageFilter.GaussianBlur(5))).convert("L"))>17
    with Image.open(source) as original:
        reference=edges(original.convert("RGB"))
    current=edges(image)
    common=int(np.logical_and(reference,current).sum())
    total=int(reference.sum())+int(current.sum())
    return 2*common/total if total else 0.0

def image_issues(image_path, legacy_reference=False):
    issues=[]
    try:
        with Image.open(image_path) as img:
            image=img.convert("RGB")
            if image.size != (1080,1350):
                return [f"{image_path.name}: tamanho {image.size}, esperado 1080x1350"]
            rules=dict(EXPECTED["pixel_bbox"])
            if legacy_reference:
                rules["seta"]=SPEC["referencia_legada"]["seta_pixel_bbox_original"]
            for feature, rule in rules.items():
                bbox=feature_bbox(image,rule["roi"])
                if bbox is None:
                    issues.append(f"{image_path.name}: {feature} nao foi detectado")
                    continue
                tol=rule["tolerance_px"]
                target=rule["bbox"]
                if any(abs(a-b)>tol for a,b in zip(bbox,target)):
                    issues.append(f"{image_path.name}: {feature} bbox={bbox}, esperado {target} (tolerancia {tol}px)")
            # Medir os glifos e espacos, nao apenas a caixa externa.
            shape=signature_f1(image)
            brightness=float(np.asarray(image)[50,50,:].mean())
            minimum=EXPECTED["signature_min_f1_dark"] if brightness<125 else EXPECTED["signature_min_f1_light"]
            if shape<minimum:
                issues.append(f"{image_path.name}: ASSINATURA_DIFERENTE_F1={shape:.4f}, minimo={minimum}")
    except Exception as e:
        issues.append(f"{image_path.name}: nao foi possivel abrir PNG: {e}")
    return issues

def check_reference():
    errors=[]
    source=ROOT / SPEC["arquivo_referencia"]
    if not source.is_file():
        return [f"REFERENCIA_OFICIAL_AUSENTE: {source}"]
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=SPEC["sha256_referencia"]:
        errors.append("HASH_DA_REFERENCIA_OFICIAL_FOI_MODIFICADO")
    errors.extend(image_issues(source,legacy_reference=True))
    return errors

def check_folder(folder, expected=None, html_override=None):
    if html_override and (ROOT/"01-conteudo") not in Path(html_override).resolve().parents:
        return ["HTML_FORA_DO_PROJETO"]
    errors=[]
    folder=Path(folder).resolve()
    contents=ROOT / "01-conteudo"
    model=ID / "exemplo-validado"
    if not(folder==model or (folder==contents or contents in folder.parents)):
        return ["PASTA_FORA_DO_PROJETO_01_CONTEUDO"]
    imgs=sorted(folder.glob("slide-*.png"))
    imgdir=folder
    if not imgs:
        imgdir=folder / "out"
        imgs=sorted(imgdir.glob("slide-*.png"))
    if not imgs:
        return ["NAO_HA_SLIDES_PNG_NA_PASTA"]
    if expected is not None and len(imgs)!=expected:
        errors.append(f"QUANTIDADE_DE_SLIDES: {len(imgs)}, esperado {expected}")
    if len(imgs)>10:
        errors.append("MAXIMO_10_SLIDES_POR_CARROSSEL")
    expectednames=[f"slide-{i:02d}.png" for i in range(1,len(imgs)+1)]
    if [f.name for f in imgs]!=expectednames:
        errors.append("ARQUIVOS_SLIDE_FORA_DE_SEQUENCIA")
    htmls=[] if html_override else sorted(folder.glob("slide-*.html"))
    if not htmls and imgdir!=folder and not html_override:
        htmls=sorted(imgdir.glob("slide-*.html"))
    if htmls:
        for f in htmls:
            errors.extend(html_issues(f))
        if len(htmls)!=len(imgs):
            errors.append(f"HTML_PNG_DESIGUAIS: HTML={len(htmls)}, PNG={len(imgs)}")
        for p in imgs:
            h=folder / (p.stem+".html")
            if not h.is_file():h=imgdir / (p.stem+".html")
            if folder!=model and h.is_file() and p.stat().st_mtime + 3 < h.stat().st_mtime:
                errors.append(f"PNG_DESATUALIZADO_APOS_HTML: {p.name}")
    else:
        html=Path(html_override).resolve() if html_override else next((p for p in (folder/"carrossel.html",folder/"index.html") if p.is_file()),None)
        if html is None or not html.is_file():
            errors.append("FONTE_HTML_EDITAVEL_AUSENTE")
        else:
            errors.extend(html_issues(html,len(imgs)))
            if min(p.stat().st_mtime for p in imgs) + 3 < html.stat().st_mtime:
                errors.append("PNG_ANTERIOR_A_ULTIMA_EDICAO_HTML")
    for p in imgs:
        errors.extend(image_issues(p))
    return errors

def main():
    parser=argparse.ArgumentParser(description="Validacao obrigatoria da seta e assinatura OFICIAIS")
    parser.add_argument("--pasta",default=None,help="pasta do novo carrossel em 01-conteudo")
    parser.add_argument("--expected",type=int,default=None)
    parser.add_argument("--html",type=str,default=None,help="HTML que originou os PNGs")
    args=parser.parse_args()
    problems=check_reference()
    if args.pasta:
        problems+=check_folder(args.pasta,args.expected,args.html)
    result={
      "padrao":SPEC["padrao"],
      "referencia_oficial":SPEC["arquivo_referencia"],
      "referencia_historica_mantida_intacta":True,
      "seta":{"top":int(EXPECTED["css"][".seta"]["top"].replace("px","")),"width":86,"height":86,"centerX":540,"stroke_width":3},
      "assinatura":{"top":1089,"font_a":"Playfair Display italic 42px","font_b":"Poppins 800 38px"},
      "pasta_testada":args.pasta,
      "aprovado_geometria":not problems,
      "falhas":problems,
      "pode_publicar":False
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if not problems else 2)

if __name__=="__main__":
    main()
