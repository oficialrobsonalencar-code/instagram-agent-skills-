# AGENTES usados neste projeto (Instagram @pastorrobsonalencar)

## general (subagente usado para tarefas multi-passo)
- Usado para: escrever scripts de publicação (postar-carrossel, postar-agendado)
- Onde mora: sessão do OpenCode (task tool)

## explore
- Para: mapear estrutura de pastas/repositórios (Instagram-clii, skills)

## task-observer
- Ativo por padrão: registra observações que viram skills reutilizáveis

## Agentes de skills (via SKILL.md em 04-skills/)
- carrossel: cria carrossel IG completo (entrevista -> copy -> PNG 1080x1350/1080)
- humanizer: remove " cara de IA" do texto (blader/humanizer v3.1.0)
- comentarios: classifica comentários e monta resposta pública + DM
- legenda: escreve legenda com hook nos primeiros 125 caracteres
- perfil: audita perfil e reescreve bio
- ig-viral: analisa reels virais, classifica hook formulas, gera swipe file
- instagram-marketing: pacote ig-* (caption-writer, carousel-planner, hashtag-strategist, etc.)
- social-publisher: publicación via SocialClaw (precisa de API key paga — não usado)

## Observações
- claude-mem instalado (v15.9.0) no OpenCode: memória persistente em ~/.claude-mem, worker em http://127.0.0.1:37777
- Navegador usado para publicar: perfil do OpenCode em C:\Users\ROBSON ALENCAR\AppData\Local\OpenCode\BrowserProfile (sessão logada do Instagram)
