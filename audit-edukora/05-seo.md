# 05 - Audit SEO technique et on-page (Phase 3, local, lecture seule)

Méthode : `curl` avec User-Agent navigateur mobile, Googlebot et WhatsApp (Caddy sert un HTML différent aux moteurs et aux robots de partage), analyse des 20 sitemaps, rendu JavaScript lu dans le navigateur intégré. Mesures de performance via PerformanceObserver (desktop et mobile émulé), sans bridage réseau.
Limites : indexation, positionnement, backlinks, Search Console non mesurables en local. Écarts local / production signalés plus bas. Aucune donnée de volume de recherche n'est avancée.
Légende : **Fait** = observé avec preuve ; **Hypothèse** = à valider.

## 1. Architecture de rendu (fait, à connaître pour tout le reste)
- Site = SPA React. L'HTML initial de toutes les pages publiques est le même `index.html` (6 282 octets) : titre et description génériques, `<div id="root">`, aucun texte, pas de canonical (posé ensuite par JavaScript).
- Exceptions : Caddy redirige vers `/prerendu` (Django) uniquement pour **Googlebot, Bingbot, DuckDuckBot, Yandex, Baidu, Applebot** et seulement sur les chemins `épreuves / cours / épreuves inédites / aide` (FR et EN). Les robots de partage (WhatsApp, Facebook, Telegram...) reçoivent `/partage-apercu` sur les mêmes chemins et sur l'accueil `/en`.
- Conséquence : accueil, listes (`/cm/epreuves`, `/cm/cours`), `/tarifs`, `/cm/themes-frequents`, `/quiz`, `/a-propos`, index `/aide` n'ont **aucun contenu dans l'HTML initial** ; les moteurs qui n'exécutent pas JavaScript (ou le font tard) ne les voient pas. Google exécute le JavaScript, mais de façon différée.

## 2. Indexabilité
| Élément | Résultat | Preuve |
|---|---|---|
| robots.txt | Présent, soigné : `Allow /`, `Disallow` des routes de téléchargement et de sessions ; robots d'IA bloqués (`/quiz/`, `/catalog/`, `/inedit/`...). Ligne `Sitemap: https://edukora.africa/sitemap.xml` (hôte de prod en dur). | `curl /robots.txt` |
| sitemap.xml | Index de 20 sous-sitemaps, **17 247 URLs** : 13 648 cours FR + 953 cours EN, 2 145 épreuves FR, 862 épreuves EN, 257 inédites FR, 20 mock-papers EN, 32+32 articles d'aide, pages statiques FR/EN. hreflang fr/en/x-default sur les entrées. `lastmod` par URL présent. Les URLs sont celles de l'hôte demandé (localhost en local). Aucune URL listée n'est interdite par robots.txt. Échantillon de 24 URLs au hasard : 24 × 200. | analyse des sitemaps |
| Absentes du sitemap | `/cm/themes-frequents` (la page "ce qui tombe"), `/quiz`, `/a-propos`, `/qui-etudie`, pages par cursus ou par matière (il n'y en a pas, voir SEO-02). | `grep` sur les 17 247 chemins |
| meta robots / X-Robots-Tag | En-tête `X-Robots-Tag: index, follow` sur tout (valeur pilotée par la variable `ROBOTS_TAG` du `.env`, par défaut index). Pages privées et utilitaires en `noindex, follow` posé par JavaScript : `/connexion`, `/quiz`, `/cm/recherche`, 404. | en-têtes, DOM rendu |
| canonical | Prérendu : auto-référent, hôte de la requête. Rendu JS : toujours `https://edukora.africa/...` (hôte de prod en dur), filtres de liste ramenés à `/cm/epreuves`. | DOM rendu |
| Codes HTTP | Épreuve ou cours inconnu pour un moteur : **404 réel** (bon). Pour un navigateur ou une route inconnue : **200** (soft 404, avec `noindex` JS sur les routes inconnues). `/cm/`, `/CM`, `/cm/epreuves/` : 200, même HTML. `/` : 200 sans redirection serveur (la SPA redirige vers `/cm`). | `curl` UA navigateur vs Googlebot |
| Redirections | Aucune redirection serveur observée (ni http→https, ni slash final, ni casse) : en local uniquement ; la production passe par Cloudflare, à vérifier. | `curl -w redirect_url` |

## 3. Pages à fort potentiel (title, meta, Hn, URL, maillage)
- **Épreuve** (`/cm/epreuves/mathematiques-bepc-2026`, prérendu) : title "Mathématiques BEPC 2026 | EduKora" (unique, sans "corrigé" ni "Cameroun"), meta description "Corrigé d'annale de Mathématiques (2026) - sujet en accès libre, corrigé détaillé par abonnement." (modèle unique pour toutes les épreuves ; **faux pour une épreuve au corrigé libre**, qui affiche "Corrigé en accès libre"). Un seul `h1`, pas de `h2` dans le HTML bot ; le HTML bot contient l'énoncé en Markdown/LaTeX brut, **pas le corrigé**, et seulement 2 liens internes (Accueil, Toutes les épreuves), alors que la page rendue en a 31 (cours associés, autres épreuves).
- **Cours** (prérendu) : texte complet du cours (prérequis, règle, exemple), `h1` + 5 `h2` + 6 `h3`, canonical commun `/cours/<slug>/lire`. Bon.
- **Accueil, listes, tarifs** (JS) : titles utiles pour l'accueil ("Corrigés BEPC, Probatoire, BAC - Cameroun | EduKora"), génériques ailleurs ("Prix | EduKora", "Épreuves et corrigés | EduKora", "Quiz | EduKora"). Hn corrects (un `h1`).
- **URLs** : lisibles pour les épreuves (`/cm/epreuves/mathematiques-bepc-2026`) ; les cours n'ont pas de pays et des slugs très longs (jusqu'à plus de 100 caractères, formulés en compétence : "identifier-les-composants-dun-formulaire-web").
- **Fil d'Ariane** : absent (ni visuel ni balisage).
- **Images** : 7 images sur l'accueil, toutes avec `alt`.

