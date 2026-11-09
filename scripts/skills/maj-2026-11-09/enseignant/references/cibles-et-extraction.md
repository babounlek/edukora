# Cibles et extraction (lecture seule)

Tout se fait sur la **base locale** (jamais la prod), en lecture seule. Le code Python n'est pas monté dans le conteneur : on lit par `docker compose exec backend python manage.py shell` (ou `docker exec edukora-backend-1 python manage.py shell -c "..."`). Sous Git Bash, préfixer par `MSYS_NO_PATHCONV=1` pour les chemins. Aucune requête d'écriture (`save`, `update`, `delete`, `bulk_*`, `--appliquer`).

Les chiffres et noms de champs ci-dessous viennent des modèles du projet ; si une requête échoue sur un nom de champ, relire le modèle (`backend/catalog/models.py`, `backend/quiz/models.py`, `backend/inedit/models.py`) plutôt que deviner.

## Corrigés d'épreuves et d'exercices

- `catalog.Exercise` : `numero_exercice`, `points` (texte), `enonce_intro_markdown`, `enonce_markdown`, `corrige_markdown`, `themes`, `statut`, `lesson` (l'épreuve), `incertitudes` (doutes de l'auteur : voir le protocole).
- `catalog.Question` : `exercise`, `numero`, `enonce_markdown`, `corrige_markdown`, `type_reponse` (`OUVERTE` ou `QCM`), `choix` (JSON), `reponse_correcte`, `points`, `difficulte_estimee`, `savoir_officiel`.
- L'épreuve elle-même est une `catalog.Lesson` (pays, examen, série, matière, année, `statut`). Filtrer sur `statut=VALIDE` pour ce que voit l'élève ; relire aussi les `BROUILLON` d'un lot avant publication si c'est la demande.
- Source brute : `backend/ingest/<pays>/<épreuve>/<épreuve>_exercice_<n>.json` (écrasable : c'est le dossier de travail de l'auteur, la base fait foi pour « ce que voit l'élève »).

## Cours

- `catalog.Lesson` de type cours (`LessonType`) : définitions, méthode, exemple résolu, erreurs classiques, exercices d'appropriation, à retenir (sept sections côté auteur, voir `correction-experte`, « Mode cours »).
- Référentiel : `programme.Module` / `programme.Savoir` (francophone seulement ; **il n'existe pas pour le GCE**, le syllabus du Board est alors la référence et n'est pas en base).

## Items de quiz

- `quiz.CompetenceItem` : `external_id`, `theme`, `subject`, `cursus` (plusieurs), `enonce_markdown` (doit se lire seul), `corrige_markdown`, `difficulte_estimee`, `type_reponse`, `choix`, `reponse_correcte`, `statut`, `est_vitrine` (item montré en essai gratuit : lui accorder plus d'attention), `source_exercises`.
- Un item rattaché à plusieurs cursus doit être juste ET au programme de chacun : un item de BAC glissé dans le BEPC est un constat E2 (cas déjà vu : l'item 2558 « cubes de binômes »).

## Épreuves inédites

- `inedit.Blueprint` : `titre`, `sections_plan` (JSON), `duree_minutes`, `bareme_total`, `competences`, `cursus`. C'est le contrat que l'épreuve doit respecter.
- `inedit.EpreuveInedite` : `titre`, `subject`, `cursus`, `blueprint`, `statut`, `score_originalite` / `score_qualite` (notes de l'auteur : ne pas s'en servir), `est_gratuite`.
- `inedit.ExerciceInedite` puis `inedit.QuestionInedite` : `numero`, `enonce_markdown`, `corrige_markdown`, `type_reponse`, `choix`, `reponse_correcte`, `points` (décimal), `criteres_notation` (JSON : voir `grille-de-notation.md`), `difficulte_estimee`.
- Contrôles propres à une inédite : somme des `points` = `bareme_total` du Blueprint ; durée plausible pour le volume ; chaque compétence du Blueprint est évaluée ; **originalité** : un énoncé qui reprend mot pour mot une annale réelle est un constat (comparer avec des annales de la même matière dans la base : `Exercise.enonce_markdown`).

## Échantillonnage

- Un lot de 30 épreuves ne se relit pas en entier en profondeur. Stratifier : par exercice (1er, milieu, dernier), par type (calcul, rédaction, QCM), par difficulté étiquetée, par année. Annoncer la règle et la taille.
- Priorité à ce qui touche le plus d'élèves : items `est_vitrine`, épreuves gratuites, cours des thèmes les plus fréquents, épreuves récemment ingérées.
- Un défaut trouvé relance une relecture **ciblée de ses voisins** (même auteur, même lot, même motif) : les erreurs se regroupent.

## Séparer énoncé et corrigé

Écrire deux fichiers par objet dans le répertoire de travail de la session (pas dans le dépôt) : `<id>.enonce.md` et `<id>.corrige.md`. Un petit script d'extraction qui ne sort que les champs `enonce_*`, `choix`, `points` pour le premier, et `corrige_*`, `reponse_correcte`, `criteres_notation` pour le second, évite toute fuite par inadvertance.
