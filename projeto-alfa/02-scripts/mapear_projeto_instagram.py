# -*- coding: utf-8 -*-
"""Mapeia materiais e skills sem tocar em contas, banco ou publicador."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import json

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"06-referencias"
SKIP={"node_modules",".git",".playwright-mcp","__pycache__","perfil-instagram","processados","fila","historico","cancelados","revisar","evidencias","quarentena","graphify-code-snapshot"}
IMG={".png",".jpg",".jpeg",".webp",".svg"}
VIDEO={".mp4",".mov",".webm"}
def scan(root):
    if not root.is_dir():return []
    return [p for p in root.rglob("*") if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP)]
def rel(p):return p.relative_to(ROOT).as_posix()
def main():
    dirs=[]
    for area in ("00-usuario","00-regras","01-conteudo","04-skills","05-agentes","06-referencias","07-identidade-visual"):
        base=ROOT/area
        if base.is_dir():
            for p in sorted(x for x in base.iterdir() if x.is_dir() and x.name not in SKIP):
                fs=scan(p);c=Counter(f.suffix.lower() for f in fs)
                dirs.append({"caminho":rel(p),"arquivos":len(fs),"imagens":sum(c[x] for x in IMG),"videos":sum(c[x] for x in VIDEO),"html":c[".html"],"mb":round(sum(f.stat().st_size for f in fs)/1048576,2)})
    skills=[]
    for area in ("04-skills",".opencode/skills",".agents/skills","06-referencias/designer-skills"):
        for p in scan(ROOT/area):
            if p.name.upper()=="SKILL.MD":skills.append({"nome":p.parent.name,"caminho":rel(p)})
    refs=[]
    for p in scan(ROOT/"06-referencias"):
        if p.suffix.lower() in IMG and "designer-skills" not in p.parts:refs.append(rel(p))
    for p in scan(ROOT/"01-conteudo"/"carrossel-feed"):
        if p.suffix.lower() in IMG and ("referencia" in p.name.lower() or "original" in p.name.lower()):refs.append(rel(p))
    g=ROOT/"graphify-out"/"graph.json"
    jd=json.loads(g.read_text(encoding="utf-8")) if g.exists() else {}
    rejected=["01-conteudo/carrossel-sensacionalismo-fé","01-conteudo/carrossel-mindgee-10nov"]
    official="07-identidade-visual/padrao-oficial/mapeamento.json"
    flow="00-regras/ORDEM-OPERACIONAL-INSTAGRAM.md"
    data={"gerado":datetime.now().astimezone().isoformat(timespec="seconds"),"raiz":str(ROOT),"codigo":{"arquivo":"graphify-out/graph.json","nos":len(jd.get("nodes",[])),"arestas":len(jd.get("edges",jd.get("links",[])))},"pastas":dirs,"skills":skills,"referencias_visuais":refs,"reprovados":rejected,"marca_aprovada":(ROOT/official).is_file(),"identidade_oficial":official,"fluxo_oficial":flow}
    OUT.mkdir(exist_ok=True)
    (OUT/"MAPA-OPERACIONAL.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    m=["# MAPA OPERACIONAL DO INSTAGRAM","",
       "Atualizado: "+data["gerado"],"",
       "IMPORTANTE: Graphify so mapeia parte do CODIGO. Este indice localiza projetos, imagens e skills, nao comprova qualidade.","",
       "## Regras","",
       "- Rota de publicacao e agendamento: "+flow,"- Identidade oficial para novos slides: "+official,"- Use o grafo para localizar codigo.","- Nao reutilizar materiais reprovados ou de quarentena.","- Visualizar a imagem real, nao apenas ler seu nome ou briefing.","- Nenhuma marca inventada por agente e identidade oficial aprovada.","- Nunca publicar sem ordem explicita.","",
       "## Grafo de codigo","",
       "Arquivo: graphify-out/graph.json; nos: "+str(data["codigo"]["nos"])+"; arestas: "+str(data["codigo"]["arestas"])+".",
       "Comando: graphify query \"qual script exporta carrossel\" --graph graphify-out/graph.json --budget 1200","",
       "## Pastas","",
       "| Caminho | Arquivos | Imagens | Videos | HTML | MB |","|---|---:|---:|---:|---:|---:|"]
    for d in dirs:m.append("| "+d["caminho"]+" | "+str(d["arquivos"])+" | "+str(d["imagens"])+" | "+str(d["videos"])+" | "+str(d["html"])+" | "+str(d["mb"])+" |")
    m+=["","## Skills reais em disco","", "Total: "+str(len(skills))+". Existir em disco nao significa estar carregada na sessao.",""]
    for s in skills:m.append("- "+s["nome"]+" : "+s["caminho"])
    m+=["","## Referencias visuais",""]
    for r in refs[:150]:m.append("- "+r)
    m+=["","## Reprovados e retirados",""]
    for r in rejected:m.append("- "+r+" : NAO REUTILIZAR")
    m+=["","## Limites","- Indice nao le credenciais nem conteudo da fila de publicacao.","- Nao substituir a inspecao visual real por este arquivo.","- Se uma referencia visual nao estiver acessivel, pedir o anexo ou caminho antes de improvisar."]
    (OUT/"MAPA-OPERACIONAL.md").write_text("\n".join(m)+"\n",encoding="utf-8")
    print(json.dumps({"ok":True,"pastas":len(dirs),"skills":len(skills),"referencias":len(refs),"nos":data["codigo"]["nos"]},ensure_ascii=False))
if __name__=="__main__":main()
