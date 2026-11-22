from pathlib import Path
import json,hashlib,re
from PIL import Image

def file_hash(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as fh:
  for chunk in iter(lambda:fh.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()

def validate_package(job):
 """Fail closed: approval words are NOT proof of image review or caption review."""
 problems=[]
 if job.get("status")!="aprovado" or not job.get("approved_by"):
  problems.append("APROVACAO_DECLARADA_AUSENTE")
 files=[Path(x) for x in job.get("files",[])]
 if not 1<=len(files)<=10 or not all(x.is_file() for x in files):
  return problems+["ARQUIVOS_AUSENTES_OU_QUANTIDADE_INVALIDA"]
 if any(x.suffix.lower()!=".png" for x in files):
  problems.append("CARROSSEL_APENAS_PNG")
 if len(set(str(p.resolve()).casefold() for p in files))!=len(files):
  problems.append("MIDIAS_REPETIDAS")
 folder=files[0].parent
 if any(p.parent.resolve()!=folder.resolve() for p in files):
  problems.append("PACOTE_MISTURA_PASTAS")
 for i,p in enumerate(files,1):
  if p.name!=f"slide-{i:02d}.png": problems.append("ORDEM_SLIDES_INVALIDA")
  try:
   with Image.open(p) as im:
    if im.size!=(1080,1350):problems.append("RESOLUCAO_INVALIDA:"+p.name)
    im.verify()
  except Exception:problems.append("PNG_INVALIDO:"+p.name)
 qa=folder/"qa-relatorio.json"
 if not qa.is_file():problems.append("QA_TECNICO_AUSENTE")
 else:
  try:
   q=json.loads(qa.read_text(encoding="utf-8-sig"))
   if q.get("slides")!=len(files) or q.get("erros") or q.get("aprovado_tecnicamente") is not True:
    problems.append("QA_TECNICO_REPROVADO")
   if q.get("aprovado_visualmente") is not True or q.get("tipografia_confirmada") is not True or q.get("publicavel") is not True:
    problems.append("QA_VISUAL_NAO_APROVADO")
  except Exception:problems.append("QA_TECNICO_INVALIDO")
 caption=str(job.get("caption",""))
 if not caption.strip():problems.append("LEGENDA_VAZIA")
 caption_path=folder.parent/"legenda.txt" if folder.name=="out" else folder/"legenda.txt"
 if not caption_path.is_file():
  problems.append("LEGENDA_TXT_AUSENTE")
 else:
  if caption_path.read_text(encoding="utf-8-sig").strip()!=caption.strip():
   problems.append("LEGENDA_DIFERE_DO_PACOTE")
  try:
   from validar_legenda_editorial import check
   issues,_=check(caption_path)
   if issues: problems.append("HUMANIZER_E_LEGENDA_NAO_VALIDADA")
  except Exception:problems.append("VERIFICADOR_EDITORIAL_INDISPONIVEL")
 proof=folder/"aprovacao-visual.json"
 if not proof.is_file():
  problems.append("COMPROVANTE_DE_AUDITORIA_VISUAL_AUSENTE")
 else:
  try:
   a=json.loads(proof.read_text(encoding="utf-8-sig"))
   actual={p.name:file_hash(p) for p in files}
   if a.get("aprovado") is not True or a.get("revisor") not in {"auditor-deus", "codex-visual"}:
    problems.append("AUDITOR_VISUAL_NAO_APROVOU")
   if a.get("images_sha256")!=actual:problems.append("SLIDES_MUDARAM_APOS_AUDITORIA")
   if a.get("caption_sha256")!=hashlib.sha256(caption.encode("utf-8")).hexdigest():
    problems.append("LEGENDA_MUDOU_APOS_AUDITORIA")
   if a.get("job_id")!=job.get("id"):problems.append("APROVACAO_DE_OUTRA_TAREFA")
  except Exception:problems.append("COMPROVANTE_VISUAL_INVALIDO")
 return problems
