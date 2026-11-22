# Padrão obrigatório de qualidade do carrossel no Alfa

A arte tem de ser realmente produzida, inspecionada e exportada, não apenas planejada.

## Fidelidade
- Com referência enviada pelo usuário, inspecionar a imagem ou vídeo real; preservar seu vocabulário visual, composição, luz, materiais e hierarquia. Não impor paleta de um projeto anterior.
- Para cada frase do roteiro, usar uma cena, imagem ou objeto específico. Fundo e identidade podem repetir; imagem principal, emoji, mão ou cartão não podem ser a mesma em todos os slides.
- Não usar emojis ampliados, cartões de aplicativo ou ícones genéricos no lugar de uma imagem cinematográfica. Não deixar decoração obstruir textos.
- Impeccable, avoid-ai-design e skills de motion auxiliam a revisão; não substituem a referência nem impõem estética própria.

## Área segura
- Arquivo final: 1080 x 1350 pixels, proporção 4:5.
- Conteúdo textual essencial dentro de x=80..1000 e y=135..1215.
- Fonte carregada, português com acentos corretos, legível no celular, sem colisões nem linhas cortadas.
- Citações bíblicas: nunca colocar número de versículo junto a uma frase autoral como se fosse citação literal. Citação literal exige conferência do texto e da tradução; paráfrase/reflexão deve ser rotulada como tal ou ficar sem referência de versículo.
- Conferir pelo menos capa, meio e CTA, preferencialmente os oito slides.

## Execução
1. Identificar a solicitação e ler as referências pertinentes sem escanear históricos enormes.
2. Criar um plano com descrição visual exclusiva de cada slide, além do roteiro.
3. Gerar HTML e ativos reais; não reutilizar o mesmo item visual em todas as páginas.
4. Rodar o exportador em 04-skills/carrossel/scripts/exportar.mjs. Se retornar erro, corrigir e tentar novamente. Nunca alegar conclusão sem PNGs válidos.
5. Entregar arquivos e legenda, sem publicar quando o usuário só pediu criação.
6. Quando o usuário pedir explicitamente para postar agora, executar a tentativa sem pedir uma segunda aprovação, verificando conta e resultado para evitar duplicações.

## Testes
- Executar 02-scripts/testar-roteamento-20261111.py após alterações no diretor.
- O exportador deve rejeitar fixtures temporarias com imagem ficticia, arte repetida ou texto fora da area segura, sem recuperar trabalhos reprovados da quarentena. Amostras de referencia aprovadas devem continuar protegidas.
- Preservar versões originais e não modificar trabalhos não solicitados.
