#!/usr/bin/env python3
# Preflight de comprovantes existentes. Somente leitura; nao cria QA nem autorizacao.
import argparse,base64,json,sys
from validar_pacote_publicacao import validate_package

def evaluate(payload):
    job = dict(payload)
    job["status"] = "aprovado"
    # Isso satisfaz somente a checagem de formato do validador;
    # nao significa que o usuario aprovou a postagem.
    job["approved_by"] = "PREFLIGHT_NAO_AUTORIZADO"
    errors = validate_package(job)
    return {
      "job_id":job.get("id"),"qa_concluido":not errors,
      "falhas":errors,
      "publicacao_autorizada":False,
      "opcoes":["Publicar agora","Agendar","Refinar","Refazer","Cancelar"] if not errors else ["Corrigir verificacoes","Refinar","Refazer","Cancelar"],
      "precisa_confirmacao_usuario":True,
      "prova_visual_humana": "conferir PNGs reais; nunca criar recibos sem auditoria"
    }
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--payload",required=True)
    args=parser.parse_args()
    job=json.loads(base64.b64decode(args.payload,validate=True).decode("utf-8"))
    print(json.dumps(evaluate(job),ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as e:
      print(json.dumps({"qa_concluido":False,"falhas":["FALHA_NO_VALIDADOR: "+str(e)[:180]],"publicacao_autorizada":False},ensure_ascii=False))
      sys.exit(2)
