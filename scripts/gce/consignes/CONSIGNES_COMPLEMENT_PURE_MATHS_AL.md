# Complément aux consignes - GCE ADVANCED LEVEL, PURE MATHEMATICS WITH MECHANICS (0765) et WITH STATISTICS (0770)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce
fichier. **Ce fichier prime** pour tout ce qui touche à ces deux matières : libellés, codes, noms de dossier, thèmes. Les compléments
Chimie / Physique / Biologie ne te concernent pas ; `CONSIGNES_COMPLEMENT_MATHS_AL.md` (Further Mathematics 0775) sert d'exemple de
forme pour les démonstrations et les équations numérotées, mais **ne mélange jamais** les thèmes et les codes.

## Identité du sujet : DEUX matières, jamais « Pure Mathematics » seul

| Sujet imprimé sur la page de garde | `matiere` (libellé exact) | `code_matiere` | Mot du dossier | PDF source |
|---|---|---|---|---|
| « Pure Maths With Mechanics » | `"Pure Mathematics with Mechanics"` | `"0765"` | `pm-mechanics` | `GCE_AL_MATHS_MECHANICS_<ANNEE>_P<n>.pdf` |
| « Pure Maths With Statistics » | `"Pure Mathematics with Statistics"` | `"0770"` | `pm-statistics` | `GCE_AL_MATHS_STATISTICS_<ANNEE>_P<n>.pdf` |

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`. **Le libellé `"Pure Mathematics"` (ou `"Pure Maths"`) seul est
  REFUSÉ** par l'ingestion et par le validateur : ce n'est pas une matière du Board. Lis la page de garde (« ADVANCED LEVEL », « 0765 » ou
  « 0770 ») : un code qui ne correspond pas au nom du fichier, un sujet « Ordinary Level » ou une autre matière (Further Mathematics 0775,
  Mathematics O Level 0570) = ne transcris rien et signale-le (les téléchargements ont déjà contenu des sujets mal rangés).
- DOSSIER = `gce-al-<mot du dossier>-<annee>-p<paper>-officiel-cameroun` (ex. `gce-al-pm-mechanics-2023-p1-officiel-cameroun`).
  `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\` (2019 à 2026, trois papers par année). Ce sont
  des **scans sans couche texte** (filigrane gcerevision.com à ignorer) : lis chaque page en image avec Read (paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les papers (vérifiés sur les sujets 2023 ; relis TOUJOURS la page de garde de l'année traitée)

- **Paper 1** : QCM, 1h30, « Answer All questions », questions à 4 réponses A-D (en principe 50 : compte-les et passe `--questions N` au
  validateur ; un sujet incomplet se signale dans `introduction_markdown` et `incertitudes`), formulaires et calculatrice autorisés. Il
  s'ouvre sur « SECTION A: PURE MATHEMATICS », puis vient la section propre à la matière (Mechanics ou Statistics) : relis la page de garde.
  UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"N"`, `type_reponse` `"qcm"`, `choix` lettres minuscules a-d, `reponse_correcte` une lettre,
  `groupes` `[]`, `points` `""`, `duree_epreuve` `"1h30"`. Recopie dans `introduction_markdown` la consigne de la page de garde. Le repère de
  section (« SECTION A: PURE MATHEMATICS », « SECTION B: ... ») se dit dans l'énoncé de la première question de la section si tu en as besoin,
  mais ne crée aucune règle de choix : toutes les questions sont obligatoires.
