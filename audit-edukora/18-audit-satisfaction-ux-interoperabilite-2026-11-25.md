# 18 - Satisfaction, expérience et interopérabilité des modules

Date : mercredi 2026-11-25 (J-6 avant le lancement du 1er décembre).
Question posée : les données sont-elles utilisées et présentées de manière optimale ?
Complète les rapports 10, 14, 16 et 17 sans les refaire. L'audit n'a modifié aucun fichier hors ce rapport ; les correctifs codés ensuite sont à la section 12.

## 1. Réponse

**Non, pas encore. Les contenus sont bien reliés entre eux chez les francophones. Ce que fait l'élève ne l'est qu'à moitié, et un même fait s'affiche différemment d'un écran à l'autre.**

| Axe | Jugement | En une phrase |
|---|---|---|
| Liens entre contenus (données) | Bon en francophone, faible au GCE | 91 à 98 % du poids des thèmes qui tombent ont un cours, 78 à 92 % un quiz ; GCE : 38 à 50 %. |
| Liens entre contenus (navigation) | Inégal | Des impasses : cours vers épreuves, épreuve vers quiz, erreurs vers cours. |
| Circulation des signaux de l'élève | Moyen | Le quiz alimente presque tout. Examens blancs, exercices faits et auto-notation alimentent peu. |
| Cohérence de la présentation | Faible | Deux anneaux, deux comptes de copies, deux mots pour le même nombre. |
| Restitution au parent | Faible | Ni note d'examen blanc, ni points perdus. |
| Pilotage par l'équipe | Faible | Une partie des événements collectés n'entre dans aucun rapport. |
| Satisfaction | Correcte en simulation, **inconnue en réel** | Aucune mesure sur de vrais élèves. |

La priorité n'est pas de collecter plus. C'est de donner une seule définition à chaque chiffre, puis de faire circuler ce qui est déjà enregistré.

## 2. À vérifier avant tout : les trois témoignages en production

L'API publique `https://edukora.africa/catalog/accueil/` sert aujourd'hui trois avis (« Mme Ngono », « Brice T. », « Aïcha M. »). Le 21 novembre elle n'en servait aucun.

Ce qui est établi, sur les copies de la base locale (mêmes noms et mêmes textes) :
- origine « saisi dans l'admin », aucun profil, aucune date de consentement ;
- les trois créés à la même seconde, le 22 novembre à 21 h 04 UTC ;
- les textes racontent des faits difficiles à placer à cette date et avant le lancement : « passé de 8 à 12 en maths au premier trimestre », « au BAC blanc, je suis tombé sur un exercice presque pareil ».

Ce que je ne sais pas : s'ils viennent de vraies personnes. Un avis saisi dans l'admin peut légitimement n'avoir ni profil ni date de consentement (accord donné hors application).

**Si l'une de ces trois personnes n'existe pas ou n'a pas donné son accord, dépublier l'avis tout de suite** (admin, décocher « publié »). Le code pose la règle « preuve sociale réelle ou absente, jamais fabriquée » (`backend/catalog/models.py`, classe `Temoignage`), et des résultats scolaires chiffrés inventés tromperaient des parents au moment de payer.

Autre changement depuis le rapport 17 : la production répond `campay_active: true`, `manual_active: false`. Le paiement automatique est rétabli (aucun paiement réel testé ici).

## 3. Méthode et limites

