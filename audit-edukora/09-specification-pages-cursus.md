# 09 - Spécification : pages d'atterrissage par cursus (lot L3, SEO-02)

Rédigée le 2026-11-12 pour votre validation (décision D4). **Rien n'est codé** : après votre accord, comptez environ 5 jours de travail (voir 08).

## État : IMPLÉMENTÉ en local le 2026-11-12 (non déployé)
Écarts par rapport à cette spécification, tous voulus :
- **GCE** : les deux pages GCE existent sous leur adresse française ET anglaise (`/cm/examens/gce-o-level` et `/en/cm/exams/gce-o-level`, auto-canoniques avec hreflang), comme tous les contenus GCE aujourd'hui. Les 13 pages deviennent 15 URLs dans le sitemap. Quand la décision D1 (chemin canonique des GCE) sera prise, elle s'appliquera à tous les contenus GCE d'un coup.
- **Cours** : beaucoup de cours ne sont rattachés à aucun examen (BEPC : 0) ; la phrase d'introduction n'en parle donc que lorsqu'il y en a (BAC D : "plus de 640 cours").
- **Liens d'entrée faits** : pied de page (colonne "Par examen") et lien "Toutes les annales du BEPC" depuis chaque fiche d'épreuve. **Pas faits** : puces de l'accueil, balisage `BreadcrumbList` (fil d'Ariane visuel présent).
- **Ajouts** : liste `/catalog/examens/<pays>/` (cache 10 min, pour le pied de page), champ `slug` dans l'API des cursus, liste des matières avec leurs comptes dans la page.
- Fichiers : `backend/catalog/pages_examen.py` (nouveau), `test_pages_examen.py` (nouveau, 18 tests), `views.py`, `urls.py`, `serializers.py`, `prerendu.py`, `apercu_partage.py`, `sitemap.py`, `segments_url.json` (+ copie frontend), `docker/caddy/Caddyfile` (regénéré) ; frontend : `ExamenPage.tsx` (+ test, 4 tests), `App.tsx`, `Footer.tsx`, `EpreuveDetailPage.tsx`, `api/*`, `countryPath.ts`, `i18n`.
- Mesures : 13 pages, 200 pour Googlebot via Caddy, 428 à 588 mots de texte chacune, canonical propre ; examen inconnu = 404 réel pour un moteur ; WhatsApp reçoit titre et description propres ; `/en/cm/examens/...` redirige en 301 vers `/en/cm/exams/...` ; CLS de la page 0,024 (mobile).

## 1. Objectif
Donner une page indexable et partageable à chaque examen que cherchent les élèves et les parents ("annales BEPC Cameroun", "BAC D annales corrigées", "GCE O Level past papers Cameroon"). Aujourd'hui `?cursus=14` est ramené par canonical à `/cm/epreuves`, donc ces recherches n'ont aucune page d'atterrissage.

## 2. Périmètre (mesuré en base locale)
13 pages pour le Cameroun, celles qui ont du contenu :
| Cursus | Id | Épreuves | | Cursus | Id | Épreuves |
|---|---|---|---|---|---|---|
| BEPC | 14 | 247 | | Probatoire E | 23 | 184 |
| Probatoire A | 15 | 199 | | BAC E | 24 | 137 |
| BAC A | 16 | 180 | | Probatoire TI | 25 | 121 |
| Probatoire C | 19 | 245 | | BAC TI | 26 | 143 |
| BAC C | 20 | 284 | | GCE O Level | 1414 | 405 |
| Probatoire D | 21 | 286 | | GCE A Level | 1416 | 456 |
| BAC D | 22 | 244 | | | | |
Exclus : les cursus des autres pays et les filières techniques sans contenu (0 épreuve) ; une page n'est créée que si le cursus a au moins une épreuve publiée (sinon 404, pour éviter les pages vides). Le total d'épreuves compte aussi des corrigés partagés entre cursus.

## 3. URL (proposition)
- Français : `/cm/examens/bepc`, `/cm/examens/probatoire-c`, `/cm/examens/bac-d`...
- Anglais : `/en/cm/exams/gce-o-level`, `/en/cm/exams/gce-a-level` ; les cursus francophones n'ont qu'une URL française (même règle que les contenus français sous `/en`).
- Nouveau segment `examens` → `exams` à ajouter dans `segments-url.json` (source unique lue par le frontend, le backend et Caddy ; un test vérifie la cohérence).
- Pourquoi pas `/cm/epreuves/bepc` : un slug d'épreuve peut avoir ce nom et prêter à confusion.
- Slug du cursus = examen + série en minuscules, avec tiret (`probatoire-c`).

