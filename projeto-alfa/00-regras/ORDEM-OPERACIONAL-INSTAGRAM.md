# Fluxo oficial do Instagram

Aplique esta ordem no Modo Deus e nos executores do projeto. O inventario de skills informa disponibilidade. A tabela define quando cada uma entra. Leia as skills indicadas para a etapa em curso. Respeite o formato, a identidade e o destino do pedido atual.

| Ordem | Etapa | Skills e fontes | Evidencia para avancar |
|---|---|---|---|
| 1 | Identificar a tarefa | instagram-processo-verificado e instagram-director | Pedido classificado como mapear, criar, revisar, consultar, agendar ou publicar. Pasta exata, formato e referencia atual identificados. |
| 2 | Consultar o que ja existe | instagram_publicador em consultar_pacote para carrossel existente | Estado atual dos PNGs, legenda, recibo e revisao visual. Corrija somente o item reprovado. Se editoriais estiver vazio, mantenha legenda e recibo. |
| 3 | Definir a direcao de arte | brand-intake e visual-reference-adapter quando houver referencia do usuario. Use layout-grid, typography-scale, visual-hierarchy e color-system conforme o trabalho. | Referencia real conferida, grade, hierarquia, fontes, margens e aplicacao de marca registradas no briefing. Use 07-identidade-visual/padrao-oficial e o mapa da seta e assinatura para carrosseis. |
| 4 | Produzir no formato pedido | ig-carousel e carrossel para carrossel. ig-reel e reel-export para Reel. ig-story para Story. instagram-destaques e ig-profile para destaques ou perfil. | Fonte ou projeto editavel na pasta autorizada. Para carrossel, preserve a arte e a pasta em andamento. Render final em PNG, 1080 x 1350. |
| 5 | Revisar texto e legenda | revisao-textual, humanizer e ig-caption | Texto e referencias conferidos. legenda.txt e recibo do validador ligados ao texto atual. Rode QA textual antes do exportador oficial. |
| 6 | Renderizar e revisar a arte | carrossel, vision-qa-local, critique-typography, critique-composition, critique-brand-consistency e design-qa-checklist | Arquivos finais abertos e conferidos. Teste cortes, contraste, fontes, seta, assinatura e recorte de grade. Diferencie QA tecnico de aprovacao visual. Vincule o comprovante ao pacote e job corretos pelo fluxo oficial. |
| 7 | Apresentar e executar a decisao | instagram_publicador em revisar e decidir, com a ferramenta nativa question entre as duas chamadas | Apresente PNGs, legenda, conta e horario quando aplicavel. Execute a acao exata autorizada por esse fluxo. |
| 8 | Confirmar a entrega | instagram_publicador em consultar_agendamentos ou comprovante do Instagram | Agendado exige tarefa Windows e NextRunTime corretos. Publicado exige comprovante real. Entrega de arte exige arquivos finais e legenda. |

## Rotas curtas

- Mapear ou auditar: leia AGENTS.md, esta ordem e o catalogo 06-referencias/SKILLS-ATIVAS-OPENCODE.json. Cruze o nome com o caminho e a etapa. Informe conflitos e skills que nao carregaram. O grafo Graphify serve para localizar codigo.
- Revisar ou retomar: passos 1 e 2, depois volte ao primeiro item que estiver pendente. A retomada em outra sessao segue o comando no AGENTS.md.
- Criar: passos 1, 3, 4, 5 e 6. Entregue a previa e o material pedido. Siga a etapa 7 somente com pedido explicito de publicar ou agendar.
- Agendar ou publicar um trabalho existente: passos 1 e 2, corrija as pendencias comprovadas e siga 7 e 8. Use legenda.txt como nome de arquivo. Encaminhe a revisao visual a executor-visual e, com evidencia disponivel, a auditor-deus quando for preciso. Nunca fabrique aprovacao ou comprovante.
- Planejar ou reaproveitar conteudo: ig-plan, ig-viral e ig-repurpose conforme o pedido. Para legenda avulsa, use humanizer e ig-caption. Para auditoria de perfil, ig-audit e ig-profile.
- Ao receber erro de ferramenta, leia o nome e o resultado da etapa exata. Use uma consulta suportada ou a alternativa somente leitura do AGENTS.md. Depois de uma tentativa fundamentada de recuperacao, informe o impedimento especifico com evidencia.

Referencia operacional unica para ordem das etapas: este arquivo. AGENTS.md define escopo e protecoes. Mapas anteriores servem para localizar materiais e regras especificas.

## Decisao de publicacao no OpenCode

1. Consulte o pacote. Se retornar JA_PUBLICADO, apresente o comprovante e encerre. Em consulta de status, encerre depois de informar o resultado.
2. Para envio solicitado, com QA aprovado, use instagram_publicador com etapa revisar uma vez. Em publicacao imediata omita quando em todas as chamadas. Para agendamento use o mesmo horario futuro com fuso nas duas chamadas.
3. Exiba as imagens e a legenda integral retornada. Se a mensagem atual do usuario JA ordena de maneira inequivoca "publique agora" ou "agende" com horario futuro completo, NAO repita uma pergunta: a decisao sera confirmada pelo verificador contra a mensagem real da sessao. Se o usuario ainda nao escolheu uma acao, use a ferramenta question com {"questions":[pergunta_question]}, preserve job_id e aguarde uma resposta real. Nunca inferir horario ambiguo nem falsificar confirmacao.
4. Na mesma sessao, chame instagram_publicador com etapa decidir, mesma pasta, legenda e horario. Ordem direta explicita e inequívoca: use publicar ou agendar conforme ordenado. Se a escolha vier da ferramenta question, mapeie Publicar agora para publicar e Agendar para agendar. Para as demais escolhas use corrigir, refinar, refazer, rascunho ou cancelar. O servidor verificara a proveniencia e recusara acao divergente.
5. Se uma escolha ja foi registrada, use a revisao existente. Em RESPOSTA_NAO_ENCONTRADA, confira se a pergunta foi concluida e pertence ao pacote. Se ja foi respondida e o erro persistir, informe a divergencia exata e encerre. Nao repita decidir, nao renove a revisao, nao use etapa publicar e nao acrescente parametros.
6. Em resultado incerto consulte o recibo antes de qualquer nova tentativa. Informe publicado apenas com confirmacao.

## Retomada apos revisao expirada
- Se decidir retornar REVISAO_EXPIRADA ou SEM_REVISAO_PENDENTE, sua proxima ferramenta e instagram_publicador em consultar_pacote na mesma pasta. Nao use glob para procurar o pacote ja conhecido. Se houver pendencia visual, confira o comprovante em out/aprovacao-visual.json e trate essa etapa. Se o QA passar, chame revisar e obtenha a nova decisao no fluxo. No caso de urgencia ou horario relativo ambiguo, confirme dia e hora antes de criar algo.
