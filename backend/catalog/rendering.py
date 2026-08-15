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
# apparaît sur l'épreuve source - un titre en gras ("**Partie A**"), sa numérotation
# d'origine ("1. ", "2) "), ou une lettre suivie de ":"/"." ("A : «...»") - voir
# _render_question_enonce, qui ne préfixe le `numero` interne que si le texte
# n'affiche déjà aucun repère de ce genre, pour ne jamais doubler l'information.
_ENONCE_ALREADY_LABELED_RE = re.compile(r"^\s*(\*\*|\d+\s*[.)]\s|[A-Za-z]\s*[.):])")


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
    """
    already_labeled = bool(_ENONCE_ALREADY_LABELED_RE.match(question.enonce_markdown))
    texte = (
        f"**{question.numero}.** {_strip_redundant_local_marker(question.enonce_markdown, question.numero)}"
        if numbered and not already_labeled
        else question.enonce_markdown
    )
    if question.type_reponse == TypeReponse.QCM and question.choix:
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


def _annotate_cours_links(corrige, exercise):
    """
    Insère un marqueur `[COURS_LINK:<id>]` juste après chaque bloc "### Rappel de
    méthode" dont le RappelDeMethode correspondant a donné naissance à un Cours -
    le frontend le détecte pour afficher un lien "Voir le cours complet" sur le
    callout. La correspondance entre un bloc du texte et son RappelDeMethode se
    fait par inclusion du texte exact extrait à l'ingestion (contenu_markdown),
    seule donnée fiable puisque le Markdown compilé ne porte pas de FK.

    Un même bloc peut correspondre à plusieurs RappelDeMethode : la compétence
    fusionne parfois plusieurs sous-questions sous un unique "### Rappel de méthode"
    plutôt que d'en écrire un par sous-question - dans ce cas tous les cours
    associés sont insérés à la suite du bloc.

    Il arrive aussi que `contenu_markdown` soit une reformulation plutôt qu'une
    citation exacte du corrigé (l'IA ne respecte pas toujours cette consigne) : le
    rappel ne matche alors aucun bloc. Son marqueur est ajouté en fin d'exercice
    plutôt que d'être perdu silencieusement - imprécis, mais le lien reste visible.
    """
    rappels = [r for r in exercise.rappels_de_methode.all() if r.cours_id and r.contenu_markdown.strip()]
    if not rappels:
        return corrige

    injected_ids = set()

    def _inject(match):
        block = match.group(0)
        cours_ids = [r.cours_id for r in rappels if r.contenu_markdown.strip() in block]
        if not cours_ids:
            return block
        injected_ids.update(cours_ids)
        markers = "\n\n".join(f"[COURS_LINK:{cid}]" for cid in cours_ids)
        # Le lookahead de _RAPPEL_BLOCK_RE ne consomme qu'un seul \n avant la
        # frontière suivante (### / ---) : la ligne blanche d'origine perd donc une
        # de ses deux newlines dans le texte restant non capturé. Sans ce \n final,
        # un "---" juste après transformerait le marqueur en titre Setext (<h2>)
        # au lieu de rester un simple paragraphe.
        return f"{block.rstrip()}\n\n{markers}\n"

    corrige = _RAPPEL_BLOCK_RE.sub(_inject, corrige)

    remaining_ids = [r.cours_id for r in rappels if r.cours_id not in injected_ids]
    if remaining_ids:
        markers = "\n\n".join(f"[COURS_LINK:{cid}]" for cid in remaining_ids)
        corrige = f"{corrige.rstrip()}\n\n{markers}"

    return corrige


def _render_exercise_block(exercise):
    """
    Rend un Exercise validé en bloc Markdown autonome (énoncé + corrigé nettoyé),
    partagé par compile_lesson_from_exercises() et lesson_preview_markdown(). Pas de
    "## Exercice N" injecté ici : enonce_markdown porte déjà cette numérotation
    lui-même (ex. "**Exercice 1 (5 points).**"), telle que transcrite depuis
    l'épreuve source - l'ajouter en plus produirait un doublon visible.
    """
    # Si l'IA a quand même inclus une fiche d'identité par exercice (ancien format
    # bloc de code, ou nouveau format tableau - oubli de consigne dans les deux cas),
    # on la retire : ces informations vivent uniquement dans Lesson.header_info().
    corrige = _FICHE_IDENTITE_RE.sub("", exercise.corrige_markdown, count=1).lstrip()
    corrige = _FICHE_IDENTITE_TABLE_RE.sub("", corrige, count=1).lstrip()
    corrige = _EXERCICE_HEADING_RE.sub("### Corrigé\n\n", corrige, count=1)
    corrige = _RAPPEL_ORPHELIN_RE.sub("", corrige)
    corrige = _annotate_cours_links(corrige, exercise)
    return f"{exercise.enonce_markdown}\n\n{corrige}"


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
    exercises = lesson.exercises.filter(statut=StatutContenu.VALIDE).order_by("numero_exercice")
    if not exercises.exists():
        return lesson.content_markdown

    blocs = [exercise.enonce_markdown for exercise in exercises]
    return "\n\n---\n\n".join(blocs)


def compile_lesson_from_exercises(lesson):
    """
    Agrège les Exercise validés (rattachés via leur FK) dans ce Lesson :
    concatène le contenu Markdown et fusionne thèmes/mots-clés sans doublon.
    N'inclut jamais un Exercise encore en BROUILLON ou REJETE.
    """
    exercises = (
        lesson.exercises.filter(statut=StatutContenu.VALIDE)
        .order_by("numero_exercice")
        .prefetch_related("themes", "mots_cles_recherche", "rappels_de_methode")
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


def _render_cours_section(cours, section):
    section_type = section.get("type")

    if section_type == "accroche":
        return section.get("contenu_markdown", "")

    if section_type == "prerequis":
        # Lie chaque prérequis au Cours correspondant quand son titre matche
        # exactement (insensible à la casse) - best-effort : un intitulé de
        # prérequis générique ("Calcul littéral") ne matchera pas toujours un
        # titre de Cours (plus spécifique), auquel cas il reste un texte simple.
        items = section.get("items") or []
        lines = []
        for item in items:
            match = (
                Cours.objects.filter(titre__iexact=item.strip(), statut=StatutContenu.VALIDE)
                .exclude(pk=cours.pk)
                .first()
            )
            lines.append(f"- [{item}](COURS_REF:{match.id})" if match else f"- {item}")
        return "## Prérequis\n\n" + "\n".join(lines)

    if section_type == "regle":
        parts = [f"## {section.get('titre') or 'La règle'}", section.get("contenu_markdown", "")]
        if section.get("formule_principale"):
            parts.append(f"$${section['formule_principale']}$$")
        for variante in section.get("variantes") or []:
            # correction-experte produit tantôt un objet {nom, quand_utiliser,
            # contenu_markdown}, tantôt - pour une simple variante de formule,
            # sans sous-titre ni précision d'usage - une chaîne nue de LaTeX brut
            # (ex. une règle "ln x>k" à côté de ses variantes "ln x<k", "ln x≥k"...,
            # constaté sans délimiteurs $$, comme formule_principale ci-dessus avant
            # d'être enveloppée). Les deux sont un contenu légitime de la
            # compétence, pas une erreur à rejeter.
            if isinstance(variante, str):
                parts.append(f"$${variante}$$")
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
        items = section.get("items_markdown") or []
        return "## Ce qu'il faut retenir\n\n" + "\n".join(f"- {item}" for item in items)

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
