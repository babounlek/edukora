# Faux serveur pour les tests Pester : imite deploy/sync-lot.sh sans reseau ni Docker.
# Etat dans $env:FAKE_DIR ; comportement choisi par $env:FAKE_SCENARIO (voir les tests).
$ErrorActionPreference = 'Stop'
$dir = $env:FAKE_DIR
$scenario = $env:FAKE_SCENARIO
$commande = $args[-1]
Add-Content -LiteralPath (Join-Path $dir 'appels.log') -Value ("ssh " + ($args -join ' | '))

function Sortie($objet) { ($objet | ConvertTo-Json -Depth 12 -Compress) }
function Lire($lot, $cle, $defaut = '') { $f = Join-Path $dir "lots\$lot\$cle"; if (Test-Path $f) { (Get-Content -LiteralPath $f -Raw).Trim() } else { $defaut } }
function Ecrire($lot, $cle, $valeur) { $d = Join-Path $dir "lots\$lot"; New-Item -ItemType Directory -Force -Path $d | Out-Null; Set-Content -LiteralPath (Join-Path $d $cle) -Value $valeur }

if ($commande -notmatch '^bash (\S+) (\S+)\s*(.*)$') { Write-Output (Sortie @{ statut = 'refuse'; erreur = 'commande inattendue' }); exit 2 }
$sous = $Matches[2]
$reste = @($Matches[3] -split '\s+' | Where-Object { $_ })
$lot = if ($reste.Count -gt 0) { $reste[0] } else { '' }

