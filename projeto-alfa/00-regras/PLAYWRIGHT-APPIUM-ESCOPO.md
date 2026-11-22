# Automação visual do Instagram: Playwright e Appium
Origem da skill Playwright: https://github.com/lackeyjb/playwright-skill
Escopo: somente I:/Projetos/Instagram-RobsonAlencar.

## Escolha obrigatória da ferramenta
- Para navegar em sites, inspecionar layout, validar formulários, capturar screenshots, conferir uploads em prévia e testar interfaces web, usar a skill local `.opencode/skills/playwright-skill/SKILL.md`.
- Para editar a capa de um Destaque diretamente no aplicativo Android do Instagram, usar a base `04-skills/instagram-android-appium`, nunca Playwright de navegador. O repositório Appium é base técnica, não contém rotina pronta de troca de capa.
- Para publicar posts e carrosséis, manter o publicador seguro existente, suas verificações e proteções contra duplicação. Não criar publicador paralelo.
- Para iPhone, as integrações Playwright Web e Appium Android não automatizam o aplicativo iOS.

## Regras permanentes
1. Ao receber uma ordem explícita para criar, testar, editar ou publicar, executar a tarefa autorizada sem pedir aprovações repetidas. Checar somente requisitos técnicos indispensáveis.
2. Abrir a página ou o aplicativo real, ler o estado atual, identificar o alvo e confirmar a operação com evidência. Não usar coordenadas inventadas nem declarar sucesso com base em intenção.
3. Não pegar imagens de pastas antigas, rascunhos rejeitados ou referências históricas. Usar exclusivamente os arquivos que integram a solicitação atual.
4. Para Destaques, usar as sete capas existentes em `01-conteudo/destaques-20261118/out` e aplicá-las somente aos Destaques correspondentes da conta `@pastorrobsonalencar`. Não publicá-las no feed ou nos Stories por engano.
5. Se não houver dispositivo Android conectado e autenticado, informar `ANDROID_NAO_CONECTADO`; não simular publicação ou contornar criando posts.
6. Não limpar cookies, sessão, mídias do aparelho, tarefas, logs ou credenciais. Não remover bloqueios existentes para forçar execução.
7. Screenshots de diagnóstico e scripts temporários devem ficar no escopo da tarefa, sem misturar com saídas finais. Não expor tokens e sessões.

## Instalação verificada no ALFA
- Playwright Skill v5.0.0: `.opencode/skills/playwright-skill`
- Executor: `node .opencode/skills/playwright-skill/run.js <script.js>`
- Biblioteca Playwright: 1.62.1; Chromium instalado, teste headless local concluído em OpenCode 1.19.4.
- Appium/Android: `04-skills/instagram-android-appium`, driver UiAutomator2, teste `highlights_preflight.py`.
- Quando a tarefa exigir seleção de ferramenta, ler somente a skill correspondente, sem carregar as duas por padrão.

## BLOQUEIO EXPLICITO: CAPAS DE DESTAQUES NAO USAM PLAYWRIGHT
- Para tarefa de aplicar, substituir ou editar capas de Destaques do Instagram, NAO abrir Playwright, Chrome nem Instagram Web procurando botao de edicao. A interface Web nao oferece esse fluxo para envio de capa personalizada.
- Usar SOMENTE automacao da interface do aplicativo Instagram em Android com Appium/UiAutomator2, se houver aparelho ou emulador Android conectado, autorizado e logado na conta certa. O repositorio de Appium instalado e uma base, nao uma rotina pronta de edicao de Destaques.
- Sem Android acessivel, registrar bloqueio concreto ANDROID_NAO_CONECTADO; nao publicar as imagens como Stories nem posts para simular resultado.
- No iPhone, Android Appium nao opera o aplicativo iOS. Nao afirmar que Playwright ou Appium Android consegue alterar as capas pelo iPhone.
