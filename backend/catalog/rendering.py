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
import unicodedata

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
# donné naissance à un Cours - voir annotate_cours_links plus bas.
#
# Le lookahead s'arrête à la première ligne blanche (\n{2,}), pas seulement au
# prochain "###"/"---" : un "Rappel de méthode" n'est en pratique jamais qu'un seul
# paragraphe (même hypothèse que le frontend, voir extractCallouts dans
# frontend/src/lib/markdown.ts). Sans cet arrêt précoce, le bloc capturé s'étendait
# jusqu'au PROCHAIN "### Rappel de méthode" (la sous-question 2 n'étant elle-même
# jamais un titre "###") - le marqueur [COURS_LINK:...] atterrissait alors après le
# corrigé ENTIER de la sous-question 1 (et même après l'énoncé de la 2), au lieu de
# juste après le paragraphe du rappel auquel il appartient. Le lien "Voir le cours
# complet" restait techniquement présent dans le Markdown mais totalement décroché de
# son encadré "Rappel de méthode" - un élève scrollant l'encadré n'y voyait jamais de
# lien juste en dessous (signalé en prod : /cm/epreuves/mathematiques-bepc-2026/lire).
# "m[eé]thode" (pas "méthode" littéral) : même tolérance que le frontend
# (extractCallouts) - correction-experte omet régulièrement l'accent en pratique.
_RAPPEL_BLOCK_RE = re.compile(
    r"###\s*Rappel de m[eé]thode\s*\n+.*?(?=\n{2,}|\n#{1,6}[ \t]|\n---|\Z)",
    re.IGNORECASE | re.DOTALL,
)

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

# Annotation de points par sous-question ("*[2 pts]*", "*[0,5 pt]*") livrée par
# correction-experte comme un PARAGRAPHE À PART, séparé de la question par une ligne
# vide - demande de mise en forme de l'utilisateur (pas un bug de contenu : la donnée
# est correcte, seule sa présentation change) : l'annotation doit apparaître sur la
# MÊME ligne que la question qu'elle chiffre, jamais isolée en dessous. Motif vérifié
# régulier à 100% sur les 139 occurrences du corpus au scan du 2026-08-22 (toujours
# "*[<nombre> pt(s)]*", toujours précédée d'un contenu non vide, jamais en tête absolue
# de texte, jamais sur une Question de type QCM) : fusion purement présentationnelle,
# appliquée au RENDU (voir _render_question_enonce) plutôt qu'au texte source stocké -
# Question.enonce_markdown garde ainsi sa forme d'origine, et toute réingestion future
# du même contenu source produit le même rendu fusionné sans nouveau backfill.
#
# Non ancrée en fin de texte : un seul cas du corpus porte encore un paragraphe après
# l'annotation ("*[0,5 pt]*\n\n*NB : ...*" - mathematiques-bac-c-2018-cameroun), que la
# fusion doit laisser intact APRÈS l'annotation désormais accolée à la question.
_POINTS_ANNOTATION_RE = re.compile(
    r"\n{2,}\s*(\*\[\s*[\d.,]+\s*(?:points?|pts?|pt)\s*\]\*)", re.IGNORECASE,
)


def _merge_inline_points_annotation(text):
    return _POINTS_ANNOTATION_RE.sub(lambda m: f" {m.group(1)}", text)


