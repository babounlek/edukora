# B1 : des réponses à toucher en maths, cadrage

Origine : test élève Guyguy du 2026-10-25. « C'est moi qui me note ? Je peux cliquer Réussi sans rien faire. » Les 6 questions de maths vues par Guyguy étaient toutes auto-notées (Réussi / Partiel / Échec), donc sans verdict instantané, sans vrai « Bravo ! » et sans points mérités.

## 1. Constat chiffré (base locale, items VALIDÉS)

| Périmètre | Ouvertes (auto-notées) | QCM |
|---|---|---|
| Maths, tous cursus | 2 712 | 421 |
| **Maths BEPC** | **1 063** | **85** |
| Physique | 751 | 469 |
| SVT | 1 419 | 1 066 |
| Chimie | 740 | 220 |

Les autres matières ont déjà environ la moitié de QCM. Les maths sont le trou (92 % d'ouvertes au BEPC), et c'est la matière où l'élève de 3e passe le plus de temps.

Ce que contient une question ouverte aujourd'hui : un énoncé (souvent en deux parties, exemples réels : coefficient directeur puis perpendiculaire, centre de classe puis moyenne, « Montre que… » puis aire) et un corrigé en deux blocs, « Rappel de méthode » puis « Corrigé », en Markdown. Il n'existe **aucune réponse finale lisible par la machine** : c'est pour cela que le site ne peut pas corriger tout seul.

Sur les 1 063 ouvertes du BEPC : environ 10 % portent une figure (104) et environ 17 % ont plusieurs parties (184, estimation par motif dans l'énoncé).

## 2. Options étudiées

| Option | Principe | Pour | Contre |
|---|---|---|---|
| **A. Convertir en QCM** (recommandée) | Garder l'énoncé, le ramener à UNE question à résultat unique, 4 choix dont 3 tirés des erreurs classiques | Verdict immédiat, points et « Bravo ! » mérités, déjà géré par le quiz, saisie en un tap | Il faut du contenu soigné : une clé fausse ou un distracteur absurde est pire qu'une auto-notation |
| B. Champ de saisie numérique | Stocker une réponse attendue, l'élève tape | Pas de distracteurs à écrire | Taper des fractions, racines ou intervalles sur un clavier de téléphone est pénible ; ne couvre que les résultats simples ; il faut quand même extraire la bonne réponse de chaque item |
| C. Mixte | QCM partout, saisie seulement pour un résultat entier ou décimal court | Le meilleur des deux | Deux interfaces à construire et à tester |

**Recommandation : A seule pour le pilote.** C pourra venir plus tard si le pilote montre un besoin.

## 3. Règles de conversion proposées

1. **Une question, un résultat.** On garde la partie la plus formatrice (le résultat final) et on laisse tomber les « Montre que… » : une démonstration reste une question ouverte, c'est un exercice de rédaction qui prépare l'examen.
2. **Quatre choix, une seule bonne réponse**, de même forme (même nombre de chiffres, même unité, même notation), jamais « aucune de ces réponses ».
3. **Les trois mauvais choix sont de vraies erreurs d'élèves** : erreur de signe, inversion, oubli d'une étape, confusion de formule. Source disponible : les cartes « Erreurs classiques » déjà écrites dans les cours.
4. **Clé équilibrée** : les bonnes réponses réparties sur a, b, c, d (aujourd'hui la tendance est à « b » ou « a », ce qui se devine).
5. **Le corrigé reste** : il devient l'explication affichée après la réponse (« Comprendre la correction » existe déjà).
6. **Pas de figure dans le pilote** (10 % des items) : ils viendront ensuite.
7. Pas de tiret cadratin (règle déjà appliquée à l'ingestion) et LaTeX contrôlé par l'audit de rendu.

## 4. Pilote proposé

- **Périmètre :** Maths BEPC, les 6 thèmes les plus fréquents aux examens (Identité remarquable, Statistiques, Factorisation, Radicaux, Triangle rectangle, Repère orthonormé), soit environ 34 questions ouvertes, dont 3 avec figure, laissées de côté.
- **Pourquoi ceux-là :** ce sont ceux qu'un élève de 3e rencontre en premier, et Identité remarquable est le quiz gratuit proposé aux visiteurs (c'est celui de la première impression).
- **Étapes :**
  1. Convertir les ~30 items sans figure (génération avec le skill de quiz, un lot par thème).
  2. **Contrôle indépendant** : un relecteur résout chaque QCM sans voir la clé (skill `enseignant`) ; tout écart est corrigé.
  3. Audit de rendu (`audit-qualite-rendu`) sur les nouveaux items.
  4. Application **sur place** par la chaîne de synchronisation, qui sait déjà mettre à jour type, choix et clé (`mettre_a_jour_item`) : l'identifiant de l'item reste, les quiz déjà joués gardent leur instantané, donc l'historique des élèves n'est pas touché.
  5. Rejouer Guyguy (même persona, même mission) et comparer la note de fun et la friction « je me note moi-même ».
- **Critères de réussite :**
  - Accord du relecteur aveugle avec la clé : 97 % ou plus, 100 % après correction.
  - 0 erreur de rendu.
  - Répartition des bonnes réponses entre a, b, c, d sans lettre à plus de 35 %.
  - Guyguy : plus de friction « je me note moi-même » sur ces thèmes, fun (Q8) de 3 à 4 ou plus.
  - Après quelques semaines de vraies parties : aucun distracteur choisi par moins de 3 % des élèves (sinon il est trop évident et à remplacer).
- **Coût estimé :** environ 5 000 jetons par question (génération, contrôle aveugle, correction), soit **de l'ordre de 150 000 à 200 000 jetons pour le pilote**. À l'échelle des 1 063 questions du BEPC : environ 5 millions ; les maths de tous les cursus (2 712) : environ 13 millions. À phaser, comme la campagne de cours GCE.

## 5. Ce qu'il y a (et n'y a pas) à coder

- **Déjà là :** le quiz sait servir un QCM, donner le verdict immédiat, les points et le « Bravo ! » ; l'ingestion sait normaliser choix et clé ; la mise à jour sur place existe.
- **À écrire, petit :**
  - une commande de **contrôle des QCM** avant application (4 choix distincts, la clé est bien l'un d'eux, pas de doublon de texte, répartition des lettres) ;
  - un export des items à convertir, par thème, avec leur énoncé et leur corrigé, pour alimenter le skill.
- **À décider (pas du code) :** voir ci-dessous.

## 6. Décisions à prendre

1. **Convertir sur place ou ajouter à côté ?** Recommandé : sur place pour les questions à résultat unique (pas de doublon dans le quiz). Ajouter à côté garderait la version ouverte, mais le quiz mêlerait les deux sur la même compétence.
2. **Que devient la version ouverte quand elle est convertie ?** Elle disparaît du quiz (le corrigé complet reste dans les épreuves et les cours). C'est une perte assumée : la rédaction reste travaillée dans les épreuves et les exercices d'application.
3. **Étendre ensuite à la Physique et à la SVT ?** Seulement si le pilote tient ses critères.
4. **Faire relire par un vrai enseignant de maths ?** Le contrôle aveugle limite les clés fausses, mais ne juge pas le niveau BEPC des distracteurs. Un enseignant sur un échantillon de 10 questions avant de passer à l'échelle serait prudent.

## 7. Risques

- **Une clé fausse** : un élève qui a raison est puni et perd confiance. Mitigation : contrôle aveugle, puis échantillon relu par un enseignant, puis suivi des questions où presque tout le monde « se trompe ».
- **Un QCM qui se devine** par élimination : mitigation par des distracteurs d'erreurs réelles et une clé équilibrée.
- **Perte de la rédaction** dans le quiz : elle reste dans les épreuves et exercices d'application ; à dire clairement dans les notes de version.
- **Limites de la mesure** : les passes Guyguy sont simulées ; seules de vraies parties diront si les distracteurs fonctionnent.
