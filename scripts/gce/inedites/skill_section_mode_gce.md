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
`duree_minutes: 90`, jamais de `criteres_notation`. **Ordre : mesurer celui du vrai paper** (Maths : ordre du syllabus, du plus simple au plus difficile dans
chaque bloc ; Biology : ordre mélangé, aucun bloc par chapitre). Difficulté : 45 à 70 % faibles, 1 à 4 élevées. Clés équilibrées (12-13 par lettre, jamais 3 de suite) **placées par le générateur**, jamais tapées. Distracteurs =
erreurs types nommées dans le piège du corrigé. Jamais « all/none of the above » en Maths, Physics, Chemistry, Computer Science, Economics, Commerce.
Chaque donnée d'une figure est écrite aussi dans son `<desc>`. Fabrication par un script générateur, voir l'étalon.
**Formats spéciaux** : les vrais Paper 1 de Chemistry (O Level aussi) contiennent 0 à 6 questions de « completion multiple » (réponses numérotées 1 à 4, options fixes
« 1, 2 and 3 only / 1 and 3 only / 2 and 4 only / 4 only ») et d'« assertion-raison » (tableau de deux énoncés, quatre options fixes), la consigne imprimée étant répétée dans chaque
question du bloc. Les reproduire par blocs consécutifs, options à **ordre imposé** (la clé découle du contenu, le générateur place les autres clés autour). Toute valeur qu'une figure
demande de lire est placée sur une graduation.

### Autres papers (règle clé de chacun ; détail dans le guide §5)

- **Structuré, tout obligatoire** (Maths P2 : Section A 10 questions de 4 à 5 points, total 45, Section B 4 questions de 15 points, total 60, soit 105 comme les
  sujets réels récents ; étalon `ep-cm-gce-ol-maths-p2-1-2026-s1`) : `groupes ["SECTION A"]`, `numero_exercice` continu `"1"`-`"10"` puis
  `"B1"`-`"B4"` (le tri est naturel depuis le 2026-10-19 ; l'étalon garde `"01"`-`"10"`, hérité de l'ancien tri en texte), sous-questions `a`, `b`, `c` avec `points` et `criteres_notation` exacts, parties
  `(i)`, `(ii)` dans `groupe_local`, tracé attendu dans le corrigé seulement.
- **Structuré avec choix** (Biology, Chemistry, History, Geography, Economics, Commerce...) : la plateforme ne code pas les règles de choix des
  inédites. Écrire la version **« answer ALL »** limitée aux questions réellement à traiter, la règle réelle dans le blueprint et l'intro. Étalon : session Biology O Level
  n°1 (`ep-cm-gce-ol-biology-p1-1-2026-s1` et `-p2-1-2026-s1`) : Paper 2 de 5 questions de 20 points en trois parties (3 en Section A, 2 en Section B), schémas anatomiques
  remplacés par des figures de **données** au Paper 1 et par une **description du dessin attendu** dans le corrigé au Paper 2, thèmes pris dans la forme la plus fréquente
  des `Tag` existants. **Aucune fuite entre les deux papers** : un énoncé ou une option du Paper 1 ne donne jamais la réponse d'une question du Paper 2. **Matière de pur rappel de cours : changer le FAIT demandé, jamais seulement les mots** ; le contrôle refuse un énoncé quasi identique à un énoncé réel (étalon Physics O Level n°1 : `ep-cm-gce-ol-physics-p1-1-2026-s1` et `-p2-1-2026-s1`, Section II en une seule branche par question).
- **Chemistry O Level** (étalon : session n°1, `ep-cm-gce-ol-chemistry-p1-1-2026-s1` et `-p2-1-2026-s1`) : Paper 1 de 50 QCM dont un bloc de 3 « completion multiple » et un de 2 « assertion-raison »,
  3 figures de données ; Paper 2 « answer ALL » de 4 exercices de 10 points (Section A), 2 de 20 (Section B : un titrage avec courbe de pH, une analyse qualitative en tableau) et 2 de 20
  (Section C : vitesse de réaction avec deux courbes, organique avec calcul) = 120 points. **Relire les deux papers l'un contre l'autre, rappel et corrigé compris** : une fuite vient aussi bien
  d'un rappel (« à 450 °C ») que d'un énoncé.
