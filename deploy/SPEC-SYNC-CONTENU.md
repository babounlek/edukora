# Spécification : chaîne de synchronisation des contenus (option B, lots par archive)

Phase 2 du chantier ([PROMPT](PROMPT-SYNC-CONTENU.md) → [AUDIT](AUDIT-SYNC-CONTENU.md) → **cette spec**).
Point d'arrêt n°2 : rien n'est codé. Cette spec est faite pour être **testée** : chaque règle a un test
d'acceptation en §12.

## 0. Décisions actées (point d'arrêt n°1)

| # | Décision | Origine |
|---|---|---|
| D1 | **Option B** : lots par archive, transfert `scp`/`ssh` depuis PowerShell, exécution côté Django. `contenu.sh` reste la voie de secours pour de simples créations. | vous |
| D2 | Une **correction** d'un contenu déjà publié se met à jour **sur place** et reste publiée, mais seulement après (a) approbation humaine du lot à la préparation, (b) passage de la porte de validation **avant commit** ; un objet qui échoue la porte est rejeté (jamais publié cassé, jamais auto-dépublié). Les inédites restent en BROUILLON + clic admin. | recommandation retenue |
| D3 | **Retrait = statut `REJETE`** (seul état stable face au gate d'ingestion). **Suppression physique interdite en v1** : elle n'est pas implémentée. | recommandation retenue |
| D4 | **Périmètre v1** : exercices (avec questions, figures, rappels), cours, items de quiz. Hors v1 : inédites (flux admin existant), programme (déjà upsert, reste sur `contenu.sh`). | recommandation retenue |
| D5 | Les **550 JSON `cm/` ignorés par git (93 dossiers GCE, mesure de la phase 3)** entrent par un lot de rattrapage, sur une **liste que vous validez** (produite en phase 3), jamais en bloc silencieux. | recommandation retenue |
| D6 | Les inconnus du serveur (§9 de l'audit) sont levés par **vous** avec `deploy/diagnostic-serveur.sh` ; je n'accède pas à la production. | recommandation retenue |

## 1. Principes de conception (dérivés de l'audit)

1. **Jamais de suppression/recréation** d'un exercice, d'une question ou d'un cours existants (cascade sur
   `ExerciceFait`, `SimulationReponse`, `LectureProgress`…). La mise à jour est **in situ**, par clé naturelle.
2. **La synchronisation ne change jamais `statut`, `published_at`, `est_vitrine`** d'un objet existant (propriété
   de l'admin), sauf l'opération explicite `retirer`/`reintegrer`.
3. **Aucune écriture hors du périmètre pédagogique** (§3.1). Liste fermée, testée.
4. **Aucun effacement déduit d'une absence** : une question, une figure ou un contenu absent du lot est
   signalé comme `structure_modifiee`/ignoré, jamais supprimé.
5. **Tout est rejouable** : lot identique → no-op ; objet identique → no-op.
6. **Le serveur est la source de vérité de l'état** : le client ne conclut jamais à l'échec d'un lot sans
   avoir interrogé `statut`.
7. **Réutiliser avant de réécrire** : les adaptateurs appellent les helpers existants de `catalog.ingestion`
   et `quiz.ingestion` (normalisation, thèmes, savoirs). Toute extraction de helper est couverte par un test
   de non-régression de la voie « création » existante.

## 2. Identités et versions

| Notion | Définition | Stockage |
|---|---|---|
| **Identifiant stable** (`id_stable`) | Chemin relatif du JSON d'ingestion, sans extension, en minuscules d'origine conservées : ex. `cm/bac-c-maths-1984-cameroun/bac-c-maths-1984-cameroun_exercice_1`. Pour un quiz : `external_id` de l'item. Pour un cours : `cours_id`. | `synchro.ContenuSynchro` |
| **Clé naturelle** | Clé d'ingestion existante : exercice = `(epreuve_source, numero_exercice, matière, année, pays, variante, paper)` ; cours = `external_id` ; item = `external_id`. Sert à **retrouver l'objet** en prod. **Immuable** : si elle résout un autre objet que celui du journal → conflit `identite_changee`. | `ContenuSynchro.cle_naturelle` |
| **Identifiant de lot** (`batch_id`) | `YYYYMMDD-HHMMSS-<8 hex du hash du manifeste>`. | `synchro.LotSynchro` |
| **Version du contenu** | Entier croissant par `ContenuSynchro` + deux empreintes (ci-dessous). | `ContenuSynchro.version` |

Deux empreintes SHA-256, volontairement distinctes :
- **`empreinte_source`** : JSON d'ingestion **canonique** (clés triées, `ensure_ascii=False`, séparateurs
  compacts, normalisation Unicode NFC, fins de ligne `\n`, clé `statut` exclue) suivi de la liste triée des
  SHA-256 des fichiers déclarés. Identique côté poste et côté serveur (même code Python partagé).
