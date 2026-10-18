# Complément aux consignes - GCE ORDINARY LEVEL, GEOGRAPHY (0550) et HISTORY (0560)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis ce fichier. **Ce fichier prime** pour tout ce qui touche à la Géographie et à l'Histoire O Level :
codes, noms de dossier, papers, règles de choix, cartes, exactitude, thèmes. Niveau Form 5 (pas Advanced) : `CONSIGNES.md` fait foi.

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Geography"` (`code_matiere` `"0550"`) ou `"History"` (`"0560"`).
  Autre matière, autre code ou autre niveau (page de garde : « ORDINARY LEVEL ») : ne transcris rien et signale-le.
- DOSSIER = `gce-ol-<geography|history>-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les deux papers

- **Paper 1** : 50 QCM, 1h30 (Geography : calculatrice permise). UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules,
  `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Un QCM numérique (échelle, gradient, densité) se justifie par le calcul recalculé avec Python ; un QCM
  factuel ambigu ou une clé imprimée douteuse : convertis en `ouverte` (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`), jamais une lettre au hasard.
  Une carte, un graphique ou un schéma imprimé dont dépend le QCM se recadre en PNG.
- **Paper 2** : 2h30, questions rédigées. **Lis la page de garde de CHAQUE année : les règles changent.** UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé, sous-questions
  (a), (b), (c)... = `questions`, `groupes` = le repère de section (`["SECTION A"]`...), identique dans tous les fichiers d'une section.
  - **Geography** (exemple 2023) : « Answer FOUR questions, choosing ONE from each section » (4 sections ; la question 1 vaut 30 points, les autres 20) : une règle
    `{"type":"parmi","portee":"SECTION <X>","repondre":1,"sur":<N de la section>}` par section. La question 1 peut être obligatoire (carte topographique/fond de carte non fournis dans le PDF :
    écris « [map supplied on the day, not reproduced here] » dans l'énoncé et donne la MÉTHODE en corrigé, sans inventer de valeurs, en le signalant dans `incertitudes`).
  - **History** (exemple 2023, « Modern World History Since 1870 ») : « Answer FOUR questions : TWO from SECTION A, ONE from SECTION B and ONE other from SECTION C ; one of the two from A must be a
    Starred question » : trois règles `parmi` (A : repondre 2, B : repondre 1, C : repondre 1, avec `sur` = le nombre de questions de chaque section). La contrainte « Starred » n'est pas exprimable :
    recopie-la dans `introduction_markdown` et `incertitudes`, et marque la question concernée dans son énoncé par « (Starred question) ».
  - Chaque règle `portee` égale un repère de `groupes` ; mêmes `regles_choix` dans TOUS les fichiers du dossier. Recopie toute la consigne de la page de garde dans `introduction_markdown`.
  - Points : ceux imprimés (ex. 30 / 20) dans `points` de l'exercice ; points des sous-questions entre crochets. Ne corrige jamais les points imprimés.
- `duree_epreuve` : `"1h30"` ou `"2h30"` selon la page de garde.

## Corrigés

- Anglais clair niveau Form 5, réponse modèle complète d'un candidat qui obtient tous les points : définitions, explication, exemples localisés (Cameroun, Afrique, monde), schémas/cartes annotés décrits,
  introduction / développement / conclusion pour les questions longues. Respecte « define », « describe », « explain », « account for », « state ».
- **Exactitude avant tout** : dates, noms, traités, lieux, chiffres et exemples reconnus ; n'invente aucune statistique précise, date, lieu inexistant ou citation ; formulation prudente en cas de doute
  (« about », « in the early 1960s ») ou retrait du détail ; consigne tout fait incertain dans `incertitudes`. Pour l'Histoire : historiographie établie (Cameroun, Afrique, monde depuis 1870).
- Calculs (échelle, densité, pente, pourcentages) recalculés avec Python (`D:\edukora\venv\Scripts\python.exe`) ; formule, remplacement, résultat avec unités.
- Un schéma ou une carte que le candidat doit dessiner se décrit dans le corrigé (légende, éléments à annoter). Un PNG produit (matplotlib, fond blanc, légendé) seulement s'il rend la réponse réellement
  compréhensible ; déclare-le dans `figures` (`type` : 30 caractères MAXIMUM). Une carte ou un graphique imprimé dans le sujet : suis la section Figures de `CONSIGNES.md` (skill
  `reproduire-figure-sans-filigrane`, jamais `pdftoppm`).

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites. **Réutilise le nom d'un thème existant quand c'est la même notion** : Grep des valeurs `"themes"` dans
`D:\edukora\backend\ingest\cm\gce-al-<geography|history>-*\*.json`, `gce-ol-<geography|history>-*\*.json` et `_gce_staging\gce-ol-<geography|history>-*\*.json` (plusieurs agents travaillent en parallèle :
relis les dossiers des autres avant de créer un nom ; n'invente pas trois noms pour la même notion). `Tag.name` est UNIQUE et PARTAGÉ avec le contenu français (Géographie/Histoire BEPC, Probatoire, BAC) et les
autres matières : n'emploie pas un mot qui existe tel quel en français (« population », « urbanisation », « climat », « colonisation », « apartheid »...), ni une variante d'accent ou de pluriel d'un thème
français, ni un nom pris par une autre matière (« energy resources », « industrial location », « industrialisation », « unemployment » le sont) ; préfère des noms qualifiés en 2 à 3 mots.

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM (un champ plus long fait échouer tout l'exercice à l'ingestion).

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper <1|2> --code <0550|0560> [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
