---
name: visual-reference-adapter
description: Usar sempre que o usuario enviar qualquer imagem/modelo visual como referencia para artes, capas, carrosseis, reels, videos, animacoes e cenas. Manter a identidade visual da referencia e adaptar o elemento principal a cada frase.
---

# Adaptacao visual universal por referencia (qualquer modelo)

## Objetivo
A referencia enviada pelo usuario e a fonte de linguagem visual do trabalho ATUAL. Nao fixar o estilo da imagem anterior em todos os trabalhos. Cada nova referencia pode substituir a direcao artistica anterior, salvo instrucao explicita de combinar estilos.

## Regras obrigatorias
1. Observe a imagem real fornecida: proporcao, geometria, hierarquia, escala, respiro, paleta, gradientes, iluminacao, sombras, profundidade, materiais, tipografia aproximada e acabamento.
2. Diferencie os invariantes (linguagem visual que faz a serie parecer uma familia) dos variaveis (titulo, simbolo, objeto, personagem, ambiente e elementos de apoio especificos de cada frase).
3. Para CADA frase do roteiro, interprete significado literal e metaforico, assunto, emocao e contexto antes de escolher o objeto ou cena. Gere uma proposta visual diferente que corresponda a ESSA frase.
4. Mantenha a identidade visual coerente com a referencia, mas NUNCA repita automaticamente o mesmo objeto ilustrativo em todas as frases. Nao copiar marcas, nomes, logos e texto de terceiros.
5. Nao presumir que toda referencia seja laranja/preta ou estilo 3D. Uma nova referencia pode ser minimalista, editorial, fotografia, colagem, tipografica, desenho, aquarela, cinematografica etc.
6. Para cenas de video, especifique movimento de camera, animacao de elementos, transicoes e duracao de cada frase, preservando a direcao artistica comum. Para carrossel, uma arte distinta por slide e layout consistente.
7. Em assuntos biblicos/historicos, nao inventar versiculos ou fatos, nem introduzir objetos anacronicos em reconstituicoes.
8. Se o modelo de imagem referencia nao estiver acessivel no projeto, NAO fingir tê-lo analisado. Solicitar o arquivo/caminho ou usar o anexo efetivamente acessivel.
9. Textos finais, marcas e rodape devem ser compostos em camada editavel quando possivel; imagens de IA devem preferencialmente vir sem texto para evitar erros ortograficos. O rodape deve usar marca real do usuario, nunca logos/URLs falsos.
10. Antes de entregar, conferir semelhança do estilo, pertinencia de cada simbolo, fidelidade textual, formato e continuidade entre as cenas. Evitar reaproveitar imagem generica por falta de modelo sem informar isso.

## Contrato de planejamento por frase
Cada frase deve ter: frase_original, mensagem_central, simbolos_candidatos (2-3), elemento_escolhido, justificativa_visual, layout_invariante, prompt_visual, movimento_se_video, duracao_se_video, verificacao.
Separar assets de referencia de assets gerados; preservar originais, registrar versao e permitir refazer uma unica cena.

## Pipeline por destino
Instagram: 1080x1350 para carrossel, 1080x1920 para Reels/Stories; executar skills de composicao/legenda e salvar para revisao, sem publicar.
Editor E: converter referencia+roteiro em plano de cenas, gerar visual especifico por frase com motor disponivel, compor em Remotion/HyperFrames e validar MP4.
Editor I: usar o mesmo planejamento e delegar aos motores ALFA/BETA existentes, sem alterar arquivos-fonte ou contar com capacidade nao testada.

**Limite:** instrucao de agente nao e implementacao de gerador de imagem. Se nao houver motor de imagem/vídeo ou entrada da referencia, registrar a pendencia com clareza.