- **`empreinte_etat`** : SHA-256 d'une **projection canonique de l'objet en base**, limitée aux champs de
  contenu mutables (§3.2). Elle sert à détecter une modification faite en production **par un autre
  mécanisme** (admin, fusion de Tags, commande de correctif). Les champs dérivés (`enonce_markdown`/`corrige_markdown`
  compilés, `updated_at`, `statut`, `published_at`) en sont exclus.

Les empreintes ne remplacent pas la clé naturelle : elles ne servent qu'à dire « a changé / n'a pas changé ».

## 3. Ce que la synchronisation écrit et ne touche pas

### 3.1 Liste fermée des modèles écrits (v1)
`catalog`: `Exercise`, `Question`, `Figure`, `RappelDeMethode`, `Cours`, `Tag` (création seule, jamais
modification/fusion) · `quiz`: `CompetenceItem`, `CompetenceItemFigure` · `Lesson` (recompilation seule,
`compile_from_exercises`, aucun champ éditorial) · `synchro.*` (journal).
**Tout le reste est interdit** : users, subscriptions, payments, quiz (activité), inedit (tentatives), access,
simulations, fiches, analytics, relances, whatsapp, `Plan`, `ReglagesTelechargement`, référentiel pays/matières.
Test T11 : un garde-fou (`assert_ecritures_autorisees`) enregistre les modèles écrits pendant un lot et échoue
si l'un n'est pas dans la liste.

### 3.2 Champs mutables par type (projection d'état et mise à jour)
- **Exercise** : `points`, `groupes`, `groupes_verifies`, `enonce_intro_markdown`, `incertitudes`,
  `mots_cles_recherche` (par nom). **Questions** (appariées par `numero`) : `ordre`, `enonce_markdown`,
  `corrige_markdown`, `difficulte_estimee`, `type_reponse`, `choix`, `reponse_correcte`, `points`,
  `savoir_officiel` (par id), `themes` (par nom). **Figures** (appariées par `external_id`) : `image`
  (SHA-256 du fichier), `page_source`, `type_figure`, `legende`, `indispensable`, `lisibilite`, `origine`.
  **Rappels** (par `external_id`) : `competence`, `contenu_markdown`. Après écriture : `compile_from_questions()`
  puis `lesson.compile_from_exercises()`.
- **Cours** : `titre`, `sous_theme`, `duree_estimee_min`, `tags`, `sections_raw`, `content_markdown`, `cursus`,
  `cursus_recommandes`. (`slug`, `statut` inchangés.)
- **CompetenceItem** : `theme`, `savoir_officiel`, `enonce_markdown`, `corrige_markdown`, `difficulte_estimee`,
  `type_reponse`, `choix`, `reponse_correcte`, `cursus`, `source_exercises`, figures. Les `QuizQuestion` déjà
  jouées portent un instantané : l'historique des élèves n'est pas affecté.
- **Structure modifiée** : question, figure ou rappel **présent en prod mais absent du JSON** ⇒ opération
  `structure_modifiee`, **non appliquée**, rapportée (cascade `SimulationReponse.sous_question`). L'ajout est permis.

## 4. Format du lot

Une archive `lot-<batch_id>.zip` + `lot-<batch_id>.zip.sha256`. Contenu :

```
manifest.json
SHA256SUMS                      # tous les fichiers du lot
approbations.json               # décisions humaines (conflits, retraits) - voir §6
ingest/<pays>/<dossier>/...     # MIROIR de backend/ingest : JSON d'ingestion octet pour octet + PNG voisins
rapport-prepare.json            # validation locale, diff, versions de référence
```

Le **miroir** permet de réutiliser tel quel le code d'ingestion (`source_dir`, `_attach_figures` cherche les PNG
à côté du JSON). `manifest.json` :

