
# Mapa técnico ponta a ponta | Projeto Instagram ALFA
**Edição técnica: 22/11/2026** · **Origem auditada:** `I:\Projetos\Instagram-RobsonAlencar` · **Destino GitHub:** `projeto-alfa/`

Esta documentação descreve o código e as regras locais inspecionadas no ALFA. Ela não inclui imagens, áudios, vídeos, credenciais, cookies, tokens, sessões, backups ou comprovantes de publicação. Cópia de código não significa sessão autenticada ou publicação comprovada.

## 1. Visão geral e fluxo completo

```text
Ordem do usuário (OpenCode no ALFA)
   │
   ├─► identificar tarefa e pasta correta
   │      ├─ consultar / auditar / revisar
   │      ├─ criar ou corrigir carrossel / Reel / Story
   │      ├─ editar Destaques / bio
   │      └─ publicar agora / agendar (somente ordem explícita)
   │
   ├─► AGENTS.md + opencode.json + modo-deus + quality-director
   │                      + instagram-write-guard
   │
   ├─► diretor_instagram.py + mapa de skills + referências autorizadas
   │
   ├─► produzir HTML / texto / cena / legenda conforme formato
   │
   ├─► qa_texto_taxonomia.py + ig-caption + humanizer
   │
   ├─► exportar.mjs (Playwright / Chromium) ou motor de vídeo adequado
   │
   ├─► validar PNG/MP4 real, tipografia, geometria, identidade e revisão visual
   │
   ├─► instagram_publicador.consultar_pacote → revisar
   │                      │
   │              aprovação verificada:
   │       ordem direta inequívoca OU pergunta respondida
   │                      │
   ├─► instagram_publicador.decidir
   │
   ├─► validar_pacote_publicacao.py → verificar_resposta_interativa.py
   │                                  → autorizacao_por_pacote.py
   │
   └─► postar-agora.py → fila-publicacao.py → publicar-seguro.cjs
                         │                       │
                         │ imediato              └─ navegador/perfil local
                         │
                         └─ futuro: agendar_post_aprovado.py
                                       │
                                 Agendador Windows
                                       │
                                execução no horário
                                       │
                       comprovante positivo do Instagram
                                       │
                    processados/ID.json OU revisar/ID.json
```

**Estados não intercambiáveis:** CRIADO, RENDERIZADO, QA_TECNICO, QA_VISUAL, AUTORIZADO, AGENDADO, TENTATIVA_INICIADA e PUBLICADO_CONFIRMADO. Uma autorização permite a tentativa, mas não comprova publicação.

## 2. Mapa das pastas

| Origem local | Responsabilidade | Política de envio ao GitHub |
|---|---|---|
| `AGENTS.md` | Instruções globais do projeto, retomada e QA | Versão técnica saneada, sem estados de postagem |
| `opencode.json` | Agente padrão e caminhos de instruções/skills | Arquivo técnico |
| `.opencode/agents/` | Agente principal `modo-deus` | Configuração técnica |
| `.opencode/plugins/` | Guard, publicador, qualidade, GPU, grafo, auditoria | Código dos plugins |
| `.opencode/skills/` | Skills do OpenCode | Textos e scripts, sem bibliotecas vendorizadas |
| `.agents/skills/` | Skills auxiliares | Textos e scripts |
| `00-regras/` | Normas de produção e publicação | Somente regras permanentes |
| `01-conteudo/` | Carrosséis, rascunhos, fontes e PNGs reais | **Excluído integralmente** |
| `00-usuario/` | Fotos e dados particulares | **Excluído integralmente** |
| `02-scripts/` | Scripts de criação, QA, fila, postagem e agendamento | Scripts ativos, sem backups/testes históricos |
| `03-agendamentos/` | Fila, perfil de navegador, autorizações, resultados e logs | **Excluído integralmente** |
| `04-skills/` | Carrossel, legenda, texto, vídeo, Appium, outros | Scripts e instruções, sem instalações dependentes |
| `05-agentes/` | Papéis dos agentes | Descrição técnica |
| `06-referencias/` | Protocolo, mapa de skills e fontes técnicas | Documentos de arquitetura, sem históricos |
| `07-identidade-visual/padrao-oficial/` | CSS/HTML/esquema da marca | Somente código, sem PNG |
| `node_modules/`, `.venv/`, `.git/` e caches | Dependências derivadas, instalação e estado | **Excluídos** |

O GitHub preserva a pasta de skills genéricas do repositório e acrescenta `projeto-alfa/` como snapshot técnico independente. Não envia a pasta local inteira, nem mescla seus bancos com outros projetos.

