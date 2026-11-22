---
name: vision-qa-local
description: >-
  Analise de imagens reais com OCR, cores RGB, geometria e regressao visual no projeto Instagram do ALFA. Execute quando o usuario pedir para ler JPG/WEBP/PNG, conferir tipografia, verificar fundo, medir margem, comparar um slide com referencia ou provar que um design nao mudou. Somente leitura. Nao cria imagens ou publicacoes.
---

# Auditoria visual real do Build ALFA

## Proibicao de adivinhar
- JPG de SaveClip pode ser WEBP internamente, detecte pelo cabecalho/Pillow, nao pela extensao.
- Nunca afirme fundo preto ou sem seta com base apenas em LLM. Meca pixels e geometria.
- OCR pode errar; sempre traga transcricao com evidencia e indique trechos duvidosos.
- Ideias, referencias, pedidos de analise e mensagens do usuario NAO autorizam produzir carrosseis, imagens, slides, HTML nem publicar.
- Nao instalar modelos ou dependencias adicionais sem verificar a necessidade.

## Comandos disponiveis (nao mutam arquivos de imagem)

OCR estruturado:
python "I:/Projetos/Instagram-RobsonAlencar/.opencode/skills/vision-qa-local/scripts/ocr_local.py" "CAMINHO.jpg"

Cor objetiva do fundo ou de uma regiao:
python "I:/Projetos/Instagram-RobsonAlencar/.opencode/skills/vision-qa-local/scripts/dominant_colors.py" "CAMINHO.jpg" --region 100,100,1200,600

Medição de centros, margens e espacamento:
python "C:/Users/ROBSON ALENCAR/.config/opencode/inspect_layout_geometry.py" "CAMINHO.jpg"

Comparar duas imagens nos pixels (diferencas de texto podem ser esperadas):
python "I:/Projetos/Instagram-RobsonAlencar/.opencode/skills/vision-qa-local/scripts/pixel_diff.py" "REFERENCIA.jpg" "CANDIDATA.png"

Validar geometria com a imagem aprovada pelo usuario:
python "I:/Projetos/Instagram-RobsonAlencar/02-scripts/validar_layout_referencia.py" "CANDIDATA.png"
- Codigo de saida 2 = reprovar. Passar geometria nao garante fonte nem conteudo exatos.

Qwen visual local como verificacao adicional, nao fonte unica:
python "C:/Users/ROBSON ALENCAR/.config/opencode/inspect_visual_build.py" "CAMINHO.jpg"

## Sequencia obrigatoria
1. Verificar caminho absoluto, hash, dimensoes e assinatura do arquivo real.
2. Fazer OCR; se houver duvidas, confirmar por recorte ou leitura visual. Registrar erros, nao inventar.
3. Medir fundo/margens/centros/posicoes via ferramentas deterministicas.
4. Se solicitado COMPARAR, usar imagem aprovada e imagem candidata, diferencas pixel-a-pixel e geometria.
5. Se NAO solicitado criar, encerrar apos diagnostico. Nao escrever arte, HTML, slides, posts, nem tarefas.
6. Nunca usar arquivos descartados ou publicar; respeitar BLOQUEIO-PUBLICACAO-ATIVO.
