# Vidéo Facebook EduKora : comment la régénérer

La vidéo est produite par un petit atelier local, sans service externe pour le montage : une animation HTML (`outils/rendu/index.html`) est photographiée image par image avec Chromium, puis encodée avec ffmpeg. La voix vient d'edge-tts (voix de synthèse Microsoft, accès internet nécessaire pour la générer).

Rien ici ne modifie le code ni la base d'EduKora : les captures sont des lectures du site public.

## Contenu du dossier

| Élément | Rôle |
|---|---|
| `edukora-facebook-1x1.mp4` | Vidéo finale, 1080x1080, 30 i/s, H.264 + AAC |
| `script-et-storyboard.md` | Voix off, textes à l'écran, durées, justification des affirmations |
| `legende-facebook.txt` | Légende principale + 2 variantes A/B avec hashtags |
| `config.json` | Voix, vitesse, lien, textes de la voix off par scène |
| `outils/` | Scripts : `tts.py`, `capture.py`, `timeline.py`, `rendu.py`, `generer.py`, `planche.py` |
| `sources/captures/` | Captures brutes du site (PNG) et positions des blocs mis en valeur |
| `sources/voix/` | Voix off par scène (.mp3) et minutage mot à mot (.json) |
| `sources/voix-off.mp3`, `voix-off-mixee.wav` | Voix assemblée et normalisée à -16 LUFS |
| `sources/sous-titres.srt` | Sous-titres (ceux de la vidéo sont incrustés) |
| `sources/polices/`, `logo-vertical-fr.svg`, `icon-dark.svg` | Polices et logo copiés du dépôt (Fraunces, Work Sans) |
| `.venv/` | Environnement Python local (à ne pas committer) |

## Prérequis (déjà installés dans `.venv`)

Python 3.14, puis `playwright` (avec Chromium), `edge-tts`, `pillow`, `numpy`, `imageio-ffmpeg` (fournit ffmpeg). Pour recréer l'environnement :

```powershell
cd D:\edukora\video-facebook
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install playwright edge-tts pillow numpy imageio-ffmpeg
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Changer un texte de la voix off

1. Modifier la phrase de la scène dans `config.json` (clé `voix`).
2. Lancer :
   ```powershell
   .\.venv\Scripts\python.exe outils\generer.py
   ```
   Les durées des scènes se recalculent sur la voix. Le total doit rester entre 40 et 45 s : s'il dépasse, raccourcir une phrase ou baisser le débit (`vitesse`, par exemple `"-4%"` devient `"+2%"`).
3. Si un texte affiché dans l'animation doit changer (titres, puces, cartes), le modifier dans `outils/rendu/index.html`. Les scènes 4, 5 et 6 se calent sur certains mots de la voix (BEPC, BAC, Probatoire, GCE, « L'élève », « parents », « Inscrivez ») : les conserver dans la phrase.
4. Pour changer la voix : `voix` dans `config.json` (`fr-FR-HenriNeural` pour une voix d'homme). Il n'existe pas de voix fr-CM chez edge-tts.

## Changer le lien

1. Modifier `lien_cta` dans `config.json` (affiché en scène 6).
2. Lancer `outils\generer.py`.
3. Penser à changer aussi le lien dans `legende-facebook.txt`.

Le lien de la voix off n'est pas lu : la voix dit seulement « Inscrivez-vous dès maintenant ».

## Refaire les captures

```powershell
.\.venv\Scripts\python.exe outils\generer.py --captures
```

Les captures viennent de `url_site` dans `config.json` (production). Le corrigé choisi (`slug`, `exercice`) est aussi dans ce fichier. Si le site change de mise en page, regarder le résultat avant de publier : les positions des blocs surlignés (scène 3) sont relevées automatiquement dans `sources/captures/exercice.json`, mais les hauteurs de cadrage sont fixées dans `outils/rendu.py` (fonction `beats3`).

## Aperçu rapide d'une image

```powershell
.\.venv\Scripts\python.exe outils\rendu.py --images 6.0 15.0 40.0
```

Les images arrivent dans `sources/apercus/`. `outils\planche.py` les assemble en planche-contact.

## Musique

Aucune musique : la vidéo est pensée pour être regardée sans son et la voix suffit. Pour en ajouter une, la mixer dans `outils/timeline.py` à -22 dB sous la voix, avec une piste libre de droits ou générée localement.

## Points à revérifier avant chaque nouvelle publication

- Le chiffre « Plus de 1 500 épreuves corrigées » (scène 4) : le compteur du site évolue.
- Le corrigé montré est-il toujours « en accès libre » ?
- Les cursus affichés correspondent-ils toujours à la barre « Choisis ton examen » ?
