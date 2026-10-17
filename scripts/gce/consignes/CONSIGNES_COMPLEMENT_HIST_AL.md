# Complément aux consignes - GCE ADVANCED LEVEL, HISTORY (code 0760)

Lis `CONSIGNES.md` (forme générale), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce fichier.
**Ce fichier prime** pour tout ce qui touche à l'Histoire : codes, noms de dossier, papers, règles de choix, corrigés, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"History"`, `code_matiere` `"0760"`
  (page de garde : « ADVANCED LEVEL », « 0760 »). Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-history-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_HISTORY_<ANNEE>_P<n>.pdf`
  (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"` (voir `CONSIGNES_COMPLEMENT_AL.md`). Un QCM d'histoire a une réponse
  factuelle : si DEUX options sont défendables ou si la date/le fait imprimé est inexact, convertis en `ouverte` (`convertir_en_ouverte.js`) plutôt que de choisir.
- **Paper 2 (Cameroon History Since 1800)** : 3 h, « answer FOUR questions, choosing at least ONE from each of the sections ». Repère les sections imprimées
  (SECTION A, SECTION B...). UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé (ou `"B1"`... si une section renumérote), `groupes` = le repère de section
  (`["SECTION A"]`...). `regles_choix` : pour CHAQUE section `{"type":"parmi","portee":"SECTION A","repondre":1,"sur":<nombre de questions de la section>}` (le minimum imposé),
  identique dans tous les fichiers du dossier ; la règle « 4 en tout » est recopiée dans `introduction_markdown` et signalée dans `incertitudes` (non exprimable).
- **Paper 3 (Africa and World History)** : 3 h, « answer FOUR questions, choosing ONE from each of the FOUR sections ». Même forme : une règle
  `{"type":"parmi","portee":"SECTION <X>","repondre":1,"sur":<N de la section>}` par section (exactement ce que dit le sujet). `groupes` = repère de section.
- Sous-questions (a), (b)... = `questions` de l'exercice ; points entre crochets dans `points`. « All questions carry equal marks » : `points` de l'exercice `""` s'il n'est pas imprimé.
- `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"` ou `"3h"`.

## Corrigés (essais et réponses factuelles)

- Réponse modèle d'un candidat qui obtient tous les points : introduction (cadre, dates, définition des termes), développement structuré (causes, déroulement, conséquences,
  acteurs, évaluation) et conclusion argumentée, au niveau Advanced. Pour une question « discuss / assess / to what extent », prends une position justifiée et nuance-la.
- **Exactitude avant tout** : dates, noms, traités, lieux et chiffres doivent être ceux de l'historiographie établie (Cameroun : Duala et traités de 1884, mandats et tutelles, UPC,
  Réunification 1961, Constitutions...). Quand une date ou un fait n'est pas sûr, n'invente pas : écris une formulation prudente (« in the early 1960s ») ou retire le détail.
  N'invente ni citation, ni statistique, ni source. Consigne dans `incertitudes` tout fait que tu n'as pas pu vérifier avec certitude.
- Pour un QCM : explique pourquoi la bonne option est exacte et le piège des autres ; termine par « **Answer: C.** ».
- Une carte ou un document imprimé (extrait de texte, tableau, carte) se recopie (texte) ou se recadre en PNG, déclaré dans `figures`.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites : par exemple `german colonial rule in cameroon`, `british and french mandates`, `trusteeship period`, `nationalist movements in cameroon`,
`reunification of cameroon`, `federal republic of cameroon`, `scramble for africa`, `slave trade and abolition`, `european explorers in africa`, `world war one`, `world war two`,
`league of nations`, `united nations organisation`, `cold war`, `pan-africanism`, `african independence movements`, `apartheid in south africa`, `organisation of african unity`,
`industrial revolution in europe`, `french revolution`. `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français (Histoire BEPC/Probatoire/BAC) : n'emploie pas un mot qui existe
tel quel en français, ni une variante d'accent ou de pluriel d'un thème français (« decolonisation » seul, « apartheid » seul, « colonisation » seul sont à éviter) : préfère des noms
qualifiés comme ci-dessus. Avant de créer un nom, fais un `Grep` des valeurs `"themes"` déjà utilisées dans `D:\edukora\backend\ingest\cm\gce-al-history-*\*.json` et
`_gce_staging\gce-al-history-*\*.json` : réutilise le nom quand la notion est la même.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0760 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS
l'ingestion, ne touche ni à la base ni à Docker ni à git.
