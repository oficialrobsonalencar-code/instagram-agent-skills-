---
name: instagram-destaques
description: Inspecionar e editar capas dos Destaques existentes de @pastorrobsonalencar no Android via Appium sem criar seções duplicadas.
---

# Instagram Destaques: protocolo obrigatório

## Estado verificado em 19/11/2026
**Estado final atualizado às 22:25:** existem os 6 Destaques originais (YouTube, Testemunhos, Twitter, Vídeos, Quarto d Guerra e WhatsApp) e 1 destaque ADICIONAL **Orações**, criado por ordem EXPRESSA do usuário com TRÊS vídeos genuínos do canal Robson Alencar (Oração da Manhã, Salmo 125, Oração da Noite Salmo 23). Sua capa aprovada preta/dourada `destaque-1-oracoes.png` está confirmada na fileira do perfil e o XML `01-conteudo/oracoes-canal-20261119/inspecao-app/67-verify-three.xml` confirmou `story 1 de 3`. Cinco outras seções extras indevidas (Pregações, Estudos, Versículos, Cultos, Contato) seguem arquivadas. O histórico `debug/restaurar-destaques-20261119/result.json` é ANTERIOR à criação autorizada de Orações. NÃO executar novamente o script de arquivamento e não remover Orações.

## Sem ambiguidades
1. Se o usuário pedir TROCAR CAPAS, **nunca clicar em Novo, Criar Destaque, adicionar Story nem publicar Feed**. O fluxo permitido é abrir o Destaque existente de nome conferido > Editar destaque > Editar capa > Abrir galeria > selecionar PNG correto > Concluir > Concluir > verificar capa circular no perfil.
2. Não alterar YouTube, Twitter, Vídeos, Quarto d Guerra ou WhatsApp com imagens de tema diferente. O único dos sete PNGs com correspondência nominal a um Destaque original é Testemunhos.
3. Se o destino não existir, relatar isso e PARAR a edição. Não criar automaticamente outra seção nem renomear uma existente.
4. Não usar Playwright/Instagram Web. Usar Appium no POCO X7 Pro com USB autorizado.
5. Antes de agir, identificar conta @pastorrobsonalencar e varrer toda a fileira horizontal nos dois sentidos. Nunca usar coordenadas fixas antigas.
6. A grade da galeria MUDA DE ORDEM. É PROIBIDO escolher imagem por índice. Identificar miniatura por comparação visual com o PNG aprovado; em caso de incerteza, não salvar.
7. Salvar a capa e depois salvar o Destaque, DUAS confirmações separadas. Screenshot da galeria ou palavra FIM no log NÃO comprovam sucesso.
8. Verificar o círculo final com screenshot. Sem prova: PENDENTE, jamais CONCLUÍDO.

## Fontes válidas
- PNGs aprovados: `01-conteudo/destaques-20261118/out/`
- Appium e biblioteca: `04-skills/instagram-android-appium/`
- Script de auditoria: `debug/appium-destaques-refazer/verificar_destaques_corrigido.py`
- Reconhecimento visual e edição: `debug/appium-destaques-refazer/validar_capa_visual.py`, `helpers.py` e `corrigir_final.py`.
- Estado restaurado: `debug/restaurar-destaques-20261119/result.json`
- Script `arquivar-extras.py`: EXECUTADO, histórico, NÃO RODAR NOVAMENTE.
- Scripts `corrigir1.py`, `corrigir2.py`, `corrigir3.py`, `verificar.py`, `verificar2.py`: OBSOLETOS, NÃO USAR.

## Invariantes
Preservar os seis Destaques originais, os Stories e a sessão autenticada. Não excluir nada definitivamente. Uma nova criação de Destaque exige ordem EXPLÍCITA do usuário para CRIAR aquele Destaque; uma ordem para trocar capas não basta. Nunca alegar 7/7 sem verificação independente da imagem correspondente no perfil.
