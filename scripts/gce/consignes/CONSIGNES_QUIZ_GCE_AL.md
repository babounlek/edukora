# Complément quiz GCE ADVANCED LEVEL (A Level) - Chimie, Physique, Biologie, Further Mathematics

Lis `CONSIGNES_QUIZ_GCE.md` en entier, puis ce complément : **il prime** pour tout ce qui touche au niveau, aux constantes et à la matière.
Le contrat des items (champs, QCM, `external_id`, rigueur par script, validateur, seconde passe) reste celui de `CONSIGNES_QUIZ_GCE.md`.

## Ce qui change par rapport à l'O Level

1. **Niveau Advanced (Lower et Upper Sixth), jamais Form 5.** Les questions ressemblent à celles des sujets A Level fournis en
   `materiel_reference` : raisonnement en plusieurs étapes, vocabulaire scientifique exact, notions du programme Advanced (mécanismes,
   cinétique, équilibres, champs, circuits à plusieurs éléments, génétique, biochimie, algèbre linéaire, nombres complexes...).
   Un QCM A Level pose un vrai piège de raisonnement, pas une définition de Form 5.
2. **Requête** : `matiere` vaut `"Chemistry"`, `"Physics"`, `"Biology"`, `"Further Mathematics"`, `"Pure Mathematics with Mechanics"` ou
   `"Pure Mathematics with Statistics"` (jamais « Pure Mathematics » seul, refusé) et `cursus` vaut
   `[{"examen":"gce_al","serie":""}]` : recopie-les TELS QUELS depuis la requête, ainsi que `competence` pour `theme`.
3. **Constantes** : l'A Level n'impose pas `g = 10`. Écris la valeur utilisée DANS l'énoncé quand elle compte (« take
   $g = 9.8\ \mathrm{m\,s^{-2}}$ »). Chimie : masses atomiques à une décimale (H = 1.0, C = 12.0, N = 14.0, O = 16.0, Na = 23.0, Mg = 24.3, Al = 27.0,
   S = 32.1, Cl = 35.5, K = 39.1, Ca = 40.1, Cu = 63.5, Zn = 65.4), volume molaire $24\ \mathrm{dm^3\,mol^{-1}}$ à r.t.p., $R = 8.31\ \mathrm{J\,K^{-1}\,mol^{-1}}$,
   $N_A = 6.02\times10^{23}\ \mathrm{mol^{-1}}$ ; donne-les dans l'énoncé quand ils servent. Physique : $c = 3.00\times10^{8}\ \mathrm{m\,s^{-1}}$, $e = 1.60\times10^{-19}\ \mathrm{C}$,
   $h = 6.63\times10^{-34}\ \mathrm{J\,s}$, $\varepsilon_0 = 8.85\times10^{-12}\ \mathrm{F\,m^{-1}}$, `G = 6.67e-11`... : donne-les dans l'énoncé quand ils servent.
3bis. **Contextes** : camerounais quand c'est naturel, mais le sujet scientifique prime ; pas de contexte forcé.
4. **Biologie** : pas de figure ; décris l'expérience, les données (tableaux Markdown) et demande une interprétation ou un calcul (rapport, pourcentage,
   rapport phénotypique). Les QCM de génétique se vérifient par script (croisements, rapports, probabilités).
5. **Further Mathematics** : tout calcul (déterminant, racine d'un complexe, somme de série, intégrale) est recalculé par script (`sympy` si disponible, sinon
   Python exact avec `fractions`). Forme exacte avant approximation. Équation numérotée avec `\\tag` : formule sur trois lignes.
5bis. **Pure Mathematics with Mechanics / with Statistics (0765 / 0770)** : même rigueur que Further Mathematics (calcul recalculé par script, forme exacte
   d'abord). Mechanics : schéma décrit dans l'énoncé (forces, axes, sens positif), `g = 9.8` écrit dans l'énoncé, unités SI. Statistics : loi et paramètres
   nommés, valeurs de table données dans l'énoncé ou calcul exact. Les thèmes de la partie Pure Mathematics (fonctions, polynômes, complexes,
   récurrence...) existent peut-être déjà côté Further Mathematics ou O Level : un thème partagé avec un autre niveau est exclu de la requête
   (niveaux différents), et un `external_id` déjà pris se renumérote à partir de 10 (voir `CONSIGNES_QUIZ_GCE.md`).
6. **Thème** : le `theme` est EXACTEMENT la valeur de `competence` (un Tag existant). N'en crée aucun autre.
7. **Aucune figure** sauf nécessité absolue (même règle que l'O Level) ; préfère un tableau Markdown ou une description.
8. **Titres du corrigé** inchangés : `### Method reminder` puis `### Solution`.

## Contrôle

Même validateur : `valider_quiz_gce.py <tranche.json> <dossier>` (il doit afficher `OK`), puis la seconde passe. Ne lance jamais l'ingestion.
