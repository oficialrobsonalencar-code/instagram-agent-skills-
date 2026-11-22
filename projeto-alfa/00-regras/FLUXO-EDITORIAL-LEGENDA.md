# Fluxo editorial obrigatório de legendas Instagram
Aplica-se a carrosséis, Reels, Stories com legenda e posts agendados.
O roteador apenas sugerir humanizer não comprova que o agente executou essa skill.

Sequência: ler voice.md -> ler mídia autorizada -> executar 04-skills/humanizer/SKILL.md -> executar 04-skills/ig-caption/SKILL.md -> conferir sentido e referências bíblicas -> salvar legenda TXT final -> rodar 02-scripts/validar_legenda_editorial.py --legenda CAMINHO --registrar --revisor humanizer+ig-caption -> conferir JSON de recibo vinculado ao hash.

O publicador oficial agora bloqueia TXT sem recibo íntegro e correspondente. Registrar recibo somente após revisão real; nunca simular revisão. Quando houver aprovação do usuário, a legenda precisa ser exatamente a versão aprovada. Qualquer edição invalida o recibo.

Não publicar nem agendar durante auditorias. Preservar bloqueio geral, materiais aprovados, fila e registros históricos. Conflitos de horários e aprovação permanecem verificações separadas.
