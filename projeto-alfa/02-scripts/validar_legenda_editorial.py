#!/usr/bin/env python3
"""Checagem editorial de legenda e recibo vinculado ao conteudo exato."""
import argparse, hashlib, json, pathlib, re, sys
def check(path, registrar=False, revisor=""):
    text=path.read_text(encoding="utf-8-sig").strip()
    issues=[]
    if not text: issues.append("legenda vazia")
    if len(text)>2200: issues.append("acima de 2200 caracteres")
    if text.startswith("#"): issues.append("abre com hashtag")
    tags=re.findall(r"(?<!\w)#[\wÀ-ÿ]+",text)
    if len(tags)>5: issues.append("mais de cinco hashtags")
    if "\ufffd" in text: issues.append("caractere corrompido")
    if re.search(r"(?i)\b(?:como modelo de linguagem|espero que ajude|aqui est[aá] a legenda)\b",text): issues.append("residuo de chatbot")
    if re.search(r"[—–]",text): issues.append("travessao a revisar")
    receipt=path.with_name(path.name+".editorial.json")
    digest=hashlib.sha256(text.encode("utf-8")).hexdigest()
    if registrar:
        if revisor!="humanizer+ig-caption": issues.append("revisor obrigatorio humanizer+ig-caption")
        if not issues:
            receipt.write_text(json.dumps({"sha256":digest,"reviewer":revisor,"skills":["humanizer","ig-caption"],"caption_file":path.name,"version":1},ensure_ascii=False,indent=2),encoding="utf-8")
    else:
        if not receipt.is_file(): issues.append("sem recibo de revisao editorial")
        else:
            try:
                data=json.loads(receipt.read_text(encoding="utf-8"))
                if data.get("sha256")!=digest: issues.append("legenda mudou depois da revisao")
                if set(data.get("skills",[]))!={"humanizer","ig-caption"}: issues.append("skills nao registradas")
                if data.get("caption_file")!=path.name: issues.append("recibo de outro arquivo")
            except (ValueError,UnicodeError): issues.append("recibo invalido")
    return issues,receipt
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--legenda",required=True)
    ap.add_argument("--registrar",action="store_true")
    ap.add_argument("--revisor",default="")
    a=ap.parse_args()
    path=pathlib.Path(a.legenda).resolve()
    problems,receipt=check(path,a.registrar,a.revisor)
    print(json.dumps({"aprovado":not problems,"falhas":problems,"recibo":str(receipt)},ensure_ascii=False))
    sys.exit(2 if problems else 0)
