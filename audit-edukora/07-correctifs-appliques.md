# 07 - Correctifs appliqués après l'audit (2026-11-12)

Demandés par le user : R2, R3, R8 (« Fais tous ») et la décision « corrigé libre dans le HTML des moteurs : oui » (R5). Tout est dans la copie de travail `D:\edukora`, **non committé**. Le diff contient aussi une suppression étrangère à ces correctifs (`scripts/edukora.ps1`), déjà présente avant l'audit : ne pas la stager avec eux.

## Fichiers modifiés
| Fichier | Rôle |
|---|---|
| `frontend/src/components/RouteFallback.tsx` | **R2** : le squelette de chargement réserve un écran (`min-h-[100svh]`) |
| `backend/catalog/apercu_partage.py` | **R3** : `description_epreuve()` (deux gabarits, niveau d'examen, pays) pour l'aperçu de partage et la page prérendue |
| `backend/catalog/prerendu.py` | **R3** + **R5** : description exacte ; une épreuve vitrine sert son corrigé complet et son lecteur est la page canonique |
| `backend/catalog/test_prerendu.py` | 3 tests ajoutés (vitrine, payante, descriptions) |
| `frontend/src/lib/i18n/fr.ts`, `en.ts` | **R3** (clés `ed.seo_description`, `ed.seo_description_libre`) et **R8** (`login.recap`, `prix.recap_choix_*`, `sb.intent` reformulé) |
| `frontend/src/pages/EpreuveDetailPage.tsx` | **R3** : même description côté navigateur que côté moteurs |
| `frontend/src/pages/PricingPage.tsx`, `SubscribePage.tsx`, `LoginPage.tsx` | **R8** : le choix (cursus · mois · total) voyage de /tarifs à /connexion et s'y affiche |

## Détail par correctif
- **R2 (UX-01, CLS)** : cause = le squelette de route ne faisait qu'une centaine de pixels ; le pied de page s'affichait dessous puis était poussé hors de l'écran à l'arrivée de la page. Correctif = squelette d'un écran entier : le pied de page démarre sous la ligne de flottaison.
- **R3 (SEO-03)** : la meta description disait "corrigé détaillé par abonnement" pour tout le monde. Maintenant : épreuve vitrine (corrigé libre) → "sujet et corrigé détaillé en accès libre, sans abonnement" ; autre épreuve → "sujet en accès libre, corrigé détaillé par abonnement" ; les deux avec le niveau d'examen et "au Cameroun" (EN : "Cameroon"). **Non fait** : l'ajout de "corrigé" dans les titles (à décider, voir ci-dessous).
- **R5 (SEO-01)** : pour une épreuve vitrine, le prérendu envoyé aux moteurs contient maintenant le corrigé complet (comme un visiteur anonyme le lit sur /lire) et le canonical est le lecteur (`.../lire`, ou `.../read` en anglais). Les épreuves payantes restent inchangées (sujet seulement, fiche canonique). La règle d'or du module ("on ne sert que ce qu'un visiteur anonyme voit") reste respectée.
- **R8 (UX-06)** : l'écran de connexion affiche "Ton choix : BEPC · 3 mois · 6 000 FCFA" quand on vient de /tarifs, et la phrase redondante devient "Plus qu'une étape pour finaliser ton abonnement. Connecte-toi en quelques secondes."

## Décisions que je n'ai pas prises
- **SEO-04 (doublon GCE)** : le module `prerendu.py` documente ce double adressage comme un choix délibéré (un élève GCE peut arriver par une URL française) ; je ne l'ai pas changé. Reste ouvert : le chemin canonique (anglais ou français) est une décision du user.
- Titles avec "corrigé" : touche environ 2 400 pages et doit rester identique côté prérendu et côté navigateur ; à décider.
- R4, R6 (pages par cursus), R9 : non demandés.

## Vérifications
- Backend : `catalog.test_prerendu` + `catalog.test_apercu_partage` : 33 tests OK (dont 3 nouveaux) dans le conteneur après copie des fichiers ; sortie `curl -A Googlebot` : épreuve libre 27,5 Ko avec corrigé (17 repères "Rappel de méthode"), canonical `/lire`, description exacte ; épreuve payante 5,4 Ko, aucun corrigé, canonical fiche ; GCE libre : description anglaise exacte.
- Frontend : `tsc --noEmit` sans erreur ; 6 fichiers de tests liés (connexion, abonnement, tarifs, épreuve, i18n, balises), 64 tests OK. Mesures dans le navigateur : voir la section suivante.

## Mesures après correctifs (build local reconstruit, visiteur, mobile 375x812, cache et service worker vidés)
| Mesure | Avant | Après |
|---|---|---|
| CLS /tarifs | 0,602 | **0** (aucun décalage) |
| CLS accueil /cm | 0,945 puis 0,901 | **0,101** (un seul décalage : le bandeau "Choisis ton examen" apparaît au-dessus de la page, 0,098) |
| CLS épreuve | 0,901 | **0,125** signalé mais compté 0 par l'API (marqué "après saisie") ; seul décalage restant = même bandeau, le pied de page ne bouge plus |
| Pied de page | poussé de y=363 à y=0 | stable |
| Description de /cm/epreuves/mathematiques-bepc-2026 (navigateur) | "... sujet en accès libre, corrigé détaillé par abonnement." | "Corrigé d'annale de Mathématiques BEPC (2026) au Cameroun : sujet et corrigé détaillé en accès libre, sans abonnement." |
| Rappel du choix sur /connexion (depuis /tarifs : BEPC, 3 mois) | absent | "Ton choix : BEPC · 3 mois · 6 000 FCFA" (captures/R8-connexion-rappel-du-choix.jpg) |
| HTML Googlebot d'une épreuve libre | 5,8 Ko, sans corrigé | 27,5 Ko avec corrigé, canonical `/lire` |

**Résiduel (non corrigé)** : le bandeau "Choisis ton examen" (BandeauCursus) est rendu seulement après le chargement de la liste des cursus, et pousse la page de 87 px. Il reste ≈ 0,10 de CLS sur l'accueil. Piste : réserver sa hauteur pendant le chargement, mais il faut décider quoi faire si la liste ne charge pas (trou vide). À traiter avec P8.

Tests : frontend 1 383 réussis, 17 ignorés (suite complète, 147 fichiers) ; `tsc --noEmit` propre ; backend `catalog.test_prerendu` + `catalog.test_apercu_partage` 33 OK. La suite `catalog` complète est lancée séparément : résultat ci-dessous si disponible.

## Mise en production (non faite)
- Backend : les 3 fichiers sont dans le dépôt et ont été copiés dans le conteneur local (`docker cp`) ; la production demande un rebuild du backend.
- Frontend : rebuild de l'image `caddy` (`docker compose build caddy && docker compose up -d caddy`), déjà fait en local.
- Après déploiement : refaire `curl -A Googlebot` sur une épreuve libre (corrigé présent) et une payante (corrigé absent), puis demander une inspection d'URL dans la Search Console sur 2-3 épreuves libres.

## Suite `catalog` complète (backend, 842 tests)
2 échecs, **tous deux sans rapport avec ces correctifs** : `catalog.test_pdf_langue` (`test_sujet_francophone_inchange`, `test_sujet_du_gce_en_anglais`) attend encore "15 000 FCFA par enfant" alors que le PDF annonce désormais "2 000 FCFA par mois et par enfant" (chantier tarification au mois, déjà noté dans les notes du projet comme non committé). Les 840 autres passent, dont les 33 de prérendu et d'aperçu de partage.

---
# Lot 2 (2026-11-12, après "lançons les améliorations")
| Commit | Contenu | Preuve |
|---|---|---|
| `b41d8228` | Tests PDF alignés sur la tarification au mois (2 000 FCFA par mois et par enfant) | `catalog.test_pdf_langue` 19 OK ; suite `catalog` entière sans échec attendu |
| `4ae50268` | Bandeau "Choisis ton examen" : réserve d'espace pendant le chargement (CLS résiduel) | CLS local, visiteur, mobile : accueil **0,001** (0,945 au départ), tarifs **0** (0,602), épreuve **0,024** (0,901) ; 2 tests ajoutés |
| `fabdcd36` | **UX-20** : sélecteur d'enfant sur la page d'abonnement (comptes à plusieurs profils) | 2 tests ajoutés (sélecteur + compte à un seul profil) ; suite frontend 1 387 OK |
Non retenu : **UX-18** ("+0 points") est un artefact de mesure (compteur animé figé dans un navigateur en arrière-plan) ; retiré des constats.
Non vérifié en navigateur : le sélecteur d'enfant (vérifié par tests unitaires seulement, pas en parcours réel : cela demandait une nouvelle connexion par code).
Documents ajoutés : 09-specification-pages-cursus.md (L3, en attente de votre validation).
Non déployé : rebuild backend + `caddy` en production.

---
# Lot 3 : L3, pages d'atterrissage par examen (2026-11-12)
13 pages (11 examens francophones + GCE O et A Level), 15 URLs au sitemap. Détail, écarts et mesures : 09-specification-pages-cursus.md (section "État").
Vérifié en local, via Caddy : Googlebot reçoit le prérendu (200, 428 à 588 mots, canonical propre) ; examen inconnu = 404 réel ; WhatsApp reçoit un aperçu propre ; sitemap 15 entrées ; pied de page et fiches d'épreuve renvoient vers les pages ; CLS de la page 0,024 ; tests : backend `catalog` 860 OK, frontend 1 391 OK (dont 4 nouveaux pour la page et 18 backend).
Non déployé : rebuild backend + `caddy` ; après déploiement, `curl -A Googlebot` sur les 13 URLs et inspection d'URL dans la Search Console.

---
# Lot 4 : L4, conversion du parent (2026-11-12) - committé
| Commit | Contenu |
|---|---|
| `a0d96c9a` | L3 : pages d'atterrissage par examen (13 pages, 15 URLs au sitemap) |
| `70f2280e` | L4 / UX-03 : bloc "Tu es parent ?" sur l'accueil visiteur (3 cartes, prix tirés de la grille, boutons "Voir les prix" et "Comment payer ?"), FR et EN, 2 tests |
L4 en entier : UX-20 sélecteur d'enfant (`fabdcd36`), UX-03 bloc parents (`70f2280e`), UX-18 retiré (artefact de mesure), UX-05 reporté après les premières données du lancement (décision du plan).
Vérifié en local (visiteur, 375 px) : la section est présente, ses deux liens mènent à /tarifs et /aide/comment-payer, aucun débordement horizontal, CLS de l'accueil 0,001. Le rendu visuel n'a pas pu être capturé (fenêtre du navigateur intégré non dessinée) : à regarder à l'écran.
Tests : frontend 1 393 OK ; backend : `catalog` 860 OK, access / aide / recherche / programme / inedit / subscriptions / quiz / users OK, sauf `access.ConcurrenceTests.test_des_requetes_simultanees_ne_depassent_pas_le_quota` ("database table is locked" : base de test SQLite, test de concurrence, sans rapport avec ces changements). La suite complète en un seul lancement est tuée par manque de mémoire (code 137) : la lancer par application.
Non déployé : rebuild backend + `caddy`.

---
# Lot 6 : L6, SEO secondaire (2026-11-12) - committé
Commit : voir `git log` ("SEO secondaire : titles corrigé, fil d'Ariane et données structurées, sitemap").
- **Titles** : les annales corrigées (type CORR) portent "- corrigé" (EN "- solutions") dans le `<title>`, côté moteurs et côté navigateur ; le h1 est inchangé ; pas de répétition si le titre le dit déjà ; les autres types ne changent pas. Décision D2 prise avec "Lancer L6" (recommandation : oui).
- **Fil d'Ariane** visible (Accueil > examen > épreuve) sur la fiche d'épreuve et la page d'examen, **balisage BreadcrumbList** dans le HTML prérendu des épreuves, cours et pages d'examen.
- **JSON-LD Organization + WebSite** dans `index.html` (HTML initial de toutes les pages).
- **Sitemap** : les thèmes qui tombent (FR et EN par pays) et À propos.
- Vérifié en local : `<title>Mathématiques BEPC 2026 - corrigé | EduKora</title>`, BreadcrumbList à 3 niveaux pour une épreuve, 2 pour un examen, 3 pour un cours ; le JSON-LD de `index.html` est dans la réponse du serveur ; fil d'Ariane visible, CLS 0 et pas de débordement à 375 px.
- Tests : `catalog` 866 OK, frontend 1 397 OK.
- **Non fait volontairement** : brotli (Caddy ne le fournit pas, Cloudflare le fait en production : à vérifier en L1), cache des images `/media` (un cache plus long risquerait de servir d'anciennes figures remplacées), `font-display` des polices KaTeX (peut faire flasher les formules).

---
# Lot 7 : petits correctifs, SEO des pages d'ensemble, PDF (2026-11-12) - committé
| Commit | Contenu |
|---|---|
| `bad71b85` | SEO-06/07/08 : accueil, listes, tarifs, à propos, aide prérendus pour les moteurs et les robots de partage ; épreuves voisines (13 liens sortants au lieu de 2) ; vrai 404 pour un moteur sur une adresse inconnue (bloc de routes généré par `scripts/generer_caddy_segments.py`). Vérifié : 0 anomalie sur 700 URLs du sitemap et 36 routes de l'application avec un User-Agent Googlebot |
| `1038acfd` | UX-13 (GCE en premier sur /en/pricing), UX-14 (langue du bouton Google : `hl`), UX-11 (message clair sans examen ni matière), UX-08 (cibles de 32 px), titres des listes, des thèmes et des tarifs |
| voir `git log` | **PDF de sujet sans montant** : le bas des PDF affichait "15 000 FCFA ... 12 000 FCFA" (fichiers générés avant la tarification au mois). Le texte ne contient plus aucun montant ; un test le garantit |
**À faire une fois, après déploiement, en local et en production** : `python manage.py generate_sujet_pdfs --force` (2 180 PDF locaux portent encore l'ancien texte). Un PDF d'essai régénéré est dans `captures/exemple-sujet-sans-montant.pdf` (Maths BEPC 2026). Plus jamais à refaire pour un changement de prix.
**Non fait** : UX-16 (vocabulaire "question/section" du GCE : choix de libellé global, à décider), brotli et caches (voir lot 6).
