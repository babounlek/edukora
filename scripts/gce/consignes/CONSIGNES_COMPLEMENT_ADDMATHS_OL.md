# Complément aux consignes - GCE ORDINARY LEVEL, ADDITIONAL MATHEMATICS (code 0575)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures, corrigés de maths), puis ce fichier. **Ce fichier prime** pour tout ce qui touche à l'Additional Mathematics :
codes, noms de dossier, papers, règles de choix, thèmes. Niveau O Level (Form 5), un cran au-dessus des Maths O Level.

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Additional Mathematics"`, `code_matiere` `"0575"`
  (page de garde : « ORDINARY LEVEL », « 0575 », « Additional Mathematics »). Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-ol-additional-maths-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`. Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les deux papers

- **Paper 1** : 50 QCM, 1h30, calculatrice non programmable permise. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d`
  minuscules, `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Chaque QCM se justifie par le calcul recalculé avec Python (`sympy` si disponible, sinon `fractions`).
  Si les options sont des courbes ou des schémas, mets l'image dans l'énoncé et la lettre comme texte de chaque choix.
- **Paper 2** : 2h30. Page de garde (à relire CHAQUE année) : « Answer ALL questions in SECTION A and ANY TWO questions from EITHER SECTION B or SECTION C ; in B and C all questions carry equal marks »,
  avec la précision « a combination of Section A and Section B OR Section A and Section C, but NOT a combination of all three ». UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé, sous-questions
  (a), (b)... = `questions`, `groupes` = le repère de section (`["SECTION A"]`, `["SECTION B"]`, `["SECTION C"]`), identique dans tous les fichiers d'une section.
  `regles_choix`, identiques dans TOUS les fichiers du dossier : UNE règle
  `{"type":"section_unique","portee":"SECTION B / SECTION C","repondre":2,"groupes":["SECTION B","SECTION C"]}` (la section A n'a pas de règle : tout est obligatoire). Elle dit « 2 questions, toutes dans
  UNE seule de B ou C » : un `parmi` par section ferait peser au barème les deux questions de la section laissée de côté. Recopie aussi la consigne complète dans `introduction_markdown`. Points : ceux imprimés (total par question) dans `points` de l'exercice, ceux des sous-questions entre crochets.
  Le sujet donne souvent « take g as 10 m s^-2 » : recopie-le dans l'introduction.
- `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"` ou `"2h30"`.

## Corrigés

- Raisonnement complet, étape par étape, avec la conclusion nette ; chaque valeur recalculée avec Python (`D:\edukora\venv\Scripts\python.exe`) ; forme exacte (fractions, racines, `\pi`, `e`, `\ln`) avant l'approximation demandée.
  Respecte « show all steps », « give your answer correct to 3 s.f. ». Programme : algèbre (fonctions, inéquations, indices et surds, logarithmes), trigonométrie, géométrie analytique, suites, dérivation et intégration élémentaires,
  vecteurs et matrices, probabilités et statistiques, cinématique/dynamique de base (Section C selon les années). Termine un QCM par « **Answer: C.** ».
- Équation numérotée avec `\tag` : formule d'affichage sur TROIS lignes (`$$`, formule, `$$`), jamais sur une seule ligne. Le `$` d'un prix ou d'une référence de tableur s'écrit `\$` hors formule.
- Une courbe, un diagramme de Venn, un schéma de forces ou un dessin imprimé dans le sujet : suis la section Figures de `CONSIGNES.md` (skill `reproduire-figure-sans-filigrane`, jamais `pdftoppm`) ;
  une figure à tracer par le candidat se décrit dans le corrigé (points clés, tableau de valeurs). `figures[].type` : 30 caractères MAXIMUM.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites. `Tag.name` est UNIQUE et PARTAGÉ avec les Maths O Level (`gce-ol-maths-*`), la Pure Mathematics A Level (`gce-al-pm-*`), la Further Mathematics et le contenu français.
**Choisis des noms propres à l'Additional Mathematics** (un angle plus avancé qu'en Maths O Level : par exemple `quadratic functions and discriminant`, `indices and surds`, `logarithms and exponential equations`,
`binomial expansion`, `arithmetic and geometric progressions`, `differentiation techniques`, `integration and area`, `trigonometric identities and equations`, `coordinate geometry of circles`, `vector geometry (additional maths)`,
`matrices and inverses (additional maths)`, `permutations and combinations`, `kinematics and motion`), et évite les noms courts partagés avec les Maths O Level ou les mots identiques en français
(`matrices`, `vectors`, `sets`, `graphs`, `functions`, `inequalities`, `probability`, `statistics`, `trigonometry`, `polynomials`, `logarithms` seuls). Avant de créer un nom, fais un `Grep` des valeurs `"themes"` dans
`D:\edukora\backend\ingest\cm\gce-ol-maths-*\*.json`, `cm\gce-al-pm-*\*.json`, `cm\gce-al-further-maths-*\*.json` (pour NE PAS les réutiliser) et dans `cm\gce-ol-additional-maths-*` et
`_gce_staging\gce-ol-additional-maths-*` (pour RÉUTILISER les noms des autres papers d'Additional Maths : plusieurs agents travaillent en parallèle, relis les dossiers des autres avant de créer un nom,
n'invente pas trois noms pour la même notion).

## Champs courts et contrôle final

`numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper <1|2> --code 0575 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, résoudre chaque question une deuxième fois, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base
ni à Docker ni à git.
