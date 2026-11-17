# 15 - Audit des fonctionnalités : l'interface est-elle conviviale et ludique ?

Date : mardi 2026-11-17 (J-14 avant le lancement du 1er décembre). Site local, commit `50deb9af`, images `caddy` et `backend` reconstruites le matin même.
Question posée : fonctionnalité par fonctionnalité, l'interface est-elle agréable à utiliser (conviviale) et donne-t-elle envie de jouer et de revenir (ludique) ?
Complète les audits 10, 13 et 14 sans les refaire.

## 1. Verdict

**Oui pour le quiz, non pour le reste.** Le quiz à choix est au niveau des meilleures applications : deux touchers avant la première question, une réponse qui se sent (couleur, mascotte Kora, points, son), un écran de résultat qui fête la réussite et console l'échec sans mentir. Les trois sessions élève y placent leur meilleur moment.

Dès que l'élève sort du quiz à choix, le plaisir s'arrête :

1. **Quatre défauts cassent le parcours au moment où l'élève veut continuer** : le bouton qui mène au quiz de la séance est masqué, le bouton principal du résultat est refusé au visiteur, le corrigé de l'épreuve d'essai est inatteignable à 375 px, l'en-tête du quiz déborde.
2. **Les questions à rédiger transforment le quiz en devoir.** C'est le pire moment de deux sessions sur trois.
3. **Les mécaniques ludiques s'arrêtent au quiz.** Examen blanc, défi de la semaine, cartes de révision et page de progression n'ont ni points, ni mascotte, ni moment de fête.
4. **Les récompenses existent mais ne se voient pas.** La page « Mes réussites » (15 niveaux, 16 jalons) n'est accessible que depuis « Mon compte », à 1 211 px de défilement.
5. **Des chiffres se contredisent sur un même écran** et retirent la satisfaction qu'ils devaient donner.
6. **Quelques phrases jugent ou excluent** : « frère » adressé à toutes les élèves, bouton « Échec », « Tu as raté ce thème il y a 24 jours ».
7. **L'échec total est mal accompagné.** Les phrases après une erreur sont bonnes, mais l'élève qui fait 0 sur 6 voit « 0% » en plus gros texte de l'écran, puis, en tête du quiz qu'on lui propose comme « plus accessible », « Ton meilleur score : 0 sur 6 » au-dessus des mêmes questions.

Aucun défaut bloquant (S1). Les défauts des points 1, 5 et 7 demandent chacun moins d'une journée.

## 2. Méthode et limites

- **Trois sessions élève dans le navigateur**, à 375 x 812, chacune jouée par un agent à contexte neuf qui n'a lu ni le code ni les rapports précédents (méthode du skill `eleve`) :
  - Guyguy, 3e, BEPC, visiteur sans compte : `docs-relecture/eleve/2026-11-17-guyguy-visiteur-M1-M2-M3-ludique-local.md`
  - Guyguy, 3e, BEPC, compte de test abonné : `docs-relecture/eleve/2026-11-17-guyguy-abonne-M8-M4-M5-ludique-local.md`
  - Aïcha, Première D, Probatoire, visiteuse découragée qui rate son quiz de maths : `docs-relecture/eleve/2026-11-17-aicha-visiteuse-M1-M2-M4-ludique-local.md`
- **Lecture du code** par moi : inventaire des mécaniques ludiques (`frontend/src/components`, `lib/retours.ts`, `lib/mascotte.ts`, `backend/quiz/xp.py`) et recherche de la cause des défauts majeurs.
- **Contrôle par moi dans le navigateur** de deux défauts majeurs, avec mesures (section 4).
- **Statut** : « Vérifié » = mesuré ou relu par moi ; « Relevé » = vu par une session, non recontrôlé ; « Code » = lu dans le code, non vu à l'écran.
- **Limites** :
  - Satisfaction simulée : un indice pour comparer des sessions, pas l'avis de vrais élèves.
  - Sons et animations non perçus (captures fixes) ; réseau local non bridé ; pas de vrai téléphone.
  - **La base locale est en retard sur la production pour les questions à choix** (noté le 2026-11-02 : en production, le quiz gratuit de PCT du BEPC est entièrement à choix). La part de questions à rédiger relevée ici est à recompter en production avant toute décision.
  - Interface anglaise, parent, compte expiré et paiement non rejoués ce jour.