def _strip_redundant_local_marker(text, numero):
    """
    Retire un marqueur local du type "(b)" en tête du texte quand il redouble
    exactement le dernier segment du `numero` complet déjà affiché en préfixe (ex.
    numero="A.3.b", texte="(b) Étudier...") - correction-experte ne recopie que la
    lettre/le chiffre local hérité de l'énoncé source, jamais le chemin complet de la
    partie, donc sans ceci le lecteur voit le même repère deux fois : une fois dans le
    préfixe compilé ("**A.3.b.**"), une fois dans le texte d'origine ("(b)").

    Le marqueur se présente aussi SANS parenthèses ("ii. ", "b. ") - forme constatée
    sur les épreuves de chimie, où une sous-question numérotée en romain donnait
    "**1.ii.** ii. $CH_3-CO-...$" en lecture. Ce cas échappe à
    _ENONCE_ALREADY_LABELED_RE, qui ne reconnaît qu'une lettre SEULE suivie de sa
    ponctuation ("a.") : "ii." en compte deux, donc le préfixe compilé était bien
    ajouté, par-dessus un marqueur déjà là.

    Cette 2e forme est réservée aux segments alphabétiques (romains, lettres) et exige
    toujours une ponctuation derrière : un segment numérique n'en a pas besoin (il est
    déjà couvert par _ENONCE_ALREADY_LABELED_RE, donc jamais préfixé ni traité ici) et
    l'accepter ici découperait un texte qui commence par un nombre sans rapport
    ("5.2 g de soude..." pour un numero "1.5"). Sans ponctuation obligatoire, un
    numero "1.i" mangerait de la même façon le "i" initial de "ionisation".
    """
    last_segment = numero.rsplit(".", 1)[-1]
    formes = [rf"\(\s*{re.escape(last_segment)}\s*\)[.:]?"]
    if last_segment.isalpha():
        formes.append(rf"{re.escape(last_segment)}\s*[.):]")
    marker_re = re.compile(rf"^\s*(?:{'|'.join(formes)})\s*", re.IGNORECASE)
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

    Une annotation de points isolée sur son propre paragraphe ("*[2 pts]*") est
    d'abord fusionnée sur la ligne de la question qu'elle chiffre - voir
    _merge_inline_points_annotation - avant tout le reste : ni le garde-fou
    `already_labeled` (qui ne regarde que le DÉBUT du texte) ni le retrait du
    marqueur local redondant (qui ne touche pas la fin du texte) n'en sont affectés.
    """
    enonce = _merge_inline_points_annotation(question.enonce_markdown)
    already_labeled = bool(_ENONCE_ALREADY_LABELED_RE.match(enonce))
    texte = (
        f"**{question.numero}.** {_strip_redundant_local_marker(enonce, question.numero)}"
        if numbered and not already_labeled
        else enonce
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


def _render_exercise_block(exercise, nb_labels_a_retirer=None):
    """
    Rend un Exercise validé en bloc Markdown autonome (énoncé + corrigé nettoyé),
    utilisé par compile_lesson_from_exercises(). Pas de "## Exercice N" injecté ici :
    enonce_markdown porte déjà cette numérotation lui-même (ex. "**Exercice 1 (5
    points).**"), telle que transcrite depuis l'épreuve source - l'ajouter en plus
    produirait un doublon visible.

    `nb_labels_a_retirer`, quand fourni par l'appelant (voir _partie_labels_to_strip),
    est le nombre de repères de partie à effacer de la tête de cet énoncé - déjà
    affichés par l'exercice précédent de cette même partie.
    """
    enonce = exercise.enonce_markdown
    if nb_labels_a_retirer:
        enonce = _strip_leading_label(enonce, nb_labels_a_retirer)
    return f"{enonce}\n\n{_clean_exercise_corrige(exercise)}"


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


# Barème en fin de titre - retiré du libellé exposé au frontend, qui reçoit `points`
# comme champ à part. Trois formes vues dans le corpus : parenthésée ("(5 points)",
# "(10 marks)", "(2,5 pts)"), séparée par un tiret ("### Exercice 2 - 3 points", tiret
# -/–/—) ou par deux-points ("**Exercice 2 : 3 points**", **Problème : 11 points**" -
# probatoire-c-e-maths 2003/2005). Un seul groupe capturant par branche : les deux
# formes non parenthésées se rejoignent car la parenthèse fermante n'est pas optionnelle
# côté forme parenthésée (sans ça "Exercice 2 - 3 points)" resterait accepté par erreur).
#
# Le nombre lui-même tolère un "/" optionnel, avec ou sans espace autour ("12/20
# points", "12 / 20 points") : notation "note obtenue/barème". Un "/" peut aussi
# précéder le nombre SEUL, avec ou sans espace après lui ("- /20 points", "- / 02,5
# points" - probatoire-c-1999/-c-e-2013, barème écrit "sur N" sans note chiffrée) :
# sans l'espace optionnel après ce "/" ouvrant, l'ancienne version de ce regex ne
# matchait QUE la forme collée ("/20"), jamais celle avec un espace après le slash -
# le suffixe entier restait alors visible tel quel dans le sommaire (scan corpus du
# 2026-08-22, mathematiques-probatoire-c-1999-cameroun exercices 2/3/4).
#
# La forme parenthésée tolère en plus une note explicative entre le nombre et l'unité
# ("(5,25 (estimation d'après les annotations manuscrites du barème) points)" -
# mathematiques-bac-c-2021-cameroun, barème manuscrit illisible) : un unique niveau de
# parenthèses imbriquées, sans texte parasite avant le nombre ni après l'unité - une
# parenthèse portant aussi une précision NON répétée avant "points" (ex. "(série C
# uniquement, 2,5 points)") continue de ne PAS matcher ici (elle est traitée par
# _POINTS_TRAILING_IN_PAREN_RE plus bas, qui préserve la précision au lieu de la jeter).
_POINTS_NUMBER = r"[\d.,]+(?:\s*/\s*[\d.,]+)?"
_POINTS_SUFFIX_RE = re.compile(
    rf"\s*(?:"
    rf"\(\s*/?\s*({_POINTS_NUMBER})\s*(?:\([^()]*\)\s*)?(?:points?|pts?|marks?)\s*\)"
    rf"|[:\-–—]\s*/?\s*({_POINTS_NUMBER})\s*(?:points?|pts?|marks?)"
    rf")\s*$",
    re.IGNORECASE,
)

# Barème répété au milieu d'un titre à rallonge fusionnant plusieurs parties ("Exercice
# I : ... (6 points). Partie A : ... (3,5 points). Partie B : ...", "Problème (11
# points) - Partie A" - séries physique/maths bac-C-et-E 2009/2012/2013, probatoire
# 2004) : contrairement à _POINTS_SUFFIX_RE (un seul repère, ancré en fin de titre, qui
# alimente aussi `points`), ce nettoyage est global et ne conditionne jamais `points` -
# volontairement restreint aux parenthèses ne contenant RIEN d'autre qu'un nombre et son
# unité, jamais un groupe portant du texte en plus ("(série C uniquement, 2,5 points)"
# reste intact : impossible de savoir si "série C uniquement" reste utile au lecteur une
# fois isolé du reste du titre).
_POINTS_PAREN_ANYWHERE_RE = re.compile(r"\s*\(\s*[\d.,/]+\s*(?:points?|pts?|marks?)\s*\)", re.IGNORECASE)

# Même repère de barème, mais accolé en fin d'une parenthèse qui porte aussi une
# précision utile ("(série C uniquement, 2,5 points)", "(poulie et deux masses, 3
# points)") : _POINTS_PAREN_ANYWHERE_RE ne le retire pas (la parenthèse ne contient pas
# QUE le barème), donc on retire seulement la queue ", N points" - jamais la parenthèse
# entière - pour garder "(série C uniquement)"/"(poulie et deux masses)" au lieu de tout
# jeter. Ancré par lookahead sur la parenthèse fermante : ne touche pas un barème suivi
# d'autre texte avant elle (ex. une répartition en plusieurs points séparés par ";").
_POINTS_TRAILING_IN_PAREN_RE = re.compile(r",?\s*[\d.,/]+\s*(?:points?|pts?|marks?)\s*(?=\))", re.IGNORECASE)

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
    il vit dans une ligne de l'énoncé, soit comme titre Markdown ("### Exercice
    1 (5 points)"), soit comme premier segment en gras ("**Section D: Essay (10
    marks).** Write an essay..." - le reste de la ligne étant déjà du préambule).

    Cette ligne est cherchée dans `enonce_intro_markdown`, et à défaut dans
    `enonce_markdown` : le préambule partagé est souvent absent (aucun des 4 exercices
    de chimie-bac-c-1999 n'en a), la référence vivant alors en tête de la première
    sous-question. Même repli que _repair_missing_exercise_heading côté ingestion.

    Ce n'est pas forcément la première ligne : un exercice qui ouvre une Partie répète
    parfois un sous-titre et/ou un préambule commun (données, formule, figure) ENTRE le
    repère de groupe et sa propre référence ("**A - Activités numériques : 6,5
    points**\n\n*Trois exercices indépendants I, II et III.*\n\nSoient les nombres...\n
    \n**Exercice I (3 pts)**" - mathematiques-bepc-2000/2001/2002-cameroun). On parcourt
    donc toutes les lignes après le repère de groupe et on garde la première qui
    ressemble à une vraie référence, en ignorant sans s'arrêter tout ce qui n'en est pas
    (sous-titre en italique, prose, formule, tableau, image). Une ligne qui n'est ni un
    titre Markdown ni un segment en gras reconnu par _REFERENCE_EXERCICE_RE EST du
    préambule ou de l'énoncé, jamais un repère : si aucune ligne ne correspond, on rend
    un titre vide plutôt qu'une première phrase tronquée en guise d'étiquette, et le
    frontend retombe sur "Exercice {numero}".

    `points` reste prioritairement le champ structuré Exercise.points ; le barème lu
    dans le titre ne sert que de repli, pour le contenu ingéré avant que ce champ ne
    soit systématiquement renseigné.

    Un exercice appartenant à un groupe (voir _exercise_group_paths) porte ce(s)
    repère(s) de groupe EN TÊTE de son intro, avant sa propre référence
    ("**Partie A**\n\n**I. Activités Numériques**\n\n**Exercice 1**") - sans ce
    passage par _leading_label_stack, la première ligne trouvée était le repère de
    GROUPE, pas celui de l'exercice (mathematiques-bepc-2017-blanc : l'exercice 1 se
    voyait étiqueté "Partie A" dans le sommaire au lieu de "Exercice 1").
    """
    source = exercise.enonce_intro_markdown
    if not source.strip():
        source = exercise.enonce_markdown
    _, apres_groupes = _leading_label_stack(source)

    titre = ""
    for raw in source[apres_groupes:].splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            titre = line.lstrip("#").strip()
            break
        if line.startswith("**"):
            fin = line.find("**", 2)
            candidat = line[2:fin].strip() if fin != -1 else ""
            if _REFERENCE_EXERCICE_RE.match(candidat):
                titre = candidat
                break
        # ni titre ni repère de groupe (déjà retirés plus haut) : sous-titre de
        # partie, préambule partagé, formule, figure... - on continue de chercher
        # la référence plus bas plutôt que de conclure à un exercice sans titre.

    titre = titre.rstrip(" .:")
    points = exercise.points.strip()
    match = _POINTS_SUFFIX_RE.search(titre)
    if match:
        titre = titre[: match.start()].rstrip(" .:")
        points = points or match.group(1) or match.group(2)

    titre = _POINTS_PAREN_ANYWHERE_RE.sub("", titre)
    titre = _POINTS_TRAILING_IN_PAREN_RE.sub("", titre).strip()

    return titre, points


