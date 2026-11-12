# 00 - Synthèse : edukora est-il prêt pour le 1er décembre 2026 ?
Audit du 2026-11-12 (J-19), version locale, lecture seule, personas jouées en visiteur seul. Simulation, pas un test utilisateur : confiance **moyenne** sur l'expérience visiteur, **faible** sur tout ce qui touche au parcours connecté et au paiement (non exécutés).

## Verdict : PRÊT SOUS CONDITIONS
Aucun constat Bloquant confirmé. L'expérience visiteur est solide : promesse comprise en 10 s, prix transparents, corrigés libres complets, quiz sans compte, recherche et interface anglaise de bonne qualité. Trois conditions avant le 1er décembre :
1. **Vérifier la production** (SEO-10) : un `noindex` oublié dans `ROBOTS_TAG`, des sitemaps en `localhost` ou l'absence de redirection https rendraient le lancement invisible. Une demi-journée, à faire d'abord.
2. **Corriger ce qui dégrade l'acquisition à bas coût** : saut de mise en page (UX-01), descriptions fausses des corrigés libres (SEO-03), doublon GCE (SEO-04), plus un arbitrage sur le corrigé libre absent du HTML bot (SEO-01).
3. **Rejouer en recette le parcours non couvert** (connexion par code, séance du jour, déclaration de paiement, activation) avec les comptes [TEST], sans paiement réel : cet audit ne l'a pas vu.

Scores de satisfaction simulés (visiteur seul, 4 personas) : revenir 6,75/10 - recommander 6,25/10 - payer **5,0/10**. Le plafond à 5 pour payer vient du même manque chez tous : la séance du jour, valeur centrale, n'est pas démontrable à un visiteur. Confiance faible.

## Mise à jour du soir (2026-11-12) : parcours connecté et correctifs
- **Parcours connecté audité** (élève abonné et parent, jusqu'à l'écran de paiement, sans déclaration de paiement) : voir 06-parcours-connecte.md. Il confirme la valeur de la séance du jour (satisfaction élève 4/5, parent 4/5 contre 3/5 en visiteur, intention de payer 6/10 contre 5/10) et ajoute un risque à vérifier en production : **l'envoi du code par e-mail** (UX-19) et l'état de **CamPay** (UX-21).
- **Correctifs appliqués en local, non committés, non déployés** : R2 (CLS), R3 (descriptions des épreuves), R5 (corrigé libre dans le HTML des moteurs, décision du user) et R8 (rappel du choix à la connexion) : voir 07-correctifs-appliques.md. Restent ouverts : R1 (production), R4 et R6 (décisions), R9 (permanence).
- Verdict inchangé : **prêt sous conditions**.

## Top 10 des risques
| # | Risque | Réf. | Gravité | Nature |
|---|--------|------|---------|--------|
| 1 | Parcours connecté et paiement non audités ici (code OTP, séance, déclaration, activation) | périmètre | Inconnue (à lever) | Non couvert |
| 2 | Configuration de production : noindex oublié, sitemaps en localhost, redirections, brotli | SEO-10 | Potentiellement Bloquant | À vérifier |
| 3 | Corrigés libres absents du HTML envoyé à Google : le meilleur appât d'acquisition n'est pas lisible par les moteurs | SEO-01 | Majeur | Prouvé |
| 4 | Aucune page indexable par cursus ni par matière ("annales BEPC Cameroun" sans page d'atterrissage) | SEO-02 | Majeur | Prouvé |
| 5 | Meta description fausse pour les corrigés libres ("corrigé par abonnement"), sans niveau ni pays | SEO-03 | Majeur | Prouvé |
| 6 | 861 épreuves GCE en double (URL FR et EN), hreflang et x-default ambigus | SEO-04 | Majeur | Prouvé |
| 7 | CLS de 0,6 à 0,95 (le pied de page saute) sur accueil, épreuve, tarifs | UX-01 | Majeur | Prouvé |
| 8 | Activation manuelle sous ≈ 3 h, hors application, au pic de charge du lancement | UX-04 | Majeur (hypothèse) | Non vérifiable |
| 9 | Parent mal servi : accueil écrit pour l'élève, connexion exigée avant de voir où payer, e-mail par défaut | UX-03, 05, 06 | Mineur cumulé, impact conversion fort | Prouvé |
| 10 | Valeur de la séance non démontrée aux visiteurs ; quiz sans Physique pour un visiteur Probatoire C | F1, UX-10 | Mineur, impact conversion | Hypothèse |

## Chiffres clés
- 0 Bloquant, 5 Majeurs prouvés, 1 Majeur non vérifiable, 1 point de production à vérifier, 15 Mineurs, 5 Cosmétiques (voir 01-constats.md).
- Poids initial de l'accueil ≈ 310 Ko compressés ; sitemap de 17 247 URLs ; interface anglaise sans mot français repéré (sauf le bouton Google).
- LCP et INP non mesurés ; 3G non bridée (estimation par le poids : 4 à 7 s avant contenu utile).

## Fichiers
01-constats.md - 02-feuille-de-route.md - 03-satisfaction.md - 04-hors-perimetre.md - 05-seo.md - _brief.md - captures/
