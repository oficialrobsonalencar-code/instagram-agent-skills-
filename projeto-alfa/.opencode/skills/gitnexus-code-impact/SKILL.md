---
name: gitnexus-code-impact
description: >-
  Consultar dependências entre funções e arquivos, rastrear execução e avaliar
  impactos de alterações de CÓDIGO do Instagram Robson Alencar. Não se aplica
  a imagens, tipografia, OCR, medição de pixels, geometria ou publicação.
---

# GitNexus: análise de código, complementar ao Graphify

## Escopo e acionamento
- Base autorizada: `I:/Projetos/Instagram-RobsonAlencar`.
- Usar apenas em tarefas de programação, depuração, chamadas entre funções ou
  análise de impactos de uma edição de código.
- Preservar Graphify para mapeamento existente e consulta geral do projeto.
- Não duplicar consultas sem necessidade; escolha uma fonte para cada objetivo.
- Não usar GitNexus em tarefas exclusivamente visuais nem como memória pessoal.

## Ferramentas MCP
- `gitnexus_query`: encontrar símbolos e fluxos relevantes.
- `gitnexus_context`: analisar chamadores e dependências de um símbolo.
- `gitnexus_impact`: verificar impacto antes de editar uma função compartilhada.
- `gitnexus_trace`: rastrear dependências entre símbolos quando aplicável.
- Limitar o contexto devolvido pelo MCP a cerca de 1600 tokens, usando
  `maxTokens` quando a ferramenta oferecer esse parâmetro.
- Conferir os arquivos reais, as linhas e os testes antes de fazer afirmações.

## Não interferir no sistema visual
- OCR, medição de letras, bounding boxes, pixels, paletas, tipografia,
  margens, alinhamentos, geometria e regressão de imagens continuam nas
  skills `vision-qa-local`, `visual-regression-testing`, nos scripts
  aprovados, no `quality-director.js` e nas regras do `AGENTS.md`.
- Não editar, substituir ou desligar essas ferramentas.
- Não gerar arte nem publicar postagens com base no grafo de código.
- Respeitar aprovações, bloqueios e identidade visual existentes.

## Segurança
- Não executar `gitnexus setup`, pois isso pode criar hooks que se
  sobrepõem aos plugins Graphify e de qualidade.
- Para manutenção manual do índice, usar apenas `analyze --index-only`,
  após verificar que não conflita com uma tarefa ativa.
- Não executar `rename` nem mutações automáticas sem ordem expressa.
- Índice desatualizado não é evidência do estado atual: verificar antes.
- Nunca iniciar modelos de GPU, embeddings ou tarefas permanentes só para
  consultar dependências.