```json
{
  "schema_sync": 1,
  "batch_id": "20261101-101500-3fa9c2d1",
  "cree_le": "2026-11-01T10:15:00Z",
  "cree_par": "poste:<nom machine>",
  "application": {"sha_attendu": "<sha déployé en prod>", "migrations_min": {"catalog": "00NN", "synchro": "0001"}},
  "reference_prod": {"exportee_le": "...", "sha256": "..."},
  "options": {"tout_ou_rien": false, "adopter": false},
  "contenus": [
    {"type": "exercice", "id_stable": "cm/…/…_exercice_1",
     "cle_naturelle": {"epreuve_source": "...", "numero_exercice": "1", "pays": "cm", "...": "..."},
     "operation": "create|update|noop|retirer|reintegrer",
     "version_reference": "<empreinte_source appliquée en prod, ou null>",
     "version_proposee": "<empreinte_source>",
     "fichier": "ingest/cm/…/…_exercice_1.json",
     "fichiers": [{"nom": "…_fig_1.png", "sha256": "…", "taille": 12345}],
     "relations": {"cours": ["…"], "themes": ["…"]},
     "validation": {"locale": "ok", "tunnel": "ok", "relecture_humaine": "non_requise|faite|a_faire"}}
  ],
  "retraits": [{"type": "exercice", "id_stable": "…", "motif": "…"}]
}
```

Règles : `schema_sync` inconnu du serveur ⇒ lot refusé ; `application.sha_attendu` ≠ version déployée ⇒
**avertissement** (pas de refus : le contenu est indépendant du code), mais `migrations_min` non satisfaites ⇒
refus ; `relecture_humaine: a_faire` ⇒ `prepare` refuse de produire l'archive (code 5).

## 5. Journal et machine à états (migration additive, nouvelle app `synchro`)

Modèles :
- `LotSynchro` : `batch_id` (unique), `statut`, `sha256_archive`, `sha256_manifeste`, `schema_sync`,
  `cree_le`, `debut_le`, `fin_le`, `pid`, `battement_le` (heartbeat), `compteurs` (JSON), `rapport` (JSON),
  `erreur`.
- `ContenuSynchro` : `type`, `id_stable` (unique avec `type`), `cle_naturelle` (JSON), `objet_pk`,
  `empreinte_source`, `empreinte_etat`, `version`, `dernier_lot`, `applique_le`.
- `OperationSynchro` : `lot`, `id_stable`, `operation`, `resultat`, `detail` (JSON), **unique `(lot, id_stable)`**
  (garantit l'idempotence d'un lot rejoué).

États d'un lot : `recu → verifie → pret → en_cours → reussi | reussi_avec_avertissements | echoue | partiel | a_verifier`.
- `a_verifier` : état posé par `statut` quand un `en_cours` a un `battement_le` périmé (> 90 s) et un `pid` mort.
- Transition `reussi` interdite si une opération est restée `en_attente`.
- Rejeu d'un `batch_id` déjà `reussi*` ⇒ **no-op, code 0**, message « déjà appliqué ».
- Rejeu d'un `batch_id` `echoue`/`partiel`/`a_verifier` ⇒ autorisé **seulement** via `reprendre`, qui n'exécute que
  les `OperationSynchro` non terminées.

## 6. Moteur de synchronisation (commande Django `sync_contenu`)

Sous-commandes : `exporter-reference`, `planifier <lot>` (simulation, **défaut**), `appliquer <lot> --confirme`,
`statut <batch_id> [--json]`, `reprendre <batch_id>`, `verifier-fichiers`, `nettoyer --apres-jours N`.

Algorithme de `planifier` (aucune écriture ; écrit seulement le rapport dans `LotSynchro`) pour chaque contenu :
1. Retrouver l'objet par **clé naturelle**. Cherche aussi la ligne `ContenuSynchro`.
2. Classer :
   - rien en prod → `create` ;
   - journalisé et `empreinte_etat(db)` = `ContenuSynchro.empreinte_etat` :
     - `version_reference` = `empreinte_source` appliquée et `version_proposee` identique → `noop` ;
     - `version_reference` = `empreinte_source` appliquée et proposée différente → `update` ;
     - `version_reference` ≠ appliquée → **`conflit_version`** (la prod a avancé depuis la préparation) ;
   - journalisé mais `empreinte_etat(db)` ≠ journal → **`conflit_etat`** (modifié en prod par un autre mécanisme) ;
   - existe en prod **sans** journal (contenu historique) → **`adoption_a_confirmer`** ;
   - la clé naturelle résout un autre objet que le journal → **`conflit_identite`**.
3. Pour `update`/`adoption`, calculer le **diff** champ par champ en appliquant la nouvelle version dans un
   `savepoint` puis en annulant (sans écrire de fichier : seuls les SHA-256 sont comparés).

