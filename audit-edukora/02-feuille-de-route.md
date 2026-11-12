# 02 - Feuille de route jusqu'au 1er décembre 2026
Date de l'audit : jeudi 2026-11-12 (J-19). Lancement : mardi 2026-12-01. Efforts : S ≤ 1 jour, M = 2 à 3 jours, L = 4 jours ou plus. Estimations de l'auditeur à partir de la lecture du comportement, pas du code : à confirmer par l'équipe.
Principe : sécuriser d'abord ce qui peut rendre le lancement invisible (production), puis ce qui améliore l'acquisition à bas coût, puis rejouer le parcours de paiement avant le gel.

## Statut au 2026-11-12 (soir)
- **Faits en local (non déployés, non committés)** : R2 (CLS, résiduel ≈ 0,10 dû au bandeau "Choisis ton examen"), R3 (descriptions ; titles non touchés), R5 (corrigé libre dans le HTML des moteurs), R8 (rappel du choix à la connexion). Détail et mesures : 07-correctifs-appliques.md. À déployer : rebuild backend et caddy.
- **R7 réalisé en partie** (élève abonné, parent, jusqu'à l'écran de paiement) : 06-parcours-connecte.md. Restent : déclaration de paiement et activation, élève libre / expiré, session expirée.
- **R1 s'étend** : fournisseur et capacité du SMTP, plafonds OTP (60 e-mails par IP et par heure ; 5 000 par jour) au regard du trafic, état de CamPay.
- **Décision prise** : corrigé libre dans le HTML des moteurs = oui. **Restent à décider** : chemin canonique des GCE (R4 ; le doublon FR/EN est un choix documenté dans `prerendu.py`), titles avec "corrigé", permanence de l'activation (R9).

## Calendrier par vagues
| Vague | Dates | Contenu |
|---|---|---|
| 0 - Sécuriser | jeu 12 - ven 13 nov | R1 (vérifier la production) |
| 1 - Correctifs rapides | lun 16 - ven 20 nov | R2, R3, R4, R8 |
| 2 - Acquisition et recette | lun 23 - ven 27 nov | R5, R6, R7, R9 |
| Gel et recette finale | sam 28 - lun 30 nov | re-mesure, Search Console, permanence paiement |
| Lancement | mar 1er déc | surveillance, bloc "juste après" |

## Bloc 1 - Indispensable avant le lancement
| # | Action | Constat | Effort | Impact | Dépendances | Critère de validation |
|---|--------|---------|--------|--------|-------------|----------------------|
| R1 | **Vérifier la production** : `ROBOTS_TAG` du `.env` sans noindex ; `<loc>` des sitemaps en `https://edukora.africa` ; redirections http→https et www ; brotli ; `X-Robots-Tag` réel ; demande d'inspection d'URL dans Search Console et envoi du sitemap | SEO-10 | S | Évite un lancement invisible (potentiellement Bloquant) | Accès à la prod et à la Search Console | `curl -sI https://edukora.africa/` sans noindex ; `curl https://edukora.africa/sitemap.xml` avec URLs https ; sitemap accepté dans Search Console |
| R2 | **Supprimer le saut du pied de page** : réserver la hauteur du contenu ou ne pas afficher le pied de page avant l'arrivée du contenu (accueil, épreuve, tarifs, toutes les pages à chargement) | UX-01 | S à M | Core Web Vitals, confort sur connexion lente | Aucune | PerformanceObserver `layout-shift` ≤ 0,1 sur /cm, /tarifs, une épreuve, un cours (mobile et desktop) |
| R3 | **Meta descriptions et titles honnêtes** : trois variantes (corrigé libre, corrigé payant, GCE) avec niveau d'examen, matière, année, "Cameroun" ; title avec "corrigé" | SEO-03 | S | Taux de clic, confiance, requêtes "épreuve X corrigé" | Texte validé par l'équipe produit | `curl -A Googlebot` sur 3 épreuves libres et 3 payantes : descriptions distinctes et exactes |
| R4 | **Supprimer le doublon GCE** : une seule URL canonique par épreuve GCE (suggestion : le chemin anglais), redirection ou canonical de l'autre, retrait des 861 doublons du sitemap, hreflang et x-default cohérents | SEO-04 | M | Indexation propre de 861 pages, anglophones sur la bonne interface | Décision : chemin canonique des GCE | `curl -A Googlebot` sur les deux URLs : même canonical ; sitemap sans doublon (compte ≈ 861 de moins) |
| R5 | **Arbitrer et appliquer le corrigé libre dans le prérendu** : inclure le corrigé des épreuves à corrigé libre dans le HTML envoyé aux moteurs (le payant reste exclu) | SEO-01 | M | Premier levier d'acquisition ("épreuve BEPC maths corrigé") | Décision produit (exposition du contenu libre) ; R3 | `curl -A Googlebot` d'une épreuve libre contient le texte du corrigé ; d'une épreuve payante : non |
| R6 | **Pages d'atterrissage par cursus** (version minimale : 11 cursus francophones + GCE O/A Level, puis par matière si le temps le permet) : URL propre, title, description, h1, liste des épreuves et lien vers les thèmes, présentes dans le sitemap et prérendues | SEO-02 | M à L | Requêtes "annales BEPC Cameroun", "BAC D annales corrigées" | R5, R3 ; choix des URLs | Chaque page répond 200 pour Googlebot avec contenu et canonical propre, listée au sitemap |
| R7 | **Rejouer en recette le parcours non couvert par cet audit** : connexion par code (e-mail et téléphone), séance du jour, choix du cursus, déclaration de paiement (jamais de paiement réel), activation par l'équipe, accès ouvert ; comptes [TEST] et environnement de recette | périmètre | M | Lève le risque n°1 | Comptes [TEST], boîte e-mail de test | Parcours complet sans erreur, accès activé, notes écrites par persona |
| R8 | **Parent à l'écran de connexion** : rappeler le choix (cursus, mois, total) sur /connexion, supprimer la phrase redondante, afficher le numéro de paiement ou son délai avant la demande d'e-mail si possible | UX-06, UX-05 | S | Conversion du payeur | R7 pour valider | Après "Continuer", la page de connexion rappelle BEPC / 3 mois / 6 000 FCFA |
| R9 | **Plan d'activation sous 3 h au pic du lancement** : permanence pendant les 3 premiers jours, message clair d'attente et d'état, numéro WhatsApp visible | UX-04 | S (organisation) | Évite l'abandon et les litiges au pic | Disponibilité de l'équipe | Délai réel mesuré sur les 20 premiers paiements ≤ 3 h |

