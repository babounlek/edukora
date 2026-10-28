# PROMPT CLAUDE CODE — Performances et économie de données d'EduKora

> À coller tel quel dans une session Claude Code ouverte à la racine de `D:\edukora`.
> Version resserrée et ancrée sur l'état réel du dépôt (constaté le 2026-10-25).

---

## 1. Mission

Rendre EduKora rapide et sobre en données mobiles pour un élève camerounais sur un smartphone d'entrée de gamme, en 3G/EDGE instable, avec un forfait qui se vide.

Principe directeur : **ne jamais télécharger une donnée inutile, ne jamais retélécharger une donnée déjà détenue, ne jamais bloquer un contenu essentiel en attendant une donnée secondaire.**

Tu travailles dans le dépôt existant. Tu mesures, tu changes, tu remesures. Tu n'écris pas un plan théorique : chaque affirmation de gain s'appuie sur une mesure que tu as faite, sinon tu écris « non mesuré ».

## 2. Ce qui existe déjà — ne pas refaire, ne pas casser

Vérifie chaque point avant de t'y fier (le code a pu bouger), puis **améliore l'existant au lieu de le doubler**.

**Frontend** (`frontend/`) : React 19, Vite 8, TypeScript, Tailwind 4, React Router 7, TanStack Query 5, react-markdown + KaTeX, Sentry, polices `@fontsource` (Fraunces, Work Sans). Interface bilingue FR/EN avec préfixe `/en` dans l'URL.

- **PWA déjà en place** : `vite-plugin-pwa` / Workbox dans `frontend/vite.config.ts`, `registerType: 'prompt'` (choix délibéré : pas de rechargement en plein examen), enregistrement dans `src/lib/pwa.ts`, interrupteur d'urgence `VITE_DISABLE_PWA=1`, `push-sw.js` pour les notifications. Règles actuelles : coquille en `NetworkFirst` (timeout 4 s), contenu de lecture en `NetworkFirst` (120 entrées, 30 jours, `purgeOnQuotaError`), `/assets/` en `CacheFirst`. **`navigateFallback: null` est volontaire** (une coquille périmée servie à un visiteur en ligne a déjà causé un incident qui a fait désactiver la PWA : lis le commentaire de `src/main.tsx` avant de toucher à quoi que ce soit ici).
- **Liste fermée du contenu hors ligne** : `src/lib/contenuDeLecture.ts` (`CONTENU_DE_LECTURE`), partagée avec les tests du service worker. Ne l'élargis jamais à des réponses personnelles (compte, paiements, séances).
- Découpage de code déjà partiel (`React.lazy` dans `App.tsx`, `EpreuveMarkdownLazy`, `GuideHost`, `CarteReponse`). `staleTime` global de 60 s dans `main.tsx`. Cache d'accueil dans `src/lib/accueilCache.ts`. Le commit `77f35b12` a déjà allégé le chargement des visiteurs anonymes et les polices. Drapeaux `flag-icons` déjà sortis du CSS (`assetsInlineLimit`).
- **Points de poids visibles dans `frontend/dist/assets`** (à confirmer par mesure, pas à prendre pour acquis) : chunk `EpreuveMarkdown` ≈ 605 Ko, `index` JS ≈ 420 Ko, CSS ≈ 220 Ko, `client` ≈ 203 Ko, plusieurs SVG de drapeaux de 100–180 Ko, `dist` ≈ 11 Mo / ~790 fichiers.

**Caddy** (`docker/caddy/Caddyfile`) : `encode zstd gzip`, `/assets/*` en `immutable` 1 an, points d'entrée (`/`, `index.html`, `sw.js`, `manifest`…) en `no-cache`. Le frontend est **cuit dans l'image caddy** : toute modification du frontend exige de reconstruire l'image caddy. La liste `@backend` des chemins envoyés à Django est tenue à la main : toute nouvelle route d'API doit y être ajoutée (oublis déjà constatés en prod). Le bloc `redirections-segments-en` est généré par `scripts/generer_caddy_segments.py` : ne pas l'éditer à la main.

**Backend** (`backend/`, Django + DRF + PostgreSQL) : `PageNumberPagination` globale, `PAGE_SIZE = 24`. Quotas de téléchargement PDF par jour (`backend/access/quota.py`) ; les PDF « sujet » passent par Django (`/access/lessons/<id>/sujet.pdf`) et Caddy bloque `/media/sujets_pdf/*` pour que personne ne contourne le quota. Cours libres : les exercices d'application sont payants, verrou côté serveur. Reprise de quiz côté serveur (`GET /quiz/en-cours/`), instantané des questions de quiz, rejeu neutre pour XP/maîtrise.

