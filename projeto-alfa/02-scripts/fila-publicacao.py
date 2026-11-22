#!/usr/bin/env python3
"""Fila de publicacao Instagram: preflight, reserva atomica, registro auditavel."""
from pathlib import Path
import argparse,datetime,json,os,sys,uuid,subprocess,re,msvcrt,time
ROOT=Path(r"I:\Projetos\Instagram-RobsonAlencar")
BASE=ROOT/"03-agendamentos"/"publicador"
QUEUE=BASE/"fila"
DONE=BASE/"processados"
FAILED=BASE/"revisar"
LOG=BASE/"publicador.log"
SCRIPTS=ROOT/"02-scripts"
RUNLOCK=BASE/".publicador-exclusive.lock"
def now():return datetime.datetime.now(datetime.timezone.utc)
def note(s):
 BASE.mkdir(parents=True,exist_ok=True)
 with LOG.open("a",encoding="utf-8") as f:f.write(now().isoformat()+" "+s+"\n")
 print(s,flush=True)
def validate(q):
 if q.get("status")!="aprovado":return "status não aprovado"
 if not q.get("id") or not q.get("approved_by"):return "aprovação não identificada"
 if not re.fullmatch(r"[A-Za-z0-9._]{2,30}",str(q.get("account","")).strip().lstrip("@")):return "account not configured or invalid"
 try:due=datetime.datetime.fromisoformat(q["scheduled_at"])
 except Exception:return "data de agendamento inválida"
 if due.tzinfo is None:return "agendamento sem fuso horário"
 if due.astimezone(datetime.timezone.utc)>now():return "futuro"
 images=q.get("files",[])
 if not (1<=len(images)<=10):return "quantidade inválida de mídias"
 for f in images:
  path=Path(f)
  if not path.is_file() or path.suffix.lower() not in (".png",".jpg",".jpeg",".mp4"):return "mídia ausente ou extensão não suportada: "+str(path)
 if not str(q.get("caption","")).strip():return "legenda ausente"
 from validar_pacote_publicacao import validate_package
 problems=validate_package(q)
 if problems:return "PACOTE_SEM_QA: "+", ".join(problems)
 return None
def browser_profile_busy():
 # Evita colidir com navegador dedicado aberto para autenticacao.
 try:
  cmd=["powershell","-NoProfile","-Command",
       "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.CommandLine -like '*publicador*perfil-instagram*' } | Select-Object -First 1 -ExpandProperty ProcessId"]
  p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=10)
  return bool(p.stdout.strip())
 except Exception as e:
  note("PRECHECK_ERRO "+str(e))
  return True

