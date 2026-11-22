# CONFIGURAÇÃO DO PROJETO INSTAGRAM — 10/11/2026
Diretório oficial: I:\Projetos\Instagram-RobsonAlencar
Integração: E:\EDITOR AUTOMATICO\VIDEO

## Objetivo
Receber pedidos em linguagem natural e escolher entre Reel, carrossel, Story, legenda, pesquisa, edição e operação de publicação. A produção de conteúdo não autoriza publicar. Preservar trabalhos e autenticação existentes.

## Componentes instalados e testados
1. 02-scripts/diretor_instagram.py: classificação Qwen 3.5 local, retorno estruturado e regras de segurança. Testado com carrossel Salmo 46 (skill ig-carousel) e Reel de convite (Estúdio do E).
2. 02-scripts/instagram_estudio.py: cliente do Estúdio http://127.0.0.1:8766, comandos verificar, planejar, criar, estado e receber. Só envia vídeo quando o diretor determinar Reel e o Estúdio aceitar. O comando criar pode iniciar síntese da voz e render; a qualidade final de cada produção exige revisão.
3. 02-scripts/receber-video-editor.py: transfere somente MP4 do Editor oficial do E com 1080x1920, faixa de áudio e 1-180s. Rejeita demos e pedidos cujo MP4 divirja da duração solicitada. Evita cópias duplicadas por SHA256. Gera manifesto de revisão. NÃO publica ou agenda.
4. 02-scripts/fila-publicacao.py: verificação extra de identificador de conta antes de abrir o publicador; backup preservado.
5. .opencode/skills/instagram-director/SKILL.md: instruções de roteamento e validação. Historical Expert reaproveitado em .opencode/skills/historical-expert para conteúdos bíblicos e históricos.
6. AGENTS.md: instruções do agente para pedidos em linguagem natural, consulta ao Graphify, restrições de publicação, revisão e preservação dos originais.
7. .opencode/plugins/graphify.js e graphify-out/graph.json: plugin local e grafo do projeto. Análise de 32 arquivos selecionados, 182 nós, 327 relações no primeiro teste (331 relações após atualização incremental). Após novos scripts, o índice é atualizado por 02-scripts/atualizar_grafo_instagram.py.
8. Agendador do Windows: "Instagram Robson - Graphify", atualização de hora em hora com usuário logado; não agenda conteúdo Instagram.

## Evidências de teste
- Health Estúdio 8766: OK.
- Envio teste do editor para I: confirmado com MP4 + manifesto e hash. Como a mídia da demo tinha áudio antigo, ela foi separada em 01-conteudo/reels-a-revisar/testes-integracao e marcada NÃO PUBLICAR.
- Classificação 'Carrossel Salmo 46': escolheu ig-carousel + carrossel, SEM envio ao gerador de vídeo.
- Classificação 'Reel convite Crente Cartoon': escolheu ig-reel + Estúdio, SEM publicar.
- Tentativa de importar job de demonstração: bloqueada intencionalmente.
- Estado da fila na auditoria inicial: 0 em fila, 0 processados, 0 revisar; 1 registro anterior na pasta cancelados.
- As alterações anteriores do usuário no Git não foram descartadas nem sobrescritas.

## Operação rápida
cd "I:\Projetos\Instagram-RobsonAlencar"
python 02-scripts\diretor_instagram.py "Crie um Reel de convite para o culto"
python 02-scripts\instagram_estudio.py planejar "Crie um Reel de convite para o culto"
python 02-scripts\instagram_estudio.py criar "Crie um Reel de convite com o Crente Cartoon" --segundos 18
python 02-scripts\instagram_estudio.py estado ID_DO_JOB
python 02-scripts\instagram_estudio.py receber ID_DO_JOB --titulo "convite"
python 02-scripts\fila-publicacao.py check
python 02-scripts\atualizar_grafo_instagram.py
graphify query "Como criar um Reel e enviar à revisão?" --graph graphify-out/graph.json --budget 1200

## Limitações reais
- Conteúdo carrossel/Story é roteado para skills, mas não foi construída uma única API automática universal para renderizar qualquer carrossel.
- Produções completas de Reel com nova voz ainda dependem de Qwen e XTTS; a voz pode sair com duração diferente e a qualidade visual do cartoon precisa de revisão.
- O HyperFrames não está integrado como renderizador padrão do projeto Instagram; Remotion continua padrão no Editor E.
- Não houve login novo, publicação, envio de DM, agendamento de post nem alteração de credenciais. A conta exata deve ser conferida antes de qualquer publicação.
- O Graphify conhece código e relações, não substitui validação da saída nem pesquisa bíblica.