- Trois lectures parallèles du code (signaux de l'élève, liens entre contenus, API contre interface). **« Vérifié »** = relu ou vu par moi ensuite. **« Relevé »** = rapporté par une lecture, non recontrôlé.
- Mesures en base **locale**, en lecture seule. La couverture est pondérée par le nombre d'épreuves, sur les thèmes tombés dans au moins 3 épreuves.
- Navigateur : site local, 375 x 812, compte `[TEST] Élève abonné` (BEPC). Écrans : accueil, Ma progression, Fiches, Historique, Examens blancs, Mes erreurs, Mes notes. Les autres constats d'écran viennent du code.
- **Aucune donnée d'usage réel lue.** L'activité locale est faite d'essais et ne dit rien des élèves.
- Production : deux lectures d'API publiques seulement.
- Effets de bord : un jeton local pour le compte de test, puis déconnexion et vidage du stockage du navigateur intégré.

## 4. Satisfaction

### 4.1 Ce qu'on sait (simulations, `docs-relecture/eleve/satisfaction.md`)

| Période | Contentement (sur 5) | Recommandation (sur 10) | Lecture |
|---|---|---|---|
| 25 octobre | 3 | 5 | Départ (Guyguy, visiteur et abonné) |
| 2 novembre | 3 à 4 | 5 à 6 | |
| 7 novembre | 3 à 4 | 6 à 7 | |
| 17 novembre | 3 à 4 | surtout 6 à 7 | Angle ludique |
| 21 novembre | surtout 4 | 7 quand la ligne est lisible | Résultat et conversion |

Tendance à la hausse, puis palier vers 4 sur 5 et 7 sur 10. Des écarts d'un point sur une session sont du bruit (règle du fichier), et les personas, missions et angles changent d'une date à l'autre. Les points forts qui reviennent : corrigés justes, quiz sans compte, retour immédiat. Les creux : niveau du quiz gratuit en Terminale, questions à rédiger, offre payante peu montrée.

### 4.2 Ce qu'on ne sait pas

Tout ce qui concerne de vrais élèves. Aucune de ces notes ne mesure la satisfaction : ce sont des hypothèses de frictions.

Dispositif minimal proposé :
1. **Après la 3e séance**, une question à un toucher (« Cette séance t'a aidé ? » : oui, un peu, non), avec motif facultatif. Rattachée à la matière et au thème.
2. **Chaque lundi** : part de « oui », retour à J+1 et J+7, quiz abandonnés, signalements.
3. **Cinq à huit entretiens** de 15 minutes sur le téléphone de l'élève (déjà recommandés au rapport 10, section 10).

## 5. Interopérabilité des contenus

### 5.1 Les données sont reliées (base locale)

| Examens | Cours disponible | Quiz disponible | Les deux |
|---|---|---|---|
| BEPC | 98 % | 92 % | 91 % |
| Probatoire (A, C, D, E, TI) | 92 à 97 % | 78 à 87 % | 72 à 85 % |
| BAC (A, C, D, E, TI) | 91 à 97 % | 80 à 91 % | 76 à 89 % |
| GCE O Level | 49 % | 50 % | 49 % |
| GCE A Level | 38 % | 38 % | 38 % |

Calcul : même thème ou même savoir officiel, avec la règle du site (`q_cours_du_cursus`). « Disponible » ne dit pas que le contenu est pertinent.

Fragilités :
- **GCE** : aucun thème rattaché à un savoir officiel, donc aucun repli ; pas de chapitres.
- **Vocabulaire éclaté** : 30 199 thèmes ; sur les 19 853 utilisés par des exercices, 10 483 (53 %) ne servent qu'à un seul exercice. Ce sont autant de progressions et de fréquences isolées.
- **Savoir officiel** : 15 % des thèmes, 6 % des questions.
- **Rappel de méthode** : 49 % des exercices en ont un relié à un cours.

### 5.2 La navigation ne suit pas toujours

| De → vers | État | Preuve | Statut |
|---|---|---|---|
| Cours → épreuves où la notion est tombée | Absent de la fiche cours ; le lecteur mène aux exercices du thème sous conditions | `CoursDetailPage.tsx` (aucun lien), `SuiteDuCours.tsx` | Fiche vérifiée, lecteur relevé |
| Épreuve → quiz | Aucun lien (fiche, lecteur, page d'un thème) | recherche de `/quiz` : 0 | Vérifié |
| Mes erreurs → cours | Les thèmes ratés sont des pastilles non cliquables | `MesErreursPage.tsx:150-157` | Vérifié, vu |
| Examen blanc sur annale → quiz, cours | Le serveur n'envoie ni `a_quiz` ni `a_cours` ; l'interface affiche les liens quand même, qui peuvent mener à vide | `simulations/views.py:340`, `InediteResultPage.tsx:349-361` | Code vérifié, page vide non reproduite |
| Copie d'examen blanc corrigée → cours | Corrigé sans lien vers le cours | `simulations/views.py:184,222` | Relevé |
| Fiche EduKora → thème, épreuves, cours | L'API ne renvoie ni thème ni épreuves sources ; les années ne sont pas cliquables | `memos/services.py:41-58` | Vérifié |
| Note gardée → sa fiche | Le lien ne porte ni examen ni matière : la page ouvre l'examen déclaré et la première matière | `memos/services.py:28-29`, `FichesEdukoraPage.tsx:73-82` | Code vérifié, échec non reproduit |
| Recherche → Fiches EduKora, aide | Non indexées ; « fiche » est compris comme « cours » | `recherche/models.py`, `intention.py:63` | Relevé |

## 6. Signaux de l'élève : enregistrés, mais peu partagés

### 6.1 Matrice

| Ce que fait l'élève | Maîtrise | Séance, révision | Mes erreurs | Points, série | Bilan parent |
|---|---|---|---|---|---|
| Quiz | oui | oui | oui | oui | oui |
| Inédite | **non** | révision | **non** | oui si conditions réelles et entamée | points seuls |
| Annale en examen blanc | **non** | révision | **non** | idem | points seuls |
| Exercice « fait », auto-notation | **non** | **non** (voir E1) | **non** | point à la création | **non** |
| Notes, cartes | non | files à part | non | un peu | non |

La colonne « points » est le total hebdomadaire, qui ne dit ni quelle copie ni quelle note.

### 6.2 Constats, par effet sur l'élève

| # | Constat | Preuve | Statut |
|---|---|---|---|
| E1 | **La séance peut reproposer un exercice déjà fait.** Le choix prend les plus récents du thème sans lire `ExerciceFait` ; le commentaire de la clôture suppose pourtant que cette trace l'évite sur la file d'entraînement. L'auto-notation « qu'as-tu réussi ? » ne sert qu'à être réaffichée. | `quiz/services.py:2253-2283`, `:2294-2302` | Vérifié (auto-notation : relevé) |
| E2 | **Les examens ne comptent pas dans la maîtrise.** Un thème réussi en copie reste « jamais travaillé » ; un thème raté part en révision sans entrer dans Mes erreurs. | aucune lecture des réponses de copie dans `quiz/services.py`, `erreurs.py` | Vérifié |
| E3 | **Une copie rendue vide, même en entraînement libre, remplit la file de révision**, qui passe devant dans la séance. Les points, eux, exigent le mode examen et une réponse. | `inedit/views.py:189-206`, `simulations/views.py:129-139` | Vérifié |
| E4 | **Le bilan parent ignore les notes d'examen blanc.** Les jours actifs ne viennent que des séances et des quiz : un message peut annoncer 0 jour de révision et des points. | `relances/bilan_parent.py:89-132`, `quiz/bilan.py:76,121` | Vérifié (cas des 0 jour : déduit) |
| E5 | **Le rappel par e-mail part même quand l'objectif du jour est atteint** ; la notification, elle, se tait. | `relances/services.py:231-239` contre `push.py:148-153` | Vérifié |
| E6 | **La note estimée se recale sur toute annale rendue**, libre ou vide comprise, et ignore les inédites. Les zéros peuvent la fausser. À régler avant de l'allumer. | `quiz/note_estimee.py:54-61` | Vérifié (effet déduit) |
| E7 | **Plusieurs définitions de « maîtrisé »** : solide à 3 réponses et 70 %, « Maîtrisé » à 6 et 85 %, saut du cours à 5 et 70 %, priorités dès 2 réponses ; le compteur « maîtrisés » compte les solides. | `quiz/services.py:899,949,2158`, `priorites.py:29` | Relevé |
| E8 | **Plusieurs définitions d'« activité du jour »** (série, relance d'absence, bilan, heure habituelle). Les rappels visent aussi le premier profil du compte. | `serie.py`, `relances/activite.py`, `bilan.py`, `push.py` | Relevé |
| E9 | **Les matières retirées par l'élève sortent de Mes erreurs, pas des révisions** : elles peuvent revenir dans la séance. | `quiz/services.py:735-747, 1908-1920` | Relevé |

## 7. Présentation : le même fait, plusieurs versions

| # | Ce que voit l'élève (compte de test) | Statut |
|---|---|---|
| P1 | **Anneau** : 43 au centre sur l'accueil (thèmes travaillés), 1 sur Ma progression (maîtrisés), le même jour. L'accueil pondère aussi par coefficient et fréquence, pas Ma progression. | Vu, `OuJenSuis.tsx:90-92`, `ParcoursPage.tsx:276,301` |
| P2 | **Mathématiques** : « 33 travaillés sur 111 **thèmes** » à l'accueil, « 33 **savoirs** travaillés sur 111 » sur Ma progression. « Thème », « savoir » et « consolidé » se mélangent. | Vu |
| P3 | **Copies** : « 8 examens blancs » d'un côté, « Tentatives (6) » dans l'historique. Les deux annales (PCT 2022, 13 sur 20 ; Maths 2026, 8 sur 20) manquent à l'historique. | Vu |
| P4 | **Meilleure note 65 %** : le classement mêle des minis sur 4 points et des annales sur 20. « +13 points depuis le premier » désigne des points de pourcentage, sur un site où « points » désigne la récompense. | Vu |
| P5 | **Annales non filtrées sur l'examen préparé**, contrairement aux inédites : un élève qui change d'examen mêle les deux dans sa meilleure note et sa tendance. | Code vérifié (`mes_simulations` filtre le profil seul), effet déduit |
| P6 | **« Où partent tes points »** : 68 % « exercices non traités », 32 % « cause non précisée ». Rien sur ce que l'élève doit apprendre, et aucune action proposée à côté. | Vu |
| P7 | **Réviser a 7 onglets** : à 375 px la rangée mesure 605 px pour 293 visibles. Sur Fiches, l'onglet actif est hors écran, et aucun onglet du bas n'est allumé (même cause pour Examens blancs, relevée dans le code). | Vu, `BottomTabBar.tsx:57-64` |
| P8 | Couleurs de note différentes entre Historique (vert dès 50) et Examens blancs (vert dès 70). | Relevé |
| P9 | Quatre files « à revoir » : thèmes, cartes, notes, erreurs, sous des mots proches. « Fiche » désigne aussi plusieurs choses. | Relevé |

## 8. Les modules récents (Mes notes, Fiches EduKora)

- En local, **83 fiches, toutes en brouillon, aucune relue**, 33 rattachées à un thème. Parmi les couples examen, matière et thème couverts, 15 sur 27 rejoignent un quiz et 18 sur 27 un thème tombé. État de la production non contrôlé.
- Elles forment une île : on y entre par les onglets, les aperçus et les notes ; rien depuis un cours, un exercice ou un résultat de quiz (relevé).
- Le rappel « tes notes sur ce thème » ne voit pas les notes prises dans un cours ou un corrigé, enregistrées sans thème (relevé). Les lecteurs offrent deux systèmes de notes côte à côte.
- Aucun événement de mesure : on ne saura pas si elles sont lues (relevé).

**Avant de les publier** : thème sur chaque fiche, liens vers cours et épreuves, lien de retour corrigé, événements « lue » et « gardée ».

## 9. Pilotage

Tout ce paragraphe est relevé, non recontrôlé.
- L'entonnoir n'a pas d'écran pour l'équipe ; la rétention ne sort que par une commande.
- Les événements de connexion et d'affichage du numéro de paiement, la recherche et les boutons d'accueil n'entrent dans aucun rapport lu par les lecteurs : ils se consultent ligne par ligne.
- La liste des signalements ne montre ni l'énoncé ni la matière, et aucune alerte n'a été trouvée.
- Les statistiques par question, recommandées au rapport 14 (M3), n'ont pas été recherchées ici.

## 10. Plan proposé

Effort : S = une journée ou moins, M = 2 à 4 jours.

### Lot 0 : aujourd'hui
Confirmer les trois témoignages (section 2).

### Lot 1 : avant le 1er décembre, sans décision de produit
| # | Action | Traite | Effort |
|---|---|---|---|
| 1 | Un vocabulaire (« thèmes », « solides », « maîtrisés ») et un seul sens pour le centre de l'anneau | P1, P2 | S |
| 2 | Annales dans l'historique ; annales filtrées sur l'examen ; minis hors de la « meilleure note » | P3, P4, P5 | S à M |
| 3 | Onglet actif amené à l'écran ; Réviser allumé sur Fiches et Examens blancs | P7 | S |
| 4 | La séance écarte les exercices faits tant qu'il en reste d'autres | E1 | S |
| 5 | Une copie libre et vide ne crée plus de révision | E3 | S |
| 6 | L'e-mail se tait quand l'objectif est atteint | E5 | S |
| 7 | Pastilles de Mes erreurs vers le cours ; `a_quiz` et `a_cours` pour les annales | 5.2 | S |
| 8 | Lien de retour d'une note vers sa fiche | 5.2 | S |

### Lot 2 : décembre, faire circuler
| # | Action | Traite | Effort |
|---|---|---|---|
| 9 | Bilan parent : dernières notes d'examen blanc, évolution, jours actifs toutes activités | E4 | M |
| 10 | Les copies notées en conditions réelles alimentent la maîtrise et Mes erreurs (**décision** : quel poids pour une auto-notation ?) | E2 | M |
| 11 | Une seule définition écrite de « maîtrisé » et d'« activité du jour », utilisée partout | E7, E8 | M |
| 12 | « Où cette notion est tombée » sur le cours ; « Quiz sur ces thèmes » sur l'épreuve | 5.2 | M |
| 13 | Raccorder les Fiches EduKora avant publication | 8 | M |
| 14 | Une page d'admin hebdomadaire : entonnoir, rétention, question de satisfaction, signalements avec énoncé | 4, 9 | M |

### Lot 3 : janvier et après
- GCE : rattacher les thèmes aux cours et quiz, en commençant par les plus fréquents.
- Fusionner les thèmes en double, d'abord parmi ceux qui tombent.
- Une entrée unique « À revoir aujourd'hui » au-dessus des quatre files.

### Mesures de réussite
| Indicateur | Aujourd'hui | Cible proposée |
|---|---|---|
| Écrans affichant un chiffre différent pour le même fait (P1 à P5) | au moins 3 écarts vus | 0 |
| Poids des thèmes GCE avec cours et quiz | 38 à 49 % | 70 % sur les cinq matières les plus passées |
| Part de « cette séance m'a aidé » | non mesurée | mesurer d'abord, fixer ensuite |
| Retour à J+7 | calculable, non lu ici | lu chaque lundi |

## 11. Ce que je ne recommande pas

- **Ajouter un tableau de bord élève de plus** : il y en a déjà trop qui se recouvrent.
- **Allumer la note estimée** avant E6 et la relecture par un enseignant.
- **Ajouter des collectes** avant d'avoir restitué celles qui existent, hors la question de satisfaction.

## 12. Suite donnée le 2026-11-25 (committée le même jour, non déployée)

Les sections 1 à 11 décrivent l'état **avant** ces correctifs.

### 12.1 Fait

| # | Ce qui change | Où |
|---|---|---|
| 1 | Même anneau et même nombre au centre sur l'accueil et sur Ma progression ; « thème » à la place de « savoir » ; « solide » à la place de « consolidé » | `lib/maitrise.ts` (`anneauPreparation`) |
| 2 | Annales dans l'historique ; annales et « points perdus » filtrés sur l'examen préparé ; meilleure note et tendance sur les épreuves entières | `lib/copies.ts`, `simulations/views.py` |
| 3 | Onglet actif de Réviser amené à l'écran ; onglet du bas allumé sur Fiches et Examens blancs | `ReviserTabs.tsx`, `BottomTabBar.tsx` |
| 4 | La séance écarte les exercices faits tant qu'il en reste d'autres | `quiz/services.py` |
| 5 | Une copie libre et vide ne programme plus de révision | `inedit/notation.py` (`copie_libre_vide`) |
| 6 | L'e-mail de rappel se tait quand l'objectif du jour est atteint | `relances/services.py` |
| 7 | Mes erreurs mène au cours ; liens quiz et cours exacts après une annale | `inedit/liens.py` |
| 8 | « Rouvrir la source » d'une note ouvre le bon examen et la bonne matière, notes déjà gardées comprises | `GET /memos/fiches/<id>/` |
| 9 | Bilan parent : notes d'examen blanc et note précédente, jours actifs toutes activités, examen préparé choisi d'abord | `relances/bilan_parent.py` |
| 10 | **En partie** : les QCM des copies en conditions réelles à l'écran comptent dans la maîtrise | `quiz/copies.py` |
| 11 | Définitions écrites de « maîtrisé », « jour actif » et « jour réussi » ; le 4e cran de la jauge s'appelle « Très solide » | `quiz/definitions.py` |
| 12 | « Où cette notion est tombée » sur le cours ; « Quiz sur ces thèmes » sur la fiche et le lecteur d'épreuve ; bouton quiz sur la page d'un thème | `catalog/liens_contenus.py` |
| 13 | **En partie** : une fiche mène à son quiz, son cours et ses sujets ; ouvertures et fiches gardées mesurées | `memos/services.py` |
| 14 | « Cette séance t'a aidé ? » (une fois, à partir de la 3e séance) ; page d'admin « Le point de la semaine » ; signalements avec matière et énoncé | `analytics/semaine.py` |
| Lot 3 | « À revoir aujourd'hui » sur Ma progression : les quatre files au même endroit | `ARevoirAujourdhui.tsx` |

### 12.2 Pas fait, et pourquoi

- **Questions rédigées dans la maîtrise (10).** L'élève les note lui-même : leur poids reste à décider.
- **Erreurs d'examen dans « Mes erreurs » (10).** La page refait des questions de quiz ; une question de copie ne se rejoue pas ainsi.
- **Thème sur chaque fiche (13).** 50 des 83 fiches locales n'en ont pas : travail de contenu, à faire à la relecture.
- **GCE (lot 3).** Un rattachement automatique ne suffit pas. Parmi les thèmes pondérés tombés dans au moins 3 épreuves, ceux qui n'ont rien mais ont un voisin au nom proche pèsent 4 %, et plusieurs voisins sont d'autres notions (« network devices » et « output devices »). Sans aucun voisin : 57 % au A Level, 46 % au O Level. La plupart des matières s'arrêtent à 150 questions et 25 cours : **il faut produire du contenu**. Liste priorisée : [18-annexe-themes-gce-sans-contenu.tsv](18-annexe-themes-gce-sans-contenu.tsv).
- **Fusion des thèmes en double (lot 3).** Les variantes d'écriture sont déjà fusionnées : en simulation locale, il reste 1 groupe fusionnable et 7 en conflit de savoir officiel. Rien appliqué (une fusion supprime des thèmes). Le correctif du point 5.1 « vocabulaire éclaté » relève donc d'un regroupement par sens, à décider.
- **Hors plan** : couleurs de note différentes (P8), matières retirées encore présentes dans les révisions (E9), rappels qui visent le premier profil, recherche qui n'indexe pas les Fiches, notes de cours enregistrées sans thème.

### 12.3 À prévoir au déploiement

Migration `analytics 0020_avis_seance_et_fiches` ; reconstruire `backend` et `caddy`.

### 12.4 Vérifications

- **Interface** : typage sans erreur ; suite complète, 1 795 tests passent, 17 sont ignorés.
- **Backend** : suite complète, 3 804 tests, 2 échecs, 9 ignorés.
  - `quiz.test_cache_parcours` : la progression lit 2 requêtes de plus (QCM des copies). Test mis à jour, son module repasse (9 tests) ; la suite complète n'a pas été relancée après ce changement de test.
  - `catalog.test_frequences_cours…test_le_filtre_respecte_le_cursus_demande` : **échoue aussi sur le dernier commit sans ces correctifs**. Non corrigé.
- **Navigateur** (local, 375 x 812, compte de test BEPC) : 43 au centre des deux anneaux ; 8 examens blancs dans l'historique et sur la page dédiée ; onglet actif visible ; liens de Mes erreurs, des fiches, du cours et de l'épreuve ; bloc « À revoir ».
- **Non vus à l'écran** : la question après la séance, le retour d'une note vers sa fiche et la page d'admin (couverts par des tests). Aucun écran anglais ni visiteur contrôlé.
- « À revoir » ne donne pas de nombre pour les thèmes : la file en comptait 43 et le compteur « En révision » 37, faute de compter la même unité.
