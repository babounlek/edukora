# Complément aux consignes - GCE ORDINARY LEVEL, ECONOMICS (code 0525)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis ce fichier. **Ce fichier prime** pour tout ce qui touche à l'Economics O Level :
codes, noms de dossier, papers, règles de choix, corrigés, thèmes. Pour le niveau (Form 5, pas Advanced), `CONSIGNES.md` fait foi.

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Economics"`, `code_matiere` `"0525"`
  (page de garde : « ORDINARY LEVEL », « 0525 »). Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-ol-economics-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les deux papers

- **Paper 1** : 50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules,
  `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Un QCM numérique (élasticité, coûts, revenu national, taux de change, pourcentage)
  se justifie par le calcul recalculé avec Python. Un tableau de données imprimé se recopie en tableau Markdown ; un graphique (offre/demande, coûts) se recadre en PNG.
- **Paper 2** : 2h30, dissertations. Page de garde : « Answer ANY FIVE questions. ONLY THE FIRST FIVE QUESTIONS ANSWERED WILL BE MARKED. All questions carry equal marks »
  (lis la page de garde de CHAQUE année : le nombre et les sections peuvent changer). UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé, sous-questions
  (a), (b), (c)... = `questions`. Si le sujet n'a pas de sections : `groupes` `["PAPER 2"]` dans chaque fichier et
  `regles_choix` `[{"type":"parmi","portee":"PAPER 2","repondre":5,"sur":<N questions imprimées>}]`, identique dans TOUS les fichiers. S'il y a des sections avec des nombres
  imposés, écris une règle `parmi` par section (le minimum imposé) avec `groupes` = le repère de section, et recopie la consigne complète dans `introduction_markdown` et `incertitudes`.
  Points : « equal marks » ; `points` de l'exercice = le total imprimé s'il y en a un, sinon `""` ; points des sous-questions entre crochets.
- `introduction_markdown` : la consigne de la page de garde, identique dans tous les fichiers du dossier. `duree_epreuve` : `"1h30"` ou `"2h30"` selon la page de garde.

## Corrigés

- Niveau Form 5, anglais clair : définitions précises du programme O Level, exemples concrets (Cameroun, marché local, cacao, café, banane, pétrole, FCFA, CEMAC), structure
  introduction / développement / conclusion pour les questions rédigées, une réponse modèle comme en rédigerait un candidat qui obtient tous les points. Respecte « define »,
  « explain », « state », « distinguish », « give reasons ».
- **N'invente aucune statistique réelle, date ou institution** : exemples hypothétiques (« suppose that... ») ou ordres de grandeur qualitatifs ; formulation prudente en cas de doute et
  trace dans `incertitudes`.
- QCM : explique pourquoi la bonne option est exacte et le piège des autres ; termine par « **Answer: C.** ». Un QCM à clé imprimée ou options douteuses : convertis en `ouverte`
  (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`), jamais une lettre au hasard.
- Les calculs sont recalculés avec Python ; formule, remplacement, résultat avec monnaie ou unités.
- Un diagramme à dessiner par le candidat se décrit dans le corrigé (axes, courbes, équilibre, déplacement). Produis un PNG (matplotlib, `D:\edukora\venv\Scripts\python.exe`, fond blanc,
  légendé) seulement quand il rend la réponse réellement compréhensible ; déclare-le dans `figures` (`type` : 30 caractères MAXIMUM) avec son placeholder `![fig-1](...)`.
  Un graphique imprimé dans le sujet : suis la section Figures de `CONSIGNES.md` (skill `reproduire-figure-sans-filigrane`, jamais `pdftoppm`).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites. **Réutilise le nom d'un thème de l'Economics A Level quand c'est la même notion** (la matière est partagée entre les deux niveaux) :
Grep des valeurs `"themes"` dans `D:\edukora\backend\ingest\cm\gce-al-economics-*\*.json` ET `gce-ol-economics-*\*.json`, et dans `_gce_staging\gce-ol-economics-*\*.json` (plusieurs agents
travaillent en parallèle : relis les dossiers des autres avant de créer un nom, n'invente pas trois noms pour la même notion). Pour une notion propre à l'O Level, un nom explicite de 2 à 3 mots.
Exemples déjà en usage : `demand and supply`, `price elasticity`, `costs and revenue`, `market structures`, `national income accounting`, `public finance`, `money and banking`,
`international trade`, `exchange rates`, `balance of payments`, `economic development`, `population and labour`. `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français et les autres matières :
évite les mots identiques en français (« inflation », « population », « agriculture », « production », « taxation » seuls...) et les noms pris par une autre matière (« industrialisation »,
« unemployment », « energy resources », « industrial location » le sont).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM (un champ plus long fait échouer tout l'exercice à l'ingestion).

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper <1|2> --code 0525 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base
ni à Docker ni à git.