## 3. Boot do OpenCode e agentes

1. Iniciar o OpenCode na raiz `I:/Projetos/Instagram-RobsonAlencar`, não na raiz de outro aplicativo.
2. `opencode.json` define `default_agent: modo-deus`, `skills.paths` e as instruções aplicáveis.
3. `.opencode/agents/modo-deus.md` define agente primário, ferramentas, delegação, testes e regras de contexto. O modelo declarado é uma dependência do provedor NVIDIA, não é instalado pelo GitHub.
4. `quality-director.js` injeta orientações de fidelidade, crítica visual, idioma e preservação de estado no contexto. Ele não publica nem audita PNG sozinho.
5. `instagram-write-guard.js` controla operações de leitura, escrita e execução. Shell liberado para renderizar não é autorização para remover bloqueios de publicação.
6. `graphify.js` e os mapas auxiliam a encontrar código por função. O grafo é cache gerado localmente e não precisa estar versionado.
7. `diretor_instagram.py` auxilia a classificar pedidos. A intenção real do usuário prevalece sobre classificações ambíguas.
8. Usar somente skills necessárias à tarefa. Diretório existente não significa que uma skill foi de fato carregada.
9. Subagentes como `executor-codigo`, `executor-visual` e `auditor-deus` só contam como efetivos depois de chamada e resultado comprovados. Não inventar retorno de auditoria nem mudar de modelo silenciosamente.
10. Compactação de sessão deve preservar: tarefa, caminho, design autorizado, versão, hash, legenda, estado QA, autorização e resultado. Não copiar histórico inteiro e não reutilizar saída de outra publicação.

## 4. Como funciona um carrossel

**Entrada:** pedido atual, tema, texto ou referência expressamente escolhida. **Fontes locais típicas:** `carrossel.html` e `legenda.txt`. **Saída operacional:** `out/slide-01.png` até `out/slide-NN.png`, QA e prévia.

1. Identificar exatamente a pasta e a versão do trabalho. Em correção, preservar o design aprovado; não inventar outro.
2. Escrever conteúdo por slide; revisar gramática, acentuação, afirmações, citações e semântica bíblica.
3. Legenda: usar `humanizer` + `ig-caption`; um CTA, no máximo cinco hashtags, gancho inicial, sem resíduos de texto de IA.
4. Rodar `qa_texto_taxonomia.py` na fonte atual. O dicionário automático não prova exegese perfeita.
5. Usar o exportador oficial `04-skills/carrossel/scripts/exportar.mjs`; ele bloqueia quando a legenda obrigatória ou o QA textual falham.
6. Playwright captura as seções `.slide` em PNG de **1080×1350**. HTML sozinho não é carrossel pronto.
7. Rodar `qa_carrossel.py`, `validar_padrao_carrossel.py`, `validar_tipografia_carrossel.py`, `validar_fidelidade.py`, `validar_layout_referencia.py` quando aplicáveis.
8. Inspecionar visualmente os PNGs gerados, inclusive capa, conteúdo e último slide, com texto, contraste, margens, caracteres e recorte central 1:1.
9. O `qa-relatorio.json` comprova apenas o que de fato foi testado. A aprovação visual e editorial exigem procedimentos próprios.
10. Mudar HTML, PNG ou legenda invalida os hashes e requer QA novamente. Nunca editar diretamente um comprovante para passar no validador.

**Padrão oficial futuro detectado:** seta central de 86×86px em `top:300px`; assinatura `top:1089px`; @pastor em Playfair Display itálico 42px, robsonalencar em Poppins 800 38px. Fonte: `07-identidade-visual/padrao-oficial/mapeamento.json`. Antiga seta `top:137px` permanece apenas como referência histórica rejeitada. A identidade deve ter geometria constante em todos os slides. A cor pode inverter por contraste.

## 5. Os validadores

| Executável | Verifica |
|---|---|
| `qa_texto_taxonomia.py` | grafia, taxonomia e regras determinísticas do texto |
| `validar_legenda_editorial.py` | legenda, hash e existência de revisão editorial real |
| `qa_carrossel.py` | integridade e geometria técnica dos PNGs |
| `validar_padrao_carrossel.py` | assinatura/seta e seu padrão em todos os slides |
| `validar_tipografia_carrossel.py` | fontes e manifesto de tipografia quando requerido |
| `validar_fidelidade.py` | referência e manifesto de fidelidade autorizados |
| `validar_layout_fixo.py`, `validar_layout_referencia.py` | alinhamentos, geometria e relação com referência |
| `validar_pacote_publicacao.py` | pacote publicável, hashes e recibos atuais |
| `avaliar_decisao_carrossel.py` | preflight sem autorizar ação |
| `verificar_resposta_interativa.py` | proveniência real da decisão do usuário na sessão OpenCode |
| `autorizacao_por_pacote.py` | permissão para job/conta/ação/hashes específicos |

