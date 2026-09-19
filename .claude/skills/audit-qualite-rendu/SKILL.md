---
name: audit-qualite-rendu
description: Audite le rendu KaTeX/Markdown de tout le contenu edukora déjà en base (Lesson/Cours/Exercise/Question, quiz.CompetenceItem, inedit.EpreuveInedite/QuestionInedite) en faisant tourner le VRAI moteur de rendu (remark-math/remark-gfm/remark-breaks/rehype-katex, la chaîne exacte de EpreuveMarkdown.tsx), jamais en relisant le Markdown à l'œil ni en devinant depuis des regex seules. Corpus-entier par défaut, pas seulement un signalement isolé. À utiliser quand l'utilisateur signale un rendu cassé sur /epreuves|cours|quiz/*/lire (formule KaTeX qui ne s'affiche pas, page blanche, symboles bruts "$$" visibles), ou demande explicitement un audit/scan/vérification du rendu du corpus ("audit KaTeX", "scanne les erreurs de rendu", "vérifie que tout s'affiche bien", "y a-t-il d'autres épreuves touchées par ce bug ?").
---

# Audit qualité de rendu (KaTeX/Markdown)

Opérationnalise une méthode déjà éprouvée à la main de nombreuses fois sur ce projet
(voir la mémoire `feedback_correction_experte_consistency` et
`project_epreuve_reader_latex_rendering_fixes`) : ne jamais diagnostiquer un rendu
cassé en relisant le Markdown, toujours en faisant tourner le moteur réel ; ne jamais
supposer qu'un signalement est isolé avant d'avoir scanné tout le corpus.

## Prérequis

- **Outillage déployé** : la commande Django `dump_rendering_corpus`
  (`backend/catalog/management/commands/dump_rendering_corpus.py`) doit être présente
  sur l'image du conteneur `edukora-backend-1` en cours d'exécution - le code n'est PAS
  bind-monté (voir `docker/backend/Dockerfile`), donc un `git pull` sur l'hôte ne
  suffit pas. Si `docker exec ... manage.py dump_rendering_corpus` échoue avec "Unknown
  command", reconstruire l'image (`docker compose build backend && docker compose up -d
  backend`) avant de continuer.
- **`frontend/src/lib/audit-rendu.test.ts` présent** et ses dépendances installées
  (`unified`/`remark-parse`/`remark-rehype` en devDependencies - `npm install` côté
  `frontend/` si absent).

## Étape 1 - Dumper tout le contenu markdown réellement rendu

```bash
docker exec edukora-backend-1 python manage.py dump_rendering_corpus --output /app/ingest/_audit/rendu_corpus.json
```

Écrit un JSON (un enregistrement par champ markdown consommé par le frontend -
`Lesson.content_markdown`, `Cours.content_markdown`, `Exercise`/`Question`/
`CompetenceItem`/`QuestionInedite`/`EpreuveInedite` `enonce_markdown`/
`corrige_markdown`, texte de chaque choix QCM) taggé par pipeline de rendu réel :
`full` (EpreuveMarkdown.tsx - preprocessing + remark-math/gfm/breaks + rehype-katex,
la lecture longue) ou `bare` (fragment court inline sans preprocessing, ex. le texte
d'un choix QCM ou le titre d'une carte de fiche - voir `ChoixText`/`CardQuestion`
côté frontend). Le préfixe `_audit/` place le dump hors du corpus de contenu
(`run_ingestion` ignore déjà tout composant de chemin commençant par `_`, même
convention que `_quiz/`).

Le fichier vit dans `backend/ingest/_audit/` côté hôte (bind-monté) - noter son chemin
absolu pour l'étape 2.

## Étape 2 - Faire tourner le vrai moteur de rendu, corpus-entier

```bash
cd frontend
AUDIT_RENDU_DUMP=<chemin absolu vers rendu_corpus.json côté hôte> npx vitest run src/lib/audit-rendu.test.ts
```

Chaque enregistrement devient son propre test (`Lesson#123 slug [content_markdown/full]`)
- vitest liste noir sur blanc lesquels échouent, avec le message KaTeX exact ou le
déséquilibre de délimiteur détecté. Deux signaux distincts sont vérifiés, tous deux
nécessaires (vérifié empiriquement en construisant les deux cas à la main) :

1. **Une exception de parsing réelle** (ex. `\dfrac{1}` - argument manquant) → KaTeX
   lève une `ParseError`, rehype-katex la rattrape et produit un `span.katex-error`.
2. **Une commande totalement inconnue mais syntaxiquement acceptée** (ex. `\hlinex` -
   un contrôle indéfini tokenisé comme un seul mot) → KaTeX ne lève RIEN et ne pose
   AUCUNE classe `katex-error` : elle rend silencieusement le nœud en rouge d'erreur
   (`mathcolor`/`style` contenant `#cc0000`). Un check qui ne regarderait que la classe
   `katex-error` manquerait cette deuxième classe entière de bugs déjà documentée dans
   la mémoire du projet.

Sans `AUDIT_RENDU_DUMP` défini, ce fichier ne fait tourner qu'un test factice toujours
vert (`npm test` normal reste propre) - ce n'est un vrai audit que lancé explicitement
avec un dump frais.

**Ne jamais se contenter d'un check regex seul** en remplacement de cette étape : une
vérification structurelle (comptage de colonnes, `\hline` collé...) a déjà,
historiquement sur ce projet, manqué un bug réel (deux spans `$...$` adjacents sans
séparateur) que seule l'exécution du vrai moteur a révélé. Un scanner de parité de
délimiteurs `$`/`$$` reste utile en complément, mais pour LOCALISER la cause racine
d'une cascade d'erreurs qui semblent sans rapport - jamais comme détection principale.

## Étape 3 - Trier chaque anomalie avant de toucher quoi que ce soit

Pour chaque test en échec, avant toute correction :

1. **Combien d'enregistrements partagent exactement cette signature ?** Grep le dump
   JSON (ou re-scanner tout `backend/ingest/**/*.json`) pour ce motif précis. Un
   signalement qui touche 1 fichier et une anomalie qui en touche 50+ n'appellent
   jamais la même réponse (voir la mémoire `feedback_correction_experte_consistency`,
   "Eighth check" : 57% du corpus non conforme a fini par exiger un correctif
   plateforme, pas un re-patch fichier par fichier qui reviendrait à chaque nouvelle
   génération).
2. **Une règle du skill concerné (`correction-experte`, `concepteur-quiz-competence`,
   `concepteur-epreuve-inedite`) couvre-t-elle déjà ce cas sans ambiguïté ?**
   - Oui → dérive stochastique du LLM, pas un trou d'instruction. Ne pas toucher le
     skill. Corriger la donnée si isolé ; si récurrent, ajouter une tolérance côté
     plateforme (`catalog/ingestion_repairs.py`, `catalog/rendering.py`).
   - Non → vrai trou d'instruction. Proposer une mise à jour du skill concerné à
     l'utilisateur avant d'éditer quoi que ce soit (voir le flux `skill-creator` déjà
     établi pour `correction-experte` : copier le skill dans un dossier scratch, éditer
     la copie, `diff` contre l'original, empaqueter, livrer par `SendUserFile`).
3. **Est-ce un bug du code de rendu/ingestion lui-même** (comportement incorrect même
   sur une entrée conforme aux règles du skill) ? → corriger `catalog/rendering.py` /
   `catalog/ingestion.py` / `catalog/ingestion_repairs.py`, ajouter un test de
   régression (`backend/catalog/tests.py`), PUIS appliquer le correctif au contenu déjà
   en base :
   - Si la logique de compilation a changé (`compile_from_questions`/
     `compile_from_exercises`/`compile_from_sections`) : `python manage.py
     recompile_exercises` (recompile depuis les champs déjà en base, pas de
     réingestion).
   - Si la correction vit dans `ingestion_repairs.py`/`ingestion.py` (agit à
     l'ingestion) : réingérer depuis le JSON source (`ingest_exercise(..., force=True)`
     ou l'action admin "Réingérer depuis le fichier JSON source").
4. **Ne jamais rouvrir une décision déjà actée** sans raison nouvelle - certains
   correctifs plateforme existent précisément parce qu'un essai côté skill avait déjà
   été tenté et n'avait pas tenu à l'échelle (voir la mémoire, "Fourteenth check" :
   `_repair_missing_exercise_heading` a été délibérément déplacé côté plateforme après
   un échec documenté côté skill).

## Étape 4 - Re-vérifier corpus-entier, jamais juste les fichiers corrigés

Après toute correction (donnée, plateforme ou skill), refaire tourner les étapes 1-2
sur TOUT le corpus, pas seulement les enregistrements initialement en échec - un
correctif plateforme peut affecter des enregistrements qui n'avaient jamais été
signalés, et un correctif mal ciblé peut introduire une régression ailleurs (voir la
mémoire, "Twelfth check" : un correctif du "Eighth check" a cassé un cas différent non
testé lors du même passage).

## Étape 5 - Rapport avant/après

Résumer pour l'utilisateur : nombre d'enregistrements audités, nombre d'anomalies
trouvées groupées par cause probable et volume, décision prise pour chacune (donnée /
plateforme / skill / signalée sans agir), et confirmation du passage à zéro échec après
correctif. Ne jamais corriger silencieusement une anomalie de grande ampleur sans
l'avoir d'abord présentée - notamment tout ce qui touche potentiellement à une
correction déjà publiée à des élèves.

## Mode tunnel : la même vérification, limitée au dernier round d'ingestion

Cet audit corpus-entier est la vérification périodique. À la fin de CHAQUE round
d'ingestion, les skills producteurs (`correction-experte`, `concepteur-quiz-competence`,
`concepteur-epreuve-inedite`, `generer-batch-quiz-competence`) lancent à la place sa
version restreinte au contenu créé/modifié récemment :

```bash
bash scripts/tunnel_validation.sh <since>     # since = 2h, 90m, 1d ou datetime ISO
```

Le script enchaîne `manage.py valider_ingestion --since` (structure, vocabulaire de
thèmes, couverture, et écriture d'un dump de rendu restreint) puis le même
`audit-rendu.test.ts` que l'étape 2 ci-dessus - même moteur, périmètre réduit
(`dump_rendering_corpus --since` produit aussi ce dump seul). Tout échec de rendu
remonté par le tunnel se triage exactement comme à l'étape 3. Le tunnel ne dispense pas
de cet audit corpus-entier après un correctif plateforme (étape 4).

## Portée non couverte par cet audit (à traiter séparément si besoin)

Le PDF de sujet (`catalog/sujet_pdf.py`) utilise un **second moteur de rendu totalement
distinct** : Playwright + KaTeX `auto-render` (détection de délimiteurs par regex sur
du HTML brut, pas d'AST Markdown) contre `sujet_pdf_template.html` - jamais
remark-math/rehype-katex. Un contenu peut donc être sain sur `/lire` et cassé en PDF,
ou l'inverse. Cet audit ne couvre QUE le pipeline web (`EpreuveMarkdown`/pipeline
"bare"). Pour auditer le PDF, réutiliser le setup Playwright déjà existant dans
`sujet_pdf.py` (`window.__katexDone`) et chercher le même signal `#cc0000` dans le DOM
rendu plutôt que dans un arbre hast - pas encore outillé.

## NFR à respecter

- **Accès DB uniquement via `docker exec` dans `edukora-backend-1`** - jamais depuis un
  venv hôte nu (voir la mémoire projet, `DB_HOST=db` injoignable depuis l'hôte).
- **Corpus-entier par défaut** - un signalement ponctuel est le déclencheur, jamais la
  portée de l'investigation.
- **Jamais de correction silencieuse à grande échelle** - toute anomalie touchant plus
  qu'une poignée d'enregistrements isolés repasse par l'utilisateur avant action (sauf
  motif mécanique déjà identique à un précédent déjà tranché).
- **Rebuild Docker après tout changement de code backend** (`catalog/rendering.py`,
  `ingestion.py`, `ingestion_repairs.py`, ou la commande `dump_rendering_corpus`
  elle-même) - aucun bind-mount de code source, un simple redémarrage du conteneur ne
  suffit pas.
- **Environnement de production réelle** (edukora.africa) - toute réingestion/
  recompilation touche le contenu réellement servi aux élèves abonnés.
