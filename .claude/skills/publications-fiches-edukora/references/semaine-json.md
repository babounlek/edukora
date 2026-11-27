# semaine.json

Un fichier par semaine, à la racine de son dossier. Le moteur (`scripts/publications/construire.mjs`) n'a besoin de
rien d'autre : les textes viennent du site.

## Champs

| Champ | Obligatoire | Rôle |
|---|---|---|
| `lundi` | oui | `"AAAA-MM-JJ"`, un lundi. Sert aux dates du planning. |
| `format` | oui | `"methode"` (fiches avec exemple, piège, exercice, réponse) ou `"definition"` (définition seule). |
| `examen` | oui | Tel qu'il se lit dans une phrase : « du BEPC », « au Probatoire D ». `"BEPC"`, `"Probatoire D"`, `"Probatoire"` (plusieurs séries), `"BAC"`. |
| `cursus` | oui | Ids des cursus : BEPC 14 ; Probatoire A 15, C 19, D 21, E 23, TI 25 ; BAC A 16, C 20, D 22, E 24, TI 26. |
| `matiere` | oui | Id de la matière (colonne « matière » de `reserve.mjs`). |
| `bandeau` | oui | Le texte après « Fiches EduKora · » sur chaque image et dans les légendes : `"Maths Probatoire D"`. Une ligne, environ 30 caractères : toutes les séries d'un examen → aucune citée (`"Éducation civique Probatoire"`). |
| `matiere_nom` | oui | Le nom dans une phrase, en minuscules sauf sigle : `"maths"`, `"PCT"`, `"éducation civique"`, `"SVT"`. Le moteur fait l'élision (« d'éducation civique »). |
| `hashtags` | oui | Ceux de l'examen et de la matière, en tête : `["#Probatoire", "#ProbatoireD", "#Maths"]`. Le moteur ajoute ceux du jour et `#Cameroun #Révisions #EduKora #FichesEduKora`. |
| `fiches` | oui | `[]` pour lister les gratuites ; puis 5 objets `{ "id", "cle", "court" }` dans l'ordre de la semaine. |
| `langue` | non | `"en"` pour une semaine GCE : images, vidéos et lignes publiées des légendes en anglais. Défaut : français. |
| `source` | non | `"http://localhost"` pour lire des fiches encore en brouillon (serveur local). À retirer avant de publier, voir la section GCE de la compétence. |
| `lien_cursus` | non | La série visée par le lien des fiches quand il y en a plusieurs (défaut : la première de `cursus`). Prendre D quand elle en fait partie. |
| `preuve` | non | Phrase de la carte du lundi au vendredi (format methode), avec `{n}`, `{debut}`, `{fin}`. Défaut : `Demandée dans <b>{n} sujets</b> du <examen> entre {debut} et {fin}`. Le nom de l'examen n'y est jamais coupé (le moteur s'en charge). |
| `defi` | non | « Le défi du dimanche : 5 … » : `"questions"` (défaut) ou `"exercices"` ; en anglais, `"exercises"`. |
| `sans_coupure` | non | Bouts de titre à ne pas couper en fin de ligne, écrits avec des espaces ordinaires : `["MA² + MB²"]`. Rarement utile : les mots à trait d'union (« est-il », « 2,4-diméthylhexane »), un nombre et son unité, un mot et la formule en « = » qui le suit ne se coupent déjà plus. Le moteur prévient si un bout ne se trouve dans aucun titre. |
| `reprise` | non | `true` pour une semaine qui reprend exprès des fiches déjà publiées (quand la réserve sera vide). Sinon le moteur refuse une fiche déjà prise. |
| `ordre_devine` | non | (definition) ordre des 5 clés le samedi, pour ne pas suivre celui de la semaine. Défaut : 4e, 1re, 5e, 3e, 2e. |
| `indices` | non | (definition) `{ "cle": "texte" }` : la définition reformulée sans le mot à trouver. |

Une fiche : `id` (celui du site, dans la liste ou dans `sources/fiches-en-ligne.json`), `cle` (minuscules, chiffres,
tirets : elle nomme les images, `j3-thales-…`), `court` (format methode seulement, 2 à 4 mots ; il situe chaque question
du défi du dimanche).

## Exemple : une série

```json
{
  "lundi": "2026-12-28",
  "format": "methode",
  "examen": "Probatoire D",
  "cursus": [21],
  "matiere": 10,
  "bandeau": "Maths Probatoire D",
  "matiere_nom": "maths",
  "hashtags": ["#Probatoire", "#ProbatoireD", "#Maths"],
  "fiches": [
    { "id": 572, "cle": "derivee-quotient", "court": "Dérivée d'un quotient" },
    { "id": 570, "cle": "asymptote", "court": "Asymptote" }
  ]
}
```

(5 fiches dans la réalité.)

## Exemple : plusieurs séries

Les mêmes 5 fiches gratuites servent la chimie du Probatoire C, D et E. Les sessions de chaque série sont réunies.

```json
{
  "lundi": "2027-01-11",
  "format": "methode",
  "examen": "Probatoire",
  "cursus": [19, 21, 23],
  "lien_cursus": 21,
  "matiere": 197,
  "bandeau": "Chimie Probatoire C, D, E",
  "matiere_nom": "chimie",
  "hashtags": ["#Probatoire", "#Chimie"],
  "preuve": "Demandée à <b>{n} sessions</b> du Probatoire C, D ou E, de {debut} à {fin}",
  "fiches": []
}
```

## Exemple : définitions

```json
{
  "lundi": "2026-12-21",
  "format": "definition",
  "examen": "BEPC",
  "cursus": [14],
  "matiere": 222,
  "bandeau": "Éducation civique BEPC",
  "matiere_nom": "éducation civique",
  "hashtags": ["#BEPC", "#ÉducationCivique"],
  "ordre_devine": ["patriotisme", "campagne", "tontine", "suffrage", "scrutin"],
  "indices": {
    "scrutin": "L'ensemble des opérations par lesquelles les électeurs, en votant, désignent leurs représentants ou se prononcent sur une question qui leur est soumise."
  },
  "fiches": [
    { "id": 6, "cle": "campagne" }, { "id": 1, "cle": "scrutin" }, { "id": 5, "cle": "suffrage" },
    { "id": 4, "cle": "patriotisme" }, { "id": 3, "cle": "tontine" }
  ]
}
```

Un indice reformule sans rien ajouter : il retire le mot (« Le scrutin est l'ensemble… » devient « L'ensemble… ») ou
coupe une précision qui le contient. Il ne doit pas devenir plus facile ni plus dur que la fiche.

## Ce que le moteur produit

| Fichier | Contenu |
|---|---|
| `sources/fiches-en-ligne.json` | L'instantané du site : les gratuites, leurs sessions, et les essais de quiz sans compte de la matière. |
| `sources/pages.html` | Toutes les vues, avant photo. |
| `images/4x5/`, `images/9x16/` | Les PNG (1080 × 1350 et 1080 × 1920). Une image qui n'est plus produite est supprimée. |
| `a-montrer-a-l-enseignant.pdf` | Les vues 4:5, deux par ligne. |
| `legendes.md` | Brouillon avec passages `⟦…⟧`, seulement s'il n'existe pas. |
| `legendes-tiktok.md` | Tiré de `legendes.md` une fois celui-ci écrit (accroche et hashtags du matin), seulement s'il n'existe pas. |
| `sources/videos.html` | Les vidéos TikTok, scène par scène, avant tournage (`filmer.py`). |
| `videos/` | (filmer.py) Une vidéo MP4 par fiche, 1080 × 1920, muette, et un `.jpg` de couverture. |
| `sources/planche-<vidéo>.png` | (filmer.py) 10 images prises dans la vidéo, pour la regarder d'un coup d'œil. |
| `../../planning.csv` | 23 lignes « À relire » (dont 5 TikTok) ; seules les lignes qui manquent à la semaine sont ajoutées. |

Format methode, par fiche : 6 vues 4:5 (question, méthode ou « à retenir », exemple, piège, à toi, réponse du soir) et
3 vues 9:16 (à toi, piège, réponse) ; samedi les 5 pièges ; dimanche le défi et ses réponses. Une fiche dont la
définition commence par `**À retenir**` est annoncée « Fiche à retenir », les autres « Fiche de méthode ».

Format definition, par fiche : le mot le matin, la définition le soir (4:5 et 9:16) ; samedi « Quel est le mot ? » ;
dimanche les 5 définitions à garder.

Vidéo TikTok, format methode : la question (fond vert), la méthode ou « À retenir » (le contenu de l'image 2, formules
comprises, 6 à 14 s), le piège, « À toi » et l'exercice avec un compte à rebours de 5 s, la réponse, l'appel vers le
site. Format definition : le mot, « Dis-le avec tes mots » et le compte à rebours, la
définition, l'appel. La durée de chaque scène suit la longueur de son texte.

L'invitation des images et des légendes dépend des essais de quiz : s'il y en a un dans la matière pour chaque série,
« Essaie un quiz… » ; sinon « Essaie un quiz gratuit dans une autre matière… ».