**Provas operacionais:** `legenda.txt.editorial.json`, `out/qa-relatorio.json`, `out/aprovacao-visual.json` e arquivos de fila/permissão ficam no PC. O comprovante visual deve conter o ID do job, aprovador real e hashes SHA-256 dos slides e da legenda. Não estão no GitHub.

## 6. Ferramenta instagram_publicador

O plugin `.opencode/plugins/instagram-publisher.js` declara estas etapas:

- `consultar_pacote`: recebe a pasta relativa a `01-conteudo` e **nome** `legenda.txt`, consulta mídias, geometria, QA e possíveis falhas. Não publica. Verifica `JA_PUBLICADO` por comprovante compatível quando encontrado.
- `revisar`: gera ou recupera o `job_id` da revisão do pacote, apresenta conta, arquivos, legenda integral, horário, falhas e opções. A revisão persiste por sessão por 45 minutos.
- `decidir`: compara pasta, legenda, horário e fingerprint do conteúdo com a revisão. Corrigido em 22/11 para aceitar a ordem direta inequívoca do usuário **sem pedir uma segunda confirmação por formalidade**.
- `publicar`: etapa legada desabilitada; não chamar para contornar `revisar`/`decidir`.
- `consultar_agendamentos`: consulta somente leitura via `status-agendamento.py`.
- `consultar_bio`/`aplicar_bio`: consulta/aplicação de bio por rota separada; só aplicar com ordem explícita exata.

**Decisão direta e segurança:** `PUBLIQUE AGORA` ou `POSTE AGORA` inequívocos, vindos da mensagem real, bastam para a decisão quando mídia/QA/conta estão corretos. Se a intenção for incerta, usa-se `question` e aguarda-se resposta de fato. A frase ambígua `PUBLIQUE AGORA 8 HS` não é interpretada como ordem imediata ou agendamento sem desambiguar o horário. Mesmo com ordem explícita, nenhuma etapa inventa prova editorial, auditoria visual ou recibo.

**Revalidação:** após a decisão, roda novo QA. A sessão Python confirma mensagem/ID reais, conta e permissão individual. Resultado incerto nunca gera retry cego.

## 7. Autorização de publicação e hashes

`validar_pacote_publicacao.py` exige, entre outras condições:
1. status correto e procedência da aprovação;
2. lista de 1 a 10 arquivos existentes, não duplicados e no mesmo diretório;
3. para carrossel, PNG 1080×1350 e nomes ordenados `slide-01.png` etc.;
4. relatório técnico atual com aprovação técnica e visual, tipografia confirmada e publicável;
5. `legenda.txt` idêntica ao conteúdo que será enviado;
6. recibo editorial atual;
7. `aprovacao-visual.json` produzida por auditor admitido, associada ao mesmo job;
8. SHA-256 de cada slide e SHA-256 da legenda iguais aos aprovados.

`autorizacao_por_pacote.py` verifica a liberação individual, horário/fuso, ação e perfil. `verificar_resposta_interativa.py` confere a mensagem do usuário no servidor OpenCode (`127.0.0.1:4096` no ALFA). A liberação global não pode ser desligada para forçar um envio. Um JSON falsificado não é solução.

## 8. Postagem imediata e estados da fila

`postar-agora.py` coleta a mídia, verifica conta, legenda e duplicidade, exige QA e autorização, cria um job de fila com lock exclusivo e chama `fila-publicacao.py` para o ID autorizado.

`fila-publicacao.py`:
1. confirma liberação por job, sem executar fila genérica quando o bloqueio global está ativo;
2. verifica se há perfil/navegador dedicado em uso;
3. move a entrada da fila de JSON para `.running` de modo a isolar a tentativa;
4. chama `publicar-seguro.cjs` usando Chrome/Playwright e sessão autenticada local;
5. exige retorno real `PUBLICACAO_CONFIRMADA`;
6. coloca sucesso em `processados/ID.json`, e falha/incerteza em `revisar/ID.json`;
7. revoga a liberação ao final;
8. isola jobs órfãos, sem reenviar automaticamente.

Cookies, sessão de navegador e dados de conta **não** devem sair do ALFA. O GitHub contém código, não um login funcional.

