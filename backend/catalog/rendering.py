"""
Moteur de compilation Markdown de catalog : transforme des Question/Exercise/Cours
déjà en base (validés) en Markdown affichable (Lesson.content_markdown, Exercise.
enonce_markdown/corrige_markdown, Cours.content_markdown). Extrait de models.py pour
séparer le schéma de son moteur de rendu - voir aussi ingestion.py (traduction JSON ->
modèles, jamais de Markdown compilé) et ingestion_repairs.py (rustines ponctuelles sur
la sortie de correction-experte, une préoccupation différente de "comment on affiche
un contenu déjà propre en base").

Les méthodes `compile_from_*`/`preview_markdown` sur Lesson/Exercise/Cours restent en
place (voir models.py) comme de fins appels vers ce module - aucun consommateur
existant (ingestion.py, admin.py, les vues) n'a besoin de changer.
"""

import re

from .models import Cours, StatutContenu, TypeReponse

# correction-experte ouvre CHAQUE corrigé d'exercice par une "fiche d'identité"
# (matière/série/examen/année) - pertinent quand un exercice est traité seul, mais
# redondant une fois plusieurs exercices d'une même épreuve fusionnés en un Lesson.
# On n'en garde qu'une seule occurrence, juste après le titre. Deux formats observés
# selon les sessions de la compétence : bloc de code, ou tableau Markdown.
_FICHE_IDENTITE_RE = re.compile(r"```\nMatière\s*:.*?```\n*(?:---\n*)?", re.DOTALL)
_FICHE_IDENTITE_TABLE_RE = re.compile(r"##\s*Fiche d['’]identité\s*\n+(?:\|.*\|\n)+\n*(?:---\n*)?")

# corrige_markdown répète aussi "## Exercice N" en tête (déjà porté par le titre qu'on
# injecte nous-mêmes) - on la retire pour ne garder qu'un simple séparateur de section.
_EXERCICE_HEADING_RE = re.compile(r"^##\s*Exercice\s+\S+[^\n]*\n+", re.IGNORECASE)

# Isole chaque bloc "### Rappel de méthode" (un exercice peut en contenir plusieurs,
# un par sous-question) pour y injecter un marqueur [COURS_LINK:id] quand ce rappel a
# donné naissance à un Cours - voir _annotate_cours_links.
_RAPPEL_BLOCK_RE = re.compile(r"###\s*Rappel de méthode\s*\n+.*?(?=\n#{1,6}[ \t]|\n---|\Z)", re.IGNORECASE | re.DOTALL)

# Marqueur de secours que correction-experte ajoute quand un rappel_de_methode ne peut
# pas être fait à correspondre verbatim au corrigé (voir SKILL.md) - la publication étant
# désormais automatique (aucune relecture humaine), on le retire par sécurité pour ne
# jamais l'exposer tel quel à un élève si un moteur de rendu venait à afficher les
# commentaires HTML.
_RAPPEL_ORPHELIN_RE = re.compile(r"<!--\s*RAPPEL_NON_APPARIE\s*:.*?-->\n*", re.IGNORECASE | re.DOTALL)

# Une sous-question transcrit souvent déjà son propre repère visible telle qu'elle
# apparaît sur l'épreuve source - repère qui prend en pratique bien plus de formes
# qu'un simple "1. "/"2) " (voir le scan corpus-entier qui a motivé cette regex) :
#   - composé à plusieurs niveaux, séparateur point OU tiret : "1.2", "2.4.1", "1-2",
#     "3-3" (physique-chimie et anglais utilisent les deux conventions), y compris
#     un niveau lettre : "2.c", "1.a" ;
#   - lettre collée sans séparateur : "5a" ;
#   - ordinal à l'ancienne (épreuves 1980s-90s) : "1°- ".
# Pas de titre en double détecté sans ceci ("**1.2.** 1.2. Une amine...",
# "**2.** 2.c. Avec...", "**1.** 5a. What...", "**1.** 1°- Combien...").
#
# La ponctuation finale (point/parenthèse/tiret) n'est OPTIONNELLE qu'après un
# niveau composé À SÉPARATEUR EXPLICITE ("1.3.2 l'expression..." sans point final,
# cas réel) - jamais après une lettre collée sans séparateur ("5a"), sous peine de
# confondre un vrai repère ("5a. What...") avec une expression algébrique qui a
# exactement la même forme ("2x est la dérivée de...", "2x" n'étant pas un numéro
# suivi d'une lettre mais "2 fois x") : sans cette distinction, `numbered` sautait à
# tort le préfixe "**2.**" sur toute question dont l'énoncé commence par un terme
# du genre "2x", "3n"... - régression détectée sur un test déjà existant.
_ENONCE_ALREADY_LABELED_RE = re.compile(
    r"^\s*("
    r"\*\*"
    r"|\d+°\s*[-.]?\s"
    r"|\d+(?:[.\-](?:\d+[a-zA-Z]?|[a-zA-Z]))+\s*[.)\-]?\s"
    r"|\d+[a-zA-Z]\s*[.)\-]\s"
    r"|\d+\s*[.)\-]\s"
    r"|[A-Za-z]\s*[.):]"
    r")",
)


def _strip_redundant_local_marker(text, numero):
    """
    Retire un marqueur local du type "(b)" en tête du texte quand il redouble
    exactement le dernier segment du `numero` complet déjà affiché en préfixe (ex.
    numero="A.3.b", texte="(b) Étudier...") - correction-experte ne recopie que la
    lettre/le chiffre local hérité de l'énoncé source, jamais le chemin complet de la
    partie, donc sans ceci le lecteur voit le même repère deux fois : une fois dans le
    préfixe compilé ("**A.3.b.**"), une fois dans le texte d'origine ("(b)").
    """
    last_segment = numero.rsplit(".", 1)[-1]
    marker_re = re.compile(rf"^\(\s*{re.escape(last_segment)}\s*\)[.:]?\s*", re.IGNORECASE)
    return marker_re.sub("", text, count=1)


