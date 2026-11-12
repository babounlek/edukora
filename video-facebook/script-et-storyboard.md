# EduKora - vidéo Facebook 1080x1080 : script et storyboard

Durée : 43,6 s · 30 i/s · MP4 H.264 + AAC · voix off fr-FR-DeniseNeural (edge-tts, vitesse -4 %) · voix normalisée à -16 LUFS · pas de musique.
Source des captures : https://edukora.africa (production, lecture seule, visiteur anonyme), prises le 12 novembre 2026.
Corrigé montré : « Mathématiques BEPC 2026 », exercice 3 (corrigé en accès libre).

Les durées ci-dessous sont celles du montage final : elles se calent sur la voix (voir `outils/timeline.py`).

| # | Plage | Visuel | Texte à l'écran | Voix off |
|---|---|---|---|---|
| 1 | 0,0 - 4,9 s | Fond vert profond, phrase en grand qui s'allume mot à mot avec la voix, « ? » géant en filigrane, symbole EduKora en haut à gauche | « Il a eu la correction… mais l'a-t-il vraiment comprise ? » (« comprise ? » en ambre) | « Il a eu la correction… mais l'a-t-il vraiment comprise ? » |
| 2 | 4,9 - 11,9 s | Capture réelle de la page du corrigé (fiche « Mathématiques BEPC 2026 », « Corrigé en accès libre »), puis défilement jusqu'aux calculs de l'exercice 1 | Titre « Chaque étape, expliquée. » + sous-titres | « Sur EduKora, chaque corrigé détaille chaque étape. Rien n'est sauté. » |
| 3 | 11,9 - 21,0 s | Capture réelle de l'exercice 3, zoom animé en trois temps avec surlignage ambre : rappel de méthode, développement de (4x-5)(3x+1), vérification de la factorisation | « 1 La méthode est rappelée » · « 2 Chaque calcul est posé » · « 3 Le résultat est vérifié » + sous-titres | « La méthode est rappelée. Chaque calcul est posé, ligne après ligne. Et le résultat est vérifié. » |
| 4 | 21,0 - 28,7 s | Capture réelle de la barre « Choisis ton examen » de l'accueil, puis puces animées au rythme de la voix | Puces BEPC · Probatoire A C D E TI · BAC A C D E TI · GCE O Level, A Level (en anglais) · « Plus de 1 500 épreuves corrigées » | « Du BEPC au Probatoire, puis au BAC. Et le GCE, en version anglaise. » |
| 5 | 28,7 - 36,4 s | Deux cartes avec icônes simples (livre, bouclier) : aucune personne à l'écran | « L'élève : Révise seul, à son rythme » · « Les parents : Chaque réponse est expliquée » | « L'élève révise seul, à son rythme. Et les parents savent que chaque réponse est expliquée. » |
| 6 | 36,4 - 43,6 s | Logo EduKora (baseline « Réussis ton examen »), bouton, lien | « Inscrivez-vous » · `edukora.africa` | « EduKora. Inscrivez-vous dès maintenant. » |

Sous-titres incrustés sur toutes les scènes sauf la 1 (le texte en grand y fait office de sous-titre, synchronisé mot à mot). Le fichier `sources/sous-titres.srt` contient aussi la scène 1.

## Affirmations affichées et leur justification

| Affirmation | Vérification (12 novembre 2026) |
|---|---|
| « Plus de 1 500 épreuves corrigées » | Le site affiche 1 520 (API `/catalog/stats/`, `corriges_disponibles`). |
| BEPC, Probatoire A/C/D/E/TI, BAC A/C/D/E/TI | Barre « Choisis ton examen » de l'accueil et API `/catalog/examens/cm/`. |
| GCE O Level et A Level, en anglais | Cursus `gce-o-level` et `gce-a-level` dans l'API ; le site propose « Preparing the GCE? Switch to English ». |
| Corrigé « en accès libre » (scène 2) | Badge présent sur la page du corrigé ; lecture sans compte. |
| « La méthode est rappelée » / « Le résultat est vérifié » | Chaque question du corrigé montré contient un « Rappel de méthode » ; la factorisation se termine par une ligne « Vérification ». |

Non affiché volontairement : prix, mention de gratuité générale, nombre d'utilisateurs, « toutes les matières », résultats d'examen.

## Légende de la scène 3 : pourquoi cet exercice

Exercice 3 du corrigé « Mathématiques BEPC 2026 » : développer, factoriser, résoudre une équation produit nul. Les formules s'affichent sans erreur (0 erreur KaTeX) et la méthode comme la vérification sont visibles à l'écran. L'exercice 2 du même corrigé n'a pas été retenu : une de ses phrases sur l'arrondi est confuse.
