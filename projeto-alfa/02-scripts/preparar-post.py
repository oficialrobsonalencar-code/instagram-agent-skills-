#!/usr/bin/env python3
"""Cria um rascunho de postagem agendada. Nunca publica nem aprova automaticamente."""
import argparse,datetime,json,pathlib,re,uuid,sys
ROOT=pathlib.Path(r'I:\Projetos\Instagram-RobsonAlencar')
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--pasta',required=True,help='nome da pasta em 01-conteudo com slides dentro de out')
 p.add_argument('--quando',required=True,help='data ISO com fuso. Ex: 2026-11-11T08:00:00-03:00')
 p.add_argument('--conta',required=True,help='identificador exato da conta Instagram')
 a=p.parse_args()
 base=(ROOT/'01-conteudo'/a.pasta).resolve()
 if (ROOT/'01-conteudo').resolve() not in base.parents:raise ValueError('Pasta fora do projeto')
 if not base.is_dir():raise ValueError('Pasta nao encontrada')
 files=sorted((base/'out').glob('slide-*.png'))
 if not 1<=len(files)<=10:raise ValueError('Esperado entre 1 e 10 slides em out')
 candidates=[base/'legenda.txt',base/'legenda-8h.txt',base/'legenda-ceia.txt']
 c=next((x for x in candidates if x.is_file()),None)
 if not c:raise ValueError('Legenda nao localizada')
 dt=datetime.datetime.fromisoformat(a.quando)
 if dt.tzinfo is None:raise ValueError('Horario precisa de fuso -03:00')
 if dt<=datetime.datetime.now(datetime.timezone.utc):raise ValueError('Horario ja passou')
 account=a.conta.strip().removeprefix('@')
 if not re.fullmatch(r'[A-Za-z0-9._]{2,30}',account):raise ValueError('Conta Instagram invalida')
 q={'id':str(uuid.uuid4()),'status':'rascunho','approved_by':'','account':account,'scheduled_at':dt.isoformat(),'files':[str(f) for f in files],'caption':c.read_text(encoding='utf-8-sig').strip()}
 folder=ROOT/'03-agendamentos'/'publicador'/'fila';folder.mkdir(parents=True,exist_ok=True)
 out=folder/(q['id']+'.json')
 out.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
 print('RASCUNHO_CRIADO',out,'SLIDES',len(files),'CONTA',account,'HORARIO',dt.isoformat())
 print('Requer aprovacao explicita: altere status para aprovado e approved_by para um nome, apos revisar todo o material.')
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERRO',str(e),file=sys.stderr);sys.exit(1)
