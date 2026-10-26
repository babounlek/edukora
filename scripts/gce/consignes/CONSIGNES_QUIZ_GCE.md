# Générer des items de quiz GCE (CompetenceItem, en anglais) - consignes de lot

Tu produis des questions de quiz d'auto-évaluation pour le GCE Ordinary Level du Cameroun (Maths, Physique, Chimie), à partir
d'une tranche de 5 « compétences » (thèmes). Le contrat complet des items est celui du skill **concepteur-quiz-competence** :
charge-le avec l'outil Skill (`anthropic-skills:concepteur-quiz-competence`) et suis-le, SAUF sur les points ci-dessous, qui PRIMENT.

## Adaptations GCE (priment sur le skill)

1. **Tout est en anglais** (énoncés, options, corrigés). Le skill parle de BEPC/BAC et de titres français : ignore ces références.
2. **Titres du corrigé en anglais** : `corrige_markdown` commence par `### Method reminder` (2 à 4 lignes : le principe ou la technique
   AVANT son application) puis `### Solution`. Jamais « Rappel de méthode » / « Corrigé ».
3. **Requête** : recopie `matiere` ("Mathematics", "Physics", "Chemistry") et `cursus` (`[{"examen":"gce_ol","serie":""}]`) TELS QUELS
   depuis la requête ; `theme` = la valeur de `competence`, exactement ; **n'écris pas `savoir_officiel`** (omets-le ou mets `null`).
4. **Niveau et style GCE O/L (Form 5)** : questions formulées comme au Cameroon GCE Board (« Calculate », « State », « Explain », « Find »),
   unités SI, `g = 10 m s^-2`, calculatrice permise, contextes camerounais plausibles (FCFA, marché, Douala, Bamenda...). Niveau
   accessible à un élève de Form 5, jamais du niveau Advanced.
5. **Matériel de référence** : des questions réelles des sujets GCE. Elles montrent le niveau et le style ; **ne les copie jamais**,
   même partiellement (le validateur refuse 9 mots consécutifs identiques à l'énoncé d'une référence). Change le contexte, les valeurs et
   la formulation. Une référence qui dépend d'une figure absente de ce que tu lis : ignore la figure et invente un énoncé autonome.
6. **Figures : le moins possible.** Un item n'a une figure que si la compétence l'exige vraiment (lecture de graphe, circuit, rayons).
   Préfère une formulation purement textuelle (valeurs, tableau Markdown, description). Si tu produis une figure : Python/matplotlib avec
   `D:\edukora\venv\Scripts\python.exe`, valeurs recalculées, axes gradués et légendés, fond blanc, ~1000 px de large, PNG nommé
   `<external_id>_fig_<n>.png` dans le dossier du lot, placeholder `![fig-1](<fichier>)` + entrée `figures` (`id`, `fichier`, `type`,
   `legende`, `origine_figure`). Une figure d'énoncé ET une figure de corrigé = deux PNG distincts.
