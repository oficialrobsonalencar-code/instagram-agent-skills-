---
name: revisao-textual
description: Revisao obrigatoria de ortografia pt-BR, vocabulario biblico, consistencia semantica e taxonomia do projeto Instagram antes da renderizacao.
---
# Revisao textual, semantica e taxonomia

**OBRIGATORIA** para todo carrossel e legenda do Instagram-RobsonAlencar.

1. Leia taxonomia-editorial.json desta skill para identificar categorias, termos, referencias e alertas de contexto.
2. Use o dicionario local de portugues brasileiro do pyspellchecker (instalado em vendor/). Nao invente palavras nem aceite grafias inadequadas como mornidade.
3. Revise ortografia, acentuacao, concordancia e clareza de cada titulo, subtitulo e legenda. O dicionario NAO verifica sozinho gramatica completa.
4. Confira a SEMANTICA com o texto biblico: uma referencia nao autoriza inventar acontecimentos nem confundir aplicacao pastoral com sentido original. Delegue auditoria contextual ao agente auditor-deus quando necessario; nao declarar exegese comprovada apenas pelo script.
5. Rode a ferramenta oficial depois de escrever o HTML e a legenda:
   python -X utf8 02-scripts/qa_texto_taxonomia.py --html "01-conteudo/carrossel-NOME/carrossel.html" --legenda "01-conteudo/carrossel-NOME/legenda.txt" --saida "01-conteudo/carrossel-NOME/qa-texto-taxonomia.json"
6. Se houver falhas, CORRIJA OS ARQUIVOS-FONTE, nao apenas o relatorio, e execute novamente. O exportador usa o mesmo QA e bloqueia PNGs reprovados.
7. Depois de aprovado, renderize com 04-skills/carrossel/scripts/exportar.mjs, valide seta e assinatura e inspecione os PNGs reais. Publique apenas por ordem expressa.

O relatorio diferencia aprovado_ortografia de aprovado_consistencia_regras. Nenhum dos dois substitui revisao visual, editorial e teologica.