**Production** : `docker-compose.prod.yml` tire des images `ghcr.io/…` (backend, relances, caddy, backup). Serveur à **2 Go de RAM** ; l'état réel de la prod est incertain (voir la mémoire du projet) : ne présume rien, ne la touche pas.

## 3. Règles non négociables

1. **Aucun déploiement, aucun `build`/`up`/`restart` sur la prod, aucune écriture sur des données de prod.** Les commandes de déploiement sont *écrites* dans le rapport, jamais lancées.
2. **Ne contourne aucune permission, aucun quota, aucun verrou d'abonnement.** Tout cache HTTP respecte la visibilité de la donnée :
   - public (catalogue, métadonnées) → cacheable ;
   - dépend de l'abonnement ou de l'utilisateur → `Cache-Control: private` et `Vary: Authorization, Cookie` (ou équivalent selon l'authentification réelle : lis-la d'abord), jamais de cache partagé ;
   - PDF protégés → jamais servis depuis un cache partagé, et les requêtes conditionnelles ou `Range` ne doivent ni contourner ni **doubler** le décompte du quota.
3. **Ne réécris pas** le frontend ni le backend, n'ajoute pas de dépendance lourde, ne change pas de bibliothèque sans mesure. Pas de migration sans justification par un plan d'exécution observé.
4. **Ne touche pas aux données pédagogiques** ni au dossier `backend/ingest/` (partagé avec le conteneur). L'arbre peut contenir des modifications non committées qui ne sont pas les tiennes : lis `git status` / `git diff` avant d'éditer un fichier, et ne les annule ni ne les écrase.
5. **Ne committe rien** sans demande explicite. Si je demande un commit, ajoute les fichiers nommément (jamais `git add .`) et relis le diff complet, pas seulement `--stat`.
6. Aucun pré-chargement de fichier volumineux (PDF, images lourdes) : l'élève paie ses octets. Tout téléchargement lourd est déclenché par un clic, avec la taille affichée avant.
7. Aucune optimisation ne dégrade la lisibilité des formules, tableaux, schémas et figures d'examen.
8. Garde les tests existants au vert. Avant de changer quoi que ce soit, lance la suite et note l'échec de référence (certains tests backend échouent déjà pour des raisons d'environnement : paiements, clés VAPID ; ce sont les *mêmes* échecs avant et après qui comptent, pas leur absence).

## 4. Environnement d'exécution

- Le code qui fait foi est la copie de travail `D:\edukora` (les worktrees de `.claude/worktrees/` sont périmés, ignore-les).
- Le dev local a besoin du Postgres Docker (`DB_HOST=db`). **Mesure sur le build de production** (`vite build` + image caddy locale ou `vite preview` derrière un Caddy local), jamais sur le serveur de dev : ses chiffres n'ont aucun rapport.
- Pour patcher le backend dans un conteneur local sans reconstruire : `docker cp` d'un fichier à la fois (pas de bind mount). Après une modification du frontend : `docker compose build caddy && docker compose up -d caddy` en **local uniquement**.
- Pour piloter le navigateur et la mesure : navigateur intégré (outils `mcp__Claude_Browser__*`) ou Lighthouse en ligne de commande si disponible. Émule le réseau avec `Network.emulateNetworkConditions` (CDP) ; profils : **lent = 400 kbit/s, latence 400 ms** (CPU ralenti ×4) et **référence = connexion rapide**.

## 5. Méthode — mesurer d'abord, puis agir en boucle courte

### Étape 0 — Référence (avant tout changement)
Construis le frontend en production, lance la stack locale et consigne dans `docs-perf/baseline.md` (ou le dossier de rapport que tu choisis, crée-le) pour chaque scénario ci-dessous : octets **transférés** (avec compression), octets **décompressés**, nombre de requêtes, FCP/LCP/TBT/TTI, temps de réponse des endpoints, nombre de requêtes SQL par endpoint.

Scénarios minimum : première visite sans cache · retour sur une page déjà visitée · accueil connecté vs anonyme · navigation entre matières · ouverture d'un cours (`/lire`) · ouverture d'une annale · démarrage et déroulement d'un quiz · téléchargement volontaire d'un PDF · coupure réseau pendant la lecture · reprise après retour du réseau · profil lent + CPU ralenti.

Outils backend : `django-debug-toolbar` n'est pas requis ; utilise `connection.queries` / `assertNumQueries` / `EXPLAIN (ANALYZE, BUFFERS)` sur les requêtes réellement observées, et un script de timing reproductible (`scripts/perf/`). Fais tourner chaque mesure ≥ 3 fois, rapporte la médiane.

