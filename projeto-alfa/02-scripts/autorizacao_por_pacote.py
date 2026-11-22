#!/usr/bin/env python3
# Autorizacao pontual de Instagram: NAO elimina o bloqueio global.
# Somente o ID, a conta, a data, a legenda e os PNGs com hashes exatos recebem passagem.
import datetime
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(r"I:\Projetos\Instagram-RobsonAlencar")
BASE = ROOT / "03-agendamentos" / "publicador"
LOCK = BASE / "BLOQUEIO-PUBLICACAO-ATIVO"
PERMITS = BASE / "liberacoes"
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
ACCOUNT = "pastorrobsonalencar"

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

def _digest(job):
    if not UUID.fullmatch(str(job.get("id", "")).lower()):
        raise ValueError("ID de carrossel invalido")
    if job.get("account") != ACCOUNT:
        raise ValueError("Conta do Instagram divergente")
    files = [Path(x) for x in job.get("files", [])]
    if not 1 <= len(files) <= 10 or any(not f.is_file() for f in files):
        raise ValueError("Midias ausentes ou quantidade invalida")
    details = []
    for f in files:
        h = hashlib.sha256()
        with f.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b""):
                h.update(chunk)
        details.append([str(f.resolve()).lower(), h.hexdigest()])
    payload = {
        "id": job["id"], "account": job["account"],
        "scheduled_at": job["scheduled_at"],
        "content_fingerprint": job.get("content_fingerprint"),
        "caption_sha256": hashlib.sha256(str(job.get("caption", "")).encode("utf-8")).hexdigest(),
        "files": details
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest()

def receipt_path(job_id):
    if not UUID.fullmatch(str(job_id).lower()):
        raise ValueError("ID invalido")
    return PERMITS / (str(job_id).lower() + ".json")

def validate_qa(job):
    from validar_pacote_publicacao import validate_package
    issues = validate_package(job)
    if issues:
        raise PermissionError("QA_REPROVADO: "+", ".join(issues))

def grant(job, *, user_message_id, session_id, action, question_part_id=None):
    if action not in ("publicar","agendar"):
        raise PermissionError("Acao nao autorizavel")
    if job.get("status")!="aprovado" or not job.get("approved_by"):
        raise PermissionError("Aprovacao do usuario nao registrada")
    if not re.fullmatch(r"msg_[A-Za-z0-9]+",str(user_message_id)):
        raise PermissionError("Resposta do usuario nao identificada")
    if not re.fullmatch(r"ses_[A-Za-z0-9]+",str(session_id)):
        raise PermissionError("Sessao nao identificada")
    due = datetime.datetime.fromisoformat(job["scheduled_at"])
    if due.tzinfo is None:
        raise PermissionError("Horario sem fuso")
    now=utc_now()
    future=due.astimezone(datetime.timezone.utc) > now
    if action=="agendar" and not future:
        raise PermissionError("Agendamento precisa ser futuro")
    if action=="publicar" and future:
        raise PermissionError("Publicacao imediata nao pode ter horario futuro")
    validate_qa(job)
    if question_part_id and not re.fullmatch(r"prt_[A-Za-z0-9]+",str(question_part_id)):
        raise PermissionError("ID_DA_PERGUNTA_INVALIDO")
    from verificar_resposta_interativa import verify
    verify(job,user_message_id=user_message_id,session_id=session_id,action=action,
           question_part_id=question_part_id)
    sig=_digest(job)
    expiry=(due.astimezone(datetime.timezone.utc)+datetime.timedelta(hours=6)) if action=="agendar" else (now+datetime.timedelta(minutes=25))
    record={
        "version":1,"id":job["id"],"account":ACCOUNT,"action":action,
        "signature_sha256":sig,"created_at":now.isoformat(),
        "expires_at":expiry.isoformat(),"session_id":session_id,
        "user_message_id":user_message_id,"authorization":"decisao_interativa_usuario_apos_qa",
        "answer_channel":"question" if question_part_id else "chat",
        "question_part_id":question_part_id
    }
    PERMITS.mkdir(parents=True,exist_ok=True)
    target=receipt_path(job["id"])
    # Exclusive create: concurrent models cannot replace an existing approval.
    with target.open("x",encoding="utf-8") as file:
        json.dump(record,file,ensure_ascii=False,indent=2)
    return record

def permitted(job):
    # Missing global lock alone is never proof of approval.
    try:
        p=receipt_path(job["id"])
        record=json.loads(p.read_text(encoding="utf-8-sig"))
        if record.get("version")!=1 or record.get("id")!=job["id"] or record.get("account")!=ACCOUNT:
            return False
        if record.get("authorization")!="decisao_interativa_usuario_apos_qa":return False
        if utc_now()>datetime.datetime.fromisoformat(record["expires_at"]):return False
        if record.get("signature_sha256")!=_digest(job):return False
        if record.get("action")!=("agendar" if job.get("publish_mode")=="agendado" else "publicar"):return False
        validate_qa(job)
        return True
    except (ValueError,TypeError,KeyError,OSError,PermissionError):
        return False

def require_permit(job):
    if not permitted(job):
        raise PermissionError("BLOQUEIO_ATIVO: somente pacote com QA completo e decisao explicita pode passar")

def revoke(job_id, result="revogada"):
    p=receipt_path(job_id)
    if not p.exists():return
    history=PERMITS/"historico"
    history.mkdir(parents=True,exist_ok=True)
    archive=history/(str(job_id)+"-"+str(result)+".json")
    if archive.exists():
        archive=history/(str(job_id)+"-"+str(result)+"-"+str(datetime.datetime.now().timestamp()).replace(".","-")+".json")
    p.rename(archive)
