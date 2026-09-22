<#
Filet de securite local en attendant un vrai hebergement cloud (voir
docker/backup/backup.sh pour la version definitive prevue pour la production -
dump + upload DigitalOcean Spaces + retention par cycle de vie sur le bucket).
Ce script ne la remplace pas : il comble juste l'absence totale de sauvegarde
pendant le developpement local, sur le disque de cette machine uniquement -
donc pas de protection si le disque meurt, ce qui reste le vrai risque tant
que le stockage distant n'est pas branche.

pg_dump tourne DANS le conteneur "db" (m'eme version que le serveur, jamais un
client local potentiellement desynchronise) puis le fichier est recupere via
"docker compose cp", pas une redirection de flux via un pipeline PowerShell -
un pipe binaire vers Set-Content/Out-File corrompt le format custom de
pg_dump (conversion d'encodage implicite), "docker compose cp" ne touche pas
aux octets.
#>

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackupDir = Join-Path $RepoRoot "backups\postgres"
$LogFile = Join-Path $BackupDir "backup.log"
$RetentionDays = 14

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Output $line
    Add-Content -Path $LogFile -Value $line
}

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DumpName = "edukora_$Timestamp.dump"
$RemotePath = "/tmp/$DumpName"
$LocalPath = Join-Path $BackupDir $DumpName

Push-Location $RepoRoot
try {
    Write-Log "Debut sauvegarde -> $DumpName"

    docker compose exec -T db sh -c "pg_dump -U `"`$POSTGRES_USER`" -d `"`$POSTGRES_DB`" --format=custom --compress=5 --no-owner --no-privileges -f $RemotePath"
    if ($LASTEXITCODE -ne 0) { throw "pg_dump a echoue (code $LASTEXITCODE)" }

    docker compose cp "db:${RemotePath}" $LocalPath
    if ($LASTEXITCODE -ne 0) { throw "docker compose cp a echoue (code $LASTEXITCODE)" }

    docker compose exec -T db rm -f $RemotePath

    $size = (Get-Item $LocalPath).Length
    if ($size -lt 1000) {
        throw "Dump suspicieusement petit ($size octets) - abandonne, fichier local supprime"
    }
    Write-Log ("Sauvegarde OK : {0} ({1:N1} Mo)" -f $DumpName, ($size / 1MB))

    $seuil = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem -Path $BackupDir -Filter "edukora_*.dump" |
        Where-Object { $_.LastWriteTime -lt $seuil } |
        ForEach-Object {
            Write-Log "Retention : suppression de $($_.Name) (> $RetentionDays j)"
            Remove-Item $_.FullName -Force
        }
}
catch {
    Write-Log "ERREUR : $_"
    if (Test-Path $LocalPath) { Remove-Item $LocalPath -Force -ErrorAction SilentlyContinue }
    throw
}
finally {
    Pop-Location
}
