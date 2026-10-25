# Audit de l'existant : chaîne de synchronisation des contenus EduKora

Phase 1 du chantier décrit dans [PROMPT-SYNC-CONTENU.md](PROMPT-SYNC-CONTENU.md). Date : 2026-10-24.
Lecture seule : aucun fichier de code modifié, aucune commande Docker/SSH, aucune requête sur la base ni
sur la production. Ce document est le point d'arrêt n°1 : aucun développement n'est engagé.

Légende : **[V]** lu dans le code ou mesuré dans le dépôt · **[D]** déduit · **[I]** inconnu, à lever.
Les numéros de ligne sont ceux du dépôt au 2026-10-24.

---

## 1. Ce qu'il faut retenir (les 10 constats qui orientent la conception)

1. **Un canal de contenu existe et fonctionne** (git + GitHub Actions « Contenu » + `deploy/contenu.sh`).
   Mais il sait seulement **créer** [V].
2. **Un contenu déjà ingéré est ignoré, jamais mis à jour**, pour tous les types sauf le programme
   officiel [V] : exercice `catalog/ingestion.py:1621-1633`, cours `:2010-2029`, quiz
   `quiz/ingestion.py:514-518`, blueprint `inedit/ingestion.py:292-294`, épreuve inédite `:495-497`.
   Aucune empreinte de source n'existe nulle part (grep `source_hash|content_hash|checksum|sha`) [V].
3. **La seule voie de correction existante est destructrice** [V]. L'action admin « Réingérer depuis le
   fichier JSON » appelle `ingest_exercise(force=True)`, qui fait `existing.delete()`
   (`catalog/ingestion.py:1810`). Le delete cascade sur `access.ExerciceFait`
   (`access/models.py:54`) et `simulations.SimulationReponse` : **la progression des élèves sur cet
   exercice est perdue**, et l'exercice change de pk (index de recherche obsolète). Un moteur de
   synchronisation ne doit donc **jamais** passer par supprimer/recréer : il faut une mise à jour sur place.
4. **Les fichiers sont supprimés à l'intérieur de la transaction** lors d'une réingestion forcée
   (`:1810-1813` dans le `atomic` de `:1644`) : une erreur ultérieure annule la base mais pas la
   suppression des fichiers [V]. Exactement le cas que la phase 2 devra éviter.
5. **Le contenu est publié (VALIDE) dès sa création**, avant le tunnel [V] : Lesson `:1701`, Exercise
   `:1832`, Cours `:2126`, CompetenceItem `quiz/ingestion.py:545`. Seul le gate de fin de run
   (`:2277-2313`) rétrograde en brouillon. Seules les **inédites** (blueprint, épreuve) entrent en
   BROUILLON et exigent un clic admin.
6. **Une dépublication manuelle peut être annulée par le run suivant** [V] : le gate remet en VALIDE toute
   Lesson en BROUILLON dont un JSON est encore sous `ingest/` et dont le tunnel est propre
   (`:2243`, `:2310-2312`). Seul REJETE est stable. Les retraits explicites devront utiliser REJETE ou un
   mécanisme à eux, jamais BROUILLON.
7. **Le code de sortie des commandes d'ingestion est 0 même avec des erreurs** [V]
   (`ingest_corrections`, `ingest_quiz_content`, `ingest_inedit_content` ne lèvent pas de `CommandError`).
   `contenu.sh` compense en cherchant `erreur(s) :` dans la sortie, ce qui est fragile.
8. **Tout `backend/ingest/` est dans `.gitignore`** (ligne 14) ; ce qui est suivi l'a été par `git add -f`
   [V]. Mesure : 27 802 JSON suivis, **4 393 JSON ignorés** au total, dont, dans `ingest/cm/`, **550 JSON d'exercices GCE (+ 85 PNG)
   répartis en 93 dossiers**, tous ingérés en local, jamais committés, donc jamais livrés (inventaire réel de la phase 3) ; 548 sous `_quiz/` (hors
   `_quiz/cm`, qui est entièrement suivi : 0 ignoré) et 4 216 sous `_gce_staging/` (staging, jamais
   ingérés par conception). Côté médias : 1 831 `sujets_pdf/cm` et 100 figures non suivis.
   Un `git status` ne montre **pas** ces fichiers (ils sont ignorés) : le risque est silencieux.
