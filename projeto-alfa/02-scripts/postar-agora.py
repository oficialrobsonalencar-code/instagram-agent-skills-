#!/usr/bin/env python3
# Ordem explicita "poste agora" = autorizacao para uma tentativa imediata.
# Nao executa para pedidos de simples criacao nem faz retries cegos.
import argparse, datetime, json, pathlib, re, subprocess, sys, uuid
ROOT=pathlib.Path(r"I:\Projetos\Instagram-RobsonAlencar")
BASE=ROOT/"03-agendamentos"/"publicador"
QUEUE=BASE/"fila"
DONE=BASE/"processados"
REVIEW=BASE/"revisar"
def main():
    parser=argparse.ArgumentParser(description="Publicacao IMEDIATA, quando ordenada explicitamente pelo usuario")
    parser.add_argument("--pasta",required=True,help="pasta de 01-conteudo com imagens em out/")
    parser.add_argument("--conta",required=True,help="perfil Instagram de destino")
    parser.add_argument("--id",dest="job_id",help="UUID gerado e vinculado ao pacote na etapa de revisao; nunca confere aprovacao")
    parser.add_argument("--sessao",help="sessao do OpenCode que colheu a decisao")
    parser.add_argument("--resposta",help="ID da resposta explicita do usuario")
    parser.add_argument("--pergunta",help="ID de ferramenta question completada, quando a resposta veio do formulario")

    parser.add_argument("--autorizado-pelo-usuario",action="store_true",help="usar apenas quando a ordem atual foi explicitamente postar")
    parser.add_argument("--legenda",help="arquivo .txt com legenda alternativa")
    parser.add_argument("--quando",help="Agendar para data/hora futura com fuso, ex: 2026-11-12T08:00:00-03:00; sem este argumento publica agora")
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    # Bloqueio global continua ativo. Liberacao e exclusivamente por pacote e QA.
    if not args.autorizado_pelo_usuario:
        raise ValueError("SEM_AUTORIZACAO: pedido explicito de postagem, imediata ou agendada, e obrigatorio")
    agora=datetime.datetime.now(datetime.timezone.utc)
    quando=agora
    if args.quando:
        quando=datetime.datetime.fromisoformat(args.quando)
        if quando.tzinfo is None:
            raise ValueError("FUSO_OBRIGATORIO: exemplo 2026-11-12T08:00:00-03:00")
        if quando.astimezone(datetime.timezone.utc)<=agora:
            raise ValueError("HORARIO_PASSADO: informe horario futuro para agendar")
    agendado=bool(args.quando)
    if args.job_id and not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", args.job_id.lower()):
        raise ValueError("ID_REVISADO_INVALIDO: exigido UUID da revisao do pacote exato")
    job_id=args.job_id or str(uuid.uuid4())
    account=args.conta.strip().lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9._]{2,30}",account):
        raise ValueError("CONTA_INVALIDA")
    root=(ROOT/"01-conteudo").resolve()
    project=(root/args.pasta).resolve()
    if root not in project.parents or not project.is_dir():
        raise ValueError("PASTA_INVALIDA: deve estar dentro de 01-conteudo")
    out=project/"out"
    if not out.is_dir(): out=project
    files=sorted(out.glob("slide-*.png"))
    if not files:
        files=sorted(f for f in out.iterdir() if f.suffix.lower() in (".mp4",".png",".jpg",".jpeg")) if out.is_dir() else []
    if not 1<=len(files)<=10:
        raise ValueError("MIDIA_AUSENTE: necessario 1 a 10 arquivos validos")
    candidates=([pathlib.Path(args.legenda)] if args.legenda else [])+[project/x for x in ("legenda.txt","legenda-8h.txt","legenda-ceia.txt")]
    caption_path=next((p for p in candidates if p.is_file()),None)
    if caption_path is None:
        raise ValueError("LEGENDA_AUSENTE: produzir legenda apropriada para o conteudo antes da tentativa")
    caption=caption_path.read_text(encoding="utf-8-sig").strip()
    if not caption:raise ValueError("LEGENDA_VAZIA")
    # Bloqueio editorial: o recibo deve corresponder exatamente ao TXT atual.
    from validar_legenda_editorial import check as validar_legenda
    problemas, _recibo = validar_legenda(caption_path)
    if problemas:
        raise ValueError("LEGENDA_SEM_REVISAO: "+", ".join(problemas))

    # Respeita exclusividade de outras tentativas no publicador.
    QUEUE.mkdir(parents=True,exist_ok=True)
    DONE.mkdir(parents=True,exist_ok=True)
    REVIEW.mkdir(parents=True,exist_ok=True)
    fingerprint=json.dumps({"account":account,"files":[str(f) for f in files],"caption":caption},ensure_ascii=False,sort_keys=True)
    import hashlib
    digest=hashlib.sha256(fingerprint.encode()).hexdigest()
    for folder in (QUEUE,DONE,REVIEW,BASE/'historico'):
        for item in list(folder.glob("*.json"))+list(folder.glob("*.running"))+list(folder.glob("*.review-before-success-*.json")):
            try:
                data=json.loads(item.read_text(encoding="utf-8-sig"))
                if data.get("content_fingerprint")==digest:
                    raise ValueError("DUPLICIDADE: material ja esta ou esteve em tentativa de publicacao: "+str(item))
            except (json.JSONDecodeError,UnicodeError):pass
    if args.dry_run:
        from validar_pacote_publicacao import validate_package
        candidate={"id":job_id,"status":"aprovado","approved_by":"SIMULACAO_NAO_AUTORIZADA",
                   "account":account,"scheduled_at":quando.isoformat(),"files":[str(f) for f in files],
                   "caption":caption,"publish_mode":"agendado" if agendado else "imediato"}
        qa_problems=validate_package(candidate)
        print(json.dumps({"qa_ok":not qa_problems,"qa_problems":qa_problems,
           "authorized":False,"publishable":False,"account":account,"job_id":job_id,
           "media_count":len(files),"caption":str(caption_path),
           "mode":"agendado" if agendado else "imediato","scheduled_at":quando.isoformat(),
           "send":False},ensure_ascii=False))
        return
    q={"id":job_id,"status":"aprovado","approved_by":"ordem_explicita_usuario","account":account,
       "scheduled_at":quando.isoformat(),"files":[str(f) for f in files],
       "caption":caption,"content_fingerprint":digest,"publish_mode":"agendado" if agendado else "imediato","authorization":"ordem_explicita_usuario"}
    from autorizacao_por_pacote import grant, revoke, require_permit, validate_qa
    # QA tecnico, visual, editorial e hashes devem existir ANTES da liberacao.
    validate_qa(q)
    if (BASE/"BLOQUEIO-PUBLICACAO-ATIVO").exists():
        if not args.sessao or not args.resposta:
            raise PermissionError("LIBERACAO_NECESSITA_RESPOSTA_INTERATIVA")
        grant(q,user_message_id=args.resposta,session_id=args.sessao,
              action="agendar" if agendado else "publicar",question_part_id=args.pergunta)
    require_permit(q)
    target=QUEUE/(q["id"]+".json")
    try:
        with target.open("x",encoding="utf-8") as out:
            json.dump(q,out,ensure_ascii=False,indent=2)
    except Exception:
        revoke(q["id"],"falha-criacao-fila")
        raise
    print("POSTAGEM_AUTORIZADA",target)
    if agendado:
        schedule=subprocess.run(
            [sys.executable,str(ROOT/"02-scripts"/"agendar_post_aprovado.py"),"agendar","--id",q["id"]],
            capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=60
        )
        if schedule.returncode != 0 or "CONFIRMADO " not in schedule.stdout:
            target.unlink(missing_ok=True)
            revoke(q["id"],"falha-agendamento")
            raise RuntimeError("AGENDAMENTO_NAO_CONFIRMADO; fila desfeita: "+(schedule.stderr or schedule.stdout)[-500:])
        print("POSTAGEM_AGENDADA_CONFIRMADA",quando.isoformat(),"CONTA",account,"MIDIAS",len(files),"ID",q["id"])
        print(schedule.stdout)
        return
    # Pedido sem horario futuro: processar a fila imediatamente, sem aguardar o agendador.
    result=subprocess.run([sys.executable,str(ROOT/"02-scripts"/"fila-publicacao.py"),"run","--only-id",q["id"]],timeout=275,capture_output=True,text=True,encoding="utf-8",errors="replace")
    print(result.stdout[-3000:]);print(result.stderr[-900:],file=sys.stderr)
    if result.returncode:raise RuntimeError("PUBLICADOR_ERRO: "+str(result.returncode))
    done=DONE/(q["id"]+".json")
    review=REVIEW/(q["id"]+".json")
    if done.exists():print("PUBLICACAO_CONFIRMADA",done)
    elif review.exists():raise RuntimeError("RESULTADO_INCERTO: revisar evidencias sem publicar novamente")
    else:raise RuntimeError("PUBLICACAO_NAO_CONFIRMADA: fila pendente, revisar log sem repetir")
if __name__=="__main__":
    try:
        # Serializa duas ordens simultaneas da IA usando lock do Windows.
        # A verificacao de duplicidade e a criacao da fila ficam protegidas.
        import msvcrt
        BASE.mkdir(parents=True,exist_ok=True)
        with (BASE/".postar-agora.lock").open("a+b") as lock:
            lock.seek(0)
            if not lock.read(1):
                lock.seek(0); lock.write(b"0"); lock.flush()
            lock.seek(0)
            try: msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
            except OSError:
                raise RuntimeError("PUBLICACAO_EM_ANDAMENTO: outra tentativa utiliza esta fila")
            try: main()
            finally:
                lock.seek(0)
                msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
    except Exception as e:
        print("ERRO",str(e),file=sys.stderr)
        sys.exit(1)
