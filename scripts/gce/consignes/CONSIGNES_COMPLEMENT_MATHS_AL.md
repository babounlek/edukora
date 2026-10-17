# Complément aux consignes - GCE ADVANCED LEVEL, FURTHER MATHEMATICS (code 0775)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce
fichier. **Ce fichier prime** pour tout ce qui touche à Further Mathematics : codes, noms de dossier, thèmes. Les compléments
Chimie / Physique / Biologie ne te concernent pas.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Further Mathematics"`, `code_matiere` `"0775"`
  (lis la page de garde : « ADVANCED LEVEL », « 0775 »). Une autre matière, un autre code ou un autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-further-maths-<annee>-p<paper>-officiel-cameroun` (ex. `gce-al-further-maths-2023-p2-officiel-cameroun`).
  `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_FURTHER_MATHS_<ANNEE>_P<n>.pdf`
  (scans, sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30, calculatrice autorisée. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"` (voir
  `CONSIGNES_COMPLEMENT_AL.md`). Lettres a-d minuscules, `reponse_correcte` une lettre. Une réponse de QCM se justifie par le calcul.
- **Paper 2** : 3 h, « Answer ALL 10 questions », points approximatifs par partie entre crochets. UN fichier PAR QUESTION
  (`numero_exercice` `"1"` à `"10"`), sous-questions (a), (b)... = `questions`. Aucune règle de choix : `regles_choix` `[]`,
  `groupes` `[]`. `points` de l'exercice = total imprimé s'il y en a un, sinon `""` ; points de chaque sous-question = ceux entre crochets.
- **Paper 3** : 2h30, « Answer ALL questions ». Même forme que le Paper 2. Lis la page de garde : si une question offre un choix
  (« EITHER ... OR »), consigne `regles_choix` comme décrit dans `CONSIGNES_COMPLEMENT_AL.md`, sinon `[]`.
- `introduction_markdown` : la consigne de la page de garde, identique dans tous les fichiers du dossier. `duree_epreuve` : `"1h30"`,
  `"3h"` ou `"2h30"` selon la page de garde.

## Corrigés

Niveau Advanced Level : démonstrations complètes (récurrences, preuves par l'absurde, justification des étapes), toute valeur
numérique recalculée avec Python (`D:\edukora\venv\Scripts\python.exe`, `sympy` s'il est installé sinon calcul à la main vérifié deux fois),
forme exacte (fractions, racines, `\pi`) avant l'approximation demandée. Pour un graphe à tracer ou un diagramme d'Argand : décris le
tracé (points clés, asymptotes, axes) dans le corrigé ; une figure imprimée dans le sujet se recadre en PNG (voir `CONSIGNES.md`).
Formules : LaTeX entre `$...$`, antislash doublé dans le JSON (`\\frac`, `\\int`, `\\sum`, `\\begin{pmatrix}`...).

**Équations numérotées** : une formule d'affichage avec `\tag{1}` s'écrit sur TROIS lignes (`$$`, la formule, `$$`), jamais `$$ ... \tag{1}$$` sur une seule ligne : le moteur de rendu la prend alors pour une formule en ligne et KaTeX refuse `\tag` (échec du tunnel, constaté sur Further Maths 2025 P3).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites. `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français, les autres matières et les
Maths O Level : **n'emploie pas** les noms de l'O Level (`matrices`, `vectors`, `sets`, `graphs`, `functions and mappings`...), ni un
mot qui existe tel quel en français. Utilise des noms propres au niveau Advanced, par exemple : `complex numbers`, `argand diagram`,
`de moivre theorem`, `roots of unity`, `matrix algebra`, `determinants and inverses`, `linear transformations`, `eigenvalues and
eigenvectors`, `vector geometry in three dimensions`, `lines and planes`, `scalar and vector products`, `polynomial equations`,
`roots and coefficients`, `mathematical induction`, `series summation`, `maclaurin series`, `hyperbolic functions`,
`first order differential equations`, `second order differential equations`, `reduction formulae`, `volumes of revolution`,
`conic sections`, `polar coordinates`, `numerical methods`, `partial fractions`, `inequalities and modulus`, `proof techniques`,
`probability distributions`, `hypothesis testing`, `statics and equilibrium`, `projectile and circular motion`.
Avant de créer un nom, fais un `Grep` des valeurs `"themes"` déjà utilisées dans
`D:\edukora\backend\ingest\cm\gce-al-further-maths-*\*.json` et dans `_gce_staging\gce-al-further-maths-*\*.json` : réutilise le nom
quand la notion est la même (cohérence entre papers et années).

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0775 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire (relire chaque page, résoudre chaque question une deuxième fois, corriger
l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
