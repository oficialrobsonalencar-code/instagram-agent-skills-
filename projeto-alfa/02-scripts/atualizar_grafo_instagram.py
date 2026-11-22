# -*- coding: utf-8 -*-
"""Atualiza grafo Instagram a partir dos scripts existentes. Sem analisar tokens, imagens ou navegador."""
from pathlib import Path
import subprocess,json,hashlib,shutil,os,sys,datetime
ROOT=Path(r'I:\Projetos\Instagram-RobsonAlencar')
SNAP=ROOT/'graphify-code-snapshot'
TARGET=ROOT/'graphify-out'
def sha(f):return hashlib.sha256(f.read_bytes()).digest()
def main():
 relative=[]
 scripts=ROOT/'02-scripts'
 for p in scripts.iterdir():
  if p.is_file() and p.suffix.lower() in ('.py','.js','.cjs','.mjs'):
   # Exclude scripts that only hold login/account manipulations from LLM indexing.
   if any(k in p.name.lower() for k in ('dm-test','entrar-instagram','inspecionar-share','debug-create','apagar-duplicado')):continue
   relative.append(p.relative_to(ROOT))
 for spec in ('04-skills/ig-reel','04-skills/ig-viral','04-skills/ig-caption','04-skills/carrossel/scripts'):
  base=ROOT/spec
  if base.is_dir():
   for p in base.iterdir():
    if p.is_file() and p.suffix.lower() in ('.py','.js','.cjs','.mjs'):relative.append(p.relative_to(ROOT))
 SNAP.mkdir(exist_ok=True)
 keep={p.as_posix() for p in relative}
 changes=0
 for r in relative:
  src=ROOT/r;dst=SNAP/r;dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists() or sha(src)!=sha(dst):shutil.copy2(src,dst);changes+=1
 for f in SNAP.rglob('*'):
  if not f.is_file() or 'graphify-out' in f.parts:continue
  rel=f.relative_to(SNAP).as_posix()
  if f.suffix.lower() in ('.py','.js','.cjs','.mjs') and rel not in keep:f.unlink()
 command=[shutil.which('graphify') or str(Path.home()/'.local'/'bin'/'graphify.exe'),'extract',str(SNAP),'--code-only','--no-cluster','--max-workers','2']
 result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
 print('SCAN_FILES',len(relative),'CHANGED',changes,'RC',result.returncode,flush=True)
 print(result.stdout[-1400:],flush=True)
 if result.returncode:raise RuntimeError(result.stderr[-1000:])
 src=SNAP/'graphify-out'/'graph.json'
 data=json.loads(src.read_text(encoding='utf-8'))
 nodes=data.get('nodes',[]);edges=data.get('edges',data.get('links',[]))
 if len(nodes)<10 or not isinstance(edges,list):raise ValueError('Grafo insuficiente')
 TARGET.mkdir(exist_ok=True)
 tmp=TARGET/'graph.json.tmp'
 shutil.copy2(src,tmp);os.replace(tmp,TARGET/'graph.json')
 info={'files':len(relative),'nodes':len(nodes),'edges':len(edges),'date':datetime.datetime.now().astimezone().isoformat(),
       'content_scanned':False,'login_automation_excluded':True,'source':str(SNAP)}
 (TARGET/'atualizacao.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
 print('GRAPH_READY',json.dumps(info,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERROR',str(e),file=sys.stderr);sys.exit(1)