def _strip_embedded_qcm_options(texte, choix):
    """
    Retire, si présent, un bloc d'options déjà recopié en prose dans `texte` - la
    règle veut que correction-experte fournisse les options UNIQUEMENT via le champ
    structuré `choix` (voir _render_question_enonce, qui les rend lui-même juste
    après), jamais aussi en texte libre, mais quand cette règle n'est pas suivie le
    lecteur verrait sinon les mêmes options deux fois de suite (une fois telles que
    transcrites, une fois telles que reconstruites).

    La mise en forme de la copie déjà présente varie beaucoup selon les épreuves -
    une option par ligne ("a) ...\\nb) ...\\nc) ..."), toutes dans une même phrase
    séparées par un espace ou un point-virgule ("a) ... ; b) ... ; c) ..."), avec ou
    sans parenthèses ("(a) ... (b) ..."), ou séparées par une ligne vide - le seul
    invariant commun à toutes est l'ORDRE des lettres, jamais leur séparateur.
    Cherche donc la première occurrence de la lettre a), n'importe quoi (non
    gourmand, y compris des sauts de ligne) jusqu'à la lettre b), etc., jusqu'à la
    fin de ligne après la dernière lettre.
    """
    lettres = [choix_item["lettre"] for choix_item in choix if choix_item.get("lettre")]
    if len(lettres) < 2:
        return texte
    marqueurs = [rf"\(?{re.escape(lettre)}\)" for lettre in lettres]
    bloc_re = re.compile(r"[\s\S]*?".join(marqueurs) + r"[^\n]*")
    match = bloc_re.search(texte)
    if not match:
        return texte
    return texte[: match.start()] + texte[match.end() :]


def _exercice_application_enonce(item):
    """
    Énoncé d'un exercice de la section 6 (mode cours) : soit un bloc unique
    (`enonce_markdown`), soit - pour un exercice à sous-questions - un préambule
    partagé (`enonce_intro_markdown`) suivi de l'énoncé de chaque `questions[]`, même
    convention que compile_exercise_from_questions() côté corrigé d'épreuve.
    """
    questions = item.get("questions")
    if not questions:
        return item.get("enonce_markdown", "")
    intro = item.get("enonce_intro_markdown") or ""
    corps = "\n\n".join(q.get("enonce_markdown", "") for q in questions)
    return f"{intro}\n\n{corps}" if intro else corps


def _exercice_application_solution(item):
    """
    Solution d'un exercice de la section 6 : soit `solution_markdown` unique, soit la
    concaténation de la solution de chaque `questions[]` - `solution_markdown` et
    `corrige_markdown` acceptés au niveau sous-question (la compétence peut nommer le
    champ selon l'un ou l'autre de ses deux modes, corrigé d'épreuve vs cours)."""
    questions = item.get("questions")
    if not questions:
        return item.get("solution_markdown", "")
    return "\n\n".join(q.get("solution_markdown") or q.get("corrige_markdown", "") for q in questions)


def _render_question_enonce(question, numbered):
    """
    Reconstruit le texte affiché d'une sous-question à partir des champs
    structurés qu'elle porte déjà (numero, choix) - correction-experte les
    fournit systématiquement à part (voir Question.choix) plutôt que de les
    recopier en prose dans enonce_markdown, pour éviter la duplication qu'on
    obtiendrait sinon entre texte libre et champ structuré. Sans cette
    reconstruction, le numero et les options d'un QCM ne seraient jamais visibles
    en dehors du Quiz (qui les lit directement depuis l'API, pas depuis ce texte
    compilé) : le lecteur d'une épreuve verrait un énoncé nu suivi d'un corrigé
    qui référence "la bonne réponse c)" sans qu'aucune option n'ait été montrée.

    `numbered` ne préfixe le numero que si l'exercice a plusieurs sous-questions -
    inutile d'afficher "1." pour l'unique question d'un exercice simple. Le
    préfixe est aussi sauté quand `enonce_markdown` affiche déjà son propre repère
    (numérotation d'origine, lettre, titre de Partie...) - voir
    _ENONCE_ALREADY_LABELED_RE : sans ce garde-fou, un exercice dont chaque
    sous-question transcrit fidèlement sa numérotation source afficherait un
    repère en double ("**2.** 2. Déduire...", "**A.1.** **Partie A**"). Quand le
    préfixe est bien ajouté, un marqueur local redondant en tête de texte ("(b)"
    pour un numero "A.3.b") est retiré - voir _strip_redundant_local_marker :
    sinon le lecteur voit "**A.3.b.** (b) ..." plutôt que "**A.3.b.** ...".

    Pour un QCM, les options sont toujours reconstruites depuis `choix` (jamais
    laissées telles quelles si déjà recopiées en prose dans enonce_markdown - voir
    _strip_embedded_qcm_options) : source unique de vérité, qui évite à la fois la
    duplication et une incohérence de mise en forme entre les deux copies (ex. point
    final sur l'une, pas sur l'autre).
    """
    already_labeled = bool(_ENONCE_ALREADY_LABELED_RE.match(question.enonce_markdown))
    texte = (
        f"**{question.numero}.** {_strip_redundant_local_marker(question.enonce_markdown, question.numero)}"
        if numbered and not already_labeled
        else question.enonce_markdown
    )
    if question.type_reponse == TypeReponse.QCM and question.choix:
        texte = _strip_embedded_qcm_options(texte, question.choix).rstrip()
        options = "\n".join(f"{choix['lettre']}) {choix['texte']}" for choix in question.choix)
        texte = f"{texte}\n\n{options}"
    return texte


