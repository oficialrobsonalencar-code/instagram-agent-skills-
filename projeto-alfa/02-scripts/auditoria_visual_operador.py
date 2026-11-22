# -*- coding: utf-8 -*-
"""Operacao MANUAL de assinatura de auditoria visual. Nunca executar por agente.

Chave PRIVADA criptografada permanece fora do projeto e do GitHub.
O auditor humano digita pessoalmente a confirmacao e a senha local.
Nenhum modo de aprovar em lote ou sem revisao.
"""
import argparse, base64, datetime, getpass, hashlib, json, os, re, sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, BestAvailableEncryption,
    load_pem_private_key, NoEncryption)
from verificar_aprovacao_visual import (
    PUBLIC_KEY_PATH, UUID, canonical_bytes, key_id_from_public_key,
    verify_visual_receipt)

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "01-conteudo"
KEY_DIR = Path(os.environ["LOCALAPPDATA"]) / "Instagram-Auditoria-Visual"
PRIVATE_KEY = KEY_DIR / "auditoria-ed25519-privada-CRIPTOGRAFADA.pem"
ACCOUNT = "pastorrobsonalencar"


def create_key_pair(password: bytes, private_path=PRIVATE_KEY, public_path=PUBLIC_KEY_PATH):
    """Usado apos a senha pessoal ser fornecida; nao sobrescreve chaves existentes."""
    if len(password) < 8:
        raise ValueError("SENHA_LOCAL_MINIMO_8_CARACTERES")
    private_path,public_path = Path(private_path),Path(public_path)
    if private_path.exists() or public_path.exists():
        raise FileExistsError("CHAVE_JA_EXISTE: nao substituir. Verifique a identidade e o backup.")
    private_path.parent.mkdir(parents=True,exist_ok=True)
    public_path.parent.mkdir(parents=True,exist_ok=True)
    key=Ed25519PrivateKey.generate()
    data=key.private_bytes(Encoding.PEM,PrivateFormat.PKCS8,BestAvailableEncryption(password))
    # Exclusive creation; never include unencrypted private key in project/github.
    with private_path.open("xb") as fh:fh.write(data)
    try:
        with public_path.open("xb") as fh:
            fh.write(key.public_key().public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo))
    except Exception:
        private_path.unlink(missing_ok=True)
        raise
    return key_id_from_public_key(key.public_key())


def resolve_package(folder):
    if not isinstance(folder,str) or not folder or Path(folder).is_absolute():
        raise ValueError("PASTA_RELATIVA_OBRIGATORIA")
    root=CONTENT.resolve()
    project=(CONTENT/folder).resolve()
    if root not in project.parents:
        raise ValueError("PASTA_FORA_DO_CONTEUDO")
    if not project.is_dir():
        raise FileNotFoundError("PASTA_DO_TRABALHO_AUSENTE")
    output=project/"out" if (project/"out").is_dir() else project
    paths=sorted(output.glob("slide-*.png"))
    if not 1 <= len(paths) <= 10:
        raise ValueError("SLIDES_INVALIDOS")
    if any(p.name!=f"slide-{i:02d}.png" for i,p in enumerate(paths,1)):
        raise ValueError("SEQUENCIA_SLIDES_INVALIDA")
    if any(p.is_symlink() or p.resolve().parent != output.resolve() for p in paths):
        raise ValueError("MIDIA_FORA_DA_PASTA")
    caption=project/"legenda.txt"
    if not caption.is_file() or caption.is_symlink():
        raise ValueError("LEGENDA_TXT_AUSENTE")
    qa_file=output/"qa-relatorio.json"
    if not qa_file.is_file():
        raise ValueError("QA_TECNICO_AUSENTE")
    qa=json.loads(qa_file.read_text(encoding="utf-8-sig"))
    if qa.get("aprovado_tecnicamente") is not True or qa.get("erros") or qa.get("slides")!=len(paths):
        raise ValueError("QA_TECNICO_REPROVADO")
    text=caption.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError("LEGENDA_VAZIA")
    return output,paths,text


