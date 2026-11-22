# PROTOCOLO DE ENTRADA DO AGENTE, Instagram / OpenCode Alfa

Este é o procedimento padrão assim que um agente abre ESTE projeto. Ele vale para Mistral, Qwen, GLM ou qualquer outro modelo, sem exigir invocação manual de skills. A instrução vale para esta pasta e não modifica outros projetos.

## 1. Na entrada
1. Identifique a raiz I:/Projetos/Instagram-RobsonAlencar, leia AGENTS.md e esta página. Não recomece projetos nem faça varreduras amplas em históricos/bancos.
2. Conheça a estrutura: 01-conteudo (peças), 02-scripts (execução), 03-agendamentos (publicador), 04-skills (habilidades), .opencode/skills (skills específicas), 06-referencias e graphify-out (mapa consultável).
3. Não carregue todas as skills no contexto. Escolha apenas as pertinentes ao pedido. Para qualquer pedido novo de criacao, adaptacao ou edicao de carrossel/video, CONSULTE primeiro o mapa graphify-out/graph.json por uma busca direcionada, para identificar scripts, referencias e versoes existentes; nao reconstrua nem leia o mapa inteiro em todas as tarefas. Se falhar, registre a falha concreta e consulte os arquivos correspondentes.
4. Verifique os arquivos existentes do tema pedido antes de criar uma versão nova. Preserve o histórico, imagens originais, personas, sessões e configurações.

## 2. Para cada novo pedido
1. Entenda o objetivo real. Distingua criar, adaptar uma referência, editar algo existente, corrigir defeitos, publicar, pesquisar ou agendar.
2. Execute python 02-scripts/diretor_instagram.py --sem-ia "PEDIDO DO USUARIO" e use tipo, skills e pendencias. Se o classificador não servir ao caso, confira a intenção real sem insistir em reclassificações repetidas.
3. Se houver mídia de referência, veja o arquivo de verdade, use .opencode/skills/visual-reference-adapter/SKILL.md, descreva a composição por cena/slide e preserve a linguagem visual. Nunca trocar referência por um template genérico.
4. Seleção: carrossel -> 04-skills/carrossel/SKILL.md, 04-skills/ig-carousel/SKILL.md e references/qa-obrigatorio.md; vídeo -> ig-reel e instagram_estudio.py ou editor apropriado; motion -> reference-to-motion / choreograph / animation-performance somente conforme a necessidade; pesquisa -> ig-audit; publicar -> fluxo seguro de publicação. Impeccable, review-animations e avoid-ai-design revisam, mas não substituem direção artística.
5. Planeje internamente o mínimo necessário, comece a executar. Se o usuário já mandou fazer/corrigir, não peça autorização extra para criação/edição. Peça somente dados ausentes indispensáveis.

## 3. Produção e revisão
1. Uma frase/ideia do roteiro = uma representação visual específica, NÃO o mesmo emoji, mão, ilustração ou cartão com título trocado.
2. Carrossel 1080x1350; conteúdo essencial na zona x=80..1000, y=135..1215; Reels/Stories 1080x1920 com margens próprias.
3. Salve HTML editável, ativos e PNG/MP4 em pasta própria; não sobrescreva versões existentes sem backup.
4. Rode o exportador OFICIAL: node 04-skills/carrossel/scripts/exportar.mjs "CAMINHO_HTML" "PASTA_SAIDA". Não usar cópias antigas ou render-geral.cjs como substituto porque podem omitir validações ou usar 1080x1080.
5. Inspecione capa, slide do meio, CTA, português, contraste, imagem específica, dimensões e recortes. Rejeição no exportador significa trabalho ainda não concluído. Para vídeo, verificar codec, duração, áudio e cenas. Corrija os erros reais.
6. Ao mudar código, faça backup e testes. Para roteamento: python 02-scripts/testar-roteamento-20261111.py. Verifique sintaxe e serviços afetados. Nunca afirme corrigido sem prova.

## 4. Publicação
1. Pedido para CRIAR ou "pronto para postar" apenas gera arquivos. NÃO posta.
2. Ordem explícita "poste agora"/"publique" autoriza tentativa imediata sem pedir confirmação de novo. Use 02-scripts/postar-agora.py e o publicador seguro, verificando pasta, legenda, conta e duplicidade. Não use scripts antigos de publicação. [VALE SOMENTE SE O ARQUIVO BLOQUEIO-PUBLICACAO-ATIVO NAO EXISTIR; ver REGRA UNICA DE PUBLICACAO no topo]
3. Só declarar publicado após verificação do Instagram; em falha/resultado incerto, preservar evidência e NÃO tentar novamente no escuro.
4. Pedido de agendamento exige data e horário identificáveis; não converter "amanhã" em publicação imediata.

## 5. Finalização
Forneça caminho exato, arquivos produzidos, provas dos testes, o que falhou e o que falta. Não confunda "servidor HTTP 200" com produto final concluído.
Quando um trabalho estiver em andamento, retomar o estado real, não varrer milhões de caracteres do histórico. Não mudar de modelo, referência ou direção estética em silêncio.
