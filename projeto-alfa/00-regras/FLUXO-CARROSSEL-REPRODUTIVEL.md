# Fluxo repetivel de carrosseis | Instagram ALFA

Objetivo: um pedido claro produz uma entrega verificavel. Nunca declarar trabalho concluido somente porque exportou PNG.

## 1. Entrada e referencias
- Executar apenas quando houver pedido explicito de criacao ou edicao.
- Identificar arquivos de referencia DO PEDIDO ATUAL. Nao reutilizar referencia antiga por proximidade de nome ou pasta.
- Registrar pedido, referencia autorizada, quantidade de slides, textos, destino e status.
- Se houver referencia, extrair geometria, blocos, alinhamentos e estilo tipografico. Nao substituir por layout generico.
- Se a fonte exata de uma imagem for incerta, pesquisar fontes do Windows e declarar aproximacao. Nao fingir identidade exata.

## 2. Tipografia do Windows, sem fallback silencioso
- Consultar 06-referencias/catalogo-fontes-windows.json; pesquisar com 02-scripts/consultar_fontes_windows.ps1 -Filtro 'NOME'.
- Confirmar familia e variantes instaladas: titulo, corpo, destaque e assinatura, com peso, inclinacao e espacamento corretos.
- Nao usar Arial, Helvetica, Times New Roman, sans-serif como fonte principal padrao, salvo referencia explicita e aprovacao registrada.
- Nao depender de @import remoto nem escolher familia que nao esteja instalada. Nao copiar ou distribuir fontes do computador.
- Apos tipografia realmente conferida e aprovada, salvar tipografia-aprovada.json na pasta do trabalho: referencia_do_pedido, familias_permitidas e aprovado_pelo_usuario.
- Nao marcar aprovado_pelo_usuario=true por inferencia ou pelo proprio agente.
- Antes de declarar entrega final: python 02-scripts/validar_tipografia_carrossel.py CAMINHO_HTML --manifesto CAMINHO_tipografia-aprovada.json.
- Codigo 4 significa REPROVADO: nao entregar como final.

## 3. Producao, revisao e entrega
- Conservar HTML/CSS e referencias autorizadas; corrigir a fonte no design, nao recriar uma estetica diferente.
- Produzir previa em pasta separada; conferir letras, acentos, alinhamento, peso, margens, cortes, assinatura e todos os slides.
- O qa_carrossel.py confere propriedades tecnicas. aprovado_tecnicamente NAO significa aprovado_visualmente.
- Rejeitar fontes ausentes, substituicoes silenciosas e importacoes remotas incorretas.
- Corrigir cada motivo de reprovacao, sem reiniciar o trabalho nem substituir a arte original aprovada.
- Trabalhos antigos rejeitados NAO sao novas referencias.

## 4. Agendar ou publicar
- O bloqueio geral impede fila sem liberacao individual; nao significa impossibilidade universal. Verificar autorizacao do pacote exato e recibo real antes de publicar. Nunca remover o bloqueio geral para forcar a fila.
- Nao reutilizar tarefas antigas IG Carrossel 8h para pedidos novos.
- Data/hora exigem dia completo, fuso America/Sao_Paulo, conta, pacote exato de PNGs e legenda revisada.
- Confirmar agendamento no mecanismo real, nao apenas responder em texto.
- Se pacote, legenda, aprovacao visual ou liberacao manual faltarem, explicar qual item falta sem afirmar que foi agendado.
- Agendamento exige nova ordem e tarefa Windows real; publicacao exige autorizacao individual comprovavel do pacote exato. Nunca reutilizar job publicado.