## 4. Contenu de la page (calculé, rien à rédiger)
1. `h1` : "Annales corrigées du BEPC au Cameroun" (modèle FR) / "GCE O Level past papers with solutions in Cameroon" (EN).
2. Introduction de 2 à 3 phrases générées : nombre d'épreuves, années couvertes (min-max), matières, ce qui est gratuit (nombre de corrigés libres), mention de la séance du jour.
3. Compteurs : épreuves, cours, matières, corrigés libres.
4. Liste des épreuves récentes (30), groupées par matière : titre, année, "corrigé gratuit" ou "sujet libre", lien vers la fiche ; lien "Voir toutes les épreuves du BEPC" vers `/cm/epreuves?cursus=14` (page de liste filtrée, non indexée).
5. Bloc "Thèmes qui tombent au BEPC" : lien vers `/cm/themes-frequents?cursus=14`.
6. Bloc quiz gratuit : lien vers l'essai du cursus.
7. Appel à l'abonnement : prix au mois, lien `/tarifs`.
8. Fil d'Ariane (Accueil > Examens > BEPC) avec balisage `BreadcrumbList`.
Les textes fixes (gabarits) sont dans les fichiers de traduction FR et EN, relus par vous.

## 5. SEO de la page
- `title` : "Annales BEPC corrigées - Cameroun | EduKora" (gabarit par langue) ; `meta description` unique avec les chiffres du cursus.
- `canonical` : la page elle-même ; `hreflang` fr/en/x-default seulement pour les cursus GCE (qui existent en deux URLs) ; pas de hreflang pour les cursus francophones.
- Prérendu moteurs : nouveau genre dans `catalog/prerendu.py` (même mécanisme que les épreuves et les cours) et dans l'expression de chemin de Caddy (`@robots_moteurs`, `@robots_apercu`) ; vrai 404 pour un cursus inconnu ou sans épreuve.
- Aperçu de partage WhatsApp (`og:title`, `og:description`, image 1200×630) via `apercu_partage.py`.
- Sitemap : ajouter les 13 pages (avec hreflang pour les GCE) ; priorité plus haute que les épreuves.
- Maillage : lien depuis l'accueil (puces d'examen), le pied de page (colonne "Par examen") et chaque fiche d'épreuve ("Toutes les annales du BEPC").

## 6. Technique
| Couche | Travail |
|---|---|
| Backend | point d'accès public `GET /catalog/examens/<slug>/` (chiffres, liste d'épreuves, indicateurs de gratuité) ; gabarits de textes ; extension du prérendu et de l'aperçu ; extension du sitemap |
| Caddy | ajouter `examens|exams` aux deux expressions de chemin ; aucune autre règle |
| Frontend | page React `ExamenPage` (route `/:country/examens/:slug`), `useSeo`, fil d'Ariane, liens d'entrée ; route ajoutée aux segments traduits |
| Tests | prérendu (200 avec texte, canonical, 404), sitemap (13 URLs), segments d'URL (cohérence), composant |
| Mesure | `curl -A Googlebot` sur les 13 URLs ; ≥ 200 mots de texte hors liste ; inspection d'URL dans la Search Console |

## 7. Critères de validation
- Chaque page répond 200 pour Googlebot avec `h1`, introduction, liste, canonical propre et description unique.
- Les 13 URLs sont dans le sitemap ; aucune URL de page vide.
- `?cursus=` garde son canonical vers la liste (aucune régression).
- Aucune page n'expose un corrigé payant (seuls des titres et des chiffres).
- Retour arrière : retirer les URLs du sitemap et `git revert` du commit.

## 8. Risques et choix à confirmer
1. **Exposition de "corrigé libre"** : la liste signale les corrigés gratuits ; cohérent avec la décision du 2026-11-12 (corrigé libre = public).
2. **Chiffres affichés** : les totaux comptent les épreuves partagées entre cursus ; je recommande d'afficher "plus de N" (arrondi vers le bas) pour ne pas promettre trop.
3. **Cursus à plusieurs séries** (ex. "Probatoire C et E" pour une même épreuve) : une épreuve apparaît sur chaque page de cursus concernée ; pas de contenu dupliqué, mais le titre de la liste doit rester celui de l'épreuve.
4. **GCE** : respecte le choix D1 (chemin anglais canonique recommandé) ; les pages GCE FR ne sont pas créées.
5. Page par matière (BEPC maths) : volontairement après le lancement (L8a).

## 9. Ce que j'attends de vous
- Accord sur l'URL (`examens` / `exams`) et le titre type.
- Validation des gabarits de texte (FR et EN) que je rédigerai à l'étape suivante.
- Confirmation que 13 pages suffisent pour le 1er décembre.
