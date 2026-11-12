# Plan court et hypothèses (Phase 0)

## Hypothèses à tester (à confirmer ou infirmer, aucune n'est un constat)
H1. L'offre ("séance de 25 min par jour") est comprise en 10 s sur mobile, mais la page d'accueil est longue (14 108 cours / 1 520 épreuves = chiffres peu parlants pour un parent).
H2. Le parent doit passer par une connexion OTP avant de voir le paiement : friction de conversion (le texte "tu te connectes d'abord" existe déjà sur /tarifs).
H3. Mobile money (MTN/Orange) est bien proposé, mais la confirmation de paiement manuelle (déclaration) est lente / peu rassurante.
H4. Le bilinguisme FR/EN a des restes (textes serveur, erreurs API, e-mails encore en français d'après la mémoire projet).
H5. SEO : bonne base (sitemaps, hreflang, pré-rendu bots) mais soft 404 en HTTP 200, canonical posé en JS, robots.txt avec hôte de prod en dur.
H6. Performance 3G : poids du bundle JS initial + polices à mesurer.

## Phases
- P1 Parent puis BEPC : visiteur (sans compte) d'abord ; parcours connecté seulement si un accès de test est accordé.
- P2 Probatoire puis GCE.
- P3 SEO technique (curl avec UA bots, HTML initial vs rendu, hreflang, JSON-LD, OG, 404).
- P4 Synthèse et livrables, revérification des Bloquant/Majeur.

## Question au user (bloquante pour les parcours connectés)
Connexion sans mot de passe. Quel accès de test m'autorisez-vous ?
 A. Rester visiteur (aucun compte) : j'audite accueil, catalogue, lecture libre, quiz gratuit sans compte, tarifs, aide, SEO. Je décris sans exécuter le tunnel d'inscription, de séance et de paiement.
 B. Vous me donnez un code OTP à chaque connexion sur un compte [TEST] (je vous dis quand).
 C. Vous m'autorisez à lire en base locale le code OTP du compte [TEST] concerné (lecture seule, comptes @exemple.local).
