# Conectar um Android com depuracao sem fio sem depender do USB.
# Execute localmente no ALFA. O codigo de pareamento nao precisa ser compartilhado no chat.
$ErrorActionPreference = 'Stop'
$adbCmd = Get-Command adb -ErrorAction Stop
$adb = $adbCmd.Source
& $adb start-server | Out-Host
Write-Host ""
Write-Host "NO POCO: Opcoes do desenvolvedor > Depuracao sem fio > Parear dispositivo com codigo"
Write-Host "O ALFA e o POCO precisam estar na mesma rede Wi-Fi."
Write-Host ""
$pairEndpoint = (Read-Host "Digite IP:PORTA mostrados na tela de PAREAMENTO").Trim()
if ($pairEndpoint -notmatch '^([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}$') {
  throw "Endereco de pareamento invalido. Use o formato 192.168.1.10:37123"
}
$pairCode = (Read-Host "Digite o codigo de 6 digitos exibido no POCO").Trim()
if ($pairCode -notmatch '^\d{6}$') { throw "O codigo precisa ter 6 digitos." }
Write-Host "Pareando..."
$pairResult = & $adb pair $pairEndpoint $pairCode 2>&1
$pairCode = $null
$pairResult | Out-Host
if ($LASTEXITCODE -ne 0 -or ($pairResult -join ' ') -notmatch 'Successfully paired') {
  throw "Pareamento nao confirmado. Confira IP, porta, codigo e mesma rede Wi-Fi."
}
Write-Host ""
Write-Host "VOLTE a tela principal de Depuracao sem fio no POCO."
Write-Host "Use o IP:PORTA da secao Endereco IP e porta (normalmente porta DIFERENTE da de pareamento)."
$debugEndpoint = (Read-Host "Digite IP:PORTA de DEPURACAO SEM FIO").Trim()
if ($debugEndpoint -notmatch '^([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}$') {
  throw "Endereco de depuracao invalido."
}
& $adb connect $debugEndpoint | Out-Host
& $adb devices -l | Out-Host
$lines = & $adb devices
$needle = '^' + [regex]::Escape($debugEndpoint) + '\s+device(?:\s|$)'
if (-not ($lines | Where-Object { $_ -match $needle })) {
  throw "Android ainda nao aparece como device. Mantenha a depuracao sem fio ativa."
}
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root '.venv\Scripts\python.exe'
$inspect = Join-Path $root 'editar_capas_destaques.py'
if (Test-Path $python) {
  & $python $inspect --inspect | Out-Host
  Write-Host "Inspecao enviada. Nao houve publicacao ou troca de capas."
} else { Write-Host "Pareamento concluido; Python do Appium nao encontrado." }
