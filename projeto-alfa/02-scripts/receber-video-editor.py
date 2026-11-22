# -*- coding: utf-8 -*-
"""Ponte segura Editor E -> revisão do Instagram I.
Nunca agenda/publica. Exige MP4 validado e áudio real. Sem reenvio duplicado.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,uuid,datetime
IG=Path(r'I:\Projetos\Instagram-RobsonAlencar')
ED=Path(r'E:\EDITOR AUTOMATICO\VIDEO')
REVIEW=IG/'01-conteudo'/'reels-a-revisar'
def probe(src):
 raw=subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)],timeout=25)
 meta=json.loads(raw)
 streams=meta.get('streams',[])
 video=next((s for s in streams if s.get('codec_type')=='video'),None)
 audio=next((s for s in streams if s.get('codec_type')=='audio'),None)
 if not video:raise ValueError('MP4 sem vídeo')
 if (video.get('width'),video.get('height'))!=(1080,1920):raise ValueError('Reel deve ser vertical 1080x1920')
 if not audio:raise ValueError('MP4 sem áudio, revisar antes de enviar para Instagram')
 duration=float(meta.get('format',{}).get('duration',0))
 if not (1<=duration<=180):raise ValueError('Duração do MP4 fora de 1 a 180 segundos')
 return {'width':1080,'height':1920,'duration':round(duration,3),
         'video_codec':video.get('codec_name'),'audio_codec':audio.get('codec_name')}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
 return h.hexdigest()
def transfer(video,title):
 src=video.resolve(strict=True)
 if ED.resolve() not in src.parents:raise ValueError('Aceito apenas resultado do Editor oficial do drive E')
 if src.suffix.lower()!='.mp4':raise ValueError('Formato não é MP4')
 meta=probe(src)
 sha=digest(src)
 REVIEW.mkdir(parents=True,exist_ok=True)
 # Manifestos anteriores são lidos, mídias não são alteradas.
 for f in REVIEW.glob('*.json'):
  try:
   info=json.loads(f.read_text(encoding='utf-8-sig'))
   if info.get('source_sha256')==sha:
    print('JA_EXISTE',info.get('destino'), 'REVIEW_ONLY',flush=True)
    return info
  except (ValueError,UnicodeError,OSError):continue
 safe=re.sub(r'[^a-z0-9-]','-',title.lower().strip(),flags=re.I).strip('-')[:44] or 'video'
 identifier=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+safe+'-'+uuid.uuid4().hex[:7]
 target=REVIEW/(identifier+'.mp4')
 temp=REVIEW/(identifier+'.partial')
 try:
  with src.open('rb') as original,temp.open('xb') as copy:
   shutil.copyfileobj(original,copy,1024*1024)
  if digest(temp)!=sha:raise RuntimeError('Cópia não passou no hash')
  temp.replace(target)
 except Exception:
  temp.unlink(missing_ok=True)
  raise
 record={
  'id':identifier,'status':'aguardando_revisao_humana','published':False,
  'scheduled':False,'approved':False,'source_sha256':sha,
  'origem':str(src),'destino':str(target),'format':meta,
  'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'caption_status':'pendente','thumbnail_status':'pendente','rights_check':'pendente',
  'observacao':'SEM PUBLICAÇÃO. Revisar visual, áudio, identidade, legenda, texto bíblico, direitos e conta antes de aprovar.'
 }
 manifest=REVIEW/(identifier+'.json')
 manifest.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 print('REEL_ENVIADO_PARA_REVISAO',target,'BYTES',target.stat().st_size,flush=True)
 print('MANIFESTO',manifest,'PUBLISHED',False,'SCHEDULED',False,flush=True)
 return record
def main():
 p=argparse.ArgumentParser()
 g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--video',help='MP4 pronto no Editor E')
 g.add_argument('--job',help='ID da produção do Estúdio')
 g.add_argument('--check',action='store_true',help='Verifica dependências, sem cópia')
 p.add_argument('--titulo',default='reel')
 args=p.parse_args()
 if args.check:
  print('IG_ROOT',IG.is_dir(),'EDITOR',ED.is_dir(),'FFPROBE',shutil.which('ffprobe') is not None)
  print('REVIEW_FOLDER',REVIEW.is_dir(),'BRIDGE_READY',IG.is_dir() and ED.is_dir() and bool(shutil.which('ffprobe')))
  return
 if args.job:
  if not re.fullmatch(r'[0-9a-f]{12}',args.job):raise ValueError('ID do job inválido')
  j=ED/'out'/'pedidos'/args.job
  status=json.loads((j/'status.json').read_text(encoding='utf-8'))
  if status.get('status')!='concluido' or status.get('qa_rejected'):raise ValueError('Pedido não aprovado na validação final; não enviar parcial')
  if status.get('mode')=='demonstracao':raise ValueError('Pedido de demonstração não pode entrar na revisão de produção')
  requested=status.get('secs_requested')
  actual=status.get('duration')
  if requested and actual and not (abs(float(actual)-float(requested))<=max(1.5,float(requested)*.15)):
   raise ValueError(f'Duração divergente: solicitado {requested}s, produzido {actual}s')
  src=j/'resultado.mp4'
 else:
  src=Path(args.video)
  # Supplying --video cannot bypass the approval/duration checks for Estúdio jobs.
  resolved=src.resolve(strict=True)
  job_dir=ED/'out'/'pedidos'
  if job_dir in resolved.parents:
   status_file=resolved.parent/'status.json'
   if not status_file.is_file():raise ValueError("Resultado sem manifesto de produção")
   st=json.loads(status_file.read_text(encoding="utf-8"))
   if st.get("status")!="concluido" or st.get("mode")=="demonstracao" or st.get("qa_rejected"):
    raise ValueError("O arquivo não corresponde a uma produção aprovada para revisão")
   requested=st.get("secs_requested");actual=st.get("duration")
   if requested and actual and not (abs(float(actual)-float(requested))<=max(1.5,float(requested)*.15)):
    raise ValueError("Arquivo com duração divergente")
 transfer(src,args.titulo)
if __name__=='__main__':
 try:main()
 except Exception as exc:print('ERRO',str(exc),file=sys.stderr);sys.exit(1)
