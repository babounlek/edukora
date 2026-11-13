# Inventaire : le gratuit vu par un visiteur et par un connecté / abonné

Date : 2026-11-13. Lecture seule, rien n'a été lancé ni modifié. Trois lectures parallèles (quiz, contenus, navigation), recoupées ici. Les points marqués **[vérifié]** ont été relus dans le code après les rapports ; les autres viennent des rapports et sont à confirmer au navigateur avant de coder.

Légende : **Vis** = visiteur (non connecté, y compris un compte invité hors `/inedit/`) ; **Cnx** = connecté sans abonnement actif ; **Abo** = abonné actif sur le cursus. Classes : **A** écart d'interface pur, **B** exige une identité ou de la persistance, **C** écart commercial voulu.

## 1. Les quatre faits qui structurent tout

1. **L'invité n'existe que sur `/inedit/`.** Son jeton n'est joint qu'aux appels inédites (`api/client.ts:36-45`) et le backend lui refuse le reste (`users/authentication.py:12-23`). `AuthContext` ne le voit jamais : pour toute la coque, un invité est un visiteur. Conséquence : accueil, historique, carnet, quiz, simulation ignorent sa copie.
2. **Le quiz du visiteur est un « essai » sans session** (id 0, rien en base, état en `sessionStorage`). Les routes quiz sont `IsAuthenticated` par défaut ; seules `/quiz/essais/*` sont ouvertes (`quiz/essai.py`). C'est la source de presque tous les écarts de persistance sur le quiz : historique, reprise, rejeu, XP, série, parcours.
3. **Le contenu lu est identique** : épreuve vitrine, cours libre, exercices vitrine, déroulé du quiz (mêmes composants, mêmes explications, mêmes confettis et sons). Les écarts sont dans ce qui entoure la lecture : suivi, mémoire, raccourcis.
4. **Le payant est montré avec un verrou et un aperçu** (sujet public, carte « exercices d'application » avec nombre et niveaux, teaser de 2 thèmes fréquents, énoncé d'aperçu d'une inédite payante). Seuls la mini-inédite de la semaine et le lecteur du corrigé non vitrine sont masqués.

## 2. Écarts à traiter, par classe

### A. Interface pure (alignables sans toucher à l'identité)

| # | Écart | Où | Gravité |
|---|---|---|---|
| A1 | **Boutons qui promettent ce que le serveur refuse au Cnx** : Fiche/Correction PDF du quiz (403 « abonnement requis » au clic), « Refaire celles que j'ai ratées » (403). **[vérifié]** `refaire_ratees_view` n'a pas l'exception vitrine de `start_session` (`quiz/views.py:1493` contre `:518`) alors que le bouton est affiché. | `QuizFichePdfButtons.tsx`, `QuizResultPage.tsx:475-523` | Haute : le gratuit paraît cassé |
| A2 | **« J'ai traité cet exercice » affiché au visiteur** dans le lecteur d'épreuve, sans branche sur la connexion. **[vérifié]** `ValiderResolution` est rendu inconditionnellement (`EpreuveReaderPage.tsx:243`) ; l'échec donne le toast d'erreur générique `ed.valide_erreur`. Un faux « session expirée » est probable (POST strict) mais non vu au navigateur. `ThemeExerciceLecturePage` fait la bonne branche (invitation à se connecter). | `EpreuveReaderPage.tsx:243,388` | Haute |
| A3 | **Cnx sur le chemin « essai »** (pas de cursus déclaré) : « t'aurait rapporté N points » est affiché, jamais crédité, et la phrase « crée ton compte » est masquée dès `isAuthenticated`. | `QuizEssaiResultPage.tsx:133` | Moyenne |
| A4 | **Nombre de questions et chrono absents pour Vis et Cnx** (10 fixe, aucun chrono) alors que le backend les accepte pour une session réelle ; l'essai plafonne à 15 et désactive le chrono côté lecteur. | `QuizStartPage.tsx:517-778`, `QuizSessionPage.tsx:130` | Moyenne |
| A5 | **Badge « Gratuit » des cours trompeur** : posé seulement si le cours est cité par une vitrine, alors que tout cours est lisible. Laisse croire que les autres sont payants. | `CoursCard.tsx:69` | Moyenne |
| A6 | **Record de score** : le Vis en a un (localStorage), le Cnx et l'Abo n'ont qu'un record de temps. Écart inversé. | `lib/quizEssai.ts:82-130` | Basse |
| A7 | **Lien de défi** : un Abo qui l'ouvre joue en mode essai (pas d'XP, pas d'historique). Pas de bandeau de défi en session réelle ; « Partager » en session pour le Vis seulement. | `QuizEssaiLancementPage.tsx:36-41` | Basse |
| A8 | **Quota PDF épuisé** : le CTA du Vis est « Connecte-toi », qui n'apporte pas un PDF de plus (3/jour pour Vis et Cnx). | `QuotaPdfInfo.tsx` | Basse |
| A9 | **Compte à rebours** (`CompteAReboursBadge`) invisible pour un visiteur qui a pourtant choisi son examen (la pastille d'examen, elle, s'affiche). | `CompteAReboursBadge.tsx:25-28` | Moyenne |
| A10 | **Navigation** : 5 liens pour le Vis contre 3 pour le connecté avec examen ; barre d'onglets mobile absente tant qu'on n'est pas connecté avec cursus. | `Header.tsx:389-409`, `BottomTabBar.tsx:31` | À arbitrer |
| A11 | **Flash de vitrine** pour l'abonné tant que `getMe` n'a pas répondu (déjà connu, noté CLS). | `CataloguePage.tsx:760-768` | Moyenne |
| A12 | **Aperçu absent** : `SeanceDuJour` et `MiniDeLaSemaine` ne sont jamais montrées à un visiteur, qui ne peut donc pas « goûter » ce que l'examen choisi débloque. | `SeanceDuJour.tsx:73-81`, `AccueilEleve.tsx:138` | À arbitrer |
| A13 | **Code mort** : `CoursDetailPage` redirige aussitôt vers le lecteur (`previewCours` inutilisé). | `CoursDetailPage.tsx:82-84` | Nettoyage |

### B. Identité et persistance (le cœur de la demande)

| # | Écart | Cause |
|---|---|---|
| B1 | **Quiz du visiteur : rien n'est gardé.** Pas d'historique, pas de consultation figée, pas de rejeu à l'identique, pas de carte « Reprendre » (l'essai survit seulement à un rechargement, dans l'onglet). « Refaire » donne un tirage différent. | Pas de `QuizSession` pour un anonyme ; jeton invité interdit hors `/inedit/` |
| B2 | **XP, objectif du jour, niveau, série, classement, bonus de révision** : le Vis voit des points simulés ; le Cnx en session réelle a l'XP réel (aucun verrou d'abonnement, sauf classement hebdo réservé aux abonnés). | Crédités sur un profil |
| B3 | **Parcours, maîtrise, « à réviser »** : Vis redirigé vers `/connexion` ; Cnx voit la structure avec cadenas (choix produit déjà documenté, voir C). | Lecture de la progression du profil |
| B4 | **Lecture** : « Lu », « Reprendre ma lecture », signets, notes, « compris », progression, coches d'exercices faits, XP de lecture, carnet, historique de lecture : tous absents pour le Vis. | Routes `IsAuthenticated` (`access/views.py:269,309,362,403,419`) |
| B5 | **Inédite gratuite via invité** : bien gérée à l'intérieur de `/inedit/` (copie, chrono, rattachement à l'inscription), mais les listes et l'accueil ne reçoivent pas le jeton (la carte reste « Essayer gratuitement » malgré une copie en cours), `/historique` et `/carnet` lui sont fermés, le choix du mode n'apparaît qu'après le premier clic, et un localStorage vidé perd la copie. | Portée du jeton |
| B6 | **Simulation d'annale** : pas de bouton pour le Vis sur une vitrine CORR (`EpreuveDetailPage.tsx:290`) ; l'API exige un compte. | `simulations/views.py:418` |
| B7 | **Partage avec code de parrainage** : seulement connecté. Mineur. | `BoutonPartager.tsx:34` |

