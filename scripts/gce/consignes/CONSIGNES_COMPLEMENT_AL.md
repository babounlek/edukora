# Complément aux consignes - GCE ADVANCED LEVEL (A Level)

Lis `CONSIGNES.md` d'abord, puis ce complément, puis le complément de TA matière (`CONSIGNES_COMPLEMENT_CHIMIE.md`, `_PHYSIQUE.md`
ou `_BIOLOGIE.md`) pour la forme (LaTeX, thèmes, figures). Ces deux derniers parlent de l'O Level : **ce complément prime** sur tout ce
qui concerne le niveau, les codes, les formats de questions et les constantes.

## Identité du sujet

- `examen` `"gce_al"` (et non `"gce_ol"`), `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`.
- `matiere` `"Chemistry"`, `"Physics"` ou `"Biology"` (la même matière que l'O Level : le niveau est porté par `examen`).
  Les autres matières ont leur complément (Further Mathematics, Pure Mathematics with Mechanics / with Statistics, Computer Science,
  ICT, Economics, History, Geography) ; la liste complète des codes du Board par niveau est `CODES_OFFICIELS_GCE` dans
  `backend/catalog/models.py` (A/L : Accounting 0705, Biology 0710, Chemistry 0715, Economics 0725, English Language 0730, Literature 0735,
  Food Science and Nutrition 0740, French 0745, Special Bilingual Education French 0746, Geography 0750, Geology 0755, History 0760,
  Pure Maths with Mechanics 0765, with Statistics 0770, Further Mathematics 0775, Physics 0780, Religious Studies 0785,
  Philosophy 0790, Computer Science 0795, ICT 0796). Le validateur refuse un libellé ou un code qui ne s'y trouve pas.
- `code_matiere` (lis le code imprimé sur la page de garde et vérifie « ADVANCED LEVEL ») : **Chemistry 0715, Physics 0780,
  Biology 0710**. Un sujet dont la page de garde dit « Ordinary Level » ne doit PAS être transcrit ici : signale-le et arrête-toi.
- DOSSIER = `gce-al-<matiere>-<annee>-p<paper>-officiel-cameroun` avec `<matiere>` = `chemistry`, `physics` ou `biology`
  (ex. `gce-al-chemistry-2023-p1-officiel-cameroun`). `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_<MATIERE>_<ANNEE>_P<n>.pdf`
  (`<MATIERE>` en majuscules : CHEMISTRY, PHYSICS, BIOLOGY). Ce sont des **scans sans couche texte** : lis chaque page en image
  avec l'outil Read (`pages`), `pdftotext` ne renvoie rien.
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` (jamais ailleurs). Préfixe tous tes fichiers temporaires par DOSSIER.

## Niveau des corrigés

Niveau **Advanced Level** (Lower et Upper Sixth), pas Form 5 : raisonnement rigoureux, démonstrations complètes, unités et chiffres
significatifs soignés, vocabulaire scientifique exact. Pour une question rédigée, écris la réponse qu'un candidat qui obtient
tous les points rendrait (définition précise, mécanisme, calcul étape par étape, conclusion). Constantes : celles que le
sujet imprime (feuille de données, formulaire) ; à défaut, dis explicitement la valeur retenue dans le corrigé
(ex. « $g = 9.8\ \mathrm{m\,s^{-2}}$ ») et note-le dans `incertitudes`. Calculatrice et formulaire autorisés.

## Paper 1 (QCM, 50 questions, 1h30)

UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, `choix` lettres minuscules a-d,
`reponse_correcte` une lettre minuscule, `points` `""`, `groupes` `[]`, `duree_epreuve` `"1h30"`. Un sujet A Level mélange des
FORMATS (Chimie : questions 1 à 36 « meilleure réponse », puis questions à plusieurs affirmations numérotées 1, 2, 3 dont il
faut dire lesquelles sont correctes, ou assertion et raison). Pour ces formats : recopie les affirmations numérotées dans
l'énoncé, et donne comme texte de chaque choix la combinaison imprimée (« 1, 2 and 3 are correct »...). La consigne propre à
ces questions (« Directions: ... ») se recopie dans `enonce_intro_markdown` de l'exercice, jamais deux fois.

## Paper 2 (théorie) et Papers suivants

Lis la page de garde : durée (souvent 3 h), nombre de questions à traiter, sections. UN fichier PAR QUESTION du sujet,
`numero_exercice` `"1"`, `"2"`... (préfixe `"B1"` si une section repart de 1), sous-questions (a), (b)... = `questions`.
**Règle de choix** (« Answer any FIVE out of the eight questions », « Section A compulsory, Section B: answer two »...) :
écris `regles_choix` identiques dans TOUS les fichiers du dossier, avec `portee` égal à un repère de `groupes` :
- sujet SANS sections : `groupes` `["PAPER 2"]` dans chaque fichier et
  `regles_choix` `[{"type":"parmi","portee":"PAPER 2","repondre":5,"sur":8}]` ;
- sujet avec sections : `groupes` `["SECTION A"]`... et une règle par section concernée.
`points` : le total imprimé de l'exercice (« Total = 20 marks ») dans `points` ; les points par bloc dans `points` de chaque
sous-question quand le sujet les imprime. Ne corrige JAMAIS les points du sujet, même s'ils ne somment pas (note-le).
`introduction_markdown` : toute la consigne de la page de garde (durée, nombre de questions, rappels), identique partout.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, courts. **Réutilise** le nom d'un thème de l'O Level quand c'est la même notion
(ex. chimie : atomic structure, periodic table, chemical bonding, mole concept, electrolysis, redox reactions, rates of reaction,
energy changes, chemical equilibrium, organic chemistry, alkanes and alkenes, alcohols and carboxylic acids, polymers,
qualitative analysis ; physique : motion, forces and their effects, work energy and power, thermal physics, waves,
current electricity, electric circuits, electromagnetic induction, electromagnetism, atomic and nuclear physics,
electronics and semiconductors ; biologie : voir le complément Biologie). Pour une notion propre au niveau Advanced, choisis un nom
explicite (ex. chemical kinetics, thermodynamics, transition elements, electrode potentials, capacitors, alternating current,
circular motion, gravitational fields, nuclear binding energy, enzyme kinetics, genetics and inheritance, protein synthesis).
`Tag.name` est UNIQUE et PARTAGÉ avec le contenu français : jamais un mot qui existe tel quel en français.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2> --code <0715|0780|0710> [--questions 50]
```

Il doit afficher `OK`. Puis la SECONDE PASSE obligatoire des consignes générales (relire chaque page, résoudre chaque question une
deuxième fois). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à un autre dossier.

## Ce que tu rends

Comme dans `CONSIGNES.md` : dossier, nombre de fichiers et de questions, sortie du validateur, `incertitudes`, questions douteuses,
figures produites, et les QCM dont la clé imprimée ou les options te semblent défectueuses (convertis en `ouverte`).