## Bloc 2 - Juste après le lancement (décembre)
| # | Action | Constat | Effort | Impact | Critère de validation |
|---|--------|---------|--------|--------|----------------------|
| P1 | Données structurées : Organization (accueil), BreadcrumbList et fil d'Ariane, LearningResource sur les cours | SEO-05 | M | Extraits, maillage | Test des résultats enrichis sans erreur sur 3 pages |
| P2 | Titles et prérendu des pages hors détail (accueil, listes, tarifs, thèmes, quiz) ; og:url propre par page | SEO-06 | M | Partage, moteurs sans JavaScript | `curl -A Googlebot` donne un title distinct par page |
| P3 | Sitemap et maillage : ajouter /cm/themes-frequents, /a-propos ; liens internes (cours associés, autres épreuves) dans le HTML bot | SEO-08 | S à M | Découverte des pages | Sitemap à jour ; ≥ 10 liens internes dans le HTML bot d'une épreuve |
| P4 | Vrai 404 serveur pour les routes inconnues ; normaliser /CM, slash final | SEO-07 | S | Indexation propre | `curl -w %{http_code}` donne 404 |
| P5 | Quiz : essai gratuit de Physique pour Probatoire C ; lien "Quiz" d'un thème qui ouvre le quiz du thème (ou le dise) | UX-10 | M | Conversion | Un visiteur Probatoire C lance un quiz de physique en 2 clics |
| P6 | Pricing EN : GCE en premier ; bouton Google selon la langue de l'interface ; majuscules des thèmes ; vocabulaire "question/section" du GCE | UX-13, 14, 15, 16 | S | Cohérence GCE | Relecture de /en/pricing, /en/login, /en/quiz |
| P7 | Entrée parent sur l'accueil (bloc "Parents" avec prix et paiement) ; test A/B de l'ordre téléphone / e-mail | UX-03, UX-05 | M | Conversion du payeur | Taux d'inscription parent comparé avant/après |
| P8 | Performance : brotli, cache des /media (≥ 1 jour), cache des API publiques, polices KaTeX en swap ; mesurer LCP et INP sur l'URL réelle (PageSpeed, données de terrain) | SEO-09 | M | 3G | LCP < 2,5 s et INP < 200 ms sur mobile, mesurés en production |
| P9 | Liens d'exercices par thème sans paramètres : retrouver le cursus par défaut | UX-11 | S | Liens partagés | /themes-frequents/<id>/exercices ouvert sans paramètre liste des exercices |
| P10 | Cibles tactiles de 24 px minimum (liens du pied de page, "Retour", "Switch to English") | UX-08 | S | Mobile | Contrôle de tailles sur 5 pages |

## Bloc 3 - Backlog (à valider avec de vrais utilisateurs)
- F1 échantillon de la séance du jour pour un visiteur ; F2 suivi de paiement avec notification et, si CamPay est actif, paiement intégré ; F3 résumé pour le parent après le quiz d'essai ; F4 pages éditoriales pour parents ; F5 mémoire de l'examen choisi par appareil (ordinateur partagé).
- Cosmétiques : UX-07 texte de mascotte en double, UX-09 ton "frère", UX-12 "Encore 48 thèmes", slugs de cours plus courts, quiz public indexable (arbitrage).
- Mesurer la satisfaction avec de vrais élèves et parents (5 à 8 entretiens courts de 15 minutes sur mobile) pour confirmer ou infirmer les scores simulés.

## Points de décision pour l'équipe (avant le 16 nov)
1. Corrigé libre dans le HTML des moteurs : oui ou non (R5).
2. Chemin canonique des épreuves GCE : chemin anglais ou français (R4).
3. Qui assure la permanence d'activation des paiements du 1er au 3 décembre (R9) ?
