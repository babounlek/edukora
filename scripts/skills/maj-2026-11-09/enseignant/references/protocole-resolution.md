# Protocole de résolution indépendante

Pourquoi : si l'enseignant lit le corrigé avant de résoudre, il vérifie la cohérence INTERNE du corrigé (les étapes s'enchaînent bien) et pas sa JUSTESSE. Une erreur d'hypothèse au début d'un corrigé très bien enchaîné passe alors inaperçue.

## Deux temps, deux fichiers

1. **Fichier `enonce`** : énoncé (+ intro d'exercice), figures décrites ou jointes, barème annoncé, type de réponse, options d'un QCM **sans** la clé. Rien d'autre.
2. **Fichier `corrige`** : corrigé, clé (`reponse_correcte`), grille (`criteres_notation`), explication. Ouvert seulement après la passe 1 terminée et écrite.

Champs à NE PAS donner pendant la passe 1, ni la passe 2 si l'on veut rester indépendant du raisonnement de l'auteur : `Exercise.incertitudes` (les doutes de l'auteur : à lire en passe 2 seulement, ils orientent la vérification), `score_originalite` et `score_qualite` des épreuves inédites (notes de l'auteur sur son propre travail : ne jamais s'en servir comme preuve).

## Passe 1 : résoudre

- Résoudre de zéro, comme l'élève le plus fort du niveau. Écrire la solution en entier, pas « je vois que ça donne 3 ».
- QCM : trouver la clé SANS regarder les options d'abord quand c'est possible (calculer, puis chercher l'option), puis éliminer chaque distracteur en disant pourquoi il est faux. Si deux options sont défendables ou aucune n'est juste, c'est un constat (E1 si la clé est fausse, E2 si l'énoncé est ambigu).
- **Vérifier chaque nombre par un calcul indépendant** (autre méthode ou autre ordre : valeur numérique, calcul exact avec `fractions`/`decimal`, dérivée par différences, ordre de grandeur). Un résultat vérifié une seule fois par la même voie n'est pas vérifié.
- Noter pendant la résolution tout ce que l'énoncé ne dit pas : donnée manquante, hypothèse implicite, unité absente, vocabulaire hors programme, cote illisible sur une figure, consigne qui admet deux lectures.
- Pour une dissertation, un commentaire, une rédaction : pas de « bonne réponse » unique. Établir à la place la liste des **attendus** d'un correcteur (problématique, notions à définir, auteurs ou œuvres du programme, structure imposée) et juger le corrigé sur ces attendus.

## Passe 2 : comparer

Pour chaque résultat : égal, différent, ou égal sous une autre forme (vérifier l'équivalence avant de conclure).

En cas de **divergence**, refaire le calcul par une troisième voie avant de décider qui a tort. Trois sorties :
- l'enseignant a tort → le noter comme « concordant après revérification » (utile pour calibrer) ;
- le corrigé a tort → constat E1 avec le calcul complet ;
- impossible de trancher (énoncé ambigu, donnée manquante) → constat E2, confiance « moyenne » ou « faible », avec les deux lectures.

Ne jamais déclarer une E1 sur la seule foi d'un désaccord : l'enseignant se trompe aussi.

## Sous-agent à contexte neuf (recommandé)

Quand l'outil Agent est disponible, la passe 1 se fait dans un sous-agent : son brief contient UNIQUEMENT les énoncés extraits, la matière, le niveau, le système (francophone ou GCE) et l'instruction de résoudre et de vérifier par le calcul. Il renvoie ses solutions et ses doutes sur l'énoncé. L'agent principal lit alors le corrigé et fait la passe 2. Le brief ne contient ni le corrigé, ni les `incertitudes`, ni l'historique de la session, ni le nom du skill auteur.

Sans Agent : écrire les solutions dans un fichier de travail AVANT d'ouvrir le fichier `corrige`, et le dire dans le rapport (« indépendance auto-imposée »).

## Calcul : outils

- Le conteneur backend a Python mais pas `sympy` : utiliser `fractions.Fraction`, `decimal.Decimal`, `math`, des boucles de contrôle numérique. Ne rien installer sans demande.
- Pour une limite, une dérivée, une intégrale : contrôle numérique à plusieurs valeurs, et recalcul par une seconde méthode.
- Pour la chimie : équilibrer l'équation et vérifier la conservation des éléments par un petit script avant de refaire la stœchiométrie.
- Pour une figure : contrôler cotes, légendes, cohérence avec le texte ; ne pas affirmer qu'elle est « fausse » à l'œil sans une valeur lisible à opposer.

## Brief type d'un sous-agent (les sous-agents ne chargent pas toujours ce skill)

Constaté au pilote du 2026-10-20 : un sous-agent n'a pas pu charger le skill et a appliqué seulement le brief. Le brief de passe 2 doit donc **contenir lui-même** l'essentiel :
- l'échelle de gravité (E1 erreur prouvée par le calcul ; E2 ambigu, deux réponses défendables, hors programme ; E3 pédagogique ; E4 forme) et la règle « jamais d'E1 sans calcul, une divergence non tranchée est une E2 » ;
- la règle « un QCM dont deux options sont défendables est une E2 (énoncé ambigu), pas une E4 » ;
- le gabarit de constat (identifiant, gravité, type, localisation, contenu actuel, ce que l'enseignant trouve, preuve, correction proposée, confiance) ;
- les trois fichiers à lire dans l'ordre (énoncés, solutions de la passe 1, corrigés) et l'interdiction d'en ouvrir d'autres ;
- le fait que le lot peut contenir zéro, un ou plusieurs défauts.
Ne pas mentionner de « défaut semé » dans le brief, même pendant un calibrage.

## Outils de calcul sur cette machine

Le `python` de l'hôte Windows est le raccourci du Microsoft Store : il ne tourne pas. Pour les calculs : `docker exec edukora-backend-1 python -c "..."` (Python sans `sympy`), ou Node, ou le Python complet s'il est installé (`.../Python314/python.exe`).
