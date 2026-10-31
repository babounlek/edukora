# Performances et économie de données — rapport d'intervention

Réalisé en local, du 2026-10-25 au 2026-10-31. **Rien n'a été déployé en production.** Le prompt d'origine est dans
`deploy/PROMPT-PERFORMANCES-DONNEES.md`. Ce rapport distingue ce qui est **mesuré** de ce qui ne l'est pas.

## 1. Diagnostic (mesuré sur la pile locale, build de production derrière Caddy)

| # | Constat | Mesure | Suite donnée |
|---|---|---|---|
| 1 | La liste des épreuves renvoie des champs qu'aucune carte n'affiche : `related_cours` = 53 % du JSON, `themes` = 21 % | 109 Ko bruts / 19,7 Ko transférés par page de 24 | **Corrigé** |
| 2 | Visite répétée : 20 Ko de listes retéléchargés à chaque fois (aucun ETag, le navigateur revalide sans pouvoir recevoir de 304) | accueil, 2e visite : 57 Ko | **Corrigé** |
| 3 | Les listes lisent le texte entier de chaque épreuve/cours en base sans l'utiliser | 616 Ko lus par page de 24 épreuves | **Corrigé** (`defer`) |
| 4 | Un fichier absent de `/assets` répondait `200 index.html` avec `immutable` 1 an | reproduit avec `curl` | **Corrigé** (404 `no-store`) |
| 5 | Pages de l'application sans `Cache-Control` (fraîcheur heuristique du navigateur) | en-têtes relevés | **Corrigé** |
| 6 | Image d'accueil JPEG de 82 Ko | 816×499 | **Corrigé** (WebP 20 Ko / 9 Ko) |
| 7 | Le précache du service worker télécharge ~1,2 Mo (gzip) juste après le premier chargement, invisible dans les mesures de page | 192 entrées, 1 213 Ko | **Réduit de 15 %** (1 027 Ko) |
| 8 | Un filet de sécurité force le chargement de ~190 Ko (Markdown + KaTeX) 8 s après l'arrivée, même sans défilement | lecture du code | **Corrigé** sur connexion lente / économie de données |
| 9 | Chaîne d'authentification d'un visiteur anonyme : 3 requêtes 401 successives au premier passage | relevé réseau | **Non traité** (déjà réduit aux visites suivantes par `sessionAnonyme`) |
| 10 | Chemin critique du premier affichage : `index` 134 Ko + `client` 76 Ko + CSS 40 Ko (gzip), dont dictionnaire français, react-dom, Radix Select, modales d'onboarding/PIN | build analysé (`scripts/perf/analyse-bundle.mjs`) | **Non traité** |

## 2. Optimisations réellement implémentées

**Backend**
- `backend/edtech_cm/etag.py` (+ `settings.py`, juste après CORS) : ETag et réponses `304` sur les GET JSON ; `Cache-Control: private, no-cache` par défaut (jamais de cache partagé, revalidation à chaque usage). L'ETag est l'empreinte du corps calculé pour la requête courante : un compte ne peut recevoir un `304` que pour un corps identique octet pour octet au sien. Les PDF, flux, erreurs, HTML et `no-store` sont exclus.
- `backend/catalog/serializers.py` : `LessonListeSerializer` (sans `themes` ni `related_cours`).
- `backend/catalog/views.py` : liste des épreuves allégée, requêtes groupées devenues inutiles retirées, `defer("content_markdown")` sur les listes d'épreuves et de cours.
- `backend/catalog/inedit_bridge.py` : `liste_allegee` pour les inédites ; la fiche détail garde ses deux champs.
- Tests : `backend/edtech_cm/test_etag.py` (8 cas), test de `catalog/tests.py` adapté (liste sans les champs, fiche détail avec).

**Caddy** (`docker/caddy/Caddyfile`, validé par `caddy validate`)
- `/assets/*` : `immutable` 1 an, **404 sans repli sur index.html** ; erreur sur `/assets` ou `/media` : `no-store`.
- Logos/icônes de la racine : 1 jour. `/media/*` : 1 heure. Pages de l'application : `no-cache`.