- **Effets de bord** : aucun fichier du code modifié. En base locale : quiz, séance et copies des comptes de test `[TEST]`. En me connectant sur l'origine où le visiteur avait joué, son compte invité a probablement été fusionné dans le compte de test `nadege+…eleve-abonne` (un profil BEPC y est apparu).

## 3. Situation par fonctionnalité

Convivial = clair, aimable, sans lourdeur. Ludique = retour immédiat, récompense, envie de recommencer.

| Fonctionnalité | Convivial | Ludique | Ce qui a été vu |
|---|---|---|---|
| Première visite, quiz d'essai sans compte | Fort | Fort | Deux touchers avant la première question, aucune fenêtre. Mais la suite proposée est refusée (D2) |
| Quiz, question à choix | Fort | Fort | Vert ou rouge, Kora, « Bravo ! +10 points », série « tu es en feu », messages d'erreur sans jugement |
| Quiz, question à rédiger | Faible | Faible | « Essaie d'abord sur ton brouillon », corrigé de 2 à 3 écrans, auto-notation « Réussi / Partiel / Échec » |
| Résultat de quiz | Fort | Fort | Anneau, confettis, phrase de Kora, points, niveau à atteindre. Trois chiffres contradictoires (D6) |
| Accueil abonné, séance du jour | Correct | Correct | Reprise en un toucher, flamme, jours cochés. Deux phrases qui refroidissent (T3, D6) |
| Exercice de la séance | Faible | Faible | Énoncé à 1 096 px, bouton de l'étape suivante masqué (D1), « Je l'ai fait » sans retour visible |
| Cours | Correct | Faible | Première phrase claire, « +2 points » à « J'ai compris ». 12 337 px, aucune figure en géométrie |
| Cartes de révision | Faible | Faible | Verso de 2 425 px, écran renvoyé au pied de page, « Paquet terminé » sans points |
| Examen blanc, mini-inédite, défi de la semaine | Correct avant, faible après | Faible | Modes bien expliqués. Après la copie : ni note immédiate, ni points, ni Kora, ni suite au défi |
| Quiz chronométré | Correct | Correct | Kora compare au score d'avant. Aucun point, deux durées annoncées |
| Ma progression | Faible | Absent | « 43 thèmes abordés sur 814 », ni points, ni niveau, ni série |
| Mes réussites | Correct | Caché | 15 niveaux, record de série, 16 jalons. Lien seulement dans « Mon compte » |
| Mes erreurs | Correct | Correct | « Refaire 10 erreurs » en un toucher |
| Recherche | Fort | - | « pitagore » corrigé en « pythagore », « La réponse en bref », état vide utile |
| Épreuves : liste et lecteur | Correct | - | Étiquettes « Gratuit » et « corrigé payant » claires, « Essaie d'abord ». Première épreuve à 1 161 px |
| Verrous et prix | Correct | - | Cadenas aimable avec « Montrer à mes parents ». Refus sec sur le quiz (D2), 6 000 FCFA présélectionné |
| Connexion par code | Correct | - | Écran du code 9 s après le toucher (envoi par SMTP en local) |
| Mascotte Kora | Fort | Fort | Citée comme meilleur moment par les deux sessions Guyguy. « frère » pour tous (T1) |

## 4. Défauts à corriger en premier

Chacun demande une journée ou moins.

