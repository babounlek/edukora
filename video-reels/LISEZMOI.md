# Vidéos verticales EduKora : comment les régénérer

Même principe que `video-facebook/` : une animation HTML (`outils/rendu/reels.html`) photographiée image par image avec Chromium, puis encodée avec ffmpeg. La voix vient d'edge-tts (accès internet nécessaire).

Rien ici ne modifie le code ni la base d'EduKora. Les captures sont des lectures du site public. Attention : le parcours du quiz sans compte (capture A) crée, côté EduKora, une session d'invité réelle, comme tout visiteur.

## Contenu

| Élément | Rôle |
|---|---|
| `A-…mp4`, `B-…mp4`, `E-…mp4` | Vidéos finales 1080x1920, 30 i/s, H.264 + AAC |
| `previsualisations/` | 4 images de prévisualisation par vidéo |
| `script-et-storyboard.md` | Voix off, textes à l'écran, durées, source de chaque affirmation |
| `legendes.txt` | Légendes (principale et variante) pour chaque vidéo |
| `specs/A.json`, `B.json`, `E.json` | Une spécification par vidéo : voix, vitesse, lien, scènes, textes, cadrages |
| `outils/` | `capture_a.py`, `capture_b.py`, `capture_e.py` (captures du site), `fabrique.py` (voix + montage), `planche_v.py` (planche-contact) |
| `sources/captures/` | Captures brutes (PNG, échelle 3) et positions des blocs surlignés |
| `sources/A`, `B`, `E` | Voix par scène (.mp3), minutage, sous-titres (.srt), voix assemblée (.mp3 et .wav) |

L'environnement Python est celui de `video-facebook/.venv` (déjà installé). Toutes les commandes se lancent depuis `D:\edukora\video-reels`.

## Changer un texte ou le lien

1. Ouvrir la spécification (`specs/A.json` par exemple).
   - `voix` d'une scène : texte lu et sous-titré.
   - `legende` d'un beat : texte affiché au-dessus de la capture.
   - `lien` : lien affiché dans la dernière scène.
   - `voix` (en haut) et `vitesse` : voix edge-tts et débit (`"-4%"`, `"+5%"`).
2. Regénérer :
   ```powershell
   ..\video-facebook\.venv\Scripts\python.exe outils\fabrique.py specs\A.json
   ```
   Les durées se recalculent sur la voix. La voix n'est refaite que si son texte, la voix ou la vitesse ont changé (`--refaire-voix` pour forcer).
3. Pour regarder quelques images avant le rendu complet :
   ```powershell
   ..\video-facebook\.venv\Scripts\python.exe outils\fabrique.py specs\A.json --images 3 9.5 20
   ```
   Les aperçus arrivent dans `sources\A\apercus\`.

Règles pour les textes de voix : écrire les nombres en chiffres collés (`2000`, `6000`) et les remplacer à l'affichage via `remplacements` (par exemple `"2000": "2 000"` avec une espace insécable). Les scènes se calent sur des mots de la voix (`cue`) : les conserver dans la phrase.

## Refaire les captures

```powershell
..\video-facebook\.venv\Scripts\python.exe outils\capture_a.py
..\video-facebook\.venv\Scripts\python.exe outils\capture_b.py
..\video-facebook\.venv\Scripts\python.exe outils\capture_e.py
```

- `capture_a.py` rejoue le parcours du quiz sans compte jusqu'à obtenir une bonne réponse (jusqu'à 6 essais). Le thème et la question sont tirés par le site : refaire la capture change l'image, parfois le texte. Les cadrages de `specs/A.json` sont mesurés pour la mise en page actuelle ; vérifier avec `--images`.
- `capture_b.py` : changer `SLUG` et `EXO` pour un autre corrigé (nouvel épisode), puis refaire les cadrages `@clé` dans `specs/B.json` à partir de `sources/captures/b-exercice.json`.
- `capture_e.py` : page des tarifs et bloc « Tu es parent ? ». La date « Accès jusqu'au… » est masquée automatiquement.

## Ajouter une vidéo

Copier une spécification, changer `id`, `sortie` et les scènes. Types de scène : `hook` (texte qui s'allume avec la voix), `shot` (capture avec caméra et surlignage), `cta` (logo, bouton, lien).

## Musique et voix

- Pas de musique (non écoutable ici, et la plupart des vidéos sont vues sans son).
- La voix est une voix de synthèse fr-FR. Il n'existe pas de voix camerounaise chez edge-tts. Pour utiliser une vraie voix, remplacer les fichiers `sources/<id>/voix/sN.mp3` et relancer ; le minutage mot à mot est à refaire (transcription locale), non automatisé aujourd'hui.

## Points à revérifier avant chaque publication

- Le prix, la durée d'activation et le code parent (vidéo E) correspondent-ils toujours au site ?
- Le thème et le chiffre « tombé dans 26 épreuves sur 28 » (vidéo A) sont ceux d'un jour donné.
- Le corrigé de la vidéo B est-il toujours « en accès libre » ?

## Versionnement (git)

Les fichiers produits (vidéos, voix, captures, aperçus, `.venv`) sont exclus de git (voir `.gitignore`). Après un clonage, recréer l'environnement Python puis refaire les captures et la voix (`outils/capture*.py`, puis `outils/generer.py` ou `outils/fabrique.py`) avant de générer la vidéo.
