# Complément aux consignes - Physics (code 0580) et leçons des lots Maths et Chimie

Lis CONSIGNES.md puis CONSIGNES_COMPLEMENT_CHIMIE.md (seule la section « Leçons du lot Maths » et les règles générales
t'intéressent) ; ce complément précise la Physique.

## Identité du sujet

- `matiere` "Physics", `code_matiere` "0580" (vérifie le code imprimé sur la page de garde), `examen` "gce_ol".
- DOSSIER = `gce-ol-physics-<annee>-p<paper>-officiel-cameroun` (ATTENTION : "physics", pas "physique").
- **VÉRIFIE LE NIVEAU sur la page de garde AVANT de transcrire** : le dossier de téléchargement contient au moins un sujet
  ADVANCED LEVEL rangé par erreur parmi les O/L (« ADVANCED LEVEL », code 07xx). Si ton PDF n'est pas « ORDINARY LEVEL » code 0580,
  ARRÊTE-TOI sans rien écrire et rapporte ce que tu as lu (code, niveau, durée, structure).
- Paper 1 : QCM (50 questions attendues, à confirmer, 1h30). Paper 2 : questions rédigées, 2h30, Section I (toutes les questions,
  environ 1h) puis Section II avec un choix dans chaque question (« answer EITHER a, b and c OR d, e and f »).

## Paper 2 : sections et choix

- Garde les numéros imprimés (uniques d'une section à l'autre : `numero_exercice` "1".."N"). `groupes` = ["SECTION I"] ou
  ["SECTION II"] (texte exact du sujet : « SECTION I » / « SECTION II » en chiffres romains, comme imprimé).
- Section II : chaque question est UN exercice dont les sous-questions sont numérotées "a".."f". `regles_choix` (identique dans TOUS
  les fichiers du dossier) :
  `[{"type":"ou","portee":"SECTION II","options":[["a","b","c"],["d","e","f"]]}]` - adapte les repères à ce que le sujet imprime
  (le sujet peut aussi proposer plus de deux jeux ; vérifie). Si une section impose « n questions sur m », utilise le type "parmi".
- Le sujet donne les points par sous-partie, ex. « (2 marks) » : additionne par bloc lettré pour `points` de la sous-question et mets
  le total de la question dans `points` de l'exercice. Ne corrige jamais les points imprimés.
- Constantes données (g, c, e...) : dans `introduction_markdown`, et utilise-les dans tes calculs, jamais d'autres valeurs.
- Les questions qui demandent de décrire une expérience (« Include: a list of apparatus, a diagram, the procedure, how the data is used,
  any precaution ») : la réponse modèle suit exactement ces cinq rubriques, en gras, avec le schéma décrit dans le corrigé.
- Schéma ou graphe à TRACER par l'élève : décris-le (axes, points clés, forme) ; ne produis pas de figure de corrigé.

## Écrire la physique

- Unités SI en LaTeX : `$\mathrm{m\,s^{-1}}$`, `$\Omega$`, `$^\circ\mathrm{C}$`. Chaque résultat numérique a son unité et un nombre de chiffres
  significatifs raisonnable (2 ou 3, comme le sujet).
- Ecris la formule, le remplacement avec les unités, puis le résultat. Vérifie TOUS les calculs avec Python (avec les constantes du sujet).
- Montages électriques, rayons lumineux, systèmes de poulies, graphes mesurés : ce sont des figures INDISPENSABLES, à produire
  (voir CONSIGNES). Lis soigneusement les valeurs portées sur un schéma de circuit avant de calculer.
- Si une donnée du sujet est contradictoire (ex. un schéma qui ne colle pas aux valeurs de l'énoncé), dis laquelle tu retiens dans
  `incertitudes` et dans le corrigé.
- Thèmes physique (anglais, minuscules, courts) : measurement, motion, forces, work energy and power, simple machines, pressure,
  density, thermal physics, heat transfer, expansion, change of state, waves, sound, light and reflection, refraction and lenses,
  electrostatics, current electricity, electric circuits, magnetism, electromagnetism, electromagnetic induction, electronics and
  semiconductors, atomic and nuclear physics, practical physics. Tag.name est UNIQUE et PARTAGÉ avec le contenu français : évite tout nom
  qui pourrait exister tel quel en français ; en cas de doute, reformule en anglais plus explicite.

## Règles d'or (retour d'expérience des lots précédents)

1. **Option fautive ou clé discutable** (QCM) : question OUVERTE, options recopiées dans l'énoncé (« *Options as printed:* A) ... »),
   valeur exacte dans le corrigé, aucune lettre désignée. Signale-la dans `incertitudes`.
2. **SECONDE PASSE OBLIGATOIRE** : après avoir fini, rouvre CHAQUE page du sujet en image, compare ton énoncé de chaque question à la
   page (données, unités, tableaux, lettres) et résous chaque question une deuxième fois. Ne rends pas ton rapport sans l'avoir faite et
   indique dans le rapport le nombre de corrections qu'elle a produites.
3. Préfixe tes fichiers temporaires par ton DOSSIER ; n'écris que dans ton dossier de sortie.
4. Le validateur attend `--code 0580`.
