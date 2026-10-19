# Complément cours GCE - matières rédigées ou de connaissances (O Level et A Level)

Matières concernées : English Language, French, Food and Nutrition, History, Geography, Citizenship Education, Religious Studies, Philosophy, Economics,
Commerce, Computer Science, ICT, Human Biology, Geology, Additional Mathematics (calculs : mêmes règles que `CONSIGNES_COURS_GCE.md`).
Lis `CONSIGNES_COURS_GCE.md` en entier (format, 7 sections dans l'ordre, tags = le thème seul, validateur, seconde passe), puis ce complément : **il prime** pour
la matière, la série, les identifiants et la façon de remplir les sept sections quand le thème ne se réduit pas à un calcul.

## Ce qui change

1. **Matière, série, identifiants** : ils viennent de ta tranche et de la table du validateur (`valider_cours_gce.py`) : `meta.matiere` = le libellé anglais attendu
   (« English Language », « History », « Food and Nutrition », « Religious Studies »...), `meta.serie` = la valeur de la tranche (`"GCE O/L"` ou `"GCE A/L"`),
   `cours_id` = `cours-gce-<court>-<slug du thème>` et `rappel_id` = `rdm-gce-<court>-<slug du thème>-0` avec `<court>` de la table `COURT` du validateur
   (`english`, `history`, `food-nutrition`, `religious-studies`, `computer-science`...). `meta.pays` `"cm"`, `meta.savoir_officiel` `null`, `meta.statut` `"brouillon"`,
   `meta.tags` = `[<le thème, à l'identique>]` (un thème de langue ou de religion porte son préfixe : `"O Level English - reading comprehension"`, `"A Level Religious Studies - ..."`).
   `source.epreuve_source` = la valeur de la tranche, `source.epreuve_id` = cette valeur sans `.pdf`.
   **`meta.titre` doit être unique dans TOUTE la matière, tous niveaux confondus** : l'ingestion déduit le slug du titre et IGNORE en silence un cours dont le slug existe déjà (un cours A Level « Question Tags: matching the tag to the statement »
   a ainsi été écarté parce que le cours O Level du même thème portait ce titre). Pour un thème déjà traité à l'autre niveau, titre différent et propre au niveau (« ... at Advanced Level: ... »).
2. **Niveau** : O Level = Form 5 (15 à 17 ans), A Level = Advanced (Lower et Upper Sixth, 17 à 19 ans). Le cours amène l'élève à répondre aux questions types des références
   de ta tranche. `regle` : 150 à 450 mots (O Level), 200 à 500 mots (A Level), organisés par intertitres Markdown (`###`) et tableaux Markdown quand ils aident
   (causes / conséquences, comparaison, plan type).
3. **Les sept sections pour un sujet de connaissances ou de rédaction** :
   - `accroche` : une situation concrète, camerounaise quand elle est vraie, qui montre pourquoi le thème tombe à l'examen ; 3 à 5 phrases, aucun fait douteux.
   - `prerequis` : 2 à 4 notions déjà acquises.
   - `regle` : le cœur du cours : définitions exactes, faits essentiels, mécanismes ou arguments, structure d'une bonne réponse à ce type de question (mot d'ordre : « define »,
     « state », « explain », « discuss », « to what extent »...). `variantes` : 1 à 3 cas ou méthodes (par exemple « question d'explication » et « question de discussion »).
   - `exemple_resolu` : une question d'examen INVENTÉE (style GCE) et sa **réponse modèle construite pas à pas** : `etapes` (3 à 6) = analyser le mot d'ordre, bâtir le plan,
     développer chaque point avec une preuve, conclure ; `conclusion_markdown` = la réponse modèle complète, ou ses points clés quand elle est longue. `epreuve_source` `false`.
   - `erreurs_classiques` : 3 à 5 vraies erreurs de copie (hors sujet, énumérer au lieu d'expliquer, anachronisme, confusion de deux notions, faute de langue typique) avec correction.
   - `exercices_application` : exactement 3 questions INVENTÉES (facile, moyen, approfondissement), énoncés autonomes ; `solution_markdown` = la réponse modèle ou les points de barème
     (« Award a mark for... ») avec le résultat final en **gras** quand il y en a un. Une question de calcul (nutrition, commerce, économie) : valeurs recalculées par script.
   - `synthese` : 4 à 6 points à retenir.
4. **Exactitude : tu n'as aucun manuel sous la main.** N'invente AUCUN fait : date, nom de personne ou de lieu, chiffre, statistique, titre d'ouvrage, citation, numéro de verset, article de loi.
   Quand tu doutes, retire le fait ou formule-le de façon générale (« in the early nineteenth century », « according to Islamic tradition »). Un cours plus court et exact
   vaut mieux qu'un cours complet et faux. Faits locaux (histoire du Cameroun, institutions, religions africaines traditionnelles, plats, géologie du Cameroun) : seulement ceux que tu peux établir avec certitude.
5. **Neutralité** (History, Citizenship, Religious Studies, Philosophy) : expose les positions et les raisons de chaque tradition ou école sans prêcher ni dénigrer (« Christians believe »,
   « for Kant... ») ; pas de position partisane sur la politique camerounaise.
6. **Langues (English Language, French)** : les règles sont énoncées en anglais ; chaque exemple de langue est VÉRIFIÉ (une phrase donnée comme correcte doit l'être ; une phrase fausse
   n'apparaît que dans `erreurs_classiques`, signalée comme fausse). French : exemples en français correct avec leur traduction anglaise, accents exacts ; le validateur signale (« warn ») le texte
   français d'un lot anglais : c'est attendu pour les exemples. Thèmes de compétence (reading, listening, directed writing, composition) : le cours enseigne la MÉTHODE (types de questions,
   stratégie, répartition du temps, grille de notation du Board connue : contenu, expression, exactitude), jamais un texte à recopier.
7. **Calculs** (Food and Nutrition, Commerce, Economics, Computer Science, ICT, Additional Mathematics, Human Biology) : toute valeur numérique d'un exemple ou d'une solution est recalculée par `assert`
   dans ton script ; unités et FCFA ; conversions binaires, tables de vérité, formules de tableur (`\$` pour un `$` hors formule) vérifiées par code.
8. **Aucune figure, aucun placeholder d'image** ; décris par le texte ou un tableau Markdown. Pas de tiret cadratin ni demi-cadratin (le validateur refuse). Pas de renvoi à « the question above ».
9. **Les 6 items de quiz du thème existent déjà** : ton cours les prépare sans en recopier un énoncé. Les références de ta tranche sont de vraies questions d'examen : niveau et style à viser,
   jamais à copier (le validateur refuse 9 mots consécutifs identiques).

## Contrôle

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_cours_gce.py <tranche.json> <dossier de sortie>
```

Il doit afficher `OK` (relis les « warn »), puis la SECONDE PASSE de `CONSIGNES_COURS_GCE.md` : relis chaque cours comme un élève ; pour chaque fait, demande-toi « en suis-je CERTAIN ? » et retire ce qui ne l'est pas ;
refais chaque exercice sans regarder ta solution. Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à un autre fichier du dépôt.

## Ce que tu rends

Dossier, nombre de cours, sortie du validateur, nombre de corrections de la seconde passe, faits retirés faute de certitude (liste courte) et thèmes non couverts honnêtement (avec la raison).
