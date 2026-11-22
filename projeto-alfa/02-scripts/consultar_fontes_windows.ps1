param(
  [string]$Filtro = "",
  [switch]$Exportar
)
$ErrorActionPreference = 'Stop'
$root = 'I:\Projetos\Instagram-RobsonAlencar'
$fontDirs = @("$env:WINDIR\Fonts", "$env:LOCALAPPDATA\Microsoft\Windows\Fonts")
$registry = @('HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts','HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts')
$items = @()
foreach ($reg in $registry) {
  if (!(Test-Path -LiteralPath $reg)) { continue }
  $props = (Get-ItemProperty -LiteralPath $reg).PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' -and $_.Value -is [string] }
  foreach ($item in $props) {
    $registered = $item.Name
    $name = $registered -replace '\s*\((TrueType|OpenType|Type 1)\)$',''
    $filename = [string]$item.Value
    $fullpath = $filename
    if (![System.IO.Path]::IsPathRooted($fullpath)) {
      $fullpath = Join-Path $fontDirs[0] $filename
      if (!(Test-Path -LiteralPath $fullpath)) {
        $fullpath = Join-Path $fontDirs[1] $filename
      }
    }
    $exists = Test-Path -LiteralPath $fullpath
    $items += [PSCustomObject]@{ nome=$name; registro=$registered; arquivo=$fullpath; existe=$exists; origem=$reg }
  }
}
$items = @($items | Sort-Object nome,arquivo -Unique)
if ($Exportar) {
  $path=Join-Path $root 'debug\catalogo-fontes-windows.json'
  $items | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $path -Encoding UTF8
  Write-Output ("CATALOGO="+$path)
}
Write-Output ("FONTES_REGISTRADAS="+$items.Count)
if ($Filtro) {
  $needle=[regex]::Escape($Filtro)
  $items | Where-Object {$_.nome -match $needle} | Select-Object nome,arquivo,existe | Format-Table -Wrap -AutoSize
} else {
  $items | Where-Object {$_.nome -match '(?i)^(Acumin Pro|Anton|Barlow|Bebas|Gilroy|League Gothic|Montserrat|Poppins)' -and $_.existe} |
    Select-Object -First 30 nome,existe | Format-Table -AutoSize
}
