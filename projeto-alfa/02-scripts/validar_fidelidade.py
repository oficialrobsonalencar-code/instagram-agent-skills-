from pathlib import Path
import json,sys,argparse
from PIL import Image
p=argparse.ArgumentParser()
p.add_argument('--manifest',required=True)
a=p.parse_args()
m=Path(a.manifest).resolve()
def fail(msg):
 print('FIDELIDADE BLOQUEADA:',msg,file=sys.stderr)
 raise SystemExit(7)
if not m.is_file():fail('manifesto ausente')
try:d=json.loads(m.read_text(encoding='utf-8-sig'))
except Exception as e:fail('manifesto JSON invalido: '+str(e))
if d.get('tipo') not in ('reproducao_fiel','adaptacao_referencia'):fail('tipo deve ser reproducao_fiel ou adaptacao_referencia')
for k in ('objetivo','preservar','alteracoes_permitidas','analise_visual_referencia'):
 v=d.get(k)
 if not v or (isinstance(v,str) and len(v.strip())<12):fail('campo insuficiente: '+k)
for key in ('referencia','foto'):
 raw=d.get(key,'')
 if not isinstance(raw,str) or not raw:fail('caminho ausente: '+key)
 f=Path(raw)
 if not f.is_absolute():f=(m.parent/f).resolve()
 if not f.is_file():fail('arquivo nao encontrado: '+key+'='+str(f))
 try:
  with Image.open(f) as im:
   im.verify()
 except Exception as e:fail('imagem ilegivel: '+key+' '+str(e))
allowed=d.get('autorizado_usuario_atual',{})
if not isinstance(allowed,dict) or not allowed.get('referencia') or not allowed.get('foto'):
 fail('declaracao de autorizacao explicita ausente')
if not d.get('referencia_pixels_inspecionados'):fail('referencia nao foi inspecionada visualmente')
print('MANIFESTO_VALIDO; isto nao aprova fidelidade estetica. Resultado visual permanece RASCUNHO ate revisao de pixels.')
