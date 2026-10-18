# Instagram Agent Skills

Agent skills for Instagram content creation — written for Claude Code, OpenCode, Codex and any AgentSkills-compatible agent. In Portuguese (pt-BR), with real file export (PNG, MP4, CSV — not just text).

Five skills, one goal: turn an idea into ready-to-post content, end to end.

## Skills

| Skill | What it does |
|---|---|
| **carrossel** | Complete Instagram carousel, cover to last slide, exported as 1080x1350 PNGs via Playwright |
| **legenda** | Caption with a first-125-characters hook, skimmable body, single CTA and niche hashtags — delivers 3 hook options |
| **perfil** | Profile audit and bio rewrite: scores 0-10 across 7 criteria, 3 bio versions up to 150 chars, top 3 changes ranked by impact |
| **comentarios** | Classifies exported comments (material request, question, praise, objection, hater, spam) and writes the public reply + DM for each — outputs table and CSV |
| **reel** | Vertical 1080x1920 reel: hook and scene-by-scene script, optional TTS narration (ElevenLabs), music mixing, rendered to MP4 with Remotion |

All skills interview the user briefly before writing, and nothing is posted automatically — the person reviews and posts.

## Install

```bash
git clone https://github.com/oficialrobsonalencar/instagram-agent-skills
```

Copy the skill folders you want into your agent's skills directory:

- **Claude Code / OpenCode:** `~/.agents/skills/`
- **Codex / others:** your equivalent skills path

Example (carrossel only):

```bash
cp -r instagram-agent-skills/skills/carrossel ~/.agents/skills/
```

Requirements per skill:
- `carrossel`: Node 18+ and Playwright (`npx playwright install chromium`)
- `reel`: Node 18+, Remotion (installed on first run), optional `ELEVENLABS_API_KEY` for narration
- `legenda`, `perfil`, `comentarios`: no dependencies — the agent does the work

## Language

The skills are written in Portuguese because that is the audience they serve — but the agent reads them in any language, so you can prompt in English and still get pt-BR-ready output. Feedback and issues in any language are welcome.

## License

[MIT](LICENSE) — use commercially, modify, redistribute. Attribution appreciated.

## Author

**Robson Alencar** — [@pastorrobsonalencar](https://www.instagram.com/pastorrobsonalencar/)

