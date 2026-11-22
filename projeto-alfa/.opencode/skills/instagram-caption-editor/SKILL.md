---
name: instagram-caption-editor
description: Revisão obrigatória de legendas do Instagram com Humanizer, voz pastoral e validação técnica antes de publicar ou agendar.
---
# Legenda editorial obrigatória
1. Ler voice.md e o conteúdo exato da mídia autorizada para a tarefa atual.
2. Carregar e APLICAR 04-skills/humanizer/SKILL.md: detectar padrões artificiais, reescrever e conferir preservação de sentido. Proibido declarar que usou a skill apenas por citá-la.
3. Carregar 04-skills/ig-caption/SKILL.md e verificar gancho, contexto, um único convite quando cabível, primeiras linhas e hashtags pertinentes.
4. Não inventar referência bíblica, testemunho, citação, número ou promessa. Conferir texto bíblico com fonte confiável quando usado.
5. Gravar a versão FINAL no arquivo legenda.txt do pacote autorizado, em UTF-8. Nunca substituir mídia ou legenda aprovadas silenciosamente.
6. Executar: python 02-scripts/validar_legenda_editorial.py --legenda "CAMINHO_DO_TXT" --revisor "humanizer+ig-caption" --registrar
7. O validador faz verificações automáticas e registra o hash da legenda. O marcador de revisão confirma uma ação do agente, não comprova por si só qualidade textual: inspecionar o texto final.
8. Se alterar qualquer caractere da legenda após o registro, revisar e registrar novamente. Sem recibo válido, bloqueio de publicação.
9. Antes de publicar, confirmar conta, pacote exato, autorização de publicação e estado do bloqueio geral. Não remover bloqueios para contornar revisão.
