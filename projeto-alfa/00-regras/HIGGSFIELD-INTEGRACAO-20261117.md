# Ponte Higgsfield Open Source com Editor E - 17/11/2026
## Arquitetura
I:/Projetos/Instagram-RobsonAlencar/02-scripts/higgsfield_editor.py -> E:/EDITOR AUTOMATICO/VIDEO/integracoes/higgsfield_open_source/higgsfield_bridge.py
A ponte compartilhada evita instalar renderizadores duplicados e conserva a lógica do Editor e os projetos existentes.
## Testes realizados
- python 02-scripts/instagram_estudio.py verificar -> Editor Automatico ok, port 8766, review folder ok, bridge ready, ffprobe ok.
- python 02-scripts/higgsfield_editor.py plan --intent adaptar --description "Adaptar video referencia preservando estilo" -> rota de adaptação existente, ComfyUI conectado, Estúdio conectado, sem geração ou publicação.
- python 02-scripts/higgsfield_editor.py validate --file "E:/EDITOR AUTOMATICO/VIDEO/out/wan2-2-teste-93b44b5740.mp4" -> MP4 existente válido; sem áudio, 128x224, 0.562s (não é entrega de Reel).
- Skill: .opencode/skills/higgsfield-editor-bridge/SKILL.md.
- AGENTS.md atualizado sem apagar as regras anteriores. Backup anterior: C:/Users/Public/Higgsfield-Integration-Backups-20261117/Instagram.AGENTS.before-higgsfield.md.
## Regras preservadas
- BLOQUEIO-PUBLICACAO-ATIVO permanece integralmente em vigor.
- Referências visuais de trabalhos passados não são autorização de reutilização.
- Não criar carrossel nem alterar identidade visual por ter recebido uma referência.
- Criação de vídeo usa a API atual de instagram_estudio.py, e importação usa receber-video-editor.py.
- A nova ponte só faz diagnóstico, planejamento e validação. Não publica, não altera filas e não sobe servidor.
## Limites
Paint a Plate precisa de modelos e recursos que não estão presentes; somente os recursos compatíveis do Editor existente estão operacionais. ComfyUI conectado não significa que os modelos Higgsfield estejam instalados.