def _render_question_corrige(question, numbered):
    """
    Miroir de _render_question_enonce côté corrigé : sans réafficher la question
    posée, un exercice à plusieurs sous-questions affiche une série de "### Rappel
    de méthode" à la suite sans aucun moyen de savoir à quelle question chacun
    répond - l'élève doit remonter au sujet, parfois des dizaines de lignes plus
    haut, pour retrouver l'énoncé correspondant. On réutilise donc
    _render_question_enonce (numero + son garde-fou "already_labeled", déjà
    éprouvé côté énoncé) comme préambule de chaque bloc corrigé, avant
    corrige_markdown lui-même - qui ne recopie jamais son propre repère : il
    commence toujours par un des titres de niveau 3 imposés par SKILL.md ("###
    Rappel de méthode", "### Piège à éviter", "### Conseil" ou directement "###
    Corrige").
    """
    if not numbered:
        return question.corrige_markdown
    return f"{_render_question_enonce(question, numbered)}\n\n{question.corrige_markdown}"


def compile_exercise_from_questions(exercise):
    """
    Concatène les Question rattachées (dans l'ordre) pour peupler enonce_markdown/
    corrige_markdown - même principe que compile_lesson_from_exercises(). Appelée
    à l'ingestion après création des Question et attache des figures (voir
    catalog.ingestion.ingest_exercise), et par clean_em_dash après correction du
    contenu source des Question.

    Peuple aussi exercise.themes en union des thèmes de chaque Question : themes vit
    maintenant au niveau de la Question (granularité utile au Mode Quiz), mais
    compile_lesson_from_exercises() lit encore exercise.themes.all() pour bâtir les
    thèmes de la Lesson (recherche plein texte) - sans ce recopiage, cette agrégation
    se viderait silencieusement.
    """
    questions = list(exercise.questions.prefetch_related("themes").order_by("ordre"))
    intro = f"{exercise.enonce_intro_markdown}\n\n" if exercise.enonce_intro_markdown else ""
    numbered = len(questions) > 1
    exercise.enonce_markdown = intro + "\n\n".join(
        _render_question_enonce(q, numbered) for q in questions
    )
    exercise.corrige_markdown = "\n\n".join(
        _render_question_corrige(q, numbered) for q in questions
    )
    exercise.save(update_fields=["enonce_markdown", "corrige_markdown", "updated_at"])

    themes = set()
    for question in questions:
        themes.update(question.themes.all())
    exercise.themes.set(themes)


def annotate_cours_links(corrige, rappels, *, append_unmatched=True):
    """
    Insère un marqueur `[COURS_LINK:<slug>]` juste après chaque bloc "### Rappel de
    méthode" dont le rappel correspondant a donné naissance à un Cours - le frontend le
    détecte pour afficher un lien "Voir le cours complet" sur le callout, vers l'URL
    publique du cours ("/cours/<slug>"). La correspondance entre un bloc du texte et son
    rappel se fait par inclusion du texte exact extrait à l'ingestion (contenu_markdown),
    seule donnée fiable puisque le Markdown compilé ne porte pas de FK.

    Pas spécifique à catalog malgré le module : `rappels` accepte tout itérable
    exposant `.cours_id`/`.cours`/`.contenu_markdown` - RappelDeMethode ici, mais aussi
    inedit.models.RappelDeMethodeInedite (voir inedit.views._corrige_markdown_with_cours_links),
    qui pointe vers ce même Cours (jamais un Cours "inédite" séparé).

    Un même bloc peut correspondre à plusieurs rappels : la compétence fusionne parfois
    plusieurs sous-questions sous un unique "### Rappel de méthode" plutôt que d'en
    écrire un par sous-question - dans ce cas tous les cours associés sont insérés à la
    suite du bloc.

    Il arrive aussi que `contenu_markdown` soit une reformulation plutôt qu'une
    citation exacte du corrigé (l'IA ne respecte pas toujours cette consigne) : le
    rappel ne matche alors aucun bloc. Avec append_unmatched=True (catalog - `corrige`
    couvre déjà tout l'exercice, donc TOUS les rappels passés lui appartiennent
    forcément), son marqueur est ajouté en fin d'exercice plutôt que d'être perdu
    silencieusement - imprécis, mais le lien reste visible. Avec append_unmatched=False
    (inedit - RappelDeMethodeInedite est rattaché à l'exercice, pas à la question, voir
    sa docstring : `corrige` ne couvre ici qu'UNE question alors que `rappels` peut
    lister ceux de l'exercice entier), ajouter en fin serait une fuite - le lien d'un
    rappel appartenant à une AUTRE question du même exercice apparaîtrait à tort sur
    celle-ci : mieux vaut le taire que le tromper.
    """
    rappels = [r for r in rappels if r.cours_id and r.contenu_markdown.strip()]
    if not rappels:
        return corrige

    injected_slugs = set()

    def _inject(match):
        block = match.group(0)
        cours_slugs = [r.cours.slug for r in rappels if r.contenu_markdown.strip() in block]
        if not cours_slugs:
            return block
        injected_slugs.update(cours_slugs)
        markers = "\n\n".join(f"[COURS_LINK:{slug}]" for slug in cours_slugs)
        # Le lookahead de _RAPPEL_BLOCK_RE ne consomme qu'un seul \n avant la
        # frontière suivante (### / ---) : la ligne blanche d'origine perd donc une
        # de ses deux newlines dans le texte restant non capturé. Sans ce \n final,
        # un "---" juste après transformerait le marqueur en titre Setext (<h2>)
        # au lieu de rester un simple paragraphe.
        return f"{block.rstrip()}\n\n{markers}\n"

    corrige = _RAPPEL_BLOCK_RE.sub(_inject, corrige)

    if append_unmatched:
        remaining_slugs = [r.cours.slug for r in rappels if r.cours.slug not in injected_slugs]
        if remaining_slugs:
            markers = "\n\n".join(f"[COURS_LINK:{slug}]" for slug in remaining_slugs)
            corrige = f"{corrige.rstrip()}\n\n{markers}"

    return corrige