## 9. Agendamento: o que acontece no Windows

A opção `agendar` requer data futura inequívoca, horário e fuso, normalmente ISO `AAAA-MM-DDTHH:MM:SS-03:00`.

`agendar_post_aprovado.py` valida o mesmo pacote/recibos, cadastra tarefa **específica por ID** no Agendador do Windows e confere `NextRunTime`. A tarefa é de execução única, sem reinício automático em falha (`RestartCount 0`), com bloqueio de instâncias concorrentes. No horário, executa somente o job aprovado. Um arquivo JSON de fila sem tarefa Windows confirmada **não** é agendamento. Um disparo da tarefa sem prova positiva no Instagram **não** é postagem.

Registros de agendas históricas são somente históricos; não devem criar tarefas novas nem ser reaplicados após uma atualização no GitHub.

## 10. Outros fluxos do projeto

**Reels e edição:** `ig-reel`, `.opencode/skills/reel-export` e motores do editor. O pipeline Remotion da skill genérica gera Reel tipográfico e pode usar TTS externo. Não é equivalente a animação de personagem, filmagem real ou clonagem de voz. Inspecionar quadros, áudio, sincronização, formato 1080×1920 e render MP4 antes de qualquer entrega.

**Stories e Destaques:** `ig-story` e `instagram-destaques`. O módulo `instagram-android-appium` contém automação via Android/ADB/Appium. Só opera com aparelho, driver e autenticação reais; não se confunde com o publicador de carrosséis.

**Perfil e bio:** `ig-profile`, `ig-audit` e plugin de auditoria de perfil. A edição de bio é uma ação externa própria, não subproduto automático de uma auditoria.

**Comentários, DMs, planejamento e pesquisa:** `ig-comment`, `ig-dm`, `ig-reply`, `ig-plan`, `ig-viral`, `instagram-last30days`. A existência da skill ou de um script não comprova conexão operacional com a plataforma. Pesquisa externa exige fonte verificável. Não republicar material de terceiros por estar em referência.

## 11. Conflitos encontrados e tratamento

**Corrigido no ALFA em 22/11/2026:** a documentação já aceitava uma ordem explícita de postagem, mas o plugin forçava uma nova pergunta mesmo quando a mensagem original continha `PUBLIQUE AGORA`. Foram alterados `.opencode/plugins/instagram-publisher.js`, `02-scripts/verificar_resposta_interativa.py` e `00-regras/ORDEM-OPERACIONAL-INSTAGRAM.md`. **10 testes de interpretação e rejeição de comandos passaram; sintaxe Python e Node aprovada.** Não houve postagem real no teste.

**Pendências que não podem ser escondidas:**
- Se o auditor visual não gera recibo real, QA e autorização podem continuar bloqueados. Não criar aprovação por conta própria.
- `QA técnico aprovado` não é `publicável`; o manifesto deve representar o material atual.
- Há versões antigas de geometria, scripts de publicação e regras no histórico. O padrão futuro é o mapa oficial e o exportador oficial. Não executar versões legadas.
- Algumas skills aparecem em várias pastas e podem conflitar. Identificar sempre o **caminho** e a versão efetivamente carregada.
- O código usa caminhos absolutos do Windows e precisa de adaptação para outra máquina.
- O GitHub original abrigava cinco skills genéricas, não o sistema local completo. O snapshot `projeto-alfa/` documenta a parte técnica local sem apagar os exemplos genéricos.
- Nenhum teste isolado comprova o funcionamento ponta a ponta do Instagram em produção.

## 12. Matriz de erros

