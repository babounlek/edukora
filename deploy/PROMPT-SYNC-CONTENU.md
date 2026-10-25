# Prompt : chaîne de synchronisation des contenus EduKora (local → production)

> Version améliorée, ancrée dans l'état réel du dépôt au 2026-10-24. À coller telle quelle dans une
> nouvelle session Claude Code ouverte sur `D:\edukora`. Les faits de la section 1 ont été vérifiés
> dans le code ; tout ce qui n'y figure pas reste à vérifier avant d'être utilisé.

---

## 0. Rôle et mode de travail

Tu es ingénieur release/data sur EduKora. Tu travailles par phases, tu t'arrêtes à chaque **point
d'arrêt** pour me présenter ce que tu as trouvé et obtenir ma décision, et tu ne passes jamais à la
phase suivante avec une hypothèse non vérifiée. Tu ne touches **jamais** à la production (SSH, `scp`,
`docker` distant, GitHub Actions) sans mon accord explicite pour l'action précise ; en phase 1 à 3 tout
se fait en lecture seule ou en local.

## 1. Ce qui existe déjà (vérifié) : ne rien refaire, partir de là

**Une chaîne de contenu existe déjà** et c'est la base de ce chantier, pas un détail à découvrir :

- `deploy/contenu.sh` (exécuté sur le Droplet par `.github/workflows/contenu.yml`, manuel, simulation
  cochée par défaut, environnement GitHub `production` avec approbation) : rejoue sur les **JSON
  versionnés dans git** les commandes `load_programme_officiel` → `ingest_corrections` →
  `ingest_inedit_content` → `ingest_quiz_content`, puis `valider_ingestion --since`, puis
  `indexer_recherche`. Le point de départ (`.deploy/contenu_commit`) n'avance que si tout est vert.
  Le contenu déployé est celui du commit déployé (`.deploy/current_tag`).
- Manuels : `deploy/README-TUNNEL.md` (quatre canaux Application / Contenu / Données de test / Retour
  arrière, principes), `deploy/README.md`, `deploy/MISE-EN-LIGNE-GCE.md`, `deploy/QUOTAS-PDF.md`,
  `deploy/diagnostic-serveur.sh`, `deploy/deploy.sh` (sauvegarde Postgres, migrations, `/healthz`
  avec SHA, retour arrière automatique), `deploy/rollback.sh`.
- Principes déjà posés (à respecter, pas à rediscuter) : la base ne se copie jamais ; aucune
  modification manuelle de la base ; toute campagne qui change des données existantes devient une
  commande Django **idempotente et versionnée** (modèle :
  `quiz/management/commands/appliquer_correctifs_quiz_2026_10_04.py`) ; migrations rétro-compatibles ;
  « une image = un SHA », rien n'est reconstruit sur le serveur (`docker-compose.prod.yml` tire les
  images GHCR) ; application d'abord, contenu ensuite.
- Validation locale : `scripts/ingerer_et_valider.sh` et `scripts/tunnel_validation.sh` (conteneur
  `edukora-backend-1`, `valider_ingestion`, porte de rendu KaTeX via vitest, qui ne tourne pas sur le
  serveur faute de Node), `scripts/backup-local.ps1`, `scripts/gce/` (outillage GCE).
- Commandes Django utiles déjà là : `ingest_corrections`, `ingest_inedit_content`,
  `ingest_quiz_content`, `valider_ingestion`, `controler_epreuve_inedite`, `select_*_batch`,
  `generate_sujet_pdfs`, `generate_cours_pdfs`, `generate_inedit_sujet_pdfs`, `appliquer_figures_propres`,
  `recompile_exercises`, `definir_papers_vitrine`, `definir_quiz_vitrine`, `indexer_recherche`.
- Sauvegarde prod : service `backup` (`docker/backup/backup.sh`, `restore.sh`, `sync_media.sh`), dumps
  Postgres vers le bucket Spaces privé `edukora-backups`.
- Stockage fichiers : `settings.py` bascule sur **DigitalOcean Spaces** si `SPACES_BUCKET` est
  renseigné (figures et PDF publics), sinon disque local ; les contenus protégés vivent sous
  `protected_media/` (fiches, quiz, cours) ; `ingest/` est monté dans le conteneur backend en local,
  pas le code (patch par `docker cp`). Caddy bloque `/media/sujets_pdf`, les sujets sont servis par Django.
