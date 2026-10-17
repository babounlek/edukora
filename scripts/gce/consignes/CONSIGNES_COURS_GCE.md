# Rédiger des cours GCE O/L (en anglais) - consignes de lot

Tu rédiges des **cours** (objets JSON « mode cours » de correction-experte) pour le GCE Ordinary Level du Cameroun
(Maths, Physique, Chimie), un cours par thème de ta tranche. Chaque cours est lu par un élève de Form 5 (15-17 ans)
qui prépare le GCE O/L : il doit comprendre, puis savoir faire les questions types de l'examen. Tout est **en anglais**.

Lis d'abord ton fichier de tranche (`_gce_staging/cours/_slice_NN.json`) : pour chaque thème il donne `matiere`, `theme`
(nom exact du Tag), `epreuve_source` et 1 à 3 vraies questions d'examen du thème (niveau et style à viser). Les 6 items de quiz
du thème existent déjà en base : ton cours doit les préparer, pas les recopier (aucun énoncé du cours ne reprend un énoncé de référence).

## Format d'un fichier (un fichier par thème, UN SEUL objet JSON, pas de tableau)

Dossier de sortie : celui que le lanceur te donne (`D:\edukora\backend\ingest\cm\cours-gce-NN\`, crée-le). Nom du fichier :
`<cours_id>.json`. N'écris JAMAIS ailleurs, ne supprime JAMAIS un fichier qui n'est pas le tien, **n'utilise jamais `rm` sur un dossier**.

```json
{
  "cours_id": "cours-gce-<matiere court>-<slug du theme>",
  "meta": {
    "titre": "<Theme in Title Case>: <angle concret>",
    "matiere": "Mathematics" | "Physics" | "Chemistry",
    "pays": "cm",
    "serie": "GCE O/L",
    "sous_theme": "<sous-thème court en anglais>",
    "duree_estimee_min": 20 a 40,
    "tags": ["<theme, EXACTEMENT comme donne>"],
    "savoir_officiel": null,
    "statut": "brouillon"
  },
  "source": {
    "epreuve_id": "<epreuve_source sans .html>",
    "epreuve_titre": "GCE O/L <matiere> past paper (Cameroon)",
    "epreuve_source": "<epreuve_source tel que donne dans la tranche>",
    "exercice_numero": "1",
    "rappel_id": "rdm-gce-<matiere court>-<slug du theme>-0",
    "rappels_lies": [],
    "correction_id": null
  },
  "sections": [ ...7 sections, dans CET ordre... ]
}
```

- `matiere court` : `maths`, `physics`, `chemistry`. `slug du theme` : minuscules, sans accents, tout non-alphanumérique -> tiret
  (« Ohm's law » -> `ohm-s-law`). `cours_id` unique, jamais réutilisé.
- `tags` : **exactement une valeur, le thème donné, à l'identique** (c'est ce qui relie le cours aux items de quiz). N'ajoute AUCUN autre tag
  (les tags secondaires fusionnent avec des tags français existants).
- `titre` : en anglais, unique, jamais identique au thème nu ; il nomme le thème et l'angle (« Mole concept: from grams to moles and back »).

## Les 7 sections (types exacts, dans l'ordre)

1. `{"type":"accroche","contenu_markdown":"..."}` : 3-5 phrases, une situation camerounaise concrète (FCFA, marché, Douala, Bamenda...), pourquoi ce thème
   revient au GCE. Pas de formule.
2. `{"type":"prerequis","items":["...", "..."]}` : 2 à 4 notions déjà acquises, formulées comme des faits (« Mass is measured in kilograms »).
3. `{"type":"regle","titre":"...","contenu_markdown":"...","formule_principale":null,"variantes":[{"nom":"...","quand_utiliser":"...","contenu_markdown":"..."}]}` :
   le cœur du cours. Définitions, formules (LaTeX), unités, tableau Markdown si utile. 1 à 3 `variantes` (cas particuliers ou méthodes). Niveau O/L strict.
4. `{"type":"exemple_resolu","enonce_markdown":"...","epreuve_source":false,"etapes":[{"numero":1,"action":"...","justification":"...","resultat_markdown":"..."}],"conclusion_markdown":"..."}` :
   un exemple complet de style GCE (calcul ou raisonnement), 3 à 6 étapes numérotées avec justification, énoncé INVENTÉ (pas copié des références).
5. `{"type":"erreurs_classiques","items":[{"erreur_markdown":"...","pourquoi_faux":"...","correction_markdown":"..."}]}` : 3 à 5 vraies erreurs d'élèves sur ce thème.
6. `{"type":"exercices_application","items":[{"numero":1,"difficulte":"facile","enonce_markdown":"...","solution_markdown":"..."},{"numero":2,"difficulte":"moyen",...},{"numero":3,"difficulte":"approfondissement",...}]}` :
   exactement 3 exercices (facile, moyen, approfondissement), énoncés autonomes et inventés, solutions détaillées avec résultat en **gras**.
7. `{"type":"synthese","items_markdown":["...", "..."]}` : 4 à 6 points à retenir.

## Rigueur (non négociable)

- **Génère les fichiers avec un script Python** (`D:\edukora\venv\Scripts\python.exe`, script préfixé par ton numéro de tranche, dans le scratchpad, jamais dans le dépôt)
  où CHAQUE valeur numérique d'un exemple ou d'une solution est RECALCULÉE (`assert`) avant d'être écrite. Chimie : équations équilibrées atome par atome (par code),
  masses atomiques O/L (H=1, C=12, N=14, O=16, Na=23, Mg=24, Al=27, S=32, Cl=35.5, K=39, Ca=40, Cu=64, Zn=65), volume molaire 24 dm3, Avogadro 6.0 x 10^23.
  Physique : g = 10 m s^-2, c(eau) = 4200 J/kg/K, v(son) = 330 m/s, formule puis remplacement avec unités puis résultat. Maths : recalcule tout.
- **Backslash LaTeX DOUBLÉ dans le JSON** : écris les chaînes Python en raw strings (`r"$\frac{1}{2}$"`) et sors le JSON avec `json.dump(..., ensure_ascii=False)`.
  Le `$` hors formule s'écrit `\$`. Les nombres : pas d'espace insécable bizarre ; sépare les milliers avec `\,` dans un `$...$`.
- **Faits exacts et au programme GCE O/L Form 5** (Cameroun). En cas de doute sur une convention, choisis la formulation la moins ambiguë ou retire-la. Jamais de niveau Advanced.
- **Pas de figure** : décris par le texte ou un tableau Markdown. Aucun placeholder d'image.
- Pas de tiret cadratin ni demi-cadratin ; pas de français ; pas de renvoi à « the question above » / « the figure below ».
- Un cours substantiel mais lisible : `regle` de 150 à 450 mots, exemple résolu complet, solutions d'exercices détaillées.

## Contrôle final

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_cours_gce.py D:\edukora\backend\ingest\_gce_staging\cours\_slice_NN.json <ton dossier de sortie>
```

Il doit afficher `OK` (les « warn » sont à relire). Puis SECONDE PASSE obligatoire : relis chaque cours comme un élève (le cours est-il exact, complet,
sans faute de physique/chimie/maths ? les erreurs classiques sont-elles de vraies erreurs ? les exercices d'application se résolvent-ils avec les seules données ?)
et refais chaque exercice sans regarder ta solution ; corrige tout écart et relance le validateur.

Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à un autre fichier du dépôt.

## Ce que tu rends

Rapport court : dossier, nombre de cours, sortie du validateur, nombre de corrections de la seconde passe, et tout thème que tu n'as pas pu couvrir honnêtement (avec la raison).
