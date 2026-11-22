# MAPA PONTA A PONTA DO INSTAGRAM (ALFA)
Atualizado em 12/11/2026. Escopo EXCLUSIVO: I:/Projetos/Instagram-RobsonAlencar.

## Documentos
- Este mapa descreve o fluxo e os sistemas.
- CATALOGO-COMPLETO-176-SKILLS-INSTAGRAM-20261112.md tem as 176 skills, divididas por função, com cada caminho e estado.
- inventario-skills-atual.json é o índice estruturado das 176 skills.
- MAPA-OPERACIONAL.md e graphify-out/graph.json localizam arquivos e código, não autorizam o uso de imagens.

## Fluxo do começo ao fim
1. ENTRADA: OpenCode Instagram em http://127.0.0.1:4123, projeto I:/Projetos/Instagram-RobsonAlencar, agente padrão Build. Ler AGENTS.md, opencode.json, protocolo de entrada e regras.
2. ENTENDIMENTO: registrar o pedido literal, formatos, fotos, referências expressamente selecionadas e itens que NÃO podem mudar. Material encontrado no disco não é autorizado por padrão.
3. CLASSIFICAÇÃO: diretor_instagram.py --sem-ia classifica em capa/carrossel, Reel, Story, texto, pesquisa, edição ou publicação. Não trocar silenciosamente vídeo por imagem ou carrossel por Reel.
4. DESCOBERTA: consultar skills necessárias do catálogo e seu SKILL.md. Não carregar as 176 skills no contexto. Se preciso, consultar graphify e mapa de arquivos por busca pontual.
5. FIDELIDADE: para pedido igual à referência, abrir os pixels ou frames da referência real do pedido, produzir manifesto-fidelidade.json, preservar composição, fonte, cores, recorte, iluminação e alterar SOMENTE o que o usuário pediu.
6. EXECUÇÃO: Build usa ferramentas reais; imagem por composição, SDXL/ComfyUI quando necessário; vídeo pelo Editor/Pipeline adequado; texto por skills de copy. Preservar originais e criar saídas separadas.
7. QA TÉCNICO: validar dimensão, resolução, área segura, imagem carregada, áudio, duração, texto, codecs e o arquivo final.
8. QA VISUAL: comparar lado a lado com a referência; corrigir divergências. PNG válido não é prova de fidelidade. Marcar RASCUNHO enquanto não houver avaliação visual.
9. ENTREGA: informar arquivos reais, caminho, o que foi verificado e pendências. Nunca responder somente que vai fazer.
10. PUBLICAÇÃO: etapa distinta e bloqueada pelo arquivo de segurança existente. Mesmo com ordem de postar, exige liberação consciente do pacote exato e uso do publicador seguro, sem scripts alternativos.

## As 176 skills, agrupadas
| Grupo | Arquivos | Responsabilidade |
|---|---:|---|
| Instagram / operação editorial | 19 | Carrossel, Reels, Stories, copy, atendimento, planejamento |
| Marketing Instagram / coleções | 20 | Pauta, audiência, legendas, hashtags, hooks |
| OpenCode / mídia e inteligência | 21 | Motion, referência visual, animação, pesquisa e direção |
| Auxiliares de vídeo e auditoria | 5 | Edição, workflows e conferência |
| Design-ops | 9 | QA e entrega |
| Design-research | 14 | Pesquisa de público e testes |
| Design-systems | 11 | Componentes, design tokens e padrões |
| Designer-toolkit | 7 | Especificação e comunicação |
| Interaction-design | 22 | Movimento e interações |
| Prototyping-testing | 10 | Protótipos e testes |
| UI-design | 19 | Layout, tipografia, cor e hierarquia |
| UX-strategy | 12 | Estratégia e conteúdo |
| Visual-critique | 7 | Revisão da composição, tipografia, cor e marca |
TOTAL = 176 arquivos SKILL.md. Inclui coleções duplicadas; não equivale a 176 habilidades únicas nem a 176 habilidades executadas.
Somente 15 caminhos de skills de design estão explicitamente registrados em opencode.json; as demais existem em disco e devem ser selecionadas por tarefa.

