#Requires -Version 5.1
# Tests Pester du transport et de la publication (phase 5) avec un FAUX serveur (fake-ssh / fake-scp) :
# aucun reseau, aucun Docker, aucun vrai serveur. Les scenarios sont choisis par $env:FAKE_SCENARIO.
#   Invoke-Pester .\scripts\tests\transport.Tests.ps1

$ici = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path (Split-Path -Parent $ici) 'edukora.ps1')

function Write-Utf8 {
    param([string]$Chemin, [string]$Texte)
    [System.IO.File]::WriteAllText($Chemin, $Texte, (New-Object System.Text.UTF8Encoding($false)))
}

function New-BancTransport {
    $racine = Join-Path ([System.IO.Path]::GetTempPath()) ('edukora-transport-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Force -Path (Join-Path $racine 'ingest\cm\dos'), (Join-Path $racine 'batches'), (Join-Path $racine 'fake') | Out-Null
    Write-Utf8 (Join-Path $racine 'cle') 'cle de test'
    Write-Utf8 (Join-Path $racine 'known_hosts') 'serveur.test ssh-ed25519 AAAA'
    $cfg = Get-ConfigParDefaut
    $cfg['IngestDir'] = Join-Path $racine 'ingest'
    $cfg['BatchesDir'] = Join-Path $racine 'batches'
    $cfg['_Source'] = ''
    $cfg['Hote'] = 'serveur.test'
    $cfg['CleSsh'] = Join-Path $racine 'cle'
    $cfg['KnownHosts'] = Join-Path $racine 'known_hosts'
    $cfg['SshExe'] = Join-Path $ici 'fake-ssh.cmd'
    $cfg['ScpExe'] = Join-Path $ici 'fake-scp.cmd'
    $cfg['DelaiSondageSecondes'] = 0
    $cfg['DelaiMaxLotSecondes'] = 120
    $cfg['ToleranceReseau'] = 6
    $json = '{"epreuve_source":"bac-test.pdf","numero_exercice":"1","matiere":"Maths","annee":2020,"statut":"brouillon",' +
    '"questions":[{"numero":"1","enonce_markdown":"q","corrige_markdown":"c"}]}'
    Write-Utf8 (Join-Path $racine 'ingest\cm\dos\dos_exercice_1.json') $json
    Save-Validation $cfg 'cm/dos' 'ok' 'valide' 'test'
    $null = Invoke-Prepare -Cfg $cfg -Unites @('cm/dos') -Approuver
    $lot = @(Get-LotsLocaux $cfg)[0].BatchId
    $env:FAKE_DIR = Join-Path $racine 'fake'
    $env:FAKE_ID = 'cm/dos/dos_exercice_1'
    Remove-Item Env:\FAKE_SCENARIO -ErrorAction SilentlyContinue
    return [pscustomobject]@{ Racine = $racine; Cfg = $cfg; Lot = $lot }
}

function Remove-BancTransport {
    param($Banc)
    Remove-Item Env:\FAKE_DIR, Env:\FAKE_SCENARIO, Env:\FAKE_ID -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $Banc.Racine -ErrorAction SilentlyContinue
}

function Get-Appels {
    param($Banc)
    $f = Join-Path $Banc.Racine 'fake\appels.log'
    if (-not (Test-Path $f)) { return @() }
    return @(Get-Content -LiteralPath $f)
}

function Test-Appele {
    param($Banc, [string]$Sous)
    return (@(Get-Appels $Banc | Where-Object { $_ -match "bash \S+ $Sous( |$)" }).Count -gt 0)
}

function Get-EtatLocal {
    param($Banc)
    return (Read-JsonFile (Join-Path $Banc.Cfg.BatchesDir "$($Banc.Lot)\etat.json")).etat
}

Describe 'Configuration distante et arguments' {
    BeforeEach { $script:b = New-BancTransport }
    AfterEach { Remove-BancTransport $script:b }

    It 'Test-ConfigDistante liste ce qui manque' {
        $c = Get-ConfigParDefaut
        $manques = Test-ConfigDistante $c
        ($manques -join ',') | Should Match 'Hote'
        ($manques -join ',') | Should Match 'CleSsh'
        (Test-ConfigDistante $script:b.Cfg).Count | Should Be 0
    }
    It 'refuse tout argument distant hors liste blanche' {
        { Invoke-Distant $script:b.Cfg 'statut' @('abc;rm -rf /') } | Should Throw
        { Invoke-Distant $script:b.Cfg 'statut' @('$(id)') } | Should Throw
        { Invoke-Distant $script:b.Cfg 'Statut;x' @() } | Should Throw
    }
    It 'ssh est lance avec cle dediee, hote epingle et sans interaction' {
        $null = Invoke-Distant $script:b.Cfg 'diagnostic'
        $ligne = (Get-Appels $script:b | Select-Object -First 1)
        $ligne | Should Match 'StrictHostKeyChecking=yes'
        $ligne | Should Match 'BatchMode=yes'
        $ligne | Should Match 'IdentitiesOnly=yes'
        $ligne | Should Match ([regex]::Escape("UserKnownHostsFile=$($script:b.Cfg.KnownHosts)"))
        $ligne | Should Match 'deploy@serveur.test'
        $ligne | Should Match 'bash /srv/edukora/deploy/sync-lot.sh diagnostic'
    }
    It 'doctor -Distant : serveur pret' {
        Invoke-DoctorDistant $script:b.Cfg | Should Be 0
    }
    It 'doctor -Distant : serveur sans la commande sync_contenu' {
        $env:FAKE_SCENARIO = 'diagnostic_ko'
        Invoke-DoctorDistant $script:b.Cfg | Should Be 2
    }
    It 'Get-LotLocal distingue un lot de creations seules' {
        $lot = Get-LotLocal $script:b.Cfg $script:b.Lot
        $lot.SeulementCreations | Should Be $true
        $lot.AvecRetraits | Should Be $false
        $m = Read-JsonFile (Join-Path $lot.Dir 'manifest.json')
        $m.contenus[0].operation = 'update'
        Write-JsonFile (Join-Path $lot.Dir 'manifest.json') $m
        (Get-LotLocal $script:b.Cfg $script:b.Lot).SeulementCreations | Should Be $false
    }
    It 'Get-LotLocal refuse un identifiant mal forme' {
        { Get-LotLocal $script:b.Cfg '../../x' } | Should Throw
    }
}

Describe 'publish : simulation et application' {
    BeforeEach { $script:b = New-BancTransport }
    AfterEach { Remove-BancTransport $script:b }

    It 'sans -Appliquer : envoie, verifie, recoit, simule, et ne sauvegarde ni n applique rien' {
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot | Should Be 0
        foreach ($s in 'ouvrir-lot', 'verifier-archive', 'recevoir', 'planifier') { (Test-Appele $script:b $s) | Should Be $true }
        foreach ($s in 'sauvegarde', 'appliquer', 'reprendre') { (Test-Appele $script:b $s) | Should Be $false }
        Test-Path (Join-Path $script:b.Racine "fake\incoming\$($script:b.Lot)\lot.zip") | Should Be $true
        Get-EtatLocal $script:b | Should Be 'planifie'
    }
    It 'avec -Appliquer : sauvegarde AVANT d appliquer, puis suit jusqu a la reussite' {
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 0
        $appels = Get-Appels $script:b
        $iSauv = [array]::FindIndex($appels, [Predicate[string]] { param($l) $l -match 'sync-lot.sh sauvegarde' })
        $iAppl = [array]::FindIndex($appels, [Predicate[string]] { param($l) $l -match 'sync-lot.sh appliquer' })
        ($iSauv -ge 0 -and $iAppl -gt $iSauv) | Should Be $true
        Get-EtatLocal $script:b | Should Be 'termine_ok'
    }
    It 'un lot de creations seules peut s appuyer sur une sauvegarde recente' {
        $null = Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer
        (Get-Appels $script:b | Where-Object { $_ -match 'sync-lot.sh sauvegarde' }) | Should Match '--max-age-h 24'
    }
    It 'un lot avec mises a jour exige une sauvegarde fraiche' {
        $lot = Get-LotLocal $script:b.Cfg $script:b.Lot
        $m = Read-JsonFile (Join-Path $lot.Dir 'manifest.json'); $m.contenus[0].operation = 'update'
        Write-JsonFile (Join-Path $lot.Dir 'manifest.json') $m
        $null = Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer
        (Get-Appels $script:b | Where-Object { $_ -match 'sync-lot.sh sauvegarde' }) | Should Not Match 'max-age-h'
    }
    It 'un lot deja applique ne se rejoue pas (idempotence, code 0)' {
        $env:FAKE_SCENARIO = 'deja_applique'
        $null = Initialize-LotServeur $script:b.Cfg (Get-LotLocal $script:b.Cfg $script:b.Lot)
        Remove-Item (Join-Path $script:b.Racine 'fake\appels.log')
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 0
        foreach ($s in 'sauvegarde', 'appliquer', 'planifier') { (Test-Appele $script:b $s) | Should Be $false }
    }
    It 'un serveur injoignable avant tout lancement est un echec certain (1), rien n est envoye' {
        $script:b.Cfg['SshExe'] = Join-Path $script:b.Racine 'inexistant.cmd'
        { Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer } | Should Throw
    }
}

Describe 'publish : cas d erreur' {
    BeforeEach { $script:b = New-BancTransport }
    AfterEach { Remove-BancTransport $script:b }

    It 'archive corrompue pendant le transfert : echec (1), jamais recue' {
        $env:FAKE_SCENARIO = 'archive_corrompue'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 1
        (Test-Appele $script:b 'recevoir') | Should Be $false
    }
    It 'scp en echec : echec (1)' {
        $env:FAKE_SCENARIO = 'scp_ko'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 1
    }
    It 'lot refuse par le serveur : echec (1)' {
        $env:FAKE_SCENARIO = 'recu_refuse'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 1
        (Test-Appele $script:b 'planifier') | Should Be $false
    }
    It 'conflits dans le plan : code 4, rien n est sauvegarde ni applique' {
        $env:FAKE_SCENARIO = 'conflit'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 4
        foreach ($s in 'sauvegarde', 'appliquer') { (Test-Appele $script:b $s) | Should Be $false }
    }
    It 'sauvegarde en echec : rien n est applique (1)' {
        $env:FAKE_SCENARIO = 'sauvegarde_ko'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 1
        (Test-Appele $script:b 'appliquer') | Should Be $false
    }
    It 'verrou pris (deploiement ou autre lot) : rien n est lance (1)' {
        $env:FAKE_SCENARIO = 'verrou_pris'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 1
        Get-EtatLocal $script:b | Should Be 'sauvegarde_ok'
    }
    It 'des retraits exigent -ConfirmerRetraits (5)' {
        $lot = Get-LotLocal $script:b.Cfg $script:b.Lot
        $m = Read-JsonFile (Join-Path $lot.Dir 'manifest.json'); $m.contenus[0].operation = 'retirer'
        Write-JsonFile (Join-Path $lot.Dir 'manifest.json') $m
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 5
        (Test-Appele $script:b 'ouvrir-lot') | Should Be $false
    }
    It 'application partielle : code 4' {
        $env:FAKE_SCENARIO = 'partiel'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 4
        Get-EtatLocal $script:b | Should Be 'termine_echec'
    }
    It 'echec simple sans conflit : code 1' {
        $env:FAKE_SCENARIO = 'echoue_simple'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 1
    }
    It 'processus interrompu cote serveur (a_verifier) : indetermine (3)' {
        $env:FAKE_SCENARIO = 'a_verifier'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 3
    }
    It 'le serveur n a pas demarre l application : echec (1), pas d attente infinie' {
        $env:FAKE_SCENARIO = 'non_demarre'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 1
    }
    It 'reussi avec avertissements : code 0' {
        $env:FAKE_SCENARIO = 'avertissements'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 0
    }
}

Describe 'coupures reseau apres le lancement' {
    BeforeEach { $script:b = New-BancTransport }
    AfterEach { Remove-BancTransport $script:b }

    It 'coupures transitoires pendant le suivi : le lot est suivi jusqu au bout (0)' {
        $env:FAKE_SCENARIO = 'reseau_transitoire'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 0
        Get-EtatLocal $script:b | Should Be 'termine_ok'
    }
    It 'coupure PENDANT le lancement mais lot demarre : confirme par statut, puis suivi (0)' {
        $env:FAKE_SCENARIO = 'lancement_reseau_coupe'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 0
    }
    It 'serveur muet apres le lancement : INDETERMINE (3), jamais conclu a un echec' {
        $env:FAKE_SCENARIO = 'reseau_permanent'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 3
        Get-EtatLocal $script:b | Should Be 'indetermine'
    }
}

Describe 'resume' {
    BeforeEach { $script:b = New-BancTransport }
    AfterEach { Remove-BancTransport $script:b }

    It 'lot inconnu du serveur : echec (1)' {
        Invoke-Resume -Cfg $script:b.Cfg -BatchId $script:b.Lot | Should Be 1
    }
    It 'lot en cours : suivi jusqu a la fin (0)' {
        $null = Initialize-LotServeur $script:b.Cfg (Get-LotLocal $script:b.Cfg $script:b.Lot)
        $null = Invoke-Distant $script:b.Cfg 'appliquer' @($script:b.Lot)
        Invoke-Resume -Cfg $script:b.Cfg -BatchId $script:b.Lot | Should Be 0
    }
    It 'etat a verifier : n agit pas sans -Reprendre (3), puis reprend avec -Reprendre' {
        $null = Initialize-LotServeur $script:b.Cfg (Get-LotLocal $script:b.Cfg $script:b.Lot)
        $env:FAKE_SCENARIO = 'a_verifier_initial'
        Invoke-Resume -Cfg $script:b.Cfg -BatchId $script:b.Lot | Should Be 3
        (Test-Appele $script:b 'reprendre') | Should Be $false
        $env:FAKE_SCENARIO = 'a_verifier_initial'
        $null = Invoke-Resume -Cfg $script:b.Cfg -BatchId $script:b.Lot -Reprendre
        (Test-Appele $script:b 'reprendre') | Should Be $true
    }
}

Describe 'resoudre, reference, rollback-info' {
    BeforeEach { $script:b = New-BancTransport }
    AfterEach { Remove-BancTransport $script:b }

    It 'resoudre ecrit la decision depuis le plan du serveur et reconstruit l archive' {
        $env:FAKE_SCENARIO = 'conflit'
        $avant = (Get-FileHash -LiteralPath (Join-Path $script:b.Cfg.BatchesDir "lot-$($script:b.Lot).zip")).Hash
        Invoke-Resoudre -Cfg $script:b.Cfg -BatchId $script:b.Lot -Decision 'ecraser' -Motif 'correction relue' | Should Be 0
        $dec = (Read-JsonFile (Join-Path $script:b.Cfg.BatchesDir "$($script:b.Lot)\approbations.json")).decisions
        @($dec).Count | Should Be 1
        $dec[0].id_stable | Should Be 'cm/dos/dos_exercice_1'
        $dec[0].empreinte_etat_prod_vue | Should Be ('e' * 64)
        $dec[0].motif | Should Be 'correction relue'
        $dec[0].version_proposee.Length | Should Be 64
        (Get-FileHash -LiteralPath (Join-Path $script:b.Cfg.BatchesDir "lot-$($script:b.Lot).zip")).Hash | Should Not Be $avant
        Get-EtatLocal $script:b | Should Be 'pret_local'
    }
    It 'resoudre : ecraser sans motif est refuse' {
        $env:FAKE_SCENARIO = 'conflit'
        Invoke-Resoudre -Cfg $script:b.Cfg -BatchId $script:b.Lot -Decision 'ecraser' | Should Be 2
    }
    It 'resoudre puis publish : l archive modifiee est renvoyee et le conflit est leve' {
        $env:FAKE_SCENARIO = 'conflit_puis_resolu'
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 4
        Invoke-Resoudre -Cfg $script:b.Cfg -BatchId $script:b.Lot -Decision 'garder_prod' | Should Be 0
        Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer | Should Be 0
        (Get-Appels $script:b | Where-Object { $_ -match '^scp' -and $_ -match 'incoming/.+/lot\.zip$' } | Measure-Object).Count | Should Be 2
    }
    It 'reference ecrit les empreintes de production' {
        Invoke-Reference $script:b.Cfg | Should Be 0
        $ref = Read-JsonFile (Join-Path $script:b.Cfg.BatchesDir '_reference-prod.json')
        $ref.contenus.PSObject.Properties.Name | Should Be 'exercice|cm/a'
    }
    It 'rollback-info n agit pas et nomme la sauvegarde du lot' {
        $null = Invoke-Publish -Cfg $script:b.Cfg -BatchId $script:b.Lot -Appliquer
        Remove-Item (Join-Path $script:b.Racine 'fake\appels.log')
        Show-RollbackInfo $script:b.Cfg $script:b.Lot | Should Be 0
        @(Get-Appels $script:b).Count | Should Be 0
    }
}
