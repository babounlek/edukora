# Synchronisation des contenus par lots : manuel d'exploitation

Complète [README-TUNNEL.md](README-TUNNEL.md). Ce canal met à jour **le contenu** (exercices, cours, quiz) de la
production **sans rebuild Docker ni redémarrage** : le poste Windows prépare un lot (archive + SHA-256), le transfère
en `scp`, et un moteur Django déjà en place (`manage.py sync_contenu`) le contrôle, le simule, puis l'applique.
Conception : [SPEC-SYNC-CONTENU.md](SPEC-SYNC-CONTENU.md). État des lieux : [AUDIT-SYNC-CONTENU.md](AUDIT-SYNC-CONTENU.md).

| Canal | Quoi | Quand l'utiliser |
|---|---|---|
| **Lots** (ce document) | créer ou **corriger** exercices, cours, quiz ; retirer un contenu | tout contenu, surtout une correction |
| Contenu (`contenu.sh`, Actions) | créations seules, depuis git | repli ; ne corrige rien |
| Application (`deploy.sh`) | code, migrations, images | une fois pour installer le moteur, puis à chaque version |

## Garanties (testées)

- Une correction met à jour le contenu **sur place** : les copies, les exercices faits et les progressions des élèves
  survivent. Jamais de suppression ; un retrait passe le contenu en `REJETE`.
- `statut`, `published_at` et `est_vitrine` d'un contenu existant ne sont **jamais** modifiés par un lot.
- Un contenu retouché en production par un autre moyen n'est **jamais écrasé** sans une décision humaine liée à l'état
  exact que vous avez vu.
- Un lot rejoué ne fait rien. Une coupure SSH n'interrompt rien et n'est **jamais** prise pour un échec : le suivi
  interroge le serveur.
- Un lot et un déploiement ne tournent jamais en même temps (verrou partagé).
- Une sauvegarde Postgres **vérifiée** précède toute modification.

## Installation (une seule fois)

### 1. Sur le serveur (application d'abord)
1. Commit des fichiers de la chaîne, **Release** puis **Deploy** : la migration `synchro` (additive) et la commande
   `sync_contenu` arrivent par le canal Application.
2. En SSH, depuis le clone (`/srv/edukora`) :
   ```bash
   bash deploy/sync-lot.sh preparer-dossiers      # crée /srv/edukora-lots (droits 700)
   bash deploy/sync-lot.sh diagnostic             # tout doit être « true » ; version déployée correcte
   bash deploy/diagnostic-serveur.sh              # lecture seule : SPACES_BUCKET, clone propre, etc.
   ```
3. **À consigner avant le premier lot réel** (réponses de `diagnostic-serveur.sh`) : les fichiers sont-ils sur Spaces ou
   sur disque ? `SPACES_BACKUP_BUCKET` est-il distinct de `SPACES_BUCKET` ? Un test de restauration a-t-il déjà été fait ?

### 2. Une clé SSH dédiée (jamais celle de votre poste)
Sur le poste :
```powershell
ssh-keygen -t ed25519 -C "edukora-lots" -f $env:USERPROFILE\.ssh\edukora_lots_ed25519
```
Ajoutez la clé **publique** au `authorized_keys` de l'utilisateur `deploy` du serveur. Récupérez l'empreinte de l'hôte
**par un autre canal que la connexion elle-même** (console du Droplet) puis construisez un `known_hosts` dédié :
```powershell
ssh-keyscan -t ed25519 <hote> | Out-File -Encoding ascii $env:USERPROFILE\.ssh\edukora_known_hosts
ssh-keygen -lf $env:USERPROFILE\.ssh\edukora_known_hosts     # comparer à l'empreinte de la console
```
L'outil se connecte avec `StrictHostKeyChecking=yes` et ce seul fichier : une empreinte inconnue ou changée = refus.

### 3. Le poste
Copiez `scripts/edukora.config.example.psd1` en `scripts/edukora.config.psd1` (ignoré par git) et renseignez `Hote`,
`Utilisateur`, `CleSsh`, `KnownHosts`. Aucun mot de passe nulle part. Puis :
```powershell
.\scripts\edukora.ps1 doctor              # prérequis locaux
.\scripts\edukora.ps1 doctor -Distant     # serveur : docker, flock, dossier des lots, commande sync_contenu
```

### 4. Test de restauration (avant le premier lot qui corrige)
Une sauvegarde qui n'a jamais été restaurée n'est pas une sauvegarde.
```bash
bash deploy/sync-lot.sh sauvegarde 20260101-000000-00000000      # sur le serveur : crée et vérifie un dump
bash deploy/sync-lot.sh test-restauration avant-20260101-000000-00000000.dump
```
Il restaure dans une base jetable, compare les compteurs des tables de contenu, puis supprime la base jetable.