def process(only_id=None):
 if (BASE/"BLOQUEIO-PUBLICACAO-ATIVO").exists() and not only_id:
  note("PUBLICACAO_PAUSADA: execucao em lote proibida; somente ID individual autorizado")
  return
 for folder in (QUEUE,DONE,FAILED):folder.mkdir(parents=True,exist_ok=True)
 # Previously interrupted runs are uncertain and must NEVER be silently published again.
 for orphan in QUEUE.glob("*.running"):
  try:
   age=time.time()-orphan.stat().st_mtime
   if age<300:
    note("EXECUCAO_RECENTE_EM_ANDAMENTO "+orphan.name)
    continue
   q=json.loads(orphan.read_text(encoding="utf-8-sig"))
   jobid=q.get("id")
   if not jobid or not re.fullmatch(r"[a-zA-Z0-9_-]{8,80}",str(jobid)):
    note("ORFAO_INVALIDO "+orphan.name)
    continue
   if (DONE/(str(jobid)+".json")).exists():
    note("ORFAO_JA_PUBLICADO "+orphan.name)
    archive=BASE/"historico"
    archive.mkdir(parents=True,exist_ok=True)
    orphan.rename(archive/(orphan.name+".apos-sucesso"))
    continue
   q["status"]="revisao_necessaria"
   q["error"]="PROCESSO_INTERROMPIDO: verificar Instagram antes de qualquer nova tentativa"
   dest=FAILED/(str(jobid)+".json")
   if not dest.exists():
    dest.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding="utf-8")
   orphan.unlink()
   note("ORFAO_ISOLADO_SEM_REENVIO "+str(jobid))
  except Exception as e:
   note("ORFAO_REQUER_REVISAO "+orphan.name+" "+str(e))
 for path in sorted(QUEUE.glob("*.json")):
  if only_id is not None and path.stem != only_id:continue
  try:q=json.loads(path.read_text(encoding="utf-8-sig"))
  except Exception as e:note("INVALID_JSON "+path.name+" "+str(e));continue
  from autorizacao_por_pacote import permitted, revoke
  if not permitted(q):
   note("BLOQUEADO_POR_PACOTE "+path.name)
   continue
  issue=validate(q)
  if issue=="futuro" or issue=="status não aprovado":continue
  if issue:
   note("PENDENTE "+path.name+" "+issue);continue
  if browser_profile_busy():
   note("ADIADO "+path.name+" navegador dedicado ocupado; sem envio")
   continue
  working=path.with_suffix(".running")
  try:os.rename(path,working)
  except OSError:continue
  q["status"]="tentativa_iniciada";q["attempt_started_at"]=now().isoformat()
  working.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding="utf-8")
  note("TENTATIVA "+q["id"])
  try:
   result=subprocess.run(["node",str(SCRIPTS/"publicar-seguro.cjs"),str(working)],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=240)
   output=(result.stdout+"\n"+result.stderr)[-3000:]
   state="publicado" if result.returncode==0 and "PUBLICACAO_CONFIRMADA" in output else "revisao_necessaria"
   q["status"]=state;q["attempt_finished_at"]=now().isoformat();q["log_tail"]=output
   target=(DONE if state=="publicado" else FAILED)/(q["id"]+".json")
   # Sem retries cegos: resultado incerto vai para revisar
   target.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding="utf-8")
   working.unlink()
   revoke(q["id"],state)
   note("RESULTADO "+q["id"]+" "+state+" exit="+str(result.returncode))
  except Exception as e:
   q["status"]="revisao_necessaria";q["error"]=str(e)
   target=FAILED/(q["id"]+".json")
   target.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding="utf-8")
   working.unlink()
   revoke(q["id"],"resultado-incerto")
   note("ERRO "+q["id"]+" "+str(e))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("mode",choices=["check","run","schedule-example"])
 p.add_argument("--only-id",default=None,help="Processa somente a fila desse ID; nunca outras postagens")
 a=p.parse_args()
 if a.mode=="schedule-example":
  print(json.dumps({"id":"ID_UNICO","status":"rascunho","approved_by":"","scheduled_at":"2026-11-11T08:00:00-03:00","files":["I:\\CAMINHO\\slide-01.png"],"caption":"Legenda aprovada"},ensure_ascii=False,indent=2))
 elif a.mode=="check":
  for x in (QUEUE,DONE,FAILED):x.mkdir(parents=True,exist_ok=True)
  print("FILA",len(list(QUEUE.glob("*.json"))),"PUBLICADOS",len(list(DONE.glob("*.json"))),"REVISAR",len(list(FAILED.glob("*.json"))))
  for f in QUEUE.glob("*.json"):
   try:print(f.name,validate(json.loads(f.read_text(encoding="utf-8"))))
   except Exception as e:print(f.name,str(e))
 else:
  BASE.mkdir(parents=True,exist_ok=True)
  with RUNLOCK.open("a+b") as lk:
   lk.seek(0)
   if not lk.read(1):
    lk.seek(0);lk.write(b"0");lk.flush()
   lk.seek(0)
   try: msvcrt.locking(lk.fileno(),msvcrt.LK_NBLCK,1)
   except OSError:
    note("PUBLICADOR_OCUPADO: outra execucao detem lock; nao iniciar segunda publicacao")
    return
   try: process(a.only_id)
   finally:
    lk.seek(0)
    msvcrt.locking(lk.fileno(),msvcrt.LK_UNLCK,1)
if __name__=="__main__":main()