Algorithme d'`appliquer` (même classement, puis écriture) :
- **Préconditions** : archive et `SHA256SUMS` revérifiés ; verrou `pg_try_advisory_lock` pris ; sauvegarde
  confirmée (§8) ; `LotSynchro.statut` transitions §5.
- **Un `atomic()` par contenu** (pas de transaction de lot : un lot de 500 exercices ne doit pas tenir un verrou
  long). `tout_ou_rien: true` ⇒ **deux passes** : planification complète d'abord, et aucune écriture si un seul
  conflit ou une seule erreur de validation existe.
- **Ordre fixe** : tags (création seule) → exercices → cours → quiz → retraits.
- **Fichiers** (voir §7) : écrits **avant** le commit, sous nom adressé par contenu ; références commutées dans
  la transaction ; anciens fichiers supprimés **après** réussite, jamais dans la transaction.
- **Porte avant commit** : dans la transaction de chaque objet mis à jour, appel de `blocked_lessons` et des
  contrôles de structure de `catalog.tunnel` ; un BLOQUANT ⇒ **rollback de cet objet**, résultat
  `rejete_validation`, le lot continue (ou s'arrête si `tout_ou_rien`). Pas de rétrogradation automatique.
- Conflits : l'objet est **sauté**, jamais écrasé. Résolution humaine par `approbations.json` (voir ci-dessous).
- `adoption_a_confirmer` n'est appliquée que si `options.adopter = true` **et** `approbations.json` contient
  l'objet avec l'`empreinte_etat_prod_vue` identique à celle observée au `planifier`.
- Post-traitement (hors transaction) : `generate_sujet_pdfs --lesson <ids> --force` pour les leçons modifiées,
  `indexer_recherche`, `calculer_frequences_cours`. Un échec ⇒ `reussi_avec_avertissements`, listé, jamais
  confondu avec un échec d'écriture.

`approbations.json` (écrit par `edukora.ps1 resoudre`, relu par le serveur) :
```json
{"decisions": [
  {"id_stable": "…", "decision": "ecraser|garder_prod", "empreinte_etat_prod_vue": "…", "par": "…", "le": "…", "motif": "…"}
]}
```
`ecraser` n'est valable que si l'état de prod au moment d'`appliquer` a **la même empreinte que celle vue**
par l'humain ; sinon retour en conflit (on n'approuve pas un diff qui a changé depuis).

Retraits : `retirer` ⇒ `statut = REJETE` ; exige `retraits[]` dans le manifeste **et** `--confirme-retraits <batch_id>` ;
`reintegrer` ⇒ `VALIDE` avec la même confirmation. Aucun `delete()` n'existe dans le moteur (test T6 : grep +
interdiction de `Model.delete` via le garde-fou d'écritures).

Adaptateurs : un par type, interface `{cle_naturelle(data), retrouver(data), projeter(obj), creer(data, source_dir),
mettre_a_jour(obj, data, source_dir), fichiers(data)}`. `creer` délègue à `ingest_exercise` / `ingest_cours` /
`ingest_competence_item` **inchangés**. `mettre_a_jour` partage avec la création des helpers extraits
(`_champs_question(q_data, exercise, subject)`, etc.) pour garantir qu'une valeur normalisée est la même en
création et en mise à jour.

## 7. Fichiers et images

| Étape | Règle |
|---|---|
| Nommage | Tout fichier **nouveau ou remplacé** est écrit sous `…/<stem>-<sha8>.<ext>` (adressé par contenu) : pas de collision possible, pas d'écrasement silencieux sur Spaces (`file_overwrite=True`), idempotent. |
| Écriture | Avant la transaction de l'objet. Après écriture : relecture du fichier et comparaison du SHA-256. Échec ⇒ aucun commit, état `echec_fichiers`. |
| Activation | La référence (`Figure.image`) est commutée **dans** la transaction de l'objet. |
| Ancien fichier | Chemin enregistré dans `OperationSynchro.detail.a_supprimer`. Supprimé par `nettoyer --apres-jours 7`, **seulement** si plus aucune ligne de la base ne le référence (contrôle sur tous les `FileField`) et si le lot est `reussi*`. |
| PDF de sujet | Régénérés en post-traitement ; un `Lesson.sujet_pdf` existant n'est jamais supprimé avant que le nouveau soit écrit. |
| Contrôle | `sync_contenu verifier-fichiers` : (a) références sans fichier, (b) fichiers sans référence, (c) SHA divergents pour les fichiers journalisés. Rapport seulement ; **aucune suppression automatique**. |
| Stockage | La stratégie ne présume pas du mode : elle passe par `default_storage` / `storages[...]`, donc valable pour Spaces et pour le disque. Le mode réel est une entrée du `doctor` (§8). |

