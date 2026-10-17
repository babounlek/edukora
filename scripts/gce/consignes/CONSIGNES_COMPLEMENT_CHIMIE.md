# Complément aux consignes - Chemistry (code 0515) et leçons du lot Maths

Lis CONSIGNES.md d'abord ; ce complément la précise, il ne la remplace pas.

## Chimie : identité du sujet

- `matiere` "Chemistry", `code_matiere` "0515" (vérifie le code imprimé sur la page de garde), `examen` "gce_ol".
- DOSSIER = `gce-ol-chemistry-<annee>-p<paper>-officiel-cameroun` (ATTENTION : "chemistry", pas "chimie").
- Paper 1 : QCM (50 questions attendues, à confirmer sur le sujet, 1h30). Paper 2 : sections A, B, C avec des choix
  (« answer 4 questions out of 5 », « 2 out of 3 », « both »...) : LIS l'en-tête avec soin.

## Paper 2 : numérotation et règles de choix

- Garde les numéros imprimés du sujet quand ils sont uniques d'une section à l'autre (ex. A = 1 à 5, B = 6 à 8, C = 9 et 10 :
  `numero_exercice` "1".."10"). Si les sections repartent de 1, préfixe : "B1", "C1".
- `groupes` = ["SECTION A"], ["SECTION B"] ou ["SECTION C"] (texte exact, en majuscules).
- `regles_choix` : écris-les dans TOUS les fichiers du dossier, identiques, avec `portee` égale à un repère de `groupes`.
  Exemple : `[{"type":"parmi","portee":"SECTION A","repondre":4,"sur":5},{"type":"parmi","portee":"SECTION B","repondre":2,"sur":3},{"type":"parmi","portee":"SECTION C","repondre":2,"sur":2}]`.
  Si l'en-tête et le titre d'une section se contredisent, retiens l'en-tête et dis-le dans `incertitudes`.
- Les « données utiles » (masses atomiques relatives, constantes) de la page de garde vont dans `introduction_markdown`.
- Points : recopie ceux du sujet bloc par bloc (`points` d'une sous-question) et « Total = N marks » dans `points` de l'exercice,
  même quand la somme est fausse (note-le dans `incertitudes`).

## Écrire la chimie

- Formules et équations en LaTeX avec `\mathrm{...}` (ex. `$2\mathrm{Na} + 2\mathrm{H_2O} \rightarrow 2\mathrm{NaOH} + \mathrm{H_2}$`).
  N'utilise PAS `\ce{...}` (mhchem n'est pas chargé). Flèche réversible : `\rightleftharpoons`.
- Une équation de ton corrigé doit être ÉQUILIBRÉE : vérifie atome par atome. Tout calcul de quantité de matière, de masse ou de
  volume est vérifié avec Python (masses atomiques du sujet, pas celles de ta mémoire).
- Formules développées ou schémas d'appareillage qu'on ne peut pas écrire en texte : produis une figure (voir CONSIGNES) ;
  une structure que l'élève doit dessiner est décrite dans le corrigé (liaisons, groupes fonctionnels).
- Tests de reconnaissance (ions, gaz) : donne le réactif, l'observation attendue et la conclusion.
- Thèmes chimie (anglais, minuscules, courts) : atomic structure, periodic table, chemical bonding, Group I elements,
  halogens, acids bases and salts, mole concept, stoichiometry, gas laws, electrolysis, redox reactions, rates of reaction,
  energy changes, metals and extraction, non-metals and their compounds, organic chemistry, alkanes and alkenes, alcohols and
  carboxylic acids, polymers, water, air and pollution, qualitative analysis, apparatus and experiments.
  Tag.name est UNIQUE et PARTAGÉ avec le contenu français : n'utilise jamais un mot identique à un thème français (ex. pas
  « matrices »). Si un nom te paraît pouvoir exister en français tel quel, reformule-le en anglais plus explicite.

## Leçons du lot Maths (à appliquer)

1. **Option fautive** : si le sujet imprimé est défectueux (la bonne valeur ne figure dans aucune option, les options sont
   identiques ou coupées), NE choisis PAS une lettre au hasard. Passe cette question en `type_reponse` "ouverte",
   `choix` [], `reponse_correcte` "", recopie les options dans l'énoncé (« *Options as printed:* A) ... B) ... »), donne la valeur
   exacte dans le corrigé et signale la coquille. Mentionne-la dans `incertitudes`.
2. **Figure illisible ou ambiguë** : une lecture retenue + l'autre notée dans le corrigé ET dans `incertitudes`.
3. **Scratchpad partagé** : plusieurs agents travaillent en parallèle. Préfixe TOUS tes fichiers temporaires (scripts, rendus de
   pages) par ton DOSSIER, et n'écris jamais dans un dossier de travail qui n'est pas le tien.
4. **Rends l'énoncé complet** : tableaux de données, valeurs numériques, légendes des schémas. Un tableau se transcrit en Markdown.
5. Le validateur attend `--code 0515`.