def annotate_single_cours_link(corrige, cours_slug):
    """
    Variante d'annotate_cours_links() pour un contenu qui n'a pas de RappelDeMethode
    dédié à apparier verbatim (voir quiz.CompetenceItem : depuis 2026-08-14 le skill
    concepteur-quiz-competence écrit lui-même un bloc "### Rappel de méthode" dans
    corrige_markdown, mais rien ne trace ce bloc vers un Cours comme le fait
    RappelDeMethode.contenu_markdown pour Exercise) - insère `[COURS_LINK:<cours_slug>]`
    juste après le premier bloc "### Rappel de méthode" trouvé, ou en fin de texte si
    aucun bloc de ce type n'existe (contenu antérieur à cette exigence). Un seul slug,
    déjà choisi par l'appelant - pas de logique d'appariement à plusieurs rappels ici,
    un CompetenceItem ne porte qu'une seule compétence.
    """
    marker = f"[COURS_LINK:{cours_slug}]"
    match = _RAPPEL_BLOCK_RE.search(corrige)
    if not match:
        return f"{corrige.rstrip()}\n\n{marker}"
    return f"{corrige[:match.end()].rstrip()}\n\n{marker}\n{corrige[match.end():]}"


def _clean_exercise_corrige(exercise):
    """
    Corrige_markdown nettoyé (fiche d'identité/rappel orphelin retirés, titre
    normalisé en "### Corrigé", liens cours injectés) - partagé par
    _render_exercise_block() (un seul bloc Markdown concaténé, voir
    compile_lesson_from_exercises) et lesson_exercises_breakdown() (énoncé/corrigé
    exposés séparément à l'API, voir sa docstring). Jamais persisté sur
    exercise.corrige_markdown lui-même : recalculé à chaque lecture, pour qu'un
    changement de cette logique de nettoyage s'applique sans ré-ingérer le contenu.
    """
    # Si l'IA a quand même inclus une fiche d'identité par exercice (ancien format
    # bloc de code, ou nouveau format tableau - oubli de consigne dans les deux cas),
    # on la retire : ces informations vivent uniquement dans Lesson.header_info().
    corrige = _FICHE_IDENTITE_RE.sub("", exercise.corrige_markdown, count=1).lstrip()
    corrige = _FICHE_IDENTITE_TABLE_RE.sub("", corrige, count=1).lstrip()
    corrige = _EXERCICE_HEADING_RE.sub("### Corrigé\n\n", corrige, count=1)
    corrige = _RAPPEL_ORPHELIN_RE.sub("", corrige)
    return annotate_cours_links(corrige, exercise.rappels_de_methode.select_related("cours").all())


def _render_exercise_block(exercise):
    """
    Rend un Exercise validé en bloc Markdown autonome (énoncé + corrigé nettoyé),
    partagé par compile_lesson_from_exercises() et lesson_preview_markdown(). Pas de
    "## Exercice N" injecté ici : enonce_markdown porte déjà cette numérotation
    lui-même (ex. "**Exercice 1 (5 points).**"), telle que transcrite depuis
    l'épreuve source - l'ajouter en plus produirait un doublon visible.
    """
    return f"{exercise.enonce_markdown}\n\n{_clean_exercise_corrige(exercise)}"


# `numero_exercice` est un CharField - il doit accepter tout repère utilisé par l'épreuve
# source, pas seulement une numérotation simple ("Probleme-IIA", "Section III", voir
# Exercise.numero_exercice) - donc un ORDER BY SQL le trie alphabétiquement : "10" et
# "11" passent avant "2". Invisible tant qu'une épreuve reste sous 10 exercices, mais
# bac-c-svt-2015-cameroun en compte 11 et était bel et bien rendue dans le désordre
# (1, 10, 11, 2, 3...), aussi bien en lecture que dans content_markdown compilé. On
# retrie donc en Python partout où l'ordre est visible par l'élève - les trois appelants
# ci-dessous chargent de toute façon la liste entière.
_LEADING_NUMBER_RE = re.compile(r"^(\d+)")


def exercise_sort_key(exercise):
    """
    Ordre d'affichage d'un Exercise : numérique d'abord ("2" avant "10"), le préfixe
    numérique servant de clé principale pour que "3a"/"3b" restent groupés juste
    derrière "3". Un repère sans préfixe numérique ("Problème", "Section III") n'a pas
    de rang déductible : il passe après les exercices numérotés, entre eux par ordre
    alphabétique - en pratique ce sont les parties finales d'une épreuve (le Problème
    après les Exercices), jamais un repère qu'il aurait fallu insérer au milieu.
    """
    numero = str(exercise.numero_exercice or "").strip()
    match = _LEADING_NUMBER_RE.match(numero)
    if match:
        return (0, int(match.group(1)), numero.lower())
    return (1, 0, numero.lower())


# Barème en fin de titre ("(5 points)", "(10 marks)", "(2,5 pts)") - retiré du libellé
# exposé au frontend, qui reçoit `points` comme champ à part.
_POINTS_SUFFIX_RE = re.compile(r"\s*\(\s*([\d.,/]+)\s*(?:points?|pts?|marks?)\s*\)\s*$", re.IGNORECASE)

