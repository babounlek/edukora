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
| 2026-10-25 | Guyguy (3e, orienté fun) | M1+M2+M3 visiteur | local | 8be75ff7 | 3 | 2 | 3 | peut-être | 5 | peut-être (parents) | Q4 QCM « Bravo ! » et corrigé 2026 libre (+1) | arrivée en anglais, mur de texte Q1 (-1) | 2026-10-25-guyguy-visiteur-M1-M2-M3-local.md |
| 2026-10-26 | Guyguy (3e, orienté fun) | M2 visiteur, Identité remarquable (après B1 pilote + A1-A7 + lot B) | local | e377a4a6 + B1 non commité | 4 | 2 | 3 | cette semaine | 6 | peut-être (parents) | série « tu es en feu », 5/5 avec confettis et record (+2) | fenêtres avant la 1re question, correction trop longue après une erreur (-1) | 2026-10-26-guyguy-visiteur-M2-identite-remarquable-local.md |
| 2026-10-25 | Guyguy (3e, orienté fun) | M8+M4+M5 abonné | local | 8be75ff7 | 3 | 3 | 3 | cette semaine | 5 | sans objet | résultat du quiz, +37 points (+2) | résultat inédite « 0,5 / 20 » (-2) | 2026-10-25-guyguy-abonne-M8-M4-M5-local.md |
| 2026-11-02 | Guyguy (3e) | M1+M2+M3+M6 visiteur (sciences, SVT, prix) | local | 3b818788 | 3 | 3 | 2 | peut-être | 5 | peut-être (parents) | QCM CO2, « Tu maîtrises ! » + mascotte (+2) | corrigé SVT payant (-1) | 2026-11-02-guyguy-visiteur-M1-M2-M3-M6-local.md |
| 2026-11-02 | Guyguy (3e) | M8+M4+M5 abonné (chrono, mini-inédite) | local | 3b818788 | 4 | 2 | 3 | demain | 6 | sans objet | objectif du jour atteint +10 (+2) | envoi du code 20 s, fin du quiz chrono (-1) | 2026-11-02-guyguy-abonne-M8-M4-M5-local.md |
| 2026-11-02 | Guyguy (3e) | M3 + murs payants, compte libre | local | 3b818788 | 3 | 3 | 3 | cette semaine | 5 | peut-être (parents) | quiz Maths +10 (+2) | rien pour convaincre les parents (-1) | 2026-11-02-guyguy-libre-M3-paywalls-local.md |
| 2026-11-07 | Guyguy (3e) | M1+M2+M3+M6 visiteur (maths, physique, épreuve, prix) | local | 14dd5ee1 | 4 | 2 | 3 | peut-être | 7 | peut-être (parents) | résultat du quiz de maths, +30 points (+2) ; corrigé 2026 gratuit (+2) | physique : exercices longs puis « +0 points » (-1) | 2026-11-07-guyguy-visiteur-M1-M2-M3-M6-local.md |
| 2026-11-07 | Guyguy (3e) | M8+M4+M5 abonné (reprise, cours PCT, mini-inédite, chrono) | local | 14dd5ee1 | 3 | 3 | 3 | cette semaine | 6 | sans objet | chrono en cours conservé, « Reprendre » (+2) | recherche « electricite » sans résultat (-2) | 2026-11-07-guyguy-abonne-M8-M4-M5-local.md |
| 2026-11-07 | Guyguy (3e) | M1+M2+M3+M10+M6 visiteur (histoire-géo, hors ligne, prix) puis compte libre (quiz, cours Pythagore) | local | 31e85dc6 | 4 | 2 | 3 | cette semaine | 6 | peut-être (parents) | corrigé Histoire BEPC 2025 gratuit complet ; recherche sans accent puis cours Pythagore (+2) | « Débloquer ma séance » tout grisé ; « Lire sans réseau » en échec (-1) | 2026-11-07-guyguy-visiteur-libre-M1-M2-M3-M10-M6-passe2-local.md |
| 2026-11-07 | Guyguy (3e) | M4+M5+M8 abonné (cours Thalès, inédite de maths BEPC n°3, reprise) | local | 31e85dc6 | 4 | 2 | 3 | cette semaine | 6 | sans objet | quiz de Thalès « tu montes » + mascotte ; « pytagore » corrigé en « pythagore » (+2) | bilan de l'inédite « tu as perdu 18,5 points » ; accueil au retour (-1) | 2026-11-07-guyguy-abonne-M4-M5-M8-maths-passe2-local.md |
| 2026-11-07 | Nadège (Tle C, BAC C) | M1+M2+M3+M6 visiteur (maths/physique BAC C, quiz, prix) puis compte libre (cours suites, paywall, progression) | local | 7835795d | 4 | 2 | 3 | cette semaine | 7 | peut-être (parents) | corrigé gratuit Maths BAC C 2026, calculs justes ; recherche « limites de suites » (+2) | quiz gratuit trop facile, tableaux coupés (-1) | 2026-11-07-nadege-tleC-visiteur-libre-M1-M2-M3-M5-M6-local.md |
| 2026-11-07 | Nadège (Tle C, BAC C) | M5+M4+M8 abonnée (inédite maths BAC C et E n°1, complexes, physique, progression, reprise) | local | 7835795d | 4 | 2 | 3 | cette semaine | 6 | sans objet | reprise du chrono dès l'accueil + grille « Note ta réponse » (+2) | recherche « Aucun cours ne correspond » ; quiz de complexes trop facile (-1) | 2026-11-07-nadege-tleC-abonnee-M5-M4-M8-local.md |

## Calibrage de la satisfaction (2026-10-24)

Scénario : rejeu de l'abandon à la saisie du code du 2026-10-19 (`2026-10-19-gogo-gce-ol-connexion-local.md`) par un persona neuf, qui n'a lu aucun rapport. Le code part vers une boîte que le persona ne peut pas lire, comme avec la boîte du parent absent.

Résultat : **calibrage réussi.** Abandon à 3 min 50 s (4 min dans la session d'origine). Q1 = 2 (≤ 2), Q2 = 4 (≥ 4), Q4 = « peut-être » (jamais « demain »), Q5 = 3 (≤ 4), plafonds respectés, notes ancrées sur le journal, pic modeste (+1) et fin à -2.

Écart relevé : le §6 de la méthode exigeait « je ne reviens pas », plus strict que le tableau des plafonds du §3. Le §6 est aligné sur le §3 (un « peut-être » est accepté s'il cite un motif réaliste).

Côté frictions, le rejeu retrouve les mêmes défauts que la session d'origine (aucune aide quand la boîte est celle d'un parent, envoi du code lent, accueil en français pour un élève du GCE) et en trouve deux de plus : un renvoi qui échoue en 503 après 25 s, puis un refus 429, avec des messages **en français** sur une page anglaise.