# correction-experte recopie parfois le repère de partie ("**A. Évaluation des
# ressources (10 points)**", "**PARTIE II : ...**") à l'identique en tête de CHAQUE
# exercice d'une même partie plutôt que du seul premier (repéré sur 8 épreuves du
# corpus au scan du 2026-08-18, ex. mathematiques-bepc-2024 : les exercices 1 à 3
# ouvrent tous les trois sur "PARTIE A : ÉVALUATION DES RESSOURCES - ACTIVITÉS
# NUMÉRIQUES."). Légitime dans enonce_intro_markdown de CHAQUE exercice concerné - ce
# repère porte sur l'exercice ENTIER, pas sur une seule sous-question (contrairement à
# l'hypothèse de ingestion_repairs._flag_part_headers_in_intro, qui ne s'applique pas
# ici) - mais redondant une fois plusieurs exercices affichés à la suite : seule sa
# première occurrence doit rester visible. Même détection qu'à l'ingestion (voir
# ingestion_repairs._INTRO_PART_HEADER_RE / _BARE_LETTERED_PART_HEADER_RE), dupliquée
# ici plutôt qu'importée : rendering.py ne dépend pas d'ingestion_repairs (préoccupations
# distinctes, voir docstring de tête de ce fichier). Séparateur point OU tiret (simple/
# demi-cadratin/cadratin, espace autour optionnel) : le corpus SVT/Espagnol écrit aussi
# bien "I. Évaluation..." que "I - Évaluation..."/"III- Exploitation...".
_PARTIE_LABEL_RE = re.compile(r"\A\s*(?:Partie\s+\S|[IVX]{1,4}\s*[.\-–—]|[A-Z]\s*[.\-–—]\s)", re.IGNORECASE)

