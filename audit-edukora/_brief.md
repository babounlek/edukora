# _brief.md : contexte partagé de l'audit edukora (rédigé le 2026-11-12, Phase 0)

Lancement public : 2026-12-01 (J-19 à la date de l'audit). Cible : version LOCALE, lecture seule.

## 1. Environnement (faits observés)
- Pile Docker déjà démarrée (3 conteneurs, "Up 3 hours") : caddy (80/443), backend (8000 interne), db (Postgres). Aucune commande de lancement nécessaire.
- URL de test : http://localhost/ -> redirige vers /cm (200, 6,3 Ko de HTML, 13 ms). Anglais : /en (200).
- Le frontend est une SPA React/Vite servie en statique par Caddy ; l'API passe par Caddy vers le backend (Django).
- Backend : DEBUG=True, EMAIL_BACKEND=SMTP (pas de console), CAMPAY_ACTIVE=False -> aucun paiement réel possible en local.
- Les ports 8001 / 5173 (dev servers) ne tournent pas ; ne pas les utiliser.
- Contenu local (page d'accueil /cm) : 1 520 épreuves corrigées, 14 108 cours, 26 matières, 237 épreuves inédites.

## 2. Authentification (BLOCAGE pour les personas connectés)
- Pas de mot de passe élève : connexion par code OTP (téléphone ou e-mail) ou Google.
- Comptes "[TEST]" déjà présents en base locale (créés par seed_donnees_test, e-mails en @exemple.local donc codes OTP non reçus par personne) :
  eleve-abonne (id 123), eleve-libre (124), eleve-expire (125), parent-famille (126), paiement-attente (127) (+ doublons ids 118-119 en test+...).
- Je ne crée aucun compte et je ne lis pas les codes OTP en base sans votre accord. Voir "Question au user" dans le plan.

## 3. Structure du site (routes, lues dans frontend/src/App.tsx)
Publiques : /:pays (catalogue), /:pays/epreuves, /:pays/epreuves/:slug (+ /lire), /:pays/cours, /cours/:slug (+ /lire), /:pays/recherche, /:pays/themes-frequents, /:pays/epreuves-inedites/:id, /tarifs, /connexion, /qui-etudie, /a-propos, /aide, /aide/:slug, /cgu, /confidentialite, /devenir-revendeur, /quiz (+ /quiz/essai : quiz gratuit sans compte).
Connecté : /abonnement, /compte, /mes-acces, /historique, /carnet, /mes-paiements, /parcours, /parcours/:subjectId, /quiz/session/:id, /inedit/tentative/:id, /simulation/:id, /espace-revendeur.
Version anglaise : préfixe /en avec segments traduits (/en/cm/past-papers/x, /en/pricing). `*` -> NotFoundPage.

## 4. SEO : éléments déjà vus (faits)
- robots.txt présent (local) : Allow /, Disallow /access/ /inedit/epreuves/ /fiches/ /quiz/sessions/ ; liste de robots IA bloqués (/quiz/, /catalog/, /inedit/, ...). Sitemap: https://edukora.africa/sitemap.xml (hôte de PROD codé en dur, alors que le sitemap local pointe http://localhost/...).
- sitemap.xml = index de 20 sitemaps (sitemap-1..20.xml), avec hreflang fr/en/x-default sur les entrées.
- Pré-rendu pour moteurs : Caddy envoie Googlebot/Bingbot/etc. vers /prerendu (backend) pour épreuves, cours, inédites, aide. Les robots de partage (WhatsApp, Facebook...) vont vers /partage-apercu. => Tester avec des User-Agent bots, pas seulement avec un navigateur.
- index.html : title/description FR génériques, pas de canonical statique (posé par JS via BalisesDeRoute), OG de base, viewport OK, lang="fr" (basculé en JS pour /en).
- Constat candidat à reverifier en Phase 3 : GET /page-qui-nexiste-pas renvoie HTTP 200 (soft 404 SPA) ; à vérifier si noindex posé par NotFoundPage.

## 5. Personas et conventions
Parent (Phase 1, d'abord), élève BEPC (Phase 1), Probatoire et GCE (Phase 2). Mobile : resize_window preset mobile (375x812) ; réseau : pas de throttling natif dans l'outil -> je l'approche par mesures de poids de ressources (read_network_requests) + calcul de temps sur 3G (~1,6 Mbit/s, 300 ms RTT), annoncé comme une estimation.
Notation : notes 1-5 ancrées, humeur par étape, 3 scores 0-10 (revenir / recommander / payer), confiance indiquée (simulation, pas un test utilisateur).
Sévérités : Bloquant / Majeur / Mineur / Cosmétique. Chaque constat : ID (UX-nn, SEO-nn), persona/axe, URL + étape, preuve, fait vs hypothèse.
Captures : seulement pour Bloquant/Majeur, 25 max, dans ./captures/.
Hors périmètre : contenu pédagogique, KaTeX -> 04-hors-perimetre.md (une ligne).