| # | Constat | Preuve | Correctif proposé | Statut |
|---|---|---|---|---|
| D1 | **Le bouton « Passer au quiz » de la séance est recouvert par la barre « Précédente / Suivante ».** La barre n'est plus fixée à l'écran : l'animation d'entrée de la page laisse une transformation sur son conteneur, qui devient le repère de la barre. Elle se pose en bas du contenu, sur le bouton (27 px recouverts sur 44). L'élève touche « Suivante » et quitte sa séance. | Mesure : bouton de 3 270 à 3 314 px, barre de 3 287 à 3 356 px, `transform: matrix(1,0,0,1,0,0)` sur le conteneur. `frontend/src/pages/ThemeExerciceLecturePage.tsx:172` et `:223` ; `frontend/src/index.css:186-199` | Sortir la barre du conteneur animé (portail, comme `PricingPage.tsx:266`), ou terminer l'animation sur `transform: none`. Contrôler ensuite `EpreuveInediteDetailPage.tsx:562` | Vérifié. Nouveau |
| D2 | **Visiteur : le bouton principal du résultat, « Encore 5 questions », est refusé.** Ligne rouge « Abonnement requis pour ce cursus. », sans lien. Même refus pour « Même thème, plus accessible » et « Quiz ciblé ». C'est le pire moment de la session visiteur (-2), juste après un quiz raté. | Trois `POST /quiz/sessions/` en 403 dans la session Guyguy (BEPC). Pour Aïcha (Probatoire D), le même bouton a marché : le refus dépend du thème. Le serveur n'accepte un thème que si toutes ses questions sont en vitrine : `backend/quiz/views.py:529` ; bouton sans condition : `frontend/src/pages/QuizResultPage.tsx:537-548` | Pour qui n'a pas l'accès : remplacer ce bouton par « Essayer une autre matière gratuite » et « Bats ton score », et écrire le refus dans les mots de l'élève avec le lien vers le prix | Relevé, cause lue. Même famille que le défaut A1 de l'inventaire du 2026-11-13, non corrigé |
| D3 | **Épreuve d'essai à 375 px : « Correction » et « Examen » sont superposés.** Le mode « Entraînement libre » promet « Corrigé accessible à tout moment » ; trois touchers n'ouvrent rien. Côté abonné, « Voir mon résultat » recouvre « Correction ». | Mesure : « Correction » de 163 à 277 px, « Examen » de 157 à 255 px (92 px communs), « Terminer » à partir de 261 px. `frontend/src/pages/InediteTentativePage.tsx:750-775` | Passer la barre sur deux lignes ou replier « PDF » et « Examen » dans un menu sous 400 px | Vérifié. Nouveau |
| D4 | **L'en-tête du quiz déborde dès qu'une série apparaît.** Le badge « 2 d'affilée » recouvre « 40 points · objectif atteint », « justes » est coupé, la page passe à 388 px de large et se décale. | Vu sur trois quiz de la session visiteur | Laisser le badge passer à la ligne ou raccourcir le compteur | Relevé |
| D5 | **Reprise d'un quiz : on arrive sur la dernière question déjà corrigée**, avec « Voir mon résultat » pour seul bouton. Le résultat dit « 100 % · Sans faute ! » avec deux questions passées ; l'historique dit « 3/5 » pour le même quiz. | Session abonné, étapes 3 à 5 et 24 | Reprendre sur la première question sans réponse ; une seule règle de score partout | Relevé |
| D6 | **Chiffres qui se contredisent sur un même écran.** « 0 séance cette semaine » juste après un quiz, au-dessus du jour coché. « À ce rythme (1 séance par semaine), tu couvres 1 % de l'essentiel » sous « 3 séances cette semaine », le jour où la séance est validée. « +10 points » au-dessus de « Objectif du jour 0 / 20 ». Cours « 30 min » puis « ≈ 9 min restantes » à 9 %. Quiz « environ 4 min » puis chrono à 9 min 30. | Sessions visiteur (5 écrans de résultat) et abonné (étapes 5, 13, 16, 19) | Une seule source par chiffre ; ne pas afficher la projection « 1 % » le jour où la séance est faite | Relevé |
| D7 | Quiz de Français : « __afin qu'__aucun » s'affiche avec ses tirets bas, la consigne dit « (souligné) ». | Session visiteur, étape 19 | Corriger le rendu du soulignement dans les items de quiz | Relevé |
| D9 | **« Tu as déjà joué ce quiz. Ton meilleur score : 0 sur 6. »** reste en tête de chaque question du quiz relancé après un 0 sur 6. Pire moment de la session Aïcha (-2). Le bandeau date du commit de ce matin (`50deb9af`). | Session Aïcha. Affiché sans condition de score : `frontend/src/pages/QuizSessionPage.tsx:445-451` | Ne citer le score que s'il atteint la moitié ; en dessous : « Deuxième essai : tu connais déjà ces questions. » | Relevé, code lu. Nouveau |
| D10 | **« Même thème, plus accessible » ressert 5 des 6 mêmes questions**, dont les questions à rédiger ; seule la « Difficile » est retirée. | Session Aïcha | Sur un thème gratuit trop court pour varier, proposer une autre matière gratuite ou le cours du thème | Relevé |
| D11 | Résultat raté : « 0% » est le plus gros texte, suivi de « 0 meilleure série » et « 0 séance cette semaine ». Une réponse déclarée « Partiel » rapporte 2 points mais compte zéro dans « 0 / 6 ». « 0 / 20 points » en tête de question est lu comme une note sur 20. | Session Aïcha | Sous 40 %, mettre en avant le titre (« Chaque quiz te rapproche de l'examen ») et les points gagnés, pas le pourcentage ; masquer les compteurs à zéro ; écrire « 0 point sur 20 aujourd'hui » | Relevé |
| D8 | « Je l'ai fait » ne change pas d'aspect après le toucher. Bouton « Un autre quiz » haut de 20 px. « Tu maîtrises ! » sur trois lignes, le point d'exclamation seul. | Sessions abonné (étape 7) et visiteur | Retour visible, zone de toucher de 44 px, mot de félicitation insécable | Relevé |

## 5. Le ton

Ce qui est bien et ne doit pas bouger : tutoiement partout, phrases courtes, aucune erreur jugée (« Pas tout à fait, mais c'est comme ça qu'on retient. », « Une erreur comprise, c'est un point gagné pour l'examen. »), résultat faible consolé sans mentir (« Ce n'est que le début. Même les meilleurs sont passés par là. »), franchise sur le compte et le prix.

| # | Constat | Preuve | Proposition | Statut |
|---|---|---|---|---|
| T1 | **Kora dit « frère » à tout le monde** : 6 phrases sur 29 en français, « mate » en anglais. Une élève reçoit « Te revoilà, frère ! ». | `frontend/src/lib/i18n/fr.ts:3316-3343` ; reçu deux fois par Aïcha : « Tu progresses, frère » | Garder le registre, retirer le mot : les variantes sans « frère » (« Bien joué ! Tu peux être fier de toi. ») ont le même effet dans les sessions | Vérifié (code et session). Connu depuis l'audit 01 (UX-09), jamais tranché |
| T7 | Kora compare à un zéro et d'une matière à l'autre : « Tu progresses, frère : la dernière fois, c'était 0 %. », puis au résultat de français « la dernière fois, c'était 20 % », qui venait des maths. | Session Aïcha. La mémoire de Kora garde un seul pourcentage par appareil (`frontend/src/lib/memoireMascotte.ts`) ; aucun plancher dans `lib/mascotte.ts:39` | Ne pas citer un score d'avant sous 30 % (« Là, tu montes. Ça se voit ! ») ; garder le souvenir par matière | Relevé, code lu |
| T2 | Auto-notation : « Sois honnête avec toi-même : as-tu réussi cette question ? » et bouton « Échec ». | Les deux sessions Guyguy | « Alors, tu l'avais ? » ; boutons « Oui / En partie / Pas encore » | Relevé |
| T3 | Première phrase de l'accueil abonné : « Tu as raté ce thème il y a 24 jours : 18 minutes pour le rendre solide. » | Session abonné, étape 3 | « Ce thème t'a résisté : 18 minutes pour le rendre solide. » | Relevé |
| T4 | Mots d'administration : « Abonnement requis pour ce cursus. », « cursus par cursus », « Ton cursus », « Provisoire 0 / 4 », « épreuves officielles en base ». Le persona n'a pas compris « cursus ». | Session visiteur | « examen » à la place de « cursus » dans tout ce que lit l'élève | Relevé |
| T5 | « +0 points » en caractères de titre sous « Sans faute ! 100 % » après un rejeu. | Session visiteur, étape 10 | Mettre le record battu en vedette, les points en petit | Relevé |
| T6 | Bilan d'examen blanc : « Une bonne part de tes points perdus n'a pas de cause. En revoyant ta copie corrigée, précise pourquoi sous chaque question ». | Session abonné, étape 22 | Une phrase d'encouragement d'abord, la demande ensuite et facultative | Relevé |

## 6. Étendre le ludique hors du quiz

L'inventaire du code confirme ce que les sessions ont ressenti : mascotte, confettis, sons et annonce de points ne sont branchés que sur le quiz, la lecture d'un cours et l'exercice déclaré fait. Aucun de ces retours dans `InediteResultPage`, `RapportFin`, `PaquetDeCartes`, `CartesDeRevision`, `MesErreurs`, `DefiDeLaSemaine`, `Progression`, `MesExamensBlancsPage`.

| # | Recommandation | Pourquoi | Effort |
|---|---|---|---|
| L1 | **Annoncer ou écarter les questions à rédiger.** Quiz d'essai et « Quiz express » de la séance : questions à choix d'abord, la première de niveau facile. Ailleurs, dire avant de lancer « 3 questions à rédiger, prends un brouillon ». | Pire moment des sessions visiteur (quiz de SVT quitté à la question 1) et abonné (quiz quitté à la troisième démonstration). À recompter en production | S pour l'ordre et l'annonce ; le stock de questions à choix dépend des campagnes en cours |
| L2 | **Montrer les récompenses là où l'élève les cherche.** En tête de « Ma progression » : niveau, points, série, record, prochain jalon, lien « Mes réussites ». Rappel du niveau sur l'accueil du visiteur qui revient. | L'élève abonné a cherché ses points dans « Ma progression », le menu et le menu du compte sans les trouver | S |
| L3 | **Fêter le passage de niveau et le jalon au moment où ils arrivent**, dans le quiz, et pas en bandeau sous le pli du résultat. | « Nouveau niveau : Malin ! » n'a été vu qu'en défilant | S |
| L4 | **Donner une fin à l'examen blanc et au défi de la semaine.** Dès la copie rendue : temps, questions traitées, mot de Kora. Au bilan : points, « Défi relevé », rappel du résultat dimanche. | Une copie rendue ne rapporte rien : aucun appel de points dans `backend/inedit`, alors qu'un examen blanc sur annale en rapporte 20 (`backend/simulations/views.py:127`). Humeur -1 deux fois de suite | S à M |
| L5 | **Cartes de révision : un verso d'un écran, la carte suivante sous les yeux, des points et une fin de paquet fêtée.** | Verso de 2 425 px ; après « Je savais », l'écran se retrouve au pied de page | S (défilement, points) ; M (verso court : contenu) |
| L6 | **Alléger le haut des pages de travail.** Exercice de la séance : énoncé à 1 096 px. Liste des épreuves : première carte à 1 161 px. Résultat de quiz : 2 452 px. | Trois couches fixes en bas, encarts d'aide et bandeaux empilés en haut | S par page |
| L7 | **Une figure dans les cours et corrigés de géométrie.** | Cours « La translation » : 12 337 px, aucune image. Déjà recommandé (audit 14, C3) | L (éditorial) |
| L8 | Donner une raison de choisir le chrono : afficher le record de temps au lancement. | « Ne rapporte pas de points et ne compte ni dans ta maîtrise ni dans ta série » est tout ce que lit l'élève | S |

Je ne recommande toujours pas les classements nominatifs, les vies ni la monnaie virtuelle (écartés par l'audit 10).

## 7. Ce qui marche et ne doit pas être cassé

- L'entrée en deux touchers, sans compte, sans fenêtre.
- Le retour d'une question à choix : une touche, vert ou rouge, Kora, un mot de félicitation qui change, « +10 points ».
- « Comprendre mon erreur », qui explique le mauvais choix précis de l'élève.
- L'écran de résultat : anneau, confettis, phrase de Kora, « Encore 20 points pour devenir Malin ».
- Kora qui compare au score d'avant : « Tu progresses : la dernière fois, c'était 40 %. »
- Le rejeu : « Ton meilleur score : 4 sur 5 », « Défier un camarade ».
- La fin de séance : « +32 points dont 10 de bonus », jour coché, flamme « Jour 1 : bien parti ! ».
- La reprise en un toucher depuis l'accueil, retrouvée en 0,5 s.
- La recherche qui pardonne les fautes et son état vide.
- Le cadenas du corrigé payant et « Montrer à mes parents ».
- Les énoncés ancrés ici : la toiture en chaume d'une case, une libraire de Yaoundé.

## 8. Satisfaction des sessions

Indice simulé, à lire en comparaison des sessions précédentes du même persona.

| Session | Verdict | Satisfaction | Effort | Retour | Recommandation | Meilleur moment | Pire moment |
|---|---|---|---|---|---|---|---|
| Guyguy visiteur | Réussie avec effort | 4/5 | 2/5 | cette semaine | 7/10 | Résultat du premier quiz : 80 %, confettis, Kora (+2) | « Abonnement requis pour ce cursus. » trois fois (-2) |
| Guyguy abonné | Réussie avec effort | 3/5 | 3/5 | cette semaine | 6/10 | Kora : « Tu progresses, frère : la dernière fois, c'était 40 %. » (+2) | Troisième question « Démontre… » de suite, quiz quitté (-2) |
| Aïcha visiteuse | Réussie avec effort | 3/5 | 3/5 | cette semaine, pas pour les maths | 6/10 | Français : « Tu maîtrises ! Objectif du jour atteint. », « tu es en feu » (+2) | « Ton meilleur score : 0 sur 6 » en tête du quiz « plus accessible » (-2) |

Aïcha n'a pas abandonné : les phrases après chaque erreur l'ont retenue, et un cours sur la dérivée se lit en entier sans payer. Elle prévient : un second 0 % au premier quiz et elle ne revient plus. Première session de ce persona, donc sans point de comparaison.

Comparaison avec le 2026-11-07 : Guyguy visiteur 4/5 et 7/10 (inchangé) ; Guyguy abonné 3 ou 4/5 et 6/10 (écart d'un point au plus, dans le bruit). Les correctifs des deux dernières semaines n'ont pas dégradé le parcours ; ils ne l'ont pas non plus fait monter, parce que les deux creux d'aujourd'hui (refus au visiteur, questions à rédiger) étaient déjà là.

## 9. Décisions à prendre

1. **« frère »** (T1) : le retirer des phrases de Kora, ou le garder en assumant qu'il s'adresse aussi aux filles ?
2. **Questions à rédiger** (L1) : les sortir du quiz d'essai et du « Quiz express », ou seulement les annoncer ?
3. **Défi de la semaine et inédites** (L4) : leur faire rapporter des points et compter pour la série, comme l'examen blanc sur annale ?
4. **« Mes réussites »** (L2) : l'intégrer à « Ma progression », ou lui donner une entrée dans le menu ?

## 10. Ordre proposé

- **Avant le 1er décembre** : D1, D2, D3, D4, D6, D9, D11, T1 à T5, T7, L2, L3. Tous d'une journée ou moins.
- **Décembre** : D5, D7, D8, D10, L1 (après recomptage en production), L4, L5, L6, L8.
- **Au fil des campagnes de contenu** : L7.

## 11. Corrections faites le 2026-11-17 (après décisions)

Décisions : « frère » retiré ; questions à choix d'abord et annonce des questions à rédiger ; défi de la semaine et inédites rapportent des points ; « Mes réussites » intégré à « Ma progression ». Local, non committé, non déployé.

| # | Ce qui a changé | Où |
|---|---|---|
| D1 | `animate-fade-up` ne garde plus l'état final (`backwards` au lieu de `both`) : plus de `transform` résiduel, la barre « Précédente / Suivante » redevient fixée à l'écran (vérifié : 652-721 px sur 812, au-dessus de la barre d'onglets). Corrige aussi les autres pages à barre fixe | `frontend/src/index.css` |
| D2, D10 | Un visiteur sans accès voit « Essayer une autre matière gratuite » au lieu de « Encore 5 questions » ; « plus accessible », « plus dur » et « Quiz ciblé » sont masqués. Un refus 403 se lit « Ce quiz-là est réservé aux abonnés… » (serveur : « réservé aux abonnés de cet examen ») | `QuizResultPage.tsx`, `quiz/views.py`, `historique.py`, `erreurs.py` |
| D3 | La barre d'outils de l'épreuve passe à la ligne : « Correction », « Examen » et « Terminer » ne se superposent plus | `InediteTentativePage.tsx` |
| D4 | L'en-tête du quiz passe à la ligne (badge de série) : plus de débordement horizontal | `QuizSessionPage.tsx` |
| D5 | « Reprendre » arrive sur la première question passée, pas sur la dernière déjà corrigée | `QuizSessionPage.tsx` |
| D6 | Pastilles « 0 série » et « 0 séance » masquées ; « tu couvres 1 % de l'essentiel » remplacé sous 10 % par une phrase de début ; durée du cours « d'étude », pastille « de lecture restantes » ; pied de page « Séance faite » quand elle l'est | `QuizResultPage.tsx`, `trajectoire.ts`, `CoursReaderPage.tsx`, `Footer.tsx` |
| D7 | Item 1343 : « __afin qu'__aucun » devient « **afin que** nul candidat », consigne « en gras ». **Base locale seulement** : à reporter en production par la chaîne de contenu | base locale |
| D8 | « Je l'ai fait » sans points affiche un message ; « Un autre quiz » et « Refaire un quiz » touchables (44 px) ; « Tu maîtrises ! » sur une ligne | `ThemeExerciceLecturePage.tsx`, `QuizResultPage.tsx`, `QuizSessionPage.tsx` |
| D9 | Le meilleur score n'est cité qu'à partir de la moitié ; dessous : « Deuxième essai… » | `QuizSessionPage.tsx` |
| D11 | Anneau : sous 40 %, « 1 / 5 » en grand et le pourcentage en petit ; « 0 / 20 points » devient « 0 points · objectif 20 » | `QuizResultPage.tsx`, `ObjectifXp`, textes |
| T1 | Plus de « frère » ni de « mate » dans les phrases de Kora (test ajouté) | `fr.ts`, `en.ts` |
| T2, T3, T6 | « Alors, tu l'avais trouvé ? » avec « Je l'avais / En partie / Pas encore » ; « Ce thème t'a résisté » ; texte des causes de points perdus adouci | textes, `quiz/textes.py` |
| T4 | « cursus » remplacé par « examen » dans les textes d'élève (34 occurrences) | `fr.ts` |
| T5 | « +0 points » en gros remplacé par « Pas de nouveaux points cette fois » | `QuizResultPage.tsx` |
| T7 | Kora ne compare qu'à un quiz de la même matière, et ne cite pas un score d'avant sous 30 % | `memoireMascotte.ts`, `mascotte.ts` |
| L1 | Les questions à choix passent d'abord, les plus simples en tête ; annonce « N questions à rédiger… » au début du quiz | `quiz/services.py` (`ordonner_pour_jouer`), `essai.py`, `QuizSessionPage.tsx` |
| L2 | Niveau, série, record, prochain jalon et liste dépliable en tête de « Ma progression » ; `/reussites` redirige ; entrée retirée de « Mon compte » | `BlocReussites.tsx`, `ParcoursPage.tsx` |
| L3 | Message et son au passage de niveau, visibles tout de suite | `QuizResultPage.tsx` |
| L4 | Une copie d'inédite rendue en conditions réelles ou sur papier rapporte 20 points (une par jour), affichés avec un mot d'encouragement avant l'auto-notation | `quiz/xp.py`, `inedit/views.py`, `InediteResultPage.tsx` |
| L5 | Cartes : la suivante revient en haut de l'écran, verso borné à 55 % de l'écran, boutons collés en bas, fin fêtée par Kora et un son | `PaquetDeCartes.tsx` |
| L8 | Le texte du chrono annonce un record de temps à battre | textes |
| F9 | « Voir mon parcours » masqué au visiteur après une mini-inédite | `InediteResultPage.tsx` |

**Non fait** : L6 (alléger le haut des pages : énoncé à 1 096 px, liste des épreuves à 1 161 px), L7 (figures dans les cours : travail éditorial), F10 (copie d'essai retrouvable dans « Examens blancs » pour un visiteur), F15 (rappel par e-mail : le compte de test n'a pas d'adresse confirmée, à revoir avec un vrai compte), l'écart « 3/5 » entre historique et résultat, « Record : 1 jours » (pluriel), points pour les cartes de révision.

**Vérifications** : frontend, types et 1 645 tests verts ; backend, 1 177 tests des applications `quiz`, `inedit`, `simulations` verts, plus 7 tests ajoutés (`quiz/test_ordre_et_points_inedite.py`). Navigateur local à 375 px : quiz d'essai (annonce, première question facile à choix, résultat), « Ma progression » avec le bloc de réussites, barre de séance. **À déployer** : reconstruire `backend` et `caddy`, aucune migration. L'item 1343 est à corriger aussi en production.