# Repère de groupe "matière" à l'état brut, sans le mot "Partie" ni numérotation :
# une épreuve combinant plusieurs matières (ex. Physique-Chimie, probatoire-A) ouvre
# chaque bloc sur le seul nom de la matière ("**CHIMIE / 10 points**", puis plus loin
# "**PHYSIQUE / 10 points**" - chimie-probatoire-a-2019-a4-bilingue). Distinct de
# _PARTIE_LABEL_RE (qui exige "Partie"/un chiffre romain/une lettre seule) : ici le
# repère est un ou plusieurs mots ENTIÈREMENT en majuscules, sans autre repère
# reconnaissable ("Exercice"/"Problème"/"Partie"/"Section" - exclus explicitement,
# sans quoi "EXERCICE 1 : ..." rejoindrait à tort la pile de groupe au lieu de rester
# la référence propre de l'exercice). Scan corpus du 2026-08-22 : un seul cas dans
# toute la base, mais la forme est simple et le risque de faux positif faible (le
# filtre MAJUSCULES SEULES exclut déjà toute phrase ordinaire).
_BARE_MATIERE_EXCLUDE_RE = re.compile(r"\A(?:Exercice|Probl[eè]me|Partie|Section)\b", re.IGNORECASE)
_BARE_MATIERE_LABEL_RE = re.compile(
    r"\A[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇŒ][A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇŒ' \-]{1,40}?(?:\s*[/:]\s*[\d.,]+\s*(?:points?|pts?|marks?))?\Z"
)


def _is_bare_matiere_label(contenu):
    return bool(_BARE_MATIERE_LABEL_RE.match(contenu)) and not _BARE_MATIERE_EXCLUDE_RE.match(contenu)


def _is_group_label(contenu):
    """Repère de groupe (Partie/romain/lettré OU nom de matière nu) - voir
    _PARTIE_LABEL_RE et _BARE_MATIERE_LABEL_RE ci-dessus. Sert de condition d'arrêt à
    _leading_label_stack : seuls ces repères rejoignent la pile, jamais la propre
    référence de l'exercice."""
    return bool(_PARTIE_LABEL_RE.match(contenu)) or _is_bare_matiere_label(contenu)