## Routine : publier un contenu

```powershell
# 1. Produire le contenu (skills) puis le valider et l'ingérer en LOCAL
.\scripts\edukora.ps1 ingest-local -Unite cm/<dossier>          # ingestion + tunnel de validation

# 2. (corrections) récupérer l'état de la production, pour que le lot dise create / update / noop
.\scripts\edukora.ps1 reference                                  # -> batches\_reference-prod.json

# 3. Préparer le lot (relecture du résumé, puis « oui » ou -Approuver)
.\scripts\edukora.ps1 prepare -Unite cm/<dossier> -Reference batches\_reference-prod.json -Nom "correction maths"

# 4. SIMULER sur le serveur : envoi, vérification, plan. Rien n'est écrit.
.\scripts\edukora.ps1 publish -BatchId <id>

# 5. Appliquer : sauvegarde vérifiée, application détachée, suivi jusqu'au bout
.\scripts\edukora.ps1 publish -BatchId <id> -Appliquer
```

`status` liste les lots locaux ; `status -BatchId <id>` montre leurs opérations.

### Codes de sortie (utilisables dans un script)
| Code | Sens | Action |
|---|---|---|
| 0 | succès (y compris « déjà appliqué ») | — |
| 1 | échec **certain** : rien n'a été modifié, ou restauration propre | corriger, relancer |
| 2 | usage ou prérequis (configuration, SSH, serveur non prêt) | `doctor` / `doctor -Distant` |
| 3 | **indéterminé** : le serveur ne répond plus après le lancement | **ne pas relancer** : `resume -BatchId <id>` |
| 4 | conflits ou contenus non appliqués | `resoudre`, puis `publish -Appliquer` |
| 5 | approbation ou confirmation manquante | relancer avec `-Approuver` / `-ConfirmerRetraits` |

## Quand le plan montre des conflits

`publish` s'arrête (code 4) et liste les contenus bloquants. Causes :

