# Suivi de la satisfaction (skill `eleve`)

Une ligne par session, jamais d'effacement. Méthode, échelles et plafonds : `references/satisfaction.md` du skill `eleve`.

Lecture : Q1 satisfaction de la mission (1-5) · Q2 effort (1 facile - 5 pénible) · Q3 utilité (1-5) · Q4 retour (demain / semaine / peut-être / non) · Q5 recommandation (0-10) · Q6 achat (oui / peut-être / non / sans objet). Pic et creux : humeur de -2 à +2 avec l'étape.

Règles de comparaison : un écart d'un point sur une seule session est du bruit ; deux points, ou un changement de verdict de mission, est un signal. Comparer toujours au même persona x même mission.

C'est une satisfaction **simulée** : un indice relatif pour repérer des creux et des régressions, pas la satisfaction réelle d'élèves. La rétention réelle se lit dans `analytics`.

## Synthèse

(à écrire tous les trois à cinq rapports : moyennes par persona et par mission, trois pires creux, trois meilleurs pics)

## Sessions

Les sessions du 2026-10-19 au 2026-10-24 ont été jouées **avant** l'ajout de la satisfaction au skill : elles n'ont pas de note et ne servent pas de point de comparaison.

| Date | Persona | Mission | Terrain | Commit | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Pic | Creux | Rapport |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24 | Gogo (calibrage) | connexion e-mail familial, code non reçu | local | f245a953 | 2 | 4 | 1 | peut-être | 3 | sans objet | étapes 3-4 (+1) | étapes 8-9 (-2) | 2026-10-24-calibrage-satisfaction-gogo-connexion-local.md |

## Calibrage de la satisfaction (2026-10-24)

Scénario : rejeu de l'abandon à la saisie du code du 2026-10-19 (`2026-10-19-gogo-gce-ol-connexion-local.md`) par un persona neuf, qui n'a lu aucun rapport. Le code part vers une boîte que le persona ne peut pas lire, comme avec la boîte du parent absent.

Résultat : **calibrage réussi.** Abandon à 3 min 50 s (4 min dans la session d'origine). Q1 = 2 (≤ 2), Q2 = 4 (≥ 4), Q4 = « peut-être » (jamais « demain »), Q5 = 3 (≤ 4), plafonds respectés, notes ancrées sur le journal, pic modeste (+1) et fin à -2.

Écart relevé : le §6 de la méthode exigeait « je ne reviens pas », plus strict que le tableau des plafonds du §3. Le §6 est aligné sur le §3 (un « peut-être » est accepté s'il cite un motif réaliste).

Côté frictions, le rejeu retrouve les mêmes défauts que la session d'origine (aucune aide quand la boîte est celle d'un parent, envoi du code lent, accueil en français pour un élève du GCE) et en trouve deux de plus : un renvoi qui échoue en 503 après 25 s, puis un refus 429, avec des messages **en français** sur une page anglaise.
