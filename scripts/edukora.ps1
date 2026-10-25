<#
.SYNOPSIS
  Chaine de synchronisation des contenus EduKora, cote poste Windows (phase 3 : outillage local).

.DESCRIPTION
  Orchestre, sans les dupliquer, les outils existants (scripts/ingerer_et_valider.sh,
  scripts/tunnel_validation.sh, commandes Django du conteneur) et l'outil Python
  backend/synchro/outil_lot.py. Voir deploy/SPEC-SYNC-CONTENU.md.

  Commandes de cette phase (le transfert et la publication en production arrivent en phase 5) :
    doctor        verifie les prerequis (lecture seule)
    generate      rappelle comment produire les contenus (aucune generation automatique)
    validate      controles statiques d'unites (JSON, identifiants, fichiers declares)
    ingest-local  ingere en local + tunnel de validation, puis enregistre la validation
    inventaire    liste les JSON ingerables non suivis par git (ignores) pour validation
    prepare       construit un lot (dossier + archive + SHA-256) apres controles
    status        liste les lots locaux
    doctor -Distant   verifie le serveur (SSH, docker, flock, dossier des lots, commande sync_contenu)
    reference     recupere les empreintes appliquees en production (pour prepare -Reference)
    publish       envoie, verifie et SIMULE un lot sur le serveur ; avec -Appliquer, sauvegarde puis applique
    resume        reprend le suivi d'un lot (jamais de relance a l'aveugle apres une coupure)
    resoudre      ecrit des decisions humaines (garder_prod | ecraser | recreer) dans un lot
    rollback-info affiche la procedure de retour arriere d'un lot (aucune action)

  Une UNITE est un dossier d'epreuve ("cm/bac-c-maths-1984-cameroun") ou un fichier de quiz
  ("_quiz/cm/derivee-bac-cdeti.json"), relatif a backend/ingest/.

  Codes de sortie : 0 succes - 1 echec certain - 2 usage/prerequis - 3 indetermine (verifier avec
  resume) - 4 conflits ou contenus non appliques - 5 validation humaine ou approbation manquante.

.EXAMPLE
  .\scripts\edukora.ps1 doctor
  .\scripts\edukora.ps1 ingest-local -Unite cm/bac-c-maths-1984-cameroun
  .\scripts\edukora.ps1 prepare -Unite cm/bac-c-maths-1984-cameroun -Nom correction-maths
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('', 'help', 'doctor', 'generate', 'validate', 'ingest-local', 'inventaire', 'prepare', 'status', 'publish', 'resume', 'resoudre', 'reference', 'rollback-info')]
    [string]$Commande = '',

    [string[]]$Unite = @(),
    [string]$Liste,
    [string]$Nom,
    [string]$Reference,
    [string]$Retraits,
    [string]$BatchId,
    [string]$Config,
    [switch]$Approuver,
    [switch]$AccepterSansTunnel,
    [switch]$ToutOuRien,
    [switch]$Adopter,
    [switch]$Strict,
    [string]$Decision,
    [string[]]$Ids = @(),
    [string]$Motif,
    [switch]$Appliquer,
    [switch]$Reprendre,
    [switch]$SansPostTraitement,
    [switch]$ConfirmerRetraits,
    [switch]$Distant,
    [switch]$SansBase,
    [switch]$Rapide
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$script:EXIT_OK = 0
$script:EXIT_ECHEC = 1
$script:EXIT_USAGE = 2
$script:EXIT_INDETERMINE = 3
$script:EXIT_CONFLITS = 4
$script:EXIT_APPROBATION = 5

try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }
$script:Racine = Split-Path -Parent $PSScriptRoot
$script:Outil = Join-Path $script:Racine 'backend\synchro\outil_lot.py'

# --------------------------------------------------------------------------- configuration

function Get-ConfigParDefaut {
    return @{
        Python           = ''
        GitBash          = 'C:\Program Files\Git\bin\bash.exe'
        Conteneur        = 'edukora-backend-1'
        IngestDir        = (Join-Path $script:Racine 'backend\ingest')
        BatchesDir       = (Join-Path $script:Racine 'batches')
        # Parametres de publication (phase 5) : lus et verifies par doctor, inutiles avant.
        Hote             = ''
        Utilisateur      = 'deploy'
        Port             = 22
        CleSsh           = ''
        KnownHosts       = ''
        CheminServeur    = '/srv/edukora'
        DossierLotsServeur = '/srv/edukora-lots'
        ScriptServeur    = ''
        SshExe           = 'ssh'
        ScpExe           = 'scp'
        DelaiSondageSecondes = 5
        DelaiMaxLotSecondes  = 7200
        ToleranceReseau  = 8
    }
}

function Read-Config {
    param([string]$Chemin)
    $cfg = Get-ConfigParDefaut
    if (-not $Chemin) { $Chemin = Join-Path $PSScriptRoot 'edukora.config.psd1' }
    $cfg['_Source'] = ''
    if (Test-Path -LiteralPath $Chemin) {
        $lu = Import-PowerShellDataFile -LiteralPath $Chemin
        foreach ($cle in $lu.Keys) { $cfg[$cle] = $lu[$cle] }
        $cfg['_Source'] = $Chemin
    }
    return $cfg
}

function Find-Python {
    param($Cfg)
    $candidats = @()
    if ($Cfg.Python) { $candidats += $Cfg.Python }
    $candidats += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python314\python.exe')
    $candidats += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe')
    $candidats += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe')
    foreach ($c in $candidats) {
        if ($c -and (Test-Path -LiteralPath $c)) { return $c }
    }
    # Le "python" nu est souvent le stub du Microsoft Store : on ne le retient que s'il repond.
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch 'WindowsApps') { return $cmd.Source }
    return $null
}

# --------------------------------------------------------------------------- utilitaires