# Un segment en gras en tête d'énoncé est tantôt la référence de l'exercice
# ("**Exercice 1 : Chimie organique (5 points)**"), tantôt le simple numéro de la
# première sous-question ("**1.** Écris le nombre..."). Sans ce filtre, une épreuve
# dont l'exercice 1 n'a pas de préambule propre se retrouvait étiquetée "1." dans le
# sommaire. Un titre Markdown ("### ...") ne pose pas cette ambiguïté et n'y est pas
# soumis. Mêmes mots-clés que _EXERCISE_HEADING_PRESENT_RE côté ingestion_repairs,
# élargis aux découpages non numérotés réellement présents dans le corpus (les épreuves
# d'anglais ouvrent sur "**Section A: Grammar (10 marks)**").
_REFERENCE_EXERCICE_RE = re.compile(r"^(?:exercice|exercise|probl[eè]me|partie|section)\b", re.IGNORECASE)


def _exercise_titre_et_points(exercise):
    """
    (titre, points) d'affichage d'un Exercise, pour le sommaire de navigation du
    lecteur (voir SommaireNav côté frontend). Le titre n'a pas de champ dédié en base :
    il vit dans la première ligne de l'énoncé, soit comme titre Markdown ("### Exercice
    1 (5 points)"), soit comme premier segment en gras ("**Section D: Essay (10
    marks).** Write an essay..." - le reste de la ligne étant déjà du préambule).

    Cette première ligne est cherchée dans `enonce_intro_markdown`, et à défaut dans
    `enonce_markdown` : le préambule partagé est souvent absent (aucun des 4 exercices
    de chimie-bac-c-1999 n'en a), la référence vivant alors en tête de la première
    sous-question. Même repli que _repair_missing_exercise_heading côté ingestion.

    Toute autre forme EST du préambule ou de l'énoncé, pas un repère : on rend alors un
    titre vide plutôt qu'une première phrase tronquée en guise d'étiquette, et le
    frontend retombe sur "Exercice {numero}".

    `points` reste prioritairement le champ structuré Exercise.points ; le barème lu
    dans le titre ne sert que de repli, pour le contenu ingéré avant que ce champ ne
    soit systématiquement renseigné.
    """
    source = exercise.enonce_intro_markdown
    if not source.strip():
        source = exercise.enonce_markdown
    line = next((raw for raw in source.splitlines() if raw.strip()), "").strip()

    titre = ""
    if line.startswith("#"):
        titre = line.lstrip("#").strip()
    elif line.startswith("**"):
        fin = line.find("**", 2)
        candidat = line[2:fin].strip() if fin != -1 else ""
        titre = candidat if _REFERENCE_EXERCICE_RE.match(candidat) else ""

    titre = titre.rstrip(" .:")
    points = exercise.points.strip()
    match = _POINTS_SUFFIX_RE.search(titre)
    if match:
        titre = titre[: match.start()].rstrip(" .:")
        points = points or match.group(1)

    return titre, points


def lesson_exercises_breakdown(lesson):
    """
    Liste ordonnée {numero_exercice, titre, points, enonce_intro_markdown,
    enonce_markdown, corrige_markdown} par exercice validé - contrairement à
    content_markdown (un seul bloc Markdown concaténé, voir
    compile_lesson_from_exercises), garde énoncé et
    corrigé comme deux régions distinctes pour le frontend, qui replie l'énoncé par
    défaut dans le corrigé lu en ligne (voir EpreuveReaderPage.tsx, l'audit UX) sans
    avoir à reparser le Markdown déjà aplati pour deviner où l'un finit et l'autre
    commence - une segmentation par texte s'était montrée fragile (ex. "### Corrigé"
    n'est pas toujours présent, voir _EXERCICE_HEADING_RE : il ne remplace un titre
    que si le corrigé source en portait un, sinon le corrigé peut commencer
    directement par "### Rappel de méthode" sans aucun marqueur de transition).

    `enonce_intro_markdown` est sorti à part (plutôt que de rester noyé en tête de
    `enonce_markdown`, comme le fait exercise.enonce_markdown lui-même) : c'est là que
    vit la référence de l'exercice ("**Exercice 1 (6 points)**", transcrite depuis le
    sujet - voir _repair_missing_exercise_heading) ET le préambule partagé par toutes
    les sous-questions (contexte/données communes). Replier ça dans le même toggle que
    le reste de l'énoncé priverait un élève qui lit directement le corrigé (le cas
    par défaut) de tout repère sur quel exercice il lit et sur le contexte auquel
    chaque "### Rappel de méthode" fait implicitement référence - le frontend affiche
    donc ce champ toujours visible, juste avant le corrigé, hors du toggle. Retiré du
    `enonce_markdown` renvoyé ici pour ne pas le dupliquer quand l'élève déplie
    quand même l'énoncé complet.

    `titre`/`points` n'alimentent pas le corps du corrigé (déjà porté par
    `enonce_intro_markdown`/`enonce_markdown`) mais son sommaire de navigation - voir
    _exercise_titre_et_points et EpreuveSommaire côté frontend. Exercise.themes n'y est
    volontairement PAS exposé : c'est le cumul des thèmes de toutes les sous-questions
    (24 tags sur le seul exercice 1 de chimie-bac-c-1999), trop fin pour servir
    d'étiquette - en prendre un au hasard désignerait mal l'exercice.

    Liste vide pour une Lesson sans Exercise (FICHE, ou tout contenu non sectionné) -
    le frontend retombe alors sur content_markdown tel quel.
    """
    exercises = lesson.exercises.filter(statut=StatutContenu.VALIDE)
    result = []
    for exercise in sorted(exercises, key=exercise_sort_key):
        intro = exercise.enonce_intro_markdown
        enonce = exercise.enonce_markdown
        if intro and enonce.startswith(f"{intro}\n\n"):
            enonce = enonce[len(intro) + 2 :]
        titre, points = _exercise_titre_et_points(exercise)
        result.append({
            "numero_exercice": exercise.numero_exercice,
            "titre": titre,
            "points": points,
            "enonce_intro_markdown": intro,
            "enonce_markdown": enonce,
            "corrige_markdown": _clean_exercise_corrige(exercise),
        })
    return result


