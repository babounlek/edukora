# Gogo, GCE O Level : connexion par code familial (local) - 2026-10-19

## 1. En-tête

- Date : 2026-10-19. Début 20:32:57 UTC, fin 20:39:40 UTC environ (durée totale environ 6 min 40 s).
- Terrain : local (http://localhost).
- URL de départ : http://localhost (accueil ; redirigée vers /cm puis /en/cm après passage en anglais).
- Persona : Gogo, Form 4, Cameroun, prépare le GCE O Level, anglophone, smartphone ; un parent tape le code.
- Viewport : mobile 375x812 (remis au preset desktop à la fin).
- Compte : connexion par code envoyé à l'adresse familiale (mboapages@gmail.com), code à saisir par l'humain.
- Mode d'exécution : sous-agent à contexte neuf.
- Attente du code : une seule demande de code (POST /auth/email/request/ à environ 20:34:50 UTC). Attente observée de 20:35:03 à 20:39:34 UTC, soit un peu plus de 4 minutes. Aucun code n'a été saisi dans l'écran pendant ce temps : le champ est resté vide.

## 2. Verdict de la mission

**Abandonnée à l'étape 4 (saisie du code) : code non saisi.** Je n'ai donc ni choisi de profil, ni vu l'accueil connecté, ni lancé le quiz de maths. Ce que l'élève retient : l'entrée en anglais est facile à trouver et la connexion par e-mail est claire, mais avant même de se connecter on lui pose deux fois la question de son examen, et il n'a pas pu voir si « son espace » l'attend sous son prénom.

Les étapes de connexion après le code (choix du profil Gogo, séance du jour, compte à rebours, abonnement, menu connecté, liste des matières GCE, quiz de maths) n'ont PAS été testées.

## 3. Journal (extrait significatif)

1. Accueil http://localhost -> redirigé vers /cm. Je vois une fenêtre « Quel examen prépares-tu ? » avec BEPC, Probatoire, BAC, puis un encadré « Tu prépares le GCE (sous-système anglophone) ? » avec un bouton « Switch to English » et « Passer ». Je comprends que ce n'est pas pour moi, tout est en français, sauf ce bouton. Je veux l'anglais. Je clique « Switch to English ».
2. Transition : fenêtre floutée, texte « Loading... » / « Skip » pendant environ 2 s. Le titre d'onglet reste en français un instant puis passe en anglais.
3. /en/cm : la fenêtre redevient « Which exam are you preparing? » avec GCE O Level et GCE A Level. Je clique « GCE O Level ».
4. Nouvelle fenêtre « Are you preparing the GCE O Level? » avec « Yes, this is my exam ». Je trouve ça redondant (je viens de cliquer). Je clique « Yes ».
5. Accueil anglais : « Every day, we tell you what to revise. », bouton vert « Read a free solution », bouton « Free quiz, no account needed », bouton « Log in » en haut à droite en vert (très visible). Image d'une lycéenne en uniforme. Je comprends le principe de la séance quotidienne de 25 minutes. Chiffres : 512 past papers, 785 lessons, 23 subjects. Exemple réel : Mathematics GCE O Level 2019 Paper 2, avec formules lisibles.
6. Je clique « Log in » : écran « Log in / It only takes a few seconds. » avec « Continue with Google » (au premier instant il était écrit « Continuer avec Google » en français), champ « Email address », bouton « Get the code », liens « I already have a code » et « Use my phone number instead ».
7. Je tape mboapages@gmail.com et je clique « Get the code » : le bouton passe à « Sending... » pendant environ 12 secondes sans autre retour (inquiétant pour un élève impatient).
8. Écran « Code sent to mboapages@gmail.com. / Code received by email [123456] / This code is valid for 5 minutes. », boutons « Confirm » (grisé), « Resend the code (55s) » en compte à rebours puis actif, « Change address ». Je comprends que mon parent doit regarder sa boîte mail. Rien ne dit de regarder dans les spams ni de qui vient le mail.
9. Attente de plus de 4 minutes (une pause de 10 s à la fois) : l'écran ne change pas, aucun message supplémentaire (ni expiration, ni rappel). Le compte à rebours de renvoi se termine après 60 s puis « Resend the code » devient actif.
10. Abandon : code non saisi. Menu hamburger ouvert pour observation : Home, Past papers (point jaune), Lessons, Quiz, Pricing, bascule FR/EN (EN actif), sélecteur de pays « Cameroon », mode sombre.

## 4. Ce qui marche bien

- Le bouton « Log in » est unique, vert, en haut à droite, visible tout de suite.
- Le passage à l'anglais est proposé dès la première fenêtre pour les anglophones (« Switch to English »), et l'URL, le titre d'onglet, la fenêtre et la page passent bien en anglais (/en/cm).
- Une fois en anglais, tout le contenu de l'accueil visible est en anglais et cible le GCE (O Level et A Level) : pas d'examen francophone dans la liste des choix, ni dans l'accueil, ni dans les exemples (Mathematics GCE O Level 2019, Chemistry GCE O Level Original Paper).
- L'écran de connexion est simple : trois modes (Google, e-mail avec code, téléphone), peu de champs, libellés clairs (« Get the code », « Confirm », « Change address »).
- Le message après la demande indique à qui le code a été envoyé et sa validité (5 minutes), avec un exemple de format (123456) et un renvoi temporisé.
- Chargement de l'accueil rapide en local ; l'exemple de corrigé affiche les formules correctement et propose un lien vers le cours.
- Le menu est court (5 entrées) et propose FR/EN et le pays.

## 5. Frictions

| Id | Sév. | Catégorie | Étape | Observé | Attendu | Preuve | Confiance |
|---|---|---|---|---|---|---|---|
| F1 | S3 | UX / langue | 1 | Un élève anglophone arrive sur une page entièrement en français et une fenêtre « Quel examen prépares-tu ? » qui ne propose que BEPC, Probatoire, BAC. Le GCE n'apparaît que dans un encadré en pointillés sous les choix, avec le texte en français « Tu prépares le GCE (sous-système anglophone) ? » ; seul le bouton est en anglais. | Un accès au GCE aussi visible que les autres examens, ou une langue d'accueil choisie d'après le navigateur ; l'encadré lisible dès la première ligne pour un anglophone. | Capture de l'accueil : fenêtre blanche avec 3 gros boutons français et l'encadré GCE en dessous, plus petit. | Moyenne |
| F2 | S3 | UX | 3-4 | Deux fenêtres successives pour le même choix : « Which exam are you preparing? » (choix GCE O Level) puis « Are you preparing the GCE O Level? » avec « Yes, this is my exam ». Un « Skip » est présent à chaque étape. | Une seule validation, ou pas de seconde confirmation si l'élève vient de choisir. | Deux captures : liste de choix, puis fenêtre de confirmation avec un bouton vert et un lien Skip. | Élevée |
| F3 | S3 | UX / performance | 7 | Après « Get the code », le bouton reste en « Sending... » environ 12 secondes. L'appel serveur d'envoi a fini en 200. Aucun message intermédiaire. | Retour rapide, ou message du type « E-mail en cours d'envoi, ça peut prendre quelques secondes ». | Capture : bouton vert grisé « Sending... », champ e-mail rempli, bouton Google grisé. | Moyenne (terrain local, envoi SMTP) |
| F4 | S3 | UX | 8-9 | L'écran du code ne dit pas dans quelle boîte chercher (spam), de quel expéditeur, ni que le parent peut saisir le code à ta place sur un autre appareil. Après 5 minutes de présence sur l'écran il n'y a aucun message : ni rappel, ni expiration. | Une aide courte « Pas reçu ? Regarde les spams / l'expéditeur est EduKora » ; message d'expiration lisible à la fin des 5 minutes. | Capture de l'écran « Code sent to... » : texte « This code is valid for 5 minutes » seul, sans aide. | Moyenne |
| F5 | S4 | langue | 6 | Le bouton Google est affiché d'abord en français (« Continuer avec Google ») puis bascule en « Continue with Google » après un instant, sur une page anglaise. | Libellé d'emblée dans la langue de l'interface. | Deux captures du bouton, la première en français. | Moyenne |
| F6 | S4 | langue | 2 | Pendant la transition vers l'anglais, le titre d'onglet reste « EduKora - Corrigés BEPC, Probatoire et BAC au Cameroun » (français) environ 2 secondes ; pendant ce temps la fenêtre floutée affiche « Loading... » et « Skip ». | Titre cohérent dès l'URL /en/cm. | Capture de la fenêtre floutée avec le titre d'onglet français. | Faible |
| F7 | S4 | confiance/vente | 5 | L'accueil annonce « 23 subjects covered » pour le GCE comme pour la version francophone (même nombre), alors que le nombre de papers et de leçons diffère. | Un chiffre vérifiable propre au GCE. | Texte des deux accueils (FR : 23 matières, EN : 23 subjects). | Faible |
| F8 | S4 | confiance/vente | 5 | Dans l'extrait de corrigé GCE, le prix est annoncé en FCFA ; pas de mention de ce que couvre l'abonnement pour le GCE O Level en dehors de « valid until your exam ». | Un résumé clair de ce qui est inclus. | Texte du bas de l'accueil : « One subscription, valid until your exam: 15 000 FCFA per child... ». | Faible |

Remarque : les erreurs console (401 d'un visiteur non connecté, échec d'enregistrement du service worker) sont normales et ne sont pas comptées comme défauts.

## 6. Mesures

- Page d'arrivée (/cm) : environ 68 ressources, environ 420 Ko transférés selon le navigateur (790 Ko de corps encodés) ; chargement du document très rapide en local (environ 65 ms pour l'événement load). Estimation 3G : environ 5 à 10 s pour 420 Ko-790 Ko sur une connexion lente (non mesuré, réseau non bridé).
- Requêtes : 108 au total sur la session. Pas d'erreur serveur ; 401 attendus sur /auth/me/ et /auth/token/refresh/.
- Console : erreurs de type « 401 Unauthorized » et « An unknown error occurred when fetching the script » (service worker).
- Envoi du code : bouton « Sending... » environ 12 s (environ 20:34:38 à 20:34:50 UTC).
- Renvoi du code : compte à rebours de 60 s.
- Validité annoncée du code : 5 minutes.
- Temps jusqu'à l'abandon : environ 6 min 40 s au total, dont plus de 4 minutes d'attente du code.

