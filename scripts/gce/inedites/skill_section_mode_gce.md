## Mode GCE (sous-système anglophone) : à lire AVANT le reste quand la demande vise le GCE

**Déclencheur** : la demande parle de GCE, O Level, A Level, Ordinary/Advanced Level, « Paper 1/2/3 », GCE Board, d'une matière en anglais
(Mathematics, Physics, Chemistry, Biology, English Language, History...), ou donne `examen: gce_ol` / `gce_al`. Tout le reste du skill (contrat JSON,
corrigés, figures, LaTeX, nommage) s'applique ; cette section en **change les paramètres**. Guide canonique, avec tous les chiffres mesurés sur
2 895 fichiers de papers réels : `scripts/gce/INEDITES_GCE.md` du dépôt (à lire en entier avant le premier blueprint d'un type de paper nouveau).
Étalon complet et contrôlé : `ingest/_inedit/cm/bp-cm-gce-ol-maths-p1-1.json` et `ep-cm-gce-ol-maths-p1-1-2026-s1.json`, produits par
`scripts/gce/inedites/generer_maths_p1.py`.

### Paramètres GCE du contrat

- **Une inédite = un paper** (Paper 1 QCM, Paper 2 rédigé, Paper 3 pratique). Le numéro de paper n'a pas de champ : il est dans le `titre`
  (`Mathematics GCE O Level Paper 1 – Original Paper No. 1`), dans l'`external_id` (`bp-cm-gce-ol-maths-p1-1`, `ep-cm-gce-ol-maths-p1-1-2026-s1`) et
  dans la consigne d'`enonce_intro_markdown`. « Original Paper » est le mot de l'interface anglaise ; jamais « Épreuve inédite n° » ici, jamais de
  tiret cadratin dans le contenu (le `–` du titre est un séparateur autorisé).
- `matiere` en libellé anglais (`Mathematics`...) ; `cursus` = `[{"examen":"gce_ol","serie":""}]` (ou `gce_al`) ; **pas de série**, pas de
  `savoirs_officiels` ni de `savoir_officiel` (référentiel absent).
- Contenu en **anglais clair** de niveau Form 5 (O/L) ou Upper Sixth (A/L), contextes camerounais (FCFA, Buea, Bamenda, Douala), SI, `g = 10 m s^-2`,
  **point décimal**, milliers par `\,` (`$240\,000$`). Les repères `### Rappel de méthode`, `### Piège à éviter`, `### Conseil` restent **en
  français** (le frontend les détecte ainsi, le PDF les traduit).
- `duree_minutes` = durée réelle du paper (90 pour un Paper 1) ; `bareme_total` = total des points du paper.
- `themes` = noms de `Tag` existants en minuscules (vocabulaire de `scripts/gce/consignes/CONSIGNES.md`), jamais inventés ;
  `rappels_de_methode[].competence` = **titre exact du `Cours` existant** du thème (`scripts/gce/inedites/cours_titres_gce_maths_ol.json`).
- Corrigé de QCM : `### Rappel de méthode` (règle générale, un paragraphe), résolution, `**Answer: C.**`, puis `### Piège à éviter` (qui nomme l'erreur
  menant à chaque distracteur) et `### Conseil` si pertinents.

### Règle d'or : la STRUCTURE se copie, le CONTENU jamais

Avant de planifier un paper, **mesurer le corpus réel** de la matière (`backend/ingest/cm/gce-ol-<matiere>-*-p<paper>-officiel-cameroun`) : nombre de
questions, ordre des thèmes, poids de chaque thème, répartition de difficulté, options, figures, durée, consignes. Le blueprint les reprend, chiffrés,
dans `sections_plan[0]` (`format`, `ordre`, `repartition`, `repartition_difficulte`, `figures_prevues`). Aucune donnée, aucun contexte, aucun nom,
aucune figure, aucun jeu d'options d'un sujet réel dans l'inédite ; le gabarit d'énoncé de syllabus (« The median of ... is ») revient légitimement.

### Paper 1 QCM (toutes matières)

1 exercice `"1"`, 50 questions `"1"` à `"50"`, `type_reponse: "qcm"`, 4 options `a`-`d`, 1 point chacune, exercice `points "50"`, `groupes: []`,
`duree_minutes: 90`, jamais de `criteres_notation`. Ordre du syllabus, du plus simple au plus difficile à l'intérieur de chaque bloc. Difficulté :
45 à 70 % faibles, 1 à 4 élevées. Clés équilibrées (12-13 par lettre, jamais 3 de suite) **placées par le générateur**, jamais tapées. Distracteurs =
erreurs types nommées dans le piège du corrigé. Jamais « all/none of the above » en Maths, Physics, Chemistry, Computer Science, Economics, Commerce.
Chaque donnée d'une figure est écrite aussi dans son `<desc>`. Fabrication par un script générateur, voir l'étalon.

### Autres papers (règle clé de chacun ; détail dans le guide §5)

- **Structuré, tout obligatoire** (Maths P2 : Section A 10 questions de 4 points, Section B 4 questions de 15 points, total propre de 100) :
  `groupes ["SECTION A"]`, `numero_exercice` `"1"`-`"10"` puis `"B1"`-`"B4"`, sous-questions `a`, `b`, `c` avec `points` et `criteres_notation` exacts.
- **Structuré avec choix** (Biology, Chemistry, History, Geography, Economics, Commerce...) : la plateforme ne code pas les règles de choix des
  inédites. Écrire la version **« answer ALL »** limitée aux questions réellement à traiter, la règle réelle dans le blueprint et l'intro.
- **Essais** (History, Religious Studies, Philosophy) : jamais un sujet réel reformulé, faits exacts, corrigé = plan et essai modèle, grille par
  contenu, exactitude, structure, exemples, langue.
- **Langues** : textes **originaux** (jamais un extrait publié), une seule réponse défendable par QCM, composition notée sur contenu, organisation,
  expression, orthographe.
- **Pratique** (Computer Science, ICT P3) : énoncé **complet en soi** (les fichiers du jour ne sont pas fournis), corrigé = algorithme, code, exemple
  d'exécution, code exécuté ou traduit en Python, sinon `incertitudes`.
- **Quantitatif** (Economics P3, Mechanics, Statistics) : tableaux Markdown, unités SI, résultat de `(a)` rappelé avant de servir à `(b)`.
- **Figures** : Maths et Physics complètes (graphes, géométrie, circuits), Biology/Geology sans schémas anatomiques ou de coupe, Geography/History sans
  cartes, langues et Religious Studies sans figure.

### Contrôles obligatoires (dans cet ordre, depuis `D:\edukora`)

1. Générateur du paper (`scripts/gce/inedites/generer_*.py`), qui écrit blueprint et épreuve dans `backend/ingest/_inedit/cm/`.
2. `venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_<paper>.py` : recalcul indépendant, la clé est la seule option égale (0 écart).
3. `venv\Scripts\python.exe scripts\gce\inedites\controle_inedite_gce.py <ep.json> <bp.json> [--matiere maths] [--type qcm]` : contrat, barème, style,
   `$`, rappels verbatim, originalité contre le corpus réel (0 erreur ; relire chaque avertissement).
4. `venv\Scripts\python.exe scripts\gce\inedites\outils_figures\verifier_figures.py <ep.json>` puis `rendre_figures.py` et **regarder** chaque figure.
5. Rendu KaTeX par le vrai moteur (dump des champs, `AUDIT_RENDU_DUMP=... npx vitest run src/lib/audit-rendu.test.ts`) puis **ingestion à
   blanc** dans une transaction annulée (le blueprint passé `VALIDE` seulement à l'intérieur de la transaction : la validation humaine, elle, reste
   à faire dans l'admin) et PDF du sujet regardé page par page.

### Défauts de plateforme connus (ne pas les contourner dans le JSON)

`score_originalite` non discriminant pour un QCM court (13 sur l'étalon sans aucun
doublon réel) ; « Exercice 1 » non traduit dans le PDF anglais ; ni `numero_paper`, ni `code_matiere`, ni `regles_choix` dans le modèle inédit. Les
signaler dans le compte rendu, ne pas les « réparer » en dupliquant du texte. (Les options de QCM absentes du PDF, relevées à l'étalon, sont
corrigées dans `compile_from_exercices` ; ne jamais les recopier dans `enonce_markdown`.)

