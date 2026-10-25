# Guyguy (3e, BEPC) : synthèse et propositions pour rendre Edukora attrayant

- Date : 2026-10-25 · Terrain : local · Commit : 8be75ff7
- Sources : deux passes de Guyguy en sous-agents à contexte neuf (phase A, navigateur seul)
  - Visiteur anonyme, M1+M2+M3 : `2026-10-25-guyguy-visiteur-M1-M2-M3-local.md`
  - Abonné connecté, M8+M4+M5 : `2026-10-25-guyguy-abonne-M8-M4-M5-local.md`

## Constat en trois lignes

Aucun S1 ni S2 : le site fonctionne et rassure. Mais Q8 « fun ou chiant » = 3/5 des deux côtés et Q4 « je reviens demain ? » n'est jamais « demain ». Les meilleurs moments sont tous des **récompenses** (écran de fin de quiz connecté : +37 points qui défilent, objectif du jour, « Bravo ! »). Les pires sont tous des **corvées sans retour** (s'auto-noter, murs de texte, 0,5/20 après avoir fait l'effort).

## Ce qui existe déjà et marche (à ne pas casser)

- Quiz sans compte en 4 clics, BEPC présélectionné, matières avec icônes colorées.
- Barre de progression en segments qui prend la couleur du résultat.
- Messages qui encouragent sans humilier (« Presque ! », « Bon début ! », « Pas tout à fait, mais c'est comme ça qu'on retient »).
- Écran de fin de quiz connecté : anneau, points qui défilent, objectif du jour, séance validée, semaine, partage du score par WhatsApp.
- Reprise en un tap (« Quiz en cours 2/6 »), cours lisibles sur mobile avec passerelle vers les exercices, énoncés locaux (FCFA, Yaoundé, Mbouda), « Lire sans réseau », corrigé 2026 libre.
- Du code de sons existe, un objectif quotidien réglable existe, un compte à rebours J-207 existe.

## Propositions, classées par effet / effort

### A. Faible effort, fort effet (à faire d'abord)

| # | Proposition | Preuve chez Guyguy | Détail concret |
|---|---|---|---|
| A1 | **Donner au visiteur la même récompense que l'abonné** à la fin d'un quiz d'essai | Visiteur : résultat « 3/5 » sec, score effacé à la fermeture, humeur retombée ; abonné : +2 sur le même écran | Mêmes points qui défilent et même anneau en essai anonyme, avec « Crée ton compte gratuit pour garder tes 27 points ». Garder le dernier score en `localStorage` et l'afficher au retour (« Ton record : 3/5, bats-le »). Transforme l'écran le plus sec en moment d'inscription naturel. |
| A2 | **Ne plus afficher « 0,5 / 20 » ni « Tu as perdu 19,5 points »** tant que l'élève n'a pas noté tous ses critères | Creux de la session (-2), trophée sur 0,5/20 | Afficher « Note à compléter : 3 questions sur 7 notées », barre de progression de notation, trophée et « points perdus » seulement quand la note est complète. À défaut, supprimer le vocabulaire de perte : « Il te reste 19,5 points à aller chercher ». |
| A3 | **Aligner les promesses et la réalité** | « Quiz express 10 questions jusqu'à 100 points » : 6 questions et 20 points | Afficher les vrais chiffres, ou rendre le quiz conforme. Une promesse non tenue casse la confiance d'un ado plus vite qu'un défaut d'ergonomie. |
| A4 | **Moins de bandeaux au premier écran** | « Choisis ton examen » + « Switch to English » = environ 40 % du premier écran sur toutes les pages vues | Replier le bandeau après le premier choix d'examen ; ne pas le remettre à chaque page. |
| A5 | **Micro-célébrations visibles et audibles** | « Le Bravo, c'est tout petit » ; sons réglables mais cachés dans Mon compte | Agrandir le « Bravo ! », petit rebond CSS + vibration courte sur bonne réponse, confettis légers (CSS, pas de bibliothèque, la data est comptée) en fin de quiz réussi. Sons activés par défaut avec un bouton volume visible dans l'en-tête. |
| A6 | **Visibilité des réglages de motivation** | Objectif du jour, sons et rappels cachés dans « Mon compte » (menu à 3 entrées) | Raccourci « Mon objectif : Régulier 20 pts » cliquable depuis l'accueil et l'écran de fin de quiz. |
| A7 | **Cours : le 2 minutes d'abord** | 5 boutons avant le titre, intro en italique de 11 lignes, page de 10,7 écrans | Résumé en 3 cartes (règle, exemple en 5 étapes, piège) en haut ; l'intro et le détail repliés ; un seul bouton principal « Faire les exercices ». |
| A8 | **Lien « Passer en français » inutile** | Arrivée sur une page GCE en anglais alors que le navigateur est en français | À vérifier d'abord (le navigateur du test est peut-être en `en` côté pane) ; si confirmé, choisir la langue d'accueil d'après `Accept-Language` pour un visiteur sans choix. |

### B. Effort moyen, c'est là que se joue l'envie de revenir

