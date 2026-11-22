---

name: carrossel
description: Cria um carrossel de Instagram completo, da capa ao último slide, pronto para postar em PNG 1080x1350. Use quando a pessoa pedir carrossel, post com vários slides, conteúdo para salvar, transformar uma ideia, texto, aula ou tema em carrossel, ou melhorar a capa e a copy de um carrossel que já existe. Faz uma entrevista curta, escolhe o formato, escreve a copy slide a slide e exporta as imagens com Playwright.
license: MIT
---


## ASSINATURA UNIVERSAL OBRIGATÓRIA

A assinatura de TODOS os slides em TODOS os novos carrosséis é um único componente idêntico ao da penúltima imagem aprovada. Altura top=1089px; @pastor em Playfair Display italic 400 42px, e robsonalencar Poppins 800 38px; espaçamentos -0.02em e -0.05em, centro e baseline invariáveis. A seta oficial tem top=300px e 86x86px. Somente cores podem variar para contraste; não mover, alterar o desenho ou recompor o texto.
Consultar 00-regras/PADRAO-OFICIAL-SETA-ASSINATURA-20261121.md e 07-identidade-visual/padrao-oficial/mapeamento.json.
Executar python 02-scripts/validar_padrao_carrossel.py --pasta SAIDA --expected N em TODOS os novos carrosséis. O exportador deve reprovar arte divergente. Publicação exige ordem própria.

## LEGENDA GLOBAL OBRIGATORIA
Antes de exportar TODO novo carrossel, criar legenda.txt na pasta do HTML e revisar com humanizer + ig-caption. Consultar 00-regras/LEGENDA-OBRIGATORIA-CARROSSEL.md. Gancho de 125 caracteres, 1 CTA e ate 5 hashtags. Exportador aborta se faltar legenda ou linter reprovar. O recibo editorial adicional e requerido antes da publicacao, nunca inventar. Entregar apenas como RASCUNHO quando nao houver aprovacao visual.
## PORTAO EXECUTAVEL PARA COPIA FIEL
Para reproduzir uma imagem autorizada no pedido atual: criar manifesto-fidelidade.json e validar com python 02-scripts/validar_fidelidade.py --manifest CAMINHO. Exportar com --manifest CAMINHO. Se a referencia faltar ou nao houver analise real da imagem, bloquear. A exportacao e RASCUNHO ate revisao visual com comparacao lado a lado; nao declarar fidelidade apenas por dimensoes/margens. Apos gerar PNG, executar python 02-scripts/comparar_referencia.py --manifest CAMINHO.json --resultado SAIDA.png --saida PASTA_REVISAO; gera comparacao-lado-a-lado.jpg e revisao-fidelidade.json com estado RASCUNHO, nunca aprovacao estetica automatica.

# Carrossel de Instagram: execução e entrega

## Acionamento
Aplicar quando o pedido mencionar carrossel, slides Instagram, copy, capa, referências visuais, edição ou exportação de posts. Usar o projeto existente e suas imagens, sem recomeçar do zero.

## Fluxo obrigatório
1. Consultar o mapa Graphify existente (graphify-out/graph.json) por consulta pontual; localizar trabalhos anteriores e as referencias relevantes. Comparar tema, copy e ativos com entregas anteriores para nao reapresentar conteudo ja pronto como inedito. Se o pedido incluir pesquisa de tendencias, usar ig-audit + ig-viral, fontes da web com data e URLs antes de escolher tema; nao alegar viralidade apenas com palpite. Ler o pedido e os arquivos/referências relevantes. Não repetir perguntas já respondidas. Se a pessoa ordenou produzir, executar diretamente, sem pedir nova aprovação da copy; solicitar confirmação apenas para decisões externas irreversíveis.
2. Identificar o formato (lista, história, passos, erros, antes/depois), elaborar 6 a 10 slides; capa forte, um ponto por slide, encerramento com um CTA. Se a pessoa enviou referência, reproduzir linguagem visual e composição, com conteúdo próprio.
3. Produzir copy, HTML e imagens no mesmo projeto, preservando arquivos originais. Para detalhes de textos, estilos, resolução e critérios, ler [fluxo completo](references/workflow-original.md).
4. Antes de criar a arte, ler [critérios obrigatórios de qualidade](references/qa-obrigatorio.md). O template HTML é somente estrutura; nunca replicar cards, emojis ou fundo genérico. Cada slide exige uma cena específica. Usar o [exportador Playwright](scripts/exportar.mjs) e corrigir falhas de área segura/repetição ANTES de entregar.
5. Ao final, informar pasta de saída, nomes dos PNGs, o que realmente foi criado e o que ainda falta. Se bloqueado, descrever o erro exato e próxima ação, sem afirmar sucesso não verificado.

## Regras de execução
- Sem arte genérica. Cada slide deve representar precisamente seu trecho da mensagem; manter uma linguagem visual consistente.
- Não inventar dados ou provas; não sobrescrever a versão existente sem backup.
- O comando de exportação, dentro da pasta de trabalho, é `node exportar.mjs carrossel.html out`. Os insumos vêm dos caminhos acima.
- Em jobs demorados, comunicar o progresso em frases objetivas. Nunca trocar de modelo, pasta, tema ou estilo silenciosamente.
- Não interpretar a pausa obrigatória do fluxo antigo como veto quando o usuário já solicitou execução.


## REVISAO PRIORITARIA 21/11/2026, MAIS RECENTE QUE O PADRAO ANTIGO
O usuario REPROVOU a seta muito perto do topo no carrossel escuro ja publicado.
Nova posicao para TODAS as artes futuras: top 300px, largura e altura 86px, centro horizontal.
A antiga posicao top 137px esta REPROVADA. A assinatura continua top 1089px, Playfair 42px e Poppins 38px.
O PNG historico da penultima imagem fica INTACTO para desenho e identidade da assinatura, mas NAO define mais a altura vertical da seta.
O validador deve conferir 300px em NOVOS slides e conferir 137px apenas no arquivo de referencia historica.
A seta de 300px fica dentro da area central de seguranca para recorte 1:1.
Nao alterar imagens ja publicadas no Instagram, nem republicar automaticamente.
A altura 300px foi definida em resposta ao pedido de baixar a seta; confirmar o visual pela previa renderizada.

## COMANDOS BASH SEGUROS PARA RENDERIZAR
Um Bash negado NAO significa que todo o Bash esteja indisponivel. A ferramenta bloqueia shell arbitrario, mas permite o exportador oficial no escopo do carrossel autorizado. Executar:
node 04-skills/carrossel/scripts/exportar.mjs 01-conteudo/carrossel-NOME/carrossel.html 01-conteudo/carrossel-NOME/out
Depois usar:
python -X utf8 02-scripts/validar_padrao_carrossel.py --pasta 01-conteudo/carrossel-NOME --expected N
Para listar, preferir read/glob; para checagem de Node/Python, node --version; python --version. Nao executar comandos de publicacao no Bash.
### Evitar loop de edit
Antes de editar, releia o arquivo atual e copie oldString literalmente. NUNCA editar trechos ausentes nem usar oldString igual a newString. Se a primeira tentativa falhar, NAO tentar correcao por suposicao: releia e use write integral somente quando necessario e autorizado. Apos toda escrita, execute QA textual NOVO; relatorio aprovado de HTML antigo nao serve.
