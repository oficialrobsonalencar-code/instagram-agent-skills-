# -*- coding: utf-8 -*-
"""Ultima trava, independente do agendador, antes de enviar ao Instagram."""
from pathlib import Path
import sys,json,re
ROOT=Path(r'I:\Projetos\Instagram-RobsonAlencar')
QUEUE=ROOT/'03-agendamentos'/'publicador'/'fila'
sys.path.insert(0,str(ROOT/'02-scripts'))
from autorizacao_por_pacote import permitted
from validar_pacote_publicacao import validate_package
def main():
    if len(sys.argv)!=2: raise ValueError('exige caminho unico de job')
    p=Path(sys.argv[1]).resolve(strict=True)
    if p.parent!=QUEUE.resolve() or p.suffix.lower()!='.running':
        raise PermissionError('ORIGEM_NAO_E_FILA_ATOMICA')
    q=json.loads(p.read_text(encoding='utf-8-sig'))
    if q.get('id')!=p.stem or q.get('status')!='tentativa_iniciada' or not q.get('approved_by'):
        raise PermissionError('ESTADO_OU_ID_INVALIDO')
    if not re.fullmatch(r'[0-9a-f-]{36}',str(q['id'])):
        raise PermissionError('ID_INVALIDO')
    approved_job=dict(q)
    approved_job['status']='aprovado'
    errors=validate_package(approved_job)
    if errors: raise PermissionError('QA_REPROVADO: '+','.join(errors))
    if not permitted(approved_job): raise PermissionError('LIBERACAO_INDIVIDUAL_AUSENTE_INVALIDA_OU_EXPIRADA')
    print('PERMITIDO_EXATAMENTE_UMA_TENTATIVA',q['id'])
if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('BLOQUEADO',type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(4)