switch ($sous) {
    'diagnostic' {
        $ok = $scenario -ne 'diagnostic_ko'
        Write-Output (Sortie ([ordered]@{ statut = 'ok'; docker = $ok; flock = $true; dossier_lots = $true; droits_dossier_lots = '700'
                    commande_sync_contenu = $ok; version_deployee = 'abc1234'; disque_libre_go = 40; utilisateur = 'deploy' }))
    }
    'ouvrir-lot' { New-Item -ItemType Directory -Force -Path (Join-Path $dir "incoming\$lot") | Out-Null; Write-Output (Sortie @{ statut = 'ok' }) }
    'verifier-archive' {
        $zip = Join-Path $dir "incoming\$lot\lot.zip"; $shaf = "$zip.sha256"
        if (-not ((Test-Path $zip) -and (Test-Path $shaf))) { Write-Output (Sortie @{ statut = 'refuse'; erreur = 'archive ou empreinte absente' }); exit 1 }
        $attendu = ((Get-Content -LiteralPath $shaf -Raw).Trim() -split '\s+')[0].ToLower()
        $obtenu = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLower()
        if ($attendu -ne $obtenu) { Write-Output (Sortie @{ statut = 'refuse'; erreur = 'SHA-256 differente : transfert corrompu' }); exit 1 }
        Write-Output (Sortie @{ statut = 'ok'; sha256 = $obtenu })
    }
    'recevoir' {
        if ($scenario -eq 'recu_refuse') { Write-Output (Sortie @{ statut = 'refuse'; erreur = 'empreinte recalculee differente du manifeste' }); exit 1 }
        if ((Lire $lot 'statut') -eq '') { Ecrire $lot 'statut' 'verifie' }
        Write-Output (Sortie @{ batch_id = $lot; statut = (Lire $lot 'statut'); operations = 2 })
    }
    'planifier' {
        $uploads = [int](Lire $lot 'uploads' '1')
        $conflit = ($scenario -eq 'conflit') -or ($scenario -eq 'conflit_puis_resolu' -and $uploads -le 1)
        if ($conflit) {
            $id = $env:FAKE_ID
            Write-Output (Sortie ([ordered]@{ batch_id = $lot; compteurs = @{ adoption_a_confirmer = 1; cree = 1 }; bloquants = 1
                        plan = @(
                            @{ type = 'exercice'; id_stable = $id; operation = 'create'; resultat_prevu = 'adoption_a_confirmer'
                                detail = @{ classe = 'adoption'; empreinte_etat_prod_vue = ('e' * 64); diff = @('questions.1.themes') } },
                            @{ type = 'exercice'; id_stable = 'autre'; operation = 'create'; resultat_prevu = 'cree'; detail = @{ classe = 'create' } }) }))
            exit 4
        }
        Write-Output (Sortie ([ordered]@{ batch_id = $lot; compteurs = @{ cree = 2 }; bloquants = 0
                    plan = @(@{ type = 'exercice'; id_stable = 'a'; operation = 'create'; resultat_prevu = 'cree'; detail = @{ classe = 'create' } }) }))
    }
    'sauvegarde' {
        if ($scenario -eq 'sauvegarde_ko') { Write-Output (Sortie @{ statut = 'refuse'; erreur = 'pg_dump en echec' }); exit 1 }
        Write-Output (Sortie ([ordered]@{ statut = 'ok'; reutilisee = ($reste -contains '--max-age-h'); dump = "avant-$lot.dump"; octets = 5000; hors_site = $true }))
    }
    { $_ -in @('appliquer', 'reprendre') } {
        if ($scenario -eq 'verrou_pris') { Write-Output (Sortie @{ statut = 'verrou_pris' }); exit 75 }
        Ecrire $lot 'statut' 'en_cours'; Ecrire $lot 'polls' '0'
        if ($scenario -eq 'lancement_reseau_coupe') { exit 255 }
        Write-Output (Sortie @{ statut = 'lance'; batch_id = $lot; journal = "journaux/$lot.log" })
    }
    'statut' {
        $etat = Lire $lot 'statut'
        if ($etat -eq '') { Write-Output (Sortie @{ batch_id = $lot; statut = 'inconnu' }); exit 1 }
        if ($scenario -eq 'deja_applique') { Write-Output (Sortie @{ batch_id = $lot; statut = 'reussi'; compteurs = @{ cree = 2 } }); exit 0 }
        if ($scenario -eq 'a_verifier_initial' -and $etat -eq 'verifie') { Write-Output (Sortie @{ batch_id = $lot; statut = 'a_verifier'; compteurs = @{} }); exit 3 }
        if ($etat -eq 'en_cours') {
            $polls = [int](Lire $lot 'polls') + 1; Ecrire $lot 'polls' $polls
            if ($scenario -eq 'reseau_permanent') { exit 255 }
            if ($scenario -eq 'reseau_transitoire' -and $polls -le 3) { exit 255 }
            if ($scenario -eq 'non_demarre') { Ecrire $lot 'statut' 'verifie'; $etat = 'verifie' }
            elseif ($polls -lt 3) { Write-Output (Sortie @{ batch_id = $lot; statut = 'en_cours'; compteurs = @{} }); exit 0 }
            else {
                $final = switch ($scenario) {
                    'partiel' { 'partiel' }
                    'a_verifier' { 'a_verifier' }
                    'echoue_simple' { 'echoue' }
                    'avertissements' { 'reussi_avec_avertissements' }
                    default { 'reussi' }
                }
                Ecrire $lot 'statut' $final; $etat = $final
            }
        }
        $compteurs = switch ($etat) { 'partiel' { @{ cree = 1; conflit_etat = 1 } } 'echoue' { @{ erreur = 2 } } default { @{ cree = 2 } } }
        $extra = @{}
        if ($etat -eq 'reussi_avec_avertissements') { $extra.avertissements = @('generate_sujet_pdfs : Playwright absent') }
        Write-Output (Sortie ($extra + @{ batch_id = $lot; statut = $etat; compteurs = $compteurs }))
    }
    'verifier-fichiers' { Write-Output (Sortie @{ references_sans_fichier = @(); sha_divergents = @() }) }
    'reference' { Write-Output (Sortie @{ genere_le = '2026-10-25T00:00:00Z'; contenus = @{ 'exercice|cm/a' = @{ empreinte_source = 'x'; empreinte_etat = 'y'; version = 1 } } }) }
    default { Write-Output (Sortie @{ statut = 'refuse'; erreur = "sous-commande inconnue $sous" }); exit 2 }
}
exit 0
