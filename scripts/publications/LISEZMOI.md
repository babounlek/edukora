# Moteur des publications « Fiches EduKora »

Fabrique les semaines de publications (Facebook, Instagram, statuts WhatsApp) rangées dans
`docs-relecture/publications/` (hors git). La compétence `publications-fiches-edukora` (`.claude/skills/`) dit
comment s'en servir ; ce fichier dit ce que fait chaque script.

| Script | Rôle |
|---|---|
| `reserve.mjs <publications>` | Lit sur le site toutes les fiches gratuites, marque celles qu'une semaine utilise déjà, écrit `reserve.csv` et affiche les semaines encore possibles. |
| `construire.mjs <semaine> [--actualiser \| --verifier]` | Lit `semaine.json`, prend l'instantané des gratuites (`sources/fiches-en-ligne.json`), écrit `sources/pages.html`, le brouillon `legendes.md` s'il manque et les lignes de `planning.csv` si la semaine n'y est pas. `--verifier` compare le site à l'instantané sans rien écrire. |
| `photographier.py <semaine>` | Photographie chaque vue (Playwright), réduit un texte qui déborde, écrit `images/` et `a-montrer-a-l-enseignant.pdf`. |

Sources : l'API publique du site (`/memos/fiches/`, `/memos/matieres/`, `/catalog/cursus/`, `/quiz/essais/`), jamais la
base locale (des fiches y sont gratuites à la main pour la relecture). Rendu : KaTeX, polices et logos de `frontend/`.

Python : `video-facebook/.venv/Scripts/python.exe` (Playwright y est installé).

Vérifié le 27/11/2026 : les quatre semaines pilotes du BEPC (maths, PCT, informatique, éducation civique) regénérées
avec ce moteur donnent les mêmes images au pixel près (à l'anticrénelage du logo près, écart ≤ 10/255 sur 4 images).
