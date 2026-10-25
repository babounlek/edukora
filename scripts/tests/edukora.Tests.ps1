#Requires -Version 5.1
# Tests Pester 3.4 (celui livre avec Windows PowerShell 5.1) de scripts/edukora.ps1.
#   Invoke-Pester .\scripts\tests
# Aucun test ne touche Docker, le reseau ou la base : l'outil Python tourne sur des dossiers temporaires.

$ici = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:Edukora = Join-Path (Split-Path -Parent $ici) 'edukora.ps1'
. $script:Edukora   # charge les fonctions sans executer la commande (voir la garde de fin de script)

function New-Banc {
    $racine = Join-Path ([System.IO.Path]::GetTempPath()) ('edukora-pester-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Force -Path (Join-Path $racine 'ingest\cm\dos'), (Join-Path $racine 'batches') | Out-Null
    $cfg = Get-ConfigParDefaut
    $cfg['IngestDir'] = Join-Path $racine 'ingest'
    $cfg['BatchesDir'] = Join-Path $racine 'batches'
    $cfg['_Source'] = ''
    return [pscustomobject]@{ Racine = $racine; Cfg = $cfg }
}

function Write-Utf8 {
    param([string]$Chemin, [string]$Texte)
    [System.IO.File]::WriteAllText($Chemin, $Texte, (New-Object System.Text.UTF8Encoding($false)))
}

function New-ExerciceJson {
    param([string]$Numero = '1', [string]$Extra = '')
    return '{"epreuve_source":"bac-test.pdf","numero_exercice":"' + $Numero + '","matiere":"Maths","annee":2020,"statut":"brouillon",' +
    '"questions":[{"numero":"1","enonce_markdown":"q","corrige_markdown":"c"}]' + $Extra + '}'
}

Describe 'Utilitaires' {
    It 'ConvertTo-ArgString protege les espaces et les guillemets' {
        ConvertTo-ArgString @('a', 'b c', '', 'd"e') | Should Be 'a "b c" "" "d\"e"'
    }
    It 'ConvertTo-GitBashPath convertit un chemin Windows' {
        ConvertTo-GitBashPath 'D:\edukora\scripts' | Should Be '/d/edukora/scripts'
    }
    It 'Get-SlugUnite remplace les separateurs' {
        Get-SlugUnite 'cm/dos' | Should Be 'cm__dos'
    }
    It 'Get-Unites fusionne, normalise, ignore les commentaires et dedoublonne' {
        $banc = New-Banc
        $liste = Join-Path $banc.Racine 'liste.txt'
        Write-Utf8 $liste "# commentaire`r`ncm\a`r`n`r`ncm/b/`r`ncm/a`r`n"
        $u = Get-Unites -Unite @('cm\c', 'cm/a') -Liste $liste
        ($u | Sort-Object) -join ',' | Should Be 'cm/a,cm/b,cm/c'
        Remove-Item -Recurse -Force $banc.Racine
    }
    It 'Write-JsonFile ecrit de l UTF-8 sans BOM' {
        $banc = New-Banc
        $f = Join-Path $banc.Racine 'x.json'
        Write-JsonFile $f ([ordered]@{ a = 'é' })
        $octets = [System.IO.File]::ReadAllBytes($f)
        ($octets[0] -eq 0xEF) | Should Be $false
        (Read-JsonFile $f).a | Should Be 'é'
        Remove-Item -Recurse -Force $banc.Racine
    }
    It 'les codes de sortie sont ceux de la specification' {
        $script:EXIT_OK | Should Be 0
        $script:EXIT_ECHEC | Should Be 1
        $script:EXIT_USAGE | Should Be 2
        $script:EXIT_INDETERMINE | Should Be 3
        $script:EXIT_CONFLITS | Should Be 4
        $script:EXIT_APPROBATION | Should Be 5
    }
}

Describe 'Configuration' {
    It 'prend les valeurs par defaut sans fichier' {
        $c = Read-Config (Join-Path ([System.IO.Path]::GetTempPath()) 'inexistant-edukora.psd1')
        $c.Conteneur | Should Be 'edukora-backend-1'
        $c.DossierLotsServeur | Should Be '/srv/edukora-lots'
        $c._Source | Should Be ''
    }
    It 'surcharge depuis un fichier psd1' {
        $banc = New-Banc
        $f = Join-Path $banc.Racine 'c.psd1'
        Write-Utf8 $f "@{ Conteneur = 'autre'; Port = 2222 }"
        $c = Read-Config $f
        $c.Conteneur | Should Be 'autre'
        $c.Port | Should Be 2222
        $c._Source | Should Be $f
        Remove-Item -Recurse -Force $banc.Racine
    }
    It 'Find-Python retient le chemin configure s il existe' {
        $banc = New-Banc
        $faux = Join-Path $banc.Racine 'python.exe'
        Write-Utf8 $faux 'x'
        Find-Python @{ Python = $faux } | Should Be $faux
        Remove-Item -Recurse -Force $banc.Racine
    }
    It 'le fichier de configuration d exemple est un psd1 valide' {
        $c = Import-PowerShellDataFile (Join-Path (Split-Path -Parent $ici) 'edukora.config.example.psd1')
        $c.DossierLotsServeur | Should Be '/srv/edukora-lots'
        $c.Utilisateur | Should Be 'deploy'
    }
}

Describe 'validate / prepare / status (outil Python reel, dossiers temporaires)' {
    BeforeEach { $script:banc = New-Banc }
    AfterEach { Remove-Item -Recurse -Force $script:banc.Racine -ErrorAction SilentlyContinue }

    It 'validate accepte une unite saine' {
        Write-Utf8 (Join-Path $script:banc.Racine 'ingest\cm\dos\dos_exercice_1.json') (New-ExerciceJson)
        Invoke-Validate -Cfg $script:banc.Cfg -Unites @('cm/dos') | Should Be 0
    }
    It 'validate refuse un JSON invalide' {
        Write-Utf8 (Join-Path $script:banc.Racine 'ingest\cm\dos\dos_exercice_1.json') '{pas du json'
        Invoke-Validate -Cfg $script:banc.Cfg -Unites @('cm/dos') | Should Be 1
    }
    It 'validate sans unite est une erreur d usage' {
        Invoke-Validate -Cfg $script:banc.Cfg -Unites @() | Should Be 2
    }
    It 'prepare refuse (1) une unite sans validation locale et ne cree aucun lot' {
        Write-Utf8 (Join-Path $script:banc.Racine 'ingest\cm\dos\dos_exercice_1.json') (New-ExerciceJson)
        Invoke-Prepare -Cfg $script:banc.Cfg -Unites @('cm/dos') | Should Be 1
        @(Get-LotsLocaux $script:banc.Cfg).Count | Should Be 0
    }
    It 'prepare exige l approbation (5) hors session interactive puis construit le lot avec -Approuver' {
        Write-Utf8 (Join-Path $script:banc.Racine 'ingest\cm\dos\dos_exercice_1.json') (New-ExerciceJson)
        Save-Validation $script:banc.Cfg 'cm/dos' 'ok' 'valide' 'test'
        Mock Test-Interactif { return $false }
        Invoke-Prepare -Cfg $script:banc.Cfg -Unites @('cm/dos') | Should Be 5
        @(Get-LotsLocaux $script:banc.Cfg).Count | Should Be 0

        Invoke-Prepare -Cfg $script:banc.Cfg -Unites @('cm/dos') -Approuver -Nom 'essai' | Should Be 0
        $lots = @(Get-LotsLocaux $script:banc.Cfg)
        $lots.Count | Should Be 1
        $lots[0].Etat | Should Be 'pret_local'
        $lots[0].Archive | Should Be $true
        $m = Read-JsonFile (Join-Path $script:banc.Cfg.BatchesDir "$($lots[0].BatchId)\manifest.json")
        $m.nom | Should Be 'essai'
        $m.contenus[0].operation | Should Be 'create'
        Invoke-Status -Cfg $script:banc.Cfg -BatchId $lots[0].BatchId | Should Be 0
    }
    It 'prepare refuse une validation perimee apres modification du contenu' {
        $f = Join-Path $script:banc.Racine 'ingest\cm\dos\dos_exercice_1.json'
        Write-Utf8 $f (New-ExerciceJson)
        Save-Validation $script:banc.Cfg 'cm/dos' 'ok' 'valide' 'test'
        Write-Utf8 $f (New-ExerciceJson -Extra ',"enonce_intro_markdown":"corrige apres validation"')
        Invoke-Prepare -Cfg $script:banc.Cfg -Unites @('cm/dos') -Approuver | Should Be 1
    }
    It 'prepare refuse un tunnel non rejoue sans -AccepterSansTunnel' {
        Write-Utf8 (Join-Path $script:banc.Racine 'ingest\cm\dos\dos_exercice_1.json') (New-ExerciceJson)
        Save-Validation $script:banc.Cfg 'cm/dos' 'ok' 'non_rejoue' 'deja en base'
        Invoke-Prepare -Cfg $script:banc.Cfg -Unites @('cm/dos') -Approuver | Should Be 1
        Invoke-Prepare -Cfg $script:banc.Cfg -Unites @('cm/dos') -Approuver -AccepterSansTunnel | Should Be 0
    }
    It 'status sans lot ne plante pas' {
        Invoke-Status -Cfg $script:banc.Cfg | Should Be 0
    }
    It 'status d un lot inconnu est un echec' {
        Invoke-Status -Cfg $script:banc.Cfg -BatchId 'nexiste-pas' | Should Be 1
    }
}

Describe 'doctor' {
    It 'signale Python et l outil de lot sans exiger Docker en mode rapide' {
        $banc = New-Banc
        $res = Get-Verifications -Cfg $banc.Cfg -Rapide
        ($res | Where-Object { $_.Verification -eq 'Python' }).Statut | Should Be 'ok'
        ($res | Where-Object { $_.Verification -eq 'Outil de lot' }).Statut | Should Be 'ok'
        @($res | Where-Object { $_.Verification -like 'Conteneur*' }).Count | Should Be 0
        Remove-Item -Recurse -Force $banc.Racine
    }
    It 'echoue (2) quand Python est introuvable' {
        $banc = New-Banc
        Mock Find-Python { return $null }
        Invoke-Doctor -Cfg $banc.Cfg -Rapide | Should Be 2
        Remove-Item -Recurse -Force $banc.Racine
    }
}
