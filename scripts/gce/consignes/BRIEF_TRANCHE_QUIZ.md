# Brief d'agent : une tranche de quiz GCE (5 compétences, 30 items)

Paramètres donnés par l'appelant : `ID` (ex. `ol-history-03`), `NIVEAU` (O Level ou A Level), `MATIERE` (libellé exact), `INDEX_DEPART` (0 sauf mention).
Dérivés : fichier de requêtes `D:\edukora\backend\ingest\_quiz\_batch_cm_gce_<ID avec « - » entre niveau, matière et numéro, tel quel>.json`
= `_batch_cm_gce_` + `<niveau>_<matiere>_<NN>` (ex. `ol-history-03` -> `_batch_cm_gce_ol_history_03.json` ; `al-pm-statistics-02` ->
`_batch_cm_gce_al_pm-statistics_02.json` : niveau, puis la matière avec ses tirets, puis le numéro, séparés par `_`).
Dossier de sortie : `D:\edukora\backend\ingest\_quiz\cm\gce-<ID>\`.
En cas de doute sur le nom du fichier de requêtes, liste `D:\edukora\backend\ingest\_quiz\` (`_batch_cm_gce_*`) : ne devine pas.

## À faire

1. Lis `D:\edukora\scripts\gce\consignes\CONSIGNES_QUIZ_GCE.md`, puis `CONSIGNES_QUIZ_GCE_AUTRES.md` (il PRIME). Charge le skill
   `anthropic-skills:concepteur-quiz-competence` (outil Skill) et suis-le sauf là où les consignes GCE le contredisent.
   Matières Further/Pure Mathematics au niveau A Level : lis aussi `CONSIGNES_QUIZ_GCE_AL.md` (constantes, rigueur par script).
2. Lis ton fichier de requêtes (5 requêtes : `competence`, `matiere`, `cursus`, `cible`, `materiel_reference`). Recopie `matiere`, `cursus` et
   `competence` (-> `theme`) TELS QUELS dans chaque item.
3. Écris UN fichier `<slug>.json` par compétence dans le dossier de sortie (tableau de 6 items : 2 FAIBLE, 3 MOYENNE, 1 ELEVEE), par un script
   Python du scratchpad (`D:\edukora\venv\Scripts\python.exe`), calculs recalculés par `assert`.
   `external_id` = `cqc-<slug>-<difficulte>-<index>` avec `index` démarrant à `INDEX_DEPART` (0 par défaut ; 10 quand l'appelant le précise : la même
   compétence existe dans une autre matière et les `external_id` ne doivent pas se heurter).
   Lettre de la bonne réponse : elle doit VARIER (jamais plus de 2 fois la même sur les 4 QCM d'un fichier, pas de « b » à répétition) ; place la bonne
   réponse à des positions différentes, même si l'ordre « naturel » des options en souffre un peu (mélange-les par script avec une graine fixe).
4. Contrôle : `set PYTHONIOENCODING=utf-8` puis
   `D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_quiz_gce.py <fichier de requêtes> <dossier de sortie>` doit afficher `OK`.
5. Seconde passe OBLIGATOIRE, y compris pour une matière « factuelle » : imprime par script, pour chaque QCM, le TEXTE de l'option désignée par
   `reponse_correcte` et vérifie qu'elle est bien la bonne (des agents ont trouvé des clés qui pointaient vers un distracteur). Relis chaque item comme un élève (l'énoncé suffit-il ? une seule bonne option ? un distracteur est-il en réalité correct ?),
   résous chaque QCM une seconde fois sans regarder ton corrigé ; corrige tout écart et relance le validateur. Un fait dont tu n'es pas sûr : écarte l'item.

## Interdits

Ne lance JAMAIS l'ingestion, ne touche pas à la base ni à un fichier du dépôt autre que ton dossier de sortie. Aucun script dans le dépôt.

## Rapport (8 lignes max)

Dossier, fichiers et items, QCM par fichier, sortie du validateur, corrections de seconde passe, compétences non couvertes honnêtement.
