# Pilote B1 : 25 QCM de maths BEPC proposés (rien n'est appliqué en base)

Date : 2026-10-26. Cadrage : `docs-relecture/eleve/2026-10-26-B1-qcm-maths-cadrage.md`.

## Ce qui a été fait

- **Périmètre :** les questions ouvertes de maths BEPC des 6 thèmes les plus fréquents (Identité remarquable, Statistiques, Factorisation, Radicaux, Triangle rectangle, Repère orthonormé) : 34 items, dont 3 avec figure (laissés de côté).
- **31 items sans figure examinés, 25 convertis en QCM, 6 non convertis** (voir plus bas).
- Chaque QCM : 1 bonne réponse, 3 mauvaises réponses tirées d'erreurs d'élèves réelles (la raison de chacune est écrite dans la section « Pourquoi les autres réponses sont fausses » du corrigé), corrigé d'origine conservé (Rappel de méthode puis Corrigé). Clés réparties : a = 7, b = 5, c = 6, d = 7.
- **Chaque valeur numérique est recalculée par code** avant d'être écrite (`genere_qcm.py`, assertions).

## Contrôles

| Contrôle | Résultat |
|---|---|
| Forme : 4 choix distincts, clé présente, structure du corrigé, `$` équilibrés, pas de tiret cadratin, pas de caractère de contrôle | OK sur 25 |
| Rendu avec la chaîne réelle du lecteur (remark-math, gfm, breaks, rehype-katex), 626 formules | 0 erreur, 0 `$` brut |
| Décimales dans les formules (`5,4` affiché « 5, 4 ») | corrigées en `5{,}4` (item 2685) ; 0 restante |
| **Relecteur indépendant sans clé** (3 passes : 26 + 12 + 13 questions, soit les 25 questions finales) | **25 réponses sur 25 identiques aux clés** ; aucune question avec plusieurs bonnes réponses ni sans bonne réponse |

Défauts trouvés par le relecteur, tous corrigés avant livraison :
- **1477 (médiane)** : la 5e valeur de la liste non rangée était déjà 26, donc un élève qui oubliait de ranger trouvait quand même la bonne réponse. Liste réordonnée ; nouveaux distracteurs « 22 » (5e valeur non rangée) et « 28,5 » (milieu des extrêmes).
- **1479 (quartiles)** : convention de calcul non précisée. Elle est maintenant rappelée dans l'énoncé.
- **2869** : choix mélangeant coordonnées et conclusion, ambigu. Question reformulée : « Que peut-on affirmer du triangle PQR ? » (rectangle en Q par la réciproque de Pythagore). **Cette reformulation n'a pas été relue à l'aveugle** (elle a été recalculée par code) : à faire valider par l'enseignant.
- 7 distracteurs jugés faibles remplacés par des erreurs plus réalistes (2554, 2676, 2675, 1177, 3344, 3345, 2685, 2868).
- Rendu : virgules décimales protégées ; « classe de 4e » remplacé par « 3e » dans l'item 1476 ; unité ajoutée à l'item 2870.

Restent (mineurs, relevés par le relecteur) : 3345, distracteur « 27 » (effectif total) peu crédible ; 1177 un peu facile (deux divisions) ; 1176, la forme `(2x+5)(-2x-5)` n'est pas proposée comme choix (l'élève doit reconnaître `-(2x+5)^2`) ; 2673, tournure maladroite « b le plus petit entier naturel possible » conservée de l'original.

## Les 6 items NON convertis : à décider

Ils sont classés BEPC mais ne semblent pas de ce niveau (avis du relecteur indépendant pour 1480 et 1479, constat de contenu pour les autres). Je ne les ai pas convertis : le sujet est de retirer ou non ces questions du cursus BEPC, pas de les mettre en QCM.

| Item | Thème | Pourquoi |
|---|---|---|
| 1178 | factorisation | équation de degré 3 résolue par discriminant |
| 1179 | factorisation | application du plan, colinéarité de vecteurs (niveau Terminale) |
| 1180 | factorisation | coût marginal, étude de signe par discriminant |
| 1181 | factorisation | nombres complexes (Terminale) |
| 1480 | statistiques | série à deux variables et point moyen (second cycle) |
| 1481 | statistiques | variance et formule de König (second cycle) |

À part : **1479 (quartiles)** est converti mais son niveau est « en limite haute de la 3e » ; à confirmer.

## Pour appliquer (seulement avec ton accord)

```bash
docker cp docs-relecture/b1-pilote/propositions.json edukora-backend-1:/tmp/b1_propositions.json
docker cp docs-relecture/b1-pilote/appliquer_qcm.py edukora-backend-1:/tmp/appliquer_qcm.py
# simulation (rien n'est écrit) :
docker compose -f docker-compose.yml exec -T backend python manage.py shell -c "import os; os.environ['B1_JSON']='/tmp/b1_propositions.json'; exec(open('/tmp/appliquer_qcm.py', encoding='utf-8').read())"
# application réelle : ajouter os.environ['B1_APPLIQUER']='1'
```

Garde-fous du script : il ne touche que les items encore ouverts et validés ; il ne modifie jamais le statut, le quiz gratuit (`est_vitrine`), le thème, le cursus ni les figures ; l'historique des élèves est protégé par l'instantané des quiz déjà joués. La simulation a été lancée : 25 items à appliquer, 0 ignoré, **base intacte**.

## Limites

- Les relecteurs sont des modèles : l'accord à 25/25 limite les clés fausses mais ne remplace pas un enseignant de maths sur le niveau BEPC des distracteurs.
- Le suivi réel (distracteur choisi par moins de 3 % des élèves) ne se voit qu'après de vraies parties.