7. **QCM** : plancher selon la matière, sur les 6 items d'un fichier : **au moins 5 QCM** pour Mathematics, Additional/Further Mathematics, Pure Mathematics with Mechanics/Statistics, Physics, Chemistry, Biology, Human Biology, Geology, Computer Science, ICT, Food and Nutrition, English Language, French, Special Bilingual Education French, Accounting, Logic ; **au moins 3** pour History, Geography, Economics, Commerce, Citizenship Education ; **au moins 2** pour Philosophy, Religious Studies, Literature in English. Et **toujours au moins 2 QCM** dans le fichier (1 pour les matières à 2/6). Le validateur refuse un fichier sous ce plancher. 4 options minimum, lettres `a` à `d`, `reponse_correcte` = la lettre. Chaque
   mauvaise option est une erreur réellement plausible pour cette compétence (oubli d'unité, confusion de formule, erreur de signe...),
   jamais une valeur absurde. Mets les options en ordre naturel (croissant pour des nombres). La bonne lettre doit varier d'un item à l'autre.
8. **`source_exercises`** : les `exercise_id` du matériel de référence qui t'ont réellement inspiré (au moins un, jamais cité dans le texte).
9. **`external_id`** : `cqc-<slug>-<difficulte>-<index>`, `slug` = le nom de la compétence en minuscules, accents supprimés, tout caractère non
   alphanumérique remplacé par un tiret (ex. « Forces and Newton's laws » -> `forces-and-newton-s-laws`), `difficulte` en minuscules
   (`faible`, `moyenne`, `elevee`), `index` = 0, 1, 2... dans l'ordre d'écriture du fichier. Chaque `difficulte_estimee` est
   `FAIBLE`, `MOYENNE` ou `ELEVEE` et respecte la `repartition_difficulte` de la cible.

## Ce que tu écris

Dans `D:\edukora\backend\ingest\_quiz\cm\<DOSSIER>\` (DOSSIER te sera donné ; crée-le) : **un fichier par compétence**,
`<slug>.json` (slug comme ci-dessus), qui contient un TABLEAU JSON de `cible.nombre_items` items. Les PNG éventuels vont dans le même dossier.
N'écris JAMAIS ailleurs, ne supprime JAMAIS un fichier qui n'est pas le tien (d'autres agents travaillent en parallèle, chacun dans son dossier).

Un item : `external_id`, `theme`, `matiere`, `cursus`, `enonce_markdown`, `corrige_markdown`, `difficulte_estimee`, `type_reponse`
("QCM" | "OUVERTE"), `choix` (`[{"lettre":"a","texte":"..."}, ...]` ou `[]`), `reponse_correcte` (lettre ou `""`), `source_exercises`, et
`figures` (`[]` si aucune).

## Rigueur (non négociable)

- **Génère les fichiers avec un script Python** (`D:\edukora\venv\Scripts\python.exe`, script préfixé par ton DOSSIER, dans le scratchpad,
  jamais dans le dépôt) dans lequel CHAQUE valeur numérique d'un corrigé est RECALCULÉE (`assert` sur le résultat) avant d'être écrite : un
  script qui échoue sur une divergence vaut mieux qu'une relecture. Pour la chimie, équations équilibrées atome par atome (vérifie par code),
  masses atomiques standard de O/L (H = 1, C = 12, N = 14, O = 16, Na = 23, Mg = 24, Al = 27, S = 32, Cl = 35.5, K = 39, Ca = 40, Cu = 64,
  Zn = 65). Pour la physique, formule, remplacement avec unités, résultat.
- **Un énoncé autonome** : aucune référence à une question voisine, à une « figure ci-dessus », à une partie précédente. Toutes les données
  nécessaires sont dans l'énoncé.
- **Backslash LaTeX DOUBLÉ dans le JSON** (`\\frac`, `\\times`, `\\ne`...) : si tu écris le JSON avec `json.dump`, écris les chaînes Python
  en raw strings (`r"$\frac{1}{2}$"`) ; le validateur refuse tout caractère de contrôle. Le `$` hors formule s'écrit `\$`.
- **Variété** : pour une même difficulté, des scénarios, valeurs et angles différents.
- **Fidélité au programme O/L** : un fait de chimie ou de physique doit être exact et au programme GCE O/L ; en cas de doute sur une convention,
  choisis la formulation la moins ambiguë ou écarte l'item.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_quiz_gce.py <fichier_de_ta_tranche.json> <ton dossier>
```

Il doit afficher `OK` (les « warn » sont à relire : français, renvois, répartition). Corrige jusqu'à `OK`.
Puis fais une SECONDE PASSE : relis chaque item comme un élève (l'énoncé suffit-il ? une seule bonne option ? un distracteur est-il en réalité
correct ?) et résous chaque QCM une deuxième fois sans regarder ton corrigé ; corrige tout écart et relance le validateur.

Ne lance JAMAIS l'ingestion, ne touche pas à la base de données ni à un autre fichier du dépôt.

## Ce que tu rends

Un rapport court : dossier, nombre de fichiers et d'items, nombre de QCM par fichier, sortie du validateur, nombre de corrections de la
seconde passe, figures produites, et toute compétence que tu n'as pas pu couvrir honnêtement (avec la raison).
