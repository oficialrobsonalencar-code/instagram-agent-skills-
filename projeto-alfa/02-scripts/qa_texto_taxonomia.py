#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA textual pt-BR para carrosseis. Nao substitui uma auditoria semantica humana ou exegese."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "04-skills" / "revisao-textual"
sys.path.insert(0, str(SKILL / "vendor"))

from bs4 import BeautifulSoup
from spellchecker import SpellChecker

TOKEN = re.compile(r"[^\W\d_]+(?:[-’'][^\W\d_]+)*", re.UNICODE)
def fold(s):
    return " ".join(s.casefold().split())

def strip_metadata(t):
    t=re.sub(r"https?://\S+", " ", t)
    t=re.sub(r"(?<!\w)[@#][\wÀ-ÿ]+", " ", t)
    return t

def valid_enclitic(token, checker):
    """Aceita pronomes encliticos comuns: praticá-la -> praticar; fazê-lo -> fazer."""
    match=re.fullmatch(r"([^\W\d_]+?)([áêô])-(?:la|lo|las|los)",token,re.UNICODE)
    if not match:
        return False
    infinitive=match.group(1)+{"á":"ar","ê":"er","ô":"or"}[match.group(2)]
    return bool(checker.known([infinitive]))

def words(t):
    return [x.casefold() for x in TOKEN.findall(strip_metadata(t))]

def text_of_slide(slide):
    clone=BeautifulSoup(str(slide),"html.parser")
    for element in clone.select("svg, style, script, .assinatura"):
        element.decompose()
    return " ".join(clone.get_text(" ", strip=True).split())

