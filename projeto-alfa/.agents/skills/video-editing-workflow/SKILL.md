---
name: video-editing-workflow
description: "Workflow completo de edição de vídeo para Reels - Pastor Robson Alencar. Use quando precisar criar, editar ou renderizar vídeos com narração de voz clonada."
---

# Workflow de Edição de Vídeo

## Estrutura de Diretórios

```
E:\EDITOR AUTOMATICO\VIDEO\
├─ src\
│  ├─ Composition.tsx          # Fonte principal Remotion
│  └─ chapters\                  # Estrutura por capítulos
├─ audio\
│  ├─ input\                    # Narrações a gerar
│  └─ output\                   # Audios renderizados
├─ assets\
│  └─ scenes\                   # Imagens das cenas
└─ output\
   └─ final\                    # Vídeos exportados finais
```

## Comandos Principais

### 1. Verificar estrutura
```bash
python paths.py
```

### 2. Usar áudio existente
```bash
python gerar_voz.py usar --nome reel_01_tres_chaves --output "E:/EDITOR AUTOMATICO/VIDEO/audio/output/tres_chaves.wav"
```

### 3. Renderizar vídeo básico
```bash
npx remotion render src/Composition.tsx output/video_basico.mp4
```

### 4. Renderizar com narração
```bash
ffmpeg -i output/video_basico.mp4 -i audio/output/tres_chaves.wav -c:v copy -c:a aac -shortest output/final/video_com_narricao.mp4
```

## Workflows Disponíveis

### Workflow 1: Criar Reel com Narração
1. `python gerar_voz.py usar --nome <id>` → gera áudio em `audio/output/`
2. `npx remotion render src/Composition.tsx output/temp.mp4` → renderiza vídeo
3. `ffmpeg -i output/temp.mp4 -i audio/output/<id>.wav -c:v copy -c:a aac output/final/<nome>.mp4`

### Workflow 2: Renderizar Capítulos Específicos
```bash
npx remotion render src/Composition.tsx output/chapter_01.mp4 --props='{"chapter": 1}'
```

### Workflow 3: Listar Audios Disponíveis
```bash
python gerar_voz.py listar
```

## Caminhos Definidos

| Finalidade | Local |
|------------|-------|
| Fonte Remotion | `E:\EDITOR AUTOMATICO\VIDEO\src\Composition.tsx` |
| Audio de entrada | `E:\EDITOR AUTOMATICO\VIDEO\audio\input\` |
| Audio de saída | `E:\EDITOR AUTOMATICO\VIDEO\audio\output\` |
| Cenas/Assets | `E:\EDITOR AUTOMATICO\VIDEO\assets\scenes\` |
| Vídeo final | `E:\EDITOR AUTOMATICO\VIDEO\output\final\` |

## Skills Conectadas

- `/guia-maquina-de-reels` - Frameworks de criação de Reels
- `/whats-the-difference-short` - Fórmula de 5 cenas para comparações
- `/remotion-best-practices` - Melhores práticas de renderização

## Configuração Renomada

**OBS**: Todos os caminhos usam as variáveis do `paths.py` para evitar erros de digitação.