### Étape 1 — Diagnostic hiérarchisé (court)
Un tableau, trié par `(octets économisés × élèves touchés) / (effort × risque)`, avec pour chaque ligne : constat mesuré, cause (fichier:ligne), correctif proposé, risque de régression. Pas de roman. Présente les **10 meilleures lignes**, puis passe directement à l'implémentation sans attendre, sauf si une ligne exige une décision produit (signale-la et continue avec les autres).

Pistes à vérifier en priorité, vu l'état du dépôt (hypothèses, pas des certitudes) :
- Poids du chunk `EpreuveMarkdown` (react-markdown + remark/rehype + KaTeX) : peut-il être découpé davantage (KaTeX chargé seulement si le contenu contient `$`) ? Les polices KaTeX sont-elles toutes précachées ?
- Contenu du chunk `index` (≈ 420 Ko) et du CSS (≈ 220 Ko) : qu'y a-t-il d'inutile à l'accueil (Sentry chargé immédiatement ? i18n EN chargé pour un visiteur FR ? 2 042 clés de traduction : un seul chunk par langue ?). Le fichier anglais (`en-*.js`, ≈ 135 Ko) ne doit jamais être téléchargé par un visiteur francophone.
- Drapeaux SVG de 100–180 Ko : optimisables (SVGO) ou remplaçables, ne charger que ceux affichés.
- Requêtes de l'accueil et des listes : doublons, cascades (waterfall), absence d'annulation au changement de page, `refetchOnWindowFocus` / `refetchOnReconnect` qui retélécharge sans nécessité sur mobile.
- Endpoints de liste qui renvoient des champs lourds (énoncés, corrigés, descriptions complètes) alors que l'écran affiche un titre et un badge. Sérialiseurs « liste » vs « détail ».
- ORM : N+1, `select_related` / `prefetch_related` manquants, compteurs calculés par requêtes séparées, index absents *démontrés* par `EXPLAIN`.
- Absence de `ETag` / `Last-Modified` sur les réponses publiques stables (catalogue, métadonnées) : un `304` sans corps économise l'essentiel. Vérifie si `ConditionalGetMiddleware` ou un décorateur `condition()` convient, en tenant compte de la langue (`Accept-Language` / préfixe `/en`) : une réponse qui varie par langue doit déclarer `Vary` correctement.
- Compression : Caddy compresse déjà zstd/gzip. Vérifie qu'elle s'applique bien aux JSON de Django proxifiés, aux SVG, et **pas** aux PDF/WebP/PNG ; vérifie que `Content-Length`/`Range` des PDF restent corrects.
- Images pédagogiques (`media/`) : poids, dimensions, WebP/AVIF possibles, `loading="lazy"`, `width`/`height`, `srcset`. Ne convertis pas une figure d'examen dont la netteté compte sans comparaison visuelle.
- Polices : combien de graisses/sous-ensembles Fraunces + Work Sans sont réellement chargés à la première visite ? `font-display: swap` ? Une police système suffit-elle pour le corps de texte ?
- `Cache-Control` des réponses JSON de Django : valeur actuelle par endpoint (probablement aucune → le navigateur ré-interroge à chaque fois).

