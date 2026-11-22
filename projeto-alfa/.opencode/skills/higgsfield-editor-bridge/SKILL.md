---
name: higgsfield-editor-bridge
description: Encaminhar planejamento e validação de reels do Instagram para o Editor E sem criar design novo, publicar ou violar bloqueios.
---
# Uso em Instagram
Leia AGENTS.md, 00-regras/ e as permissões de referência do pedido atual antes de agir.
Diagnóstico: python 02-scripts/higgsfield_editor.py doctor
Plano: python 02-scripts/higgsfield_editor.py plan --intent adaptar --description "pedido de video" 
O script de integração não publica, não cria imagens ou vídeos automaticamente, não acessa a conta do Instagram e não escolhe mídia sem autorização.
Para produção já autorizada e compatível, continue usando 02-scripts/instagram_estudio.py e o motor do E: existente, após inspeção do pedido e validação da referência. Não sobrescreva o fluxo nem burle BLOQUEIO-PUBLICACAO-ATIVO.
Usar Paint a Plate apenas quando o diagnóstico confirmar instalação, GPU e workflows. Caso contrário, manter a rota do Editor existente e indicar o que falta.
Arquivo pronto: python 02-scripts/higgsfield_editor.py validate --file CAMINHO.mp4, depois 02-scripts/receber-video-editor.py para revisão. Não publicar.
