# Session élève : Gogo / épreuve inédite English Language (paper blanc partagé) / local

- Date : 2026-10-20 (heures UTC non relevées par le sous-agent ; fin vers 12 h locale, session d'environ 20 min)
- Terrain : local ; commit local : 9adaece5 (plus les changements non committés du message du code parent) ; URL de départ : `http://localhost/en/cm/mock-papers/english-language-gce-o-level-paper-1-original-paper-no-1`
- Persona : Gogo (Form 5, GCE O Level, Bamenda, interface anglaise), compte déjà connecté, abonnement actif « Original papers included » ; **appareil : bureau 1920x945** (l'émulation mobile 375x812 n'a pas pris dans Chrome : `innerWidth` resté à 1920)
- Mode d'exécution : **sous-agent à contexte neuf** (sans accès au code, à la base ni aux rapports précédents), piloté dans Chrome
- Calibrage : non testé cette session (méthode inchangée depuis les rapports Gogo précédents)

## Verdict de mission
**Réussie avec effort.** Gogo comprend que c'est un paper maquette d'EduKora de 90 min et 50 QCM, le passe en « Real conditions », le quitte puis le reprend sans perte, rend sa copie (22 réponses, **19 / 50 = 7,6 / 20, 38 %**), relit les corrections et suit le lien vers son parcours. Il retient sa note et que des thèmes reviennent « demain ». Mais il n'a **jamais su ce que son accès inclut** et il est déstabilisé par le « prochain pas » du parcours.

## Journal (extrait)
1. Page du lien partagé : titre, badge « Original paper », « Indicative duration: 90 min », « 1 exercise », « written by EduKora, never taken from past papers ». Trois cartes de mode (Real conditions, On paper, Free practice). Je ne vois ni « gratuit / compris dans mon accès », ni le nombre de questions dans l'en-tête.
2. Sous les cartes : consigne, texte d'écoute entier, question 1 ; « The rest of the paper stays unseen until you start it ». Pas de bouton « Start » : on démarre en cliquant une carte.
3. Fenêtre « Sit the paper under real conditions? » : « The 1 h 30 timer starts straight away and does not stop. » Boutons « Not now » / « Start the timer ». Je démarre.
4. Épreuve : en-tête collant (minuteur 1:29:52, « 0 / 50 completed », « Finish paper », « PDF »), grille des 50 questions à droite. Chargement immédiat.
5. Q1-10 (listening, texte d'écoute affiché en entier) : sélection instantanée, aucun indice juste/faux. Préfixe « (Listening passage in question 1, Section One) » répété.
6. Drapeau « flag for review » sur Q8 : fonctionne, mais minuscule.
7. Q11-18 (lecture, 6 paragraphes) : le texte est attaché à la question 11 et défile hors de l'écran ; je remonte pour relire.
8. Saut par la grille vers Q29 : la question se place bien sous l'en-tête. 22 réponses au total.
9. « Leave the paper » : « The timer keeps running… Everything you've ticked is kept… » Je quitte.
10. Catalogue : la carte dit « Resume the paper ». 11. Reprise : « Timer running: 1:25:29 left », réponses et drapeau intacts.
12. « Finish paper » : « 22 questions of 50 », « 28 not completed are worth 0 points », liste des numéros non faits, « 1 question flagged ». Je rends la copie.
13. Correction : « Marking finished · your mark: 19 / 50 ». 14. Bilan : 19/50, 7,6/20, 38 %, « Time used: 34:33 », deux libellés français, tableau « Result by skill » (22 compétences), « What you'll see again » (18 thèmes « tomorrow »).
15. Relecture : bonnes réponses en vert, mon choix faux en rouge ; aucune explication.
16. « See my path » : Mastered 1 / In revision 17 / To discover 147. 17. Parcours English : « Start by finding your level. You haven't tried anything on this exam yet… » juste après un paper de 50 questions.

## Ce qui marche bien (à ne pas casser)
- Parcours complet fluide : choisir un mode, démarrer, répondre, quitter, reprendre, rendre, relire, suite.
- Les trois fenêtres de confirmation (démarrer, quitter, rendre) : elles disent ce qui se passe avec le minuteur, ce qui est conservé, quelles questions manquent et lesquelles sont marquées.
- En-tête collant (minuteur, progression, « Finish paper ») et grille de questions toujours visibles ; reprise fiable (réponses, drapeau, minuteur).
- Aucune correction pendant l'épreuve, fidèle à l'examen ; note ramenée sur 20 avec l'explication « 28 not completed counted as 0 points ».
- Liens directs du bilan vers Quiz et Lessons par thème ; « My progress » est alimenté par le paper.

## Frictions
| Id | Sév. | Catégorie | Étape | Observé | Attendu | Preuve | Confiance | Statut |
|---|---|---|---|---|---|---|---|---|
| E-F1 | S2 | langue | Bilan | « Where your points went » affiche « Questions non traitées » et « Cause non précisée » en français | Libellés anglais | texte du bilan | élevée | nouvelle |
| E-F2 | S2 | fonctionnel | Bilan | « Time used: 34:33 » alors que le minuteur est passé de 1:29:52 à 1:24:43 (~5 min) et que le bloc « Your time » dit « 4 min » : trois temps incohérents | Un seul temps cohérent | texte du bilan, valeurs du minuteur | moyenne | nouvelle |
| E-F3 | S2 | contenu/UX | Parcours English | « You haven't tried anything on this exam yet - a 20-question placement test… » juste après un paper de 50 questions rendu et « 12 to review » | Prochain pas qui tient compte du paper fait | texte de la page | élevée | nouvelle |
| E-F4 | S2 | langue | Parcours English | Titre de section « Les thèmes qui reviennent le plus à l'examen » en français | Titre anglais | texte de la page | élevée | nouvelle |
| E-F5 | S2 | confiance/vente | Page de l'épreuve | Rien ne dit si l'épreuve est gratuite ou comprise dans l'accès (seul indice : cadenas ouvert dans le catalogue) | Une ligne « Included in your plan » / « Free preview » avant de démarrer | page d'arrivée | moyenne (compte abonné ; écran d'un non-abonné non vu) | proche de R-F8 (« ce que couvre l'abonnement ») |
| E-F6 | S3 | UX | Bilan | 16 compétences à « 0 / 1 » sont des questions non faites, mêlées aux vraies erreurs ; les 18 thèmes « tomorrow » viennent surtout des non-faites (3 réponses fausses seulement) | Séparer erreurs et non-faites ; ne programmer en révision que les thèmes réellement manqués | texte du bilan | moyenne | nouvelle |
| E-F7 | S3 | UX | Relecture | La grille marque toutes les questions traitées de la même couleur ; il faut ouvrir chaque question pour trouver les rouges | Grille juste / fausse / non faite, filtre « mes erreurs » | captures | élevée | nouvelle |
| E-F8 | S3 | contenu | Relecture | Aucune explication du « pourquoi » : seules les bonnes réponses sont cochées | Courte explication par question (au moins pour les fautes) | recherche de texte, rien trouvé | moyenne | nouvelle |
| E-F9 | S3 | contenu/UX | Q11-25 | Le texte de lecture est attaché à la question 11 et défile hors de l'écran | Texte fixe ou repliable à côté des questions, ou « retour au texte » | captures | élevée en bureau ; mobile non testé | nouvelle |
| E-F10 | S3 | UX | Épreuve | Libellés « Ex. 1 · Q19 » pour un paper à un seul exercice ; la grille saute 19-25 sans signal quand on va à Q29 | « Q19 » simple | captures | moyenne | nouvelle |
| E-F11 | S4 | UX | Fenêtre « Real conditions » | « …then tick each question completed » inadapté à un QCM | « …then pick your answer » | texte de la fenêtre | élevée | nouvelle |
| E-F12 | S4 | accessibilité | Épreuve | Option choisie (fond vert pâle, bordure fine) proche de l'état survol ; pastille du drapeau minuscule | Contraste plus net | captures | moyenne | nouvelle |
| E-F13 | S4 | langue | Épreuve | « Finish  paper » (double espace) ; options « a) » dans l'aperçu mais « A. » dans l'épreuve ; préfixe « (Listening passage…) » répété sur chaque question | Typographie homogène | texte et captures | moyenne | nouvelle |
| E-F14 | S4 | UX | Relecture | Une question non traitée n'affiche pas « Not answered » | Mention explicite | capture Q19 | moyenne | nouvelle |
| E-F15 | S4 | contenu | Bilan vs parcours | 18 thèmes « tomorrow » au bilan, 12 « to review » pour English dans le parcours | Chiffres cohérents ou expliqués | deux écrans | faible | nouvelle |
| E-F16 | — | outil | — | Émulation mobile 375x812 sans effet dans Chrome | — | `innerWidth` 1920 | élevée | limite du test |

## Mesures
- Page d'arrivée (bureau, cache chaud, non représentatif d'une 3G) : 89 ms, 63 requêtes, ~17 Ko transférés (~1,8 Mo décodés). Aucune erreur console relevée (suivi démarré après le chargement initial).
- Épreuve : environ 2 clics par question, aucune latence perceptible ; ~16 000 caractères de page pour 50 questions et 2 textes.
- Résultat : 19/50, 3 réponses fausses sur 22 (Q3, Q15, Q31), 28 non traitées.

