from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import argparse,json,datetime,subprocess,sys
ap=argparse.ArgumentParser()
ap.add_argument('--manifest',required=True)
ap.add_argument('--resultado',required=True)
ap.add_argument('--saida',required=True)
args=ap.parse_args()
here=Path(__file__).resolve().parent
check=subprocess.run([sys.executable,str(here/'validar_fidelidade.py'),'--manifest',args.manifest],capture_output=True,text=True)
if check.returncode!=0:
 print(check.stderr.strip());sys.exit(7)
m=Path(args.manifest).resolve()
spec=json.loads(m.read_text(encoding='utf-8-sig'))
raw=Path(spec['referencia'])
ref=raw if raw.is_absolute() else (m.parent/raw).resolve()
result=Path(args.resultado).resolve()
if not result.is_file():
 print('BLOQUEADO: resultado inexistente',file=sys.stderr);sys.exit(7)
dest=Path(args.saida).resolve()
dest.mkdir(parents=True,exist_ok=True)
with Image.open(ref) as a, Image.open(result) as b:
 a=a.convert('RGB');b=b.convert('RGB')
 canvas=Image.new('RGB',(1200,830),'#101010')
 for idx,(img,title) in enumerate([(a,'REFERENCIA AUTORIZADA'),(b,'RESULTADO GERADO')]):
  tile=ImageOps.contain(img,(550,750),Image.Resampling.LANCZOS)
  x=30+idx*600+(550-tile.width)//2
  y=55+(750-tile.height)//2
  canvas.paste(tile,(x,y))
  ImageDraw.Draw(canvas).text((30+idx*600,14),title,fill='white')
 comp=dest/'comparacao-lado-a-lado.jpg'
 canvas.save(comp,quality=90)
report={'estado':'RASCUNHO_AGUARDANDO_REVISAO_VISUAL','referencia':str(ref),'resultado':str(result),'comparacao':str(comp),'requer':'verificar composicao, enquadramento, tipografia, cores, textura, proporcoes e elementos extras; registrar divergencias antes de aprovacao','gerado_em':datetime.datetime.now().isoformat()}
(dest/'revisao-fidelidade.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print('COMPARACAO_CRIADA',comp)
print('ESTADO',report['estado'])
