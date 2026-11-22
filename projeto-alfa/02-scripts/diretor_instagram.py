# -*- coding: utf-8 -*-
"""Diretor de conteúdo: interpreta pedido e encaminha ao workflow já existente.
Não executa postagens. Detecta intenção explícita de postar; Qwen opcional.
"""
import json,re,urllib.request,argparse,sys
TYPES=('reel','carrossel','story','legenda','pesquisa','edicao','publicacao')
SKILLS={
 'reel':['ig-reel','ig-viral','humanizer','ig-caption','instagram_estudio.py'],
 'carrossel':['ig-carousel','carrossel','ig-caption','humanizer'],
 'story':['ig-story','ig-caption'],
 'legenda':['ig-caption','humanizer'],
 'pesquisa':['ig-audit','ig-viral','ig-plan'],
 'edicao':['video-editing-workflow','instagram_estudio.py'],
 'publicacao':['postar-agora.py','fila-publicacao.py','publicar-seguro.cjs']
}
def rules(t):
 x=t.casefold()
 # Pedidos para criar conteudo nao significam publicacao.
 denial=bool(re.search(r"\b(?:sem|n[aã]o)\s+(?:publicar|postar|agendar|publique|poste)\b",x))
 explicit=bool(re.search(
    r"\b(?:poste|postem|publique|publiquem|publica|posta|compartilhe|compartilha)\b"
    r"|\b(?:pode|quero|preciso|manda|mande|vai|vamos)\s+(?:que\s+)?(?:postar|publicar|publique|poste|publica|posta)\b"
    r"|\b(?:postar|publicar)\s+(?:agora|ja|já|isso|esse|essa|este|esta|o|a)\b",x))
 scheduling=bool(re.search(r"\b(?:agende|agenda|agendar)\b",x))
 # 'pronto para postar' significa apenas producao.
 if explicit and not denial: return 'publicacao'
 if scheduling and not denial: return 'publicacao'
 if re.search(r"\b(carrossel|carroussel|slides?|sequ[eê]ncia de fotos)\b",x):return 'carrossel'
 # Arte estatica: capa de carrossel/post/card individual deve ir ao designer,
 # nao ao pipeline de video. Capa de reel ou video continua no fluxo de reel.
 if re.search(r"\b(capa|arte|card|post est[aá]tico|imagem est[aá]tica)\b",x):
  if re.search(r"\b(reels?|v[ií]deos?|motion|anima[cç][aã]o)\b",x):return 'reel'
  return 'carrossel'
 if re.search(r"\b(stories|story|enquete|caixinha)\b",x):return 'story'
 if re.search(r"\b(legenda|descri[cç][aã]o|hashtags?|caption)\b",x):return 'legenda'
 if re.search(r"\b(edit(ar|e)|cort(ar|e)|melhorar v[ií]deo|tirar pausas)\b",x):return 'edicao'
 if re.search(r"\b(analis[ae]|audit[ea]|auditar|pesquis[ae]|estat[ií]stic\w*|perfil|tend[eê]ncia\w*|melhores hor[aá]rios)\b",x):return 'pesquisa'
 return 'reel'
def model(t):
 instr=(
 'Classifique esta solicitação de trabalho Instagram em JSON com: tipo (um de reel, carrossel, story, legenda, pesquisa, edicao, publicacao), '
 'assunto (curto), precisa_referencia (booleano), notas (breve). Responda SOMENTE JSON. '
 'Publicação é apenas quando o usuário manda publicar/postar/agendar, nunca porque pediu um Reel para Instagram. '
 'Se houver vídeo narrado, use reel; se pedir lista desmembrada em slides, carrossel. Pedido: '+t[:1500])
 data=json.dumps({'model':'qwen3.5:latest','messages':[{'role':'user','content':instr}],
                  'think':False,'stream':False,'format':'json','options':{'num_predict':280,'temperature':0.1}},ensure_ascii=False).encode()
 req=urllib.request.Request('http://127.0.0.1:11435/api/chat',data=data,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=55) as r:j=json.load(r)
 return json.loads(j['message']['content'])
def plan(t,use_model=True):
 if len(t.strip())<4 or len(t)>2500:raise ValueError('Pedido muito curto ou muito longo')
 direct=rules(t)
 source='regras'
 x={}
 if use_model:
  try:
   x=model(t)
   if x.get('tipo') in TYPES:source='qwen3.5'
  except Exception as e:x={'warning':str(e)[:180]}
 kind= x.get('tipo') if source=='qwen3.5' else direct
 # safety guard - direct explicit publish intent cannot be overridden by LLM.
 if direct=='publicacao':kind='publicacao'
 # clear explicit requests should not be overwritten by classifier.
 if direct in ('carrossel','story','legenda','edicao','pesquisa','publicacao'):kind=direct
 # Pedido composto: pesquisar tendencias E produzir carrossel precisa das duas etapas.
 research_requested=bool(re.search(r'\b(?:pesquis\w*|busc\w*|investig\w*|tend[eê]ncia\w*|viraliz\w*|atualidad\w*|not[ií]cia\w*)\b',t.casefold()))
 selected_skills=list(SKILLS[kind])
 if research_requested and kind in ('carrossel','reel','story'):
  selected_skills=['ig-audit','ig-viral']+[s for s in selected_skills if s not in ('ig-audit','ig-viral')]
 needs=[]
 if kind=='publicacao' and re.search(r'\b(?:agend(?:e|ar)|agenda)\b',t.casefold()) and not re.search(r'\b(?:agora|já|ja|hoje)\b',t.casefold()):
  needs.append('Verificar o horário solicitado para agendamento')
 # A ausência de pasta explícita não impede buscar o conteúdo pelo contexto atual.
 # A ordem explicita de postagem e a autorizacao, nao pedir segunda confirmacao.

 if kind=='edicao' and not re.search(r'[A-Z]:\\[^"\n]+\.(mp4|mov|webm|mkv)',t,re.I):
  needs.append('Qual é o arquivo de vídeo original?')
 if kind=='reel' and 'anim' in t.casefold() and not re.search(r'(?:acenar|andar|gestos|convidar|falar|pregar|mostrar)',t.casefold()):
  needs.append('Que ação o personagem deve fazer?')
 return {'tipo':kind,'assunto':str(x.get('assunto',t))[:180],'fonte':source,
         'skills':selected_skills,'pesquisa_web_previa':research_requested and kind in ('carrossel','reel','story','pesquisa'),
         'mapa_graphify':'graphify-out/graph.json' if kind in ('carrossel','reel','story','edicao') else None,
         'verificar_novidade':kind in ('carrossel','reel','story'),
         'formatos':{'reel':'1080x1920','carrossel':'1080x1350','story':'1080x1920','legenda':'texto','pesquisa':'relatório','edicao':'conforme mídia','publicacao':'publicar agora com autorizacao explicita'}[kind],
         'pendencias':needs,'execucao_disponivel':kind in ('reel','carrossel','story','legenda','edicao','publicacao') and not needs,
         'aprovacao_publicacao':kind=='publicacao' and direct=='publicacao','publicado':False,
         'observacao':('Usar postar-agora.py para ordem explicita, validar conta e midia, registrar resultado; nunca alegar PUBLICADO sem comprovante.' if kind=='publicacao' else 'Criar conteudo nao autoriza publicar.')}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('pedido');p.add_argument('--sem-ia',action='store_true')
 args=p.parse_args()
 try:print(json.dumps(plan(args.pedido,not args.sem_ia),ensure_ascii=False,indent=2))
 except Exception as exc:print('ERRO',str(exc),file=sys.stderr);sys.exit(1)