| Résultat du plan | Signification | Décision typique |
|---|---|---|
| `adoption_a_confirmer` | ce contenu existe en production **sans avoir jamais été synchronisé** et diffère du JSON | `garder_prod` (la production devient la base) ou `ecraser` (appliquer le JSON) |
| `conflit_etat` | modifié en production (admin, campagne de correctifs) depuis la dernière synchronisation | `garder_prod` ou `ecraser` après lecture du diff |
| `conflit_version` | un autre lot a fait avancer la production depuis votre référence | refaire `reference` puis `prepare` |
| `conflit_identite` | fichier renommé, clé naturelle changée, ou contenu purgé en production | renommage : revenir au nom d'origine ; purge : `recreer` |
| `structure_modifiee` | une question / figure / rappel de la production est absent du JSON : **jamais supprimé** | corriger le JSON |
| `rejete_validation` | la correction produirait un exercice cassé (porte du tunnel) | corriger le contenu |
| `correction_hors_perimetre` | le JSON a changé mais aucun champ synchronisé (ex. consigne ou durée de l'épreuve) | corriger dans l'admin |

```powershell
# Voir le détail : batches\<id>\plan-serveur.json
.\scripts\edukora.ps1 resoudre -BatchId <id> -Decision garder_prod                       # tout ce qui bloque
.\scripts\edukora.ps1 resoudre -BatchId <id> -Decision ecraser -Motif "correction relue" -Ids cm/dossier/fichier
.\scripts\edukora.ps1 resoudre -BatchId <id> -Decision recreer -Ids cm/dossier/fichier  # contenu purgé en prod
.\scripts\edukora.ps1 publish  -BatchId <id> -Appliquer
```
Une décision `ecraser` cite l'état de production que **vous** avez vu et la version du lot que vous avez relue : elle
ne s'applique jamais à autre chose. `garder_prod` sur un contenu jamais synchronisé enregistre la production comme base :
il n'est plus proposé en adoption et une correction ultérieure s'applique proprement dessus.

> Mesure faite sur la base locale (140 contenus tirés au hasard) : environ un tiers du corpus historique diffère de ses
> JSON (thèmes fusionnés par des campagnes, figures « sans filigrane », cours renommés). Le premier contact avec le
> corpus historique passe donc par ces décisions ; faites-les par unité, en relisant les écarts (`diff`).

## Retraits
Un retrait passe le contenu en `REJETE` (visible nulle part, rien n'est supprimé). Il se prépare avec un fichier
`retraits.json` (`[{"type":"exercice","id_stable":"...","motif":"..."}]`) passé à `prepare -Retraits`, et exige
`publish -Appliquer -ConfirmerRetraits`. Un retrait et une publication du même contenu dans le même lot sont refusés.

**Remplacer une épreuve** (ex. une épreuve à deux sujets ingérée en un seul bloc) : créer les nouvelles épreuves, puis retirer
l'ancienne. Types de retrait : `exercice`, `cours`, `quiz` et `lecon` (une épreuve entière, jamais publiée par lot). Un contenu
ingéré avant la chaîne n'a pas de journal : le retrait porte alors sa `cle_naturelle`, et lui seul le désigne (absent ou ambigu =
erreur, jamais un choix au hasard). `outil_lot.py retraits <ingest> <unité> --motif "..." --sortie retraits.json` produit les
retraits des exercices d'une unité et de leur leçon. Les cours ne sont jamais retirés par cette commande : ils se rattachent par
compétence et servent à d'autres épreuves ; un nouveau cours de même titre est dédoublonné vers l'existant. Les retraits passent
toujours après les créations du lot.

## Coupure, panne, reprise

| Situation | Ce qui se passe | Que faire |
|---|---|---|
| Wi-Fi coupé **avant** le lancement | échec certain (1), rien n'a bougé | relancer `publish` |
| Wi-Fi coupé **pendant** l'application | l'application continue sur le serveur (détachée) ; le suivi tolère les coupures | relancer rien : `resume -BatchId <id>` |
| Le serveur ne répond plus après le lancement | code 3, état `indetermine` | `resume -BatchId <id>` (interroge, ne relance pas) |
| Conteneur redémarré en plein lot | lot `a_verifier` | `resume -BatchId <id> -Reprendre` : seules les opérations non terminées sont rejouées |
| Lot partiel | les contenus sans conflit sont appliqués, les autres attendent | `resoudre` puis `publish -Appliquer -Reprendre` |
| Déploiement lancé pendant un lot | `deploy.sh` refuse (verrou) | attendre la fin du lot |

Sur le serveur : `bash deploy/sync-lot.sh statut <id>` ; journal `/srv/edukora-lots/journaux/<id>.log` ;
`docker compose exec backend python manage.py sync_contenu statut <id> --detail`.

## Retour arrière
`.\scripts\edukora.ps1 rollback-info -BatchId <id>` affiche la procédure (aucune action). En pratique : un lot corrige sur
place et ne supprime rien, donc **un nouveau lot** corrige une erreur ; pour dépublier, un lot avec retrait. En dernier
recours : la sauvegarde `avant-<id>.dump` (`/srv/edukora-lots/sauvegardes`, 8 conservées, plus la copie hors site de
`backup.sh`), restaurée selon [README-TUNNEL.md](README-TUNNEL.md) « Si ça tourne mal ».

## Entretien
- `bash deploy/sync-lot.sh nettoyer --apres-jours 7` liste les anciens fichiers remplacés (figures, PDF de sujet) ;
  `--appliquer` les supprime, **seulement** s'ils ne sont plus référencés (champ fichier **ou** URL citée dans un texte,
  y compris l'historique des quiz joués).
- `bash deploy/sync-lot.sh verifier-fichiers` : références sans fichier (rapport seul).
- Après un changement du code de rendu qui modifie légitimement les contenus compilés :
  `manage.py sync_contenu rafraichir-journal` (liste) puis `--confirme`.

## Limites connues
- Types couverts : exercices (questions, figures, rappels), cours, items de quiz. Inédites, programme officiel : hors lots.
- `Lesson.content_markdown` (contenu compilé de l'épreuve) n'est pas protégé contre une retouche manuelle ; les champs
  de la `Lesson` (consigne, durée…) ne sont pas synchronisés (`correction_hors_perimetre`).
- `quiz.source_exercises` (identifiants de la base locale) n'est pas appliqué en production.
- Un cours dont le titre existe déjà est rattaché au cours existant au lieu d'être créé (règle de l'ingestion historique).
- Le PDF de sujet est régénéré sous un nouveau nom ; l'ancien reste jusqu'à `nettoyer`.

## Tests
```powershell
Invoke-Pester .\scripts\tests                                   # poste (faux serveur, aucun réseau)
cd backend\synchro; python -I -m unittest discover -s . -p "test_*.py"    # outil de lot (stdlib seule)
docker exec edukora-backend-1 python manage.py test synchro     # moteur (SQLite ; PostgreSQL : réglage temporaire)
docker cp deploy edukora-backend-1:/tmp/deploy-tests; docker exec edukora-backend-1 bash /tmp/deploy-tests/tests/test-sync-lot.sh
```
