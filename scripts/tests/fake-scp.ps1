# Faux scp : copie le fichier source vers $env:FAKE_DIR\incoming\<lot>\<nom>, sans reseau.
$ErrorActionPreference = 'Stop'
$dir = $env:FAKE_DIR
Add-Content -LiteralPath (Join-Path $dir 'appels.log') -Value ("scp " + ($args -join ' | '))
$source = $args[-2]; $dest = $args[-1]
if ($dest -notmatch 'incoming/(\d{8}-\d{6}-[0-9a-f]{8})/(\S+)$') { Write-Error "destination inattendue : $dest"; exit 1 }
$lot = $Matches[1]; $nom = $Matches[2]
if ($env:FAKE_SCENARIO -eq 'scp_ko') { exit 1 }
$cible = Join-Path $dir "incoming\$lot"
New-Item -ItemType Directory -Force -Path $cible | Out-Null
Copy-Item -LiteralPath $source -Destination (Join-Path $cible $nom) -Force
if ($nom -eq 'lot.zip') {
    $n = Join-Path $dir "lots\$lot"; New-Item -ItemType Directory -Force -Path $n | Out-Null
    $f = Join-Path $n 'uploads'; $v = 0; if (Test-Path $f) { $v = [int](Get-Content $f -Raw) }
    Set-Content -LiteralPath $f -Value ($v + 1)
    if ($env:FAKE_SCENARIO -eq 'archive_corrompue') { Add-Content -LiteralPath (Join-Path $cible $nom) -Value 'octets en trop' }
}
exit 0