9. **Le canal git ne peut pas livrer un lot « contenu seul »** [D] : `release.yml` exclut
   `backend/ingest/**` (`paths-ignore`, l.19-22), donc un commit qui ne touche que des JSON ne produit pas
   d'image ; `deploy.yml` exige les images du SHA ; et `contenu.sh` refuse si le clone n'est pas au SHA
   déployé (l.57-61). Le contenu est donc **couplé aux déploiements d'application**, ce qui contredit
   l'objectif d'indépendance.
10. **Aucune détection de conflit, aucun journal de lots, aucune version par contenu** n'existent. La
    reprise après coupure repose sur « l'ingestion ignore l'existant », ce qui est idempotent pour la
    création mais ne dit rien de l'état d'un lot interrompu (pas de transaction de lot : une transaction
    **par exercice/cours/item**).

---

## 2. Le canal existant, tel qu'il fonctionne

| Élément | Fait | Source |
|---|---|---|
| Déclencheur | GitHub Actions « Contenu », manuel, **simulation cochée par défaut**, environnement `production` (approbation) | `.github/workflows/contenu.yml` [V] |
| Transport | `appleboy/ssh-action` vers le Droplet, `git fetch` (pas de checkout), timeout 120 min | `contenu.yml` [V] |
| Source des JSON en prod | Bind mount `./backend/ingest:/app/ingest` = **le clone git du serveur** (pas l'image : `.dockerignore:23`) | `docker-compose.yml:39` [V] |
| Périmètre | `git diff --diff-filter=A <contenu_commit>..HEAD` sur `backend/ingest` et `backend/programme/fixtures` | `contenu.sh:77-81` [V] |
| Fichiers modifiés | **Seulement signalés**, jamais appliqués | `contenu.sh:18-22, 98-103` [V] |
| Ordre | programme → corrections → inédites → quiz → `valider_ingestion --since` → `indexer_recherche` | `contenu.sh` [V] |
| Détection d'erreur | recherche de `erreur(s) :`, `CommandError`, `Traceback` dans la sortie | `contenu.sh:128-134` [V] |
| Point de départ | `.deploy/contenu_commit`, avancé seulement si tout est vert | `contenu.sh` [V] |
| Sauvegarde avant contenu | **Aucune** (elle n'existe que dans `deploy.sh`) | [V] |
| Filtre des dossiers | tout chemin dont un composant commence par `_` est ignoré (`_audit`, `_gce_staging`...) | `contenu.sh:90`, `run_ingestion` [V] |
| Hors canal | `definir_papers_vitrine`, `definir_quiz_vitrine`, `completer_points_gce`, `ajouter_rappels_gce`, `generate_inedit_sujet_pdfs`, `calculer_frequences_cours` : **à la main en SSH** | `MISE-EN-LIGNE-GCE.md` §3, grep [V] |

Application : `deploy.sh` sauvegarde Postgres (échec = abandon), tire les images GHCR par SHA, applique les
migrations (`run --rm --no-deps`), bascule, exige `/healthz` = SHA déployé (45 essais de 2 s), sinon retour
arrière des images. Pas de `trap`, pas de verrou, pas de `concurrency` dans les workflows [V].

---

## 3. Identité et comportement d'ingestion, type par type

| Type | Modèle | Clé d'identité réelle | Contrainte d'unicité en base | Si l'objet existe | `updated_at` / empreinte |
|---|---|---|---|---|---|
| Lesson (sujet) | `catalog/models.py:730` | **Combinaison sans contrainte** : `epreuve_source` + matière + année + `CORR` + pays + variante + paper (`ingestion.py:1675-1680`) | Seul `slug` | Réutilisée ; seuls les champs **vides** sont complétés ; `title`/`slug` jamais recalculés | `updated_at` ; pas d'empreinte |
| Exercise | `:977` | `(lesson, numero_exercice)` | `unique_exercice_par_lesson` | **Ignoré** ; `force=True` = delete + recréation | `updated_at` |
| Question | `:1096` | aucune propre (créée avec l'exercice) | `unique_question_par_exercice` | jamais touchée seule | `updated_at` |
| Figure d'exercice | `:1215` | `(exercise, external_id)` | `unique_figure_par_exercice` | créée avec l'exercice ; PNG absent = `IngestionError` | `created_at` |
| Cours | `:1255` | `external_id` (= `cours_id`) | `external_id`, `slug` ; **`titre` non unique** | cas 1 : retour sans mise à jour ; cas 3 : **dédoublonnage par `titre__iexact` parmi les VALIDE : le nouveau cours n'est pas créé et son contenu est perdu** (`:2094-2100`) | `updated_at` |
| Rappel de méthode | `:1463` | `get_or_create(external_id)` | `external_id` | si l'id existe sur un autre exercice, **rien n'est rattaché** (silencieux) [D] | `created_at` |
| Tag | `:661` | `name` exact → `iexact` → variantes sans accents/pluriel → création | `name` (sensible à la casse) | réutilisé ; peut poser `savoir_officiel` si NULL | aucun |
| Module / Savoir | `programme/models.py:4, 61` | Module : `(subject, classe, serie_label, numero)` ; Savoir : `(module, numero)` | Module oui ; **Savoir aucune** | **mis à jour** (`update_or_create`) ; savoirs absents du JSON **supprimés** (SET_NULL sur Tag/Question/Séance) | aucun |
| CompetenceItem | `quiz/models.py:49` | `external_id` si non vide | partielle sur `external_id != ""` | **ignoré** ; **sans `external_id` : toujours créé (doublon à chaque relance)** | `updated_at` |
| Figure de quiz | `:147` | `(item, external_id)` | oui | créée avec l'item | `created_at` |
| Blueprint | `inedit/models.py:56` | `external_id` | partielle | ignoré | `updated_at` |
| EpreuveInedite | `:126` | `external_id` | partielle + `slug` | ignorée | `updated_at` |
| ExerciceInedite / QuestionInedite | `:288` / `:337` | créés avec l'épreuve | oui | jamais touchés | **aucune date** |
| RappelDeMethodeInedite | `:431` | `get_or_create(external_id)` | oui | idem rappel | `created_at` |

Autres faits utiles [V sauf mention] :
- Un changement de `annee`, `epreuve_source` ou `matiere` dans un JSON déjà ingéré **crée une deuxième Lesson**
  (épreuve en double) : aucune contrainte ne l'empêche [D].
- `meta.statut` d'un JSON de cours est ignoré ; seul un `statut` « obsolete… » sur un exercice est lu (`:2232`).
- `published_at` n'est quasiment jamais renseigné (seul le gate l'écrit) ; les actions admin inédit/quiz font
  `queryset.update(statut=…)` sans le toucher.
- Les `.update()` ne bumpent pas `updated_at`, donc échappent à `valider_ingestion --since`.
- Hors transaction dans l'ingestion quiz : création de Tag et liaison `savoir_officiel` (`:522-524`) ;
  un item rejeté peut laisser ces effets.
- Les filtres de dossiers n'excluent que les enfants directs de `_inedit` et `_quiz` : `_inedit/_bareme/*.json`
  et `_quiz/_audit` sont traités puis échouent en « Pays inconnu » [D].
- `load_programme_officiel` : un seul `atomic` par fichier ; un doublon de Savoir (aucune contrainte) fait
  tout échouer.

### Formats de fichiers (JSON existants à envelopper, pas à remplacer)
- **Exercice** `ingest/<pays>/<epreuve>/<epreuve>_exercice_<n>.json` : `epreuve_source, matiere, serie,
  examen, annee, …, questions[{numero, enonce_markdown, corrige_markdown, themes, rappels_de_methode, …}]`
  (obligatoires : `REQUIRED_KEYS`, `:1541`). Figures : PNG à côté du JSON, `…_exercice_<n>_fig_<k>.png`.
- **Cours** `…_cours_<slug>.json` : `cours_id`, `meta{…}`, `source{…}`, `sections[]` ; trié par la présence de `sections`.
- **Quiz** `_quiz/<pays>/*.json` (tableau) : `external_id` (`cqc-<slug>-<diff>-<i>`), `theme` (Tag exact), …
- **Inédite** `_inedit/<pays>/bp-…json` / `ep-…json` ; figures = **SVG intégré au Markdown**, aucun fichier image.
- **Programme** `programme/fixtures/programme_officiel_cm_*.json` (10 fichiers).

---

## 4. Fichiers et stockage

### 4.1 Champs fichier [V]
| Modèle.champ | Storage | Accès |
|---|---|---|
| `Lesson.sujet_pdf` | `default` | public (Spaces `public-read`) ; servi par `/access/lessons/<id>/sujet.pdf` avec quota ; Caddy bloque `/media/sujets_pdf/*` |
| `Figure.image`, `CompetenceItemFigure.image` | `default` | public ; converties en WebP ≤ 1200 px à l'ingestion |
| `EpreuveInedite.sujet_pdf` | `inedit_protected` | privé |
| `FicheGeneree.*_pdf`, `QuizSession.*_pdf` | `fiches_protected`, `quiz_protected` | privé, générés par l'élève |
| PDF de cours | `cours_protected`, **sans FileField**, nom `<variante>/<pk>-<empreinte>.pdf` | cache régénérable, génération détachée au premier téléchargement |
| `ManualPayment.proof` | `default` | **public** (voir risque R7) |

Deux modes selon `SPACES_BUCKET` (`settings.py:373-455`) : Spaces (public-read + 4 storages privés à la
racine du même bucket) ou disque (`MEDIA_ROOT`, `protected_media/{,fiches,quiz,cours}`). **[I] Le mode réel
de la production n'est pas dans le dépôt.**

### 4.2 Comment les fichiers arrivent en prod aujourd'hui
- **JSON et PNG source** : par le clone git (bind mount). Les PNG doivent être **à côté du JSON**
  (`_attach_figures`, `ingestion.py:1415-1417`) ; sinon l'exercice échoue en prod.
- **Figures** : 6 258 fichiers de `media/` sont suivis par git (malgré `.gitignore`) et atterrissent dans
  `./media` du serveur par le checkout ; les nouvelles figures sont écrites par Django à l'ingestion.
- **PDF de sujet** : produits **sur place** par `generate_sujet_pdfs`, chaîné à la fin de `ingest_corrections`
  (`:107`). Ils ne sont **jamais** poussés depuis le poste. `generate_inedit_sujet_pdfs` n'est lancé par
  aucun automatisme [V].
- **Sauvegarde fichiers** (`sync_media.sh`) : `rclone copy /media` vers `SPACES_BACKUP_BUCKET`. Couvre `./media`
  du serveur ; **ne couvre pas `protected_media`** ni les objets déjà dans le bucket public.

### 4.3 Problèmes de fichiers constatés
- **Écrasement silencieux sur Spaces** [D] : aucun `AWS_S3_FILE_OVERWRITE` (grep négatif confirmé), donc
  `file_overwrite=True` par défaut. Deux figures de même pays et de même nom s'écrasent. Sur disque, Django
  suffixe (1 760 doublons suffixés sur 4 747 fichiers dans `media/figures/cm` en local). Les PDF de sujet
  sont nommés par `slugify(title)`, non unique.
- **Références cassées → HTTP 500** : un `sujet_pdf` référencé mais absent lève une exception dans
  `ouvrir_sujet` (`access/sujets_publics.py:22-26`) ; le crédit de quota est annulé (`quota.py:436-440`).
- **Figures et PDF « avant filigrane »** : `/media/figures_avant_filigrane/*` n'est **pas** bloqué par Caddy
  alors que le commentaire dit « jamais à servir » ; 416 fichiers y sont suivis par git et donc présents
  sur le serveur. 116 PDF `sujets_pdf_avant_filigrane` aussi sont versionnés.
- **`/app/logs` et `/tmp` ne sont pas montés** : rapports d'ingestion et verrous PDF perdus à chaque
  recréation du conteneur.

---

## 5. Compétences de génération

**Elles ne sont pas dans le dépôt.** Racine vivante (cache géré par Claude Desktop) :
`C:\Users\Administrateur\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\local-agent-mode-sessions\skills-plugin\b753a7e6-84a4-4175-9017-11ed073d6178\109e0e24-b249-4600-8c4f-284c2f0b64eb\skills\<nom>\SKILL.md`
(45 skills au `manifest.json`). Les notes mémoire pointant vers `Roaming\Claude` sont **périmées**.
Une écriture directe dans ce cache ne persiste pas : la voie fiable est `.skill` puis « Save skill » par vous.
**Aucun skill n'est exécutable en ligne de commande** : ce sont des prompts joués par une session Claude.
Ce qui s'automatise, ce sont leurs scripts et les commandes Django.

| Skill | Rôle | Entrée → sortie | Humain obligatoire |
|---|---|---|---|
| `correction-experte` | transcrire/corriger épreuves réelles + cours par rappel | PDF dans `ingest/<pays>/<épreuve>/` → `…_exercice_N.json`, `…_cours_<slug>.json`, `…_fig_K.png` | aucune relecture avant publication (VALIDE direct) ; garde-fous : `verifier_lot.py` + tunnel |
| `concepteur-epreuve-inedite` | blueprint puis épreuve inédite (jamais une copie) | `select_inedit_batch` / blueprint validé → `_inedit/<pays>/bp-…`, `ep-…` | **blueprint validé en admin ; épreuve publiée par clic admin** |
| `concepteur-quiz-competence` | items `CompetenceItem` autonomes | `select_quiz_batch` → `_quiz/<pays>/<slug>.json` | aucune relecture avant publication |
| `generer-batch-quiz-competence` | orchestration `select_quiz_batch` → génération → ingestion → tunnel | **skill projet** (`D:\edukora\.claude\skills`), absent du manifest Desktop | à la demande |
| `tunnel-completude-edukora` | boucle de correction post-ingestion (A→D) | rapport d'erreurs → JSON corrigés, `ingest_exercise(force=True)` | décisions « Humain » ; max 3 passes |
| `couverture-quiz-lot-edukora` | étape E : quiz manquants (≤ 5 compétences/passe) | thèmes du lot → `_quiz/…` | après `TUNNEL VALIDÉ` |
| `reproduire-figure-sans-filigrane` | figures propres, retraitement des figures ingérées | PDF d'origine → PNG ; `figures_manifeste`, `appliquer_figures_propres` | contrôle à l'œil de chaque figure |
| `enseignant` | relecture adversaire (écrit seulement des rapports) | base locale en lecture → `docs-relecture/enseignant/*.md` | confirme les constats |
| `eleve` | test utilisateur dans le navigateur | persona + mission → `docs-relecture/eleve/*.md` | saisie du code e-mail |
| `audit-qualite-rendu` | rendu KaTeX du corpus | `dump_rendering_corpus` + vitest | valide les correctifs |
| `audit-couverture-programme`, `rattachement-savoir` | diagnostic de couverture ; rattachement (dormant depuis le 09-18) | lecture seule / diff d'un champ | — |

Décalages cache ↔ dépôt [V] : seul `concepteur-epreuve-inedite` a un `.skill` du dépôt **plus récent que le cache**
(`scripts/gce/inedites/concepteur-epreuve-inedite.skill`, 10-20 ; cache du 10-19) : **à réinstaller**.
`audit-couverture-programme` et `rattachement-savoir` n'ont aucune copie dans le dépôt.

Prérequis communs : Docker (`edukora-backend-1`, base injoignable depuis l'hôte), code backend **non** bind-monté
(commande absente = `docker cp` ou rebuild local), Git Bash avec `MSYS_NO_PATHCONV=1`, **pas de `python` nu**
(interpréteurs : `Python314`, `venv`, `Anaconda3` pour PyMuPDF/OpenCV), Node + vitest (porte KaTeX), Tesseract.
**[I]** Une tâche planifiée Cowork pour `correction-experte` existe-t-elle ? Non inspecté.

Conventions de nommage observées : dossier `<examen>-<serie>-<matière>-<année>-[officiel-]<pays>` ; GCE
`gce-ol-maths-2019-p1-officiel-cameroun` ; inédites `bp-<pays>-<matière>-<examen>-<série>-<seq>`,
`ep-<id blueprint>-<année>-s<n>`. `ingest/cm` : 1 987 dossiers, 21 921 JSON, 3 187 PNG (dont 644 dossiers GCE).

---

## 6. Données opérationnelles : jamais touchées par une synchronisation

Liste à faire valider (écriture interdite pour le moteur) :
- **users** : `User`, `Profil`, `OTPCode`, `AuthIdentity`.
- **subscriptions** : `Subscription`, `InscriptionInedite`, `InscriptionRepetiteur`, `ParrainageRecompense` ;
  `Plan` = configuration commerciale (prix, durée), à ne pas écraser.
- **payments** : `Transaction`, `MobileMoneyAccount`, `ManualPayment`.
- **quiz (activité)** : `QuizSession`, `QuizQuestion` (snapshot), `QuizAnswer`, `RevisionSchedule`,
  `SeanceJournaliere`, `ObjectifMatiere`, `VisiteAccueil`, `GainXP`, `JourXP`.
- **inedit (activité)** : `TentativeInedite`, `TentativeReponse`.
- **access** : `LectureProgress`, `ExerciceFait`, `MarqueEtude`, `CompteurQuota`, `TelechargementPdf` ;
  `ReglagesTelechargement` = configuration.
- **simulations**, **fiches** (`FicheGeneree`, `FicheItem`), **analytics**, **relances**, **whatsapp**,
  `RechercheSansResultat`.
- **Dérivés reconstruits, jamais synchronisés** : `EntreeRecherche`, `TermeRecherche` (`indexer_recherche`),
  `FrequenceCours` (`calculer_frequences_cours`). `Temoignage` est éditorial.
- **Référentiel lu, jamais modifié** : `Country`, `Subject`, `Series`, `Cursus`, `Filiere`, `ExamenLabel`, `ExamSession`.

**Suppressions en cascade à bloquer dans le moteur** (un delete de contenu détruit de l'activité élève) :
Lesson → `LectureProgress`, `MarqueEtude`, `SimulationEpreuve` ; Cours → `LectureProgress`, `MarqueEtude` ;
Exercise → `ExerciceFait`, `SimulationReponse` ; Tag → `RevisionSchedule` ; EpreuveInedite/QuestionInedite →
tentatives et réponses ; Savoir supprimé → SET_NULL sur Tag/Question/Séance. `FicheItem.competence_item` est
PROTECT (empêche de supprimer un item utilisé).

---

## 7. Sauvegarde, journal, reprise

- **Postgres** : `backup.sh` (cron 02:00, `pg_dump --format=custom`, refus < 1 000 octets, envoi vers
  `SPACES_BACKUP_BUCKET/postgres/<niveau>/`) ; `restore.sh` restaure dans une **nouvelle** base. **Aucune
  vérification d'intégrité du dump** (`pg_restore --list`), rétention via règles manuelles du dashboard **[I]**,
  **aucune trace d'un test de restauration** dans le dépôt **[I]**.
- **Fichiers** : voir §4.2 ; `protected_media` non sauvegardé ; `ManualPayment.proof` non sauvegardé en mode Spaces.
- **Journal** : `.deploy/historique.log` n'enregistre ni débuts d'opération, ni `--sans-sauvegarde`, ni échecs
  de rollback, ni échecs de `contenu.sh`. `.deploy/` n'est pas dans `.gitignore` (vide en local).
- **Local** : `scripts/backup-local.ps1` (dump dans `backups/postgres`, rétention 14 jours) ; ce n'est pas la prod.
- **SSH** : secrets `DEPLOY_HOST/USER/SSH_KEY/PATH` côté GitHub ; utilisateur `deploy` (groupes `sudo` et `docker`,
  équivalent root) ; `harden-ssh.sh` désactive root et mot de passe ; **empreinte d'hôte non épinglée**, port 22
  ouvert à tous.

---

## 8. Matrice de risques (ce que fait le code aujourd'hui)

| # | Scénario | Comportement actuel | Gravité |
|---|---|---|---|
| R1 | Corriger un contenu existant | Ignoré par le canal ; réingestion admin = suppression/recréation avec perte d'`ExerciceFait`/`SimulationReponse` | **Haute** |
| R2 | Lot « contenu seul » | Impossible sans commit de code : pas d'image, refus si clone ≠ `current_tag` | **Haute** |
| R3 | Contenu local non committé (550 JSON `cm/` en 93 dossiers GCE + 85 PNG, médias) | Jamais livré ; invisible dans `git status` | **Haute** |
| R4 | Modification concurrente local/prod | Aucune détection (rien ne compare) | Haute |
| R5 | Coupure SSH en cours d'ingestion | Pas de transaction de lot : état partiel ; gate, thèmes proposés et PDF non exécutés ; rapport « running » mort détecté par pid | Haute |
| R6 | Relance après timeout | OK pour la création (existant ignoré) ; pas de statut de lot ; `contenu_commit` n'avance qu'en cas de succès complet | Moyenne |
| R7 | Données sensibles publiques | `ManualPayment.proof` en `default` (public-read sur Spaces, ou `/media/manual_payments/` servi par Caddy) ; `figures_avant_filigrane` servi | Moyenne (hors périmètre sync, à signaler) |
| R8 | Écrasement de fichiers sur Spaces | silencieux (`file_overwrite` par défaut) | Moyenne |
| R9 | Fichier référencé absent | HTTP 500 + crédit de quota annulé | Moyenne |
| R10 | Déploiements/ingestions simultanés | aucun `concurrency`, aucun `flock` | Moyenne |
| R11 | `rollback.sh` | revient aux images, pas au clone git ; contenu.sh refuse ensuite | Moyenne |
| R12 | `git checkout` bloqué | fichier suivi modifié ou figure committée après écriture Django en prod | Moyenne |
| R13 | Publication sans relecture | exercices, cours et quiz sont VALIDE à la création | Produit (à assumer) |
| R14 | Retrait par BROUILLON | republié par le gate au run suivant | Moyenne |
| R15 | Sauvegarde non vérifiée | dump jamais testé en restauration ; fichiers partiellement couverts | **Haute** avant toute opération destructive |

---

## 9. Incertitudes à lever avant la phase 2

À lever en lecture seule sur le serveur avec `deploy/diagnostic-serveur.sh` (aucun secret en sortie) :
1. **`SPACES_BUCKET` renseigné en prod ?** (Spaces ou disque ; conditionne toute la stratégie fichiers).
2. `SPACES_BACKUP_BUCKET` ≠ `SPACES_BUCKET` ? Cycle de vie du bucket de sauvegarde, date du dernier test de restauration.
3. Contenu de `.deploy/` (SHA courant, `contenu_commit`), clone propre ou non.
4. CDN Spaces actif (`SPACES_CDN_DOMAIN`) ? Les URL de figures en base sont-elles relatives ou absolues ?
5. Le contenu GCE récent est-il déjà en prod, et l'état « Chargement de départ » du contenu a-t-il été fait ?
6. Doublons de Lesson existants en base (aucune contrainte sur la clé réelle).
7. Une tâche Cowork planifiée existe-t-elle pour `correction-experte` ?

---

## 10. Pré-analyse de la décision d'architecture (point d'arrêt n°1)

Contraintes qui ressortent de l'audit, quelle que soit l'option :
- **Un moteur de mise à jour sur place est indispensable** (jamais delete + recréation) : c'est le cœur du
  chantier, et il doit être **livré par le canal Application** (nouvelle commande Django dans l'image).
  Première conséquence : un déploiement applicatif préalable est inévitable, une seule fois.
- Il faut une **empreinte canonique** par contenu (colonne ou table de journal ; migration additive).
- Il faut une identité stable **explicite pour Lesson, Exercise et Cours** : aujourd'hui elle n'est pas portée
  par une contrainte (Lesson) ou repose sur le titre (Cours, dédoublonnage destructeur).

| | A. Étendre git + Actions | B. Lot (archive + `scp` + SSH) | C. Hybride (manifeste par git, binaires par archive/Spaces) |
|---|---|---|---|
| Indépendance du code | **Non** (R2 : couplé aux SHA) sans refonte des workflows | **Oui** | Partielle |
| Contenus non committés (R3) | Il faut `git add -f` systématique, risque d'oubli | **Résolu** : le lot est construit depuis ce qui est ingéré en local | Partiel |
| Binaires (figures, PDF) | Dans git (gros dépôt, 6 258 fichiers déjà suivis) | **Dans le lot, SHA-256 vérifié** | Selon le choix |
| Traçabilité / approbation | Native (Actions, environnement `production`) | À construire (journal de lots, rapport) ; approbation = confirmation du script | Mixte |
| Reprise après coupure SSH | Timeout 120 min déjà géré | Possible avec `statut <batch_id>` côté serveur | Mixte |
| Effort / risque | Moyen mais plafonné par R2 | Plus de code neuf (script PowerShell + moteur + journal) | Le plus complexe |

**Recommandation provisoire : option B**, en gardant `contenu.sh` comme voie de secours pour les créations
simples. Motifs : c'est la seule qui tient l'exigence « indépendant du code » (R2), qui supprime le risque
silencieux des contenus ignorés (R3), et qui rend possible le contrôle d'intégrité fichier par fichier.
Prix : journal de lots et approbation à construire, et une première livraison applicative du moteur.
Option A resterait viable seulement si vous acceptez que chaque mise à jour de contenu passe par un commit
et un déploiement d'application.

### Questions pour vous (décisions requises avant la phase 2)
1. **Option A, B ou C ?** (recommandation : B).
2. **Politique de publication des corrections** : une version corrigée d'un exercice déjà publié passe-t-elle
   en ligne directement (comme la création aujourd'hui) ou repasse-t-elle par une validation humaine ?
3. **Retraits** : quel état utiliser (REJETE est le seul stable face au gate) ? Souhaitez-vous « dépublier »
   ≠ « supprimer » avec suppression physique interdite par défaut ?
4. **Périmètre des types pour la première livraison** : recommandation = exercices + cours + quiz ; inédites,
   programme et figures retraitées dans un second temps.
5. **Les 550 JSON ignorés (93 dossiers GCE) de `ingest/cm/`** : les intégrer au prochain lot (c'est l'objet même de la chaîne)
   ou seulement ceux d'une liste que vous validez ?
6. **Lever les inconnus du §9** : m'autorisez-vous à vous guider pour lancer `diagnostic-serveur.sh` (c'est vous
   qui l'exécutez sur le serveur) ? Je n'accède pas à la production.
7. **Réinstallation de `concepteur-epreuve-inedite`** (`.skill` du 10-20 non installé) : à faire de votre côté.
8. **Constats hors périmètre à traiter à part** : `ManualPayment.proof` public, `figures_avant_filigrane`
   servi par Caddy, empreinte d'hôte SSH non épinglée.