## Regra obrigatoria para video como referencia
- Se a referencia for um VIDEO, nao tratar como imagem estatica. Primeiro analisar duracao, cenas, ritmo de cortes, movimento predominante, enquadramento, cores, luz e audio.
- Usar implementacao E: python analisar_video_referencia.py --referencia ARQUIVO --saida PASTA para produzir storyboard e analise JSON.
- Depois executar python planejar_adaptacao_video.py --analise PASTA/analise-referencia.json --roteiro FRASES.txt --saida PASTA/plano-cenas.json para obter cena visual especifica por frase com Qwen.
- O video de referencia orienta a linguagem audiovisual, NAO justifica copiar logos, texto de terceiros, personagens e conteudo protegido.
- Na producao final, recriar efeitos para a mensagem do usuario: movimentos de camera, composicao, cortes, transicoes, graficos e som, preservando a direcao geral.
- Originais permanecem intactos. Referencia temporaria nao e output final.
- O analisador atual detecta cortes e movimento aproximados e registra quadros; a compreensao visual de objetos especificos da referencia e recriacao/renderizacao dos efeitos exigem um modelo de visao ou revisao. Nao declarar resultado final sem MP4 validado.
- Para varios videos de referencia, estudar cada um separadamente e aplicar apenas os aspectos que o usuario aprovou, sem misturar estilos automaticamente.


## Leitura visual real do video
- Depois do storyboard, executar no E: python ver_video_referencia_ia.py --analise PASTA/analise-referencia.json
- Usa Qwen2.5-VL local para observar quadros reais, não apenas metadados.
- planejar_adaptacao_video.py usa vision_review junto com cortes, cores, audio e movimento para conceitos distintos por frase.
- Se visão local falhar, reportar falha, não fingir leitura visual completa.
- Para vídeos de terceiros, recriar linguagem audiovisual com conteúdo próprio, não copiar logotipos nem personagens.


## Modo universal: criação, adaptação ou somente edição
- Esta regra não vale apenas para Reels, animações ou projetos bíblicos. Vale para qualquer demanda audiovisual ou visual: edição de vídeo pronto, cortes, colorização, legendas, transições, áudio, vinheta, capa, imagem, carrossel, Story e composição.
- PRIMEIRO detectar se o pedido é (A) CRIAR do zero, (B) ADAPTAR com uma referência, (C) EDITAR mídia já existente ou (D) CORRIGIR um problema pontual.
- Modo EDITAR: usar o arquivo original como fonte e aplicar apenas as mudanças pedidas. NÃO recriar toda a mídia, substituir rostos, vozes, texto, identidade visual ou imagens existentes sem solicitação explícita.
- Modo ADAPTAR: estudar vídeo/imagem de referência e transferir princípios de composição, movimentos, ritmo, transições, iluminação e acabamento ao material próprio fornecido. Não transferir automaticamente objetos, marcas, rostos ou textos alheios.
- Modo CRIAR: planejar cenas e produzir ativos novos, coerentes com o roteiro e com as referências fornecidas.
- Modo CORRIGIR: preservar o restante e corrigir somente o aspecto solicitado.
- Usar ffprobe/OpenCV e Qwen2.5-VL para leitura de mídia quando disponíveis; combinar com interpretação temporal e linguística para roteiro e efeitos. Inspecionar o arquivo REAL, nunca presumir conteúdo a partir do nome.
- Identificar a mídia de origem e a referência separadamente; se não houver arquivo necessário, não fingir ter analisado ou editado.
- Criar saída nova, preservando original, trilhas e metadados relevantes sempre que tecnicamente possível. Não sobrescrever arquivos aprovados sem autorização.
- Entregar resultado REAL e verificável, com duração, codec, resolução, áudio e revisão de quadros. Se o motor ainda não executa certo tipo de edição, informar claramente e não simular sucesso.
- Uma imagem de referência pode estabelecer estética; vídeo de referência pode estabelecer estética E linguagem temporal; áudio de referência pode orientar ritmo, timbre ou tratamento conforme autorização.
- Escolher ferramentas pelo objetivo: FFmpeg para cortes/transcodificação/áudio, Remotion ou HyperFrames para motion e textos, ComfyUI para geração, SCINE para voz, edição gráfica para artes. Não acionar geração IA quando basta editar.
- Não publicar nem agendar automaticamente como efeito colateral de criar ou editar.
