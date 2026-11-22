# -*- coding: utf-8 -*-
"""Cliente seguro do Estudio Automatico no projeto Instagram.
Fluxo: entender -> pedir (opcional) -> acompanhar -> importar para revisão.
NÃO publica, NÃO agenda, NÃO manipula credenciais.
"""
import argparse,json,urllib.request,urllib.error,sys,re,subprocess,pathlib
from diretor_instagram import plan as ig_director
EDITOR_URL='http://127.0.0.1:8766'
IG=pathlib.Path(r'I:\Projetos\Instagram-RobsonAlencar')
def request(path,payload=None):
 data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode('utf-8')
 headers={'Content-Type':'application/json'} if data else {}
 req=urllib.request.Request(EDITOR_URL+path,data=data,headers=headers)
 try:
  with urllib.request.urlopen(req,timeout=12) as res:return json.loads(res.read().decode('utf-8'))
 except urllib.error.HTTPError as exc:
  raise RuntimeError(f'Editor HTTP {exc.code}: {exc.read().decode("utf-8","replace")[:450]}') from exc
def main():
 p=argparse.ArgumentParser(description='Orquestrar videos do Instagram com IA do Estúdio E; sem publicar')
 sub=p.add_subparsers(dest='mode',required=True)
 plan=sub.add_parser('planejar');plan.add_argument('pedido')
 create=sub.add_parser('criar');create.add_argument('pedido');create.add_argument('--segundos',type=int,default=18)
 status=sub.add_parser('estado');status.add_argument('job')
 take=sub.add_parser('receber');take.add_argument('job');take.add_argument('--titulo',default='reel')
 sub.add_parser('verificar')
 args=p.parse_args()
 if args.mode=='verificar':
  print(json.dumps(request('/api/health'),ensure_ascii=False))
  subprocess.run([sys.executable,str(IG/'02-scripts'/'receber-video-editor.py'),'--check'],check=True)
 elif args.mode in ('planejar','criar'):
  local_plan=ig_director(args.pedido,use_model=True)
  print('DIRETOR_INSTAGRAM',json.dumps(local_plan,ensure_ascii=False),flush=True)
  if local_plan['tipo']!='reel' or local_plan['pendencias']:
   print('FLUXO_NAO_E_REEL_OU_PENDENTE; acione as skills indicadas e nao envie ao gerador de video.',flush=True)
   return
  interpretation=request('/api/interpret',{'prompt':args.pedido})
  print('INTERPRETACAO',json.dumps(interpretation,ensure_ascii=False),flush=True)
  if args.mode=='planejar':return
  if not interpretation.get('ready'):
   print('PENDENTE_DE_ESCLARECIMENTO; nenhum vídeo foi iniciado',flush=True)
   return
  if not 8<=args.segundos<=40:raise ValueError('Duração permitida para o Estúdio: 8 a 40 segundos')
  if interpretation.get('intent') not in ('video_cartoon','personagem_falando'):
   print('MOTOR_NAO_INTEGRADO; nenhuma tarefa foi enviada',flush=True);return
  result=request('/api/jobs',{'prompt':args.pedido,'mode':'producao','seconds':args.segundos})
  print('PRODUCAO_SOLICITADA',result['id'],'CONSULTE: python instagram_estudio.py estado '+result['id'])
 elif args.mode=='estado':
  if not re.fullmatch(r'[0-9a-f]{12}',args.job):raise ValueError('Job inválido')
  print(json.dumps(request('/api/jobs/'+args.job),ensure_ascii=False,indent=2))
 elif args.mode=='receber':
  subprocess.run([sys.executable,str(IG/'02-scripts'/'receber-video-editor.py'),'--job',args.job,'--titulo',args.titulo],check=True)
if __name__=='__main__':
 try:main()
 except Exception as ex:print('ERRO',str(ex),file=sys.stderr);sys.exit(1)
