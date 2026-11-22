"""Validar resposta REAL no historico OpenCode. Falhar fechado se API nao confirmar."""
from pathlib import Path
import re,time
import json,unicodedata,urllib.request,urllib.parse
ROOT=r"I:\Projetos\Instagram-RobsonAlencar"
def normalize(value):
 text=unicodedata.normalize("NFD",str(value)).casefold()
 return "".join(x for x in text if unicodedata.category(x)!="Mn").strip(" .!?")
def choice(text):
 normalized=normalize(text).removesuffix(" (recomendado)")
 exact={
  "publicar agora":"publicar","publicar":"publicar","publique agora":"publicar",
  "pode publicar":"publicar","agendar":"agendar","pode agendar":"agendar"
 }.get(normalized)
 if exact:return exact
 # Somente comandos afirmativos e inequivocos. Nao inferir horarios.
 if re.fullmatch(r"(?:por favor )?(?:publique|poste|publicar|postar)(?: o carrossel| este carrossel| esse post)? agora",normalized):
  return "publicar"
 if re.fullmatch(r"(?:por favor )?(?:agende|agendar)(?: o carrossel| esse post)?",normalized):
  return "agendar"
 return None
def verify(job, *, user_message_id, session_id, action, question_part_id=None):
 url="http://127.0.0.1:4096/session/"+session_id+"/message?limit=160"
 try:
  with urllib.request.urlopen(url,timeout=9) as response:msgs=json.load(response)
 except Exception as exc:
  raise PermissionError("HISTORICO_OPENCODE_INDISPONIVEL: "+type(exc).__name__) from exc
 if not isinstance(msgs,list):raise PermissionError("HISTORICO_INVALIDO")
 user=next((m for m in msgs if m.get("info",{}).get("id")==user_message_id and
            m.get("info",{}).get("role")=="user"),None)
 if user is None:raise PermissionError("MENSAGEM_DO_USUARIO_NAO_ENCONTRADA")
 if question_part_id:
  part=next((p for m in msgs for p in m.get("parts",[]) if p.get("id")==question_part_id
             and p.get("type")=="tool" and p.get("tool")=="question"
             and p.get("state",{}).get("status")=="completed"),None)
  if part is None:raise PermissionError("PERGUNTA_AINDA_NAO_RESPONDIDA")
  state=part.get("state",{})
  questions=state.get("input",{}).get("questions",[])
  if len(questions)!=1:raise PermissionError("PERGUNTA_AMBIGUA")
  title=questions[0].get("question","")
  if job["id"] not in title:
   # Resolve a shortened folder name only against the preceding approved review.
   start=state.get("time",{}).get("start",0)
   reviews=[p["state"] for m in msgs for p in m.get("parts",[])
            if p.get("tool")=="instagram_publicador" and p.get("state",{}).get("status")=="completed"
            and p["state"].get("input",{}).get("etapa")=="revisar"
            and 0 < p["state"].get("time",{}).get("end",0) <= start]
   review=json.loads(max(reviews,key=lambda r:r["time"]["end"])["output"]) if reviews else {}
   folder=review.get("pasta","")
   folder_path=(Path(ROOT)/"01-conteudo"/folder).resolve()
   files=[Path(f).resolve() for f in job["files"]]
   slug=Path(folder).name.removeprefix("carrossel-")
   if not (slug and re.search(r"(?<![\w-])(?:carrossel-)?"+re.escape(slug)+r"(?![\w-])",title,re.I)
           and action=="publicar" and review.get("quando")=="agora"
           and review.get("job_id")==job["id"] and review.get("qa_aprovado") is True
           and review.get("conta")==job["account"] and review.get("legenda_integral")==job["caption"]
           and review.get("midias")==[f.name for f in files]
           and all(f.parent in (folder_path,folder_path/"out") for f in files)
           and 0<=time.time()*1000-state["time"]["end"]<=45*60*1000):
    raise PermissionError("PERGUNTA_DE_OUTRO_PACOTE")
  out=state.get("output")
  if isinstance(out,str):
   try:out=json.loads(out)
   except Exception:out={"answers":[[out]]}
  answers=out.get("answers",out.get("answer",[])) if isinstance(out,dict) else []
  answers=state.get("metadata",{}).get("answers",answers)
  result=[]
  def flatten(value):
   if isinstance(value,str):result.append(value)
   elif isinstance(value,list):
    for x in value:flatten(x)
  flatten(answers)
  if len(result)!=1 or choice(result[0])!=action:
   raise PermissionError("ESCOLHA_DO_USUARIO_DIVERGE_DA_ACAO")
 else:
  content="\n".join(str(p.get("text","")) for p in user.get("parts",[])
                     if p.get("type")=="text" and not p.get("synthetic"))
  if choice(content)!=action:
   raise PermissionError("MENSAGEM_NAO_AUTORIZA_A_ACAO")
 return True
