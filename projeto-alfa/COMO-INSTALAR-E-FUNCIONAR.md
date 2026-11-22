# Como instalar, configurar e operar o projeto Instagram ALFA

Este documento descreve o procedimento correto de montagem e funcionamento **sem fornecer credenciais**. Não contém tokens, cookies, senhas, chaves, perfis de navegador, estados de fila ou material de mídia.

## 1. Pré-requisitos

Ambiente principal: Windows, OpenCode, Node.js e npm, Python 3 e bibliotecas Python utilizadas pelo código, navegador Chromium/Chrome e Playwright. O agendamento depende do Agendador de Tarefas e PowerShell do Windows. Outros módulos podem exigir FFmpeg, Remotion, ADB, Android SDK e Appium.

O repositório registra o código e os manifests de dependências. Ele não fornece binários, modelos de IA, a conta autenticada do Instagram nem serviços externos. Instale cada dependência pela fonte oficial e confirme versões compatíveis.

## 2. Organização das pastas

- `AGENTS.md` e `00-regras/`: entrada e governança dos agentes, QA e autorização.
- `opencode.json`: configura instruções, agente principal e localização das skills.
- `.opencode/agents/`: definição de comportamento do agente.
- `.opencode/plugins/`: publicador, proteção de escrita, orquestração e integração com o OpenCode.
- `.opencode/skills/`, `.agents/skills/`, `04-skills/`: habilidades específicas de produção, revisão, vídeo, pesquisa e automação.
- `02-scripts/`: executáveis de renderização, verificação, autorização, fila e agendamento.
- `07-identidade-visual/padrao-oficial/`: esquemas CSS/HTML e configuração geométrica da identidade.
- `01-conteudo/`: área **local**, criada para cada novo trabalho, com fontes, mídia e relatórios.
- `03-agendamentos/`: área **local** de operações, histórico, comprovantes e sessão autenticada.

**Importante:** `01-conteudo/`, `03-agendamentos/`, dados pessoais, imagens, vídeos, logs e arquivos de configuração com segredos **não são necessários no GitHub**. Eles são necessários, quando aplicáveis, no ambiente real de execução e devem permanecer privados.

## 3. Procedimento de configuração

1. Clonar o projeto em uma pasta de trabalho própria. Não sobrescrever o projeto do ALFA em funcionamento.
2. Instalar OpenCode, Node.js/npm, Python e as dependências indicadas nos manifests. Conferir quais bibliotecas Python cada script importa; Pillow, Appium-Python-Client e Selenium são exemplos identificados nos arquivos do projeto.
3. Conferir `.opencode/package.json`, `package.json` da raiz e manifests de skills. Instalar as dependências **em suas pastas corretas**, sem copiar `node_modules` nem `.venv` de outro computador.
4. Revisar `opencode.json` e os plugins/scripts que contêm caminhos absolutos do ALFA. Ajustar esses caminhos apenas **na nova instalação**, sem modificar acidentalmente o projeto original.
5. Instalar separadamente skills externas cujas pastas são referenciadas, mas não foram copiadas para o GitHub, respeitando licenças e procedência.
6. Configurar serviços e autenticadores externos exclusivamente no ambiente local, por seus procedimentos oficiais. **Não colocar nenhum valor de autenticação em README, logs, commits ou exemplos do GitHub.**
7. Garantir que o mecanismo de proteção de escrita tenha sua configuração local legítima de verificação e autorização. **Nunca remover bloqueios, falsificar aprovação nem gerar um recibo apenas para satisfazer o código.**
8. Criar diretórios operacionais locais vazios; não restaurar fila antiga, tarefas históricas do Windows nem comprovantes de outras postagens.
9. Verificar a compatibilidade da sessão do navegador com o perfil do Instagram, sem exportar cookies ou pastas de perfil.
10. Testar a descoberta das skills no OpenCode, o reconhecimento do agente e o fluxo de QA em material fictício de ensaio.