| # | Proposition | Preuve | Détail concret |
|---|---|---|---|
| B1 | **Une réponse à toucher, pas une auto-notation** | « C'est moi qui me note ? Je peux cliquer Réussi sans rien faire. » Q1/Q3 des deux passes, 6 questions sur 6 en maths | Pour les questions dont la solution est un nombre, une expression courte ou un choix : champ de réponse ou 4 choix (les distracteurs viennent des « erreurs classiques » déjà écrites dans les cours), verdict instantané « Excellent ! +10 points » ou « Pas tout à fait ». Garder l'auto-notation pour les questions rédigées. À piloter sur un thème de maths avant d'étendre. |
| B2 | **Une vraie série de jours** | Seule une « série de bonnes réponses d'affilée » est visible ; la semaine L à D n'apparaît qu'à la fin d'un quiz | Flamme « J4 » dans l'en-tête, jour de repos offert (1 « glaçon » par semaine) pour ne jamais culpabiliser. Garder l'objectif du jour existant comme moteur. |
| B3 | **Niveaux et titres sur l'XP existant** | « Niveaux, badges, titres : rien vu » | Paliers : Débutant, Malin, Costaud, Champion du BEPC (à nommer avec des élèves). Barre « encore 40 points pour passer Costaud » sur l'accueil. |
| B4 | **Points partout, pas seulement dans les quiz** | « J'ai compris » et « Je l'ai fait » ne rapportent rien à l'écran ; Ma progression : anneau 0 %, 1 savoir sur 1101 | +5 pour un cours lu jusqu'au bout, +10 par exercice, le tout compté dans l'objectif du jour. Dans Ma progression, montrer un petit total par thème (« 2/6 ») plutôt qu'un 0 % sur 1101. |
| B5 | **Un vrai défi entre potes** | « Défier un camarade » existe mais « je ne sais pas ce que mon pote voit » ; Q5 = 5/10 des deux côtés | Le lien ouvre le même quiz chez le copain, sans compte, avec le score du défieur en tête (« Brice a fait 4/5. Bats-le ! »). Résultat renvoyé à l'expéditeur par le même lien. Pas de classement public (mineurs). |
| B6 | **Un seul chemin, pas 17 cours quasi identiques** | Recherche « système d'équations » : 17 cours aux titres presque pareils, choix au hasard | Mettre en tête « Ton prochain cours » (le parcours par thème existe déjà), regrouper les variantes, afficher durée et niveau. |
| B7 | **Quiz « encore une » en fin de partie** | Seul « Refaire cet essai » est proposé | Boutons « 5 questions de plus », « Même thème, plus dur », « Bats ton score ». |
| B8 | **Une inédite courte** | Inédite complète = corvée de 7 questions x 4 critères | « Mini-brevet 20 min » (2 exercices), avec le même bilan par compétence qui plaît déjà. |

### C. Effort plus élevé, identité du site

| # | Proposition | Détail |
|---|---|---|
| C1 | **Une mascotte avec une voix** | Le logo livre + toque peut s'animer : réagit au résultat, parle comme un grand frère (« Frère, c'est du système, tu gères »). Elle porte aussi les rappels. Registre à valider avec de vrais élèves de Douala et Yaoundé. |
| C2 | **Duel 60 secondes et mini-jeux de révision** | Vrai/faux éclair, associer terme et définition, « question du jour » à jouer en 30 s ; pensé pour jouer dans un taxi avec peu de data. |
| C3 | **Badges** | Premier quiz, 3 jours de suite, thème maîtrisé, défi gagné ; affichés sur Ma progression. |
| C4 | **Boucle sociale encadrée** | Défis entre amis connus, classement de classe optionnel avec pseudo et accord du parent, en lien avec l'espace parent déjà existant. |

## Ordre conseillé

1. A2 puis A1 : un creux qui blesse et un écran sec, correctifs courts.
2. B1 (pilote sur un thème de maths) : c'est le point qui ennuie le plus, et il se voit sur 6 questions sur 6.
3. B2 + B3 + B4 ensemble : série, niveaux et points partout forment une seule boucle ; en séparer un la rend creuse.
4. B5 puis C1 : le canal d'arrivée est le bouche-à-oreille WhatsApp, donc un défi qui se partage vaut plus qu'une page de plus.

## Comment savoir si ça marche

Rejouer Guyguy avec le même persona et les mêmes missions (suivi dans `satisfaction.md`) : l'objectif est Q8 passant de 3 à 4 et un Q4 « demain » (aujourd'hui jamais atteint), avec un écart d'au moins deux points sur une des deux notes avant de conclure. Les vraies mesures sont la rétention J1/J7 de l'app `analytics`, dont le vocabulaire d'évènements est fermé côté backend : tout nouvel évènement de gamification demandera de l'étendre.

## Limites

- Satisfaction **simulée** : un indice relatif, pas l'avis d'élèves réels. Les propositions sont des hypothèses à tester avec de vrais élèves de 3e.
- Réseau non bridé, pas un vrai téléphone ; poids de l'arrivée mesuré : 78 requêtes, environ 239 Ko transférés.
- Un seul thème de quiz approfondi côté visiteur, une seule matière approfondie côté abonné. Les sons n'ont pas été écoutés.
- Certaines frictions du compte de test (« Ce thème t'a déjà posé problème » juste avant « jamais travaillé », deux boutons « Reprendre ») viennent peut-être de l'historique du compte : à confirmer avant d'agir.
- 3 erreurs console « An unknown error occurred when fetching the script » vues dans les deux passes, cause non investiguée (phase B non demandée).