# Titre Markdown ou premier segment en gras en tête d'un texte, quoi qu'il porte
# ensuite sur la même ligne (correction-experte enchaîne parfois directement le
# contenu après le repère, sans saut de ligne - ex. "**PARTIE A : ... NUMÉRIQUES.** On
# considère le nombre..."). Même principe que _REFERENCE_EXERCICE_RE ci-dessus,
# factorisé ici pour être réutilisable exercice par exercice plutôt qu'à l'échelle
# d'une seule ligne déjà isolée.
_LEADING_LABEL_RE = re.compile(r"\A\s*(?:(#{1,4}[^\n]*)|\*\*([^\n*]+?)\*\*)")


def _leading_label(text):
    """(repère, position juste après lui dans `text`) - (None, 0) si `text` ne
    commence pas par un titre Markdown ou un segment en gras."""
    match = _LEADING_LABEL_RE.match(text or "")
    if not match:
        return None, 0
    contenu = match.group(1) or match.group(2)
    if match.group(1):
        contenu = contenu.lstrip("#").strip()
    return contenu.strip(), match.end()


def _leading_label_stack(text):
    """
    (pile de repères de partie, position juste après le dernier) en tête de `text` -
    ([], 0) si `text` ne commence par aucun. Un exercice imbrique parfois PLUSIEURS
    repères d'affilée ("**Partie A : Évaluation des ressources (10 points)**" puis,
    juste en dessous, "**I - Évaluation des savoirs (4 points)**" avant le contenu
    propre à l'exercice) - voir _partie_labels_to_strip, qui compare deux piles plutôt
    que deux repères isolés. S'arrête au premier segment en tête qui n'est PAS un
    repère de partie (_PARTIE_LABEL_RE) : la propre référence de l'exercice
    ("**Exercice 2 : ...**") ne rejoint donc jamais la pile.
    """
    pile = []
    reste = text or ""
    while True:
        contenu, fin = _leading_label(reste)
        if not contenu or not _is_group_label(contenu):
            break
        pile.append(contenu)
        reste = reste[fin:].lstrip()
    return pile, len(text or "") - len(reste)


def _partie_labels_to_strip(exercises):
    """
    {exercise.pk: nombre de repères de tête à retirer} pour chaque Exercise de
    `exercises` (déjà triés par exercise_sort_key) dont enonce_intro_markdown répète
    EXACTEMENT, position par position, le début de la pile de repères déjà portée par
    l'exercice précédent - dict vide si aucun exercice ne répète son prédécesseur. Deux
    piles ne partagent que leur PRÉFIXE commun : dès qu'un niveau diffère (ex. bascule
    de "PARTIE A"/"I -" à "PARTIE A"/"II -", ou de "PARTIE A" à "PARTIE B"), ce niveau
    et tous les suivants restent affichés et deviennent la nouvelle pile active - voir
    _leading_label_stack/_PARTIE_LABEL_RE.
    """
    a_retirer = {}
    pile_active = []
    for exercise in exercises:
        pile, _ = _leading_label_stack(exercise.enonce_intro_markdown)
        commun = 0
        while commun < len(pile) and commun < len(pile_active) and pile[commun] == pile_active[commun]:
            commun += 1
        if commun:
            a_retirer[exercise.pk] = commun
        pile_active = pile_active[:commun] + pile[commun:]
    return a_retirer


# Sous-familles de repère de groupe, pour ordonner leur PROFONDEUR relative (voir
# _exercise_group_paths) - "Partie X" et la forme lettrée courte ("A. Évaluation...")
# désignent le même niveau (voir commentaire de _BARE_LETTERED_PART_HEADER_RE côté
# ingestion_repairs : simple alternative d'écriture, jamais deux niveaux concurrents
# dans une même épreuve), d'où un seul "kind" pour les deux. Un chiffre romain forme
# la seule autre famille observée dans le corpus.
_KIND_ROMAN_RE = re.compile(r"\A\s*[IVX]{1,4}\s*[.\-–—]", re.IGNORECASE)
_KIND_PARTIE_RE = re.compile(r"\A\s*(?:Partie\s+\S|[A-Z]\s*[.\-–—]\s)", re.IGNORECASE)


def _label_kind(contenu):
    """Famille d'un repère de groupe ("roman", "partie", "matiere") - sert à établir
    sa profondeur relative dans _exercise_group_paths, jamais son texte affiché."""
    if _KIND_ROMAN_RE.match(contenu):
        return "roman"
    if _KIND_PARTIE_RE.match(contenu):
        return "partie"
    return "matiere"