- **Paper 2** : 3 h, « Full marks may be obtained for answers to ALL questions ». UN fichier PAR QUESTION (`numero_exercice` `"1"`, `"2"`...),
  les parties (i), (ii), (a), (b) = `questions` de l'exercice (numérote-les `i`, `ii`... ou `a`, `b`... comme imprimé, `"i.a"` si les deux
  niveaux existent). `regles_choix` `[]`, `groupes` `[]`. Les points imprimés par partie (« (5, 3 marks) » = 5 puis 3) vont dans `points` de la
  sous-question concernée ; ne corrige JAMAIS un total qui ne somme pas, note-le dans `incertitudes`. Le Paper 2 des deux matières porte surtout
  sur la partie PURE MATHEMATICS (fonctions, polynômes, logarithmes, nombres complexes, récurrence, dérivation, intégration, trigonométrie,
  équations différentielles, relations d'équivalence) : même niveau de rigueur, mêmes thèmes.
- **Paper 3** : lis la page de garde (durée, nombre de questions, consigne de choix éventuelle, partie Mechanics ou Statistics). Même forme
  que le Paper 2 ; si un choix est imprimé (« Answer any ... »), `regles_choix` comme décrit dans `CONSIGNES_COMPLEMENT_AL.md`, sinon `[]`.
- `duree_epreuve` : `"1h30"`, `"3h"`, etc., selon la page de garde ; `introduction_markdown` : la consigne imprimée, identique dans tous les
  fichiers du dossier.

## Corrigés

Niveau Advanced Level : démonstrations complètes (récurrence, preuve par l'absurde, justification de chaque étape), toute valeur numérique
recalculée avec Python (`D:\edukora\venv\Scripts\python.exe`, `sympy` s'il est installé, sinon deux calculs indépendants), forme exacte
(fractions, racines, `\pi`) avant l'approximation demandée. QCM : la réponse se justifie par le calcul ; si la clé imprimée est fausse ou si la
bonne valeur n'est dans aucune option, passe la question en `ouverte` (voir `CONSIGNES.md`, `convertir_en_ouverte.js`) et dis-le dans
`incertitudes`. Tracé demandé (graphe linéarisé, courbe, diagramme d'Argand) : décris les points clés dans le corrigé et joins une figure SVG ou PNG exacte
si le sujet imprime déjà une figure (recadrée, vérifiée visuellement).
- **Mechanics** : toute mise en équation part d'un schéma décrit (forces, axes, sens positif choisi) ; `g = 9.8 m s^-2` sauf indication du sujet,
  valeur retenue écrite dans le corrigé et notée dans `incertitudes` ; unités SI à chaque ligne.
- **Statistics** : loi et paramètres nommés explicitement, formules rappelées, tables remplacées par un calcul exact quand c'est possible
  (sinon valeur de table citée) ; arrondi demandé seulement à la dernière ligne.
- **Équations numérotées** : une formule d'affichage avec `\tag{1}` s'écrit sur TROIS lignes (`$$`, la formule, `$$`), jamais en une seule ligne.
- Formules : LaTeX entre `$...$`, antislash doublé dans le JSON (`\\frac`, `\\int`, `\\sum`, `\\begin{pmatrix}`).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites. `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français, les autres matières, les Maths O Level
et **Further Mathematics** : n'emploie pas un nom déjà pris (`matrices`, `vectors`, `sets`, `graphs`, `functions and mappings`, `complex
numbers`, `mathematical induction`, `polar coordinates`, `partial fractions`... existent déjà) ni un mot qui existe tel quel en français. Le
Paper 2 couvre les mêmes notions que Further Maths : **réutilise** le thème existant quand la notion est la même (cohérence entre matières,
c'est le but du Tag partagé) ; n'invente un nom que pour une notion propre à ces matières, en le faisant précéder du domaine si le mot est
générique (ex. `projectile motion mechanics`, `binomial distribution statistics`).
Avant de créer un nom, fais un `Grep` des valeurs `"themes"` déjà utilisées dans `D:\edukora\backend\ingest\cm\gce-al-*\*.json` et
`_gce_staging\gce-al-*\*.json`. Exemples probables : `kinematics and motion graphs`, `newton laws and connected particles`,
`work energy and power mechanics`, `momentum and impulse`, `equilibrium of rigid bodies`, `friction`, `projectile motion mechanics`,
`circular motion mechanics`, `simple harmonic motion`, `permutations and combinations`, `probability rules`, `conditional probability`,
`binomial distribution statistics`, `poisson distribution statistics`, `normal distribution`, `sampling and estimation`,
`correlation and regression`, `statistical hypothesis tests`, `data representation statistics`. **Contrôle OBLIGATOIRE avant l'ingestion** (fait par le
chef de lot, pas par toi) : `find_tag_variant` sur la liste des thèmes du lot ; une fusion silencieuse avec un tag français est la panne
la plus fréquente du GCE (voir `scripts/gce/README.md` §4).

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code <0765|0770> [--questions 50]
```

Le validateur vérifie aussi que `matiere`, `examen` et `code_matiere` forment une matière officielle : il refuse `Pure Mathematics` seul et un
code qui ne correspond pas au libellé. Il doit afficher `OK`, puis la SECONDE PASSE obligatoire (relire chaque page, résoudre chaque
question une deuxième fois, corriger l'écart : à exiger explicitement, un agent peut l'omettre). Ne lance JAMAIS l'ingestion, ne touche ni à la base
ni à Docker ni à git.

## Ce que tu rends

Comme dans `CONSIGNES.md` : dossier, nombre de fichiers et de questions, sortie du validateur, `incertitudes`, questions douteuses, figures
produites, QCM défectueux convertis en `ouverte`, et la liste exacte des `themes` utilisés (pour le contrôle des collisions).
