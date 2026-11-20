# Vidéos verticales EduKora (9:16, 1080x1920) : scripts et storyboards

Trois vidéos pour Facebook Reels, WhatsApp Statut, Instagram Reels et TikTok. Voix off de synthèse fr-FR-DeniseNeural (edge-tts), voix normalisée à -16 LUFS, sous-titres incrustés, pas de musique. Les textes et sous-titres restent dans la zone sûre des applications (sous-titres à 430 px du bord bas, marges de 80 et 120 px).

Toutes les images de l'application sont des captures réelles du site de production https://edukora.africa prises le 16 novembre 2026, en visiteur anonyme. Aucune donnée personnelle, aucune personne à l'écran.

| Vidéo | Fichier | Durée |
|---|---|---|
| A. Ta première séance | `A-premiere-seance-9x16.mp4` | 39,3 s |
| B. Un exercice, expliqué (épisode 1) | `B-un-exercice-explique-ep1-9x16.mp4` | 36,0 s |
| E. Parents : prix et paiement | `E-parents-prix-paiement-9x16.mp4` | 45,1 s |

## A. « Ta première séance »

Parcours réellement rejoué sur le site : choix de l'examen (BEPC), thème proposé, quiz sans compte, bonne réponse, correction.

| Scène | Visuel | Voix off | Texte à l'écran |
|---|---|---|---|
| 1 Accroche | Texte qui s'allume mot à mot sur fond vert | « Tu prépares un examen ? Essaie une séance, sans compte. » | idem (le texte est le sous-titre) |
| 2 | Capture de l'accueil, carte « Ta première séance » | « Tu choisis ton examen. » | « Tu choisis ton examen » |
| 3 | Capture du thème proposé (« Identité remarquable », Mathématiques, 5 questions), badge surligné | « On te montre un thème qui tombe souvent. Ici : tombé dans 26 épreuves sur 28. » | « Un thème qui tombe souvent » |
| 4 | Capture de la première question du quiz | « Tu l'essaies tout de suite : cinq questions, sans compte. » | « 5 questions, sans compte » |
| 5 | Capture de la bonne réponse, « Excellent ! +10 points » surligné | « Tu vois tout de suite si tu as juste. » | « La réponse, tout de suite » |
| 6 | Capture de « Comprendre la correction » : rappel de méthode, puis corrigé | « Chaque réponse vient avec sa correction : la méthode, puis le calcul. » | « La méthode est rappelée » puis « Puis le calcul » |
| 7 Appel à l'action | Logo, bouton, lien | « Chaque jour, une séance de 25 minutes. Essaie la tienne sur edukora.africa. » | « Gratuit pour essayer » · « Commencer, sans compte » · `edukora.africa` |

## B. « Un exercice, expliqué » (épisode 1)

Corrigé en accès libre : Mathématiques BEPC 2026, exercice 4, question 1 (côtés d'un triangle rectangle).

| Scène | Visuel | Voix off | Texte à l'écran |
|---|---|---|---|
| 1 Accroche | Texte mot à mot | « Un exercice de BEPC. Saurais-tu le refaire seul ? » | idem |
| 2 | Capture de l'énoncé puis de la figure | « Un triangle rectangle, un angle de 30 degrés. On cherche deux longueurs. » | « Un triangle rectangle » · « On cherche AB et BC » |
| 3 | Rappel de méthode surligné | « Sur EduKora, la méthode est rappelée d'abord. » | « 1 La méthode est rappelée » |
| 4 | Calculs de AB et de BC surlignés | « Puis chaque calcul est posé, ligne par ligne, jusqu'au résultat. » | « 2 Chaque calcul est posé » |
| 5 | Encadré « Piège à éviter » surligné | « Et le piège à éviter est signalé : ne pas confondre adjacent et opposé. » | « 3 Le piège est signalé » |
| 6 Appel à l'action | Logo, bouton, lien | « Épisode 1. Le corrigé complet est en accès libre sur EduKora. » | « Épisode 1 · Maths BEPC » · « Lire le corrigé complet » · `edukora.africa` |

Pour les épisodes suivants, changer le corrigé dans `outils/capture_b.py` (`SLUG`, `EXO`) et les cadrages dans `specs/B.json`.

## E. « Parents : prix et paiement »

Captures de la page des tarifs (BEPC choisi, 3 mois par défaut) et du bloc « Tu es parent ? » de l'accueil.

| Scène | Visuel | Voix off | Texte à l'écran |
|---|---|---|---|
| 1 Accroche | Texte mot à mot | « Parents : combien ça coûte, et comment on paie ? » | idem |
| 2 | Bloc « Un prix simple » puis pastille « Aucun prélèvement automatique » surlignée | « 2 000 francs CFA par mois. Paiement par Mobile Money, sans prélèvement automatique. » | « Un prix simple » · « Sans prélèvement automatique » |
| 3 | Choix du nombre de mois, puis récapitulatif (3 mois = 6 000 FCFA) surligné | « Par enfant, vous choisissez le nombre de mois : de 1 mois jusqu'à l'examen. Trois mois, par exemple : 6 000 francs CFA. » | « Tu choisis le nombre de mois » · « Le total est affiché avant de payer » |
| 4 | Les 3 étapes « Comment ça se passe » | « Vous payez en une fois, par Orange Money ou MTN MoMo. Notre équipe vérifie le transfert, généralement sous 3 heures, puis l'accès s'active. » | « Paiement par Mobile Money » · « Accès activé après vérification » |
| 5 | Carte « Tu gardes la main » (code parent) | « Un code parent garde la main sur les paiements. Et vous pouvez essayer gratuitement avant de payer. » | « Le parent garde la main » |
| 6 Appel à l'action | Logo, bouton, lien | « EduKora. Essayez une première séance sur edukora.africa. » | « Gratuit pour essayer » · « Commencer, sans compte » · `edukora.africa` |

## Affirmations et leur source (16 novembre 2026)

| Affirmation | Source sur le site |
|---|---|
| Séance quotidienne de 25 minutes, thème qui tombe souvent | Accueil : « 25 minutes par jour sur un thème qui tombe vraiment à ton examen » |
| Quiz sans compte, 5 questions, « tombé dans 26 épreuves sur 28 » | Parcours rejoué le 16 novembre ; le thème et le chiffre sont ceux affichés ce jour-là et peuvent varier |
| « Gratuit pour essayer » | Accueil : « Gratuit pour essayer. Ensuite 2 000 FCFA par mois » |
| 2 000 FCFA par mois, par enfant, de 1 mois jusqu'à l'examen | Page des tarifs et API des plans (7 mois maximum pour le BEPC) |
| 3 mois = 6 000 FCFA | Récapitulatif de la page des tarifs, BEPC, 3 mois par défaut |
| Orange Money ou MTN MoMo, en une fois, sans prélèvement automatique | Accueil et page des tarifs |
| Activation généralement sous 3 heures après vérification | Page des tarifs, « Comment ça se passe » |
| Code parent pour les paiements | Accueil, bloc « Tu es parent ? » |
| Corrigé « en accès libre » | Badge de la page du corrigé |

Non affiché volontairement : date d'accès calculée par la page des tarifs et compte à rebours « J-… » (masqués dans les captures), numéro WhatsApp du support, promesses de résultats, comparaison chiffrée avec d'autres services.
