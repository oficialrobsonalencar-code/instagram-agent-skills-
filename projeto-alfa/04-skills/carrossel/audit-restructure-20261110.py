from pathlib import Path
from datetime import datetime
root=Path(r'I:\Projetos\Instagram-RobsonAlencar\04-skills\carrossel')
skill=root/'SKILL.md'
old=skill.read_text(encoding='utf-8-sig')
backup=root/('SKILL.md.backup-audit-20261110')
if backup.exists():
    raise SystemExit('BACKUP_ALREADY_EXISTS_ABORT')
backup.write_text(old, encoding='utf-8')
refs=root/'references'
refs.mkdir(exist_ok=True)
detail=refs/'workflow-original.md'
if detail.exists(): raise SystemExit('REFERENCE_ALREADY_EXISTS_ABORT')
detail.write_text('# Procedimento completo original (preservado)\n\n'+old.split('---',2)[2].strip()+'\n',encoding='utf-8')
front=old.split('---',2)[1]
main='''---
'''+front+'''---
# Carrossel de Instagram: execução e entrega

## Acionamento
Aplicar quando o pedido mencionar carrossel, slides Instagram, copy, capa, referências visuais, edição ou exportação de posts. Usar o projeto existente e suas imagens, sem recomeçar do zero.

## Fluxo obrigatório
1. Ler o pedido e os arquivos/referências relevantes. Não repetir perguntas já respondidas. Se a pessoa ordenou produzir, executar diretamente, sem pedir nova aprovação da copy; solicitar confirmação apenas para decisões externas irreversíveis.
2. Identificar o formato (lista, história, passos, erros, antes/depois), elaborar 6 a 10 slides; capa forte, um ponto por slide, encerramento com um CTA. Se a pessoa enviou referência, reproduzir linguagem visual e composição, com conteúdo próprio.
3. Produzir copy, HTML e imagens no mesmo projeto, preservando arquivos originais. Para detalhes de textos, estilos, resolução e critérios, ler [fluxo completo](references/workflow-original.md).
4. Usar [template HTML](templates/carrossel.html) como base e o [exportador Playwright](scripts/exportar.mjs); exportar em 1080x1350, validar capa, slide intermediário e CTA, corrigindo cortes e acentuação.
5. Ao final, informar pasta de saída, nomes dos PNGs, o que realmente foi criado e o que ainda falta. Se bloqueado, descrever o erro exato e próxima ação, sem afirmar sucesso não verificado.

## Regras de execução
- Sem arte genérica. Cada slide deve representar precisamente seu trecho da mensagem; manter uma linguagem visual consistente.
- Não inventar dados ou provas; não sobrescrever a versão existente sem backup.
- O comando de exportação, dentro da pasta de trabalho, é `node exportar.mjs carrossel.html out`. Os insumos vêm dos caminhos acima.
- Em jobs demorados, comunicar o progresso em frases objetivas. Nunca trocar de modelo, pasta, tema ou estilo silenciosamente.
- Não interpretar a pausa obrigatória do fluxo antigo como veto quando o usuário já solicitou execução.
'''
skill.write_text(main,encoding='utf-8')
print('BACKUP', backup)
print('REFERENCE',detail)
print('MAIN_CHARS',len(main))