## 7. Idées d'amélioration

- Choisir la langue d'accueil d'après la langue du navigateur, ou mettre l'accès GCE au même niveau que BEPC/Probatoire/BAC dans la première fenêtre (effet : un anglophone ne perd pas 4 écrans ; effort moyen).
- Supprimer la seconde fenêtre de confirmation après le choix de l'examen (effet : un clic et un écran en moins ; effort faible).
- Message intermédiaire pendant l'envoi du code (« envoi en cours, jusqu'à 30 s ») et aide « pas reçu ? vérifie les spams » (effet : moins d'abandons à l'étape du code ; effort faible).
- Afficher un message d'expiration du code à 5 minutes et proposer automatiquement « Resend the code » (effet : l'élève comprend pourquoi ça ne marche plus ; effort faible).
- Demander dès l'écran de connexion « le compte est celui d'un parent ? ton prénom sera choisi ensuite » pour rassurer les familles (effet : moins d'hésitation ; effort faible).
- Libellé du bouton Google fixé sur la langue de l'interface (effort faible).

## 8. Ce que cette session ne dit pas

- Rien sur le choix de profil, l'accueil connecté, la séance du jour, le compte à rebours, l'abonnement, le menu connecté, la liste des matières GCE ni le quiz de maths : la mission n'a pas dépassé la saisie du code.
- Pas de mesure de la motivation d'un vrai élève.
- Réseau non bridé (local, aucun bridage 3G) : les temps sont optimistes sauf l'envoi du code.
- Testeur simulé, pas un vrai élève de Form 4 ; pas de relecture scientifique du contenu.
- Connexion prévue avec l'aide d'un humain pour le code : le code n'a pas été saisi dans la fenêtre d'attente de 4 minutes. On ne sait pas si le courriel est arrivé ni après quel délai (non vérifié, par règle).
- Un seul code demandé, une seule fois, à 20:34:50 UTC environ.

## 10. Suite (opérateur)

Mission abandonnée à l'étape de saisie du code : l'attente a dépassé les 4 minutes prévues sans que le code soit saisi (l'humain n'a pas vu l'e-mail à temps). L'utilisateur s'est ensuite connecté lui-même ; le second passage est dans `2026-10-19-gogo-gce-ol-connecte-local.md` (statuts et dédoublonnage dans sa section 9). Les frictions F1 à F7 de ce rapport (accueil en français pour un élève GCE, examen demandé deux fois, 12 s sans retour après « Get the code », écran du code sans indication ni message d'expiration) restent à vérifier en phase B ; F3 est probablement l'envoi SMTP réel, propre au local.