| Sintoma | Causa a verificar | Correção correta |
|---|---|---|
| `LEGENDA_ARQUIVO_ESPERADO` | agente enviou texto em vez de `legenda.txt` | passar apenas o nome do arquivo |
| `QA_TECNICO_AUSENTE` | relatório não existe para o pacote atual | executar QA da mídia real |
| `QA_VISUAL_NAO_APROVADO` | revisão visual não concluída | auditar PNGs, sem falsificar JSON |
| `SLIDES_MUDARAM_APOS_AUDITORIA` | hash não corresponde à revisão | nova auditoria dos arquivos atualizados |
| `APROVACAO_DE_OUTRA_TAREFA` | ID do job não coincide | revalidar pacote correto |
| `RESPOSTA_NAO_ENCONTRADA` | resposta real não verificada | conferir mensagem ou question, sem repetir decidir cegamente |
| `REVISAO_EXPIRADA` | revisão com mais de 45 min | consultar e revisar de novo, mantendo arquivos aprovados |
| `ARQUIVOS_HORARIO_OU_LEGENDA_MUDARAM` | fingerprint da revisão divergiu | refazer a revisão |
| `BLOQUEADO_POR_PACOTE` | falta autorização/QA específicos | resolver a pendência real; manter bloqueio global |
| `AGENDAMENTO_NAO_CONFIRMADO` | Task Scheduler/NextRunTime inválido | corrigir tarefa e só então declarar agendado |
| `PUBLICACAO_NAO_CONFIRMADA` | ausência de comprovante do Instagram | marcar incerto e não reenviar |
| `Connection Closed` | sessão/navegador desconectado | diagnosticar sessão local sem upload duplicado |
| Playwright/Chromium indisponível | dependência de navegador | corrigir instalação e renderizar de novo |
| `401`/`429` de API/modelo | permissão, token ou limite do provedor | diagnosticar provedor sem trocar modelos silenciosamente |
| fonte divergente | fonte ausente ou fallback indevido | consultar fontes, corrigir CSS e reexportar |

## 13. Dependências e instalação em outra máquina

Origem: Windows, OpenCode 1.x, Node.js, Python (Pillow usado no QA), Playwright/Chromium. Alguns subfluxos exigem Remotion, FFmpeg, Android SDK/ADB/Appium, ferramentas de editor, APIs externas e provedores de modelo. **Não presume que tudo esteja instalado e disponível.**

Restauração segura:
1. Clonar o repositório e localizar `projeto-alfa/`.
2. Adaptar paths absolutos ao novo computador; não compartilhar pastas de fila nem perfis entre máquinas.
3. Instalar dependências por package manifests e instruções das skills; `node_modules` e `.venv` não são copiados.
4. Instalar separadamente skills externas não distribuídas e respeitar suas licenças.
5. Configurar provedores e acesso ao Instagram por mecanismos próprios e seguros. **Não copiar cookies, arquivos de sessão ou senhas.**
6. Criar pastas operacionais locais vazias, sem recuperar jobs históricos.
7. Validar sintaxe, configuração do OpenCode, roteamento, QA, exportador e reconhecimento de comandos em ensaio sem publicação.
8. Para validar publicação real, é indispensável autorização específica, pacote aprovado, sessão válida e comprovante da plataforma.

## 14. Matriz de aceitação

| Etapa | O que comprova sucesso |
|---|---|
| GitHub | commit remoto confirmado, arquivos exatos no manifesto, nenhum binário de mídia ou credencial |
| OpenCode | config válida, agente carregado e ferramentas reconhecidas |
| Produção | arquivos reais editáveis e PNG/MP4 produzido, não somente respostas em texto |
| Texto/legenda | conteúdo revisado e recibo vinculado à versão atual |
| Imagem/layout | checagens de geometria, tipografia e inspeção visual |
| Autorização | usuário real, ação explícita e pacote/hashes corretos |
| Agendamento | tarefa Windows cadastrada e NextRunTime confirmado |
| Postagem | recibo real com evidência positiva do Instagram |
| Falha ou timeout | estado de revisão sem reenviar automaticamente |
| Segurança | nenhuma credencial, mídia, sessão, log operacional ou material pessoal versionado |

## 15. Inventário minucioso dos arquivos técnicos

Consultar os documentos gerados na sincronização: `INVENTARIO-TECNICO.md` (cada arquivo, dimensão e hash SHA-256) e `MANIFESTO-TECNICO.json` (índice automatizável). Estes identificam o que foi copiado para o GitHub e permitem comparar versões sem usar mídia ou informações de login.

**Limites do relatório:** sintaxe e testes unitários da correção de decisões foram verificados; publicação e agendamento externos não foram disparados. O estado atual de autenticação e de filas do ALFA depende de consulta local contemporânea.

## AUDITORIA V2 - ASSINATURA INDEPENDENTE
- 02-scripts/verificar_aprovacao_visual.py: confere assinatura Ed25519 e hashes do pacote.
- 02-scripts/qa_carrossel.py: so preserva aprovacao visual assinada.
- 02-scripts/validar_pacote_publicacao.py: bloqueia provas antigas e invalidas.
- 02-scripts/auditoria_visual_operador.py: assinatura interativa apos inspecao real, com senha privada fora do projeto.
- 00-regras/AUDITORIA-VISUAL-ASSINADA-V2.md: procedimento sem credenciais no GitHub.
- Chaves e recibos reais permanecem apenas no ambiente local protegido.
- Ate instalacao de chave publica legitima, comprovantes sem prova V2 falham fechado.
