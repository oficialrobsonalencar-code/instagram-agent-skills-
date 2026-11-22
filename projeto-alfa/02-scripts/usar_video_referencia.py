# -*- coding: utf-8 -*-
"""Entrada única do projeto de Reprodução I para vídeo de referência.
Análise física no E e plano semântico no Qwen. Não renderiza/publica.
"""
from pathlib import Path
import argparse,subprocess,sys,uuid
ED=Path(r'E:\EDITOR AUTOMATICO\VIDEO')
PROJECT=Path(r'I:\Projetos\Instagram-RobsonAlencar\01-conteudo\referencias-video')
def run(cmd):
 subprocess.run(cmd,check=True,timeout=240)
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--referencia',required=True)
 x=p.add_mutually_exclusive_group(required=True)
 x.add_argument('--roteiro')
 x.add_argument('--frases',nargs='+')
 p.add_argument('--saida')
 a=p.parse_args()
 if not Path(a.referencia).is_file():raise FileNotFoundError(a.referencia)
 target=Path(a.saida) if a.saida else PROJECT/'saidas-referencia'/uuid.uuid4().hex[:10]
 target.mkdir(parents=True,exist_ok=True)
 cmd=[sys.executable,str(ED/'analisar_video_referencia.py'),'--referencia',a.referencia,'--saida',str(target)]
 run(cmd)
 run([sys.executable,str(ED/"ver_video_referencia_ia.py"),"--analise",str(target/"analise-referencia.json")])
 plan=[sys.executable,str(ED/'planejar_adaptacao_video.py'),'--analise',str(target/'analise-referencia.json'),'--saida',str(target/'plano-cenas.json')]
 plan.extend(['--roteiro',a.roteiro] if a.roteiro else ['--frases',*a.frases])
 run(plan)
 print('REFERENCIA_ESTUDADA_PLANO_PRONTO',target,flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERRO',str(e),file=sys.stderr);sys.exit(1)