def _exercise_group_paths(exercises):
    """
    {exercise.pk: [repère_niveau_0, repère_niveau_1, ...]} - la pile de groupes
    (Partie/section romaine/matière) à laquelle appartient chaque Exercise de
    `exercises` (déjà triés par exercise_sort_key), pour construire un sommaire
    hiérarchique côté frontend (voir EpreuveSommaire). [] pour un exercice qui
    n'appartient à aucun groupe détecté.

    Contrairement à _partie_labels_to_strip (qui ne sert qu'à dédupliquer un repère
    répété À L'IDENTIQUE), cette fonction doit reconstituer la pile ENTIÈRE d'un
    exercice qui ne restate qu'un SEUL niveau ("**II - Évaluation des savoir-faire**"
    ne redit pas "Partie A" au-dessus, pourtant l'exercice en fait toujours partie -
    voir sciences-de-la-vie-et-de-la-terre-bepc-2018/2025/2026). La comparaison
    PAR POSITION de _partie_labels_to_strip ne suffit donc pas ici : un exercice qui
    ne déclare qu'un repère de niveau "roman" doit remplacer UNIQUEMENT le niveau
    "roman" de la pile active, sans toucher au niveau "partie" au-dessus - même quand
    ce niveau "roman" occupait la position 1 pour un exercice précédent, mais la
    position 0 pour un autre (l'ORDRE Partie/romain varie d'une épreuve à l'autre :
    "Partie A > I." pour mathematiques-bepc-2017-blanc, mais "I. > Partie A" pour le
    format APC des épreuves SVT/BEPC ci-dessus - voir _label_kind, jamais une
    profondeur fixée globalement par famille).

    La profondeur de chaque famille ("roman"/"partie"/"matiere") est donc déterminée
    UNE FOIS par épreuve, à partir du premier repère empilé plusieurs niveaux à la
    fois (seule pile qui révèle sans ambiguïté quel niveau est le plus extérieur) -
    un exercice qui ne déclare qu'un seul repère à la fois ne fait ensuite que
    remplacer le niveau correspondant à sa famille, quelle que soit sa position dans
    SA PROPRE pile.
    """
    profondeur_par_famille = {}
    piles = []
    for exercise in exercises:
        pile, _ = _leading_label_stack(exercise.enonce_intro_markdown)
        piles.append(pile)
        for repere in pile:
            famille = _label_kind(repere)
            if famille not in profondeur_par_famille:
                profondeur_par_famille[famille] = len(profondeur_par_famille)

    result = {}
    pile_active = {}
    for exercise, pile in zip(exercises, piles):
        for repere in pile:
            profondeur = profondeur_par_famille[_label_kind(repere)]
            for niveau in [n for n in pile_active if n >= profondeur]:
                del pile_active[niveau]
            pile_active[profondeur] = repere
        result[exercise.pk] = [pile_active[niveau] for niveau in sorted(pile_active)]
    return result


def _fallback_group_paths_if_needed(exercises):
    """{exercise.pk: [...]} via _exercise_group_paths (analyse de texte), calculé
    seulement si au moins un exercice de `exercises` n'a pas encore de Exercise.groupes
    renseigné en base - {} sans jamais analyser le texte quand toute l'épreuve vient
    d'une ingestion postérieure à l'introduction de ce champ. Un exercice avec
    Exercise.groupes non vide n'indexe jamais le résultat (voir les appelants), donc {}
    est un résultat sûr même si aucun exercice n'a de repère détectable par regex."""
    if all(exercise.groupes for exercise in exercises):
        return {}
    return _exercise_group_paths(exercises)


# Un repère de groupe porte souvent un sous-titre et/ou un barème qui n'apportent rien
# à un en-tête de navigation ("Partie A : Évaluation Ressources : 10 points" - le
# barème total de la partie, sans intérêt une fois affiché comme simple séparateur de
# section ; "CHIMIE / 10 points" de même). Réutilise le même nettoyage de barème que
# _exercise_titre_et_points, puis tronque au premier ":"/"/" qui introduit ce
# sous-titre - UNIQUEMENT quand il y en a un (un repère romain sans sous-titre distinct
# comme "I. Activités Numériques" n'a ni ':' ni '/' et reste donc intact).
_GROUP_LABEL_SUBTITLE_RE = re.compile(r"\s*[:/]")


def _simplify_group_label(contenu):
    """Libellé compact d'un repère de groupe pour le sommaire de navigation - voir
    _exercise_group_paths. Le texte complet reste visible dans le corps de l'épreuve
    (jamais modifié par cette fonction, purement cosmétique côté sommaire)."""
    label = contenu.strip()
    match = _POINTS_SUFFIX_RE.search(label)
    if match:
        label = label[: match.start()].rstrip(" .:")
    label = _POINTS_PAREN_ANYWHERE_RE.sub("", label).strip()
    label = _POINTS_TRAILING_IN_PAREN_RE.sub("", label).strip()
    sous_titre = _GROUP_LABEL_SUBTITLE_RE.search(label)
    if sous_titre:
        label = label[: sous_titre.start()].strip()
    return label or contenu.strip()


