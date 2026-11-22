# Auditoria visual assinada V2: procedimento e seguranca

## Objetivo
O publicador **nao pode** considerar `aprovacao-visual.json` uma prova de revisao apenas pelo nome `auditor-deus`/`codex-visual` e pelos hashes. Agora o Python exige assinatura **Ed25519** verificavel por chave publica confiavel no ALFA.

Os validadores `02-scripts/verificar_aprovacao_visual.py`, `validar_pacote_publicacao.py` e `qa_carrossel.py` impedem publicacao ou aprovacao visual quando a assinatura V2 estiver ausente, invalida ou ligada a outro conteudo, job ou conta. O verificador nao assina e nao inventa auditoria.

## Quem assina
O **responsavel humano pela auditoria visual** examina os PNGs finais e a legenda integral e assina com senha no terminal local. A assinatura nao substitui a inspecao das imagens. O operador usa o revisor `auditor-humano` e nao falsifica a identidade dos agentes.

A chave **privada** deve permanecer criptografada em `%LOCALAPPDATA%\Instagram-Auditoria-Visual\`, fora do projeto, do GitHub, do OpenCode e dos backups compartilhados. Nao expor senha, cookies, tokens ou chave privada em chats, logs, prompts ou commits. A chave **publica** local fica em `00-regras/visual-audit-public-key.pem`; ela nunca deve ser substituida silenciosamente.

## Inicializacao pessoal unica no ALFA
Em um PowerShell aberto pela pessoa responsavel, com ambiente Windows interativo, na pasta do projeto:

```powershell
python 02-scripts/auditoria_visual_operador.py inicializar
```

O programa pede uma senha pessoal criada e digitada diretamente na maquina (minimo de 8 caracteres; recomenda-se uma senha dificil de adivinhar), confirma a senha e gera o par de chaves. Nenhuma senha precisa ser entregue ao ChatGPT ou ao GitHub. Se ja existir uma chave publica ou privada, **a inicializacao recusa sobrescreve-la**.

Nao executar `inicializar` dentro de um agente ou automacao. Antes da primeira aprovacao, conferir que o arquivo publico confiavel existe e que a chave privada esta protegida e fora do projeto.

## Revisao e assinatura de um carrossel
1. Obter os PNGs finais em `01-conteudo/<pasta>/out/slide-01.png` etc. e a legenda em `01-conteudo/<pasta>/legenda.txt`; rodar a verificacao tecnica do exportador ou `qa_carrossel.py`.
2. Usar `instagram_publicador` em `revisar` para obter o **job_id real**. Nao inventar ou reciclar o ID de outro pacote.
3. O responsavel abre **cada imagem real**, le a legenda e confere fidelidade, textos, cortes, tipografia e padrao grafico. Os scripts de QA nao equivalem a essa revisao.
4. Se houver um comprovante antigo, **arquiva-lo** antes de novo registro, sem apagar evidencias. A ferramenta recusa sobrescrever um comprovante existente.
5. No PowerShell interativo, a pessoa responsavel executa:

```powershell
python 02-scripts/auditoria_visual_operador.py aprovar --pasta "rascunhos/PASTA_DO_TRABALHO" --job-id "UUID_DA_REVISAO"
```

6. O programa mostra os caminhos de cada slide e a legenda, exige uma frase exata de aprovacao e pede a senha local diretamente no console. Somente entao assina os hashes das imagens e legenda, conta, ID do job e data. Uma senha errada nao produz recibo.
7. Refazer a verificacao local de `qa_carrossel.py` para atualizar `qa-relatorio.json` com `aprovado_visualmente`, `tipografia_confirmada` e `publicavel`. O verificador de assinatura volta a conferir os bytes na hora da tentativa de publicacao.
8. Apresentar imagens e legenda ao usuario, conferir ordem explicita e seguir `instagram_publicador: revisar -> decidir`, sem confirmacao duplicada desnecessaria. A validacao de assinatura **nao substitui autorizacao real de publicar**.

## Contrato assinado (sem dados sensiveis)
A assinatura Ed25519 cobre a representacao JSON canonica dos campos:
`version=2`, `alg=Ed25519`, `key_id`, `aprovado`, `revisor`, `job_id`, `account`, `audited_at`, `images_sha256` e `caption_sha256`, com prefixo de dominio `IG-VISUAL-AUDIT-V2` e byte NUL. O campo `signature` usa base64. A chave publica vem de arquivo local confiavel, **nunca do recibo**.

## Efeito sobre comprovantes anteriores
Comprovantes sem assinatura, inclusive os dois identificados no ALFA em 22/11/2026, ficam **inaptos**. Eles nao podem ser assinados retroativamente por IA. Exige-se revisao real do material e nova assinatura pelo responsavel.

## Testes isolados e limite
Testes de assinatura, adulteracao, alteracao de PNG/legenda, troca de job, conta e chave usam pares Ed25519 **efemeros em diretorio temporario**. Isso nao concede permissao de postagem em producao. O teste nao configura a chave legitima, nao acessa credenciais, nao registra tarefas no Windows e nao publica no Instagram. A publicacao real ainda precisa de homologacao propria.
