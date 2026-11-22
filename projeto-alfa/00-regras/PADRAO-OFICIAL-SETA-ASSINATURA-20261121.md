# PADRAO OFICIAL: SETA E ASSINATURA, 21/11/2026

**Referência histórica aprovada para desenho da seta e assinatura (NÃO para altura):** PENÚLTIMA (3ª de 4) imagem no print do usuário.
**A última (4ª) está ERRADA. Não copiar.**
Título que identifica a correta: **ISSO NÃO TEM / NADA A VER / COM AQUILO**, subtítulo **E vice-versa.**
O arquivo definitivo foi localizado no projeto e seu SHA-256 foi verificado. Não escolher versões pelo nome ou pela data.

## Fonte de verdade
- PNG historico intacto (desenho e assinatura, seta vertical antiga REPROVADA): `07-identidade-visual/padrao-oficial/REFERENCIA-CORRETA-PENULTIMA.png`
- Mapeamento estruturado: `07-identidade-visual/padrao-oficial/mapeamento.json`
- Modelo editável corrigido: `07-identidade-visual/padrao-oficial/modelo-base-claro.html`
- Exemplo historico de HTML + PNG, NAO usar sua altura antiga da seta: `07-identidade-visual/padrao-oficial/exemplo-validado/`
- Componentes e tipografia: `07-identidade-visual/padrao-oficial/geometria-seta-assinatura.css`

## Medidas OBRIGATÓRIAS, em coordenadas do PNG 1080 × 1350
| Objeto | Medida aprovada |
|---|---|
| Seta | `top:300px`, `left:50%`, `translateX(-50%)`, `86 × 86px` |
| SVG seta | viewBox 0 0 86 86; círculo cx=43, cy=43, r=40; stroke-width=3 |
| Traço interno | d=`M28 43h30M47 33l10 10-10 10`; mesmo desenho e direção |
| Assinatura | `top:1089px`, centrada, uma linha, `display:flex`, `align-items:baseline` |
| Parte 1 | `@pastor`: Playfair Display italic 400 42px, espaçamento -0.02em |
| Parte 2 | `robsonalencar`: Poppins 800 38px, espaçamento -0.05em |
| Pixel da seta | bbox aproximado [493,296,586,389], tolerância 5px |
| Pixel da assinatura | bbox aproximado [335,1101,750,1144], tolerância 8px |

**NUNCA voltar a 137px, 220px ou 177px na seta, nem 68×68px.**
O post claro final e a prévia antiga foram comparados pixel a pixel: são iguais fora da região da seta. O PNG historico nao define a nova altura vertical. A prévia v2 também altera título e assinatura, e está reprovada como matriz visual.
Para fundo escuro, mudar somente o contraste de texto/seta, preservando geometria, fontes, pesos e alinhamentos.

## Processo obrigatório de um NOVO carrossel
1. Ler este documento, o mapeamento JSON e copiar os componentes do modelo oficial. Não escolher uma das outras imagens do print.
2. Criar o conteúdo novo em pasta própria sob `01-conteudo/`, com HTML editável e 6-10 PNGs `1080×1350`.
3. Renderizar PNG reais; conferir título, quebras, ortografia, legibilidade, fundo, contraste, área útil e assinatura em cada slide.
4. **Bloquear entrega se** `python 02-scripts/validar_padrao_carrossel.py --pasta "CAMINHO" --expected NUMERO` não retornar `aprovado_geometria:true`.
5. Depois executar também `python 02-scripts/qa_carrossel.py "PASTA-QUE-CONTEM-PNG" --expected NUMERO --exigir-cenas` e revisão visual humana.
6. Se qualquer PNG discordar do JSON atualizado na altura da seta OU da referência histórica na assinatura, corrigir a fonte e renderizar de novo. Não maquiar relatório JSON.
7. Criar prévia de todos os slides e simular a grade 1:1. A nova seta top 300px fica inteiramente dentro do recorte central 1:1; altura 137px foi rejeitada.
8. **Não publicar** como consequência de renderizar. Publicação requer ordem específica, conta verificada, controle antirreenvio e confirmação real do Instagram.

Histórico: carrosséis já publicados (escuro e claro de ansiedade) devem permanecer intactos, mesmo que usem outra geometria. O novo contrato vale para NOVAS criações e revisões solicitadas.


## REVISAO PRIORITARIA 21/11/2026, MAIS RECENTE QUE O PADRAO ANTIGO
O usuario REPROVOU a seta muito perto do topo no carrossel escuro ja publicado.
Nova posicao para TODAS as artes futuras: top 300px, largura e altura 86px, centro horizontal.
A antiga posicao top 137px esta REPROVADA. A assinatura continua top 1089px, Playfair 42px e Poppins 38px.
O PNG historico da penultima imagem fica INTACTO para desenho e identidade da assinatura, mas NAO define mais a altura vertical da seta.
O validador deve conferir 300px em NOVOS slides e conferir 137px apenas no arquivo de referencia historica.
A seta de 300px fica dentro da area central de seguranca para recorte 1:1.
Nao alterar imagens ja publicadas no Instagram, nem republicar automaticamente.
A altura 300px foi definida em resposta ao pedido de baixar a seta; confirmar o visual pela previa renderizada.