- **Essais** (History, Religious Studies, Philosophy) : jamais un sujet réel reformulé, faits exacts, corrigé = plan et essai modèle, grille par
  contenu, exactitude, structure, exemples, langue.
- **Langues** : textes **originaux** (jamais un extrait publié), une seule réponse défendable par QCM, composition notée sur contenu, organisation,
  expression, orthographe.
- **Pratique** (Computer Science, ICT P3) : énoncé **complet en soi** (les fichiers du jour ne sont pas fournis), corrigé = algorithme, code, exemple
  d'exécution, code exécuté ou traduit en Python, sinon `incertitudes`.
- **Quantitatif** (Economics P3, Mechanics, Statistics) : tableaux Markdown, unités SI, résultat de `(a)` rappelé avant de servir à `(b)`.
- **Figures** : Maths et Physics complètes (graphes, géométrie, circuits), Biology/Geology sans schémas anatomiques ou de coupe, Geography/History sans
  cartes, langues et Religious Studies sans figure.

### Session de papers

Les papers d'une matière et d'un niveau forment une **session** (« Original Paper No. 1 » pour le Paper 1 ET le Paper 2) : concevoir les blueprints ensemble, avec dans
chacun un bloc `session` (`papier_jumeau`, `numero_session`, `themes_communs_aux_deux_papers`, `themes_propres_au_paper_N`), sans donnée, contexte ni figure
partagés ; générer un paper après l'autre (chacun avec ses contrôles, `--jumeau` compare au paper déjà fait) ; valider et publier les papers de la session ensemble.

### Contrôles obligatoires (dans cet ordre, depuis `D:\edukora`)

1. Générateur du paper (`scripts/gce/inedites/generer_*.py`), qui écrit blueprint et épreuve dans `backend/ingest/_inedit/cm/`.
2. `venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_<paper>.py` : recalcul indépendant (QCM : la clé est la seule option égale ; paper rédigé : chaque ligne
   `**Answer: ...**` et les valeurs intermédiaires citées) (0 écart).
3. `venv\Scripts\python.exe scripts\gce\inedites\controle_inedite_gce.py <ep.json> <bp.json> [--matiere maths] [--type qcm|redige] [--sections "SECTION A:10:45,SECTION B:4:60"]
   [--jumeau <autre paper>]` : contrat, barème, grilles, style, `$`, rappels verbatim, originalité contre le corpus réel et le paper jumeau (0 erreur ; relire chaque avertissement).
4. `venv\Scripts\python.exe scripts\gce\inedites\outils_figures\verifier_figures.py <ep.json>` puis `rendre_figures.py` et **regarder** chaque figure.
5. Rendu KaTeX par le vrai moteur (dump des champs, `AUDIT_RENDU_DUMP=... npx vitest run src/lib/audit-rendu.test.ts`) puis **ingestion à
   blanc** dans une transaction annulée (le blueprint passé `VALIDE` seulement à l'intérieur de la transaction : la validation humaine, elle, reste
   à faire dans l'admin) et PDF du sujet regardé page par page.

### Défauts de plateforme connus (ne pas les contourner dans le JSON)

`score_originalite` non discriminant pour un QCM court (13 sur l'étalon sans aucun
doublon réel) ; « Exercice 1 » non traduit dans le PDF anglais ; ni `numero_paper`, ni `code_matiere`, ni `regles_choix` dans le modèle inédit . Les
signaler dans le compte rendu, ne pas les « réparer » en dupliquant du texte. (Les options de QCM absentes du PDF, relevées à l'étalon, sont
corrigées dans `compile_from_exercices` ; ne jamais les recopier dans `enonce_markdown`. Les points de chaque question rédigée y sont aussi imprimés « [3 marks] » : ne jamais les
écrire dans l'énoncé.)