### Étape 2 — Implémenter par groupes, vérifier à chaque groupe
Ordre :
1. **Gains immédiats** : requêtes redondantes supprimées, champs inutiles retirés des listes, découpage de code, chargement différé, images/SVG/polices, pagination ou chargement progressif là où une liste dépasse ce qu'un écran affiche.
2. **Réutilisation des données** : `Cache-Control` + `ETag` / `304` sur les réponses publiques stables, `staleTime`/`gcTime` raisonnés par type de donnée dans TanStack Query, persistance du cache de requêtes **uniquement pour les données publiques et non sensibles**.
3. **Résilience réseau** : améliore la PWA existante plutôt que de la remplacer — indicateur « disponible hors ligne » sur les contenus de la liste fermée, action explicite « Garder hors ligne » (taille affichée, plafond de stockage, suppression en un geste, purge à la déconnexion et à la révocation de l'abonnement), message de mise à jour (déjà en `prompt`), file d'attente locale des réponses de quiz.
4. **Structurel** : requêtes SQL coûteuses, endpoints lourds, JS résiduel.

Après **chaque** groupe : tests frontend (`npm test`, `tsc -b`, `oxlint`), tests backend ciblés, remesure des scénarios touchés, note dans le journal. Si une mesure *empire*, annule ce changement (sur ton propre diff seulement) et consigne pourquoi.

### Étape 3 — Quiz hors ligne (le point le plus risqué : fais-le en dernier et prudemment)
La reprise de quiz existe déjà côté serveur (`/quiz/en-cours/`). Ajoute seulement ce qui manque :
- file locale des réponses non confirmées (IndexedDB), chacune avec une **clé d'idempotence** générée côté client ; le serveur rejette les doublons sans effet de bord ;
- une réponse n'est « enregistrée » dans l'interface qu'après l'accusé du serveur ;
- un rejeu ou une synchronisation tardive ne doit pas créditer l'XP deux fois, ne pas modifier un score déjà calculé, ne pas réouvrir une session terminée ;
- conflit (session terminée ou abandonnée côté serveur) → message clair, aucune perte silencieuse ;
- ne télécharge **pas** les corrigés avant l'étape pédagogique prévue ; ne mets pas les clés de correction dans un cache local lisible.
Si la sécurité de la synchronisation ne peut pas être démontrée par des tests, **ne livre pas la fonction** : documente la limite.

## 6. Tests de non-régression à écrire ou à vérifier

- Accès public / abonné / non-abonné / utilisateur A ≠ utilisateur B sur chaque endpoint dont tu changes les en-têtes (un test par cas : l'abonné reçoit le contenu, le non-abonné non, et aucune réponse privée ne porte `public`).
- PDF : quota décompté une seule fois, `Range` et requêtes conditionnelles ne le contournent pas, `/media/sujets_pdf/*` reste bloqué.
- Contrats API : le frontend (et ses tests) fonctionne avec les nouvelles formes de réponse ; tout champ retiré d'une liste est vérifié absent des usages (`grep` + types TypeScript).
- Pagination : pas de doublon ni d'omission d'un lot à l'autre (ordre stable).
- Service worker : un déploiement ne laisse pas un ancien JS parler à un nouveau backend (test de la stratégie de mise à jour ; tests existants de `CONTENU_DE_LECTURE`).
- Quiz : score, correction, XP, reprise, avec et sans réseau.
- Langues : FR et EN (préfixe `/en`) ; un cache ne mélange jamais les deux.
- Caddy : valide la configuration (`caddy validate`) ; vérifie les en-têtes par `curl -I` sur : une page, un asset hashé, `index.html`, `sw.js`, une API publique, une API privée, un PDF.

## 7. Livrables (un seul rapport, `docs-perf/RAPPORT.md`, + diff dans l'arbre de travail)

1. Diagnostic (tableau du §5, étape 1) avec les chiffres mesurés.
2. Liste des fichiers modifiés, une ligne de justification chacun.
3. Tableau **avant / après** par scénario : transféré, décompressé, requêtes, FCP/LCP/TTI (profil lent et rapide), requêtes SQL, temps de réponse. Une colonne « mesuré / non mesuré ». Distingue explicitement octets sur le réseau, octets décompressés et octets servis depuis le cache.
4. Résultats des tests, avec les échecs d'environnement connus nommés séparément des régressions.
5. Optimisations **non** faites et pourquoi (risque, besoin d'une décision produit, besoin de la prod).
6. Migrations / changements de config nécessaires (en espérant : aucune migration).
7. Commandes exactes pour rejouer tests et mesures en local avec Docker.
8. Procédure de déploiement adaptée à l'existant (images ghcr, rebuild caddy pour le frontend, mise à jour des `@backend` si une route a été ajoutée), **non exécutée**.
9. Points à surveiller après mise en production (taux de `304`, taille des réponses, erreurs Sentry liées au service worker, stockage utilisé, quotas PDF, temps de réponse sur 2 Go de RAM).

## 8. Critère de réussite

Sur le profil 400 kbit/s : première visite sensiblement plus légère et utilisable plus tôt ; visite répétée proche de zéro octet pour la coquille et les données publiques déjà vues (`304` ou cache) ; un cours ou une annale déjà ouvert se relit sans réseau ; aucune fuite de contenu protégé ; aucun test qui passait avant ne casse.

Fixe-toi des **budgets chiffrés après avoir mesuré la référence** (JS initial, CSS bloquant, octets de la première visite, requêtes à l'accueil), annonce-les dans le diagnostic, et rends compte de leur atteinte. N'invente pas d'objectif avant d'avoir vu les chiffres.

Si tu butes sur une décision qui change le produit (par exemple : durée de conservation hors ligne d'un contenu payant après fin d'abonnement), pose **une** question précise puis continue sur les autres chantiers.

Commence maintenant par l'étape 0.
