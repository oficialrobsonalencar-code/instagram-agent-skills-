$ErrorActionPreference='Stop'
$root='I:\Projetos\Instagram-RobsonAlencar'
$python=Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
$worker=Join-Path $root '02-scripts\atualizar_grafo_instagram.py'
$log=Join-Path $root '03-agendamentos\grafo-atualizacao.log'
if(!(Test-Path $root)){exit 0}  # I: pode estar desconectado
if(!(Test-Path $worker)){exit 2}
if((Test-Path $log) -and (Get-Item $log).Length -gt 262144){
 $backup=Join-Path (Split-Path $log -Parent) 'grafo-atualizacao-anterior.log'
 Move-Item $log $backup -Force
}
"[$(Get-Date -Format o)] Inicio" | Out-File -Append -Encoding utf8 -LiteralPath $log
& $python -u $worker *>> $log
$rc=$LASTEXITCODE
"[$(Get-Date -Format o)] Exit=$rc" | Out-File -Append -Encoding utf8 -LiteralPath $log
exit $rc