## 4. Como funciona a produção

**Carrossel:** ordem do usuário → identificar pasta e referência autorizada → texto e legenda → QA textual/editorial → `04-skills/carrossel/scripts/exportar.mjs` com Playwright → PNG real 1080×1350 → QA técnico, geométrico e visual → recibos vinculados ao pacote atual.

**Reel:** roteiro/cenas → seleção de motor apropriado (Remotion ou editor correspondente) → geração de quadros, movimento e áudio → renderização MP4 → conferência do vídeo real. Uma skill tipográfica não equivale, por si, a animação de personagens.

**Stories e Destaques:** produção e validação específicas; automação Android exige dispositivo, ADB e Appium operacionais. Não confundir esse módulo com o publicador de carrosséis.

**Perfil e bio:** consulta e edição são ações separadas. Uma auditoria não autoriza editar a bio automaticamente.

## 5. Como funciona a publicação

1. `instagram_publicador.consultar_pacote` identifica os arquivos reais, o nome `legenda.txt`, a conta e as pendências. Se o mesmo conteúdo já estiver confirmado como publicado, encerra a tentativa.
2. `instagram_publicador.revisar` exibe o pacote, a legenda e o resultado do QA.
3. `instagram_publicador.decidir` usa a ordem direta inequívoca do usuário ou uma escolha realmente respondida. Não exige nova pergunta por formalidade, mas **nunca interpreta autorização ambígua**.
4. `validar_pacote_publicacao.py` confere tamanho, integridade, ordem, relatório técnico/visual, recibo editorial e hashes SHA-256.
5. `verificar_resposta_interativa.py` e `autorizacao_por_pacote.py` confirmam a decisão real, a ação, a conta e o job exatos.
6. `postar-agora.py` prepara a fila e impede duplicidade; `fila-publicacao.py` processa apenas o job permitido; `publicar-seguro.cjs` opera o navegador autenticado local.
7. Sucesso exige **comprovação positiva da plataforma**. Falha ou resultado desconhecido vai para revisão sem reenvio automático.

## 6. Como funciona o agendamento

A data/hora futura deve ser completa, com fuso. `agendar_post_aprovado.py` registra uma tarefa Windows de execução única para o job autorizado. O sistema precisa confirmar a existência da tarefa e seu `NextRunTime`. No horário, a tarefa chama o processo para o mesmo ID. O mero agendamento **não equivale a publicação concluída**; o resultado final deve ser verificado.

## 7. Testes sem publicar nada

Verificar JSON e sintaxe Python/Node.js, instalação de dependências, registro das skills, renderização de mídia fictícia, validação editorial e visual, identificação de pacotes, bloqueio de duplicação, horário com fuso e estado de QA. Não realizar `publicar`, `agendar` ou edição de perfil em teste de diagnóstico sem ordem específica.

## 8. Evidências e segurança

Registrar por operação: arquivo de origem, versão, hashes, QA, decisão real, job e comprovante de execução. Esses dados operacionais ficam **no computador**, não no GitHub público. O repositório guarda apenas a implementação técnica, contratos e procedimentos de instalação e de funcionamento.

## 9. Limitações conhecidas do snapshot

- Caminhos absolutos do ALFA não foram parametrizados em todos os scripts.
- Algumas skills externas necessárias ao projeto estão declaradas em `opencode.json`, mas não estão distribuídas neste snapshot.
- Dependências e serviços externos devem ser instalados e configurados separadamente.
- O mecanismo de verificação das autorizações depende de sua configuração local legítima, que não faz parte do GitHub.
- Teste de sintaxe bem-sucedido não prova publicação ou agendamento real. Não afirmar implantação completa sem teste de ponta a ponta.

**Leia também:** `MAPA-PONTA-A-PONTA.md`, `INVENTARIO-TECNICO.md`, `MANIFESTO-TECNICO.json` e `VERIFICACAO-TECNICA.md`.