**Frontend**
- `CataloguePage.tsx` : image d'accueil WebP responsive (`srcset` 408/816 px).
- `vite.config.ts` : précache sans le dictionnaire anglais, sans les polices `latin-ext`, sans les polices KaTeX rares (elles restent mises en cache à l'usage par la règle `ressources-app`).
- `lib/connexion.ts` (+ test) et `EpreuveMarkdownLazy.tsx` : pas de chargement « de confort » sur 2G/3G ou en économie de données.
- `api/types.ts` + deux pages de détail : `themes` et `related_cours` optionnels (le compilateur vérifie qu'aucun consommateur de liste ne les lit).

**Outils** : `scripts/perf/mesure_pages.py` (mesure réseau CDP, profils rapide/lent, 3 répétitions, médiane), `scripts/perf/analyse-bundle.mjs`.

## 3. Mesures avant / après

Profil « rapide » (réseau local, viewport 390×800, médiane de 3 exécutions). Octets = **transférés sur le réseau** (compressés). « 2e visite » = même contexte, service worker et cache conservés.

| Page | 1re visite avant | 1re visite après | 2e visite avant | 2e visite après |
|---|---|---|---|---|
| Accueil | 838 Ko | 705 Ko | 57 Ko | **4 Ko** |
| Accueil d'un pays | 838 Ko | 705 Ko | 57 Ko | **4 Ko** |
| Épreuves | 524 Ko | 497 Ko | 46 Ko | **5 Ko** |
| Cours | 509 Ko | 487 Ko | 25 Ko | **2 Ko** |
| Tarifs | 471 Ko | 469 Ko | 22 Ko | **3 Ko** |
| Accueil anglais | 821 Ko | 566 Ko | 42 Ko | **4 Ko** |

Points d'API (même machine, médiane de 3, `Accept-Encoding: zstd`) :

| Endpoint | Brut avant → après | Transféré avant → après | Temps avant → après |
|---|---|---|---|
| `/catalog/lessons/` (24) | 109 Ko → 28 Ko | 19,7 Ko → 2,3 Ko | 0,18 s → 0,10 s |
| `/catalog/lessons/?page=2` | 124 Ko → 29 Ko | 23,8 Ko → 2,3 Ko | 0,32 s → 0,11 s |
| `/catalog/cours/` | 22,9 Ko → 23,3 Ko | 3,6 Ko → 3,5 Ko | 0,39 s → 0,11 s |
| `/catalog/subjects/` | 10,7 Ko → 10,9 Ko | 1,5 Ko → 1,6 Ko | 0,04 s → 0,06 s |

Revalidation (`If-None-Match`) à travers Caddy, trois encodages : **304, 0 octet** dans les trois cas.
Précache du service worker (build de production) : 1 213 Ko → 1 027 Ko gzip.

**Réserves à lire avant de citer ces chiffres**
- L'image « avant » de la pile locale n'est pas identique à l'image « après » : d'autres sessions ont modifié le frontend entre les deux mesures. Les écarts de première visite (−3 % à −31 %) ne sont donc pas tous attribuables à mes changements ; l'écart de visite répétée l'est (ETag/304 mesuré directement).
- Les temps d'API « avant » datent du 2026-10-25 ; la base locale a changé depuis (autres lots d'ingestion).
- **Profil lent (400 kbit/s, latence 400 ms, CPU ×4) : aucune amélioration mesurée.** Premier affichage ≈ 7,7–9,3 s avant, 8,2–9,6 s après (bruit). Le chemin critique (point 10) n'a pas été touché. De plus, à cette vitesse la mesure s'arrête avant la fin des téléchargements différés et du précache : les chiffres de « 2e visite » du profil lent ne sont pas exploitables.
- Pas de Lighthouse, pas de smartphone réel. Le nombre de requêtes SQL « avant » n'a pas été mesuré : « après », une page de 24 épreuves en fait 8 (avec ou sans `defer`, qui ne change que les octets lus) ; les requêtes groupées des cours associés et de leur statut vitrine ont été supprimées de ce chemin.

## 4. Tests

| Suite | Résultat |
|---|---|
| Backend `catalog edtech_cm access`, avant | 969 tests, OK (5 ignorés) |
| Backend `catalog edtech_cm access`, après | 996 tests, OK (5 ignorés) |
| Backend `inedit recherche`, après | 482 tests, OK |
| Backend `catalog access recherche`, après le dernier `defer` | 1 193 tests, OK |
| Frontend `vitest` complet | 1 260 tests OK ; 1 suite en erreur d'environnement Windows (`EBUSY` sur un fichier temporaire), repassée seule : OK |
| `tsc -b` | OK |
| `oxlint` | avertissements existants uniquement |

Non testés : le comportement dans un vrai navigateur après déploiement (mise à jour du service worker avec le précache réduit), les droits d'accès sur les endpoints dont les en-têtes changent au-delà des tests unitaires du middleware.

## 5. Limites et optimisations différées

- **Quiz hors ligne** (file locale idempotente, reprise) : **non fait**. La reprise côté serveur existe déjà (`/quiz/en-cours/`) ; le reste demande une conception propre (clé d'idempotence, XP, session terminée) et ne doit pas être livré sans tests de synchronisation.
- **Premier affichage sur réseau lent** : le chemin critique reste ~250 Ko gzip. Pistes : charger à la demande les modales d'onboarding/PIN et les menus Radix de l'en-tête, scinder `fr.ts` (152 Ko bruts) par page, `rehype-raw`/`parse5` (≈ 160 Ko bruts dans le chunk Markdown) si le contenu n'a pas besoin de HTML brut.
- **Précache** : les ~690 Ko de JavaScript restent précachés ; ils protègent un onglet ouvert contre un déploiement (chunks supprimés). À revoir seulement avec un test de mise à jour sur navigateur réel.
- **Polices** : 6 fichiers `woff2` (~125 Ko) au premier affichage ; réduire les graisses changerait l'identité visuelle, décision produit.
- **Pagination** : pas de `page_size` paramétrable ; l'accueil charge une page de 24 pour n'en montrer qu'une, désormais pour 2 Ko transférés.
- **Chaîne d'authentification anonyme** (point 9) : non traitée.
- **Images pédagogiques** (`media/`) : non auditées (conversion WebP des figures d'examen à ne faire qu'avec comparaison visuelle).

## 6. Commandes pour rejouer

```bash
# Tests backend (la pile locale doit tourner)
docker exec edukora-backend-1 sh -c 'cd /app && python manage.py test catalog edtech_cm access inedit recherche --noinput --parallel 1'
# Tests et typage frontend
cd frontend && npx tsc -b && npx vitest run
# Mesure réseau (profils rapide / lent) ; MSYS_NO_PATHCONV=1 sous Git Bash
venv/Scripts/python.exe scripts/perf/mesure_pages.py --profil rapide --sortie docs-perf/mesure.json
venv/Scripts/python.exe scripts/perf/mesure_pages.py --profil lent --repetitions 2
# Composition des chunks
cd frontend && node ../scripts/perf/analyse-bundle.mjs
# Validation Caddy
docker run --rm -e SITE_DOMAIN=:80 -v "$(pwd -W)/docker/caddy/Caddyfile:/etc/caddy/Caddyfile:ro" edukora-caddy:latest caddy validate --config /etc/caddy/Caddyfile
```

## 7. Déploiement (non exécuté)

Aucune migration, aucune variable d'environnement nouvelle. Il faut reconstruire **les deux images** : `edukora-backend` (middleware, sérialiseur, `defer`) et `edukora-caddy` (frontend embarqué + Caddyfile). Procédure : celle de `deploy/` (images `ghcr.io/…`, `deploy/deploy.sh`, retour arrière `deploy/rollback.sh`). Le Caddyfile de production contient des règles propres à la prod (media servi depuis `/srv/edukora/media`, Cloudflare devant) : relire le diff du Caddyfile avant de construire. Reprendre aussi la liste `@backend` si une route d'API a été ajoutée entre-temps. Un service worker déjà installé chez les élèves proposera la mise à jour (mode « prompt »).

## 8. À surveiller après la mise en production

- Part de réponses `304` sur l'API (journaux Caddy) et taille moyenne des réponses de liste.
- **Cloudflare** : `/media/*` et les logos sont maintenant `public` (1 h / 1 jour) : une figure redessinée peut rester servie jusqu'à 1 h chez l'élève et sur le cache de bord ; la purge Cloudflare habituelle ne couvre pas le cache du navigateur. Si c'est gênant, ramener `/media` à `no-cache`.
- Erreurs Sentry liées au service worker ou à « Failed to fetch dynamically imported module » après la mise à jour.
- Temps de réponse et mémoire sur le serveur de 2 Go (le `defer` doit les réduire, à confirmer).
- Qu'aucun écran n'attend plus `themes`/`related_cours` dans une liste (recherche, accueil) : un champ qui manquerait se verrait comme une section vide.