function ConvertTo-ArgString {
    param([string[]]$Arguments)
    $parts = foreach ($a in $Arguments) {
        if ($null -eq $a) { $a = '' }
        if ($a -eq '' -or $a -match '[\s"]') { '"' + ($a -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"' } else { $a }
    }
    return ($parts -join ' ')
}

function Invoke-Native {
    <# Lance un programme et capture stdout et stderr separement, sans les melanger. #>
    param([string]$Fichier, [string[]]$Arguments = @(), [string]$Entree)
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Fichier
    $psi.Arguments = ConvertTo-ArgString $Arguments
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.RedirectStandardInput = ($PSBoundParameters.ContainsKey('Entree'))
    $psi.CreateNoWindow = $true
    $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
    $psi.EnvironmentVariables['PYTHONUTF8'] = '1'
    $p = [System.Diagnostics.Process]::Start($psi)
    if ($psi.RedirectStandardInput) {
        # Octets bruts : StandardInput.Write() emet un BOM UTF-8 que Python lit comme un caractere invalide.
        $octets = (New-Object System.Text.UTF8Encoding($false)).GetBytes($Entree)
        $p.StandardInput.BaseStream.Write($octets, 0, $octets.Length)
        $p.StandardInput.Close()
    }
    # Lecture asynchrone de stderr pour eviter tout blocage si un tampon se remplit.
    $errTask = $p.StandardError.ReadToEndAsync()
    $out = $p.StandardOutput.ReadToEnd()
    $p.WaitForExit()
    return [pscustomobject]@{ Code = $p.ExitCode; Out = $out; Err = $errTask.Result }
}

function Write-JsonFile {
    param([string]$Chemin, $Objet)
    $dir = Split-Path -Parent $Chemin
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $texte = ($Objet | ConvertTo-Json -Depth 20)
    # UTF-8 SANS BOM : Set-Content -Encoding UTF8 ajouterait un BOM (PowerShell 5.1).
    [System.IO.File]::WriteAllText($Chemin, $texte, (New-Object System.Text.UTF8Encoding($false)))
}

function Read-JsonFile {
    param([string]$Chemin)
    return (Get-Content -LiteralPath $Chemin -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Get-SlugUnite { param([string]$U) return ($U -replace '/', '__') }

function Get-DossiersEtat {
    param($Cfg)
    $b = $Cfg.BatchesDir
    return @{
        Validations = (Join-Path $b '_validations')
        Rapports    = (Join-Path $b '_rapports')
        Inventaire  = (Join-Path $b '_inventaire')
    }
}

function Invoke-Outil {
    <# Appelle backend/synchro/outil_lot.py ; retourne Code, Json (resume) et les flux bruts. #>
    param($Cfg, [string[]]$Arguments)
    $py = Find-Python $Cfg
    if (-not $py) { throw 'Python introuvable (renseigner Python dans scripts/edukora.config.psd1).' }
    $r = Invoke-Native -Fichier $py -Arguments (@('-I', $script:Outil) + $Arguments)
    $json = $null
    $texte = if ($r.Out.Trim()) { $r.Out } else { $r.Err }
    $texte = $texte.Trim()
    if ($texte.StartsWith('{')) { try { $json = $texte | ConvertFrom-Json } catch { $json = $null } }
    return [pscustomobject]@{ Code = $r.Code; Json = $json; Out = $r.Out; Err = $r.Err }
}

function ConvertTo-GitBashPath {
    param([string]$Chemin)
    $full = [System.IO.Path]::GetFullPath($Chemin)
    $lecteur = $full.Substring(0, 1).ToLower()
    return '/' + $lecteur + $full.Substring(2).Replace('\', '/')
}

function Invoke-GitBash {
    <# Execute une commande Git Bash en affichant et capturant stdout+stderr fusionnes (2>&1 cote bash). #>
    param($Cfg, [string]$Commande, [hashtable]$Env = @{})
    foreach ($k in $Env.Keys) { Set-Item -Path "Env:$k" -Value $Env[$k] }
    try {
        $lignes = @(& $Cfg.GitBash -c "( $Commande ) 2>&1" | ForEach-Object { Write-Host $_; $_ })
        $code = $LASTEXITCODE
    }
    finally {
        foreach ($k in $Env.Keys) { Remove-Item -Path "Env:$k" -ErrorAction SilentlyContinue }
    }
    return [pscustomobject]@{ Code = $code; Lignes = $lignes; Texte = ($lignes -join "`n") }
}

function Get-Unites {
    <# Fusionne -Unite et -Liste (une unite par ligne, # commentaire) ; dedoublonne. #>
    param([string[]]$Unite, [string]$Liste)
    $tout = @()
    foreach ($u in $Unite) { if ($u) { $tout += ($u -replace '\\', '/').Trim('/') } }
    if ($Liste) {
        if (-not (Test-Path -LiteralPath $Liste)) { throw "Liste introuvable : $Liste" }
        foreach ($l in (Get-Content -LiteralPath $Liste -Encoding UTF8)) {
            $t = $l.Trim()
            if ($t -and -not $t.StartsWith('#')) { $tout += ($t -replace '\\', '/').Trim('/') }
        }
    }
    return @($tout | Select-Object -Unique)
}

function Test-Interactif { return ([Environment]::UserInteractive -and -not [Console]::IsInputRedirected) }

function Get-ApprobateurParDefaut { return "$($env:USERNAME)@$($env:COMPUTERNAME)" }

# --------------------------------------------------------------------------- doctor

function New-Verification {
    param([string]$Nom, [ValidateSet('ok', 'avertissement', 'erreur')][string]$Statut, [string]$Detail)
    return [pscustomobject]@{ Verification = $Nom; Statut = $Statut; Detail = $Detail }
}

function Get-Verifications {
    param($Cfg, [switch]$Rapide)
    $v = New-Object System.Collections.ArrayList
    function Add-V { param($x) [void]$v.Add($x) }

    Add-V (New-Verification 'PowerShell' $(if ($PSVersionTable.PSVersion.Major -ge 5) { 'ok' } else { 'erreur' }) $PSVersionTable.PSVersion.ToString())
    Add-V (New-Verification 'Configuration' $(if ($Cfg._Source) { 'ok' } else { 'avertissement' }) $(if ($Cfg._Source) { $Cfg._Source } else { 'aucun scripts/edukora.config.psd1 (valeurs par defaut)' }))

    $py = Find-Python $Cfg
    if ($py) {
        $ver = (Invoke-Native -Fichier $py -Arguments @('--version')).Out.Trim()
        Add-V (New-Verification 'Python' 'ok' "$py ($ver)")
        $t = Invoke-Native -Fichier $py -Arguments @('-I', $script:Outil, 'controler', '--help')
        Add-V (New-Verification 'Outil de lot' $(if ($t.Code -eq 0) { 'ok' } else { 'erreur' }) $script:Outil)
    }
    else {
        Add-V (New-Verification 'Python' 'erreur' 'introuvable (le python nu est le stub du Microsoft Store)')
    }

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        $sales = @(& git -C $script:Racine status --porcelain --untracked-files=no 2>$null).Count
        Add-V (New-Verification 'Git' 'ok' "$($git.Source) ; $sales fichier(s) suivi(s) modifie(s)")
        if ($sales -gt 0) { Add-V (New-Verification 'Arbre git' 'avertissement' "$sales fichier(s) suivi(s) modifie(s) : sans effet sur un lot (les lots viennent de backend/ingest), mais verifier avant un deploiement") }
    }
    else { Add-V (New-Verification 'Git' 'erreur' 'git introuvable') }

    Add-V (New-Verification 'Git Bash' $(if (Test-Path -LiteralPath $Cfg.GitBash) { 'ok' } else { 'erreur' }) "$($Cfg.GitBash) (le bash du PATH est WSL : ne pas l'utiliser)")
    Add-V (New-Verification 'Dossier ingest' $(if (Test-Path -LiteralPath $Cfg.IngestDir) { 'ok' } else { 'erreur' }) $Cfg.IngestDir)

    if (-not $Rapide) {
        $dk = Get-Command docker -ErrorAction SilentlyContinue
        if ($dk) {
            $etat = Invoke-Native -Fichier $dk.Source -Arguments @('ps', '--filter', "name=$($Cfg.Conteneur)", '--format', '{{.Names}} {{.Status}}')
            if ($etat.Code -ne 0) { Add-V (New-Verification 'Docker' 'erreur' "demon injoignable : $($etat.Err.Trim())") }
            elseif ($etat.Out.Trim()) {
                Add-V (New-Verification 'Conteneur backend' 'ok' $etat.Out.Trim())
                $chk = Invoke-Native -Fichier $dk.Source -Arguments @('exec', $Cfg.Conteneur, 'python', 'manage.py', 'check', '--database', 'default')
                Add-V (New-Verification 'Django + base locale' $(if ($chk.Code -eq 0) { 'ok' } else { 'erreur' }) $(if ($chk.Code -eq 0) { 'manage.py check --database default' } else { ($chk.Err + $chk.Out).Trim() }))
            }
            else { Add-V (New-Verification 'Conteneur backend' 'erreur' "$($Cfg.Conteneur) ne tourne pas (docker compose up -d db backend)") }
        }
        else { Add-V (New-Verification 'Docker' 'erreur' 'docker introuvable') }
    }

    try {
        New-Item -ItemType Directory -Force -Path $Cfg.BatchesDir | Out-Null
        $lecteur = (Get-Item -LiteralPath $Cfg.BatchesDir).PSDrive
        $libreGo = [math]::Round($lecteur.Free / 1GB, 1)
        Add-V (New-Verification 'Espace disque' $(if ($libreGo -ge 2) { 'ok' } else { 'erreur' }) "$libreGo Go libres sur $($lecteur.Name): (minimum 2 Go)")
    }
    catch { Add-V (New-Verification 'Dossier des lots' 'erreur' $_.Exception.Message) }

    $ign = & git -C $script:Racine check-ignore -q 'batches/x' 2>$null; $batchesIgnore = ($LASTEXITCODE -eq 0)
    & git -C $script:Racine check-ignore -q 'scripts/edukora.config.psd1' 2>$null; $cfgIgnore = ($LASTEXITCODE -eq 0)
    Add-V (New-Verification 'Ignore git (batches, config)' $(if ($batchesIgnore -and $cfgIgnore) { 'ok' } else { 'erreur' }) $(if ($batchesIgnore -and $cfgIgnore) { 'batches/ et edukora.config.psd1 sont ignores' } else { 'ajouter batches/ et scripts/edukora.config.psd1 a .gitignore (risque de secret committe)' }))

    # Publication (phase 5) : seulement des avertissements tant que rien n'est configure.
    foreach ($p in @(
            @{ N = 'ssh'; C = 'ssh' }, @{ N = 'scp'; C = 'scp' })) {
        $ok = [bool](Get-Command $p.C -ErrorAction SilentlyContinue)
        Add-V (New-Verification "OpenSSH ($($p.N))" $(if ($ok) { 'ok' } else { 'avertissement' }) $(if ($ok) { (Get-Command $p.C).Source } else { 'absent (necessaire a la publication, phase 5)' }))
    }
    Add-V (New-Verification 'Serveur (hote/utilisateur)' $(if ($Cfg.Hote -and $Cfg.Utilisateur) { 'ok' } else { 'avertissement' }) $(if ($Cfg.Hote) { "$($Cfg.Utilisateur)@$($Cfg.Hote):$($Cfg.Port)" } else { 'non configure (phase 5)' }))
    $cleOk = $Cfg.CleSsh -and (Test-Path -LiteralPath $Cfg.CleSsh)
    Add-V (New-Verification 'Cle SSH dediee' $(if ($cleOk) { 'ok' } else { 'avertissement' }) $(if ($Cfg.CleSsh) { $Cfg.CleSsh } else { 'non configuree (phase 5)' }))
    $khOk = $Cfg.KnownHosts -and (Test-Path -LiteralPath $Cfg.KnownHosts)
    Add-V (New-Verification 'known_hosts dedie' $(if ($khOk) { 'ok' } else { 'avertissement' }) $(if ($Cfg.KnownHosts) { $Cfg.KnownHosts } else { 'non configure (empreinte d''hote non epinglee)' }))
    return , $v
}

function Invoke-Doctor {
    param($Cfg, [switch]$Rapide)
    $res = Get-Verifications -Cfg $Cfg -Rapide:$Rapide
    foreach ($r in $res) {
        $couleur = switch ($r.Statut) { 'ok' { 'Green' } 'avertissement' { 'Yellow' } default { 'Red' } }
        Write-Host ('[{0,-13}] {1} : {2}' -f $r.Statut, $r.Verification, $r.Detail) -ForegroundColor $couleur
    }
    $nbErr = @($res | Where-Object { $_.Statut -eq 'erreur' }).Count
    $nbAv = @($res | Where-Object { $_.Statut -eq 'avertissement' }).Count
    Write-Host ''
    if ($nbErr -gt 0) { Write-Host "doctor : $nbErr erreur(s), $nbAv avertissement(s) - prerequis non satisfaits." -ForegroundColor Red; return $script:EXIT_USAGE }
    Write-Host "doctor : prerequis satisfaits ($nbAv avertissement(s))." -ForegroundColor Green
    return $script:EXIT_OK
}

# --------------------------------------------------------------------------- validate / ingest-local

function Invoke-Validate {
    param($Cfg, [string[]]$Unites)
    if ($Unites.Count -eq 0) { Write-Host 'validate : indiquer -Unite ou -Liste.'; return $script:EXIT_USAGE }
    $etat = Get-DossiersEtat $Cfg
    New-Item -ItemType Directory -Force -Path $etat.Rapports | Out-Null
    $rapport = Join-Path $etat.Rapports ("controle-{0:yyyyMMdd-HHmmss}.json" -f (Get-Date))
    $r = Invoke-Outil $Cfg (@('controler', $Cfg.IngestDir, '--sortie', $rapport) + $Unites)
    if ($null -eq $r.Json) { Write-Host "validate : sortie inattendue de l'outil.`n$($r.Err)"; return $script:EXIT_ECHEC }
    Write-Host ("validate : {0} unite(s), {1} element(s), {2} erreur(s). Rapport : {3}" -f $r.Json.unites, $r.Json.elements, $r.Json.erreurs, $rapport)
    if ($r.Json.erreurs -gt 0) {
        foreach ($u in (Read-JsonFile $rapport)) { foreach ($e in $u.erreurs) { Write-Host "  ERREUR $e" -ForegroundColor Red } }
        return $script:EXIT_ECHEC
    }
    return $script:EXIT_OK
}

function Save-Validation {
    param($Cfg, [string]$U, [string]$Locale, [string]$Tunnel, [string]$Resume)
    $etat = Get-DossiersEtat $Cfg
    # Empreinte calculee APRES l'ingestion : elle reecrit parfois les JSON (themes proposes).
    $e = Invoke-Outil $Cfg @('empreinte', $Cfg.IngestDir, $U)
    $emp = if ($e.Json) { $e.Json.empreinte_unite } else { '' }
    $enr = [ordered]@{
        unite = $U; empreinte_unite = $emp; locale = $Locale; tunnel = $Tunnel
        horodatage = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'); resume = $Resume
    }
    Write-JsonFile (Join-Path $etat.Validations ((Get-SlugUnite $U) + '.json')) $enr
}

function Invoke-IngestLocal {
    param($Cfg, [string[]]$Unites, [switch]$Strict)
    if ($Unites.Count -eq 0) { Write-Host 'ingest-local : indiquer -Unite ou -Liste.'; return $script:EXIT_USAGE }
    $code = Invoke-Validate -Cfg $Cfg -Unites $Unites
    if ($code -ne 0) { Write-Host 'ingest-local : controles statiques en echec, rien n''est ingere.' -ForegroundColor Red; return $code }

    $racineGb = ConvertTo-GitBashPath $script:Racine
    $strictArg = if ($Strict) { ' --strict' } else { '' }
    $echecs = 0
    foreach ($u in $Unites) {
        Write-Host "=== ingest-local : $u ===" -ForegroundColor Cyan
        $env_ = @{ MSYS_NO_PATHCONV = '1'; SANS_INDEX_RECHERCHE = '1'; SANS_FREQUENCES_COURS = '1' }
        if ($u.StartsWith('_quiz/')) {
            $cmd = "DEPART=`$(docker exec $($Cfg.Conteneur) date -u -d '1 minute ago' +%Y-%m-%dT%H:%M:%S+00:00) && " +
            "docker exec $($Cfg.Conteneur) python manage.py ingest_quiz_content /app/ingest/$u 2>&1 | grep -Ev '^\([0-9.]+\) ' | tee /tmp/edukora_ingest_quiz.log && " +
            "! grep -qE 'erreur\(s\) :|CommandError|Traceback' /tmp/edukora_ingest_quiz.log && " +
            "bash $racineGb/scripts/tunnel_validation.sh `"`$DEPART`"$strictArg"
        }
        else {
            $cmd = "bash $racineGb/scripts/ingerer_et_valider.sh $u$strictArg"
        }
        $r = Invoke-GitBash -Cfg $Cfg -Commande $cmd -Env $env_
        $t = $r.Texte
        if ($r.Code -ne 0 -or $t -match 'TUNNEL NON VALID' -or $t -match 'INGESTION EN ERREUR') {
            Save-Validation $Cfg $u 'echec' 'echec' "code $($r.Code)"
            Write-Host "ingest-local : ECHEC sur $u (code $($r.Code))." -ForegroundColor Red
            $echecs++
        }
        elseif ($t -match 'TUNNEL VALID') {
            Save-Validation $Cfg $u 'ok' 'valide' 'ingestion + tunnel valides'
            Write-Host "ingest-local : $u valide." -ForegroundColor Green
        }
        elseif ($t -match 'Rien de nouveau') {
            Save-Validation $Cfg $u 'ok' 'non_rejoue' 'deja en base locale : tunnel non rejoue'
            Write-Host "ingest-local : $u etait deja en base ; tunnel non rejoue (statut non_rejoue)." -ForegroundColor Yellow
        }
        else {
            Save-Validation $Cfg $u 'echec' 'echec' 'sortie non reconnue'
            Write-Host "ingest-local : sortie non reconnue pour $u : traiter comme un echec." -ForegroundColor Red
            $echecs++
        }
    }
    # Index de recherche et frequences : une seule fois pour toute la serie (voir ingerer_et_valider.sh).
    Write-Host '=== recherche globale + frequences de cours ===' -ForegroundColor Cyan
    # Le conteneur logge chaque requete SQL sur stderr en DEBUG : 2>&1 AVANT le grep, sinon il inonde la sortie.
    $filtre = "2>&1 | grep -Ev '^\([0-9.]+\) ' | tail -n 3"
    $null = Invoke-GitBash -Cfg $Cfg -Env @{ MSYS_NO_PATHCONV = '1' } -Commande "docker exec $($Cfg.Conteneur) python manage.py indexer_recherche $filtre ; docker exec $($Cfg.Conteneur) python manage.py calculer_frequences_cours $filtre"
    if ($echecs -gt 0) { return $script:EXIT_ECHEC }
    return $script:EXIT_OK
}

# --------------------------------------------------------------------------- inventaire

$script:SnippetBase = @'
import json
from catalog.models import Exercise, Cours
from quiz.models import CompetenceItem
ex = ["%s|%s" % (r["lesson__epreuve_source"], r["numero_exercice"]) for r in Exercise.objects.values("lesson__epreuve_source", "numero_exercice")]
co = list(Cours.objects.exclude(external_id="").values_list("external_id", flat=True))
it = list(CompetenceItem.objects.exclude(external_id="").values_list("external_id", flat=True))
with open("/tmp/base_sync.json", "w", encoding="utf-8") as f:
    json.dump({"exercices": ex, "cours": co, "items": it}, f)
print("EXPORT_OK", len(ex), len(co), len(it))
'@

function Export-BaseLocale {
    param($Cfg, [string]$Destination)
    $dk = (Get-Command docker -ErrorAction Stop).Source
    # Pas de stdin : le flux d'entree d'un processus .NET Framework emet un BOM que Python refuse.
    # Le script passe par un fichier temporaire (ASCII, sans BOM) copie dans le conteneur.
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) 'edukora_export_base.py'
    [System.IO.File]::WriteAllText($tmp, $script:SnippetBase, (New-Object System.Text.UTF8Encoding($false)))
    $c1 = Invoke-Native -Fichier $dk -Arguments @('cp', $tmp, "$($Cfg.Conteneur):/tmp/edukora_export_base.py")
    if ($c1.Code -ne 0) { throw "docker cp (script) en echec : $($c1.Err.Trim())" }
    $r = Invoke-Native -Fichier $dk -Arguments @('exec', $Cfg.Conteneur, 'python', 'manage.py', 'shell', '-c', "exec(open('/tmp/edukora_export_base.py').read())")
    Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue
    if ($r.Out -notmatch 'EXPORT_OK') { throw "Export de la base locale en echec : $($r.Err.Trim()) $($r.Out.Trim())" }
    $cp = Invoke-Native -Fichier $dk -Arguments @('cp', "$($Cfg.Conteneur):/tmp/base_sync.json", $Destination)
    if ($cp.Code -ne 0) { throw "docker cp en echec : $($cp.Err.Trim())" }
}

function Invoke-Inventaire {
    param($Cfg, [switch]$SansBase)
    $etat = Get-DossiersEtat $Cfg
    New-Item -ItemType Directory -Force -Path $etat.Inventaire | Out-Null
    $argv = @('inventaire', $script:Racine, '--sortie', $etat.Inventaire)
    if (-not $SansBase) {
        $base = Join-Path $etat.Inventaire 'base-locale.json'
        try { Export-BaseLocale -Cfg $Cfg -Destination $base; $argv += @('--base', $base) }
        catch { Write-Host "inventaire : base locale indisponible ($($_.Exception.Message)). Relancer avec -SansBase pour une liste sans comparaison." -ForegroundColor Red; return $script:EXIT_USAGE }
    }
    $r = Invoke-Outil $Cfg $argv
    if ($null -eq $r.Json -or $r.Code -ne 0) { Write-Host "inventaire en echec : $($r.Err)"; return $script:EXIT_ECHEC }
    $j = $r.Json
    Write-Host ("inventaire : {0} unite(s) avec des JSON non suivis par git, {1} JSON non suivis." -f $j.totaux.unites_avec_non_suivis, $j.totaux.json_non_suivis)
    $j.par_statut.PSObject.Properties | ForEach-Object { Write-Host ("  {0,-26} {1}" -f $_.Name, $_.Value) }
    Write-Host ("  fichiers suivis mais modifies (candidats a correction) : {0}" -f $j.modifies_suivis)
    Write-Host "Resultats : $($j.sortie)\inventaire.json et inventaire-unites.tsv"
    return $script:EXIT_OK
}

# --------------------------------------------------------------------------- prepare

function Invoke-Prepare {
    param($Cfg, [string[]]$Unites, [string]$Nom, [string]$Reference, [string]$Retraits, [switch]$Approuver,
        [switch]$AccepterSansTunnel, [switch]$ToutOuRien, [switch]$Adopter)
    if ($Unites.Count -eq 0) { Write-Host 'prepare : indiquer -Unite ou -Liste.'; return $script:EXIT_USAGE }
    $etat = Get-DossiersEtat $Cfg
    $lots = $Cfg.BatchesDir
    New-Item -ItemType Directory -Force -Path $lots | Out-Null
    $liste = Join-Path $etat.Rapports ('unites-{0:yyyyMMdd-HHmmss}.txt' -f (Get-Date))
    New-Item -ItemType Directory -Force -Path $etat.Rapports | Out-Null
    [System.IO.File]::WriteAllLines($liste, $Unites, (New-Object System.Text.UTF8Encoding($false)))

    $argv = @('preparer', '--ingest', $Cfg.IngestDir, '--lots', $lots, '--validations', $etat.Validations, '--liste', $liste, '--machine', $env:COMPUTERNAME)
    if ($Nom) { $argv += @('--nom', $Nom) }
    if ($Reference) { $argv += @('--reference', $Reference) }
    if ($Retraits) { $argv += @('--retraits', $Retraits) }
    if ($AccepterSansTunnel) { $argv += '--accepter-sans-tunnel' }
    if ($ToutOuRien) { $argv += '--tout-ou-rien' }
    if ($Adopter) { $argv += '--adopter' }

    $essai = Invoke-Outil $Cfg $argv
    if ($essai.Code -eq 1) {
        Write-Host 'prepare : REFUSE.' -ForegroundColor Red
        if ($essai.Json -and $essai.Json.erreurs) { foreach ($e in $essai.Json.erreurs) { Write-Host "  - $e" -ForegroundColor Red } } else { Write-Host $essai.Err }
        return $script:EXIT_ECHEC
    }
    if ($essai.Code -eq 2 -or $null -eq $essai.Json) { Write-Host "prepare : usage ou sortie inattendue.`n$($essai.Err)"; return $script:EXIT_USAGE }
    $j = $essai.Json
    Write-Host ("prepare : {0} unite(s), {1} element(s)." -f $j.unites, $j.elements)
    $j.operations.PSObject.Properties | ForEach-Object { Write-Host ("  {0,-10} {1}" -f $_.Name, $_.Value) }
    if ($j.reference_absente) { Write-Host '  ATTENTION : aucune reference de production fournie (-Reference) : classement provisoire, le serveur reclassera.' -ForegroundColor Yellow }
    foreach ($a in $j.avertissements) { Write-Host "  avertissement : $a" -ForegroundColor Yellow }

    if ($j.statut -eq 'rien_a_publier') { Write-Host 'prepare : rien a publier (tout est inchange).' -ForegroundColor Green; return $script:EXIT_OK }

    if (-not $Approuver) {
        if (Test-Interactif) {
            $rep = Read-Host 'Approuver ce lot pour publication ? (tapez oui)'
            if ($rep -ne 'oui') { Write-Host 'prepare : lot non approuve, rien n''est ecrit.'; return $script:EXIT_APPROBATION }
        }
        else { Write-Host 'prepare : approbation requise (relancer avec -Approuver), rien n''est ecrit.'; return $script:EXIT_APPROBATION }
    }
    $final = Invoke-Outil $Cfg ($argv + @('--approuve-par', (Get-ApprobateurParDefaut)))
    if ($final.Code -ne 0 -or $null -eq $final.Json -or $final.Json.statut -ne 'pret') {
        Write-Host "prepare : echec a la construction du lot.`n$($final.Out)$($final.Err)" -ForegroundColor Red
        return $script:EXIT_ECHEC
    }
    $f = $final.Json
    Write-JsonFile (Join-Path $f.dossier 'etat.json') ([ordered]@{
            batch_id = $f.batch_id; etat = 'pret_local'; archive = $f.archive; sha256_archive = $f.sha256_archive
            approuve_par = (Get-ApprobateurParDefaut); le = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        })
    Write-Host "prepare : lot $($f.batch_id) pret." -ForegroundColor Green
    Write-Host "  archive : $($f.archive)"
    Write-Host "  sha256  : $($f.sha256_archive)"
    Write-Host '  (la publication en production arrive en phase 5)'
    return $script:EXIT_OK
}

# --------------------------------------------------------------------------- status / generate / help

function Get-LotsLocaux {
    param($Cfg)
    if (-not (Test-Path -LiteralPath $Cfg.BatchesDir)) { return @() }
    $res = @()
    foreach ($d in (Get-ChildItem -LiteralPath $Cfg.BatchesDir -Directory | Where-Object { $_.Name -notlike '_*' } | Sort-Object Name)) {
        $f = Join-Path $d.FullName 'etat.json'
        $etat = if (Test-Path -LiteralPath $f) { (Read-JsonFile $f).etat } else { 'inconnu' }
        $zip = Join-Path $Cfg.BatchesDir ("lot-{0}.zip" -f $d.Name)
        $res += [pscustomobject]@{ BatchId = $d.Name; Etat = $etat; Archive = (Test-Path -LiteralPath $zip) }
    }
    return $res
}

function Invoke-Status {
    param($Cfg, [string]$BatchId)
    $lots = @(Get-LotsLocaux $Cfg)
    if ($BatchId) {
        $lot = $lots | Where-Object { $_.BatchId -eq $BatchId }
        if (-not $lot) { Write-Host "status : lot $BatchId introuvable localement."; return $script:EXIT_ECHEC }
        $m = Read-JsonFile (Join-Path $Cfg.BatchesDir "$BatchId\manifest.json")
        $ops = $m.contenus | Group-Object operation | ForEach-Object { "$($_.Name)=$($_.Count)" }
        Write-Host "Lot $BatchId : etat local $($lot.Etat) ; operations : $($ops -join ', ')"
        Write-Host 'Serveur : non interroge (la publication et le suivi distant arrivent en phase 5).'
        return $script:EXIT_OK
    }
    if ($lots.Count -eq 0) { Write-Host 'Aucun lot local.'; return $script:EXIT_OK }
    $lots | Format-Table -AutoSize | Out-String | Write-Host
    return $script:EXIT_OK
}

function Invoke-Generate {
    Write-Host @'
generate : aucune generation n'est automatisee ici. Les competences sont des sessions Claude, pas des
commandes. Procedure par type (voir deploy/AUDIT-SYNC-CONTENU.md section 5) :

  Corrections et cours  skill correction-experte        -> backend/ingest/<pays>/<epreuve>/*.json (+ PNG)
  Quiz                  skill concepteur-quiz-competence -> backend/ingest/_quiz/<pays>/<competence>.json
  Inedites              skill concepteur-epreuve-inedite -> backend/ingest/_inedit/... (hors v1 de la chaine)

Ensuite, pour chaque unite produite :
  .\scripts\edukora.ps1 validate     -Unite <unite>
  .\scripts\edukora.ps1 ingest-local -Unite <unite>
  .\scripts\edukora.ps1 prepare      -Unite <unite>

Une relecture humaine reste necessaire pour les inedites (blueprint valide en admin, epreuve publiee
par clic admin) ; rien n'est publie automatiquement.
'@
    return $script:EXIT_OK
}

function Show-Aide {
    Get-Help $PSCommandPath -Detailed | Out-String | Write-Host
    return $script:EXIT_OK
}

# --------------------------------------------------------------------------- transport et publication (phase 5)
#
# Principe : le poste ne conclut JAMAIS qu'un lot a echoue parce qu'une connexion SSH est tombee. Avant de
# lancer l'application, une coupure = echec certain (code 1, rien n'est parti). Apres le lancement, une
# coupure = indetermine (code 3) : on interroge `statut` sur le serveur, on ne relance jamais a l'aveugle.

function Test-ConfigDistante {
    param($Cfg)
    $manques = @()
    if (-not $Cfg.Hote) { $manques += 'Hote' }
    if (-not $Cfg.Utilisateur) { $manques += 'Utilisateur' }
    if (-not $Cfg.CleSsh -or -not (Test-Path -LiteralPath $Cfg.CleSsh)) { $manques += 'CleSsh (fichier introuvable)' }
    if (-not $Cfg.KnownHosts -or -not (Test-Path -LiteralPath $Cfg.KnownHosts)) { $manques += 'KnownHosts (fichier introuvable)' }
    return , $manques
}

function Get-OptionsSsh {
    param($Cfg)
    return @(
        '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', "UserKnownHostsFile=$($Cfg.KnownHosts)",
        '-o', 'IdentitiesOnly=yes', '-i', [string]$Cfg.CleSsh,
        '-o', 'ConnectTimeout=20', '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3'
    )
}

function Get-JsonDerniereLigne {
    param([string]$Texte)
    $lignes = @($Texte -split "`r?`n" | Where-Object { $_ -match '^\{' })
    if ($lignes.Count -eq 0) { return $null }
    try { return ($lignes[-1] | ConvertFrom-Json) } catch { return $null }
}

function Invoke-Distant {
    <# Une sous-commande de deploy/sync-lot.sh sur le serveur. Les arguments sont limites a [A-Za-z0-9._-]. #>
    param($Cfg, [string]$Sous, [string[]]$Arguments = @())
    if ($Sous -notmatch '^[a-z-]+$') { throw "Sous-commande distante invalide : $Sous" }
    foreach ($a in $Arguments) { if ($a -notmatch '^[A-Za-z0-9._-]+$') { throw "Argument distant refuse : $a" } }
    $script = if ($Cfg.ScriptServeur) { $Cfg.ScriptServeur } else { "$($Cfg.CheminServeur)/deploy/sync-lot.sh" }
    $commande = (@('bash', $script, $Sous) + $Arguments) -join ' '
    $r = Invoke-Native -Fichier $Cfg.SshExe -Arguments ((Get-OptionsSsh $Cfg) + @('-p', [string]$Cfg.Port, "$($Cfg.Utilisateur)@$($Cfg.Hote)", $commande))
    return [pscustomobject]@{ Code = $r.Code; Reseau = ($r.Code -eq 255); Json = (Get-JsonDerniereLigne $r.Out); Out = $r.Out; Err = $r.Err }
}

function Send-VersServeur {
    param($Cfg, [string]$Local, [string]$DistantRelatif)
    $dest = "$($Cfg.Utilisateur)@$($Cfg.Hote):$($Cfg.DossierLotsServeur)/$DistantRelatif"
    return (Invoke-Native -Fichier $Cfg.ScpExe -Arguments ((Get-OptionsSsh $Cfg) + @('-P', [string]$Cfg.Port, $Local, $dest)))
}

function Update-Etat {
    param([string]$LotDir, [hashtable]$Champs)
    $chemin = Join-Path $LotDir 'etat.json'
    $h = [ordered]@{}
    if (Test-Path -LiteralPath $chemin) { (Read-JsonFile $chemin).PSObject.Properties | ForEach-Object { $h[$_.Name] = $_.Value } }
    foreach ($k in $Champs.Keys) { $h[$k] = $Champs[$k] }
    $h['mis_a_jour_le'] = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    Write-JsonFile $chemin $h
}

function Get-LotLocal {
    param($Cfg, [string]$BatchId)
    if ($BatchId -notmatch '^\d{8}-\d{6}-[0-9a-f]{8}$') { throw "batch_id invalide : '$BatchId' (attendu AAAAMMJJ-HHMMSS-8hex, voir la commande status)" }
    $dir = Join-Path $Cfg.BatchesDir $BatchId
    $zip = Join-Path $Cfg.BatchesDir "lot-$BatchId.zip"
    $shaFichier = "$zip.sha256"
    foreach ($f in @($dir, $zip, $shaFichier, (Join-Path $dir 'manifest.json'))) {
        if (-not (Test-Path -LiteralPath $f)) { throw "Lot local incomplet ou introuvable : $f" }
    }
    $manifeste = Read-JsonFile (Join-Path $dir 'manifest.json')
    $sha = ((Get-Content -LiteralPath $shaFichier -Raw -Encoding UTF8).Trim() -split '\s+')[0].ToLower()
    $ops = @($manifeste.contenus | ForEach-Object { $_.operation })
    return [pscustomobject]@{
        BatchId = $BatchId; Dir = $dir; Zip = $zip; ShaFichier = $shaFichier; Sha = $sha; Manifeste = $manifeste
        SeulementCreations = (@($ops | Where-Object { $_ -notin @('create', 'noop') }).Count -eq 0)
        AvecRetraits = (@($ops | Where-Object { $_ -in @('retirer', 'reintegrer') }).Count -gt 0)
    }
}

function Get-StatutDistant {
    param($Cfg, [string]$BatchId)
    $r = Invoke-Distant $Cfg 'statut' @($BatchId)
    if ($r.Reseau) { return [pscustomobject]@{ Etat = 'reseau'; Statut = $null; Json = $null } }
    if ($null -eq $r.Json) { return [pscustomobject]@{ Etat = 'illisible'; Statut = $null; Json = $null } }
    return [pscustomobject]@{ Etat = 'ok'; Statut = [string]$r.Json.statut; Json = $r.Json }
}

function Get-CodeSortieLot {
    <# Code de sortie d'un lot arrive a un etat terminal. #>
    param([string]$Statut, $Compteurs)
    switch ($Statut) {
        'reussi' { return $script:EXIT_OK }
        'reussi_avec_avertissements' { return $script:EXIT_OK }
        'partiel' { return $script:EXIT_CONFLITS }
        'a_verifier' { return $script:EXIT_INDETERMINE }
        'echoue' {
            $noms = @()
            if ($Compteurs) { $noms = @($Compteurs.PSObject.Properties | Where-Object { $_.Value -gt 0 } | ForEach-Object { $_.Name }) }
            if (@($noms | Where-Object { $_ -match '^conflit|^adoption|^structure|^correction|^rejete' }).Count -gt 0) { return $script:EXIT_CONFLITS }
            return $script:EXIT_ECHEC
        }
        default { return $script:EXIT_INDETERMINE }
    }
}

function Write-ResumeCompteurs {
    param($Compteurs)
    if ($null -eq $Compteurs) { return }
    foreach ($p in $Compteurs.PSObject.Properties) { Write-Host ('  {0,-26} {1}' -f $p.Name, $p.Value) }
}

function Initialize-LotServeur {
    <# Envoie l'archive si le serveur n'a pas exactement la meme, la verifie, la fait recevoir. Idempotent. #>
    param($Cfg, $Lot)
    $r = Invoke-Distant $Cfg 'ouvrir-lot' @($Lot.BatchId)
    if ($r.Reseau -or $r.Code -ne 0) { return @{ Ok = $false; Message = "ouvrir-lot : serveur injoignable ou refus ($($r.Code)) $($r.Err.Trim())" } }
    $v = Invoke-Distant $Cfg 'verifier-archive' @($Lot.BatchId)
    $presente = ($null -ne $v.Json -and $v.Json.statut -eq 'ok' -and ([string]$v.Json.sha256).ToLower() -eq $Lot.Sha)
    if (-not $presente) {
        Write-Host "  envoi de l'archive ($([math]::Round((Get-Item -LiteralPath $Lot.Zip).Length / 1KB)) Ko)..."
        foreach ($paire in @(@($Lot.Zip, 'lot.zip'), @($Lot.ShaFichier, 'lot.zip.sha256'))) {
            $e = Send-VersServeur $Cfg $paire[0] "incoming/$($Lot.BatchId)/$($paire[1])"
            if ($e.Code -ne 0) { return @{ Ok = $false; Message = "scp en echec ($($e.Code)) : $($e.Err.Trim())" } }
        }
        $v = Invoke-Distant $Cfg 'verifier-archive' @($Lot.BatchId)
        if ($v.Code -ne 0 -or $null -eq $v.Json -or $v.Json.statut -ne 'ok' -or ([string]$v.Json.sha256).ToLower() -ne $Lot.Sha) {
            return @{ Ok = $false; Message = "archive recue differente de l'archive locale (transfert corrompu) : $($v.Out.Trim())" }
        }
    }
    Update-Etat $Lot.Dir @{ etat = 'televerse'; sha256_archive = $Lot.Sha }
    $rc = Invoke-Distant $Cfg 'recevoir' @($Lot.BatchId)
    if ($rc.Reseau -or $rc.Code -ne 0 -or $null -eq $rc.Json) {
        $detail = if ($rc.Json -and $rc.Json.erreur) { $rc.Json.erreur } else { $rc.Err.Trim() }
        return @{ Ok = $false; Message = "le serveur refuse le lot : $detail" }
    }
    Update-Etat $Lot.Dir @{ etat = 'recu_serveur' }
    return @{ Ok = $true; Message = '' }
}

function Invoke-PlanDistant {
    param($Cfg, $Lot)
    $p = Invoke-Distant $Cfg 'planifier' @($Lot.BatchId)
    if ($p.Reseau -or $null -eq $p.Json -or $null -eq $p.Json.PSObject.Properties['plan']) {
        return @{ Ok = $false; Plan = $null; Message = "planification impossible : $($p.Out.Trim()) $($p.Err.Trim())" }
    }
    Write-JsonFile (Join-Path $Lot.Dir 'plan-serveur.json') $p.Json
    return @{ Ok = $true; Plan = $p.Json; Message = '' }
}

function Write-Plan {
    param($Plan)
    Write-Host ("Plan : {0} contenu(s), {1} bloquant(s)" -f @($Plan.plan).Count, $Plan.bloquants)
    Write-ResumeCompteurs $Plan.compteurs
    $bloquants = @($Plan.plan | Where-Object { $_.resultat_prevu -match '^conflit|^adoption|^structure|^correction|^rejete|^erreur' })
    foreach ($b in ($bloquants | Select-Object -First 25)) {
        $raison = ''
        if ($b.detail.PSObject.Properties['erreur']) { $raison = $b.detail.erreur }
        elseif ($b.detail.PSObject.Properties['raisons']) { $raison = ($b.detail.raisons -join ' ; ') }
        elseif ($b.detail.PSObject.Properties['diff'] -and $b.detail.diff) { $raison = 'ecarts : ' + (($b.detail.diff | Select-Object -First 4) -join ', ') }
        Write-Host ("  [{0}] {1} {2}" -f $b.resultat_prevu, $b.id_stable, $raison) -ForegroundColor Yellow
    }
    if ($bloquants.Count -gt 25) { Write-Host "  ... et $($bloquants.Count - 25) autre(s) (voir plan-serveur.json)" -ForegroundColor Yellow }
}

function Wait-Lot {
    <# Interroge `statut` jusqu'a un etat terminal. Tolere les coupures reseau (indetermine si elles durent). #>
    param($Cfg, [string]$BatchId)
    $limite = (Get-Date).AddSeconds([int]$Cfg.DelaiMaxLotSecondes)
    $echecsReseau = 0
    $nonDemarre = 0
    $dernier = $null
    while ((Get-Date) -lt $limite) {
        $s = Get-StatutDistant $Cfg $BatchId
        if ($s.Etat -ne 'ok') {
            $echecsReseau++
            if ($echecsReseau -ge [int]$Cfg.ToleranceReseau) { return @{ Fin = 'indetermine'; Statut = $dernier } }
        }
        else {
            $echecsReseau = 0
            $dernier = $s.Json
            switch ($s.Statut) {
                { $_ -in @('reussi', 'reussi_avec_avertissements', 'partiel', 'echoue', 'a_verifier') } { return @{ Fin = 'termine'; Statut = $s.Json } }
                'inconnu' { return @{ Fin = 'inconnu'; Statut = $s.Json } }
                { $_ -in @('verifie', 'pret', 'recu') } {
                    $nonDemarre++
                    if ($nonDemarre -ge 6) { return @{ Fin = 'non_demarre'; Statut = $s.Json } }
                }
                default { $nonDemarre = 0 }
            }
        }
        if ([int]$Cfg.DelaiSondageSecondes -gt 0) { Start-Sleep -Seconds ([int]$Cfg.DelaiSondageSecondes) }
    }
    return @{ Fin = 'delai'; Statut = $dernier }
}

function Complete-Lot {
    <# Affiche le resultat d'un lot arrive a un etat terminal, met a jour l'etat local, retourne le code de sortie. #>
    param($Cfg, $Lot, $Attente)
    switch ($Attente.Fin) {
        'indetermine' {
            Update-Etat $Lot.Dir @{ etat = 'indetermine' }
            Write-Host "RESULTAT INDETERMINE : le serveur ne repond plus. Le lot a peut-etre ete applique." -ForegroundColor Red
            Write-Host "Ne PAS relancer : .\scripts\edukora.ps1 resume -BatchId $($Lot.BatchId) interroge le serveur." -ForegroundColor Red
            return $script:EXIT_INDETERMINE
        }
        'delai' {
            Update-Etat $Lot.Dir @{ etat = 'indetermine' }
            Write-Host "Delai d'attente depasse : le lot tourne peut-etre encore. Utiliser resume -BatchId $($Lot.BatchId) pour reprendre le suivi." -ForegroundColor Red
            return $script:EXIT_INDETERMINE
        }
        'non_demarre' {
            Write-Host "Le serveur n'a pas demarre l'application (verrou pris par un deploiement ?). Journal : $($Cfg.DossierLotsServeur)/journaux/$($Lot.BatchId).log" -ForegroundColor Red
            return $script:EXIT_ECHEC
        }
        'inconnu' {
            Write-Host 'Lot inconnu du serveur apres le lancement.' -ForegroundColor Red
            return $script:EXIT_ECHEC
        }
    }
    $s = $Attente.Statut
    $code = Get-CodeSortieLot -Statut ([string]$s.statut) -Compteurs $s.compteurs
    Write-Host "Lot $($Lot.BatchId) : $($s.statut)"
    Write-ResumeCompteurs $s.compteurs
    if ($s.PSObject.Properties['avertissements']) {
        foreach ($a in @($s.avertissements)) { if ($a) { Write-Host "  avertissement : $a" -ForegroundColor Yellow } }
    }
    $etat = switch ($code) { 0 { 'termine_ok' } 3 { 'indetermine' } default { 'termine_echec' } }
    Update-Etat $Lot.Dir @{ etat = $etat; statut_serveur = [string]$s.statut }
    if ($code -eq 0) {
        $f = Invoke-Distant $Cfg 'verifier-fichiers'
        if ($f.Json) {
            $manquants = @($f.Json.references_sans_fichier)
            if ($manquants.Count -gt 0) { Write-Host "ATTENTION : $($manquants.Count) reference(s) sans fichier (voir verifier-fichiers sur le serveur)." -ForegroundColor Yellow }
            else { Write-Host '  fichiers : toutes les references ont leur fichier.' -ForegroundColor Green }
        }
    }
    elseif ($code -eq $script:EXIT_CONFLITS) {
        Write-Host "Des contenus n'ont pas ete appliques. Voir : .\scripts\edukora.ps1 resoudre -BatchId $($Lot.BatchId) ..., puis publish -Appliquer -Reprendre." -ForegroundColor Yellow
    }
    return $code
}

function Invoke-Publish {
    param($Cfg, [string]$BatchId, [switch]$Appliquer, [switch]$Reprendre, [switch]$SansPostTraitement, [switch]$ConfirmerRetraits)
    $manques = Test-ConfigDistante $Cfg
    if ($manques.Count -gt 0) { Write-Host "publish : configuration incomplete : $($manques -join ', ')" -ForegroundColor Red; return $script:EXIT_USAGE }
    $lot = Get-LotLocal $Cfg $BatchId
    if ($lot.AvecRetraits -and $Appliquer -and -not $ConfirmerRetraits) {
        Write-Host 'Ce lot contient des retraits : ajouter -ConfirmerRetraits pour les appliquer.' -ForegroundColor Red
        return $script:EXIT_APPROBATION
    }
    Write-Host "=== publish $BatchId ($(if ($Appliquer) { 'application' } else { 'simulation' })) ===" -ForegroundColor Cyan

    # 1. Etat deja connu du serveur : un lot termine ne se rejoue pas, un lot en cours ne se double pas.
    $avant = Get-StatutDistant $Cfg $BatchId
    if ($avant.Etat -ne 'ok') { Write-Host 'Serveur injoignable : rien n''a ete lance (relancer plus tard).' -ForegroundColor Red; return $script:EXIT_ECHEC }
    $deja = [string]$avant.Statut
    if ($deja -in @('reussi', 'reussi_avec_avertissements')) {
        Write-Host "Lot deja applique ($deja) : rien a faire." -ForegroundColor Green
        Update-Etat $lot.Dir @{ etat = 'termine_ok'; statut_serveur = $deja }
        return $script:EXIT_OK
    }
    if ($deja -eq 'en_cours') {
        Write-Host 'Le lot est en cours d''application sur le serveur : suivi.' -ForegroundColor Yellow
        return (Complete-Lot $Cfg $lot (Wait-Lot $Cfg $BatchId))
    }
    if ($deja -eq 'a_verifier' -and -not $Reprendre) {
        Write-Host 'Etat a verifier (processus interrompu cote serveur). Utiliser : resume -BatchId ... -Reprendre' -ForegroundColor Red
        return $script:EXIT_INDETERMINE
    }

    # 2. Transfert, verification, reception.
    $init = Initialize-LotServeur $Cfg $lot
    if (-not $init.Ok) { Write-Host "publish : $($init.Message)" -ForegroundColor Red; return $script:EXIT_ECHEC }

    # 3. Simulation sur le serveur.
    $plan = Invoke-PlanDistant $Cfg $lot
    if (-not $plan.Ok) { Write-Host "publish : $($plan.Message)" -ForegroundColor Red; return $script:EXIT_ECHEC }
    Update-Etat $lot.Dir @{ etat = 'planifie' }
    Write-Plan $plan.Plan
    if ($plan.Plan.bloquants -gt 0) {
        Write-Host 'Des contenus bloquent : rien n''est applique. Resolvez avec `resoudre` puis relancez.' -ForegroundColor Yellow
        return $script:EXIT_CONFLITS
    }
    if (-not $Appliquer) {
        Write-Host 'Simulation terminee, aucun conflit. Relancer avec -Appliquer pour appliquer.' -ForegroundColor Green
        return $script:EXIT_OK
    }

    # 4. Sauvegarde verifiee (une sauvegarde recente suffit pour un lot qui ne fait que creer).
    $argsSauvegarde = @($BatchId)
    if ($lot.SeulementCreations) { $argsSauvegarde += @('--max-age-h', '24') }
    $sv = Invoke-Distant $Cfg 'sauvegarde' $argsSauvegarde
    if ($sv.Reseau -or $sv.Code -ne 0 -or $null -eq $sv.Json -or $sv.Json.statut -ne 'ok') {
        $detail = if ($sv.Json -and $sv.Json.erreur) { $sv.Json.erreur } else { $sv.Err.Trim() }
        Write-Host "Sauvegarde en echec : rien n'a ete modifie. $detail" -ForegroundColor Red
        return $script:EXIT_ECHEC
    }
    Update-Etat $lot.Dir @{ etat = 'sauvegarde_ok'; sauvegarde = [string]$sv.Json.dump }
    Write-Host "  sauvegarde : $($sv.Json.dump) ($(if ($sv.Json.reutilisee) { 'recente, reutilisee' } else { 'creee et verifiee' }))" -ForegroundColor Green

    # 5. Lancement detache. Apres cette ligne, une coupure n'est plus un echec certain.
    $sous = if ($Reprendre -or $deja -in @('partiel', 'echoue')) { 'reprendre' } else { 'appliquer' }
    $argsLancement = @($BatchId)
    if ($ConfirmerRetraits) { $argsLancement += '--confirme-retraits' }
    if ($SansPostTraitement) { $argsLancement += '--sans-post-traitement' }
    Update-Etat $lot.Dir @{ etat = 'application_lancee' }
    $l = Invoke-Distant $Cfg $sous $argsLancement
    if ($l.Code -eq 75) { Write-Host 'Un lot ou un deploiement est en cours sur le serveur (verrou pris) : rien n''a ete lance.' -ForegroundColor Red; Update-Etat $lot.Dir @{ etat = 'sauvegarde_ok' }; return $script:EXIT_ECHEC }
    if ($l.Reseau -or $null -eq $l.Json) {
        $s = Get-StatutDistant $Cfg $BatchId
        if ($s.Etat -ne 'ok' -or $s.Statut -in @('verifie', 'pret', 'recu')) {
            Write-Host 'Le lancement n''a pas pu etre confirme. Interrogez : resume -BatchId ... (ne pas relancer a l''aveugle).' -ForegroundColor Red
            Update-Etat $lot.Dir @{ etat = 'indetermine' }
            return $script:EXIT_INDETERMINE
        }
    }
    elseif ($l.Json.statut -ne 'lance') {
        Write-Host "Lancement refuse : $($l.Out.Trim())" -ForegroundColor Red
        return $script:EXIT_ECHEC
    }
    Write-Host '  application lancee sur le serveur (detachee : une coupure SSH ne l''interrompt pas).'
    return (Complete-Lot $Cfg $lot (Wait-Lot $Cfg $BatchId))
}

function Invoke-Resume {
    param($Cfg, [string]$BatchId, [switch]$Reprendre)
    $manques = Test-ConfigDistante $Cfg
    if ($manques.Count -gt 0) { Write-Host "resume : configuration incomplete : $($manques -join ', ')" -ForegroundColor Red; return $script:EXIT_USAGE }
    $lot = Get-LotLocal $Cfg $BatchId
    $s = Get-StatutDistant $Cfg $BatchId
    if ($s.Etat -ne 'ok') { Write-Host 'Serveur injoignable : etat inconnu. Reessayer plus tard.' -ForegroundColor Red; return $script:EXIT_INDETERMINE }
    Write-Host "Etat du lot sur le serveur : $($s.Statut)"
    switch ($s.Statut) {
        'inconnu' { Write-Host 'Le serveur ne connait pas ce lot (jamais envoye ?). Utiliser publish.'; return $script:EXIT_ECHEC }
        'en_cours' { return (Complete-Lot $Cfg $lot (Wait-Lot $Cfg $BatchId)) }
        { $_ -in @('a_verifier', 'partiel', 'echoue') } {
            if (-not $Reprendre) {
                Write-Host "Etat '$($s.Statut)' : verifiez le rapport (statut -BatchId), puis relancez avec -Reprendre pour ne rejouer que les operations non terminees." -ForegroundColor Yellow
                Write-ResumeCompteurs $s.Json.compteurs
                return (Get-CodeSortieLot -Statut $s.Statut -Compteurs $s.Json.compteurs)
            }
            return (Invoke-Publish -Cfg $Cfg -BatchId $BatchId -Appliquer -Reprendre)
        }
        default { return (Complete-Lot $Cfg $lot @{ Fin = 'termine'; Statut = $s.Json }) }
    }
}

function Invoke-Resoudre {
    param($Cfg, [string]$BatchId, [string]$Decision, [string[]]$Ids = @(), [string]$Motif)
    $manques = Test-ConfigDistante $Cfg
    if ($manques.Count -gt 0) { Write-Host "resoudre : configuration incomplete : $($manques -join ', ')" -ForegroundColor Red; return $script:EXIT_USAGE }
    if ($Decision -notin @('garder_prod', 'ecraser', 'recreer')) { Write-Host 'resoudre : -Decision garder_prod | ecraser | recreer'; return $script:EXIT_USAGE }
    $lot = Get-LotLocal $Cfg $BatchId
    $init = Initialize-LotServeur $Cfg $lot
    if (-not $init.Ok) { Write-Host "resoudre : $($init.Message)" -ForegroundColor Red; return $script:EXIT_ECHEC }
    $plan = Invoke-PlanDistant $Cfg $lot
    if (-not $plan.Ok) { Write-Host "resoudre : $($plan.Message)" -ForegroundColor Red; return $script:EXIT_ECHEC }
    Write-Plan $plan.Plan
    $argv = @('resoudre', '--lot', $lot.Dir, '--plan', (Join-Path $lot.Dir 'plan-serveur.json'), '--decision', $Decision, '--par', (Get-ApprobateurParDefaut))
    if ($Motif) { $argv += @('--motif', $Motif) }
    if ($Ids.Count -gt 0) { $argv += '--ids'; $argv += $Ids }
    $r = Invoke-Outil $Cfg $argv
    if ($null -eq $r.Json -or $r.Code -ge 2) { Write-Host "resoudre : $($r.Out)$($r.Err)" -ForegroundColor Red; return $script:EXIT_USAGE }
    Write-Host ("resoudre : {0} decision(s) '{1}' ecrite(s) ; {2} ignoree(s)." -f $r.Json.posees, $Decision, @($r.Json.ignorees).Count)
    foreach ($i in @($r.Json.ignorees)) { Write-Host "  ignore : $i" -ForegroundColor Yellow }
    Update-Etat $lot.Dir @{ etat = 'pret_local'; sha256_archive = $r.Json.sha256_archive; decisions = $Decision }
    Write-Host "Archive reconstruite. Suite : .\scripts\edukora.ps1 publish -BatchId $BatchId -Appliquer"
    if ($r.Json.posees -eq 0) { return $script:EXIT_ECHEC }
    return $script:EXIT_OK
}

function Invoke-Reference {
    param($Cfg)
    $manques = Test-ConfigDistante $Cfg
    if ($manques.Count -gt 0) { Write-Host "reference : configuration incomplete : $($manques -join ', ')" -ForegroundColor Red; return $script:EXIT_USAGE }
    $r = Invoke-Distant $Cfg 'reference'
    if ($r.Reseau -or $null -eq $r.Json -or $null -eq $r.Json.PSObject.Properties['contenus']) {
        Write-Host "reference : reponse inattendue du serveur ($($r.Code)) $($r.Err.Trim())" -ForegroundColor Red
        return $script:EXIT_ECHEC
    }
    $dest = Join-Path $Cfg.BatchesDir '_reference-prod.json'
    Write-JsonFile $dest $r.Json
    Write-Host ("reference : {0} contenu(s) journalise(s) en production -> {1}" -f @($r.Json.contenus.PSObject.Properties).Count, $dest)
    Write-Host 'Utilisation : .\scripts\edukora.ps1 prepare ... -Reference batches\_reference-prod.json'
    return $script:EXIT_OK
}

function Show-RollbackInfo {
    param($Cfg, [string]$BatchId)
    $lot = Get-LotLocal $Cfg $BatchId
    $etat = Read-JsonFile (Join-Path $lot.Dir 'etat.json')
    $dump = if ($etat.PSObject.Properties['sauvegarde']) { [string]$etat.sauvegarde } else { '' }
    Write-Host "Retour arriere du lot $BatchId : AUCUNE action automatique n'est lancee par cette commande."
    Write-Host '1. Un lot corrige du contenu SUR PLACE et ne supprime rien : le plus souvent, un nouveau lot corrige l''erreur.'
    Write-Host '2. Pour annuler un contenu publie a tort : lot avec retrait (statut REJETE), jamais de suppression.'
    if ($dump) {
        Write-Host "3. Sauvegarde prise avant ce lot : $($Cfg.DossierLotsServeur)/sauvegardes/$dump"
        Write-Host '   Restauration (decision humaine, base jetable d''abord) : bash deploy/sync-lot.sh test-restauration ' -NoNewline; Write-Host $dump
        Write-Host '   puis procedure de deploy/README-TUNNEL.md, section « Si ca tourne mal » (arreter backend et relances).'
    }
    else { Write-Host '3. Aucune sauvegarde enregistree pour ce lot (lot non applique ?).' }
    return $script:EXIT_OK
}

function Invoke-DoctorDistant {
    param($Cfg)
    $manques = Test-ConfigDistante $Cfg
    if ($manques.Count -gt 0) { Write-Host "doctor -Distant : configuration incomplete : $($manques -join ', ')" -ForegroundColor Red; return $script:EXIT_USAGE }
    $r = Invoke-Distant $Cfg 'diagnostic'
    if ($r.Reseau) { Write-Host "Connexion SSH impossible : $($r.Err.Trim())" -ForegroundColor Red; return $script:EXIT_USAGE }
    if ($null -eq $r.Json) { Write-Host "Reponse inattendue (le script deploy/sync-lot.sh est-il deploye ?) : $($r.Out) $($r.Err)" -ForegroundColor Red; return $script:EXIT_USAGE }
    $j = $r.Json
    $lignes = @(
        @('docker', [bool]$j.docker, 'docker accessible a l''utilisateur'),
        @('flock', [bool]$j.flock, 'flock installe (verrou partage avec deploy.sh)'),
        @('dossier des lots', [bool]$j.dossier_lots, "$($Cfg.DossierLotsServeur) (creer avec : bash deploy/sync-lot.sh preparer-dossiers)"),
        @('droits 700', ([string]$j.droits_dossier_lots -eq '700'), "droits actuels : $($j.droits_dossier_lots)"),
        @('commande sync_contenu', [bool]$j.commande_sync_contenu, 'presente dans le conteneur (livree par un Deploy de l''application)'),
        @('disque', ([int]$j.disque_libre_go -ge 5), "$($j.disque_libre_go) Go libres")
    )
    $nbErr = 0
    foreach ($l in $lignes) {
        $statut = if ($l[1]) { 'ok' } else { 'erreur'; $nbErr++ }
        Write-Host ('[{0,-7}] {1} : {2}' -f $statut, $l[0], $l[2]) -ForegroundColor $(if ($l[1]) { 'Green' } else { 'Red' })
    }
    Write-Host "Version deployee : $($j.version_deployee) ; utilisateur : $($j.utilisateur)"
    if ($nbErr -gt 0) { return $script:EXIT_USAGE }
    return $script:EXIT_OK
}

# --------------------------------------------------------------------------- point d'entree

function Invoke-Main {
    $cfg = Read-Config $Config
    $unites = Get-Unites -Unite $Unite -Liste $Liste
    switch ($Commande) {
        'doctor' { if ($Distant) { return (Invoke-DoctorDistant -Cfg $cfg) } else { return (Invoke-Doctor -Cfg $cfg -Rapide:$Rapide) } }
        'generate' { return (Invoke-Generate) }
        'validate' { return (Invoke-Validate -Cfg $cfg -Unites $unites) }
        'ingest-local' { return (Invoke-IngestLocal -Cfg $cfg -Unites $unites -Strict:$Strict) }
        'inventaire' { return (Invoke-Inventaire -Cfg $cfg -SansBase:$SansBase) }
        'prepare' { return (Invoke-Prepare -Cfg $cfg -Unites $unites -Nom $Nom -Reference $Reference -Retraits $Retraits -Approuver:$Approuver -AccepterSansTunnel:$AccepterSansTunnel -ToutOuRien:$ToutOuRien -Adopter:$Adopter) }
        'status' { return (Invoke-Status -Cfg $cfg -BatchId $BatchId) }
        'publish' { return (Invoke-Publish -Cfg $cfg -BatchId $BatchId -Appliquer:$Appliquer -Reprendre:$Reprendre -SansPostTraitement:$SansPostTraitement -ConfirmerRetraits:$ConfirmerRetraits) }
        'resume' { return (Invoke-Resume -Cfg $cfg -BatchId $BatchId -Reprendre:$Reprendre) }
        'resoudre' { return (Invoke-Resoudre -Cfg $cfg -BatchId $BatchId -Decision $Decision -Ids $Ids -Motif $Motif) }
        'reference' { return (Invoke-Reference -Cfg $cfg) }
        'rollback-info' { return (Show-RollbackInfo -Cfg $cfg -BatchId $BatchId) }
        default { return (Show-Aide) }
    }
}

# Dot-sourcer le script (tests Pester) charge les fonctions sans rien executer.
if ($MyInvocation.InvocationName -ne '.') {
    try { $code = @(Invoke-Main)[-1] }
    catch {
        Write-Host "edukora : $($_.Exception.Message)" -ForegroundColor Red
        $code = $script:EXIT_USAGE
    }
    exit ([int]$code)
}