def _strip_leading_label(text, nb_labels):
    """`text` sans ses `nb_labels` premiers repères de partie de tête (voir
    _leading_label_stack) ni les lignes vides qui les séparent du reste - `text`
    inchangé si un repère attendu ne s'y retrouve pas (garde-fou, ne devrait pas
    arriver vu les appelants : `nb_labels` vient toujours de _partie_labels_to_strip,
    calculé sur ce même `text`)."""
    reste = text or ""
    for _ in range(nb_labels or 0):
        contenu, fin = _leading_label(reste)
        if not contenu or not _PARTIE_LABEL_RE.match(contenu):
            return text
        reste = reste[fin:].lstrip()
    return reste


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

    `groupes` alimente le même sommaire d'un niveau supplémentaire : la pile de
    repères (Partie/section romaine/matière) à laquelle appartient l'exercice, déjà
    simplifiée pour l'affichage. Vient de Exercise.groupes (renseigné dès l'ingestion
    depuis le JSON source de correction-experte) quand ce champ est non vide, sinon
    reconstruit par analyse de texte en repli - voir _fallback_group_paths_if_needed/
    _exercise_group_paths/_simplify_group_label. [] pour la grande majorité des
    épreuves (aucun groupe déclaré ni détecté), auquel cas le frontend retombe sur un
    sommaire plat, inchangé.

    Liste vide pour une Lesson sans Exercise (FICHE, ou tout contenu non sectionné) -
    le frontend retombe alors sur content_markdown tel quel.
    """
    exercises = sorted(lesson.exercises.filter(statut=StatutContenu.VALIDE), key=exercise_sort_key)
    a_retirer = _partie_labels_to_strip(exercises)
    groupes_par_exercice = _fallback_group_paths_if_needed(exercises)
    result = []
    for exercise in exercises:
        intro = exercise.enonce_intro_markdown
        enonce = exercise.enonce_markdown
        if intro and enonce.startswith(f"{intro}\n\n"):
            enonce = enonce[len(intro) + 2 :]
        if exercise.pk in a_retirer:
            intro = _strip_leading_label(intro, a_retirer[exercise.pk])
        titre, points = _exercise_titre_et_points(exercise)
        groupes = exercise.groupes or groupes_par_exercice.get(exercise.pk, [])
        result.append({
            "numero_exercice": exercise.numero_exercice,
            "titre": titre,
            "points": points,
            "groupes": [_simplify_group_label(g) for g in groupes],
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

    `groupes` : voir lesson_exercises_breakdown, même mécanique, exposée aussi côté
    sujet public pour que la fiche (non-abonné) affiche le même sommaire hiérarchique
    que le lecteur (voir EpreuveDetailPage.tsx).
    """
    exercises = sorted(
        lesson.exercises.filter(statut=StatutContenu.VALIDE), key=exercise_sort_key,
    )
    a_retirer = _partie_labels_to_strip(exercises)
    groupes_par_exercice = _fallback_group_paths_if_needed(exercises)
    result = []
    for exercise in exercises:
        titre, points = _exercise_titre_et_points(exercise)
        enonce_markdown = exercise.enonce_markdown
        if exercise.pk in a_retirer:
            enonce_markdown = _strip_leading_label(enonce_markdown, a_retirer[exercise.pk])
        groupes = exercise.groupes or groupes_par_exercice.get(exercise.pk, [])
        result.append({
            "numero_exercice": exercise.numero_exercice,
            "titre": titre,
            "points": points,
            "groupes": [_simplify_group_label(g) for g in groupes],
            "enonce_markdown": enonce_markdown,
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

    a_retirer = _partie_labels_to_strip(exercises)
    blocs = [
        _strip_leading_label(exercise.enonce_markdown, a_retirer[exercise.pk])
        if exercise.pk in a_retirer else exercise.enonce_markdown
        for exercise in exercises
    ]
    if lesson.introduction_markdown:
        blocs.insert(0, lesson.introduction_markdown)
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
    a_retirer = _partie_labels_to_strip(exercises)

    blocs = []
    if lesson.introduction_markdown:
        blocs.append(lesson.introduction_markdown)
    themes = set(lesson.themes.all())
    mots_cles = set(lesson.mots_cles_recherche.all())

    for exercise in exercises:
        blocs.append(_render_exercise_block(exercise, a_retirer.get(exercise.pk)))
        themes.update(exercise.themes.all())
        mots_cles.update(exercise.mots_cles_recherche.all())

    lesson.content_markdown = "\n\n---\n\n".join(blocs)
    lesson.save(update_fields=["content_markdown", "updated_at"])
    lesson.themes.set(themes)
    lesson.mots_cles_recherche.set(mots_cles)


# Connecteurs français qui ne trompent jamais : un vrai fragment de LaTeX brut sans
# backslash ("U = mV²/(2|q|)", "AE/AB = AF/AC") n'en contient aucun. Volontairement
# sans accent (comparé à un texte lui-même désaccentué par _strip_accents ci-dessous)
# pour n'avoir à écrire chaque mot qu'une fois.
_PROSE_CONNECTOR_WORDS = frozenset({
    "puis", "avec", "dans", "pour", "avant", "apres", "jamais", "toujours",
    "soit", "donc", "comme", "alors", "quand", "meme", "deja", "plutot",
    "sans", "entre", "chaque", "tout", "tous", "toute", "toutes", "ainsi",
    "lorsque", "celui", "celle", "ceux", "depuis",
})
# Un "mot" au sens de ce détecteur : 3 lettres consécutives ou plus - exclut les
# variables isolées ("x", "AB") et les nombres, sans exclure les mots réels courts.
_WORDY_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ]{3,}")


def _strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def _looks_like_prose(text):
    """
    Distingue une phrase en français/anglais glissée par erreur dans un champ
    "formule" (jamais du LaTeX - ex. "Multiplication/division d'abord, puis
    addition/soustraction au même dénominateur", constaté en prod sur le Cours
    "calculer-une-expression-fractionnaire...") d'un fragment de LaTeX brut
    légitime sans backslash (ex. "U = mV²/(2|q|)", "AE/AB = AF/AC = EF/BC").
    Seulement appelée par _wrap_bare_formula sur un texte déjà sans "$" - un texte
    qui contient un backslash est toujours réputé volontaire, jamais reclassé ici
    même s'il combine par ailleurs beaucoup de mots (ex. un "\\text{...}" protège
    déjà la prose qu'il contient du mode math, c'est la façon correcte de mélanger
    les deux : \"n_0 \\quad\\text{soit : je pose } 0\").

    Mesuré sur tout le corpus de Cours (876 sections "La règle" affectées avant ce
    correctif, sur 2786 avec formule_principale/variantes) : ce critère distingue
    correctement les deux cas sur un large échantillon manuel, sans prétendre à la
    perfection - un fragment de LaTeX brut à la fois long et très verbal (rare)
    pourrait encore être classé prose à tort, et l'inverse pour un fragment très
    court. Aucun moyen plus fiable : KaTeX ne lève ni erreur ni couleur rouge sur
    ce genre de contenu (il "parse" avec succès, juste avec un résultat visuel
    faux), donc l'audit-qualite-rendu ne peut pas trancher ça à la place de ce
    détecteur - voir la mémoire projet, "RappelDeMethode contenu_markdown vide" et
    apparentés pour d'autres bugs de rendu de la même famille.
    """
    if "\\" in text:
        return False
    wordy = _WORDY_TOKEN_RE.findall(text)
    if len(wordy) >= 6:
        return True
    if len(wordy) < 4:
        return False
    normalized = _strip_accents(text.lower())
    return any(
        re.search(rf"(?<![a-z]){re.escape(word)}(?![a-z])", normalized)
        for word in _PROSE_CONNECTOR_WORDS
    )


def _wrap_bare_formula(text):
    # `formule_principale`/`variantes` (str) arrivent tantôt en LaTeX brut sans
    # aucun `$` (besoin d'être enveloppé en display math pour KaTeX), tantôt déjà
    # comme du markdown avec ses propres spans `$...$` mêlés à du texte français
    # (ex. "$(\\ln|x|)'=\\dfrac1x$ pour tout $x\\in\\mathbb R^*$ ; ..." - constaté
    # sur le Cours "fonction inverse et logarithme"). Envelopper ce second cas en
    # `$$...$$` casse KaTeX ($$$ triple, ou du texte français lu comme du LaTeX
    # display) : on ne l'enveloppe que si aucun `$` n'est déjà présent.
    #
    # Troisième cas, découvert après coup (voir _looks_like_prose) : ni "$" ni
    # backslash, mais aucun LaTeX non plus - une phrase entière glissée dans ce
    # champ par erreur. L'envelopper en $$...$$ collerait tous les mots ensemble
    # (le mode math de KaTeX ignore les espaces hors commande) sans jamais lever
    # d'erreur - on la laisse alors telle quelle, affichée comme texte normal dans
    # le même encadré "formule" plutôt que comme une fausse formule illisible.
    if "$" in text or _looks_like_prose(text):
        return text
    return f"$${text}$$"


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