## 8. Poste Windows : `scripts/edukora.ps1` (PowerShell 5.1) et transport

Sous-commandes : `doctor`, `generate`, `validate`, `ingest-local`, `inventaire`, `prepare`, `resoudre`, `publish`,
`status`, `resume`, `reference`. Aucune ne duplique `ingerer_et_valider.sh` / `tunnel_validation.sh` : elles les appellent.
Config : `scripts/edukora.config.psd1` **non committé** (+ `.example` sans valeur réelle) : hôte, utilisateur, port,
fichier de clé dédiée, `known_hosts` dédié, chemin du clone, dossier des lots. Aucun mot de passe.

`publish` (idempotent, reprend où il s'est arrêté, état local dans `batches/<id>/etat.json`) :
1. `doctor` + lot `pret` localement + archive et `.sha256` présents.
2. Verrou local ; connexion SSH (`StrictHostKeyChecking=yes`, `ServerAliveInterval=15`).
3. Verrou serveur `flock` sur `/srv/edukora-lots/.sync.lock` (partagé avec `deploy.sh` en phase 5).
4. `scp` vers `/srv/edukora-lots/incoming/<batch_id>/` (**hors du clone** et des données ; `chmod 700`, propriétaire `deploy`).
5. `sha256sum -c` côté serveur ; copie dans le conteneur (`docker compose cp` vers `/tmp/lots/<batch_id>`).
6. **Sauvegarde** : `exec -T backup ./backup.sh`, puis `pg_restore --list` du dernier dump (intégrité) ; échec ⇒ code 1,
   rien modifié. Pour un lot contenant seulement des `create`, un dump de moins de 24 h suffit.
7. `sync_contenu planifier` ⇒ rapport affiché ; si conflits ou `adoption_a_confirmer` non approuvés ⇒ code 4/5, arrêt.
8. `docker compose exec -d backend python manage.py sync_contenu appliquer … --confirme` **détaché** (survit à une
   coupure SSH) ; résultats uniquement dans `LotSynchro`.
9. Boucle d'interrogation de `sync_contenu statut --json` jusqu'à un état terminal, tolérante aux coupures.
10. Récupération du `rapport` ; vérifications §10 ; nettoyage du dossier temporaire du conteneur **seulement** si
    `reussi*` ; archive conservée 30 jours côté serveur.

Codes de sortie : `0` succès · `1` échec certain (rien d'appliqué, ou restauration propre) · `2` usage/prérequis ·
`3` **indéterminé, vérification requise** (coupure ou `a_verifier`) · `4` conflits (partiel selon mode) ·
`5` validation humaine ou approbation manquante.

Sauvegarde/restauration : avant la **première** utilisation en prod, test de restauration d'un dump sur une base
jetable (README étape 9) avec comparaison des compteurs ; consigné dans le rapport de phase 5.

## 9. Séparation application / données

- **Livraison applicative unique préalable** : nouvelle app `synchro` (migration additive), commande `sync_contenu`,
  helpers extraits. Elle passe par le canal **Application** (Release → Deploy). Aucun `docker cp` en production.
- Ensuite, **chaque mise à jour de contenu ne touche ni image ni service** : pas de `build`, pas de `up`, pas de
  redémarrage. Vérifié par T10 (identifiants de conteneurs identiques avant/après).
- `contenu.sh` reste inchangé et fonctionne en parallèle (T12).

## 10. Vérifications après lot (rapport lisible + JSON)

Créés / mis à jour / inchangés / conflits / rejetés par la porte / ignorés ; `structure_modifiee` ; version
appliquée par contenu ; absence de doublons (recherche de Lesson/Exercise dupliqués sur la clé naturelle) ;
relations (questions sans thème, rappels sans cours) ; fichiers attendus présents avec bon SHA-256 ; état final du
lot ; échecs de post-traitement ; durées.

## 11. Reprise après erreur

| Situation | Détection | Reprise |
|---|---|---|
| Échec avant toute écriture | `LotSynchro.statut = echoue`, aucune `OperationSynchro` terminée | `publish` à nouveau (même `batch_id`) |
| Échec pendant la transaction d'un objet | l'objet est rollbacké, résultat `erreur` | `reprendre` : seuls les objets non terminés |
| Échec fichiers | `echec_fichiers`, rien commuté | idem, après `verifier-fichiers` |
| Coupure SSH après lancement | le client reçoit 255 | **code 3**, `status` interroge le serveur, jamais de relance aveugle |
| Processus mort (redémarrage conteneur) | heartbeat périmé + pid mort ⇒ `a_verifier` | `reprendre` (idempotent grâce à `OperationSynchro`) |
| Confirmation perdue | `statut = reussi` en base | le client lit l'état et sort en 0 |
| Lot rejoué | `batch_id` `reussi*` | no-op |
| Opération incorrecte | restauration d'un dump sur base jetable puis décision humaine | procédure documentée ; pas de restauration automatique |

## 12. Tests d'acceptation (mapping avec le prompt §7)

Django (`TestCase`/`TransactionTestCase`, stockage temporaire, aucune dépendance réseau) :
T1 création · T2 rejeu du même lot (0 écriture, `updated_at` intacts) · T3 correction (même pk, aucun doublon,
`ExerciceFait` et `SimulationReponse` conservés, version +1, ancien fichier encore présent avant `nettoyer`) ·
T4 lot sans changement · T5 conflit d'état (modification admin simulée) + conflit de version + identité changée ·
T6 retrait explicite (`REJETE`), contenu absent du lot intact, aucun `delete` · T7 interruptions (exception dans la
transaction ⇒ rollback de l'objet ; échec fichier ; processus tué ⇒ `a_verifier` ⇒ `reprendre`) ·
T8 `verifier-fichiers` (référence sans fichier, orphelin, SHA divergent) · T11 garde-fou d'écritures + données
opérationnelles intactes (comptes, abonnements, paiements, quotas) · T13 `structure_modifiee` (question absente non
supprimée) · T14 porte avant commit (BLOQUANT ⇒ objet rejeté, jamais publié cassé) · T15 adoption (objet historique
non journalisé : refus sans approbation, application avec approbation et empreinte vue identique) ·
T16 non-régression de la voie « création » (`ingest_exercise` produit exactement les mêmes objets qu'avant
l'extraction des helpers).
Pester/PowerShell : parsing de config, calcul d'archive et SHA, machine d'états locale, codes de sortie.
Intégration en local (conteneur) : T9 sauvegarde→restauration sur base jetable avec comparaison des compteurs ;
T10 aucun rebuild ni redémarrage ; T12 `contenu.sh auto --simulation` identique ; simulation de coupure SSH
(kill du client pendant `appliquer` puis `status`).

## 13. Plan d'exécution et points d'arrêt

| Phase | Contenu | Livrables | Arrêt |
|---|---|---|---|
| 3 | `edukora.ps1` (`doctor`, `validate`, `ingest-local`, `inventaire`, `prepare`, `status` local), calcul d'empreintes partagé Python, **liste des 93 unités (550 JSON) ignorées pour votre validation** | script + tests Pester, `inventaire` | n°3 |
| 4 | App `synchro`, `sync_contenu` sur **un type** (exercice) de bout en bout en local, puis cours, puis quiz | migration, commande, T1-T16 | n°4 |
| — | **Livraison applicative** (vous) : commit, Release, Deploy | — | feu vert prod |
| 5 | Transport, `publish`/`resume`, verrou serveur, test de restauration, premier lot réel (création seule), puis premier lot de correction | rapports de lot | n°5 |
| 6 | Documentation `deploy/README-SYNC-CONTENU.md`, mise à jour de `README-TUNNEL.md` | docs | fin |

## 14. Risques résiduels et incertitudes de conception

1. **Adoption des contenus historiques** : sans journal, la première correction d'un objet de prod ne peut pas
   prouver qu'il n'a pas été retouché à la main ; d'où l'approbation explicite avec diff. Volume potentiel :
   des milliers d'objets ; l'adoption sera **par lot et à la demande**, pas globale.
2. **Campagnes de correctifs légitimes** (fusion de Tags, `appliquer_themes_questions`) modifient la projection
   (thèmes par nom) ⇒ faux `conflit_etat`. Mitigation : ces commandes doivent, à terme, rafraîchir
   `ContenuSynchro.empreinte_etat` (hook) ; en attendant, résolution `ecraser`/`garder_prod` par humain.
3. **Dépendance au clone git en production** pour `contenu.sh` n'est pas modifiée ; le canal B ne lit **pas**
   `/app/ingest`. Cohabitation à tester (T12).
4. **Mode de stockage de prod inconnu** [I] : la stratégie est neutre, mais `doctor` doit l'afficher et le
   premier lot réel ne doit pas partir avant que vous ayez lancé `diagnostic-serveur.sh`.
5. **Le gate d'ingestion historique** (republication des brouillons) n'est pas appelé par le moteur ; les `create`
   passent par `ingest_*` qui restent soumis à ses règles actuelles (R14 de l'audit).
6. **Fichiers volumineux** : `docker compose cp` d'un lot de plusieurs centaines de Mo est lent ; seuil à mesurer en
   phase 5 (au-delà, montage dédié du dossier des lots, qui exigerait une modification de compose via le canal Application).

## 15. Questions pour le point d'arrêt n°2

1. Valider les **identités** : `id_stable` = chemin relatif du JSON (exercice), `cours_id` (cours), `external_id`
   (quiz), avec clé naturelle immuable.
2. Valider la **liste fermée** des modèles écrits (§3.1) et l'**interdiction de toute suppression physique** en v1.
3. Valider que `statut`, `published_at`, `est_vitrine` ne sont **jamais** modifiés par une mise à jour.
4. Valider la **résolution des conflits** par `approbations.json` (`ecraser` lié à l'empreinte vue / `garder_prod`).
5. Autorisez-vous la **modification de `deploy.sh`** pour partager le verrou `flock` avec les lots (petit changement,
   via le canal Application) ?
6. Le **dossier de lots serveur** `/srv/edukora-lots` (hors du clone) vous convient-il, ou préférez-vous un autre chemin ?

## 16. Écarts constatés à l'implémentation (phase 4)

Décisions prises en codant, à relire ; elles précisent la spec sans la contredire.

| # | Sujet | Réalisé |
|---|---|---|
| E1 | Mise à jour d'un exercice | `ingest_exercise(..., sync=ContexteSync)` : question appariée par `numero`, figure par `external_id`, rappel par `external_id`. Aucun `delete()`. Une question sans thème dans le JSON garde ses thèmes. |
| E2 | Fichiers | Tout fichier écrit par le moteur est nommé `<stem>-<sha8>.<ext>`. Une figure dont le fichier stocké est octet pour octet identique n'est pas réécrite. L'ancien fichier est seulement noté (`a_supprimer`) ; `nettoyer` ne le supprime que s'il n'est plus référencé. |
| E3 | Cours | Seuls titre, sous-thème, durée, sections (donc `content_markdown`) et tags sont mis à jour. `cursus` et `cursus_recommandes` ne le sont pas (dérivés de l'épreuve source). |
| E4 | Quiz | `source_exercises` n'est pas appliqué (ids de la base locale, faux en production). |
| E5 | Plan | `planifier` simule le lot ENTIER dans une transaction unique annulée à la fin : un cours voit l'exercice simulé juste avant lui. Aucun fichier écrit. |
| E6 | Adoption | Contenu existant non journalisé : si le contenu appliqué serait identique à l'existant, il est journalisé sans aucune écriture sur le contenu (`inchange`) ; sinon `adoption_a_confirmer` jusqu'à une décision `ecraser` portant l'empreinte d'état vue, avec `options.adopter`. Mesuré sur données réelles : 5 exercices GCE ingérés historiquement, diff vide pour les 5. |
| E7 | Retraits | Un retrait remplace l'entrée `noop` du même contenu ; il est refusé s'il coexiste avec une création ou une mise à jour du même contenu dans le lot. |
| E8 | Journal | Une opération terminée n'est écrite qu'après le commit du contenu : si le processus meurt entre les deux, la reprise classe le contenu `noop` et l'opération apparaît `inchange` (données correctes, libellé approximatif). |
| E9 | PDF de sujet | La régénération (`generate_sujet_pdfs --force`) utilise `save_sujet_pdf`, qui supprime l'ancien PDF avant d'enregistrer le nouveau : en cas d'échec le sujet est temporairement sans PDF (404 propre, régénérable). Signalé en avertissement du lot. |
| E10 | Verrou | `pg_try_advisory_lock` sur PostgreSQL ; sans effet sur SQLite (tests). |

### 16 bis. Revue indépendante et corrections (phase 4)

Un relecteur adverse a exercé le moteur sur PostgreSQL réel : 1 défaut de gravité haute, 14 moyens, 8 bas. Tous
sont traités ou documentés ; chacun a un test de non-régression (`backend/synchro/test_revue.py`).

| Constat | Correction |
|---|---|
| H1 `nettoyer` supprimait une image encore citée dans un instantané de quiz | Une image citée par un champ fichier **ou par son URL dans un texte** (instantanés, énoncés, contenus compilés) n'est jamais supprimée. |
| M1 doublon d'exercice si deux Lessons ont la même clé | `cree` ou pk différent de l'objet du journal ⇒ `conflit_identite`, transaction annulée. |
| M2 décision ajoutée à un lot déjà reçu ignorée | `recevoir` d'un même lot remplace `approbations.json` (vérifié par SHA256SUMS) tant que le lot n'est ni en cours ni réussi. |
| M3 post-traitement perdu après une mort du processus | Persisté dans le lot, reprenable (`post-traiter`), seules les leçons non traitées sont refaites. |
| M4 PDF supprimé avant écriture du nouveau | Nouveau PDF sous un nom adressé, référence commutée, ancien conservé et proposé à `nettoyer`. |
| M5 statut / vitrine écrasés par une course | Objet relu sous verrou de ligne dans la transaction, empreinte d'état revérifiée ; enregistrements partiels sans `statut`, `published_at` ni `est_vitrine`. |
| M6 porte qui rejetait un exercice sain | Règles bloquantes bornées à l'exercice ; mise à jour = « avant / après ». |
| M7 fichier renommé : plan et application divergent | `conflit_identite` explicite au classement. |
| M8 correction hors périmètre journalisée comme appliquée | Nouveau résultat bloquant `correction_hors_perimetre`, journal non avancé. |
| M9 champ compilé retouché à la main écrasé | Champs compilés (`Exercise.enonce/corrige_markdown`, `Cours.content_markdown`) inclus dans l'empreinte d'état ; commande `rafraichir-journal` pour un changement légitime du code de rendu. **Reste non couvert : `Lesson.content_markdown`.** |
| M10 cours dédoublonné : rattachement du rappel annulé | Le rattachement est conservé, le résultat reste `ignore_dedoublonne`. |
| M11 fichiers orphelins, noms suffixés à la reprise, écriture non relue | Fichier existant identique réutilisé ; écriture relue et comparée ; fichiers écrits d'un traitement annulé consignés (`orphelins`) pour `nettoyer`. |
| M12 plan bloqué par un retrait | La confirmation se donne à l'application, le plan l'annonce. |
| M13 PID réutilisé : lot `en_cours` bloqué | Lot mort = battement périmé **et** verrou consultatif libre (PID seulement sous SQLite). |
| M14 contenu purgé en production non recréable | Décision `recreer` liée à l'`objet_pk_absent` et à la version proposée. |
| B1 / B2 chemins et erreurs d'archive | Chemins confinés à `<lot>/ingest`, noms de figures sans séparateur, toute erreur d'archive = `ErreurLot` + dossier nettoyé. |
| B3 quiz désigné par position | Désigné par `external_id`. |
| B4 empreinte sur l'objet en mémoire | Calculée sur l'objet relu. |
| B5 deux fichiers, même exercice | Refusé dès `prepare`. |
| B8 décision réutilisable d'un lot à l'autre | `version_proposee` obligatoire dans toute décision `ecraser`. |
| B6, B7 (documentés, non corrigés) | `_link_tags_to_savoir` peut renseigner `Tag.savoir_officiel` (dérogation à « Tag : création seule »). Une figure historique encodée autrement que par l'ingestion actuelle paraît « différente » et est remplacée (ancien fichier conservé). |

### 16 ter. Mesure sur données réelles (lot de 140 éléments, base locale)

Plan en lecture seule de 19 unités francophones et GCE tirées au hasard (140 contenus) : **92 identiques** à la base,
**45 « différents »**, 3 cours dédoublonnés. Les écarts ne sont pas des erreurs du moteur mais des divergences réelles
entre les JSON du disque et la base : thèmes / mots-clés modifiés par des campagnes de correctifs (fusions de Tags),
`groupes_verifies` posé après coup, figures remplacées par la campagne « sans filigrane », cours dont le JSON a été
renommé / dédoublonné. Conséquence de conception : **le premier contact avec le corpus historique se fait par
adoption, avec décision humaine** (`ecraser` = appliquer le JSON, `garder_prod` = prendre la production pour base
sans l'appliquer). `garder_prod` enregistre désormais la production comme base : le lot n'est plus proposé en
adoption, et une correction ultérieure s'applique proprement par-dessus. Le tri en masse (« garder la production pour
tout ce qui diffère, appliquer ceci ») relève de la commande `resoudre` du poste (phase 5).