### C. Écarts commerciaux voulus (à ne pas aligner, seulement à rendre lisibles)

- Un seul thème de quiz gratuit par matière et par cursus (`quiz/gratuits.py`) ; fiches et corrections PDF réservées aux abonnés ; parcours : maîtrise et quiz par savoir verrouillés pour le Cnx ; classement complet des thèmes fréquents (teaser de 2) ; classement hebdo.
- Exercices d'application des cours, corrigés des épreuves non vitrine, simulation de ces épreuves, mini-inédites, inédites payantes.
- Quota PDF 3/jour (Vis, Cnx) contre 12/jour (Abo), plus plafonds réseau et budget global pour les anonymes.
- Compte, paiement, mes accès, parrainage, mode parent et PIN, push et rappels, langue verrouillée par l'abonnement.

## 3. Ce qui se perd à l'inscription ou à la connexion

- **Examen choisi** : poussé sur le compte seulement si celui-ci n'en a pas ; la valeur en attente est effacée dans tous les cas, même si l'appel échoue (`AuthContext.tsx:80-90`). Perte silencieuse. Ordre d'exécution avec le calcul de destination : non vérifié.
- **Quiz d'essai et records** : jamais transmis au compte (sessionStorage / localStorage).
- **Filtres de liste** : effacés à la connexion et à la déconnexion.
- **Pays** : pas de champ sur le compte ; la connexion écrase le pays du navigateur par celui du cursus.
- **Langue** : écrasée par la langue du cursus si imposé.
- **Copie d'inédite de l'invité** : transmise ; mais si le compte est déjà utilisé, XP et révisions de l'invité sont abandonnés.
- Résidus après déconnexion sur appareil partagé : recherches récentes, cache d'accueil, `edukora.push.invite`.

## 4. Décisions que seul le produit peut trancher

