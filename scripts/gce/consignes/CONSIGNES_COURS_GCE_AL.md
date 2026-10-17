# Complément cours GCE ADVANCED LEVEL (A Level) - Chimie, Physique, Biologie, Further Mathematics

Lis `CONSIGNES_COURS_GCE.md` en entier, puis ce complément : **il prime** pour le niveau, les constantes, la matière et la série.
Le format (un objet JSON par thème, 7 sections dans l'ordre, tags = le thème seul), la rigueur par script et le validateur restent ceux de
`CONSIGNES_COURS_GCE.md`.

## Ce qui change

1. **Niveau Advanced (Lower et Upper Sixth), jamais Form 5.** Le cours doit amener un élève de 17-19 ans à traiter les questions types du sujet
   A Level (références de la tranche) : définitions précises, mécanismes, démonstrations utiles, formules avec unités, cas particuliers,
   vocabulaire exact. Une `regle` de 200 à 500 mots est normale ; l'exemple résolu est un vrai problème A Level en 4 à 6 étapes.
2. **`meta.matiere`** : `"Chemistry"`, `"Physics"`, `"Biology"`, `"Further Mathematics"`, `"Pure Mathematics with Mechanics"` ou
   `"Pure Mathematics with Statistics"` (jamais « Pure Mathematics » seul).
   **`meta.serie`** : `"GCE A/L"` (et non `"GCE O/L"`). `meta.pays` `"cm"`, `meta.savoir_officiel` `null`, `meta.statut` `"brouillon"`.
3. **Identifiants** : `cours_id` = `cours-gce-<court>-<slug du theme>` avec `<court>` = `chemistry`, `physics`, `biology`, `further-maths`, `pm-mechanics` ou `pm-statistics` (table `COURT` de `valider_cours_gce.py`) ;
   `rappel_id` = `rdm-gce-<court>-<slug du theme>-0`. `source.epreuve_source` = la valeur de la tranche (un sujet A Level) ; `epreuve_id` = cette valeur sans `.pdf`.
4. **Constantes** : écris-les dans le cours quand elles servent (A Level : masses atomiques à une décimale, H = 1.0, C = 12.0, N = 14.0, O = 16.0,
   Na = 23.0, S = 32.1, Cl = 35.5 ; $g = 9.8\ \mathrm{m\,s^{-2}}$ ; $N_A = 6.02\times10^{23}\ \mathrm{mol^{-1}}$ ; $R = 8.31\ \mathrm{J\,K^{-1}\,mol^{-1}}$ ; volume molaire
   $24\ \mathrm{dm^3\,mol^{-1}}$ à r.t.p.), et utilise la même valeur dans tout le cours.
5. **Biologie** : pas de figure ; décris les structures et les expériences par le texte et par des tableaux Markdown ; les `exercices_application` de génétique
   se vérifient par script (rapports, probabilités). Pas de contenu au-delà du programme A Level du GCE Board.
6. **Further Mathematics, Pure Mathematics with Mechanics / with Statistics** : toute étape de calcul est recalculée (sympy ou `fractions`), forme exacte avant approximation, équation numérotée
   (`\\tag`) sur trois lignes (`$$`, formule, `$$`).
7. **Chimie** : équations équilibrées atome par atome par script ; conditions et réactifs exacts pour les réactions organiques ; états de la matière.
8. **Physique** : formule, remplacement avec unités, résultat ; définitions exactes (champ, potentiel, capacité...).
9. **Les 6 items de quiz du thème existent déjà** : ton cours les prépare sans en recopier un énoncé. Aucune figure, aucun placeholder d'image.
10. **Titres** inchangés (anglais). Les 7 sections et leurs champs sont ceux de `CONSIGNES_COURS_GCE.md`.

## Contrôle

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_cours_gce.py <tranche.json> <dossier de sortie>
```

La tranche porte `"serie": "GCE A/L"` : le validateur la lit. Il doit afficher `OK` ; puis la seconde passe. Ne lance jamais l'ingestion.
