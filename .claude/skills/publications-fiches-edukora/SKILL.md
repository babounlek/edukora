---
name: publications-fiches-edukora
description: Prépare une semaine de publications pour les réseaux sociaux d'EduKora (Facebook, Instagram, statuts WhatsApp) à partir des Fiches EduKora GRATUITES du site, pour n'importe quel examen (BEPC, Probatoire, BAC) et n'importe quelle matière. Choisit la prochaine semaine dans la réserve des gratuites, produit les images 4:5 et 9:16, les légendes, le PDF pour l'enseignant et les lignes du planning dans docs-relecture/publications/semaines/. Ne publie jamais rien. À utiliser dès que l'utilisateur parle de contenu pour ses pages ou ses plateformes, de posts, de carrousels, de statuts, de « la semaine suivante », de « prépare la semaine des maths du Probatoire », du planning ou du calendrier de publication, de la réserve de fiches gratuites, même sans dire « réseaux sociaux » ni « semaine ». Aussi pour regénérer une semaine après une correction de l'enseignant, ou pour vérifier une semaine juste avant de la publier.
---

# Publications des Fiches EduKora

Une semaine de publications = une matière d'un examen, 5 fiches gratuites, 7 jours. Le format a été éprouvé sur les
quatre premières semaines du BEPC (maths, PCT, informatique, éducation civique) ; le moteur commun les refait au pixel
près. Ton travail : choisir la semaine, lancer le moteur, regarder les images, écrire les légendes et les points pour
l'enseignant. Le moteur s'occupe de tout ce qui doit être exact (textes des fiches, années, liens, dates).

**Rien ne se publie depuis cette compétence.** Le site ne montre une fiche qu'après la case « relu par un enseignant »,
et les images reprennent les fiches telles quelles : une erreur dans une image partagée ne se corrige plus. Chaque
semaine part donc avec le statut « À relire » et un PDF pour l'enseignant de la matière.

## Où sont les choses

- `docs-relecture/publications/` (hors git) : `LISEZMOI.md` pour l'utilisateur, `planning.csv` (toutes les
  publications et leur statut), `reserve.csv` (les fiches gratuites en ligne et la semaine de chacune), `semaines/`.
- `docs-relecture/publications/semaines/AAAA-MM-JJ_examen_matiere/` : une semaine. Date = son lundi. Exemples :
  `2026-12-28_probatoire-d_maths`, `2027-01-11_probatoire-cde_chimie`, `2027-02-08_probatoire_education-civique`.
- `scripts/publications/` (dans git) : le moteur. `construire.mjs`, `photographier.py`, `reserve.mjs`.
- Les anciens dossiers `pilote-*` sont l'avant-migration : ne pas s'en servir comme source, ne pas y écrire.

Commandes, depuis `D:\edukora` (Python : celui de `video-facebook`, il a Playwright) :

```
node scripts/publications/reserve.mjs docs-relecture/publications
node scripts/publications/construire.mjs docs-relecture/publications/semaines/<semaine>          [--actualiser | --verifier]
video-facebook/.venv/Scripts/python.exe scripts/publications/photographier.py docs-relecture/publications/semaines/<semaine>
```

