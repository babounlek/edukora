# Relecture enseignant : pilote de calibrage / Mathématiques / 8 questions

- Date : 2026-10-20 ; base locale (lecture seule) ; copie de travail hors dépôt
- Périmètre : 8 questions de la base locale, tirées au hasard avec une graine fixe : 4 questions ouvertes de maths francophones (Probatoire D 2008, 2009, 2012, 2013, choisies autonomes) et 4 QCM de GCE O Level Mathematics Paper 1 (2021, 2023, 2024, 2026). Échantillon d'essai, pas une relecture de lot.
- Mode d'exécution : **deux sous-agents à contexte neuf** : passe 1 (énoncés seuls, sans corrigé, sans clé), passe 2 (énoncés + solutions de la passe 1 + corrigés). L'agent principal a préparé les fichiers et connaissait les défauts semés ; il n'a rien relu lui-même.
- Calibrage : **deux défauts semés dans la copie des corrigés, jamais en base.**

## Défauts semés et résultat

| Défaut semé | Où | Retrouvé ? | Comment |
|---|---|---|---|
| Erreur de signe : `-3y_I = +3` devenu `-3`, donc m = 11/2 au lieu de 5/2 | P3 (Probatoire D 2009, ex. 2, q. 1) | **Oui, E1, confiance haute** | La passe 1 avait m = 5/2 ; divergence refaite à la main et par contrôle numérique (4x − 3y + 5 = 0 passe par I) ; correction proposée exacte |
| Clé de QCM décalée : b (230°) remplacée par c (130°), explication laissée à 230° | P4 (GCE O Level 2021, bearing) | **Oui, E1, confiance haute** | La passe 1 avait b ; la clé contredit l'explication du corrigé ; vérifié par vecteurs ; correction proposée exacte, avec l'erreur typique 130° = 180° − 50° |

**Taux de détection : 2 sur 2.** Faux positifs sur les 6 objets non touchés : **aucune E1, aucune E2**. Un constat E4 (P8) et une observation (P7) : ce sont de vrais points du contenu d'origine, voir plus bas.

## Constats sur le contenu d'origine (pas semés)

| Id | Gravité (selon moi) | Où | Constat |
|---|---|---|---|
| R1 | **E2** (le sous-agent l'a classé E4) | `catalog.Question` 67505, GCE O Level 2023 Paper 1 : « V inversement proportionnel à t », options a-d | L'option **d) `Vk = 1/t`** donne `V = 1/(kt)`, qui est aussi inversement proportionnelle à `t` avec la constante `1/k` : une deuxième option est défendable. La clé c reste la forme canonique `V = k/t`, mais l'explication (« not the standard form ») affirme que d n'est pas une variation inverse. Les deux passes l'ont signalé, indépendamment. À confier à `correction-experte` : reformuler l'option d, ou l'énoncé (« where k is the constant of proportionality »), ou les deux. |
| R2 | E4 | `catalog.Question` 49362, Probatoire D 2008, q. 3 | Le corrigé renvoie à « l'équation résolue en 2 » sans la reproduire alors que la question est affichée seule : un élève n'a pas la résolution de 2t² − (√2−1)t − √2/2 = 0 (Δ = (1+√2)², t = √2/2 ou −1/2). Ajouter une ligne rendrait le corrigé autonome. Le résultat est juste. |
| R3 | note | Probatoire D 2013, q. 1 (triangle) | « Nature » du triangle non précisée dans l'énoncé ; le corrigé conclut « rectangle en B » et ajoute BA ≠ BC, ce qui est bien. Rien à corriger. |

Concordances : P1, P2, P5, P6 entièrement concordants ; P7 et P8 concordants sur le résultat et la clé.

## Ce que le pilote apprend sur le skill

1. **Le protocole fonctionne** : la divergence entre la passe 1 (indépendante) et le corrigé a fait apparaître les deux défauts, y compris la clé de QCM, avec la preuve par le calcul et la correction.
2. **Un sous-agent ne charge pas toujours le skill** : le sous-agent de passe 2 n'a pas pu l'ouvrir (refus des deux noms) et a travaillé avec le seul brief. Corrigé dans le skill : le brief type de la passe 2 est maintenant écrit dans `references/protocole-resolution.md` (échelle de gravité, gabarit, règle E1/E2, fichiers, pas de « défaut semé » dans le brief). **`enseignant.skill` est à réinstaller** (copie dans ce dossier).
3. **Un second QCM défendable est une E2** : le sous-agent l'a classé E4, faute d'avoir la règle. Règle ajoutée à `SKILL.md` (gravité E2).
4. **Python de l'hôte** : le `python` du PATH Windows est le raccourci du Microsoft Store ; les calculs passent par le conteneur (`docker exec edukora-backend-1 python`) ou Node. Noté dans le protocole.

## Ce que ce pilote ne dit pas

- Deux défauts, tous deux **détectables par contradiction interne** (la clé contredit l'explication ; le calcul est refaisable en trois lignes). Un défaut plus subtil (hypothèse implicite fausse dans un long raisonnement, clé ET explication changées de façon cohérente, erreur de programme) n'a pas été testé : seule la passe 1 indépendante peut alors le trouver, et sa fiabilité dépend de la difficulté de l'exercice. À semer lors d'un deuxième calibrage sur des exercices plus longs (BAC C, A Level).
- Échantillon de 8 : le taux de faux positifs sur 6 objets n'a qu'une valeur indicative.
- Aucune relecture de cours, de quiz ou d'inédite (grilles de notation) dans ce pilote ; seules les questions et leurs clés ont été éprouvées.
- Les deux sous-agents ont lu leurs fichiers d'après une consigne : l'indépendance de la passe 1 repose sur cette consigne, pas sur une barrière technique.
- Ce rapport n'est pas une relecture scientifique officielle des 8 questions.

## Suite proposée (à la demande seulement)

- Confier R1 (et éventuellement R2) à `correction-experte`, puis réingestion par `tunnel-completude-edukora`.
- Deuxième calibrage avec des défauts plus subtils et des exercices de BAC C / A Level avant de s'en servir pour dire qu'un lot est propre.
- Première vraie relecture ciblée : les items `est_vitrine` de maths (quiz gratuits), les plus vus par les élèves.

## Correction de R1 appliquée (2026-10-20, non committée)

Item 67505 (GCE O Level 2023 Paper 1, question 35). L'option d est restée telle quelle (c'est le texte imprimé du sujet) ; c'est l'**énoncé** qui est précisé : « where k is a constant is » devient « where k is the constant of proportionality, is ». Avec k constante de proportionnalité de `V = k/t`, l'option d (`V = 1/(kt)`, constante 1/k) n'est plus défendable ; la clé c ne change pas. Le corrigé le dit : l'option A (`V = t/k`) et l'option B (`V = kt`) sont des variations directes ; la d a pour constante 1/k, pas k. Une ligne ajoutée aux `incertitudes` de l'exercice (écart avec le texte du sujet, source, date), comme le veut la règle « ne jamais déformer le sujet sans le dire ».

Appliqué à l'identique dans `backend/ingest/cm/gce-ol-maths-2023-p1-officiel-cameroun/..._exercice_1.json` (diff de 4 lignes) et dans la base locale (`Question` 67505 + `Exercise.incertitudes`). Aucun doublon de la question en base, rien dans l'index de recherche. **À rejouer en prod** : mettre à jour la même question (pas de réingestion complète nécessaire) ; une réingestion du JSON local reproduit déjà la correction.
