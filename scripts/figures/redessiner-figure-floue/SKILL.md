---
name: redessiner-figure-floue
description: Redessine FIDÈLEMENT une figure d'épreuve déjà ingérée qui est floue, pixellisée ou illisible (scan basse résolution, JPEG écrasé, texte baveux), quand il n'existe pas de PDF d'origine pour la refaire proprement - c'est le cas de toutes les épreuves francophones (BEPC, Probatoire, BAC). Mesure les formes sur l'original agrandi avec une grille graduée, redessine en haute définition (Pillow, suréchantillonné) en reprenant formes, proportions, positions, étiquettes et texte, compare côte à côte avec l'original, puis applique en local et en PROD (Spaces + dossier media servi par Caddy + purge du cache Cloudflare). À utiliser dès que l'utilisateur dit « cette image est floue », « redessine cette figure », « refais ce schéma proprement », donne l'URL d'une figure /media/figures/..., même sans le mot « redessiner ». Différent de reproduire-figure-sans-filigrane (extrait ou nettoie une figure à partir du PDF) : ici on n'a que l'image floue.
---

# Redessiner fidèlement une figure floue

Objectif : une figure **nette et fidèle** à l'originale. « Fidèle » veut dire : mêmes formes (pas des ellipses à la place de formes irrégulières), mêmes proportions, mêmes positions, mêmes étiquettes et valeurs, même texte. Jamais de contenu ajouté qui donne une réponse (étiquette, valeur, légende absente de l'original), jamais de contenu retiré.

**Règle d'or : mesurer, ne pas dessiner de mémoire.** Un premier jet « à vue » (deux ellipses pour un chromosome) a été refusé par l'utilisateur : « les formes doivent être fidèles ». Le bon réflexe est d'agrandir l'original avec une grille graduée et de relever les coordonnées.

## Quand ne PAS utiliser ce skill
- Le PDF d'origine existe (GCE, ou épreuve avec PDF conservé) : utiliser `reproduire-figure-sans-filigrane` (extraction native, zéro pixel inventé).
- La figure est floue mais lisible et sans filigrane : une retouche n'apporte rien, la laisser.

## Environnement
Python n'est PAS installé sur l'hôte Windows. Tout passe par le conteneur backend (Pillow + polices Liberation présents) :
```
docker compose exec -T backend python - < script.py
```
Les chemins `/tmp/...` dans une commande Git Bash sont réécrits par MSYS : passer par `docker compose exec -T backend sh -c "..."`. Pour envoyer un script dans le conteneur : `cat script.py | docker compose exec -T backend sh -c "cat > /tmp/script.py"`. Copie vers l'hôte : `docker compose cp backend:/tmp/x.png <scratchpad>/x.png`, puis `Read` pour voir l'image.

## Processus

### 1. Identifier la figure
L'URL `/media/figures/<pays>/<nom>.webp` donne le nom de fichier. L'id de Figure s'obtient par `Figure.objects.filter(image__contains="<nom>")`. L'id est le même en local et en prod quand la base prod vient du même ingest, mais **toujours le vérifier en prod** (nom de fichier ET titre de la leçon). Lire l'énoncé de l'exercice : les étiquettes de la figure doivent y correspondre.

### 2. Voir et mesurer l'original
`scripts/agrandir.py` découpe une zone, l'agrandit (x3 ou x4) et trace des **graduations rouges** en coordonnées d'origine :
```
cat scripts/agrandir.py | docker compose exec -T backend sh -c "cat > /tmp/agrandir.py"
docker compose exec -T backend sh -c "FIG=<chemin relatif sous media> ZONE=x0,y0,x1,y1 ECHELLE=4 python /tmp/agrandir.py"
```
Relever pour chaque élément : position (x, y), hauteur, largeur et, pour une forme, sa **demi-largeur à plusieurs hauteurs** (un profil de 8 à 12 repères suffit). Ce que le flou cache mais que l'énoncé impose se déduit de l'énoncé, jamais d'une supposition.

Points d'attention :
- Zoomer par petites zones, un objet à la fois (un chromosome, une cellule de tableau, une flèche).
- Les contours de l'original sont souvent **irréguliers** : un léger défaut de symétrie est une information visuelle à garder (faible amplitude, basse fréquence, jamais un « dentelé »).
- Distinguer plein / contour / pointillé, épaisseur du trait, petit anneau, flèche, indice.