## 4. Bilinguisme
- `lang` : `fr` par défaut, `en` sur `/en/...` (posé dès l'HTML via un script, puis par l'application). Bon.
- hreflang : présent sur les pages statiques (accueil, tarifs...) et les épreuves GCE ; absent des épreuves francophones (pas d'équivalent EN, normal).
- **Contenu dupliqué** : 861 épreuves GCE existent à la fois sous `/cm/epreuves/<slug>` et `/en/cm/past-papers/<slug>`, avec le même contenu anglais, chacune auto-canonique, toutes deux dans le sitemap, hreflang `fr` ↔ `en` et `x-default` pointant vers l'URL de la version "française" (SEO-04).
- og:locale : `fr_FR` / `en_GB`, bien posé.

## 5. Open Graph, Twitter, partage WhatsApp / Facebook (fait)
Pages d'épreuve, de cours et accueil `/en` : `og:title`, `og:description`, `og:image` 1200×630 (PNG généré, 56 Ko, 0,15 s), `og:image:alt`, `twitter:card=summary_large_image`, `og:locale`. Très bon pour le partage. Limites : sur les autres pages (tarifs, listes, thèmes, quiz, aide), `og:url` = `https://edukora.africa/` et image par défaut ; `og:type` vaut `website` partout (même pour une épreuve).

## 6. Données structurées (fait)
Aucun `application/ld+json` sur le site (accueil, tarifs, épreuve, cours, prérendu). Candidats utiles : `Organization` (accueil), `BreadcrumbList`, `LearningResource` / `Course` sur les cours, `FAQPage` sur `/tarifs` (note : Google ne montre plus les résultats enrichis FAQ qu'à certains sites ; ne pas attendre d'effet visible).

## 7. Performance (local, estimations)
- Poids initial de l'accueil : ≈ 310 Ko compressés (JS+CSS), hero 20 Ko ; fichiers `/assets` en cache 1 an immuable (très bien).
- Compression d'origine : **gzip seulement** (433 Ko → 140 Ko pour le bundle principal ; `Accept-Encoding: br` ne donne pas de brotli). Hypothèse : Cloudflare (utilisé en production d'après les notes du projet) peut compresser en brotli ; à vérifier sur l'URL réelle.
- **CLS** : 0,945 puis 0,901 sur `/cm`, 0,901 sur une épreuve, 0,602 sur `/tarifs`. Un seul décalage à 540-735 ms : le pied de page est affiché sans le contenu, puis poussé vers le bas à l'arrivée du contenu (UX-01 reproduit sur 3 pages, desktop et mobile).
- LCP et INP : non mesurés (l'outil du navigateur intégré n'a pas renvoyé de LCP). Ne pas conclure.
- Images de contenu `/media/...` : cache 1 h seulement. Requêtes API publiques (stats, cursus, campagnes) : `Cache-Control: private, no-cache`. 20 déclarations de polices KaTeX en `font-display: block` (texte invisible possible jusqu'au chargement de la police).
- Mobile-first : `viewport` correct, pas de défilement horizontal vérifié sur ~15 pages (375 px).

## 8. Pages d'erreur
- Route inconnue : page 404 soignée (FR et EN), `noindex, follow`, titre "Page not found", mais **HTTP 200**.
- Épreuve ou cours inconnu : 404 réel pour les moteurs (prérendu) ; pour un visiteur la SPA affiche un message ("Cette épreuve n'existe pas...") sans `noindex` et avec le titre de la page précédente de type "Solution | EduKora" (HTTP 200 côté navigateur, sans conséquence si les moteurs passent par le prérendu).

## 9. Écarts local / production à vérifier
1. `ROBOTS_TAG` du `.env` de production : ne doit pas contenir `noindex` ; sur toute autre machine exposée (recette), il doit en contenir un.
2. `https://edukora.africa` est codé en dur dans les canonical/og:url posés par JavaScript et dans `robots.txt` : correct en production, trompeur sur une recette.
3. Compression (brotli), redirections http→https et `www`, cache HTML derrière Cloudflare : non vérifiables ici.
4. Sitemap : en production, vérifier que les `<loc>` sont en `https://edukora.africa/...` (ici `http://localhost`).
5. Google Search Console : le fichier de vérification `googlee01691e70fdf5677.html` est présent ; un test d'inspection d'URL réelle reste à faire.

## 10. Intentions de recherche probables (hypothèses, sans volumes) et page qui devrait y répondre
| Intention probable (élève / parent) | Page aujourd'hui | Écart |
|---|---|---|
| "épreuve BEPC maths corrigé", "BEPC maths 2024 corrigé" | Page d'épreuve `/cm/epreuves/<matière-examen-année>` | Title sans "corrigé" ; description fausse pour les corrigés libres ; corrigé absent du HTML bot |
| "sujet probatoire C physique 2023" | Idem | Idem ; pas de page de synthèse "Probatoire C physique" |
| "annales BEPC Cameroun", "BAC D annales corrigées" | Aucune page cursus indexable (filtre `?cursus=` ramené à `/cm/epreuves`) | Absence de page par cursus et par matière (SEO-02) |
| "cours équation du second degré terminale" | `/cours/<slug>/lire` | Slugs en forme de compétence ("résoudre-...") ; bon contenu dans le HTML bot |
| "GCE past papers Cameroon", "GCE O Level maths 2019 solutions" | `/en/cm/past-papers/...` | URL dupliquée en FR (SEO-04) ; pas de page "GCE O Level past papers" par matière |
| "quiz maths BEPC en ligne" | `/quiz` (noindex) | Page volontairement non indexable : à arbitrer |
| "thèmes qui tombent au BAC / probatoire" | `/cm/themes-frequents` | Hors sitemap, contenu JS uniquement |
| "EduKora prix", "EduKora avis", "payer EduKora mobile money" (requêtes de marque) | `/tarifs`, `/aide/comment-payer` | Title "Prix \| EduKora" faible ; pas de balisage Organization |
| "comment réviser le BEPC", "méthode de révision probatoire" (parents) | Aucune page éditoriale | Contenu éditorial absent ; hypothèse de levier d'acquisition |

## 11. Ce qui est bon
Prérendu bots avec 404 réels, canonical, OG 1200×630 et alt ; sitemaps bilingues avec hreflang et `lastmod` ; robots.txt réfléchi ; `noindex` sur les pages privées ; titres uniques sur les pages de détail ; `lang`, viewport et alt d'images corrects ; cache longue durée des assets ; contenu de cours complet pour les moteurs.
