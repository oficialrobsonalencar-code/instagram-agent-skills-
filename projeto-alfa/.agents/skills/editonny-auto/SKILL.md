---
name: editonny-auto
description: "Editonny para agentes - vídeos automatizados com reconhecimento de voz e visão. Use quando precisar de edição automática de vídeos após análise visual/áudio."
---

# editonny-auto

## Agente que ouve e age automaticamente

Use quando o agente precisa:
- Analisar vídeos automaticamente (reconhecimento de fala, visão computacional)
- Gerar cortes, legendas, transições programaticamente
- Criar vídeos a partir de descrições textuais

## Fluxo Automático

1. **Análise Inicial** - O agente detecta automaticamente:
   - Duração total
   - Identidade de falantes
   - Principais tópicos
   - Momentos de pausa

2. **Extração de Narração** - Transcreve automaticamente:
   ```bash
   python scripts/editonny.py transcript --input /caminho/video.mp4
   ```

3. **Geração de Cenas** - Cria baseado em tópicos:
   ```bash
   python scripts/editonny.py scene --project ./project --use "three-steps" --auto
   ```

4. **Renderização** - Gera vídeo final:
   ```bash
   python scripts/editonny.py build --output ./output.mp4
   ```

## Scripts Principais

| Comando | Função |
|---------|--------|
| `doctor` | Verifica pré-requisitos |
| `catalog "termo"` | Busca cenas por palavra-chave |
| `media status` | Verifica arquivos de mídia |
| `inspect video.mp4 --json` | Analisa vídeo |
| `scene --project ./p --use ID` | Aplica cena |
| `workspace init` | Cria workspace |
| `build` | Renderiza vídeo |

## Uso com Pastor Robson

Para vídeos automatizados do Pastor Robson:

```bash
# 1. Analisar vídeo existente
python scripts/editonny.py inspect ./videos/raw/reel_01.mp4 --json

# 2. Transcrever narração
python scripts/editonny.py transcript --input ./videos/raw/reel_01.mp4 --output ./transcricao/

# 3. Buscar cenas apropriadas
python scripts/editonny.py catalog "crucificação"
python scripts/editonny.py catalog "resurreição"

# 4. Criar projeto com cenas
python scripts/editonny.py workspace init --title "Três Cruzas" --auto

# 5. Aplicar cenas
python scripts/editonny.py scene --project ./project --use tres-cruzas --auto

# 6. Renderizar
python scripts/editonny.py build --output ./output/reel_tres_cruzas.mp4
```

## Configurações Automáticas

Quando o agente detecta que deve agir automaticamente:
- **Formato**: 1080x1920 (vertical Reels)
- **FPS**: 30
- **Codec**: H.264, MP4
- **Áudio**: -14 LUFS padrão
- **Legendas**: automáticas, sem sobrepor rosto

## Cenários Predefinidos

Para conteúdo bíblico:
- `tres-cruzas` - Estrutura de 3 pontos-chave
- `resurreição` - Narrativa de eventos
- `crucificação` - Detalhe histórico
- `crescimento` - Estatísticas e dados

## Integração com XTTS

O editonny pode usar voz clonada local:
```bash
python scripts/editonny.py tts --text "Texto da narração" --voice "./voz/pr_robson_minha_voz.wav" --output narration.wav
```

## Permissões Necessárias

O agente pode:
- ✅ Ler/transcrever vídeos locais
- ✅ Gerar legendas automáticas
- ✅ Aplicar cenas do catálogo
- ✅ Renderizar saída local

O agente NÃO pode:
- ❌ Enviar conteúdo para serviços externos
- ❌ Utilizar vozes comerciais (ElevenLabs, etc.)
- ❌ Publicar automaticamente

Use `/editonny-auto` para iniciar edição automatizada!