### 3. Dessiner
Partir de `scripts/gabarit_dessin.py` : suréchantillonnage x4, tracé en coordonnées d'origine, helpers ligne / texte / ellipse / bague, `interp` (profil de demi-largeurs) et `bras` (forme définie par profil). Même taille que l'original (largeur et hauteur inchangées : la mise en page de l'exercice en dépend). Polices Liberation Serif/Sans. Fond blanc, noir `#111`, aucun filigrane.

Sortie : `/tmp/fig_nouvelle.png` (référence) et `.webp` qualité 92.

### 4. Comparer, itérer
```
cat scripts/comparer.py | docker compose exec -T backend sh -c "cat > /tmp/comparer.py"
docker compose exec -T backend sh -c "FIG=<chemin> ZONE=x0,y0,x1,y1 python /tmp/comparer.py"
```
`comparer.py` met l'original et le nouveau dessin côte à côte (même zone, agrandie). Regarder les **écarts de forme**, pas seulement de position, et corriger jusqu'à ce que l'œil ne voie plus de différence structurelle (jonctions, proportions bras court/long, coins arrondis ou vifs). Compter 3 à 5 itérations.

### 5. Appliquer en local
Dossier de lot dans le conteneur : `<id>.png` + `rapport.jsonl` (`{"id": <id>, "statut": "redessinee"}`), puis
```
python manage.py appliquer_figures_propres --dossier /tmp/lot_flou --statuts redessinee --ids <id>            # simulation
python manage.py appliquer_figures_propres --dossier /tmp/lot_flou --statuts redessinee --ids <id> --appliquer
```
Le nom du fichier est conservé (les URL sont écrites en dur dans le Markdown) ; l'ancienne image est sauvegardée dans `media/figures_avant_filigrane/<id>_<nom>`. Recharger l'URL locale et contrôler visuellement.

### 6. Appliquer en PROD (seulement sur demande explicite de l'utilisateur)
Voir `scripts/appliquer_prod.sh` (hôte `157.245.140.254`, utilisateur `deploy`, clé dédiée `~/.ssh/edukora_lots_ed25519`, empreinte épinglée dans `~/.ssh/edukora_known_hosts`). **Trois choses à faire, sinon les visiteurs ne voient rien changer :**
1. **Spaces** (stockage Django) : `appliquer_figures_propres` dans le conteneur backend de prod (simulation puis `--appliquer`).
2. **Dossier `/srv/edukora/media/figures/<pays>/`** : **Caddy sert `/media` depuis ce dossier**, pas depuis Spaces (la commande ne le touche pas). Sauvegarder l'ancien fichier dans `media/figures_avant_filigrane/<id>_<nom>`, puis y copier le fichier exact stocké sur Spaces.
3. **Cache Cloudflare** : `/media` est mis en cache (`max-age=14400`, `cf-cache-status: HIT`). Sans purge, l'ancienne image reste servie jusqu'à 4 h. Le skill n'a pas accès au compte Cloudflare : demander à l'utilisateur de purger l'URL (Caching > Purge Cache > Custom Purge). Vérifier avec `curl -sI` ; avec un paramètre `?x=...` on voit déjà la nouvelle image si le serveur est bon.

Vérification finale : télécharger l'URL publique (avec paramètre de contournement) et comparer la taille au fichier stocké, puis `Read` l'image.

## Garde-fous
- Ne jamais dessiner une information absente de l'original ou de l'énoncé (valeur, nom, flèche de sens, légende).
- Ne pas changer les dimensions du fichier.
- Prod : jamais sans demande explicite ; toujours simulation avant `--appliquer` ; toujours vérifier l'id et la leçon en prod ; ne pas supprimer les sauvegardes `figures_avant_filigrane`.
- Annoncer honnêtement l'écart restant (forme approchée) et le cache Cloudflare tant qu'il n'est pas purgé.
- Rendre compte : id de Figure, fichier, ce qui a été relevé, ce qui reste approché.

## Exemple de référence
`exemples/chromosomes_probatoire_a_svt_2024.py` : tableau de caryotypes (Figure 2189, Probatoire A SVT 2024, exercice 2). Profils mesurés de chromosomes X (contour : bras court en écusson, anneau, bras long en gélule) et Y (plein : masse arrondie, anneau ouvert, corps à pans coupés), tableau à 4 lignes, légende. Montre `interp`/`bras`, le positionnement par repères gradués et l'enchaînement comparer/itérer.