Sous Git Bash, préfixer Python de `PYTHONUTF8=1` (sinon les accents de la sortie font planter l'affichage).

## Les règles de la série

Elles ont été décidées avec l'utilisateur ; le moteur applique celles qui touchent aux images.

- « Fiches EduKora » sur chaque image et en tête de chaque légende ; numéros de 1 à 5 dans la semaine (ce n'est pas
  un numéro du site).
- **Jamais de total de fiches** dans une invitation (« 33 fiches »…) : il change. On dit « certaines gratuites, les
  autres avec l'abonnement ».
- Seules les sessions **officielles** sont annoncées : un examen blanc n'est pas le BEPC.
- Uniquement des fiches **gratuites en ligne**, lues sur le site au moment de construire. Les publier, c'est donner ce
  que le site donne déjà ; une fiche payante sur Facebook serait un cadeau que l'abonné paie. Publier une partie d'une
  fiche payante est une décision de l'utilisateur, pas la tienne.
- Le soir, la réponse va en commentaire sur Facebook, en story sur Instagram, en statut sur WhatsApp.

## Le GCE (anglophone)

Le planning couvre aussi le GCE O Level et A Level (cursus 1414 et 1416). Une semaine GCE s'adresse à des élèves
anglophones : images et légendes **entièrement en anglais** (le site dit « EduKora sheets » pour les fiches), hashtags
`#GCE #OLevel` ou `#ALevel`, liens vers les pages anglaises du site.

Au 27/11/2026, le GCE n'a **aucune fiche** (ni en ligne ni en base locale) ; il a 31 quiz gratuits sans compte
(`reserve.mjs` les compte). Le moteur ne sait faire que des semaines de fiches, en français. Tant que l'utilisateur
n'a pas tranché la forme d'une semaine GCE (fiches GCE à écrire d'abord, ou semaine tirée des quiz gratuits), ne
fabrique rien pour le GCE : ne traduis pas une fiche francophone (les programmes diffèrent) et n'invente pas de
contenu. Dis où en est la réserve GCE et demande. La décision, une fois prise, va dans le `LISEZMOI.md` des
publications.

## Déroulé pour une nouvelle semaine

### 1. Faire le point

Lance `reserve.mjs` : il réécrit `reserve.csv` et affiche les groupes examen × matière qui ont encore 5 gratuites
libres, les doublons de notion entre examens et les semaines déjà préparées. Lis aussi la fin de `planning.csv`.

Si l'utilisateur a nommé la semaine (« les maths du Probatoire D »), fais celle-là. Sinon propose la suivante en suivant
l'ordre du `LISEZMOI.md` des publications s'il en donne un, à défaut ces repères :
- le lundi qui suit la dernière semaine préparée ;
- alterner une semaine BEPC et une semaine lycée, pour que chaque public ait quelque chose au moins une semaine sur deux ;
  le GCE prend sa place dans ce tour dès qu'une forme de semaine GCE est décidée (voir plus haut) ;
- les langues vivantes 2 (allemand, espagnol) en dernier : seuls les élèves qui les ont prises sont concernés ;
- un groupe de moins de 5 gratuites (le dessin du BEPC, 3) ne fait pas une semaine sans l'accord de l'utilisateur ;
- regarde le calendrier de la semaine : Noël, Nouvel An, Fête de la Jeunesse (11 février), Fête nationale (20 mai).
  Une semaine d'éducation civique sur la paix et le vivre-ensemble tombe bien avec le 11 février ; un 25 décembre
  mérite une ligne dans le LISEZMOI de la semaine.

### 2. Créer la semaine et choisir les fiches

Crée le dossier et un `semaine.json` avec `"fiches": []` (champs : `references/semaine-json.md`, à lire). Lance
`construire.mjs` : il prend l'instantané du site (`sources/fiches-en-ligne.json`) et liste les gratuites, avec leurs
sessions officielles et le format qui leur convient. Lis les textes complets dans l'instantané.

Garde 5 fiches et **ordonne-les pour raconter une progression** : du simple au plus dur, une notion qui en utilise une
autre vient après elle (la médiane après le polygone des effectifs cumulés, l'asymptote avant le tableau de variation qui
en demande les limites), les notions voisines ensemble (les trois mots de l'élection), du matériel vers l'algorithmique.
L'élève qui suit la semaine doit sentir un fil. Pour chaque fiche : une `cle` courte (nom des images,
`ensemble-points`) et, en format methode seulement, un `court` (2 à 4 mots, il situe chaque question du défi du
dimanche : sans lui, « 9 cycles » ne dit pas de quel moteur on parle).

Une fiche marquée « DÉJÀ DANS … » dans la liste est publiée par une autre semaine (même fiche gratuite à deux examens,
comme « Tontine ») : écarte-la. Le moteur refuse de la prendre.

Le bandeau doit tenir sur une ligne (environ 30 caractères) : pour toutes les séries d'un examen, n'en cite aucune
(« Éducation civique Probatoire ») ; pour deux ou trois, cite-les (« Chimie Probatoire C, D, E »). Pour le lien des
fiches d'une semaine à plusieurs séries, prends D quand elle en fait partie, sinon la première : les liens se
ressemblent d'une semaine à l'autre.

### 3. Construire et regarder

Relance `construire.mjs` (vues + brouillon `legendes.md` + lignes du planning), puis `photographier.py` (images + PDF).
Le moteur s'arrête avec un message clair si une fiche n'est plus gratuite, si le format ne convient pas ou si un indice
du samedi donne la réponse : corrige `semaine.json` et relance.

**Regarde les images toi-même** (outil Read sur les PNG) : au moins, pour chaque jour, la carte du matin
(`-1-question`), la vue méthode (`-2-methode`), la réponse du soir, puis le samedi et le dimanche. Le contrôle
automatique ne repère que le texte trop petit, qui déborde, ou un bandeau sur deux lignes ; il ne voit pas un titre
coupé au mauvais endroit, une formule mal placée, une liste qui se lit mal. Une vue signalée « sous 36 px sans
débordement » est souvent lisible : regarde-la avant de conclure. Un titre qui se coupe au milieu d'une formule
(« MA² + / MB² ») se règle avec `sans_coupure` dans `semaine.json`.

Si une fiche se lit mal en image (trop longue, structure confuse), ne réécris pas son texte : signale-le dans les
points pour l'enseignant, la correction se fait sur la fiche. Si c'est **le moteur** qui rend mal un texte correct
(numérotation, espace, mise en page), corrige `scripts/publications/` (il est dans git), reconstruis la semaine et les
autres semaines pas encore publiées, regarde les vues touchées, et dis-le dans ton compte rendu. Si tu ne peux pas
modifier le moteur, écris-le en tête du LISEZMOI de la semaine, sous « À corriger avant publication ».

### 4. Écrire les légendes

`legendes.md` arrive avec tout ce qui est calculé (en-têtes, années, liens, hashtags, invitations) et des passages
`⟦…⟧` à écrire. Remplace chacun, sans toucher au reste. Le ton et des exemples tirés des semaines déjà faites sont dans
`references/legendes.md` : lis-le avant d'écrire. Les réponses du soir reprennent celle de la fiche (rappelée dans le
passage), jamais une réponse refaite de tête.

### 5. Le LISEZMOI de la semaine

Écris `LISEZMOI.md` dans le dossier de la semaine, sur ce modèle :

```markdown
# <Matière> <examen> : semaine du <lundi> au <dimanche>, fiches gratuites seules

**Rien n'est publié. Ne rien publier avant la relecture d'un enseignant de <matière>** (`a-montrer-a-l-enseignant.pdf`).

## Les 5 fiches
<les 5, dans l'ordre, et pourquoi cet ordre. Constaté en ligne le <date> : ce sont les gratuites. Quiz sans compte dans la matière : oui/non.>

## À montrer à l'enseignant (jugements de l'assistant, à confirmer)
- <ambiguïtés repérées en lisant les fiches : un exercice qui contredit la méthode, une réponse qui cite une notion
  que la fiche n'explique pas, une formulation qui peut tromper, une unité, une donnée manquante>
- Les mentions « d'après le <examen> AAAA » des exercices et les années annoncées, à comparer aux sujets.

Une correction se fait sur la fiche en ligne (et dans le fichier du dépôt s'il existe), puis `--actualiser`.

## Regénérer
<les deux commandes, avec le chemin de la semaine>
```

Les points pour l'enseignant sont la partie la plus utile du LISEZMOI : lis chaque fiche comme un élève qui ne connaît
pas la notion, refais chaque calcul, et note ce qui le ferait trébucher (une étape que la méthode ne donne pas mais
que la réponse utilise, un piège que l'exercice n'exerce pas, un mot jamais défini). Dis que ce sont tes jugements, à
confirmer. Si tu peux lire les sujets (base locale, en lecture seule), confronte-y les années annoncées ; sinon laisse
ce point à l'enseignant.

Note aussi ce qui tient au calendrier : un 31 décembre ou un 1er janvier sera peu lu, une légende qui cite une fête
datée (« ce 11 février ») est à retoucher si la date bouge.

### 6. Finir

Relance `reserve.mjs` (la semaine y apparaît), puis `construire.mjs … --verifier` : il doit dire que site, instantané et
légendes concordent. Dans ton compte rendu : la semaine et ses dates, les 5 fiches, les vues signalées, les points pour
l'enseignant, et que rien n'est publié. Les images sont dans `images/4x5/` (Facebook, Instagram) et `images/9x16/`
(statuts, stories).

## Après la relecture de l'enseignant

Une correction se fait **sur la fiche** (administration du site ; et dans `backend/memos/donnees/<fichier>.json` si la
matière en a un), jamais seulement dans les images. Puis `construire.mjs --actualiser` (il liste ce qui a changé),
`photographier.py`, et reporte à la main dans `legendes.md` ce que la correction touche (les légendes ne sont jamais
réécrites par le moteur). Dans `planning.csv`, le statut passe à `Relu (par qui)`.

## Juste avant de publier

`construire.mjs … --verifier` compare le site à l'instantané (texte modifié, fiche plus gratuite, quiz disparu) et
cherche des `⟦…⟧` oubliés. S'il signale un écart : `--actualiser`, `photographier.py`, légendes. Le statut passe à
`Programmé`, puis `Publié` avec le lien de la publication. La colonne `Réactions` (commentaires, partages, deux jours
après) servira à choisir les semaines à reprendre quand la réserve sera vide.

## Pièges connus

- La réserve change : des fiches deviennent gratuites dans la journée (5 en anglais du Probatoire le 27/11/2026).
  Relance toujours `reserve.mjs` avant de choisir.
- Une même fiche peut être gratuite à deux examens (« Tontine », BEPC et Probatoire) : `reserve.mjs` et la liste de
  `construire.mjs` la marquent comme prise dès qu'une semaine l'utilise.
- Semaine à plusieurs séries (chimie C/D/E, physique D/TI, éducation civique) : `cursus` liste toutes les séries,
  `examen` vaut « Probatoire » ; voir `references/semaine-json.md`. Dis dans le LISEZMOI quelle série vise le lien.
- Format `definition` (éducation civique) : le samedi on retrouve le mot à partir de sa définition. Si une définition
  contient un mot du terme (même au singulier, même accordé), le moteur s'arrête : écris un `indices` qui la reformule
  sans ce mot, sans rien ajouter. Relis quand même l'indice : un synonyme trop transparent donne aussi la réponse.
- Les fiches d'éducation civique du lycée ont été rédigées à partir des sujets, pas extraites de questions « Définis… »
  (voir le `_commentaire` du fichier dans `backend/memos/donnees/`). « Notion demandée » reste vrai ; « comme à
  l'examen » ou « l'examen te demandera de la définir » ne l'est pas.
- `planning.csv` n'est complété qu'une fois par semaine : pour changer des dates, édite le fichier.
- Le brouillon `legendes.md` n'est écrit que s'il n'existe pas ; pour repartir de zéro, supprime-le d'abord.
