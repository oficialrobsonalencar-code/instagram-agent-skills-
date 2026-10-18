# Instagram Agent Skills

Skills de agente para criação de conteúdo de Instagram — feitas para Claude Code, OpenCode, Codex e qualquer agente compatível com AgentSkills. Em português (pt-BR), com exportação real de arquivo (PNG, MP4, CSV — não só texto).

Cinco skills, um objetivo: transformar uma ideia em conteúdo pronto pra postar, de ponta a ponta.

## Skills

| Skill | O que faz |
|---|---|
| **carrossel** | Carrossel completo de Instagram, da capa ao último slide, exportado em PNG 1080x1350 via Playwright |
| **legenda** | Legenda com gancho na primeira linha (antes do "mais"), corpo fácil de escanear, um único CTA e hashtags de nicho — entrega 3 opções de gancho |
| **perfil** | Auditoria de perfil e reescrita de bio: nota 0-10 em 7 critérios, 3 versões de bio até 150 caracteres, 3 mudanças de maior impacto em ordem |
| **comentarios** | Classifica comentários exportados (pediu o material, dúvida, elogio, objeção, hater, spam) e escreve a resposta pública + DM de cada um — entrega tabela e CSV |
| **reel** | Reel vertical 1080x1920: gancho e roteiro cena a cena, narração opcional com TTS (ElevenLabs), mixagem de trilha, renderizado em MP4 com Remotion |

Todas as skills fazem uma entrevista curta antes de escrever, e nada é postado automaticamente — a pessoa revisa e posta.

## Instalar

```bash
git clone https://github.com/oficialrobsonalencar/instagram-agent-skills
```

Copie as pastas das skills que quiser para o diretório de skills do seu agente:

- **Claude Code / OpenCode:** `~/.agents/skills/`
- **Codex / outros:** o equivalente no seu agente

Exemplo (só o carrossel):

```bash
cp -r instagram-agent-skills/skills/carrossel ~/.agents/skills/
```

Requisitos por skill:
- `carrossel`: Node 18+ e Playwright (`npx playwright install chromium`)
- `reel`: Node 18+, Remotion (instalado no primeiro uso), `ELEVENLABS_API_KEY` opcional para narração
- `legenda`, `perfil`, `comentarios`: sem dependências — o agente faz o trabalho

## Licença

[MIT](LICENSE) — use comercialmente, modifique, redistribua. Atribuição apreciada.
