# -*- coding: utf-8 -*-
"""Contrato verificavel da geometria publicada de seta e assinatura."""
import re, json, hashlib, sys
from pathlib import Path
from PIL import Image
root=Path(r'I:\Projetos\Instagram-RobsonAlencar')
base=root/'01-conteudo'/'rascunhos'/'ansiedade-21nov-revisao'
source=base/'revisto'
light=base/'claro'
rules={
 '.top-arrow': {'top':'177px','left':'calc(50% - 34px)','width':'68px','height':'68px','stroke-width':'1.7'},
 '.sig': {'top':'1090px','width':'100%','text-align':'center','white-space':'nowrap','line-height':'1'},
 '.sig .at': {'font':"italic 37px 'Playfair Display',Georgia,serif"},
 '.sig .handle': {'font':"800 36px 'Poppins',Arial,sans-serif",'letter-spacing':'-.045em'}
}
def css(text,selector):
 m=re.search(re.escape(selector)+r'\s*\{([^}]+)\}',text)
 if not m:return None
 return dict(pair.split(':',1) for pair in [v.strip() for v in m.group(1).split(';')] if ':' in pair)
proof=json.loads((source/'aprovacao-visual.json').read_text(encoding='utf-8-sig'))
issues=[]
for i in range(1,11):
 name=f'slide-{i:02d}'
 old=(source/(name+'.html')).read_text(encoding='utf-8')
 new=(light/(name+'.html')).read_text(encoding='utf-8')
 for sel,props in rules.items():
  ref,now=css(old,sel),css(new,sel)
  if ref is None or now is None:issues.append(f'{name}:{sel}:seletor_ausente');continue
  for key,required in props.items():
   if ref.get(key)!=required:issues.append(f'{name}:{sel}:{key}:referencia_publicada_diverge')
   if now.get(key)!=required:issues.append(f'{name}:{sel}:{key}:alterado_no_claro')
 for marker in ('<span class="at">@pastor</span>','<span class="handle">robsonalencar</span>'):
  if marker not in old or marker not in new:issues.append(f'{name}:assinatura_textual_diverge')
 svg=r'<svg class="top-arrow"[^>]*>.*?</svg>'
 if re.search(svg,old,re.S).group(0)!=re.search(svg,new,re.S).group(0):
  issues.append(f'{name}:svg_da_seta_foi_alterado')
 historic=source/(name+'.png')
 if hashlib.sha256(historic.read_bytes()).hexdigest()!=proof['images_sha256'].get(name+'.png'):
  issues.append(f'{name}:historico_modificado')
 img=Image.open(light/(name+'.png')).convert('RGB')
 if img.size!=(1080,1350):issues.append(f'{name}:dimensoes_incorretas')
 if min(img.getpixel((15,15)))<210:issues.append(f'{name}:fundo_nao_claro')
print(json.dumps({'slides_testados':10,'assinatura_e_seta_preservadas':not issues,'historico_protegido':not issues,'erros':issues},ensure_ascii=False,indent=2))
sys.exit(0 if not issues else 1)