def lesson_preview_exercises(lesson):
    """
    Sujet public découpé par exercice - {numero_exercice, titre, points,
    enonce_markdown} - pour que la fiche d'une épreuve puisse repérer chaque exercice
    et pointer directement vers son corrigé (/lire#exercice-3), au lieu du seul bloc
    Markdown aplati de lesson_preview_markdown() où rien ne distingue un exercice du
    suivant.

    Ne renvoie JAMAIS le moindre champ de corrigé : contrairement à
    lesson_exercises_breakdown(), l'appelant est une vue publique
    (access.views.preview_lesson, AllowAny) - c'est le sujet gratuit, jamais le contenu
    réservé aux abonnés. `enonce_markdown` est l'énoncé complet, préambule inclus (pas
    de champ `enonce_intro_markdown` séparé ici : rien n'est replié dans le sujet, tout
    est déjà visible).

    Liste vide pour une Lesson sans Exercise - le frontend retombe alors sur
    preview_markdown tel quel, exactement comme pour le corrigé.
    """
    exercises = sorted(
        lesson.exercises.filter(statut=StatutContenu.VALIDE), key=exercise_sort_key,
    )
    result = []
    for exercise in exercises:
        titre, points = _exercise_titre_et_points(exercise)
        result.append({
            "numero_exercice": exercise.numero_exercice,
            "titre": titre,
            "points": points,
            "enonce_markdown": exercise.enonce_markdown,
        })
    return result


def lesson_preview_markdown(lesson):
    """
    Contenu public (non-abonné, identique connecté ou non) : l'énoncé complet de
    CHAQUE exercice - l'équivalent d'un sujet d'épreuve non corrigé, mis à
    disposition gratuitement. Le corrigé (rappel de méthode, résolution, piège,
    conseil) reste toujours réservé aux abonnés, quel que soit le nombre
    d'exercices - ce n'est plus un aperçu partiel mais le sujet dans son entier.

    Pour une FICHE/SUJET non sectionnée (sans Exercise du tout), le contenu
    n'a pas de séparation énoncé/corrigé : il reste montré tel quel.
    """
    exercises = sorted(
        lesson.exercises.filter(statut=StatutContenu.VALIDE), key=exercise_sort_key,
    )
    if not exercises:
        return lesson.content_markdown

    blocs = [exercise.enonce_markdown for exercise in exercises]
    return "\n\n---\n\n".join(blocs)


def compile_lesson_from_exercises(lesson):
    """
    Agrège les Exercise validés (rattachés via leur FK) dans ce Lesson :
    concatène le contenu Markdown et fusionne thèmes/mots-clés sans doublon.
    N'inclut jamais un Exercise encore en BROUILLON ou REJETE.
    """
    exercises = sorted(
        lesson.exercises.filter(statut=StatutContenu.VALIDE).prefetch_related(
            "themes", "mots_cles_recherche", "rappels_de_methode",
        ),
        key=exercise_sort_key,
    )

    blocs = []
    themes = set(lesson.themes.all())
    mots_cles = set(lesson.mots_cles_recherche.all())

    for exercise in exercises:
        blocs.append(_render_exercise_block(exercise))
        themes.update(exercise.themes.all())
        mots_cles.update(exercise.mots_cles_recherche.all())

    lesson.content_markdown = "\n\n---\n\n".join(blocs)
    lesson.save(update_fields=["content_markdown", "updated_at"])
    lesson.themes.set(themes)
    lesson.mots_cles_recherche.set(mots_cles)


def _wrap_bare_formula(text):
    # `formule_principale`/`variantes` (str) arrivent tantôt en LaTeX brut sans
    # aucun `$` (besoin d'être enveloppé en display math pour KaTeX), tantôt déjà
    # comme du markdown avec ses propres spans `$...$` mêlés à du texte français
    # (ex. "$(\\ln|x|)'=\\dfrac1x$ pour tout $x\\in\\mathbb R^*$ ; ..." - constaté
    # sur le Cours "fonction inverse et logarithme"). Envelopper ce second cas en
    # `$$...$$` casse KaTeX ($$$ triple, ou du texte français lu comme du LaTeX
    # display) : on ne l'enveloppe que si aucun `$` n'est déjà présent.
    return text if "$" in text else f"$${text}$$"


def _match_cours_by_title(item, exclude_pk):
    """Cours dont le titre matche exactement (insensible à la casse) un intitulé de
    prérequis, sinon None - best-effort : un intitulé générique ("Calcul littéral")
    ne matchera pas toujours un titre de Cours plus spécifique."""
    return (
        Cours.objects.filter(titre__iexact=item.strip(), statut=StatutContenu.VALIDE)
        .exclude(pk=exclude_pk)
        .first()
    )