## Idées d'amélioration (classées effet / effort)

**1. Effet élevé, effort faible (à faire d'abord)**
- **Traduire les libellés français du bilan et du parcours** (E-F1, E-F4) : « Questions non traitées », « Cause non précisée », « Les thèmes qui reviennent le plus à l'examen ». Même famille que les restes de langue déjà corrigés ailleurs ; un balayage des clés servies par le serveur dans les résultats d'épreuve inédite serait utile.
- **Dire sur la page de l'épreuve ce qui est inclus** (E-F5) : une ligne « Included in your plan » pour l'abonné, « Free preview / Unlock with… » pour un visiteur, avant le choix du mode.
- **Corriger la phrase « tick each question completed »** (E-F11) et la typographie (E-F13).
- **Afficher « Not answered » en relecture** (E-F14).

**2. Effet élevé, effort moyen**
- **Un prochain pas qui tient compte du paper rendu** (E-F3) : après une épreuve, le parcours doit proposer « Revise your weak topics » ou « Retry only what you missed », pas un test de placement comme si rien n'avait été fait.
- **Relecture orientée erreurs** (E-F7, E-F6) : grille colorée juste / fausse / non faite, filtre « mes erreurs », et dans le bilan séparer les non-faites des fautes. Ne programmer « tomorrow » que les thèmes réellement manqués (sinon un élève qui rend à moitié se voit imposer 18 thèmes).
- **Un temps unique et cohérent** (E-F2) : établir une seule source (début, fin, minuteur) et l'afficher partout.
- **Texte de lecture toujours accessible** (E-F9) : colonne fixe en bureau, volet repliable ou lien « retour au texte » sur mobile.

**3. Effet moyen, effort élevé**
- **Courte explication par question** en relecture (E-F8) : la valeur de l'épreuve inédite pour un élève est dans le « pourquoi ».
- **« Refaire seulement mes erreurs »** depuis la relecture.
- **Lecture audio du texte d'écoute** : à l'examen il est lu à voix haute, ici il est affiché en entier (à décider avec le contenu : la compréhension orale n'est pas la même épreuve).

## Diagnostic [phase B] (2026-10-20, lecture seule, rien modifié)

Méthode : code, et lecture de la tentative n° 199 et du parcours de Gogo en base locale.

### E-F2 : trois temps incohérents au bilan : **cause confirmée**

| Ce que voit l'élève | D'où ça vient | Valeur pour la tentative 199 |
|---|---|---|
| « Time used: 34:33 » (en-tête du bilan) | `inedit/views.py:376` : `temps_total_secondes = submitted_at - started_at` | `started_at` 07:54:28, rendue 08:29:01 : **34:33** |
| « Your time : 4 min » (carte du temps) | `inedit/rapport.py:66` `temps_par_exercice` : intervalles entre `exam_mode_started_at` et chaque réponse, jusqu'à la DERNIÈRE réponse cochée (pas jusqu'au rendu) ; appelée avec `exam_mode_started_at` (`views.py:348`) | chrono lancé à 08:23:34, dernière réponse à 08:27:12 (`answered_at`, voir `notation.py:210`) : **3 min 38 s**, arrondi à « 4 min », soit 1 min 49 s de moins que le temps réel jusqu'au rendu (08:29:01) |
| Minuteur de l'épreuve (1:29:52 → 1:24:43) | durée du chrono depuis `exam_mode_started_at` | **5 min 27 s** entre lancement du chrono et rendu |

Le fait déclencheur : `started_at` est l'instant de **création de la copie**, pas du chrono. `start_tentative` (`views.py:548`) réutilise une copie encore vide (« une copie encore vide est réutilisée ») : la copie créée à 07:54 a attendu **29 minutes** avant que le mode « Real conditions » n'enclenche le chrono à 08:23. Ces 29 minutes sont comptées dans « Time used ». Même mécanisme en entraînement libre : une copie ouverte puis reprise le lendemain afficherait « Time used » en heures ou en jours, sans lien avec le temps travaillé.

**Correction proposée (non appliquée).** Une seule définition : « temps passé sur l'épreuve ».
1. Mode examen ou papier : `submitted_at - exam_mode_started_at` (ici 5:27), cohérent avec le minuteur ; mode libre : pas de « Time used » (il n'y a pas de chrono), ou « Done in N sessions » plus tard. Une ligne à changer dans `_tentative_resultat_payload` (`views.py:376`).
2. Carte « Your time » : la durée totale qu'elle somme s'arrête à la dernière réponse ; soit prolonger le dernier intervalle jusqu'au rendu (`rapport.temps_par_exercice` reçoit déjà `debut`, lui ajouter `fin`), soit n'afficher que les parts en pourcentage (déjà calculées) et la durée totale de la ligne précédente. Les deux écrans disent alors la même chose.
3. Tests : `inedit/test_rapport.py` (fin de la dernière réponse) et un test de `_tentative_resultat_payload` avec une copie créée bien avant le chrono. Effort : faible.

### E-F3 : « You haven't tried anything on this exam yet » après un paper : **cause confirmée**

`frontend/src/pages/ParcoursSubjectPage.tsx:66` : `prochainesEtapes` décide « diagnostic » (test de positionnement de 20 questions) quand **aucun savoir n'a de `taux`** (`aUnHistorique = savoirs.some(s => s.taux !== null)`). Or `taux` ne vient que de l'historique de QUIZ. Un paper rendu alimente `quiz.RevisionSchedule` (`inedit/views.py:125`, « thèmes laissés de côté ») mais ne produit aucun `taux`.

Mesure sur le parcours English Language de Gogo après le paper : **32 thèmes, 0 avec `taux`, 17 `en_revision`.** Deux endroits de la même page se contredisent : le bandeau « My progress » compte 17 thèmes en révision (calculé côté serveur à partir de `RevisionSchedule`), tandis que la carte « prochaine étape » dit que rien n'a été tenté. Si la condition était `taux !== null || en_revision`, `prochainesEtapes` renverrait déjà les 3 premiers thèmes en révision, ce qui est la bonne recommandation.

**Correction proposée (non appliquée).**
1. `aUnHistorique = savoirs.some((s) => s.taux !== null || s.en_revision)` : une ligne. Test dans `ParcoursSubjectPage.test.tsx` avec un thème `en_revision` et sans taux.
2. Mieux, pour un élève qui vient de rendre un paper : une carte « Revise the N topics from your paper » qui lance la séance de révision, plutôt que la liste générique. À décider avec vous (produit).
3. Effort : faible pour 1, moyen pour 2.

Lien avec E-F6 (18 thèmes « tomorrow » dont la plupart viennent des questions non faites) : c'est la même source, `_planifier_revisions_des_questions_non_traitees` (`views.py:178`) ; corriger E-F3 sans trancher E-F6 recommanderait en tête des thèmes que l'élève n'a jamais vus plutôt que ceux qu'il a ratés.

## Ce que cette session ne dit pas
- Pas de mesure de motivation ni de plaisir réels : Gogo est un testeur simulé, qui répond sciemment avec quelques erreurs.
- **Aucun rendu mobile** (émulation inopérante) : le texte de lecture long, la grille de questions et le clavier tactile restent à tester.
- Réseau non bridé, cache chaud : aucune vraie mesure de data ou de 3G.
- 22 questions sur 50 vues : les sections vocabulaire (Q41-50) et une grande partie de la grammaire n'ont pas été parcourues.
- Pas de relecture scientifique des corrigés (une seule vérification au passage : Q31 cohérente).
- Compte abonné : l'écran d'un visiteur ou d'un non-abonné devant ce paper (mur, essai) n'a pas été vu.
- La tentative n° 199 (copie rendue) reste dans la base locale.

## Corrections appliquées (2026-10-20, non committées)

| Friction | Correction | Preuve |
|---|---|---|
| E-F1 libellés français du bilan | `CartePertes` (`RapportFin.tsx`) traduit les causes d'après leur CODE (clés `rf.cause_*`, variante « Exercices not attempted » pour une annale par exercice), repli sur le libellé du serveur ; `InediteResultPage` passe l'unité | 2 tests (`InediteResultPage.test.tsx`, anglais et annale par exercice) |
| E-F4 titre français du parcours | `quiz/textes.py` : clé `parcours.titre_themes` (FR / EN) ; `construire_parcours` l'écrit dans la langue du cursus | 2 tests (`quiz/test_parcours_gce.py`) ; backend 785 verts (quiz, inedit) |
| E-F5 « inclus dans l'accès » | Fiche de l'épreuve : ligne « This paper is included in your plan » pour un abonné (pas pour une épreuve offerte, qui a son badge Gratuite) | 1 test (`EpreuveInediteDetailPage.test.tsx`) |
| E-F11 phrase « tick each question completed » | `cm.regle3_ecran` : « …(or pick your answer for a multiple-choice question) » (la fiche ne sait pas si l'épreuve est un QCM, donc formulation neutre) | texte vérifié, pas de test dédié |
| E-F13 (a) « Finish  paper » | Le bouton avait deux éléments flex séparés par l'écart du bouton : le texte est maintenant dans un seul `<span>` | tests existants (« Terminer ») verts |
| E-F14 « non traitée » | Une QCM sans réponse affiche « Not completed: this question is worth 0 points. » en relecture (comme les questions ouvertes) | 1 test (`InediteTentativePage.test.tsx`) |

**Non modifié, et pourquoi.** E-F13 (b) et (c) sont du CONTENU de l'épreuve publiée (id 179) : le préfixe « (Listening passage in question 1, Section One) » est écrit dans l'énoncé de chaque question en base, et les lettres de choix y sont en minuscules (`a`, `b`…, l'écran les met en majuscules). À trancher avec l'auteur du paper (retirer le préfixe des questions 2 et suivantes, ou le garder comme repère de la section).

**Vérification.** Frontend 94 fichiers, 838 tests verts, `tsc` propre ; backend `quiz` + `inedit` 785 verts ; caddy reconstruit, backend patché (`docker cp` + redémarrage). **Non vu à l'écran** : le Chrome de l'utilisateur était sur le profil Guyguy (BEPC), pas sur Gogo ; je n'ai pas changé de profil pour ne pas perturber sa navigation. À regarder sous Gogo : fiche de l'épreuve (ligne « included in your plan »), bilan de la copie 199 (libellés anglais), parcours English (titre anglais), bouton « Finish paper ».

## Corrections, 2e lot : ce qui était clair (2026-10-20, non committé)

| Friction | Correction | Preuve |
|---|---|---|
| E-F10 libellés « Ex. 1 · Q19 » | Dans un paper à un seul exercice, les repères des fenêtres « Finish » disent « Q19 » (clé `ct.repere_question_seule`) ; « Ex. 2 · Q1 » reste pour plusieurs exercices | 2 tests (`InediteTentativePage.test.tsx`) |
| E-F7 (+ E-F14, légende) grille de relecture | Copie rendue : une QCM est **juste** (vert), **fausse** (rouge) ou **non traitée** (bordure en pointillés) ; la légende ne montre que les états présents (plus de « à traiter » ni de « à noter » dans un paper de QCM) ; l'état est dit dans l'`aria-label` de chaque pastille | 1 test |
| E-F12 contraste | Option choisie : bordure pleine + anneau + coche (plus seulement un fond très pâle) ; pastille de drapeau agrandie (`size-4`) | non testé à l'écran |

**Laissé, et pourquoi.** E-F6 (non-faites mêlées aux erreurs, 18 thèmes « tomorrow ») : c'est un choix de produit documenté dans `inedit/views.py` (« les thèmes laissés de côté reviennent dans la séance du jour »), pas un oubli ; à trancher avec vous. E-F2 (trois temps) et E-F3 (prochain pas du parcours) : causes à diagnostiquer en phase B avant de corriger. E-F8 (explications), E-F9 (texte de lecture fixe) : travail de contenu et de mise en page, pas une correction rapide. E-F15 (confiance faible) et E-F13 b/c (contenu du paper) inchangés.

**Vérification** : frontend 94 fichiers, 840 verts, `tsc` propre, caddy reconstruit. **Non vu à l'écran** : la tentative n° 199 de Gogo n'a pas été rouverte (le Chrome de l'utilisateur n'était pas sur ce profil).

## Corrections, 3e lot : E-F2 et E-F3 (2026-10-20, non committé)

| Friction | Correction | Preuve |
|---|---|---|
| E-F2 trois temps | `inedit/rapport.py` : `temps_passe_secondes(exam_mode_started_at, submitted_at)` remplace « rendu − création de la copie » dans `_tentative_resultat_payload` (inedit) ET dans `simulations/views.py` ; **rien en entraînement libre** ; la carte « Your time » (`temps_par_exercice`) reçoit `fin` et prolonge le dernier intervalle jusqu'au rendu, donc son total rejoint le temps passé | 5 tests `inedit/test_rapport.py` (copie créée 35 min avant le chrono → 6 min ; libre → None ; jamais négatif ; dernier intervalle jusqu'au rendu), 2 tests `inedit/tests.py` (chrono de 5 min sur copie vieille d'une heure ; libre → null) ; `inedit` + `simulations` : 339 verts |
| E-F3 « tu n'as encore rien tenté » | `ParcoursSubjectPage.tsx` : `aUnHistorique = taux !== null \|\| en_revision` ; un paper rendu (qui n'alimente que la file de révision) compte comme un historique et recommande les premiers thèmes en révision | 2 tests `ParcoursSubjectPage.test.tsx` (rien tenté → positionnement ; thèmes en révision sans taux → pas de positionnement) |

**Recalculé sur la tentative 199** (base locale, après redémarrage du backend) : `temps_total_secondes` = 326 s (5 min 26 s) et la carte du temps = 326 s pour l'exercice 1, au lieu de 34:33 et 4 min : les trois valeurs concordent avec le minuteur.

**Vérification** : frontend 94 fichiers, 842 verts, `tsc` propre ; backend `inedit` + `simulations` 339 verts ; caddy reconstruit, backend patché (`docker cp` + redémarrage). Page de parcours de Gogo non revue à l'écran.

**À noter.** Les anciens résultats déjà calculés ne sont pas stockés : ils sont recalculés à chaque lecture, donc ils se corrigent d'eux-mêmes. En entraînement libre l'en-tête n'affiche plus « Time used » (il n'y avait pas de chrono pour le justifier).
