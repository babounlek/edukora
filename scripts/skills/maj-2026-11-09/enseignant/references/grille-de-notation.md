# Relire une grille de notation et un barème

Dans edukora, une réponse ouverte n'est PAS notée automatiquement : l'élève s'auto-évalue en cochant des critères (`QuestionInedite.criteres_notation`), ou saisit des points par quarts quand la question n'a pas de critères. Les points d'un QCM sont tout ou rien sur la clé. La qualité de la correction vécue par l'élève dépend donc de la qualité de la grille et du barème, pas d'un algorithme : c'est là que l'enseignant est le plus utile côté « correction ».

Règles de calcul du produit (lire `backend/inedit/notation.py`, docstring en tête) : dénominateur = barème complet, questions non traitées incluses ; barème d'une question = `points`, ou somme de ses critères, ou barème annoncé dans l'énoncé, ou répartition égale (signalée « barème estimé »).

## Ce qu'une bonne grille respecte

- **Critères observables** : l'élève peut cocher oui ou non en relisant sa copie à côté du corrigé. « Applique correctement la dérivée du produit » se coche ; « comprend la notion » ne se coche pas (E2).
- **Atomiques et indépendants** : un critère = une idée. Deux étapes dans un même critère, ou un critère qui dépend d'un autre déjà échoué, fausse l'auto-évaluation (E3).
- **Somme exacte** : la somme des points des critères = `points` de la question, et la somme des questions = points de l'exercice = barème annoncé. Refaire ces sommes en `Decimal` (E1 si le total affiché à l'élève est faux).
- **Proportionnés** : un critère à 0,25 point pour une étape triviale et 0,25 pour la conclusion qui concentre le raisonnement déséquilibre la note (E3). Comparer avec l'usage d'un corrigé d'examen de la même matière.
- **Alignés sur le corrigé** : chaque critère correspond à un passage du corrigé ; chaque étape notée par un correcteur d'examen (résultat avec unité, justification, énoncé du théorème) a son critère (E3 si une étape notée manque).
- **Pas de double peine** : une erreur de calcul au début ne doit pas faire perdre tous les critères suivants qui reposent sur la valeur fausse quand la méthode reste juste (convention « erreur reportée » : à signaler si la grille ne la prévoit pas).
- **Langue et niveau** : formulation claire pour un élève du niveau (GCE : anglais simple ; francophone : tutoiement ou impersonnel cohérent avec le reste).

## QCM

- Une seule option correcte ; clé = option réellement correcte (refaire le calcul).
- Distracteurs plausibles : correspondent à des erreurs fréquentes (signe, oubli de conversion, formule voisine), pas à des absurdités qui s'éliminent sans savoir.
- Pas d'indice dans la forme : option correcte systématiquement la plus longue, la seule avec un qualificatif, toujours en même position sur le lot (statistiquement : une répartition très déséquilibrée des lettres correctes d'un Paper 1 est un signal E3).
- Aucune option « toutes les réponses » / « aucune » sans nécessité.
- Pour un QCM issu d'une annale où l'option correcte n'existe pas : voir `conventions-par-systeme.md` (question ouverte).

## Barème global d'une épreuve inédite

- Total = `Blueprint.bareme_total` (en général 20 pour une épreuve francophone) ; si l'épreuve est de type GCE, total = somme des points imprimés du paper.
- Répartition cohérente avec la durée et la difficulté étiquetée : pas 12 points sur le dernier exercice le plus court.
- Barème « estimé » (répartition égale) : à signaler à l'auteur comme à améliorer en barème explicite, c'est visible de l'élève.
