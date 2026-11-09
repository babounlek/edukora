# Gabarit de rapport

Fichier : `docs-relecture/enseignant/AAAA-MM-JJ-<matiere>-<cible>.md` (cible : `corriges`, `cours`, `quiz`, `inedite`, ou le slug de l'épreuve).

```markdown
# Relecture enseignant : <matière / niveau> / <cible> / <périmètre>

- Date : AAAA-MM-JJ ; base locale ; commit : <hash>
- Périmètre : <ex. 12 exercices de Maths BAC C 2019-2023> ; échantillon : <règle et taille> sur <population>
- Système : francophone | GCE ; examen/série ou matière/paper : ...
- Mode d'exécution : sous-agent à contexte neuf pour la passe 1 | agent principal (indépendance auto-imposée)
- Calibrage : défaut semé retrouvé ? oui | non | non testé (voir ci-dessous)

## Verdict
Une phrase : « N objets relus, X concordants, Y constats (E1 : a, E2 : b, E3 : c, E4 : d) ». Puis : prêt à publier | à corriger avant publication | à reprendre.

## Concordances
Ce qui a été refait et qui est juste (identifiants). C'est le dénominateur du rapport.

## Constats
| Id | Gravité | Type | Localisation | Contenu actuel | Ce que trouve l'enseignant | Preuve | Correction proposée | Confiance | Statut |
|---|---|---|---|---|---|---|---|---|---|
| C1 | E1 | clé fausse | `inedit.QuestionInedite` 5123, Q17 | clé « c » | clé « b » : 3/4 + 1/4 = 1, donc ... | calcul complet ou script | « b » ; explication : ... | élevée | nouveau |

Type : résultat faux, clé fausse, définition fausse, énoncé ambigu, donnée manquante, hors programme, niveau inadapté, barème incohérent, grille inutilisable, étape notée absente, rédaction non conforme, notation, orthographe/registre, originalité.
Confiance : élevée (recalculé par deux voies, ou évident) | moyenne | faible (désaccord non tranché). Une confiance faible n'est jamais classée E1.
Statut : nouveau | déjà connu | régression.

## Défauts semés (calibrage)
Ce qui a été semé dans la copie de travail, ce qui a été retrouvé, ce qui a été manqué. Un défaut manqué = relecture à refaire plus strictement avant de conclure.

## Propositions
Classées par gravité puis par effort : corrections à confier à `correction-experte`, ré-ingestion par `tunnel-completude-edukora`, trous de programme à signaler à `audit-couverture-programme`. Aucune action sans demande de l'utilisateur.

## Ce que cette relecture ne dit pas
Adapter la liste de SKILL.md : pas un enseignant de la discipline ; échantillon et taux ; ce qui ne se calcule pas ; barèmes officiels connus seulement par la base.
```

## Règles de rédaction

- Un constat = un fait refaisable. Écrire le calcul, pas « le résultat semble faux ».
- Ne jamais écrire « le corrigé est mauvais » : écrire quelle ligne, quelle valeur, quelle règle.
- Pas de gonflement : un rapport sans E1 est un bon rapport. Une E1 non prouvée est une E2.
- Citer l'identifiant (modèle + id, ou chemin JSON + clé) et l'extrait minimal ; ne pas recopier des pages d'annale.
- Les propositions de correction sont du texte prêt à reprendre, dans la langue du contenu et au niveau du cursus.
