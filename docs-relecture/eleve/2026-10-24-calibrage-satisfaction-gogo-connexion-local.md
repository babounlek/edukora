# Session élève : Gogo / connexion par e-mail familial + séance de maths du jour / local

- Date et heures UTC : début 2026-10-24T14:26:24Z, fin 2026-10-24T14:32Z (dernière action utile 14:31:31Z, abandon)
- Terrain : local ; commit local : non relevé (la session n'avait pas le droit de lire le projet) ; URL de départ : http://localhost/
- Persona : Gogo, 15 ans, Form 4, GCE O Level, Cameroun anglophone, smartphone familial, data comptée ; appareil émulé : 375x812 (mobile) ; compte : visiteur (jamais connectée)
- Mode d'exécution : sous-agent à contexte neuf
- Calibrage : défaut connu retrouvé ? non testé ; satisfaction calibrée ? voir « Comparaison » en bas : abandon franc obtenu avec Q1 = 2 (conforme au plafond), mais Q4 = « peut-être » et non « non » (écart avec le critère du §6 de satisfaction.md, à arbitrer par l'orchestrateur)
- Contrainte du scénario : le code de connexion part vers la boîte du parent, que Gogo ne peut pas lire. Le seul moyen de réussir serait un code affiché par le site, ce qui n'est pas le cas.

## Verdict de mission
**Abandonnée à l'étape 9** (après 2 renvois, environ 3 min 50 s après la première demande de code). Gogo retient que le site dit « Code envoyé » mais que le code va chez papa, et que quand elle redemande, il lui répond en français que l'envoi est impossible, puis de patienter.
Satisfaction en un coup d'œil : Q1 2/5 · effort 4/5 · retour peut-être · recommandation 3/10

## Journal (extrait)
Gogo écrit dans son registre. Humeur de -2 à +2.

| # | Heure UTC | Je vois / je comprends / je veux / je fais | Humeur |
|---|---|---|---|
| 1 | 14:26:24 | Je vois http://localhost/ qui m'envoie sur /cm : tout est en français (« Chaque jour, on te dit quoi réviser »), pastilles BEPC / Probatoire A / Probatoire C. Un bouton « Connexion » en haut. « Er, this is the French side, I'm doing GCE. » Je veux me connecter. Il y a « Switch to English » sous les boutons, donc je ne me perds pas. Je n'étais pas connectée (bouton Connexion visible), rien à déconnecter. | -1 |
| 2 | 14:26:40 | J'ai touché le menu par erreur (3 traits) : Accueil, Épreuves, Cours, Quiz, Prix, bascule FR/EN, liste de pays. Je le referme (le menu reste ouvert un moment, je dois tâtonner un peu). | 0 |
| 3 | 14:26:55 | Je touche « Switch to English » : le site passe à /en/cm, « Every day, we tell you what to revise », pastilles GCE O Level / GCE A Level. « Ok, now it's for me. » | +1 |
| 4 | 14:27:05 | Je touche « Log in » : page /en/login. « Continue with Google » (pas pour moi, je n'ai pas de compte Google à moi), champ « Email address », « Get the code », « I already have a code », « Use my phone number instead ». Pendant le fondu d'apparition, le bouton Google s'est affiché une seconde en français (« Continuer avec Google ») puis en anglais. C'est clair, on a 4 choix. | +1 |
| 5 | 14:27:29 | Je tape l'adresse familiale test+edukora-test-eleve-libre@exemple.local et touche « Get the code ». Le bouton passe à « Sending… » pendant environ 3 secondes (POST /auth/email/request/ : 3 104 ms, 200). Puis « Code sent to test+edukora…». | 0 |
| 6 | 14:27:42 | Écran « Code received by email » avec un champ « 123456 », « This code is valid for 5 minutes », « Nothing received? Check your spam folder: the sender is EduKora », bouton « Resend the code (54s) » qui compte à rebours. Je comprends que le code est parti, mais « c'est le mail de Maman/Papa, pas le mien, je ne peux pas le lire d'ici ». Rien à l'écran ne m'explique quoi faire dans ce cas. J'attends 10 secondes, puis un peu plus. | -1 |
| 7 | 14:28:00 | Je touche le « ? » (aide). Le panneau s'ouvre sur « Discover EduKora », « How to read this lesson », « How to work on this exercise », « How to find a past paper », « How to search », puis tout en bas « I do not receive my login code : look in your junk folder (spam): the sender is EduKora. You can also ask for a new code. » et un bouton « Write to us on WhatsApp » (non touché : ce serait envoyer un message). Rien pour « mon parent a le mail ». Le bouton X du panneau n'a pas réagi au premier toucher ; j'ai fermé avec la touche Échap. | -1 |
| 8 | 14:30:00 | Après environ 2 min 20 s d'attente, « Resend the code » est actif. Je touche (renvoi 1). « Sending… / Sending can take a few seconds… » pendant environ 25 secondes, puis un message rouge **en français** : « Envoi du code impossible pour le moment. Merci de réessayer plus tard. » (POST : 24 575 ms, 503). « Why is it in French now? And what does it mean, later when? » | -2 |
| 9 | 14:30:55 | Le bouton « Resend the code » est de nouveau actif sans compte à rebours. Je touche (renvoi 2). Réponse en 56 ms (429) : message rouge **en français** : « Merci de patienter avant de redemander un code. » Je n'ai aucun moyen de savoir combien de temps patienter. | -2 |
| 10 | 14:31:31 | Environ 3 min 50 s depuis la première demande, 2 renvois faits, toujours aucun code à saisir. J'abandonne : « I'll ask Dad tonight, I can't do my maths session now. » Pas de séance de maths vue de la journée. | -2 |

## Satisfaction (notée à chaud, avant le tableau de frictions)

| Mesure | Note | Ancrage (étape, citation, capture) |
|---|---|---|
| Q1 Satisfaction de la mission (1-5) | 2 | « I only wanted to do my maths session and I didn't even get in. » (étape 10). Pas fâchée contre le site (le début était clair, étapes 3 et 4 à +1), mais ça ne valait pas l'effort. |
| Q2 Effort (1 facile - 5 pénible) | 4 | « French first, then the code goes to Dad's mail, then it hangs 25 seconds and says nothing I can use. » (étapes 1, 6, 8) |
| Q3 Utilité pour l'examen (1-5) | 1 | Je n'ai pas vu une seule question de maths. « I'm exactly as ready as before. » (étape 10) |
| Q4 Retour | peut-être | Pourquoi : le site m'a plu au début (« Every day, we tell you what to revise », étape 3), donc je retenterai quand papa a son téléphone. Mais si ça me redit « impossible pour le moment » en français, je laisse tomber. Pas « demain » : aucun moyen d'entrer seule. |
| Q5 Recommandation (0-10) | 3 | « I can't tell my friend it works, I didn't see it work. » (étape 10) |
| Q6 Achat | sans objet | Aucune offre ni prix vus dans la session. |

Courbe d'humeur : étape 1 (-1) → 2 (0) → 3 (+1) → 4 (+1) → 5 (0) → 6 (-1) → 7 (-1) → 8 (-2) → 9 (-2) → 10 (-2)
Pic : bouton « Switch to English » puis page de connexion claire (+1, étapes 3 et 4) · Creux : message rouge en français après 25 s d'attente (-2, étape 8), puis « Merci de patienter » (-2, étape 9) · Fin : -2 (abandon)
Verbatim : « It said the code was sent, but it went to Dad's mail, and when I tried again it just told me off in French. »
Plafonds respectés : oui (mission abandonnée : Q1 = 2 ≤ 2, Q2 = 4 ≥ 4, Q4 ≠ « demain », Q5 = 3 ≤ 4 ; Q1 ≤ 2 donc Q5 ≤ 6 ; aucun Q1 = 5)
Écart satisfaction x frictions : cohérent. Deux frictions S2 sur le chemin (F1 et F2) et une fin à -2 donnent une note basse. Le pic (+1) est modeste : rien n'a donné de plaisir à Gogo (voir §4). L'impasse de F1 tient au scénario (parent absent), mais le site ne dit rien à l'élève dans ce cas.
Comparaison avec la dernière session du même persona x mission : aucune (première session de ce persona x cette mission dans le cadre de ce calibrage ; le persona n'a pas lu les rapports précédents). Pour le calibrage (§6) : abandon franc obtenu avec Q1 = 2, ce qui est conforme (Q1 ≤ 2) ; Q4 = « peut-être » au lieu de « je ne reviens pas » : l'orchestrateur décide si cela compte comme trop indulgent.

## Ce qui marche bien
- Sur mobile, la bascule vers l'anglais est visible dès l'accueil (« Switch to English » sous les boutons, étape 1) et un seul toucher suffit ; le site passe à /en/cm (pic d'humeur +1, à ne pas casser).
- La page de connexion est courte et lisible sur 375 px : Google, e-mail, « Get the code », « I already have a code », rien de superflu ; le champ du code affiche l'exemple « 123456 » (étapes 4 et 6).
- L'écran du code rassure sur ce qui est fait : adresse rappelée, « valid for 5 minutes », indication « the sender is EduKora » pour chercher dans les spams.
- Un compte à rebours « Resend the code (54s) » est affiché au début (étape 6), donc on sait quand on peut redemander.
- Les erreurs rouges sont visibles (couleur, position au-dessus du bouton) et le site ne plante pas.

## Frictions

| Id | Sév. | Catégorie | Étape | Observé | Attendu | Preuve | Confiance | Statut |
|---|---|---|---|---|---|---|---|---|
| F1 | S2 | UX | 6, 7, 10 | Quand la boîte mail est celle d'un parent absent, l'écran du code ne propose aucune sortie : seuls « Resend » et « Change address » ; l'aide du « ? » dit « look in your junk folder » et « ask for a new code ». Ni « demande à ton parent de te lire le code », ni lien de connexion à envoyer à l'adulte, ni retour à la séance en mode visiteur. Gogo repart sans séance de maths. | Un texte qui s'adresse à l'élève dont le mail est celui d'un parent (« Ton parent a reçu le code : demande-le-lui »), ou une porte de sortie utile (essayer sans compte) | étapes 6, 7, 10 (humeur -1, -1, -2) ; captures de l'écran du code et du panneau d'aide | élevée | nouvelle |
| F2 | S2 | UX / langue / fiabilité | 8 | Le renvoi du code reste sur « Sending… » environ 25 s (24 575 ms) puis échoue en 503. Message rouge en français sur une page anglaise : « Envoi du code impossible pour le moment. Merci de réessayer plus tard. » Pas de précision (quand ? pourquoi ?). | Réponse rapide ou délai expliqué ; message dans la langue de la page ; consigne concrète | étape 8, humeur -2 ; POST /auth/email/request/ 503 ; console « Failed to load resource: 503 » | élevée (observée une fois en bout de parcours, message affiché à l'écran) | nouvelle |
| F3 | S3 | UX / langue | 9 | Le bouton « Resend the code » est de nouveau actif juste après l'échec, sans compte à rebours ; le toucher donne 429 en 56 ms et un message en français « Merci de patienter avant de redemander un code. » sans durée. Le site invite à cliquer puis refuse. | Bouton désactivé avec compte à rebours (comme au début) ; message dans la langue de la page avec la durée | étape 9, humeur -2 ; POST 429 ; console « 429 » | élevée | nouvelle |
| F4 | S3 | Langue / orientation | 1 | Le visiteur de http://localhost/ arrive sur /cm, en français ; une élève du GCE doit repérer « Switch to English » (un seul toucher). Le bandeau « Choisis ton examen… » propose BEPC / Probatoire, pas le GCE. | Accueil dans la langue du navigateur ou du contexte ; ou choix de langue plus visible | étape 1, humeur -1 | moyenne (dépend de la langue du navigateur de test, non connue) | nouvelle |
| F5 | S3 | UX | 7 | Le « ? » de la page de connexion ouvre le centre d'aide complet (guides leçon, exercice, recherche…) ; la réponse « I do not receive my login code » est tout en bas, après plusieurs écrans de défilement. | Aide contextuelle à la page : la question du code en premier | étape 7, humeur -1 | moyenne | nouvelle |
| F6 | S4 | UX | 5 | Premier envoi : « Sending… » environ 3,1 s avant « Code sent » (3 104 ms). Acceptable seul, mais le message « Sending can take a few seconds… » n'apparaît qu'au renvoi. | Retour plus rapide ou message d'attente dès le premier envoi | étape 5 ; mesure PerformanceResourceTiming | élevée | nouvelle |
| F7 | S4 | UX | 7 | Le bouton X du panneau d'aide n'a pas fermé le panneau au premier toucher ; fermé avec Échap. | Fermeture au premier toucher | étape 7 | faible (impression unique, possible souci de repérage des coordonnées de ma part) | nouvelle |
| F8 | S4 | Langue | 4 | Pendant le fondu d'apparition de la page de connexion, le bouton Google a affiché une seconde « Continuer avec Google » (français) avant « Continue with Google ». | Texte stable dans la langue choisie | capture de l'étape 4 | faible | nouvelle |
| F9 | S4 | Technique | 6 à 9 | Console : deux erreurs « An unknown error occurred when fetching the script. » dès l'arrivée sur la page de connexion, puis 503 et 429 dus aux renvois. Aucun effet visible. | Console propre | read_console_messages | faible | nouvelle |

Catégorie « valeur / émotion » : non ajoutée. La satisfaction basse est expliquée par F1 et F2 (S2), pas par un défaut de ton.

## Mesures
- Départ : http://localhost/ redirige vers /cm (français) ; après bascule : /en/cm, puis /en/login.
- POST /auth/email/request/ : premier envoi 3 104 ms, 200 ; renvoi 1 : 24 575 ms, 503 ; renvoi 2 : 56 ms, 429.
- Délais : première demande à 14:27:29Z environ ; renvoi 1 vers 14:30:08Z ; renvoi 2 vers 14:30:55Z ; abandon à 14:31:31Z (environ 3 min 50 s après la première demande, 5 min depuis le début de la session). Attente cumulée sans action : environ 2 min 20 s avant de pouvoir renvoyer (le compte à rebours initial était de 54 s à l'écran, mais le renvoi a été fait plus tard).
- Page de connexion : 84 ressources dans la fenêtre de performance (57 fichiers JS) dont 10 appels API (catalogue, accès, inédites) déclenchés alors que Gogo ne fait que se connecter ; transfert observé 103 Ko (nombreux fichiers déjà en cache, donc chiffre bas ; réseau non bridé). Navigation : 59 ms (local).
- Console : 2 erreurs de script non précisées, 1 erreur 503, 1 erreur 429.
- Je n'ai pas vérifié qu'un e-mail est réellement parti : le 200 du premier envoi dit seulement que le serveur a accepté la demande.

## Écarts local / prod
Non applicable (local seulement).

## Idées d'amélioration
Séparées des constats, par effet/effort.
1. Texte d'écran du code pour les familles qui partagent une boîte mail (effet élevé, effort faible, catégorie expérience) : une phrase « Le code a été envoyé à cette adresse. Si c'est l'adresse de ton parent, demande-lui de te le lire. » avec un bouton « Continuer sans compte » ou « Faire un quiz gratuit » pour ne pas repartir les mains vides.
2. Traduire les messages d'erreur d'envoi du code (503 et 429) dans la langue de la page et ajouter la durée d'attente (effet élevé, effort faible, expérience) : déjà noté en mémoire projet comme « erreurs API encore en français ».
3. Désactiver « Resend the code » avec un compte à rebours après un échec ou un 429, comme au premier envoi (effet moyen, effort faible, expérience).
4. Réduire ou expliquer l'attente de 25 s au renvoi : message « Sending can take a few seconds » dès le premier envoi, délai d'expiration plus court, puis échec expliqué (effet moyen, effort moyen, expérience).
5. Aide contextuelle du « ? » sur la page de connexion : mettre la question « Je ne reçois pas mon code » en premier (effet moyen, effort faible, expérience).
6. Choisir la langue de l'accueil selon la langue du navigateur ou mémoriser le choix pour le GCE (effet moyen, effort moyen, expérience).
7. Un lien de connexion par e-mail ou un code que le parent peut transmettre par message est une piste de fonctionnalité (effet à évaluer, effort élevé, fonctionnalité manquante). Hypothèse : non vérifiée, je ne connais pas le fonctionnement du site.

## Diagnostic [phase B]
Non fait : la consigne interdisait de lire le code, la base et les logs. Hypothèse non vérifiée : le 503 de 24 s au renvoi ressemble à un envoi d'e-mail qui attend un serveur de messagerie injoignable en local, et le 429 à une limite de fréquence côté serveur ; cela reste à confirmer par l'orchestrateur.

## Ce que cette session ne dit pas
- La satisfaction est simulée : un indice relatif pour comparer des sessions, pas la satisfaction d'élèves réels. Une vraie Gogo aurait peut-être demandé le code à son parent par téléphone ou par message, ce que le scénario excluait.
- Réseau non bridé : les 25 s du renvoi seraient pires avec une data comptée ou un réseau lent ; la durée mesurée vient peut-être de l'environnement local (hypothèse).
- Le code n'a jamais été saisi : l'écran de connexion réussie, l'espace de Gogo et la séance de maths du jour n'ont pas été vus. Rien dans cette session ne dit si l'espace après connexion est bon.
- Le contenu du e-mail reçu par le parent (lisibilité, objet, expéditeur) n'a pas été vu.
- Pas de relecture scientifique ni de test de l'option téléphone ou Google (interdits par le scénario).
- Testeur simulé sans mémoire entre sessions : « peut-être » est une intention, pas un comportement observé.
- Ligne à ajouter à docs-relecture/eleve/satisfaction.md (non modifié par cette session, selon la consigne) : | 2026-10-24 | Gogo | connexion e-mail familial + séance de maths | local | non relevé | 2 | 4 | 1 | peut-être | 3 | sans objet | pic : étape 3-4 (+1) | creux : étape 8-9 (-2) | 2026-10-24-calibrage-satisfaction-gogo-connexion-local.md |