## Caminhos e componentes do projeto
- 00-usuario: fotos e dados do usuário (uso NÃO automático).
- 00-regras: autorização, fidelidade, formato e bloqueios.
- 01-conteudo: originais autorizados, material de trabalho e saídas.
- 02-scripts: roteador, exportador, QA, integrações e publicador.
- 03-agendamentos/publicador: fila, perfil, revisão, processados, evidências e bloqueio.
- 04-skills: procedimentos editoriais e marketing.
- 05-agentes: definição local de agentes (não assumir que todos operam).
- 06-referencias: documentação, catálogo e índices, sem autorização implícita de uso criativo.
- .opencode/skills: técnicas locais para vídeo, motion, visual e pesquisa.
- .agents/skills: auxiliares de produção e auditoria.
- graphify-out: mapa de código, não catálogo de mídias autorizadas.
- Quarentena externa: conteúdo reprovado, proibido recuperar automaticamente.

## Quando e como cada família trabalha
- CAPA ESTÁTICA/CARROSSEL: carrossel + ig-carousel + visual-reference-adapter + crítica visual. Exigir imagem original acessível, manifesto, HTML/PNG, QA e revisão.
- REEL: ig-reel + reference-to-motion + choreograph + video-editing-workflow conforme pedido. Exigir MP4, áudio, duração e comparação temporal quando houver vídeo de referência.
- STORY: ig-story e copy, dimensão 1080x1920.
- LEGENDA: ig-caption, humanizer, hook, revisão bíblica quando aplicável.
- PESQUISA: instagram-last30days, ig-audit, ig-viral. Exigir fontes datadas.
- PERFIL E PLANEJAMENTO: ig-profile, ig-plan, coleções de marketing. Não impor marca não aprovada.
- COMENTÁRIOS E DMs: comentarios, ig-comment, ig-reply, ig-dm, para rascunhos; envio é ação diferente.
- EDIÇÃO: preservar mídia original e modificar somente o solicitado.
- REVISÃO: design-qa-checklist, critique-composition, critique-typography, critique-color, critique-brand-consistency, impeccable, avoid-ai-design.
- PUBLICAR: usar somente scripts seguros autorizados, depois de removido conscientemente o bloqueio de segurança. Nunca publicar por pedido de criação.

## Verificações reais em 12/11/2026
- OpenCode 4123: HTTP 200, agente Build padrão e regras locais reconhecidas.
- Ollama 11435: API de catálogo responde. Inferência não foi testada nesta auditoria.
- FreeToken 1918: gerenciador responde, backend_ready=false. Não declarar inferência pronta antes de gerar resposta.
- ComfyUI ALFA: responde em 192.168.100.2:8188; loopback 127.0.0.1:8188 não respondeu.
- Editor Automático API 8766: não respondeu. Ponte por HTTP indisponível.
- Scripts de vídeo no E: e I: existem, mas renderização completa não foi testada.
- Pasta 01-conteudo/reels-a-revisar não existe no instante verificado.
- BLOQUEIO-PUBLICACAO-ATIVO existe; não foi removido.
- Corrigido: roteador confundia capa estática com Reel. Quatro casos direcionados e seis regressões passaram.
- Fidelidade: sintaxe e quatro testes de rejeição passaram; ainda é preciso verificar novo trabalho com referência visual real.
- Inicialização automática do servidor 4123 foi testada via script, mas sem reiniciar todo o Windows.

## Principais scripts
- 02-scripts/diretor_instagram.py: classifica pedido.
- 04-skills/carrossel/scripts/exportar.mjs: gera slides, exige cenas e faz QA.
- 02-scripts/qa_carrossel.py: controla qualidade técnica.
- 02-scripts/validar_fidelidade.py: bloqueia referência/manifesto não autorizado ou ausente.
- 02-scripts/comparar_referencia.py: cria comparação lado a lado e registro de rascunho.
- 02-scripts/instagram_estudio.py: ponte HTTP do vídeo (porta 8766 indisponível).
- 02-scripts/receber-video-editor.py: recebe e verifica MP4.
- 02-scripts/usar_video_referencia.py: prepara a referência de vídeo.
- 02-scripts/postar-agora.py, fila-publicacao.py e publicar-seguro.cjs: publicação protegida, NÃO executar enquanto houver bloqueio.

## Critérios de pronto
Só declarar EXECUTADO E VERIFICADO quando o pedido e fontes forem confirmados, as ferramentas realmente executarem, arquivo final existir/abrir, QA passar, comparação visual for feita para tarefas com referência e o caminho for apresentado. De outro modo registrar RASCUNHO ou BLOQUEADO com causa exata. Não publicar automaticamente.
