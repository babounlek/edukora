# 01 - Constats finaux (dédoublonnés, sévérisés, revérifiés) - audit du 2026-11-12

Cible : version locale (Docker, http://localhost), lecture seule. Personas jouées en **visiteur seul** (choix du user) : parent, élève BEPC, élève Probatoire C, élève GCE O Level ; mobile 375x812. Audit SEO par curl (User-Agent navigateur, Googlebot, WhatsApp) et rendu JS.
**Fait** = observé avec preuve. **Hypothèse** = à valider. Simulation : pas un test utilisateur.
**Non couvert** : inscription réelle (code OTP), séance du jour, parcours connecté, déclaration de paiement, profils enfants, A Level, 3G réelle, LCP et INP, indexation réelle.
Revérification (Phase 4) : chaque Majeur a été rejoué une seconde fois avec les étapes écrites ; résultat dans la colonne "Retest".

## A. Synthèse par sévérité
- **Bloquant : 0 confirmé.** 1 point à vérifier en production qui pourrait en devenir un (SEO-10).
- **Majeur (reproduits 2 fois) : 5** : UX-01, SEO-01, SEO-02, SEO-03, SEO-04. **Majeur non vérifiable sans paiement : 1** (UX-04, hypothèse).
- **Mineur : 15** - **Cosmétique : 5**.

## B. Constats Majeurs et à vérifier
| ID | Persona / axe | Constat (fait) | Étapes de reproduction | Retest | Impact |
|----|---------------|----------------|------------------------|--------|--------|
| UX-01 | Tous, performance perçue | Décalage de mise en page (CLS) très élevé : 0,945 puis 0,901 sur l'accueil /cm, 0,901 sur une épreuve, 0,602 sur /tarifs. Un seul décalage à 540-735 ms : le pied de page s'affiche sans le contenu puis est poussé vers le bas. Seuil "mauvais" de Google : 0,25. | 1. Ouvrir http://localhost/cm (mobile ou desktop). 2. Console : PerformanceObserver `layout-shift` (buffered). 3. Lire la valeur et `sources` (FOOTER). | Reproduit 4 fois sur 3 pages (mobile et desktop). Confirmé. | Acquisition (Core Web Vitals), sensation de saut sur connexion lente |
| SEO-01 | SEO rendu / contenu | Le HTML prérendu pour Googlebot contient l'énoncé mais pas le corrigé, y compris pour les corrigés en accès libre (Maths BEPC 2026, Physique Probatoire C et E 2026, Additional Mathematics GCE O Level 2023 testés). Les cours sont prérendus en entier. Hypothèse : choix voulu pour protéger le payant ; à arbitrer pour les libres. | `curl -A "Googlebot/2.1" http://localhost/cm/epreuves/mathematiques-bepc-2026` puis chercher le texte du corrigé ("Rappel de méthode") : absent. | Reproduit sur 3 épreuves libres. Confirmé. | Acquisition (requêtes "épreuve X corrigé") |
| SEO-02 | SEO pages d'atterrissage | Aucune page indexable par cursus ni par matière : `?cursus=14` est ramené par canonical à /cm/epreuves ; les sitemaps ne listent que /cm et /cm/epreuves comme pages de liste. | Ouvrir /cm/epreuves?cursus=14&gratuit=true, lire `link[rel=canonical]` ; `grep` des 17 247 URLs des sitemaps. | Reproduit. Confirmé. | Acquisition ("annales BEPC Cameroun", "BAC D maths") |
| SEO-03 | SEO on-page | La meta description de toutes les épreuves est la même phrase-type : "... sujet en accès libre, corrigé détaillé par abonnement." Fausse pour les corrigés libres (page : "Corrigé en accès libre" / "Free-access solution"). Sans niveau d'examen ni "Cameroun" ; titles sans "corrigé". | `curl -A Googlebot` sur /cm/epreuves/mathematiques-bepc-2026 (libre) et .../mathematiques-bepc-2025 (payant) : description identique. | Reproduit sur 3 pages libres FR/EN. Confirmé. | Acquisition (taux de clic), confiance |
| SEO-04 | SEO bilinguisme | 861 épreuves GCE sont sous /cm/epreuves/<slug> et /en/cm/past-papers/<slug> avec le même contenu anglais, auto-canoniques, toutes deux dans le sitemap ; hreflang fr↔en et x-default vers l'URL "française". | `curl -A Googlebot` sur les deux URLs de biology-gce-o-level-2026-paper-1 : deux canonical distincts, mêmes hreflang. | Reproduit sur 2 paires. Confirmé. | Acquisition GCE, doublons d'index, anglophones sur interface française |
| UX-04 | Parent, conversion | Fait : l'activation du paiement est manuelle, "≈ 3 heures", paiement hors application (numéro Mobile Money affiché après connexion). **Hypothèse** (non exécutée) : un élève qui veut réviser de suite attend jusqu'à 3 h sans suivi ; pic de charge au lancement. | Lire /tarifs "Comment ça se passe" étape 3. | Non vérifiable sans paiement. **Hypothèse, pas un Majeur prouvé.** | Conversion, confiance, charge d'équipe |
| SEO-10 | SEO écarts local/prod | À vérifier en production : ROBOTS_TAG du .env sans noindex ; loc des sitemaps en https://edukora.africa ; redirections http→https/www ; brotli. En local, canonical JS, og:url et robots.txt portent l'hôte de prod en dur. | Caddyfile (`X-Robots-Tag "{$ROBOTS_TAG:index, follow}"`), robots.txt, sitemap. | Non vérifiable en local. | Acquisition (un noindex oublié serait Bloquant) |

## C. Constats Mineurs et Cosmétiques
| ID | Persona / axe | Constat | Sévérité | Impact |
|----|---------------|---------|----------|--------|
| UX-02 | Élève, parent, conversion | Un lien direct /lire vers un corrigé payant renvoie à /connexion sans contexte (ni titre, ni prix). **Retest : le bouton Partager du lecteur partage la fiche /epreuves/<slug>, et la fiche payante n'a pas de lien "Lire"** : seul un favori ou un historique y mène. Rétrogradé de Majeur à Mineur. (capture : captures/UX-02-lire-payant-redirige-connexion.jpg) | Mineur | Conversion (faible) |
| UX-03 | Parent | Accueil et tarifs parlent à l'élève ("tu") ; l'entrée "Parent" n'existe que dans À propos et dans "Montrer à mes parents" (fiche payante). Hypothèse : un parent venu d'un message WhatsApp ne se reconnaît pas sur l'accueil. | Mineur | Conversion |
| UX-05 | Parent | À la connexion, l'e-mail est le champ par défaut, le téléphone un lien secondaire (le formulaire téléphone fonctionne, +237). Hypothèse : beaucoup de parents n'ont pas d'e-mail. | Mineur | Conversion |
| UX-06 | Parent | Après "Continuer · 3 mois · 6 000 FCFA", /connexion ne rappelle pas le choix (BEPC, 3 mois, total) ; le texte est redondant ("Connecte-toi pour finaliser ton abonnement. Connecte-toi en quelques secondes."). Le parent s'arrête avant de voir où payer. | Mineur | Conversion |
| UX-08 | Tous, mobile | **Qualifié** : 33 éléments de moins de 32 px de haut ou de large sur une épreuve : 10 liens en ligne, "Retour au catalogue" (74x18), liens du pied de page (≈ 20 px), "Switch to English" (20 px), "Tout voir", "Fermer". Les boutons principaux sont corrects. | Mineur | Mobile, clics ratés |
| UX-10 | Probatoire C | Le bouton "Quiz" du thème n°1 de Physique mène à /quiz générique ; la liste d'essais gratuits n'a pas de Physique (Anglais, Chimie, Français, Info, Littérature, Maths, Philosophie). | Mineur | Conversion, rétention |
| UX-11 | Probatoire C | /cm/themes-frequents/11947/exercices ouvert sans ?subject=&cursus= affiche "Aucun exercice trouvé..." alors que 21 exercices existent. | Mineur | Rétention (lien partagé) |
| UX-13 | GCE | /en/pricing : la liste des cursus commence par BEPC/Probatoire/BAC, GCE O/A Level à la fin. | Mineur | Conversion GCE |
| UX-14 | GCE | /en/login : bouton "Continuer avec Google" en français (hypothèse : langue du navigateur). | Mineur | Cohérence |
| SEO-05 | SEO | Aucune donnée structurée (0 JSON-LD). Utiles : Organization, BreadcrumbList, LearningResource ; pas de fil d'Ariane. | Mineur | Acquisition |
| SEO-06 | SEO | Accueil, listes, tarifs, thèmes, quiz, À propos : aucun texte dans l'HTML initial ; titles JS génériques ("Prix", "Épreuves et corrigés", "Quiz" suivis de "\| EduKora") ; og:url = https://edukora.africa/ partout. | Mineur | Acquisition, partage |
| SEO-07 | SEO erreurs | Routes inconnues en HTTP 200 (noindex posé en JS) ; /CM, /cm/, /cm/epreuves/ répondent 200 avec le même HTML. Pour un moteur, épreuve ou cours inconnu = 404 réel (bien). Absorbe l'ancien UX-17. | Mineur | Indexation |
| SEO-08 | SEO sitemap, maillage | /cm/themes-frequents, /quiz, /a-propos, /qui-etudie absents du sitemap ; /quiz en noindex ; slugs de cours très longs et sans pays ; HTML bot d'une épreuve : 2 liens internes contre 31 dans la page rendue. | Mineur | Acquisition |
| SEO-09 | Performance | gzip sans brotli à l'origine (433 → 140 Ko) ; /media en cache 1 h ; API publiques en no-cache ; 20 polices KaTeX en font-display:block. Hypothèse : Cloudflare corrige en prod. | Mineur | Performance 3G |
| UX-12 | Probatoire C | "Encore 48 thèmes classés" identique pour Maths, Physique, Chimie (API : nb_themes_verrouilles = 48) : probablement un plafond à 50. | Cosmétique | Confiance |
| UX-07 | Accessibilité | Texte de la mascotte du résultat du quiz présent deux fois dans le texte de la page (probable doublon pour lecteur d'écran). | Cosmétique | Faible |
| UX-09 | Élève | Message "C'est correct, frère." après 2/5 : ton à valider (élève fille, parent). | Cosmétique | Faible |
| UX-15 | GCE | Thèmes de quiz sans majuscules : "Economic development of cameroon". | Cosmétique | Faible |
| UX-16 | GCE | Épreuve GCE affichée "19 exercises" / "Exercise 1" pour des questions de section A. | Cosmétique | Faible |

## D. Fonctionnalités manquantes attendues (hypothèses à valider, pas des constats)
- F1 : un échantillon de la séance du jour pour un visiteur (une séance gratuite). Raison : les 4 personas ne dépassent pas 5/10 pour payer car la valeur centrale (séance + mémoire) reste une promesse.
- F2 : suivi de l'état d'un paiement avec notification (SMS/WhatsApp) et délai affiché ; paiement Mobile Money intégré si CamPay est actif en production (CAMPAY_ACTIVE=False en local).
- F3 : un résumé ou un message pour le parent après le quiz d'essai ("voici ce que ton enfant a fait"), prolongeant "Montrer à mes parents".
- F4 : pages éditoriales pour parents ("comment réviser le BEPC") pour l'acquisition (SEO).
- F5 : mémoire de l'examen choisi par appareil : sur ordinateur partagé, un autre élève retrouve le choix (observé : Probatoire C resté jusqu'à la visite GCE).

## E. Ce qui marche bien (à ne pas casser)
Accueil lisible en 10 s ; tarifs transparents avant connexion avec barre d'achat fixe ; paywall honnête et "Montrer à mes parents" ; corrigés libres complets, lecture sans réseau, PDF avec quota affiché ; quiz sans compte avec retour pédagogique et résultat clair ; recherche tolérante aux accents ; thèmes qui tombent avec top 2 gratuit ; cours en onglets ; interface anglaise complète, 404 traduite ; poids initial raisonnable (≈ 310 Ko) et cache long des assets ; prérendu bots, OG/Twitter soignés, sitemaps bilingues, robots.txt réfléchi, noindex sur pages privées.

---
## F. Complément : parcours connecté (voir 06-parcours-connecte.md)
Comptes [TEST] élève abonné et parent, mobile, local, jusqu'à l'écran de paiement (aucune déclaration de paiement).
| ID | Constat | Sévérité | Statut |
|----|---------|----------|--------|
| UX-18 | **Retiré : artefact de mesure** (compteur animé figé à 0 dans un navigateur en arrière-plan, voir 06). Reste une hypothèse mineure : "Partiel" compte 0 dans "0 / 7" et figure parmi les questions "ratées" | Cosmétique | Hypothèse |
| UX-19 | Envoi du code par e-mail synchrone (~12 s au premier envoi en local, échec au second) ; capacité du SMTP et plafonds OTP à confirmer en production (60 e-mails par IP et par heure) | Majeur (hypothèse, non vérifiable en local) | À vérifier en prod |
| UX-20 | /tarifs → Continuer paie pour le profil actif (Test) alors que l'enfant à abonner est Cadet ; pas de sélecteur d'enfant ; "Payer pour Cadet" (Mes accès) est correct | Mineur | Fait |
| UX-21 | "Le paiement automatique est momentanément indisponible" à l'écran de paiement (CAMPAY_ACTIVE faux en local) | À vérifier en prod | À vérifier en prod |
| UX-22 | Anneau de progression "0 %" (5 sur 1 122 savoirs) démotivant au début | Cosmétique | Hypothèse |
Mise à jour de UX-04 : si CamPay est actif en production, l'attente de 3 h ne concerne que le repli manuel.
Satisfaction connectée : élève abonné Q1 4/5, parent Q1 4/5 (3/5 en visiteur), payer 6/10 (5/10 en visiteur).

## G. Statut après correctifs (voir 07-correctifs-appliques.md)
| ID | Statut au 2026-11-12 |
|----|----------------------|
| UX-01 (CLS) | **Corrigé en local** (pied de page stable) : /tarifs 0, /cm ≈ 0,10, épreuve : seul reste le bandeau "Choisis ton examen" ; non déployé |
| SEO-03 (descriptions) | **Corrigé en local** (libre / payant, niveau d'examen, Cameroun) ; non déployé ; titles inchangés |
| SEO-01 (corrigé libre dans le HTML moteurs) | **Corrigé en local** pour les épreuves vitrine, canonical sur le lecteur ; non déployé |
| UX-06 (choix perdu à la connexion) | **Corrigé en local** ("Ton choix : BEPC · 3 mois · 6 000 FCFA", phrase redondante supprimée) ; non déployé |
| SEO-02, SEO-04, SEO-10, UX-04, UX-19, UX-21 | **Ouverts** (décisions ou vérifications en production) |
Mises à jour (lot 2) : UX-01 CLS accueil 0,001, tarifs 0, épreuve 0,024 (corrigé, non déployé) ; UX-20 corrigé en local (sélecteur d'enfant, tests) ; UX-18 retiré (artefact de mesure).
Mise à jour (lot 3) : **SEO-02 corrigé en local** (13 pages d'examen indexables, au sitemap, prérendues, liées depuis le pied de page et les fiches d'épreuve) ; non déployé.