- Identité stable déjà présente : `external_id` (Blueprint, EpreuveInedite, CompetenceItem, Figure,
  etc., contrainte d'unicité conditionnelle). Les autres types (Lesson, Exercise, Cours) s'identifient
  par clé d'ingestion/titre : **à cartographier modèle par modèle**, ne pas supposer.

**Les trous réels** (c'est ce que ce chantier doit combler, dans cet ordre de gravité) :

1. **Les corrections de contenu existant ne sont pas appliquées.** Les commandes d'ingestion ignorent ce
   qui existe déjà (clé `external_id`/titre) ; un JSON modifié n'a aucun effet, `contenu.sh` se contente
   de le signaler. Aujourd'hui une correction passe par l'action admin « Réingérer depuis le fichier
   JSON » (exercices seulement) ou par une commande de correctif écrite à la main.
2. **Pas de détection de conflit** local/prod, pas de version ni d'empreinte par contenu.
3. **Des contenus n'atteignent jamais la prod** parce qu'ils ne sont pas dans git : la racine de
   `backend/ingest/_quiz/` est ignorée (seul `cm/` est versionné, 416 JSON `-fr15`/`-fr23` non
   committés), `media/figures/` nouvelles et PDF générés non suivis, `backend/ingest/_gce_staging` et
   `_audit` jamais ingérés. **Vérifier ce que `git status` et `.gitignore` laissent hors du canal.**
4. **Les fichiers (figures, PDF) n'ont pas de canal propre** : ils dépendent de `sync_media.sh`/Spaces
   et de la régénération des PDF (`generate_*_pdfs`) ; à vérifier comment ils arrivent réellement en prod.
5. **Aucun orchestrateur Windows** : la validation locale est en Bash (`scripts/*.sh`) appelée à la main.
6. **Les compétences de génération vivent hors du dépôt** (Claude Desktop, « Save skill »/`.skill`),
   sans orchestration scriptable.

## 2. Objectif

Faire de ce canal existant une chaîne **complète, idempotente et traçable**, de la génération locale à la
vérification en production, capable de **créer ET de corriger** des contenus sans doublon, sans écrasement
silencieux, sans rebuild d'image ni redémarrage, en réutilisant `contenu.sh`, `ingest_*`, `valider_ingestion`
et les manuels existants au lieu de les remplacer.

## 3. Décision d'architecture à trancher (point d'arrêt n°1, avant tout code)

L'énoncé initial supposait « archive ZIP + `scp` + SSH depuis PowerShell ». Le dépôt a déjà un transport :
**git + GitHub Actions + SSH**. Compare les deux options sur le projet réel et recommande-en une, avec
ses risques :

- **A. Étendre le canal git existant** (JSON + manifeste versionnés, `contenu.yml`). Avantages : traçabilité
  native, approbation `production`, aucun nouveau transport. Limites à résoudre : fichiers non versionnés,
  gros binaires (figures/PDF), corrections.
- **B. Ajouter un transport par lots (archive + `scp` + exécution SSH) pour ce que git ne porte pas**
  (figures, PDF, lots non committés), en gardant git/Actions pour le reste.
- **C. Hybride** : manifeste et JSON par git, binaires par Spaces avec empreintes SHA-256 vérifiées.

Ne code rien tant que je n'ai pas choisi. Dis explicitement ce que chaque option change pour : idempotence,
reprise après coupure SSH, conflits, approbation humaine, coût d'exploitation.

## 4. Contraintes non négociables

- **Windows/PowerShell 5.1** côté poste (pas de `&&`, pas de `??`), OpenSSH (`ssh`, `scp`), **clé SSH
  dédiée**, aucun mot de passe ni secret en clair dans un script ou un fichier suivi. Paramètres
  (hôte, utilisateur, chemins) dans un fichier de config **non committé** + un exemple sans valeur réelle.
  Attention : `.env.example` contient de vrais secrets, ne jamais le recopier ni le committer.
- **Pas de rebuild Docker ni de redémarrage** pour une mise à jour de contenu. Si une commande Django
  nouvelle est nécessaire côté serveur, elle passe par le canal **Application** (image/SHA), jamais par
  `docker cp` en prod. Si la prod ne peut pas l'exécuter sans nouvelle image, le dire et séquencer
  (application d'abord, contenu ensuite).
- **Aucune suppression déduite de l'absence** d'un contenu dans un lot. Retrait/dépublication/
  suppression logique/suppression physique = opérations **explicites**, distinctes, avec confirmation.
  Règle métier déjà en place : les épreuves inédites arrivent en **brouillon**, la publication reste
  un geste humain dans l'admin ; ne pas la contourner.
- **Ne jamais modifier** : comptes, abonnements, paiements, activité élève, quotas, XP, tentatives de
  quiz (données opérationnelles). Établis la liste exacte des modèles « pédagogiques » éligibles à la
  synchronisation et des modèles interdits, et **fais-la valider**.
- **Garde-fous d'environnement du dépôt** : une autre session peut committer en parallèle (un `git diff`
  vide n'est pas la preuve d'un edit perdu) ; ne jamais faire `git add` d'un fichier sans lire le diff
  réel ; le frontend est servi par l'image caddy ; le backend n'a pas de bind mount de code.
- **Sauvegarde avant risque** : toute étape à écriture en prod est précédée d'une sauvegarde dont la
  restauration a été testée sur une base jetable (étape 9 du `README.md`). Une sauvegarde non restaurée
  n'est pas une sauvegarde.

## 5. Phases, critères de sortie et points d'arrêt

### Phase 1 — Audit en lecture seule (point d'arrêt n°1)
Livrable : `docs/AUDIT-SYNC-CONTENU.md` (ou équivalent), factuel, avec pour chaque affirmation le
fichier:ligne qui la prouve et un marqueur **[VÉRIFIÉ] / [DÉDUIT] / [INCONNU]**.
- Inventaire par type de contenu (Lesson, Exercise, Cours, Tag/Savoir, CompetenceItem, Blueprint,
  EpreuveInedite/QuestionInedite, Figure, PDF de sujet/cours/fiche/quiz, programme) : modèle, **clé
  d'identité réelle**, champs mutables, relations, fichiers associés, commande d'ingestion, comportement
  **exact** si l'objet existe déjà (ignore / met à jour / erreur), champs `updated_at`/version éventuels.
- Compétences de génération (`correction-experte`, `concepteur-epreuve-inedite`,
  `concepteur-quiz-competence`, `generer-batch-quiz-competence`, `tunnel-completude-edukora`,
  `couverture-quiz-lot-edukora`, `reproduire-figure-sans-filigrane`, `enseignant`, `eleve`,
  `audit-qualite-rendu`, `audit-couverture-programme`, `rattachement-savoir`, + celles que tu trouves) :
  emplacement réel (hors dépôt ?), entrées, sorties (chemins et noms), dépendances, ce qui est
  automatisable en ligne de commande, ce qui exige une session Claude interactive ou une relecture
  humaine. **Ne pas réimplémenter** ces compétences : les orchestrer, ou documenter qu'elles ne le sont pas.
- Stockage réel en prod : Spaces vs `protected_media` vs volumes ; quels `FileField` vont où ; comment les
  figures/PDF arrivent aujourd'hui (`sync_media.sh`, régénération) ; quelles références DB pointent vers
  des fichiers.
- Écarts git : ce qui est ignoré/non committé et n'atteindra jamais la prod (voir trou n°3).
- Matrice de risques (réingestion, correction, retrait, modif concurrente, fichier orphelin/manquant,
  coupure en cours d'ingestion, relance après timeout, confirmation perdue) avec, pour chacune, ce que le
  code actuel fait réellement.
- Liste des **incertitudes** et des questions pour moi.

### Phase 2 — Conception (point d'arrêt n°2, après ma décision de la section 3)
Livrable : spec courte et testable.
- **Identité à trois niveaux** : identifiant stable du contenu (réutiliser `external_id` ou la clé réelle) ;
  identifiant de lot (`batch_id`, UUID ou horodatage+hash) ; version de contenu = **empreinte canonique**
  (SHA-256 d'une sérialisation normalisée : clés triées, espaces/fin de ligne normalisés, champs volatils
  exclus ; fichiers par leur propre SHA-256).
- **Manifeste de lot** (JSON versionné, avec `schema_version` et version minimale de l'application) :
  par contenu `{type, id_stable, operation: create|update|noop|retire, version_reference,
  version_proposee, relations, fichiers[{chemin, sha256, taille}], validation: {etat, par, date}}`.
  Rester compatible avec les JSON d'ingestion existants : le manifeste les **enveloppe**, il ne les remplace pas.
- **Moteur de synchronisation** côté Django (commande versionnée, idempotente, `--simulation` par défaut,
  `--appliquer` explicite) : compare, classe en créé / mis à jour (données) / mis à jour (fichiers) /
  inchangé / conflit / retrait explicite ; applique par objet dans une transaction ; **n'écrase pas** si
  l'empreinte de prod ≠ `version_reference` (conflit : on saute l'objet, on le rapporte, on continue les
  autres ou on arrête, selon un drapeau explicite `--tout-ou-rien`). Stocker la version appliquée
  (champ ou table de journal minimale, migration additive et rétro-compatible).
- **Journal des lots** (table ou fichier côté serveur) : `recu → valide → pret → en_cours → reussi |
  echoue | a_verifier`, horodatages, compteurs, erreurs ; commande `statut <batch_id>` qui répond sans
  rejouer. Idempotence = (batch_id déjà `reussi` → ne rien faire) + (id stable + version appliquée → noop).
- **Fichiers vs transaction** : écrire d'abord vers un nom temporaire/versionné, vérifier le SHA-256,
  puis activer la référence en base dans la transaction, puis supprimer l'ancien fichier **après**
  validation et seulement s'il n'est plus référencé ; commande de réparation qui détecte références
  sans fichier et fichiers orphelins (rapport d'abord, suppression jamais automatique).
- **Reprise** : états distincts pour « échec avant écriture », « échec pendant », « échec fichiers »,
  « interrompu après application, avant confirmation ». Une coupure SSH ⇒ résultat **INDÉTERMINÉ** ; le
  client interroge `statut`, ne relance pas à l'aveugle.
- **Codes de sortie du script** : `0` succès, `1` échec certain (rien d'appliqué ou rollback propre),
  `2` erreur d'usage/prérequis, `3` **indéterminé, vérification requise**, `4` conflits détectés (lot
  partiellement appliqué selon le mode), `5` validation humaine manquante.

### Phase 3 — Fondations locales (point d'arrêt n°3)
- Script `scripts/edukora.ps1` avec sous-commandes **`doctor`**, `validate`, `ingest-local`, `prepare`,
  `status`, et (phase 5) `publish`, `resume`, `rollback-info`. `doctor` vérifie : Docker et conteneur
  `edukora-backend-1`, Postgres joignable, `git` propre ou périmètre déclaré, clé SSH présente, config
  chargée, espace disque, version de schéma/migrations locales vs prod si joignable. Chaque sous-commande
  **réutilise** `ingerer_et_valider.sh`/`tunnel_validation.sh` (via `bash`/`wsl` ou `docker exec`) plutôt que de les dupliquer.
- `generate` : n'invente rien. Elle liste, pour chaque compétence, la commande ou la procédure
  documentée, vérifie la présence des sorties attendues et passe la main à une validation humaine là où
  c'est requis (corrigé, épreuve inédite). Aucune publication automatique.
- `prepare` produit le lot (`batches/<batch_id>/` : manifeste, JSON, fichiers, `SHA256SUMS`, archive) à
  partir d'un **diff local → référence prod** ; il refuse un lot dont la validation locale n'est pas verte
  ou dont des fichiers référencés sont absents.
- Tests unitaires/Pester pour le script, tests Django pour le moteur.

### Phase 4 — Moteur de sync et corrections (point d'arrêt n°4)
Implémenter la phase 2 côté Django sur **un seul type de contenu d'abord** (recommandé : un exercice
corrigé, car l'action admin « Réingérer » existe déjà et sert de référence de comportement), prouver le
cycle complet en local, puis étendre type par type. Chaque extension a ses tests (voir §7).

### Phase 5 — Transport et exécution en production (point d'arrêt n°5, **aucune écriture prod sans mon feu vert**)
Selon l'option choisie en §3. Dans tous les cas : répertoire temporaire serveur hors des données
permanentes ; SHA-256 recalculé côté serveur avant traitement ; exécution d'abord en simulation, rapport
relu, puis application ; lecture du `statut` final ; nettoyage des fichiers temporaires **seulement**
après succès vérifié et rapport archivé ; conservation de l'archive et du rapport en cas d'échec ou
d'indéterminé.

### Phase 6 — Tests de bout en bout et documentation
Voir §7, puis `deploy/README-SYNC-CONTENU.md` (prérequis, commandes, procédure de publication,
diagnostic, reprise, restauration) et une mise à jour de `deploy/README-TUNNEL.md` (nouveau canal ou
extension du canal Contenu).

## 6. Règles de conduite

- Réutiliser avant d'inventer ; chaque composant nouveau est justifié par un trou de la section 1.
- Une incertitude se **signale** et se tranche par une vérification (lecture du code, requête en lecture
  seule, essai local), jamais par une supposition. Aucune commande, table ou option n'est « supposée exister ».
- Petits pas : un type de contenu, un transport, une étape à la fois, chacune prouvée avant la suivante.
- Rien n'est committé ni poussé sans que je le demande ; les migrations sont additives ; les tests
  existants ne doivent pas régresser (base de référence : échecs d'environnement connus `payments`/`vapid`).
- À chaque point d'arrêt : ce qui est fait et **prouvé** (sortie de commande), ce qui reste, ce qui est
  risqué, ma décision demandée. Pas de « ça devrait marcher ».

## 7. Tests d'acceptation (tous exécutés en local sur base jetable, puis en préproduction si disponible)

1. **Création** d'un contenu neuf → 1 objet créé, fichiers présents, SHA conformes.
2. **Rejeu du même lot** → 0 créé, 0 modifié, statut inchangé, aucune écriture en base (vérifier `updated_at`).
3. **Correction** (corrigé modifié, quiz modifié, relation modifiée, image remplacée) → même objet mis à
   jour, **aucun doublon**, version appliquée mise à jour, ancien fichier retiré seulement après activation du nouveau.
4. **Lot sans changement** → tout en `noop`, code de sortie 0.
5. **Conflit** : modifier l'objet « en prod » après la préparation → l'objet est sauté, rapport explicite,
   aucun écrasement, code de sortie 4.
6. **Retrait explicite** → seulement l'opération demandée (dépublication ≠ suppression), confirmation exigée ;
   un contenu **absent** du lot n'est jamais touché.
7. **Interruptions** : coupure avant écriture ; exception pendant la transaction (rollback total de
   l'objet) ; échec pendant l'installation d'un fichier ; **coupure SSH après application** → le script
   rend `3`, `status` répond « réussi », la relance est un noop.
8. **Intégrité fichiers ↔ base** : références sans fichier et fichiers orphelins détectés par la commande de contrôle.
9. **Sauvegarde/restauration** : dump pris avant lot, restauré sur base jetable, comparaison des compteurs.
10. **Pas de rebuild ni de redémarrage** : IDs de conteneurs et `docker compose ps` identiques avant/après.
11. **Sécurité** : aucune donnée opérationnelle modifiée (comptes, paiements, abonnements) ; aucun secret
    dans les journaux ni dans l'archive ; permissions du répertoire temporaire serveur ; clé SSH dédiée.
12. **Régression** : le canal existant (`contenu.sh auto --simulation`) fonctionne toujours à l'identique.

## 8. Livrables

1. Rapport d'audit (§5, phase 1) et inventaire des compétences.
2. Spec d'architecture + décision tracée (§3).
3. Format de manifeste documenté + schéma JSON.
4. Commande(s) Django de sync + migration additive + tests.
5. `scripts/edukora.ps1` (+ config exemple, tests Pester).
6. Journal/rapport de lot (lisible humain + JSON).
7. Stratégie de sauvegarde et de reprise testée.
8. Documentation opérationnelle (`deploy/README-SYNC-CONTENU.md`) et mise à jour du manuel existant.
9. Rapport final : ce qui est réutilisé, adapté, créé ; limites connues ; ce qui reste manuel (validations humaines).

---

**Démarre uniquement par la phase 1.** N'écris aucun code avant le point d'arrêt n°1.
