# Complément quiz GCE - les 19 matières sans quiz (O Level et A Level)

Lis `CONSIGNES_QUIZ_GCE.md` en entier, puis ce complément : **il prime** pour le niveau, la matière et la rigueur. Le contrat des items
(champs, QCM, `external_id`, validateur, seconde passe, dossier de sortie, ce que tu rends) reste celui de `CONSIGNES_QUIZ_GCE.md`.
Ce complément remplace les passages de `CONSIGNES_QUIZ_GCE.md` propres à Maths/Physique/Chimie (constantes, `g = 10`, masses atomiques).

## 1. Niveau : donné par la requête, jamais deviné

- `cursus` vaut `[{"examen":"gce_ol","serie":""}]` (**O Level, Form 5**) ou `[{"examen":"gce_al","serie":""}]` (**A Level, Lower/Upper Sixth**).
  Recopie-le TEL QUEL dans chaque item. Une requête = UN niveau.
- **O Level** : questions courtes et directes, vocabulaire du programme Form 5, un seul raisonnement à la fois.
- **A Level** : raisonnement en plusieurs étapes, analyse, comparaison, évaluation, vocabulaire précis de la discipline ; un QCM A Level pose un
  vrai piège de raisonnement, pas une définition de Form 5.
- `matiere` = le libellé de la requête, tel quel (« Citizenship Education », « Special Bilingual Education French »...). `theme` = `competence`
  de la requête, exactement. Pas de `savoir_officiel`.

## 2. Rigueur par famille de matières

Tout fait doit être **exact, vérifiable et au programme du Cameroon GCE Board**. Si tu n'es pas certain d'un fait (date, chiffre, nom, valeur),
**écarte l'item** ou reformule pour ne garder que ce dont tu es sûr. N'invente jamais une statistique, une citation, un texte de loi ni un événement.

- **Sciences du vivant et de la terre** (Biology, Human Biology, Geology, Food and Nutrition) : faits de manuel standard ; pas de figure, décris
  l'expérience ou donne un tableau Markdown et demande une interprétation ou un calcul (pourcentage, rapport, rendement). Calculs recalculés par script.
- **Maths** (Additional Mathematics, Pure Mathematics with Mechanics / with Statistics) : tout calcul recalculé par script (`sympy` sinon `fractions`),
  forme exacte avant approximation. Mechanics : décris le schéma dans l'énoncé, `g = 9.8` écrit dans l'énoncé (A Level) ou `g = 10` (O Level),
  unités SI. Statistics : loi et paramètres nommés, valeurs de table données dans l'énoncé.
- **Informatique** (Computer Science, ICT) : tout code montré (fenêtre ```` ``` ````) est **exécuté par script** et la sortie annoncée est celle obtenue ;
  pseudo-code lisible, pas de syntaxe exotique ; pour ICT, tableur (références, fonctions) : donne le contenu des cellules en tableau Markdown et recalcule.
- **Économie et commerce** (Economics, Commerce) : calculs (élasticité, coût, profit, TVA, pourcentages) recalculés par script ; contextes camerounais
  plausibles (FCFA, marchés, coopératives, CEMAC) sans chiffres réels inventés présentés comme officiels.
- **Géographie et histoire** (Geography, History, Citizenship Education) : faits, dates et noms vérifiés ; formulations neutres sur les sujets politiques
  (pas d'opinion, pas de jugement sur un camp) ; l'histoire du Cameroun, de l'Afrique et du monde reste celle du programme. Pas de carte : décris
  l'emplacement avec des repères ; pour une lecture de tableau ou de données, donne les données dans l'énoncé.
- **Philosophy et Religious Studies** : exposé neutre et exact des doctrines, textes, auteurs, notions ; aucune prise de position ni hiérarchie entre
  croyances ; QCM sur ce que dit un auteur, un texte, une tradition, ou sur la structure d'un argument. Pas de citation entre guillemets si tu n'es pas sûr
  de sa forme exacte : paraphrase.
- **English Language** : le texte étudié (extrait, phrase, consigne de rédaction) est **dans l'énoncé** et original (jamais copié d'un sujet fourni ni d'un
  texte protégé) ; grammaire, vocabulaire, compréhension, résumé, registre. Une seule bonne option, les autres des erreurs réellement commises par les élèves.
- **French (O Level) et Special Bilingual Education French (A Level)** : **c'est du français appris par des anglophones**. La consigne et le corrigé
  explicatif sont **en anglais** (`### Method reminder`, `### Solution` restent en anglais) ; le texte cible (phrase, dialogue, passage, options) est en
  **français correct**, avec ses accents. Le validateur signale le français en « warn » : c'est attendu ici, à relire seulement pour la justesse
  (accords, conjugaison, genre). Niveau Form 5 (O) ou Sixth (A). Aucun texte copié.

## 3. Ce qui reste valable partout

- **Aucune figure** (zéro `figures`, zéro `![fig-`), sauf besoin absolu ; privilégie tableau Markdown ou description.
- **QCM** : plancher de la matière (voir `CONSIGNES_QUIZ_GCE.md` point 7 : 5 sur 6 en sciences, maths, langues et informatique ; 3 sur 6 en histoire, géographie, économie, commerce, citoyenneté ; 2 sur 6 en philosophie, religion, littérature), lettres `a` à `d`, bonne lettre variée, chaque distracteur = erreur plausible. **Une seule** bonne option : si deux options
  peuvent se défendre, reformule.
- **Énoncé autonome**, jamais « the passage above », « the figure ». Un texte à lire est dans l'énoncé.
- **`source_exercises`** : les `exercise_id` du matériel de référence qui t'ont inspiré (jamais cités). Ne copie JAMAIS le matériel de référence (9 mots
  consécutifs identiques = refus du validateur) : change contexte, valeurs et formulation.
- **Corrigé** : `### Method reminder` (2 à 4 lignes) puis `### Solution`, en anglais.
- Fichier = un tableau de `cible.nombre_items` items ; génération par script Python (`D:\edukora\venv\Scripts\python.exe`, script dans le scratchpad, jamais
  dans le dépôt), `json.dump` avec chaînes brutes pour le LaTeX, validateur jusqu'à `OK`, puis seconde passe en résolvant chaque QCM sans regarder ton corrigé.
