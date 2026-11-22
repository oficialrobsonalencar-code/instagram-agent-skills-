#!/usr/bin/env python3
"""Diagnostico somente leitura do agendamento; nao agenda nem publica."""
import argparse,datetime,json,subprocess,sys
from pathlib import Path
ROOT=Path(r"I:\Projetos\Instagram-RobsonAlencar")
BASE=ROOT/"03-agendamentos"/"publicador"
LOCK=BASE/"BLOQUEIO-PUBLICACAO-ATIVO"

def read_jobs(directory):
    result=[]
    for f in sorted((BASE/directory).glob("*.json")):
        try:
            q=json.loads(f.read_text(encoding="utf-8-sig"))
            item={"id":q.get("id") or f.stem,
                  "status":q.get("status"),"scheduled_at":q.get("scheduled_at"),
                  "account":q.get("account"),
                  "media_count":len(q.get("files") or []),
                  "error":str(q.get("error") or "")[:380]}
            if directory in ("fila","revisar"):
                try:
                    from validar_pacote_publicacao import validate_package
                    item["qa_failures"]=validate_package(q)
                except Exception as exc:
                    item["qa_failures"]=["VALIDADOR_INDISPONIVEL: "+type(exc).__name__]
            item["upload_attempted"]=bool(q.get("attempt_started_at"))
            item["upload_confirmed"]=q.get("status")=="publicado" and bool(q.get("attempt_finished_at"))
            item["needs_user_decision"]=directory=="revisar"
            result.append(item)
        except Exception as exc:
            result.append({"id":f.stem,"status":"JSON_INVALIDO","error":str(exc)[:180]})
    return result

def get_tasks():
    script='''$ErrorActionPreference="Stop"
Get-ScheduledTask -ErrorAction Stop | Where-Object {$_.TaskName -eq "IG Publicador Seguro - Fila Aprovada" -or $_.TaskName -like "IG Robson Post Aprovado *"} | ForEach-Object {
 $t=$_; $i=Get-ScheduledTaskInfo -TaskName $t.TaskName -TaskPath $t.TaskPath
 [PSCustomObject]@{name=$t.TaskName;state=[string]$t.State;next_run=if($i.NextRunTime.Year -ge 2026){$i.NextRunTime.ToString("o")}else{$null};last_result=$i.LastTaskResult;last_run=if($i.LastRunTime.Year -ge 2026){$i.LastRunTime.ToString("o")}else{$null};wake=[bool]$t.Settings.WakeToRun;start_when_available=[bool]$t.Settings.StartWhenAvailable}
} | ConvertTo-Json -Compress'''
    try:
        r=subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-Command",script],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=20)
        if r.returncode:return [],"WINDOWS_TASK_QUERY_FAILED: "+(r.stderr or r.stdout)[-250:]
        x=json.loads(r.stdout) if r.stdout.strip() else []
        return x if isinstance(x,list) else [x],None
    except Exception as exc:return [],type(exc).__name__+": "+str(exc)[:140]

def status():
    result={"at":datetime.datetime.now().astimezone().isoformat(),
            "account":"pastorrobsonalencar",
            "block_active":LOCK.is_file(),
            "block_reason":LOCK.read_text(encoding="utf-8-sig",errors="replace").strip()[:300] if LOCK.exists() else "",
            "queue":read_jobs("fila"),"review":read_jobs("revisar"),
            "published_history_count":len(list((BASE/"processados").glob("*.json")))}
    result["tasks"],result["task_error"]=get_tasks()
    result["global_lock_mode"]="BLOQUEIO_EM_LOTE; excecao apenas por pacote com QA e resposta verificavel"
    from autorizacao_por_pacote import permitted
    authorized=[]
    for p in sorted((BASE/"fila").glob("*.json")):
        try:
            job=json.loads(p.read_text(encoding="utf-8-sig"))
            due=datetime.datetime.fromisoformat(job["scheduled_at"])
            if permitted(job) and due.tzinfo and due.astimezone(datetime.timezone.utc)>datetime.datetime.now(datetime.timezone.utc):
                authorized.append(job["id"])
        except Exception:continue
    result["authorized_future_job_ids"]=authorized
    result["can_schedule_new_post"]=bool(authorized)
    result["can_review_and_ask"]=True
    result["message"]="FILA em revisar nao prova publicacao nem agendamento; corrigir QA e perguntar ao usuario antes de agir."
    return result
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    r=status()
    if args.json:print(json.dumps(r,ensure_ascii=False,indent=2))
    else:
        print("AGENDAMENTO_IG",r["at"])
        print("BLOQUEIO",r["block_active"],r["block_reason"])
        print("FILA",len(r["queue"]),"REVISAR",len(r["review"]),"PUBLICADOS_ANTERIORES",r["published_history_count"])
        for q in r["queue"]:print("PENDENTE",q["id"],q["status"],q.get("scheduled_at"),q.get("qa_failures"))
        for t in r["tasks"]:print("TAREFA",t["name"],t["state"],"PROXIMO",t["next_run"],"RESULTADO",t["last_result"])
    if r["task_error"]:
        print("ERRO_AGENDADOR",r["task_error"],file=sys.stderr)
        raise SystemExit(2)