def _render_cours_section(cours, section):
    section_type = section.get("type")

    if section_type == "accroche":
        return section.get("contenu_markdown", "")

    if section_type == "prerequis":
        # Lie chaque prérequis au Cours correspondant quand son titre matche
        # exactement (insensible à la casse) - best-effort : un intitulé de
        # prérequis générique ("Calcul littéral") ne matchera pas toujours un
        # titre de Cours (plus spécifique), auquel cas il reste un texte simple.
        #
        # "items_markdown" en repli sur "items" : constaté sur 638 Cours du corpus
        # (~18% des sections prerequis), la compétence utilise parfois le nom de champ
        # de la section synthese ("items_markdown") au lieu de celui documenté pour
        # prerequis ("items") - sans ce repli, la section reste vide (aucun item), pas
        # d'erreur visible, juste un "## Prérequis" sans rien dessous.
        items = section.get("items") or section.get("items_markdown") or []
        lines = []
        for item in items:
            match = _match_cours_by_title(item, cours.pk)
            lines.append(f"- [{item}](COURS_REF:{match.slug})" if match else f"- {item}")
        return "## Prérequis\n\n" + "\n".join(lines)

    if section_type == "regle":
        parts = [f"## {section.get('titre') or 'La règle'}", section.get("contenu_markdown", "")]
        if section.get("formule_principale"):
            parts.append(_wrap_bare_formula(section["formule_principale"]))
        for variante in section.get("variantes") or []:
            # correction-experte produit tantôt un objet {nom, quand_utiliser,
            # contenu_markdown}, tantôt - pour une simple variante de formule,
            # sans sous-titre ni précision d'usage - une chaîne nue de LaTeX brut
            # (ex. une règle "ln x>k" à côté de ses variantes "ln x<k", "ln x≥k"...,
            # constaté sans délimiteurs $$, comme formule_principale ci-dessus avant
            # d'être enveloppée). Les deux sont un contenu légitime de la
            # compétence, pas une erreur à rejeter.
            if isinstance(variante, str):
                parts.append(_wrap_bare_formula(variante))
                continue
            parts.append(f"### {variante.get('nom', '')}")
            if variante.get("quand_utiliser"):
                parts.append(f"*Quand l'utiliser : {variante['quand_utiliser']}*")
            parts.append(variante.get("contenu_markdown", ""))
        return "\n\n".join(p for p in parts if p)

    if section_type == "exemple_resolu":
        parts = ["## Exemple résolu", section.get("enonce_markdown", "")]
        for etape in section.get("etapes") or []:
            # Même tolérance texte-brut que pour erreurs_classiques/exercices_application
            # ci-dessous : "etapes" est parfois une liste de chaînes nues plutôt que
            # d'objets {numero, action, justification, resultat_markdown} - constaté sur
            # bac-c-d-chimie-1999-cameroun. Pas de titre "Étape N" à défaut d'un numero/
            # action distincts à afficher.
            if isinstance(etape, str):
                parts.append(etape)
                continue
            parts.append(f"**Étape {etape.get('numero', '')} - {etape.get('action', '')}**")
            if etape.get("justification"):
                parts.append(etape["justification"])
            if etape.get("resultat_markdown"):
                parts.append(etape["resultat_markdown"])
        if section.get("conclusion_markdown"):
            parts.append(section["conclusion_markdown"])
        return "\n\n".join(p for p in parts if p)

    if section_type == "erreurs_classiques":
        # Un item peut être un objet {erreur_markdown, pourquoi_faux,
        # correction_markdown} (forme structurée) ou - constaté sur
        # bac-c-d-chimie-1999/2000/2001/2002-cameroun et une centaine d'autres
        # Cours du corpus - une simple chaîne de texte, sans cette décomposition.
        # Même tolérance déjà en place pour `regle.variantes` juste au-dessus : les
        # deux sont un contenu légitime de la compétence, pas une erreur à rejeter.
        parts = ["## Erreurs classiques"]
        for item in section.get("items") or []:
            if isinstance(item, str):
                parts.append(f"### Erreur\n\n{item}")
                continue
            parts.append(f"### Erreur\n\n{item.get('erreur_markdown', '')}")
            parts.append(f"### Pourquoi c'est faux\n\n{item.get('pourquoi_faux', '')}")
            parts.append(f"### Correction\n\n{item.get('correction_markdown', '')}")
        return "\n\n".join(parts)

    if section_type == "exercices_application":
        # Titre distinct de "### Corrigé" (utilisé ailleurs pour le corrigé payant
        # d'une épreuve, toujours visible) : le frontend masque spécifiquement
        # "### Solution" derrière un bouton, pour que l'élève cherche par lui-même
        # avant de voir la réponse - c'est le principe même de l'auto-évaluation.
        #
        # Même tolérance texte-brut que ci-dessus pour "erreurs_classiques" : un
        # item peut être une simple chaîne (l'énoncé seul, sans solution fournie) -
        # dans ce cas pas de bloc "### Solution" (rien à y mettre, un toggle vide
        # serait pire qu'une absence de toggle).
        parts = ["## Exercices d'application"]
        for item in section.get("items") or []:
            if isinstance(item, str):
                parts.append(f"### Exercice\n\n{item}")
                continue
            parts.append(
                f"### Exercice {item.get('numero', '')} ({item.get('difficulte', '')})\n\n"
                f"{_exercice_application_enonce(item)}",
            )
            parts.append(f"### Solution\n\n{_exercice_application_solution(item)}")
        return "\n\n".join(parts)

    if section_type == "synthese":
        # `items_markdown` arrive tantôt en liste de points à puce, tantôt - comme
        # constaté sur 574 Cours du corpus - en une seule chaîne de synthèse déjà
        # rédigée en prose. Même tolérance str/liste que pour les autres sections
        # ci-dessus : itérer une chaîne caractère par caractère produirait une puce
        # par lettre.
        items = section.get("items_markdown")
        if not items:
            return ""
        body = items if isinstance(items, str) else "\n".join(f"- {item}" for item in items)
        return "## Ce qu'il faut retenir\n\n" + body

    return ""


def compile_cours_from_sections(cours):
    """Aplatit cours.sections_raw (fourni par correction-experte) en Markdown affichable."""
    blocs = [_render_cours_section(cours, section) for section in cours.sections_raw]
    cours.content_markdown = "\n\n---\n\n".join(bloc for bloc in blocs if bloc)
    cours.save(update_fields=["content_markdown", "updated_at"])