1. **Étendre l'invité au quiz** (jeton accepté sur `/quiz/`, session réelle limitée aux thèmes vitrine, rattachement à l'inscription). C'est le levier qui règle B1, B2 et une partie de B4 d'un coup, au prix d'un volume de lignes à plafonner et à purger (`purger_invites` n'est pas encore planifiée en prod).
2. **Le visiteur gagne-t-il de l'XP et une série** pendant l'essai, ou garde-t-on les « points simulés » ?
3. **Montrer un aperçu** de la séance du jour et de la mini-inédite au visiteur qui a déclaré son examen.
4. **Navigation** : un seul menu pour tous, ou on garde le menu élève réservé au connecté avec examen ?
5. **Record de score** : le donner à tous, ou le retirer au visiteur.

## 4 bis. Décisions prises le 2026-11-13 (lot 3, « mémoire »)

1. **Invité pour le quiz gratuit : oui.** Un visiteur qui lance un quiz gratuit reçoit un compte invité, comme pour les inédites. Sa séance est réelle (historique, reprise, rejeu, « refaire les ratées »), transmise à son compte à l'inscription. Seuls les thèmes gratuits restent jouables (le garde de `start_session` s'applique déjà à un invité, qui n'a aucun abonnement).
2. **Points XP réels** pour l'invité, repris par le compte neuf à l'inscription ; le classement hebdomadaire reste réservé aux abonnés.
3. **Portée : le quiz seulement.** Le suivi de lecture (« Lu », reprise, signets, notes, exercices faits, carnet) et la simulation restent réservés aux comptes ; on mesure d'abord l'effet sur les inscriptions et le volume d'invités avant d'élargir.
4. Non tranchés, hors lot 3 : aperçu de la séance du jour / mini-inédite pour le visiteur, navigation unique.

### Plan de réalisation (à lancer sur accord)

**Backend**
- `users/authentication.py` : ouvrir à l'invité UNE LISTE FINE de routes quiz (démarrer, répondre, terminer, séance en cours, historique d'une séance, rejeu, refaire les ratées), pas `/quiz/` en bloc : parcours, plan du jour, bilan et classement n'ont pas de sens pour un invité.
- `users/invites.py::rattacher` : compte déjà utilisé, faire passer aussi les `QuizSession` (et leurs réponses) sur son profil actif ; compte neuf : le profil entier (XP compris) devient le sien, ce qui marche déjà. À vérifier : XP et révisions d'un invité quand le compte est déjà utilisé (aujourd'hui abandonnés).
- Garder les routes `/quiz/essais/*` comme repli (création d'invité refusée par un plafond, stockage bloqué).
- Tests : accès invité aux seules routes prévues, refus ailleurs, thème payant refusé, rattachement des séances, XP repris.

**Frontend**
- `api/client.ts` : joindre le jeton d'invité aux routes quiz ouvertes ; `useEssaiSansCompte`-équivalent pour les pages quiz (l'invité reste « non authentifié » pour la coque).
- Lancement : `EssaisGratuitsQuiz`, `QuizEssaiLancementPage` (lien de défi) et l'aperçu des matières créent l'invité puis démarrent une vraie séance ; repli sur l'essai actuel si la création échoue.
- `QuizSessionPage` / `QuizResultPage` / `QuizHistoriquePage` / carte « Reprendre » : accepter l'invité ; bilan XP réel ; carte « Garde ta copie » à l'inscription (comme `BandeauEssaiSansCompte`).
- Retirer les points simulés et le record local pour les séances d'invité.

**Production** : migration `users` 0020, rebuild backend + caddy, **planifier `purger_invites`**, et trancher la mention dans la politique de confidentialité (aucune donnée personnelle pour un invité).

**Risques** : volume de comptes invités (plafonds 60/IP/h et 5000/jour déjà en place), un jeton rejouable sur des routes non prévues (d'où la liste fine), la fusion à l'inscription d'un compte déjà utilisé.

## 5. Ordre de travail proposé

1. **Lot « les promesses fausses »** (A1, A2, A3, A5, A8) : petit, sans identité, corrige ce qui fait paraître le gratuit cassé. À faire en premier.
2. **Lot « mêmes réglages »** (A4, A6, A7, A9) : nombre de questions, chrono, record, décompte, aligne l'écran de démarrage.
3. **Lot « mémoire »** (décision 1, puis B1 à B5, plus la perte à l'inscription) : le gros chantier, à ne lancer qu'après arbitrage.
4. **Lot « coque »** (A10 à A12) : après la décision 4, à vérifier au navigateur.

## 6. Non vérifié

Aucun rendu navigateur ; le faux « session expirée » du A2 est déduit du code ; le comportement d'un visiteur qui ouvre à la main `/quiz/session/:id` (401 puis échec du refresh) ; le contenu de `plan_du_jour` pour un Cnx (donc `FlammeSerie` et `SeanceDuJour` pour lui) ; le cache hors-ligne du service worker pour les routes quiz ; le plafond serveur de `n` pour `start_session` ; `QuotaPdfPastille` ; les composants `Moments`, `AccueilEleve` hors son montage de `MiniDeLaSemaine`.