def prepare_receipt(folder,job_id,auditor="auditor-humano"):
    if not UUID.fullmatch(job_id.lower()):
        raise ValueError("JOB_UUID_INVALIDO")
    if auditor != "auditor-humano":
        raise ValueError("ASSINATURA_HUMANA_NAO_PODE_FINGIR_AGENTE")
    output,paths,caption=resolve_package(folder)
    payload={
        "version":2,"alg":"Ed25519","key_id":None,"aprovado":True,
        "revisor":auditor,"job_id":job_id,"account":ACCOUNT,
        "audited_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "images_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "caption_sha256":hashlib.sha256(caption.encode("utf-8")).hexdigest(),
    }
    return output,paths,caption,payload


def sign_prepared_receipt(payload,private_key_path,password,public_key_path=PUBLIC_KEY_PATH):
    """Assina APENAS apos a confirmacao manual no terminal do auditor."""
    private=load_pem_private_key(Path(private_key_path).read_bytes(),password=password)
    if not isinstance(private,Ed25519PrivateKey):
        raise ValueError("CHAVE_PRIVADA_ALGORITMO_INVALIDO")
    receipt=dict(payload)
    receipt["key_id"]=key_id_from_public_key(private.public_key())
    receipt["signature"]="base64:"+base64.b64encode(private.sign(canonical_bytes(receipt))).decode("ascii")
    # No need to print private material. The caller validates against the pinned public key.
    if not Path(public_key_path).exists():
        raise ValueError("CHAVE_PUBLICA_NAO_INSTALADA")
    return receipt


def command_init():
    print("Configuracao local do auditor responsavel. A senha NAO deve ser compartilhada com agentes.")
    one=getpass.getpass("Crie a senha privada da auditoria: ").encode("utf-8")
    two=getpass.getpass("Confirme a senha privada: ").encode("utf-8")
    if one != two:raise ValueError("CONFIRMACAO_DA_SENHA_DIVERGENTE")
    key_id=create_key_pair(one)
    print("CHAVE_PUBLICA_INSTALADA",str(PUBLIC_KEY_PATH))
    print("CHAVE_PRIVADA_CRIPTOGRAFADA_FORA_DO_PROJETO",str(PRIVATE_KEY))
    print("IDENTIFICADOR_DA_CHAVE",key_id)


def command_approve(folder,job_id):
    output,paths,caption,payload=prepare_receipt(folder,job_id)
    proof=output/"aprovacao-visual.json"
    if proof.exists():
        raise FileExistsError("COMPROVANTE_EXISTENTE: faca backup manual e realize nova revisao antes de substituir")
    print("AUDITORIA VISUAL LOCAL: abra e inspecione CADA ARQUIVO em",str(output))
    for p in paths:print("SLIDE_PARA_REVISAR",p.name)
    print("LEGENDA_INTEGRAL_PARA_CONFERENCIA:\n"+caption)
    print("Verifique corte, textos, referencia, fonte, identidade, assinatura e conteudo real. A verificacao matematica nao substitui inspecao.")
    phrase="REVISEI E APROVO "+job_id
    typed=input("Apos revisar os PNGs e a legenda, digite EXATAMENTE '"+phrase+"': ").strip()
    if typed != phrase:raise PermissionError("AUDITOR_NAO_CONFIRMOU_REVISAO_REAL")
    password=getpass.getpass("Digite a senha local privada da auditoria: ").encode("utf-8")
    receipt=sign_prepared_receipt(payload,PRIVATE_KEY,password)
    # Check CURRENT files, not only their captured hashes, immediately before writing.
    verify_visual_receipt(receipt,paths,caption,job_id,ACCOUNT)
    with proof.open("x",encoding="utf-8") as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
    print("APROVACAO_VISUAL_ASSINADA_COM_CHAVE_HUMANA",str(proof))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Somente operador humano. Nao executar por agente OpenCode.")
    parser.add_argument("etapa",choices=["inicializar","aprovar"])
    parser.add_argument("--pasta",help="caminho relativo ao 01-conteudo")
    parser.add_argument("--job-id",help="UUID exato da revisao")
    args=parser.parse_args()
    try:
        if args.etapa=="inicializar":command_init()
        else:
            if not args.pasta or not args.job_id:raise ValueError("PASTA_E_JOB_ID_OBRIGATORIOS")
            command_approve(args.pasta,args.job_id)
    except Exception as exc:
        print(type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(1)