def cours_preview_markdown(cours):
    """
    Aperçu public (non-abonné) : accroche + prérequis + règle seulement - assez pour
    comprendre la méthode, jamais l'exemple résolu, les erreurs classiques, les
    exercices ni la synthèse, qui restent le contenu vendu. Dérivé directement de
    sections_raw (pas d'un découpage de content_markdown déjà compilé).
    """
    allowed_types = {"accroche", "prerequis", "regle"}
    blocs = [
        _render_cours_section(cours, section) for section in cours.sections_raw
        if section.get("type") in allowed_types
    ]
    return "\n\n---\n\n".join(bloc for bloc in blocs if bloc)


# --- Découpage structuré des sections (lecture en ligne) -------------------------
#
# Les fonctions ci-dessous produisent, pour chaque type de section, un dict structuré
# plutôt que du Markdown déjà concaténé - pour que le frontend puisse donner à chaque
# type son propre habillage visuel (encadré de règle, étapes numérotées, carte
# erreur/correction...) sans avoir à re-parser du Markdown aplati pour deviner où un
# champ commence et finit (fragilité déjà rencontrée et évitée ailleurs, voir
# lesson_exercises_breakdown ci-dessus). Reproduisent la même tolérance str-vs-objet
# que _render_cours_section (str nue constatée sur une centaine de Cours du corpus) en
# parallèle plutôt qu'en le réutilisant : content_markdown - la seule sortie de
# _render_cours_section - reste la source utilisée telle quelle pour la recherche
# plein texte (catalog.views) et l'audit KaTeX (skill audit-qualite-rendu), donc ce
# chemin déjà éprouvé n'est volontairement pas touché.

def _build_regle_section_data(section):
    variantes = []
    for variante in section.get("variantes") or []:
        if isinstance(variante, str):
            variantes.append({"nom": None, "quand_utiliser": None, "body_markdown": _wrap_bare_formula(variante)})
            continue
        variantes.append({
            "nom": variante.get("nom") or None,
            "quand_utiliser": variante.get("quand_utiliser") or None,
            "body_markdown": variante.get("contenu_markdown", ""),
        })
    formule = section.get("formule_principale")
    return {
        "type": "regle",
        "titre": section.get("titre") or "La règle",
        "body_markdown": section.get("contenu_markdown", ""),
        "formule_markdown": _wrap_bare_formula(formule) if formule else None,
        "variantes": variantes,
    }


def _build_exemple_resolu_section_data(section):
    etapes = []
    for etape in section.get("etapes") or []:
        if isinstance(etape, str):
            etapes.append({
                "numero": None, "action": None, "justification": None,
                "resultat_markdown": None, "body_markdown": etape,
            })
            continue
        etapes.append({
            "numero": etape.get("numero"),
            "action": etape.get("action") or None,
            "justification": etape.get("justification") or None,
            "resultat_markdown": etape.get("resultat_markdown") or None,
            "body_markdown": None,
        })
    return {
        "type": "exemple_resolu",
        "enonce_markdown": section.get("enonce_markdown", ""),
        "etapes": etapes,
        "conclusion_markdown": section.get("conclusion_markdown") or None,
    }


def _build_erreurs_classiques_section_data(section):
    items = []
    for item in section.get("items") or []:
        if isinstance(item, str):
            items.append({"erreur_markdown": item, "pourquoi_faux": None, "correction_markdown": None})
            continue
        items.append({
            "erreur_markdown": item.get("erreur_markdown", ""),
            "pourquoi_faux": item.get("pourquoi_faux") or None,
            "correction_markdown": item.get("correction_markdown") or None,
        })
    return {"type": "erreurs_classiques", "items": items}


def _build_exercices_application_section_data(section):
    items = []
    for item in section.get("items") or []:
        if isinstance(item, str):
            items.append({"numero": None, "difficulte": None, "enonce_markdown": item, "solution_markdown": None})
            continue
        items.append({
            "numero": item.get("numero"),
            "difficulte": item.get("difficulte") or None,
            "enonce_markdown": _exercice_application_enonce(item),
            "solution_markdown": _exercice_application_solution(item) or None,
        })
    return {"type": "exercices_application", "items": items}


def _build_prerequis_section_data(cours, section):
    # "items_markdown" en repli sur "items" - voir la même tolérance dans
    # _render_cours_section ci-dessus (638 Cours du corpus affectés).
    items = []
    for item in section.get("items") or section.get("items_markdown") or []:
        match = _match_cours_by_title(item, cours.pk)
        items.append({"label": item, "cours_slug": match.slug if match else None})
    return {"type": "prerequis", "items": items}


def _build_cours_section_data(cours, section):
    section_type = section.get("type")

    if section_type == "accroche":
        body = section.get("contenu_markdown", "")
        return {"type": "accroche", "body_markdown": body} if body else None
    if section_type == "prerequis":
        return _build_prerequis_section_data(cours, section)
    if section_type == "regle":
        return _build_regle_section_data(section)
    if section_type == "exemple_resolu":
        return _build_exemple_resolu_section_data(section)
    if section_type == "erreurs_classiques":
        return _build_erreurs_classiques_section_data(section)
    if section_type == "exercices_application":
        return _build_exercices_application_section_data(section)
    if section_type == "synthese":
        items = section.get("items_markdown")
        if not items:
            return None
        body = items if isinstance(items, str) else "\n".join(f"- {item}" for item in items)
        return {"type": "synthese", "body_markdown": body}

    return None


def cours_sections_breakdown(cours, allowed_types=None):
    """
    Sections de cours.sections_raw individuellement typées (dicts structurés, pas de
    Markdown concaténé) pour la lecture en ligne - voir Cours.sections_breakdown().

    `allowed_types` restreint les sections retournées avant construction (même filtre
    que cours_preview_markdown, ex. {"accroche", "prerequis", "regle"} pour un aperçu
    non-abonné).
    """
    sections = cours.sections_raw
    if allowed_types is not None:
        sections = [s for s in sections if s.get("type") in allowed_types]
    built = [_build_cours_section_data(cours, section) for section in sections]
    return [section for section in built if section]
