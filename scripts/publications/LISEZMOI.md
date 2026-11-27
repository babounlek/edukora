# Moteur des publications « Fiches EduKora »

Fabrique les semaines de publications (Facebook, Instagram, statuts WhatsApp) rangées dans
`docs-relecture/publications/` (hors git). La compétence `publications-fiches-edukora` (`.claude/skills/`) dit
comment s'en servir ; ce fichier dit ce que fait chaque script.

| Script | Rôle |
|---|---|
| `reserve.mjs <publications>` | Lit sur le site toutes les fiches gratuites, marque celles qu'une semaine utilise déjà, écrit `reserve.csv` et affiche les semaines encore possibles. |
| `construire.mjs <semaine> [--actualiser \| --verifier]` | Lit `semaine.json`, prend l'instantané des gratuites (`sources/fiches-en-ligne.json`), écrit `sources/pages.html` et `sources/videos.html`, le brouillon `legendes.md` s'il manque, `legendes-tiktok.md` une fois `legendes.md` écrit, et les lignes qui manquent à `planning.csv`. `--verifier` compare le site à l'instantané et contrôle légendes et vidéos, sans rien écrire. |
| `photographier.py <semaine>` | Photographie chaque vue (Playwright), réduit un texte qui déborde, écrit `images/` et `a-montrer-a-l-enseignant.pdf`. |
| `filmer.py <semaine> [vidéos]` | Filme `sources/videos.html` à 30 images par seconde (une image immobile n'est photographiée qu'une fois), encode en MP4 avec ffmpeg (imageio-ffmpeg) dans `videos/`, avec une couverture `.jpg` et une planche de contrôle dans `sources/`. |

Langue : `"langue": "en"` dans `semaine.json` (GCE) met en anglais tous les textes fixes des images, des vidéos et des
lignes publiées des légendes (table `T` pour les vues, `C` pour les légendes, dans `construire.mjs`).

Sources : l'API publique du site (`/memos/fiches/`, `/memos/matieres/`, `/catalog/cursus/`, `/quiz/essais/`), jamais la
base locale (des fiches y sont gratuites à la main pour la relecture), sauf `"source": "http://localhost"` pour des fiches
encore en brouillon (semaines GCE préparées avant leur mise en ligne). Rendu : KaTeX, polices et logos de `frontend/`.

Mise en page : une formule en ligne et le mot qui la précède devant un « = » ou l'unité qui la suit forment un bloc
insécable ; un mot à trait d'union ne se coupe pas ; une formule en ligne de plus de 40 caractères peut se couper ; une
page du défi trop chargée est remplacée par deux (`-a`, `-b`). Le contrôle de débordement mesure le texte visible contre
son encadré (réponse, piège), pas seulement contre la zone.

Python : `video-facebook/.venv/Scripts/python.exe` (Playwright y est installé).

Vérifié le 27/11/2026 : les quatre semaines pilotes du BEPC (maths, PCT, informatique, éducation civique) regénérées
avec ce moteur donnent les mêmes images au pixel près (à l'anticrénelage du logo près, écart ≤ 10/255 sur 4 images).