def run(html_path,caption_path,taxonomy_path):
    spec=json.loads(taxonomy_path.read_text(encoding="utf-8-sig"))
    html=html_path.read_text(encoding="utf-8-sig")
    caption=caption_path.read_text(encoding="utf-8-sig")
    soup=BeautifulSoup(html,"html.parser")
    slide_nodes=soup.select(".slide")
    slides=[text_of_slide(s) for s in slide_nodes]
    failures=[];warnings=[]
    if not slides:
        failures.append({"tipo":"ESTRUTURA","origem":"html","descricao":"Nao existem elementos .slide"})
    if "\ufffd" in html or "\ufffd" in caption:
        failures.append({"tipo":"CODIFICACAO","origem":"arquivos","descricao":"Caractere de substituicao Unicode; conferir codificacao e fonte"})
    if not caption.strip():
        failures.append({"tipo":"ESTRUTURA","origem":"legenda","descricao":"Legenda vazia"})

    checker=SpellChecker(language="pt",distance=1)
    exceptions=set(fold(t) for t in spec.get("excecoes_dicionario",[]))
    errors={fold(e["palavra"]):e for e in spec.get("termos_inadequados",[])}
    locations={"legenda":caption}
    locations.update({f"slide-{i:02d}":v for i,v in enumerate(slides,1)})
    by_location={}
    for loc,body in locations.items():
        all_words=words(body)
        by_location[loc]=all_words
        missing=checker.unknown(set(all_words)-exceptions)
        missing={token for token in missing if not valid_enclitic(token,checker)}
        for token in sorted(set(all_words)):
            if token in errors:
                item=errors[token]
                failures.append({"tipo":"VOCABULARIO","origem":loc,"palavra":token,"sugestao":item["sugestao"],"descricao":item["motivo"]})
            elif token in missing:
                failures.append({"tipo":"ORTOGRAFIA","origem":loc,"palavra":token,"sugestao":checker.correction(token),"descricao":"Palavra nao reconhecida no dicionario pt-BR ou no lexico do projeto; revisar antes de aprovar"})
        # Repetition and punctuation, but avoid normal headings in uppercase.
        if re.search(r"(?i)\b(\w{3,})\s+\1\b",body):
            warnings.append({"tipo":"REPETICAO","origem":loc,"descricao":"Possivel palavra duplicada"})
        if loc=="legenda" and re.search(r"\s+[,.!?;:]",body):
            warnings.append({"tipo":"PONTUACAO","origem":loc,"descricao":"Espaco imediatamente antes de pontuacao"})

    themes=set()
    for category in spec.get("categorias",[]):
        terms=list(category.get("subcategorias",[]))
        matched=[t for t in terms if any(fold(t) in fold(txt) for txt in locations.values())]
        if matched:
            themes.add(category["id"])

    for idx,content in enumerate(slides,1):
        loc=f"slide-{idx:02d}"; norm=fold(content)
        for ref in spec.get("referencias",[]):
            if fold(ref["citacao"]) not in norm:
                continue
            for forbidden in ref.get("alerta",[]):
                if fold(forbidden) not in norm:
                    continue
                result={"tipo":"SEMANTICA_REFERENCIA","origem":loc,
                        "referencia":ref["citacao"],"expressao":forbidden,
                        "descricao":"Associacao que nao representa diretamente a passagem; revisar o contexto",
                        "orientacao":ref.get("correcao","")}
                # A reference applied to community life may be appropriate, but cannot be claimed
                # as a direct quotation. Flag as warning; hard-fail demonstrably wrong attribution.
                if ref["citacao"]=="Hebreus 10:25":
                    warnings.append(result)
                else:
                    failures.append(result)

    # Compare the account's topic to the slides. Advisory only; this is not proof of factual meaning.
    if "religiosidade" in fold(caption) and not any("religiosidade" in fold(s) for s in slides):
        warnings.append({"tipo":"COERENCIA","origem":"carrossel","descricao":"A legenda destaca religiosidade, mas os slides nao a mencionam diretamente"})

    checksum=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    return {
        "schema_version":1,"idioma":"pt-BR","dicionario":"pyspellchecker-pt 0.8.3 + lexico do projeto",
        "taxonomia":str(taxonomy_path),"html":str(html_path),"legenda":str(caption_path),
        "sha256_html":checksum(html_path),"sha256_legenda":checksum(caption_path),
        "slides":len(slides),"categorias_encontradas":sorted(themes),
        "aprovado_ortografia":not any(e["tipo"] in ("ORTOGRAFIA","VOCABULARIO","CODIFICACAO") for e in failures),
        "aprovado_consistencia_regras":not any(e["tipo"] in ("SEMANTICA_REFERENCIA","ESTRUTURA") for e in failures),
        "aprovado":not failures,
        "falhas":failures,"avisos":warnings,
        "limite":"O detector de ortografia verifica vocabulario. A taxonomia verifica regras contextuais documentadas. Nao valida sozinho teologia, gramática completa ou exegese; revisao editorial permanece necessaria."
    }

def main():
    ap=argparse.ArgumentParser(description="QA ortografico, taxonomico e regras contextuais de carrossel")
    ap.add_argument("--html",required=True)
    ap.add_argument("--legenda",required=True)
    ap.add_argument("--taxonomia",default=str(SKILL/"taxonomia-editorial.json"))
    ap.add_argument("--saida",default=None)
    a=ap.parse_args()
    html_path=Path(a.html).resolve()
    caption_path=Path(a.legenda).resolve()
    try:
        if not html_path.is_file() or not caption_path.is_file():
            raise FileNotFoundError("HTML ou legenda ausentes")
        out=run(html_path,caption_path,Path(a.taxonomia).resolve())
    except Exception as e:
        print(json.dumps({"aprovado":False,"falhas":[{"tipo":"FALHA_TECNICA","descricao":str(e)}]},ensure_ascii=False))
        sys.exit(4)
    data=json.dumps(out,ensure_ascii=False,indent=2)
    if a.saida:
        Path(a.saida).resolve().write_text(data+"\n",encoding="utf-8")
    print(json.dumps({"aprovado":out["aprovado"],"slides":out["slides"],"falhas":out["falhas"][:35],"avisos":out["avisos"][:15],"relatorio":str(Path(a.saida).resolve()) if a.saida else None},ensure_ascii=False))
    sys.exit(0 if out["aprovado"] else 2)

if __name__=="__main__":
    main()
