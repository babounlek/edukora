import random
import unicodedata
from collections import Counter, defaultdict
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from access.models import ExerciceFait, LectureProgress
from catalog.models import Cours, Difficulte, Lesson, Origine, Question, StatutContenu, Subject, Tag
from programme.models import Module, Savoir

# Miroir volontaire de lib/maitrise.ts SEUIL_MAITRISE (frontend) - resume_parcours a
# besoin de classer chaque savoir pour produire un histogramme (voir sa docstring), ce
# que construire_parcours ne fait jamais (il ne renvoie que des taux bruts, le
# classement restant une décision d'affichage). Aucun partage de constante possible
# entre les deux bases de code : si l'une change, l'autre doit suivre à la main.
SEUIL_MAITRISE = 70

# construire_parcours : un Savoir peut être couvert par plusieurs Cours distincts (un
# Tag est partagé par plusieurs Cours, un Savoir porte plusieurs Tags) - jusqu'à
# plusieurs dizaines en pratique quand un tag est trop générique. Plafond d'affichage,
# pas une vérité pédagogique ("il n'y a que 3 cours utiles") : au-delà, c'est un signal
# de tagging à corriger côté données, pas une raison de charger une liste illimitée
# côté page.
PARCOURS_COURS_PAR_SAVOIR_MAX = 3

# construire_parcours : matières où le classement des thèmes réels par fréquence
# d'examen remplace le Module→Savoir officiel (voir
# project_parcours_par_frequence_conception_2026_09_14) - décision arrêtée par
# pilotage concret sur le corpus, pas un choix arbitraire : Français/Philo/
# Histoire-Géo/Anglais testent une méthodologie sur des sujets renouvelés, pas un
# stock fixe de notions récurrentes (BEPC Français : 94 tags, fréquence max 4,
# aucun thème n'atteindrait SEUIL_MINIMUM_THEMES_PARCOURS). PHYSIQUE_CHIMIE et
# PHYSIQUE_CHIMIE_TECH sont la même matière (4e/3e) sous deux codes historiques.
SUBJECTS_PARCOURS_PAR_FREQUENCE = {
    "MATHS", "PHYSIQUE", "CHIMIE", "SVT", "PHYSIQUE_CHIMIE", "PHYSIQUE_CHIMIE_TECH",
    # Filière technique (TI) : signal de fréquence traité comme pour les sciences.
    "PROGRAMMATION", "SYSTEMES_INFORMATION", "RESEAUX_SECURITE",
}

# En dessous, le signal de fréquence n'est pas fiable - même seuil et même
# justification que catalog.views.SEUIL_MINIMUM_THEMES_FREQUENTS (mesuré sur SVT BAC
# D Cameroun : 5 épreuves en base, occurrence max 2, "tombé 2 fois sur 5" sonnerait
# comme une fausse promesse). Sous ce seuil, construire_parcours retombe sur
# l'affichage Module→Savoir habituel plutôt que d'afficher un classement peu fiable.
SEUIL_MINIMUM_THEMES_PARCOURS = 8

# Filière TI : corpus mince (1 à 6 épreuves par matière et cursus en base), le seuil
# général les renverrait tous au Module→Savoir. On classe quand même les thèmes, sans
# plancher d'occurrences (un thème vu une fois reste utile à réviser sur si peu d'épreuves).
SUBJECTS_CORPUS_MINCE_PARCOURS = {"PROGRAMMATION", "SYSTEMES_INFORMATION", "RESEAUX_SECURITE"}

# Fusion mécanique haute confiance (variantes grammaticales/de casse d'une même
# notion, jamais des familles parent-enfant - voir la règle de granularité
# "séparée" dans project_parcours_par_frequence_conception_2026_09_14) : variante ->
# forme canonique choisie. Tag.name est unique globalement (voir catalog.Tag), donc
# ces deux formes sont bien deux lignes distinctes en base à regrouper ici, jamais
# une redondance à corriger côté données.
TAGS_ALIAS_PARCOURS_FREQUENCE = {
    "identité remarquable": "identités remarquables",
    "vecteur": "vecteurs",
    "effectif": "effectifs",
    "fréquences": "fréquence",
    "système de deux équations": "système d'équations",
    "milieu d'un segment": "milieu",
    "mesure d'un angle": "mesure d'angle",
    "perpendicularité": "droites perpendiculaires",
    "théorème de Pythagore": "Pythagore",
    "équation produit": "équation produit nul",
    "règle du produit nul": "équation produit nul",
    "caryotype": "Caryotype",
    # Maths Terminale (BAC C/D) : mêmes notions écrites de deux façons (jamais
    # parent-enfant - "dérivée d'un produit" reste distinct de "dérivée").
    "dérivation": "dérivée",
    "représentation graphique": "tracé de courbe",
    "monotonie": "sens de variation",
    "variations": "sens de variation",
    "calcul d'aire": "aires",
    "tangente à une courbe": "Tangente",
    "intégrale": "calcul intégral",
    "noyau d'un endomorphisme": "noyau",
    "vecteurs colinéaires": "colinéarité",
    "convergence de suite": "convergence",
    "distance entre deux points": "distance",
}

# Tags-poubelle à exclure du classement (jamais à fusionner : un nom de discipline
# utilisé comme tag ne désigne aucune notion précise à réviser) - mesuré sur PCT où
# "technologie" ressortait #3 du classement sans rien dire d'utile.
TAGS_BLOCKLIST_PARCOURS_FREQUENCE = {"technologie", "physique", "chimie", "mécanique", "électricité", "svt", "Cameroun"}

# Un thème qui n'est jamais retombé qu'une seule fois n'est justement pas un thème
# qui "revient" - mesuré sur BEPC Maths : sur 476 thèmes candidats après filtrage,
# 246 (plus de la moitié) n'apparaissent que dans une seule épreuve. Sans ce
# plancher, la liste se noierait dans du bruit et perdrait la promesse même du
# classement par fréquence.
PARCOURS_FREQUENCE_OCCURRENCES_MIN = 2

# Le plancher fixe de 2 laisse 250 à 380 thèmes sur les gros corpus de Maths (BAC C :
# 382, Probatoire C : 295), une liste qu'aucun élève ne parcourt jusqu'au bout. On
# relève donc le plancher, d'une occurrence à la fois, jusqu'à ramener la liste à
# ce plafond : la règle ne touche que les listes trop longues (BAC C : plancher 5,
# 101 thèmes ; Probatoire C : plancher 5, 99 thèmes) et laisse intacts les corpus
# déjà courts (BAC A, TI : plancher 2).
PARCOURS_FREQUENCE_THEMES_MAX = 130

from .models import (
    CompetenceItem, ModeQuiz, ObjectifMatiere, OrigineSeance, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare,
    RevisionSchedule,
    SeanceJournaliere, StatutSeance,
)

# Répartition cible pour un test de niveau (mode DIAGNOSTIC) : couvrir tout le spectre
# de difficulté plutôt que de refléter la composition du catalogue (qui peut être
# majoritairement "moyenne" par exemple, ce qui donnerait un diagnostic peu discriminant).
_REPARTITION_DIAGNOSTIC = {
    Difficulte.FAIBLE: 0.4,
    Difficulte.MOYENNE: 0.4,
    Difficulte.ELEVEE: 0.2,
}

# Poids appliqué en mode PRATIQUE à un thème jamais pratiqué (ou à un utilisateur sans
# aucun historique) - ni favorisé ni pénalisé, un tirage qui doit se comporter comme un
# tirage uniforme classique tant qu'il n'y a rien à corriger.
_POIDS_THEME_NEUTRE = 1.0

# Paliers de la file de révision espacée (RevisionSchedule) : un thème raté revient
# demain, puis - à chaque réussite suivante - dans 3 jours, puis 7 jours, avant de
# graduer hors de la file. Trois paliers seulement (pas cinq/six comme un Leitner
# classique papier) : suffisant pour couvrir la fenêtre utile avant un examen, sans
# complexifier l'UI d'une file qui doit rester consultable d'un coup d'œil.
LEITNER_INTERVALS_JOURS = [1, 3, 7]


def _items_eligibles(cursus, subject=None, theme=None, savoir=None):
    """
    Source unique du Mode Quiz depuis la bascule : CompetenceItem, jamais
    catalog.Question. Contrairement à l'ancien pool (Question extraite d'un Exercise,
    filtrée après coup par Question.references_missing_figure faute de mieux), un
    CompetenceItem est écrit dès l'origine pour se suffire seul - aucun filtre de
    rattrapage n'est nécessaire ici : statut=VALIDE est la seule porte d'entrée.

    `savoir` (distinct de `theme`) : filtre par savoir officiel plutôt que par un Tag
    précis - un Savoir peut porter plusieurs Tags (voir programme.Savoir.tags), donc
    filtrer sur `theme__savoir_officiel` couvre tous les CompetenceItem du savoir
    plutôt que de forcer l'appelant à deviner lequel de ces Tags interroger. Sert le
    parcours (voir construire_parcours) : une étape s'y lance par Savoir, jamais par
    Tag brut.
    """
    qs = CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus).distinct()
    if subject:
        qs = qs.filter(subject=subject)
    if theme:
        qs = qs.filter(theme=theme)
    if savoir:
        qs = qs.filter(theme__savoir_officiel=savoir)
    return list(qs)


def _selection_stratifiee_par_difficulte(items, n):
    """
    Pioche selon _REPARTITION_DIAGNOSTIC. Si une tranche de difficulté n'a pas assez
    d'items disponibles, complète avec les items restants des autres tranches plutôt
    que de renvoyer moins de n items - un test de niveau incomplet est moins utile
    qu'un test légèrement moins équilibré.
    """
    by_difficulte = {}
    for item in items:
        by_difficulte.setdefault(item.difficulte_estimee, []).append(item)
    for bucket in by_difficulte.values():
        random.shuffle(bucket)

    selection = []
    for difficulte, part in _REPARTITION_DIAGNOSTIC.items():
        cible = round(n * part)
        bucket = by_difficulte.get(difficulte, [])
        selection.extend(bucket[:cible])
        by_difficulte[difficulte] = bucket[cible:]

    if len(selection) < n:
        restants = [item for bucket in by_difficulte.values() for item in bucket]
        random.shuffle(restants)
        selection.extend(restants[: n - len(selection)])

    return selection[:n]


def _poids_par_theme(user, cursus):
    """
    Poids par thème (id -> poids) favorisant, en mode PRATIQUE, les thèmes où
    l'utilisateur échoue le plus - à partir de son historique de réponses sur CE cursus
    uniquement (jamais tous cursus confondus : une faiblesse en Maths BAC C n'a pas de
    sens à reporter sur un autre cursus). Un thème absent du résultat (jamais pratiqué)
    doit être traité comme neutre par l'appelant (voir _POIDS_THEME_NEUTRE), pas comme
    exclu : ne rien avoir essayé n'est pas une faiblesse.

    Se limite aux réponses sourcées depuis un CompetenceItem : lui seul porte un thème
    unique et sans ambiguïté (contrairement à catalog.Question.themes, M2M, et de toute
    façon plus jamais tiré par generer_session depuis la bascule - voir QuizQuestion).
    """
    reponses = (
        QuizAnswer.objects.filter(
            quiz_question__session__user=user,
            quiz_question__session__cursus=cursus,
            quiz_question__competence_item__isnull=False,
        )
        .select_related("quiz_question__competence_item")
    )

    stats = {}
    for reponse in reponses:
        theme_id = reponse.quiz_question.competence_item.theme_id
        s = stats.setdefault(theme_id, {"total": 0, "reussies": 0})
        s["total"] += 1
        if reponse.est_correcte:
            s["reussies"] += 1

    poids = {}
    for theme_id, s in stats.items():
        taux_reussite = s["reussies"] / s["total"]
        # 1.7 à 0% de réussite, 0.3 à 100% - jamais 0 (un thème déjà maîtrisé reste
        # théoriquement tirable, la répétition espacée y trouvera sa place plus tard)
        # et jamais démesuré (un thème très en échec ne doit pas monopoliser toute la
        # séance au détriment de la couverture du reste du cursus).
        poids[theme_id] = 1.7 - 1.4 * taux_reussite
    return poids


def _selection_ponderee_par_theme(items, poids_par_theme, n):
    """
    Tirage sans remise pondéré (algorithme A-ES d'Efraimidis-Spirakis) : chaque item
    reçoit une clé aléatoire élevée à la puissance 1/poids de son thème, puis on garde
    les n clés les plus hautes. Une repondération continue plutôt qu'un simple "toujours
    les pires thèmes d'abord", qui figerait la séance sur les mêmes questions d'une
    session à l'autre.
    """
    cles = [
        (random.random() ** (1 / poids_par_theme.get(item.theme_id, _POIDS_THEME_NEUTRE)), item)
        for item in items
    ]
    cles.sort(key=lambda paire: paire[0], reverse=True)
    return [item for _, item in cles[:n]]


def generer_session(user, cursus, mode, subject=None, theme=None, savoir=None, n=10):
    """
    Sélectionne jusqu'à n CompetenceItem et crée une QuizSession. Lève ValueError si
    aucun item n'est éligible pour ces critères (pas encore de banque générée pour
    cette compétence/ce cursus) - à la vue de traduire en réponse HTTP appropriée. Ce
    ValueError est attendu tant que la banque CompetenceItem n'est pas encore peuplée
    pour un cursus/thème donné - ce n'est pas un bug, voir la discussion de bascule.

    mode=DIAGNOSTIC : répartition stratifiée par difficulté (voir
    _selection_stratifiee_par_difficulte). mode=PRATIQUE : tirage pondéré par thème
    selon le taux d'échec de l'utilisateur sur ce cursus (voir _poids_par_theme) - sans
    historique (première session, ou thème jamais pratiqué), retombe sur un poids
    neutre équivalent à l'ancien tirage uniforme.

    `savoir` : voir _items_eligibles - filtre alternatif à `theme`, utilisé pour
    lancer un quiz depuis une étape du parcours (voir construire_parcours).
    """
    items = _items_eligibles(cursus, subject=subject, theme=theme, savoir=savoir)
    if not items:
        raise ValueError("Aucune question disponible pour ces critères.")

    if mode == ModeQuiz.DIAGNOSTIC:
        selection = _selection_stratifiee_par_difficulte(items, n)
    else:
        poids_par_theme = _poids_par_theme(user, cursus)
        selection = _selection_ponderee_par_theme(items, poids_par_theme, n)

    session = QuizSession.objects.create(user=user, cursus=cursus, subject=subject, theme=theme, mode=mode)
    QuizQuestion.objects.bulk_create([
        QuizQuestion(session=session, competence_item=item, ordre=ordre)
        for ordre, item in enumerate(selection, start=1)
    ])
    return session


def enregistrer_resultat_pour_revision(user, cursus, subject, theme, correcte):
    """
    Fait avancer/reculer l'échéance de révision d'un thème (voir RevisionSchedule)
    selon le résultat d'une réponse de Quiz - seul appelant : quiz.views.answer_question,
    uniquement pour une réponse sourcée depuis un CompetenceItem (thème unique et sans
    ambiguïté, même restriction que _poids_par_theme).

    Échec : (ré)ouvre le suivi de ce thème au palier 0 (J+1), même s'il n'était pas
    encore suivi - un thème raté doit toujours revenir demain, qu'il s'agisse d'une
    première alerte ou d'une rechute après un palier plus avancé.

    Réussite : ne crée jamais de suivi pour un thème qui n'a jamais posé problème (rien
    à corriger) ; fait avancer d'un palier un thème déjà suivi - au dernier palier, une
    réussite de plus gradue le thème hors de la file plutôt que de le boucler
    indéfiniment.
    """
    if not correcte:
        RevisionSchedule.objects.update_or_create(
            user=user, cursus=cursus, theme=theme,
            defaults={
                "subject": subject,
                "palier": 0,
                "due_at": timezone.localdate() + timedelta(days=LEITNER_INTERVALS_JOURS[0]),
            },
        )
        return

    schedule = RevisionSchedule.objects.filter(user=user, cursus=cursus, theme=theme).first()
    if not schedule:
        return

    if schedule.palier >= len(LEITNER_INTERVALS_JOURS) - 1:
        schedule.delete()
        return

    schedule.palier += 1
    schedule.due_at = timezone.localdate() + timedelta(days=LEITNER_INTERVALS_JOURS[schedule.palier])
    schedule.save(update_fields=["palier", "due_at", "updated_at"])


def revisions_dues(user, cursus=None):
    """
    Thèmes dont l'échéance de révision (voir RevisionSchedule) est aujourd'hui ou
    dépassée, du plus en retard au moins en retard (voir RevisionSchedule.Meta.ordering)
    - le plus urgent d'abord.
    """
    qs = (
        RevisionSchedule.objects.filter(user=user, due_at__lte=timezone.localdate())
        .select_related("cursus__series", "subject", "theme")
    )
    if cursus:
        qs = qs.filter(cursus=cursus)
    return qs


def maitrise_par_theme(user, cursus=None):
    """
    Vue d'ensemble de la maîtrise de l'utilisateur, thème par thème, à partir de la
    TOTALITÉ de son historique de réponses - contrairement à RevisionSchedule, qui ne
    suit que les thèmes actuellement en difficulté (et disparaît une fois un thème
    gradué, voir enregistrer_resultat_pour_revision), cette vue doit aussi montrer ce
    qui est déjà maîtrisé : "je progresse" est aussi motivant que "voilà mes lacunes".
    Alimente le tableau "Ma maîtrise" de la page Compte.

    Même restriction que _poids_par_theme/enregistrer_resultat_pour_revision : se
    limite aux réponses sourcées depuis un CompetenceItem (thème unique et sans
    ambiguïté). Triée du taux de réussite le plus faible au plus élevé - ce qui mérite
    le plus d'attention en premier, cohérent avec la file de révision.
    """
    reponses = (
        QuizAnswer.objects.filter(quiz_question__session__user=user, quiz_question__competence_item__isnull=False)
        .select_related("quiz_question__competence_item__theme", "quiz_question__competence_item__subject")
    )
    if cursus:
        reponses = reponses.filter(quiz_question__session__cursus=cursus)

    stats = {}
    for reponse in reponses:
        item = reponse.quiz_question.competence_item
        cle = (item.subject_id, item.theme_id)
        s = stats.setdefault(cle, {
            "subject_id": item.subject_id,
            "subject_label": item.subject.label,
            "theme_id": item.theme_id,
            "theme": item.theme.name,
            "total": 0,
            "reussies": 0,
        })
        s["total"] += 1
        if reponse.est_correcte:
            s["reussies"] += 1

    en_revision_qs = RevisionSchedule.objects.filter(user=user)
    if cursus:
        en_revision_qs = en_revision_qs.filter(cursus=cursus)
    themes_en_revision = set(en_revision_qs.values_list("theme_id", flat=True))

    for s in stats.values():
        s["taux"] = round(100 * s["reussies"] / s["total"])
        s["en_revision"] = s["theme_id"] in themes_en_revision

    return sorted(stats.values(), key=lambda s: s["taux"])


def maitrise_par_savoir(user, cursus=None):
    """
    Comme maitrise_par_theme, mais agrégée par programme.Savoir plutôt que par Tag -
    seule alimentation interne de construire_parcours (jamais exposée telle quelle en
    API, contrairement à maitrise_par_theme). Un Savoir peut porter plusieurs Tags
    (voir Savoir.tags, et le cas réel documenté dans _cours_pour_theme côté vues) :
    ce regroupement les fusionne, plutôt que de forcer l'appelant à recomposer un score
    par savoir à partir de plusieurs entrées de maitrise_par_theme. Seules les réponses
    dont le thème est déjà rattaché à un Savoir officiel comptent ici - un thème sans
    rattachement n'a, par construction, aucun savoir à créditer (même situation que
    _poids_par_theme/maitrise_par_theme pour l'historique catalog.Question, exclu pour
    la même raison de granularité fiable).

    Renvoie {savoir_id: taux} plutôt qu'une liste triée : construire_parcours doit
    pouvoir chercher le taux d'un savoir précis pendant qu'il parcourt le programme
    dans SON propre ordre (Module.ordre/Savoir.ordre), pas dans un ordre de tri par
    faiblesse qui n'a de sens que pour maitrise_par_theme.
    """
    reponses = (
        QuizAnswer.objects.filter(
            quiz_question__session__user=user,
            quiz_question__competence_item__isnull=False,
            quiz_question__competence_item__theme__savoir_officiel__isnull=False,
        )
        .select_related("quiz_question__competence_item__theme")
    )
    if cursus:
        reponses = reponses.filter(quiz_question__session__cursus=cursus)

    stats = {}
    for reponse in reponses:
        savoir_id = reponse.quiz_question.competence_item.theme.savoir_officiel_id
        s = stats.setdefault(savoir_id, {"total": 0, "reussies": 0})
        s["total"] += 1
        if reponse.est_correcte:
            s["reussies"] += 1

    return {savoir_id: round(100 * s["reussies"] / s["total"]) for savoir_id, s in stats.items()}


def _normaliser_pour_recherche(texte):
    """Minuscules sans accents, pour comparer un nom de thème à un titre de cours."""
    decompose = unicodedata.normalize("NFD", texte.lower())
    return "".join(ch for ch in decompose if unicodedata.category(ch) != "Mn")


def construire_parcours_par_frequence(user, cursus, subject):
    """
    Variante de construire_parcours pour SUBJECTS_PARCOURS_PAR_FREQUENCE : au lieu du
    programme officiel (Module→Savoir), classe les thèmes réels (catalog.Tag) par
    fréquence d'apparition dans les épreuves officielles du (cursus, subject) - voir
    project_parcours_par_frequence_conception_2026_09_14 pour la conception complète
    et son schéma de liaison validé.

    Renvoie None si le corpus est trop mince pour un classement fiable
    (SEUIL_MINIMUM_THEMES_PARCOURS) - à charge de l'appelant de retomber sur le
    Module→Savoir habituel plutôt que d'afficher un classement qui n'aurait pas de
    sens. Renvoie sinon une liste de dicts au même format qu'un
    module["savoirs"] de construire_parcours (id/numero/intitule/taux/en_revision/
    a_lu_le_cours/has_quiz/cours), avec des clés additives (theme_id, savoir_label,
    nb_epreuves, frequence_pct) qu'un consommateur du format existant peut ignorer -
    resume_parcours n'a besoin de rien de plus pour continuer à fonctionner sans
    modification.

    `Tag.savoir_officiel` est délibérément ignoré comme clé de jointure - démontré
    non fiable (90% des tags les plus fréquents pointent hors de la plage du
    cursus). Le pont retenu ici est entièrement basé sur des champs déjà fiables :
    Question.savoir_officiel (agrégé par thème, pour l'étiquette informative
    uniquement), la lignée Cours←RappelDeMethode←Exercise←Lesson.cursus (pour les
    cours), et CompetenceItem.theme+cursus (pour le quiz, déjà correctement scopé).

    Une seule requête par étape (jamais une boucle par thème candidat, qui serait un
    N+1 sur 400-600 tags par matière) : chaque étape calcule sa donnée pour TOUS les
    thèmes candidats d'un coup, puis les résultats sont recombinés en Python par
    groupe d'alias.
    """
    mince = subject.code in SUBJECTS_CORPUS_MINCE_PARCOURS
    lessons = Lesson.objects.filter(statut=StatutContenu.VALIDE, subject=subject, cursus=cursus)
    if not mince:
        # Corpus mince (TI) : les blancs/établissements comptent, sinon le Probatoire n'a aucune épreuve officielle.
        lessons = lessons.filter(origine=Origine.OFFICIEL)
    lessons = lessons.distinct()
    nb_sessions = lessons.count()
    if nb_sessions < (1 if mince else SEUIL_MINIMUM_THEMES_PARCOURS):
        return None

    tags_bruts = list(
        Tag.objects.filter(questions_as_theme__exercise__lesson__in=lessons)
        .exclude(name__in=TAGS_BLOCKLIST_PARCOURS_FREQUENCE),
    )
    if not tags_bruts:
        return []

    # Regroupement par alias : un groupe = une forme canonique + l'ensemble des ids
    # de Tag qui y renvoient (lui-même si le tag n'a pas d'alias connu).
    groupes = {}
    for tag in tags_bruts:
        canonique = TAGS_ALIAS_PARCOURS_FREQUENCE.get(tag.name, tag.name)
        groupe = groupes.setdefault(canonique, {"nom": canonique, "tag_ids": set()})
        groupe["tag_ids"].add(tag.id)
    tous_tag_ids = {tid for g in groupes.values() for tid in g["tag_ids"]}

    # Fréquence par groupe = nb de Lesson distinctes couvertes par l'UNION de ses
    # tags (jamais la somme des fréquences individuelles, qui compterait deux fois
    # une épreuve mobilisant à la fois "vecteur" et "vecteurs"). Une seule requête
    # (lesson_id, tag_id) pour tous les tags candidats, recombinée en Python.
    tags_par_lesson = defaultdict(set)
    for lesson_id, tag_id in (
        Lesson.objects.filter(pk__in=lessons.values("pk"), exercises__questions__themes__id__in=tous_tag_ids)
        .values_list("id", "exercises__questions__themes__id")
        .distinct()
    ):
        tags_par_lesson[lesson_id].add(tag_id)
    for groupe in groupes.values():
        groupe["nb_epreuves"] = sum(
            1 for tags_de_la_lesson in tags_par_lesson.values() if tags_de_la_lesson & groupe["tag_ids"]
        )

    # Étiquette de savoir informative (jamais une clé de jointure) : le savoir
    # dominant parmi les Question.savoir_officiel déjà rattachées à ce thème sur ce
    # (cursus, subject) - voir campagne de rattachement. Un thème sans savoir
    # dominant (transversal ou hors référentiel, ex. calorimétrie) reste affiché
    # sans étiquette plutôt que d'être exclu.
    savoir_counts_par_tag = defaultdict(Counter)
    for tag_id, savoir_id in (
        Question.objects.filter(
            themes__id__in=tous_tag_ids, exercise__lesson__in=lessons, savoir_officiel__isnull=False,
        )
        .values_list("themes__id", "savoir_officiel_id")
    ):
        savoir_counts_par_tag[tag_id][savoir_id] += 1
    for groupe in groupes.values():
        compteur = Counter()
        for tag_id in groupe["tag_ids"]:
            compteur.update(savoir_counts_par_tag.get(tag_id, {}))
        groupe["savoir_id"] = compteur.most_common(1)[0][0] if compteur else None
    savoirs_par_id = {
        s.id: s for s in Savoir.objects.filter(id__in={g["savoir_id"] for g in groupes.values() if g["savoir_id"]})
    }

    # Thème -> Quiz : direct et déjà fiable (voir docstring ci-dessus).
    tags_avec_quiz = set(
        CompetenceItem.objects.filter(
            theme_id__in=tous_tag_ids, cursus=cursus, statut=StatutContenu.VALIDE,
        ).values_list("theme_id", flat=True),
    )

    # Thème -> Cours : Cours.cursus est vide en pratique (voir la conception) - le
    # vrai signal est la lignée vers l'Exercise source de son RappelDeMethode.
    cours_par_tag_id = defaultdict(list)
    for cours in (
        Cours.objects.visibles()
        .filter(subject=subject, tags__id__in=tous_tag_ids, rappels_source__exercise__lesson__cursus=cursus)
        .annotate(nb_rappels=Count("rappels_source", distinct=True))
        .prefetch_related("tags")
        # Les seuls champs lus plus bas. Sans only(), le DISTINCT comparait aussi
        # sections_raw (le cours entier) ligne à ligne : ~185 ms sur les Maths de
        # Terminale, soit la moitié du temps de toute la page Ma progression.
        .only("id", "slug", "titre", "sous_theme")
        .distinct()
    ):
        for tag in cours.tags.all():
            if tag.id in tous_tag_ids:
                cours_par_tag_id[tag.id].append(cours)

    # Progression de l'utilisateur, par tag brut (avant regroupement par alias) -
    # même source que maitrise_par_savoir (QuizAnswer via CompetenceItem), mais
    # gardée par Tag ici puisque le thème EST le tag, pas un Savoir.
    stats_par_tag = defaultdict(lambda: {"total": 0, "reussies": 0})
    for reponse in (
        QuizAnswer.objects.filter(
            quiz_question__session__user=user,
            quiz_question__session__cursus=cursus,
            quiz_question__competence_item__theme_id__in=tous_tag_ids,
        )
        .select_related("quiz_question__competence_item")
    ):
        s = stats_par_tag[reponse.quiz_question.competence_item.theme_id]
        s["total"] += 1
        if reponse.est_correcte:
            s["reussies"] += 1

    tags_en_revision = set(
        RevisionSchedule.objects.filter(user=user, cursus=cursus, theme_id__in=tous_tag_ids)
        .values_list("theme_id", flat=True),
    )
    tags_lus = set(
        LectureProgress.objects.filter(user=user, cours__tags__id__in=tous_tag_ids)
        .values_list("cours__tags__id", flat=True),
    )

    plancher = 1 if mince else PARCOURS_FREQUENCE_OCCURRENCES_MIN
    if not mince:
        while (
            plancher < nb_sessions
            and sum(1 for g in groupes.values() if g["nb_epreuves"] >= plancher) > PARCOURS_FREQUENCE_THEMES_MAX
        ):
            plancher += 1

    resultat = []
    for groupe in groupes.values():
        if groupe["nb_epreuves"] < plancher:
            continue
        tag_ids = groupe["tag_ids"]

        # Même dédoublonnage par sous_theme + plafond que construire_parcours -
        # voir PARCOURS_COURS_PAR_SAVOIR_MAX.
        candidats, vus = [], set()
        for tid in tag_ids:
            for c in cours_par_tag_id.get(tid, []):
                if c.id not in vus:
                    vus.add(c.id)
                    candidats.append(c)
        # Du plus pertinent au moins pertinent (jusqu'ici : ordre des id, donc "ellipse"
        # proposait un cours de probabilités) : le thème apparaît dans le titre, puis
        # le cours sert le plus d'exercices de ce cursus, puis il est le plus ciblé
        # (peu de tags), puis id pour la stabilité.
        nom_normalise = _normaliser_pour_recherche(groupe["nom"])
        candidats.sort(key=lambda c: (
            nom_normalise not in _normaliser_pour_recherche(f"{c.titre} {c.sous_theme or ''}"),
            -c.nb_rappels,
            len(c.tags.all()),
            c.id,
        ))
        cours_finaux, sous_themes_vus = [], set()
        for c in candidats:
            cle = c.sous_theme or c.slug
            if cle in sous_themes_vus:
                continue
            sous_themes_vus.add(cle)
            cours_finaux.append(c)
            if len(cours_finaux) >= PARCOURS_COURS_PAR_SAVOIR_MAX:
                break

        total = sum(stats_par_tag[tid]["total"] for tid in tag_ids if tid in stats_par_tag)
        reussies = sum(stats_par_tag[tid]["reussies"] for tid in tag_ids if tid in stats_par_tag)
        savoir = savoirs_par_id.get(groupe["savoir_id"])
        theme_id = min(tag_ids)

        resultat.append({
            "id": theme_id,
            "theme_id": theme_id,
            "numero": "",
            "intitule": groupe["nom"],
            "savoir_label": savoir.intitule if savoir else None,
            "nb_epreuves": groupe["nb_epreuves"],
            "frequence_pct": round(100 * groupe["nb_epreuves"] / nb_sessions),
            "taux": round(100 * reussies / total) if total else None,
            "en_revision": bool(tag_ids & tags_en_revision),
            "a_lu_le_cours": bool(tag_ids & tags_lus),
            "has_quiz": bool(tag_ids & tags_avec_quiz),
            "cours": [{"slug": c.slug, "titre": c.titre, "sous_theme": c.sous_theme} for c in cours_finaux],
        })

    resultat.sort(key=lambda d: (-d["nb_epreuves"], d["intitule"]))
    for index, item in enumerate(resultat):
        item["numero"] = str(index + 1)
    return resultat


def construire_parcours(user, cursus, subject):
    """
    Vue séquencée du programme officiel (voir programme.Module/Savoir) pour un
    cursus/matière donnés, enrichie savoir par savoir avec la progression réelle de
    l'utilisateur - alimente GET /quiz/parcours/. Contrairement à maitrise_par_theme/
    revisions_dues (vues plates, sans notion d'ordre), c'est la structure du
    programme officiel qui organise l'affichage (Module.ordre, Savoir.ordre, déjà
    fiables - voir programme.Module) ; la progression de l'élève ne fait qu'annoter
    chaque étape.

    Ne filtre RIEN sur le contenu disponible : un Savoir sans Cours ni CompetenceItem
    apparaît quand même (`cours=[]`, `has_quiz=False`) plutôt que d'être masqué - la
    structure du programme doit rester visible même incomplète (cas du BEPC
    aujourd'hui), pas seulement les savoirs déjà couverts. C'est au frontend de
    griser une étape sans contenu, jamais à cette fonction de la faire disparaître.

    Pour SUBJECTS_PARCOURS_PAR_FREQUENCE, remplace entièrement cette vue par un
    classement des thèmes réels par fréquence d'examen (voir
    construire_parcours_par_frequence) - repris dans un unique pseudo-module pour
    que resume_parcours (qui ne lit que module["savoirs"]) continue de fonctionner
    sans changement. Retombe sur le Module→Savoir habituel si le corpus est encore
    trop mince pour un classement fiable.
    """
    if subject.code in SUBJECTS_PARCOURS_PAR_FREQUENCE:
        themes = construire_parcours_par_frequence(user, cursus, subject)
        if themes is not None:
            return [{
                "numero": "",
                "titre": "Les thèmes qui reviennent le plus à l'examen",
                "savoirs": themes,
            }]

    taux_par_savoir = maitrise_par_savoir(user, cursus=cursus)
    savoir_ids_en_revision = set(
        RevisionSchedule.objects.filter(user=user, cursus=cursus, theme__savoir_officiel__isnull=False)
        .values_list("theme__savoir_officiel_id", flat=True)
    )
    savoir_ids_lus = set(
        LectureProgress.objects.filter(user=user, cours__tags__savoir_officiel__isnull=False)
        .values_list("cours__tags__savoir_officiel_id", flat=True)
    )
    savoir_ids_avec_quiz = set(
        CompetenceItem.objects.filter(
            statut=StatutContenu.VALIDE, cursus=cursus, theme__savoir_officiel__isnull=False,
        )
        .values_list("theme__savoir_officiel_id", flat=True)
    )

    modules = Module.objects.filter(subject=subject, cursus=cursus).prefetch_related("savoirs").distinct()

    parcours = []
    for module in modules:
        savoirs_payload = []
        for savoir in module.savoirs.all():
            # Tous les Cours publiés qui couvrent ce savoir (voir Cours.tags ->
            # Tag.savoir_officiel) - même relation que le niveau 2 de
            # quiz.views._cours_pour_theme, ici interrogée directement par
            # Savoir plutôt que déduite d'un CompetenceItem particulier. Plusieurs
            # cours distincts sont légitimes (voir PARCOURS_COURS_PAR_SAVOIR_MAX) :
            # l'assimilation d'un savoir peut demander plus d'une leçon.
            #
            # Fenêtre de candidats plus large que le plafond final : deux Cours
            # distincts partagent parfois le même sous_theme (ex. deux exercices
            # différents sur "Nombres complexes - similitudes") - les afficher tels
            # quels produirait deux boutons visuellement identiques mais menant à des
            # pages différentes. On sur-récupère un peu pour dédupliquer sur
            # sous_theme avant de plafonner, sans pour autant charger tous les
            # candidats (jusqu'à plusieurs centaines dans les cas de tag trop
            # générique - voir la note sur PARCOURS_COURS_PAR_SAVOIR_MAX).
            candidats_bruts = (
                Cours.objects.visibles()
                .filter(subject=subject, tags__savoir_officiel=savoir)
                .filter(Q(cursus=cursus) | Q(cursus__isnull=True))
                # Voir construire_parcours_par_frequence : sans only(), le DISTINCT
                # compare aussi le contenu entier de chaque cours.
                .only("id", "slug", "titre", "sous_theme")
                .distinct()
                .order_by("id")[: PARCOURS_COURS_PAR_SAVOIR_MAX * 3]
            )
            cours_candidats = []
            sous_themes_vus = set()
            for c in candidats_bruts:
                # Clé de dédoublonnage = sous_theme quand renseigné (c'est lui qui
                # s'affiche) ; à défaut le slug, pour ne jamais fusionner deux cours
                # sans sous_theme entre eux (ils n'ont alors rien de visuellement
                # identique à dédupliquer).
                cle = c.sous_theme or c.slug
                if cle in sous_themes_vus:
                    continue
                sous_themes_vus.add(cle)
                cours_candidats.append(c)
                if len(cours_candidats) >= PARCOURS_COURS_PAR_SAVOIR_MAX:
                    break
            savoirs_payload.append({
                "id": savoir.id,
                "numero": savoir.numero,
                "intitule": savoir.intitule,
                # None (jamais tenté) distingué de 0% (tenté, en échec) - la vue
                # d'ensemble doit savoir laquelle des deux situations elle affiche.
                "taux": taux_par_savoir.get(savoir.id),
                "en_revision": savoir.id in savoir_ids_en_revision,
                "a_lu_le_cours": savoir.id in savoir_ids_lus,
                "has_quiz": savoir.id in savoir_ids_avec_quiz,
                "cours": [
                    {"slug": c.slug, "titre": c.titre, "sous_theme": c.sous_theme} for c in cours_candidats
                ],
            })
        parcours.append({"numero": module.numero, "titre": module.titre, "savoirs": savoirs_payload})
    return parcours


def resume_parcours(user, cursus):
    """
    Une ligne par matière ayant un programme officiel pour ce cursus (voir
    programme.Module.cursus), réduite à un histogramme de statuts par savoir -
    alimente le tableau de bord GET /quiz/parcours/resume/, point d'entrée
    "toutes tes matières" au-dessus du détail séquencé (construire_parcours).

    Réutilise construire_parcours tel quel plutôt que de dupliquer sa logique de
    jointure Module/Savoir/maîtrise/Cours : au volume actuel (quelques dizaines de
    savoirs par matière, une poignée de matières par cursus), le coût redondant est
    négligeable et ça élimine tout risque que le résumé raconte une histoire
    différente du détail sur lequel il renvoie.

    N'exclut aucune matière, même sans aucun contenu encore rattaché (`sans_contenu`
    == `total`) - même principe que construire_parcours pour un savoir isolé : la
    structure du programme reste visible, c'est au frontend de l'afficher en retrait.
    """
    subjects = (
        Subject.objects.filter(modules_officiels__cursus=cursus).distinct().order_by("label")
    )

    resume = []
    for subject in subjects:
        savoirs = [s for module in construire_parcours(user, cursus, subject) for s in module["savoirs"]]
        # Un seul bucket par savoir, jamais un chevauchement à retrancher après coup -
        # chaque condition est testée dans cet ordre de priorité précis (ex. un savoir
        # sans contenu ne compte jamais pour "à réviser" même si une donnée historique
        # incohérente le laissait croire).
        #
        # "en_cours" (taux connu, pas encore maîtrisé, pas dans la file de révision)
        # est distinct de "a_decouvrir" (jamais pratiqué du tout) - sans cette
        # distinction, un thème pourtant travaillé disparaissait de l'agrégat : le
        # taux `s["taux"]` est une moyenne historique qui ne s'efface jamais, alors
        # que RevisionSchedule suit la Leitner récente et GRADUE (supprime la ligne)
        # dès qu'une série de réussites récentes l'a fait remonter les paliers -
        # même si la moyenne à vie reste sous SEUIL_MAITRISE. Un thème raté plusieurs
        # fois puis enfin maîtrisé récemment se retrouvait donc compté comme
        # "à découvrir", exactement comme un thème jamais ouvert - constaté sur un
        # compte réel (35 réponses, 54 % de moyenne, gradué hors révision : ni
        # maîtrisé, ni en révision, ni même visible).
        compteurs = {"maitrises": 0, "en_revision": 0, "en_cours": 0, "a_decouvrir": 0, "sans_contenu": 0}
        for s in savoirs:
            if not s["has_quiz"] and not s["cours"]:
                compteurs["sans_contenu"] += 1
            elif s["taux"] is not None and s["taux"] >= SEUIL_MAITRISE:
                compteurs["maitrises"] += 1
            elif s["en_revision"]:
                compteurs["en_revision"] += 1
            elif s["taux"] is not None:
                compteurs["en_cours"] += 1
            else:
                compteurs["a_decouvrir"] += 1
        resume.append({
            "subject_id": subject.id,
            "subject_code": subject.code,
            "subject_label": subject.label,
            "total": len(savoirs),
            **compteurs,
        })
    return resume


# --- Séance du jour -----------------------------------------------------------------
#
# Voir quiz.models.SeanceJournaliere pour le stockage, et plan_du_jour ci-dessous pour
# l'ordre de priorité. Rien ici ne calcule de contenu neuf : tout réutilise le moteur
# déjà en place (révision espacée, parcours par fréquence, banque de quiz) - la valeur
# ajoutée est de n'en sortir QU'UNE chose à faire, aujourd'hui.

# Budget de temps, jamais de volume : un élève tient un engagement de durée ("25
# minutes ce soir"), pas un engagement de quantité ("12 questions"). Les étapes
# s'empilent jusqu'à ce budget, et la dernière qui déborderait est laissée de côté
# plutôt que tronquée.
BUDGET_SEANCE_MINUTES = 25

# Durées indicatives par type d'étape - assumées approximatives : mesurer le temps
# réellement passé demanderait un suivi de lecture qu'on n'a pas (LectureProgress ne
# stocke aucune position, voir sa docstring), et une fausse précision ("7 min") ne
# vaudrait pas mieux qu'un ordre de grandeur honnête.
DUREE_ETAPE_MINUTES = {"cours": 8, "exercice": 12, "quiz": 5}

# Au-delà, une lecture n'est plus "en cours" : c'est une lecture d'avant-hier qu'on
# proposerait de reprendre alors que l'élève est passé à autre chose.
FENETRE_LECTURE_EN_COURS_HEURES = 48

# Nombre de séances terminées récentes qui bloquent une matière. Cinq jours de maths
# d'affilée, c'est un abandon programmé - la rotation n'est pas un confort, c'est ce
# qui fait tenir sur des mois.
ROTATION_MATIERES_RECENTES = 2

# Taille du quiz de fin de séance : de quoi vérifier qu'on a compris, jamais une
# session complète (10 items) qui doublerait à elle seule le budget de la séance.
QUIZ_FIN_DE_SEANCE_N = 5

# Plafond du quiz de fin de séance sur un gros budget : au-delà, l'exercice de vérif'
# redevient une session de quiz complète et mange la séance au lieu de la conclure.
QUIZ_QUESTIONS_MAX = 10

# Exercices d'examen maximum dans une séance - ce qui distingue une séance intensive
# d'une séance normale rallongée : s'entraîner veut dire refaire, pas lire plus
# longtemps.
EXERCICES_PAR_SEANCE_MAX = 2

# Budgets proposés à l'élève ("combien de temps as-tu ?"). 25 reste le défaut et la
# recommandation ; 10 sert les jours où il n'a qu'un trajet, 45 les révisions de
# week-end. Ce sont des PLAFONDS : la séance affiche toujours sa durée réelle, qui
# peut être inférieure quand le contenu manque (voir _construire_etapes).
BUDGETS_SEANCE_MINUTES = (10, 25, 45)


def plan_du_jour(user, cursus, date=None):
    """
    La séance du jour, créée une fois puis relue telle quelle (voir
    SeanceJournaliere) - renvoie None quand il n'y a rien à proposer (cursus sans
    contenu exploitable).

    Ordre de priorité :
      1. une révision due (voir revisions_dues) - un thème raté hier passe avant tout ;
      2. une lecture ouverte il y a moins de 48 h - finir ce qu'on a commencé passe
         avant d'ouvrir un nouveau front ;
      3. le thème du parcours qui revient le plus souvent à l'examen ;
      4. un calibrage, pour un élève sans historique dont le parcours n'a rien
         d'exploitable.

    Le calibrage a d'abord été placé DEVANT le parcours, au motif qu'en dernier il ne
    se déclencherait presque jamais. L'essai en conditions réelles a montré que c'était
    une erreur : la toute première séance d'un élève qui vient de payer était "on situe
    ton niveau", c'est-à-dire un test, là où il attendait précisément qu'on lui dise
    quoi réviser. Un nouvel abonné voit désormais une vraie séance, sur le thème le
    plus fréquent de son cursus - pour le BAC C, "tableau de variation" en maths, tombé
    dans 28 des 44 dernières épreuves. C'est cette phrase-là qui justifie l'abonnement,
    pas une note de départ.

    Le calibrage reste en repli : un cursus dont aucun thème n'est encore exploitable
    (banque de quiz trop mince, voir _contient_quiz) vaut mieux qu'un écran vide.
    """
    date = date or timezone.localdate()
    existante = SeanceJournaliere.objects.filter(user=user, cursus=cursus, date=date).first()
    if existante is not None:
        return existante

    proposition = _construire_seance(user, cursus)
    if proposition is None:
        return None

    # get_or_create plutôt que create : deux onglets ouverts au passage de minuit
    # lanceraient deux constructions concurrentes, et la contrainte unique ferait
    # lever la seconde. Celle qui arrive après lit simplement la séance de l'autre -
    # elles proposent de toute façon la même chose.
    seance, _ = SeanceJournaliere.objects.get_or_create(
        user=user, cursus=cursus, date=date, defaults=proposition,
    )
    return seance


def _construire_seance(user, cursus, themes_interdits=frozenset(), avec_calibrage=True):
    """
    Choisit quoi proposer, sans rien écrire en base. Renvoie les `defaults` d'une
    SeanceJournaliere, ou None.

    Chaque priorité est d'abord essayée en respectant la rotation des matières, puis -
    si aucune ne passe - réessayée sans elle : mieux vaut une troisième séance de
    maths que pas de séance du tout.

    `themes_interdits` : thèmes à ne pas reproposer, quelle que soit la passe. Sert
    aux séances supplémentaires (voir seance_supplementaire) - une matière peut
    revenir dans la journée si elle est seule à avoir du contenu, jamais le thème
    qu'on vient de travailler. `avec_calibrage` : on ne se calibre pas deux fois dans
    la même journée.
    """
    # Un objectif de matière choisi par l'élève passe AVANT la sélection automatique, et
    # avant la rotation : c'est son choix explicite, et sa durée limitée (voir
    # ObjectifMatiere) est ce qui protège contre la lassitude. S'il n'y a rien à
    # proposer sur cette matière, on retombe sur le plan normal plutôt que sur un écran vide.
    objectif = objectif_matiere_actif(user, cursus)
    if objectif is not None:
        autres = set(Subject.objects.exclude(pk=objectif.subject_id).values_list("id", flat=True))
        for candidat in (
            _seance_depuis_revision_due(user, cursus, autres, themes_interdits),
            _seance_depuis_lecture_en_cours(user, cursus, autres, themes_interdits),
            _seance_depuis_parcours(user, cursus, autres, themes_interdits),
        ):
            if candidat is not None:
                return candidat

    matieres_recentes = _matieres_recentes(user, cursus)
    for exclues in (matieres_recentes, set()):
        for candidat in (
            _seance_depuis_revision_due(user, cursus, exclues, themes_interdits),
            _seance_depuis_lecture_en_cours(user, cursus, exclues, themes_interdits),
            _seance_depuis_parcours(user, cursus, exclues, themes_interdits),
            # Le calibrage passe APRÈS le parcours, et non avant : c'est un vrai repli,
            # pour un cursus dont aucun thème n'est exploitable. Voir la docstring de
            # plan_du_jour pour pourquoi il était devant, et pourquoi c'était une
            # erreur.
            _seance_de_calibrage(user, cursus) if avec_calibrage else None,
        ):
            if candidat is not None:
                return candidat
        if not matieres_recentes:
            # Deuxième passe identique à la première - rien à regagner à la refaire.
            break
    return None


# Durée d'un objectif de matière. Une semaine : assez pour préparer un devoir ou un
# chapitre, assez court pour que la rotation reprenne d'elle-même.
DUREE_OBJECTIF_MATIERE_JOURS = 7


def objectif_matiere_actif(user, cursus, date=None):
    """L'objectif de matière en cours, ou None - un objectif échu vaut absence."""
    return (
        ObjectifMatiere.objects.filter(user=user, cursus=cursus, jusqu_au__gte=date or timezone.localdate())
        .select_related("subject")
        .first()
    )


def matieres_pour_objectif(cursus):
    """Matières qu'on peut choisir : celles qui ont de quoi faire une séance, c'est-à-dire
    une banque de quiz (voir _contient_quiz) sur ce cursus."""
    return list(
        Subject.objects.filter(competence_items__statut=StatutContenu.VALIDE, competence_items__cursus=cursus)
        .distinct()
        .order_by("label"),
    )


def definir_objectif_matiere(user, cursus, subject, date=None):
    """
    Se concentre sur `subject` pendant DUREE_OBJECTIF_MATIERE_JOURS jours. Renvoie
    l'objectif, ou None si la matière n'est pas proposable sur ce cursus.

    Si la séance du jour n'est pas commencée et porte sur une autre matière, elle est
    remplacée : un choix qui ne prendrait effet que demain donnerait l'impression que le
    bouton n'a rien fait.
    """
    date = date or timezone.localdate()
    if subject.id not in {s.id for s in matieres_pour_objectif(cursus)}:
        return None
    objectif, _ = ObjectifMatiere.objects.update_or_create(
        user=user, cursus=cursus,
        defaults={"subject": subject, "jusqu_au": date + timedelta(days=DUREE_OBJECTIF_MATIERE_JOURS - 1)},
    )

    seances_du_jour = list(SeanceJournaliere.objects.filter(user=user, cursus=cursus, date=date))
    if seances_du_jour:
        courante = max(seances_du_jour, key=lambda s: s.ordre)
        # Une séance dont le quiz est déjà lancé est en cours de travail : on ne la retire
        # pas sous les doigts de l'élève.
        if (
            courante.statut == StatutSeance.PROPOSEE
            and courante.subject_id != subject.id
            and courante.quiz_session_id is None
        ):
            proposition = _construire_seance(
                user, cursus,
                themes_interdits={s.theme_id for s in seances_du_jour if s.theme_id},
                avec_calibrage=False,
            )
            if proposition is not None and proposition["subject"].id == subject.id:
                _, creee = SeanceJournaliere.objects.get_or_create(
                    user=user, cursus=cursus, date=date, ordre=courante.ordre + 1, defaults=proposition,
                )
                if creee:
                    courante.statut = StatutSeance.REMPLACEE
                    courante.save(update_fields=["statut"])
    return objectif


def retirer_objectif_matiere(user, cursus):
    """Revient à la sélection automatique dès la prochaine séance. La séance du jour,
    déjà construite, n'est pas touchée."""
    ObjectifMatiere.objects.filter(user=user, cursus=cursus).delete()


def _contient_quiz(etapes):
    """
    Une séance sans quiz n'en est pas une : elle ne vérifie rien, ne nourrit pas la
    révision espacée (voir enregistrer_resultat_pour_revision, qui ne se déclenche que
    sur une réponse) et ne peut même pas se clore toute seule - l'élève doit déclarer
    à la main qu'il a fini. Constaté sur trois séances d'anglais d'affilée : "relire
    la méthode" puis "faire l'exercice", et rien pour savoir si c'était compris.

    Un thème sans banque de quiz n'est donc pas proposé du tout. Mieux vaut ne rien
    proposer aujourd'hui que proposer quelque chose qu'on ne sait pas évaluer.
    """
    return any(etape.get("type") == "quiz" for etape in etapes)


def _matieres_recentes(user, cursus):
    """Matières des dernières séances TERMINÉES - une séance proposée puis ignorée ne
    bloque rien, l'élève n'a pas travaillé cette matière."""
    return {
        subject_id
        for subject_id in SeanceJournaliere.objects.filter(
            user=user, cursus=cursus, statut=StatutSeance.TERMINEE, subject__isnull=False,
        )
        # `-ordre` en second : depuis les séances supplémentaires, une même journée
        # peut en porter plusieurs, et c'est la DERNIÈRE travaillée qui doit compter
        # comme la plus récente.
        .order_by("-date", "-ordre")
        .values_list("subject_id", flat=True)[:ROTATION_MATIERES_RECENTES]
    }


def _seance_depuis_revision_due(user, cursus, matieres_exclues, themes_interdits=frozenset()):
    for schedule in revisions_dues(user, cursus):
        if schedule.subject_id in matieres_exclues or schedule.theme_id in themes_interdits:
            continue
        etapes = _construire_etapes(cursus, schedule.subject, theme=schedule.theme, user=user)
        if not _contient_quiz(etapes):
            continue
        return {
            "origine": OrigineSeance.REVISION_DUE,
            "subject": schedule.subject,
            "theme": schedule.theme,
            "etapes": etapes,
        }
    return None


def _seance_depuis_lecture_en_cours(user, cursus, matieres_exclues, themes_interdits=frozenset()):
    """
    Reprend un cours ouvert récemment. Au niveau du DOCUMENT, jamais "à l'exercice 3" :
    LectureProgress ne stocke aucune position de lecture (voir access.models), et
    promettre une reprise fine qu'on ne sait pas tenir se retournerait contre nous.
    """
    depuis = timezone.now() - timedelta(hours=FENETRE_LECTURE_EN_COURS_HEURES)
    lectures = (
        LectureProgress.objects.filter(user=user, cours__isnull=False, last_read_at__gte=depuis)
        .select_related("cours__subject")
        .prefetch_related("cours__tags")
        .order_by("-last_read_at")
    )
    for lecture in lectures:
        cours = lecture.cours
        if cours.subject_id in matieres_exclues:
            continue
        theme = next(iter(cours.tags.all()), None)
        if theme is not None and theme.id in themes_interdits:
            continue
        etapes = _construire_etapes(cursus, cours.subject, theme=theme, cours_impose=cours)
        if not _contient_quiz(etapes):
            continue
        return {
            "origine": OrigineSeance.LECTURE_EN_COURS,
            "cours": cours,
            "subject": cours.subject,
            "theme": theme,
            "etapes": etapes,
        }
    return None


def _seance_de_calibrage(user, cursus):
    """
    Dix questions pour situer son niveau, uniquement pour qui n'a jamais répondu sur ce
    cursus. Présenté comme un calibrage et jamais comme un test : un élève qui croit
    passer un examen dès l'ouverture de l'appli la referme.
    """
    a_un_historique = QuizAnswer.objects.filter(
        quiz_question__session__user=user, quiz_question__session__cursus=cursus,
    ).exists()
    if a_un_historique:
        return None
    if not _items_eligibles(cursus):
        return None
    return {
        "origine": OrigineSeance.DIAGNOSTIC,
        "subject": None,
        "theme": None,
        "etapes": [{
            "type": "quiz",
            "libelle": "10 questions pour situer ton niveau",
            "mode": ModeQuiz.DIAGNOSTIC,
            "n": 10,
            "duree_min": 10,
        }],
    }


def _seance_depuis_parcours(user, cursus, matieres_exclues, themes_interdits=frozenset()):
    """
    Le thème qui revient le plus souvent à l'examen, parmi ceux que l'élève n'a pas
    encore travaillés - toutes matières confondues, et jamais un thème sans quiz.

    Le classement se fait sur le POURCENTAGE d'épreuves touchées, pas sur le nombre
    brut : un thème tombé 9 fois sur 10 en SVT pèse plus qu'un thème tombé 11 fois sur
    41 en anglais, alors que le compte brut dirait l'inverse. Les matières dont le
    parcours suit le programme officiel plutôt que la fréquence (français, philo,
    histoire-géo - voir SUBJECTS_PARCOURS_PAR_FREQUENCE) n'ont aucune fréquence à
    annoncer : elles passent après, jamais devant, plutôt que de se voir attribuer un
    chiffre inventé.

    Cette recherche balaie toutes les matières au lieu de s'arrêter à la première, et
    c'est délibérément plus coûteux : jusqu'à une douzaine d'appels à
    construire_parcours_par_frequence. Acceptable parce que la séance n'est construite
    qu'UNE fois par jour et par élève (voir SeanceJournaliere, la table est le cache) -
    ce serait à revoir si elle devait se recalculer à chaque affichage.

    Le rang de la matière (voir _subjects_par_priorite : coefficient x (1 - maîtrise))
    ne décide plus, il départage : à fréquence égale, on préfère la matière qui pèse le
    plus au diplôme et où l'élève est le plus faible.
    """
    # Seules les matières qui ont une banque de quiz sur ce cursus : ailleurs, aucun
    # thème ne passerait le filtre "sans quiz" de toute façon, autant ne pas payer le
    # classement par fréquence pour rien.
    avec_quiz = set(
        Subject.objects.filter(competence_items__statut=StatutContenu.VALIDE, competence_items__cursus=cursus)
        .values_list("id", flat=True),
    )

    candidats = []
    for rang, subject in enumerate(_subjects_par_priorite(user, cursus)):
        if subject.id in matieres_exclues or subject.id not in avec_quiz:
            continue

        par_frequence = construire_parcours_par_frequence(user, cursus, subject)
        if par_frequence is not None:
            etapes_parcours, cle_theme, cle_savoir = par_frequence, "theme_id", None
        else:
            etapes_parcours = [s for module in construire_parcours(user, cursus, subject) for s in module["savoirs"]]
            cle_theme, cle_savoir = None, "id"

        for entree in etapes_parcours:
            if not entree["has_quiz"]:
                continue
            if cle_theme is not None and entree[cle_theme] in themes_interdits:
                continue
            candidats.append({
                "subject": subject,
                "rang_matiere": rang,
                "entree": entree,
                "cle_theme": cle_theme,
                "cle_savoir": cle_savoir,
                "frequence_pct": entree.get("frequence_pct"),
            })

    if not candidats:
        return None

    # Jamais travaillé d'abord : c'est là qu'il y a le plus à gagner. À défaut (tout
    # entamé), le moins bien maîtrisé - il reste toujours quelque chose à réviser.
    jamais_travailles = [
        c for c in candidats if c["entree"]["taux"] is None and not c["entree"]["a_lu_le_cours"]
    ]
    pool = jamais_travailles or candidats

    def cle_de_tri(c):
        # Fréquence décroissante d'abord ; une matière sans classement par fréquence
        # (frequence_pct absent) passe après toutes celles qui en ont un.
        return (
            c["frequence_pct"] is None,
            -(c["frequence_pct"] or 0),
            0 if jamais_travailles else (c["entree"]["taux"] or 0),
            c["rang_matiere"],
            c["entree"]["intitule"],
        )

    for choisi in sorted(pool, key=cle_de_tri):
        entree, subject = choisi["entree"], choisi["subject"]
        theme = Tag.objects.filter(pk=entree[choisi["cle_theme"]]).first() if choisi["cle_theme"] else None
        savoir = Savoir.objects.filter(pk=entree[choisi["cle_savoir"]]).first() if choisi["cle_savoir"] else None
        # Le cours retenu est mémorisé sur la séance (voir SeanceJournaliere.cours) :
        # le classement qui l'a choisi n'est pas rejoué à chaque ajustement de durée,
        # et sans cette trace un aller-retour 25 -> 10 -> 25 minutes le perdrait.
        cours_retenu = Cours.objects.filter(slug=entree["cours"][0]["slug"]).first() if entree["cours"] else None
        etapes = _construire_etapes(
            cursus, subject, theme=theme, savoir=savoir, cours_proposes=entree["cours"], user=user,
        )
        # `has_quiz` dit qu'il existe un quiz sur ce thème pour ce cursus ; seul
        # _construire_etapes sait s'il en reste dans le budget de la séance. On
        # redescend donc au candidat suivant plutôt que d'abandonner le parcours.
        if not _contient_quiz(etapes):
            continue
        return {
            "origine": OrigineSeance.PARCOURS,
            "cours": cours_retenu,
            "subject": subject,
            "theme": theme,
            "savoir": savoir,
            "etapes": etapes,
        }
    return None




def _theme_deja_maitrise(user, cursus, theme):
    """
    L'élève a-t-il déjà prouvé qu'il sait faire ? Sert à ne pas lui réimposer la
    méthode d'un thème qu'il réussit - lui faire relire huit minutes de cours pour
    quelque chose qu'il maîtrise, c'est le meilleur moyen de lui apprendre à sauter
    les séances.

    Même seuil que partout ailleurs (SEUIL_MAITRISE), mais sur un échantillon minimal :
    un thème n'est pas "maîtrisé" sur deux bonnes réponses. Cinq, c'est un quiz de fin
    de séance complet - la plus petite preuve qui vaille quelque chose.
    """
    if theme is None:
        return False
    stats = {"total": 0, "reussies": 0}
    for reponse in QuizAnswer.objects.filter(
        quiz_question__session__user=user,
        quiz_question__session__cursus=cursus,
        quiz_question__competence_item__theme=theme,
    ):
        stats["total"] += 1
        if reponse.est_correcte:
            stats["reussies"] += 1
    if stats["total"] < REPONSES_MINIMUM_MAITRISE_THEME:
        return False
    return 100 * stats["reussies"] / stats["total"] >= SEUIL_MAITRISE


def _construire_etapes(
    cursus, subject, theme=None, savoir=None, cours_impose=None, cours_proposes=None,
    budget_minutes=BUDGET_SEANCE_MINUTES, user=None,
):
    """
    Relire la méthode, la mettre en pratique sur un vrai sujet d'examen, se vérifier -
    dans cet ordre, et seulement tant que le budget de la séance le permet.

    Le quiz est RÉSERVÉ d'abord, avant de remplir le reste : c'est la seule étape
    obligatoire (voir _contient_quiz), et un remplissage glouton naïf la faisait sauter
    dès que le budget descendait - un budget de 10 minutes partait entièrement dans le
    cours (8 min) et ne laissait rien pour vérifier quoi que ce soit, donc aucune
    séance du tout. Une fois le reste rempli, le quiz récupère ce qui n'a pas servi,
    jusqu'à QUIZ_QUESTIONS_MAX : c'est ce qui fait qu'une séance longue interroge
    davantage plutôt que de finir en avance.

    À 25 minutes - le défaut - la composition est exactement celle d'avant : méthode
    (8) + exercice (12) + 5 questions (5).

    Une étape absente (pas de cours rattaché au thème, aucun exercice tombé dessus,
    banque de quiz pas encore générée) est simplement omise : une séance plus courte
    reste une séance, une séance qui renvoie vers du vide n'en est pas une.
    """
    a_du_quiz = bool(_items_eligibles(cursus, subject=subject, theme=theme, savoir=savoir))
    # Réservation : sans elle, le quiz passerait après le cours et l'exercice et
    # sauterait sur les petits budgets.
    reserve = DUREE_ETAPE_MINUTES["quiz"] if a_du_quiz else 0
    restant = budget_minutes - reserve

    etapes = []
    cours = cours_impose or (cours_proposes[0] if cours_proposes else None)
    # Un thème déjà maîtrisé n'a pas besoin qu'on en réexplique la méthode : le temps
    # gagné part en entraînement et en vérification (voir plus bas, le quiz récupère
    # ce qui n'a pas servi). `cours_impose` échappe à la règle - il vient d'une lecture
    # que l'élève avait lui-même ouverte, la lui retirer serait absurde.
    if cours_impose is None and user is not None and _theme_deja_maitrise(user, cursus, theme):
        cours = None
    if cours is not None and restant >= DUREE_ETAPE_MINUTES["cours"]:
        # construire_parcours* renvoie des dicts {slug, titre, sous_theme}, la lecture
        # en cours un vrai Cours - les deux portent les mêmes deux champs utiles ici.
        etapes.append({
            "type": "cours",
            "libelle": "Relire la méthode",
            "slug": cours["slug"] if isinstance(cours, dict) else cours.slug,
            "titre": cours["titre"] if isinstance(cours, dict) else cours.titre,
            "duree_min": DUREE_ETAPE_MINUTES["cours"],
        })
        restant -= DUREE_ETAPE_MINUTES["cours"]

    if theme is not None:
        # Plusieurs exercices sur les gros budgets : c'est ce qui distingue une séance
        # intensive d'une séance normale rallongée artificiellement - s'entraîner, ça
        # veut dire refaire, pas lire plus longtemps.
        for exercice in _exercices_pour_theme(cursus, subject, theme, EXERCICES_PAR_SEANCE_MAX):
            if restant < DUREE_ETAPE_MINUTES["exercice"]:
                break
            etapes.append(dict(exercice, duree_min=DUREE_ETAPE_MINUTES["exercice"]))
            restant -= DUREE_ETAPE_MINUTES["exercice"]

    if a_du_quiz:
        # Une question par minute (voir DUREE_ETAPE_MINUTES) : le quiz reprend sa
        # réserve plus tout ce que le cours et les exercices n'ont pas consommé.
        questions = min(QUIZ_QUESTIONS_MAX, max(QUIZ_FIN_DE_SEANCE_N, reserve + restant))
        etapes.append({
            "type": "quiz",
            "libelle": str(questions) + " questions",
            "mode": ModeQuiz.PRATIQUE,
            "n": questions,
            "duree_min": questions,
        })

    return etapes


def _exercices_pour_theme(cursus, subject, theme, maximum):
    """
    Des exercices réellement tombés sur ce thème, le plus récent d'abord - c'est ce qui
    distingue une révision edukora d'une fiche de cours : l'élève travaille les sujets
    qui sont vraiment tombés, pas des exercices inventés pour l'occasion.

    Un exercice bavard peut porter le thème sur plusieurs de ses Question : une seule
    entrée par exercice, jamais par sous-question (même dédoublonnage que
    catalog.views.ThemeExercicesView).

    Même source que ThemeExercicesView, sans sa restriction d'accès : le gating est
    décidé plus haut, sur la séance entière (voir la vue).
    """
    questions = (
        Question.objects.filter(
            themes=theme, exercise__lesson__statut=StatutContenu.VALIDE,
            exercise__lesson__subject=subject, exercise__lesson__cursus=cursus,
        )
        .select_related("exercise__lesson")
        .order_by("-exercise__lesson__year", "exercise__numero_exercice")
    )
    vus, trouves = set(), []
    for question in questions:
        lesson = question.exercise.lesson
        numero = question.exercise.numero_exercice
        cle = (lesson.id, numero)
        if cle in vus:
            continue
        vus.add(cle)
        trouves.append({
            "type": "exercice",
            # Permet de marquer l'exercice comme fait quand la séance est clôturée
            # (voir terminer_seance) - sans quoi la file d'entraînement du thème le
            # reproposerait alors qu'il vient d'être travaillé.
            "exercise_id": question.exercise.pk,
            "libelle": "Exercice " + str(numero) + " - " + lesson.title if numero else lesson.title,
            "lesson_slug": lesson.slug,
            "lesson_title": lesson.title,
            "lesson_year": lesson.year,
            "numero_exercice": numero,
        })
        if len(trouves) >= maximum:
            break
    return trouves



def terminer_seance(seance):
    """Marque la séance du jour comme faite - idempotent : reconfirmer une séance déjà
    terminée ne doit ni décaler son horodatage ni la compter deux fois."""
    if seance.statut == StatutSeance.TERMINEE:
        return seance
    seance.statut = StatutSeance.TERMINEE
    seance.termine_at = timezone.now()
    seance.save(update_fields=["statut", "termine_at"])

    # Les exercices de la séance comptent comme faits. C'est une inférence, la seule
    # qu'on se permette : déclarer sa séance terminée, c'est déclarer en avoir fait les
    # étapes. Sans elle, la file d'entraînement du thème reproposerait dès le lendemain
    # l'exercice travaillé la veille, et les deux surfaces se contrediraient.
    for etape in seance.etapes:
        if etape.get("type") == "exercice" and etape.get("exercise_id"):
            ExerciceFait.objects.get_or_create(user=seance.user, exercise_id=etape["exercise_id"])
    return seance


def seances_terminees_cette_semaine(user, cursus, date=None):
    """
    Séances faites sur les 7 derniers jours glissants - jamais une série (streak) de
    jours consécutifs. Téléphone partagé, coupure de courant, connexion absente : "tu
    as perdu ta série de 12 jours" fait désinstaller, quand "4 séances cette semaine"
    reste vrai et encourageant après une journée manquée.
    """
    date = date or timezone.localdate()
    return SeanceJournaliere.objects.filter(
        user=user, cursus=cursus, statut=StatutSeance.TERMINEE,
        date__gt=date - timedelta(days=7), date__lte=date,
    ).count()


def seance_du_jour(user, cursus, date=None):
    """La séance du jour déjà construite, sans jamais en créer une - contrairement à
    plan_du_jour, dont c'est le rôle. Sert aux appels qui réagissent à une action de
    l'élève (fin de quiz, clôture) et qui n'ont aucune raison de faire naître une
    séance au passage.

    La plus AVANCÉE de la journée quand il y en a plusieurs (voir
    SeanceJournaliere.ordre et son Meta.ordering) : celle qui est en cours, jamais
    celle qu'il a déjà terminée ce matin."""
    return SeanceJournaliere.objects.filter(
        user=user, cursus=cursus, date=date or timezone.localdate(),
    ).first()


def cle_etape(etape):
    """Identifiant stable d'une étape, celui que le frontend renvoie quand l'élève
    l'ouvre. Pas l'indice : ajuster_duree_seance recompose la liste, et une étape
    conservée doit rester cochée."""
    if etape.get("type") == "cours":
        return f"cours:{etape.get('slug')}"
    if etape.get("type") == "exercice":
        return f"exercice:{etape.get('lesson_slug')}:{etape.get('exercise_id')}"
    return "quiz"


def etape_ouverte(seance, etape):
    """Le quiz se lit sur la session rattachée, les autres étapes sur la liste
    enregistrée à l'ouverture."""
    if etape.get("type") == "quiz":
        return seance.quiz_session_id is not None
    return cle_etape(etape) in seance.etapes_ouvertes


def marquer_etape_ouverte(user, cursus, cle):
    """Note qu'une étape cours/exercice de la séance en cours a été ouverte.

    Renvoie la séance, ou None si la clé ne désigne aucune étape de la séance (clé
    inventée, séance recomposée depuis) - jamais d'écriture d'une clé qu'on ne connaît
    pas. Idempotent : rouvrir la même étape n'écrit rien."""
    seance = seance_du_jour(user, cursus)
    if seance is None:
        return None
    valides = {cle_etape(e) for e in seance.etapes if e.get("type") != "quiz"}
    if cle not in valides:
        return None
    if cle not in seance.etapes_ouvertes:
        seance.etapes_ouvertes = [*seance.etapes_ouvertes, cle]
        seance.save(update_fields=["etapes_ouvertes"])
    return seance


def rattacher_quiz_a_la_seance(user, session):
    """
    Note que CETTE session de quiz a été lancée depuis la séance du jour - à
    n'appeler que sur une session réellement créée par ce chemin (voir le paramètre
    `seance` de quiz.views.start_session), jamais deviné d'après un thème commun :
    un élève peut très bien lancer un quiz sur le même thème de son propre chef, et
    ce serait alors sa séance qui se clôturerait toute seule.

    Ne remplace jamais un rattachement vers une session TERMINÉE : si l'élève relance
    un quiz après avoir déjà bouclé celui de sa séance, c'est le premier - celui qui a
    réellement clôturé la séance - qui reste la trace.

    Une session ABANDONNÉE, elle, se remplace. La règle ne distinguait pas les deux,
    et la conséquence se voyait à l'usage : ouvrir le quiz de sa séance puis quitter
    sans répondre liait définitivement la séance à une session sans fin, et AUCUNE
    tentative suivante ne pouvait plus la clôturer - l'élève refaisait le quiz en
    entier et voyait sa séance rester "à faire". Un abandon ne doit pas condamner la
    journée.
    """
    seance = seance_du_jour(user, session.cursus)
    if seance is None:
        return None
    if seance.quiz_session_id is not None and seance.quiz_session.completed_at is not None:
        return None
    seance.quiz_session = session
    seance.save(update_fields=["quiz_session"])
    return seance


def cloturer_seance_si_quiz_termine(session):
    """
    Clôt la séance du jour quand le quiz qui la terminait vient d'être bouclé.

    L'étape quiz est toujours la dernière d'une séance (voir _construire_etapes) :
    la boucler, c'est avoir fait la séance. Demander en plus à l'élève de cliquer
    "J'ai fini" juste après lui ferait déclarer ce que l'application vient de le voir
    faire - le bouton reste pour les séances SANS quiz (un cours, un exercice : rien
    ne dit quand on a fini de lire).

    Renvoie la séance clôturée, ou None s'il n'y avait rien à clôturer.
    """
    seance = session.seances.filter(statut=StatutSeance.PROPOSEE).first()
    if seance is None:
        return None
    return terminer_seance(seance)


def score_de_la_seance(seance):
    """
    "4/5" - le résultat du quiz de la séance, seulement une fois la session terminée.

    None tant qu'elle ne l'est pas, ou si la séance n'avait pas d'étape quiz : un
    "0/0" affiché en fin de séance se lirait comme un échec alors qu'il n'y avait
    simplement rien à noter.
    """
    session = seance.quiz_session
    if session is None or session.completed_at is None:
        return None
    total = 0
    reussies = 0
    for quiz_question in session.quiz_questions.select_related("answer"):
        answer = getattr(quiz_question, "answer", None)
        if answer is None:
            continue
        total += 1
        if answer.est_correcte:
            reussies += 1
    if not total:
        return None
    return {"reussies": reussies, "total": total}


# Coefficient retenu pour une matière dont aucune épreuve ne porte de coefficient
# lisible : la valeur la plus fréquente du corpus (mesurée sur BAC D : 62 épreuves à
# 2, contre 45 à 4 et 11 à 1). "Ni favorisée ni pénalisée" plutôt qu'écartée - une
# matière sans coefficient transcrit reste une matière à réviser.
COEFFICIENT_PAR_DEFAUT = 2.0

# En dessous de ce nombre de réponses sur une matière, son taux de réussite n'est pas
# un signal : c'est du bruit. Constaté en vérifiant le classement sur des données
# réelles - six réponses en SVT (5 bonnes) suffisaient à faire passer une matière de
# coefficient 4 de la première à la DERNIÈRE place, alors que l'élève n'avait traité
# qu'un seul thème sur toute la matière. Sous ce seuil, la maîtrise est ignorée et
# seul le coefficient décide.
REPONSES_MINIMUM_MAITRISE_MATIERE = 10

# Idem pour UN thème (voir _theme_deja_maitrise) : cinq, c'est un quiz de fin de
# séance complet - la plus petite preuve qui vaille quelque chose. Plus bas que le
# seuil par matière, qui agrège plusieurs thèmes.
REPONSES_MINIMUM_MAITRISE_THEME = 5


def _coefficient_par_subject(cursus):
    """
    Coefficient dominant par matière pour ce cursus, lu depuis les épreuves déjà en
    base (catalog.Lesson.coefficient) - il n'existe aucun référentiel de coefficients
    dans le modèle : catalog.Subject prévoit explicitement d'en accueillir un "plus
    tard" (voir sa docstring) et ne l'a jamais reçu. En attendant, l'information est
    bien là, transcrite épreuve par épreuve depuis les sujets réels.

    Ne retient que les valeurs NUMÉRIQUES SIMPLES ("4", "1,5"). Le champ est du texte
    libre et une minorité de valeurs sont composites ("D:4", "C,D : 1,5 ; E : 2",
    mesuré à 19 sur 154 pour BAC D) : deviner quelle part s'applique à quelle série
    demanderait un analyseur de codes de série, pour un gain nul - il reste presque
    toujours une épreuve à valeur simple sur la même matière, et à défaut le
    coefficient par défaut s'applique.

    Valeur dominante (la plus fréquente) et non moyenne : une transcription erronée
    isolée ne doit pas décaler le coefficient de toute une matière. Départage par la
    plus grande valeur, pour que le résultat ne dépende jamais de l'ordre des lignes.
    """
    valeurs = defaultdict(Counter)
    for subject_id, brut in (
        Lesson.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus)
        .exclude(coefficient="")
        .values_list("subject_id", "coefficient")
    ):
        texte = (brut or "").strip().replace(",", ".")
        try:
            valeur = float(texte)
        except ValueError:
            continue  # valeur composite : voir la docstring
        if valeur > 0:
            valeurs[subject_id][valeur] += 1

    return {
        subject_id: max(compteur.most_common(), key=lambda paire: (paire[1], paire[0]))[0]
        for subject_id, compteur in valeurs.items()
    }


def _maitrise_par_subject(user, cursus):
    """
    Taux de réussite par matière (0 à 1) sur ce cursus, pour les seules matières
    réellement pratiquées (voir REPONSES_MINIMUM_MAITRISE_MATIERE). Une matière
    absente du résultat n'a pas été assez pratiquée pour qu'on en dise quoi que ce
    soit - à l'appelant de la traiter comme "tout reste à faire", jamais comme une
    matière maîtrisée.

    Mêmes restrictions que _poids_par_theme : uniquement les réponses sourcées d'un
    CompetenceItem, qui seul porte une matière sans ambiguïté.
    """
    stats = defaultdict(lambda: {"total": 0, "reussies": 0})
    for reponse in (
        QuizAnswer.objects.filter(
            quiz_question__session__user=user,
            quiz_question__session__cursus=cursus,
            quiz_question__competence_item__isnull=False,
        )
        .select_related("quiz_question__competence_item")
    ):
        s = stats[reponse.quiz_question.competence_item.subject_id]
        s["total"] += 1
        if reponse.est_correcte:
            s["reussies"] += 1
    return {
        subject_id: s["reussies"] / s["total"]
        for subject_id, s in stats.items()
        if s["total"] >= REPONSES_MINIMUM_MAITRISE_MATIERE
    }


def _subjects_par_priorite(user, cursus):
    """
    Matières du cursus, de la plus utile à travailler aujourd'hui à la moins utile.

    `coefficient x (1 - maîtrise)` : ce qui pèse à l'examen, pondéré par ce qui n'est
    pas encore acquis. Une matière jamais pratiquée compte comme entièrement à
    découvrir, donc les matières à fort coefficient passent naturellement en premier
    pour un élève qui démarre ; une matière déjà maîtrisée descend d'elle-même sans
    jamais disparaître.

    Remplace un tri par ordre ALPHABÉTIQUE de libellé, qui était le vrai point faible
    du plan : un élève de BAC D sans révision due ni lecture en cours tournait en
    boucle sur les trois premières matières de l'alphabet, quel que soit leur poids au
    baccalauréat ou son niveau réel. Seule la rotation des matières (voir
    _construire_seance) l'en sortait, et elle ne fait que décaler le problème d'un cran.

    Départage par libellé : à score égal, l'ordre ne doit pas dépendre du SGBD.
    """
    subjects = list(
        Subject.objects.filter(lessons__statut=StatutContenu.VALIDE, lessons__cursus=cursus).distinct(),
    )
    coefficients = _coefficient_par_subject(cursus)
    maitrise = _maitrise_par_subject(user, cursus)

    def score(subject):
        poids = coefficients.get(subject.id, COEFFICIENT_PAR_DEFAUT)
        return poids * (1 - maitrise.get(subject.id, 0.0))

    return sorted(subjects, key=lambda s: (-score(s), s.label))


def seance_supplementaire(user, cursus, date=None):
    """
    Une séance de PLUS, pour l'élève qui a fini la sienne et veut continuer.

    "Continuer quand même" renvoyait jusqu'ici vers la liste des thèmes fréquents,
    c'est-à-dire vers le catalogue auquel tout ce travail sert justement à se
    substituer : on lui disait "voilà ce qu'il faut faire aujourd'hui", il le faisait,
    et pour sa peine on lui rendait la charge de choisir. Une séance finie doit pouvoir
    être suivie d'une autre séance, pas d'une liste.

    Jamais créée d'office, seulement sur demande explicite : c'est ce qui préserve la
    promesse d'une seule chose à faire. Tant que la séance en cours n'est pas terminée,
    cet appel la renvoie telle quelle plutôt que d'en empiler une deuxième.

    Les thèmes déjà travaillés aujourd'hui sont exclus - reproposer le thème qu'on
    vient de finir serait la pire réponse possible à "je veux continuer". La matière,
    elle, peut revenir : sur un cursus où une seule matière a du contenu, l'exclure
    reviendrait à ne rien proposer.

    Renvoie None quand il n'y a plus rien à proposer.
    """
    date = date or timezone.localdate()
    seances_du_jour = list(SeanceJournaliere.objects.filter(user=user, cursus=cursus, date=date))
    if not seances_du_jour:
        return None

    courante = max(seances_du_jour, key=lambda s: s.ordre)
    if courante.statut != StatutSeance.TERMINEE:
        return courante

    proposition = _construire_seance(
        user, cursus,
        themes_interdits={s.theme_id for s in seances_du_jour if s.theme_id},
        # On ne se calibre pas deux fois dans la même journée.
        avec_calibrage=False,
    )
    if proposition is None:
        return None

    seance, _ = SeanceJournaliere.objects.get_or_create(
        user=user, cursus=cursus, date=date, ordre=courante.ordre + 1, defaults=proposition,
    )
    return seance


# Nombre de refus acceptés dans une journée avant de rendre la main. Au-delà, ce n'est
# plus un mauvais tirage, c'est que l'élève sait ce qu'il veut travailler et que nos
# priorités ne le rejoignent pas aujourd'hui : lui reproposer une dixième séance serait
# s'obstiner. On lui rend alors le catalogue, qui redevient la bonne réponse.
REFUS_MAX_PAR_JOUR = 3


def remplacer_seance(user, cursus, date=None):
    """
    "Ce n'est pas ce que je veux réviser" : remplace la séance du jour par une autre,
    sur un thème différent.

    Ce lien renvoyait jusqu'ici vers la liste des thèmes fréquents - même défaut que
    "Continuer quand même" (voir seance_supplementaire) : l'élève signale que notre
    sélection est à côté, et on lui répond par un catalogue de 130 thèmes. Un coach à
    qui on dit "pas ça" propose autre chose ; il ne tend pas le sommaire.

    La séance refusée est conservée au statut REMPLACEE, jamais supprimée : elle ne
    compte pas comme faite, elle ne bloque aucune rotation (voir _matieres_recentes,
    qui ne regarde que les séances TERMINÉES), et elle reste la trace que notre
    sélection s'est trompée.

    Renvoie None quand il n'y a plus rien à proposer, ou après REFUS_MAX_PAR_JOUR -
    à l'appelant d'afficher alors le catalogue, qui redevient la bonne réponse.
    """
    date = date or timezone.localdate()
    seances_du_jour = list(SeanceJournaliere.objects.filter(user=user, cursus=cursus, date=date))
    if not seances_du_jour:
        return None

    courante = max(seances_du_jour, key=lambda s: s.ordre)
    if courante.statut == StatutSeance.TERMINEE:
        # Refuser une séance déjà faite n'a pas de sens - c'est "continuer" qu'il
        # voulait (voir seance_supplementaire), et l'écran ne propose de toute façon
        # pas ce bouton dans cet état.
        return courante
    if sum(1 for s in seances_du_jour if s.statut == StatutSeance.REMPLACEE) >= REFUS_MAX_PAR_JOUR:
        return None

    proposition = _construire_seance(
        user, cursus,
        themes_interdits={s.theme_id for s in seances_du_jour if s.theme_id},
        # On ne se calibre pas deux fois dans la même journée.
        avec_calibrage=False,
    )
    # Rien trouvé : on garde la séance en cours plutôt que de laisser l'élève sans
    # rien. Marquer REMPLACEE avant d'avoir un remplaçant le laisserait devant un
    # écran vide - d'où cet ordre, et pas l'inverse.
    if proposition is None:
        return None

    remplacante, creee = SeanceJournaliere.objects.get_or_create(
        user=user, cursus=cursus, date=date, ordre=courante.ordre + 1, defaults=proposition,
    )
    if creee:
        courante.statut = StatutSeance.REMPLACEE
        courante.save(update_fields=["statut"])
    return remplacante


# Coefficient à partir duquel on le cite comme raison : au-dessus du coefficient par
# défaut, sinon la phrase "coefficient 2" ne distingue rien - c'est la valeur la plus
# répandue du corpus (voir COEFFICIENT_PAR_DEFAUT).
COEFFICIENT_REMARQUABLE_MIN = COEFFICIENT_PAR_DEFAUT + 0.5


def raisons_de_la_seance(seance):
    """
    Pourquoi CETTE séance et pas une autre, en phrases vérifiables.

    Le produit repose entièrement sur la crédibilité de sa recommandation : un élève
    qui ne comprend pas pourquoi on lui propose ce thème n'a aucune raison de nous
    croire plutôt que de retourner choisir lui-même. Chaque ligne renvoyée ici est un
    fait déjà en base - une fréquence comptée, un coefficient transcrit d'une épreuve,
    une réponse qu'il a lui-même ratée - jamais une reformulation de l'intention.

    Volontairement AUCUNE raison inventée quand on ne sait pas : mieux vaut une seule
    ligne vraie que trois lignes dont une est devinée. La fréquence à l'examen n'est
    pas reprise ici - elle a déjà son badge (voir _frequence_du_theme), et la répéter
    ferait du remplissage.

    Renvoie une liste de dicts {code, texte} : le code pilote l'icône côté frontend,
    le texte est écrit ici parce qu'il dépend de chiffres que seul le serveur a.
    """
    raisons = []

    if seance.origine == OrigineSeance.DIAGNOSTIC:
        return [{
            "code": "calibrage",
            "texte": "On ne sait pas encore où tu en es - ces questions servent à le situer.",
        }]

    if seance.subject_id and seance.cursus_id:
        coefficient = _coefficient_par_subject(seance.cursus).get(seance.subject_id)
        if coefficient and coefficient >= COEFFICIENT_REMARQUABLE_MIN:
            # Coefficient tel que transcrit sur les épreuves de ce cursus (voir
            # _coefficient_par_subject) - jamais un barème que nous aurions décidé.
            valeur = int(coefficient) if coefficient == int(coefficient) else coefficient
            raisons.append({
                "code": "coefficient",
                "texte": f"{seance.subject.label} est coefficient {valeur} à ton examen.",
            })

    if seance.subject_id and seance.cursus_id:
        objectif = objectif_matiere_actif(seance.user, seance.cursus)
        if objectif is not None and objectif.subject_id == seance.subject_id:
            raisons.append({
                "code": "objectif",
                "texte": f"Tu as choisi de te concentrer sur {seance.subject.label} jusqu'au {objectif.jusqu_au:%d/%m}.",
            })

    if seance.origine == OrigineSeance.REVISION_DUE and seance.theme_id:
        dernier_echec = (
            QuizAnswer.objects.filter(
                quiz_question__session__user=seance.user,
                quiz_question__competence_item__theme_id=seance.theme_id,
            )
            .exclude(resultat_declare=ResultatDeclare.REUSSI)
            .order_by("-answered_at")
            .first()
        )
        if dernier_echec is not None:
            jours = (timezone.localdate() - timezone.localtime(dernier_echec.answered_at).date()).days
            quand = "aujourd'hui" if jours == 0 else ("hier" if jours == 1 else f"il y a {jours} jours")
            raisons.append({"code": "echec", "texte": f"Tu as raté ce thème {quand}."})
        else:
            raisons.append({"code": "echec", "texte": "Ce thème t'a déjà posé problème."})

    elif seance.origine == OrigineSeance.LECTURE_EN_COURS:
        raisons.append({"code": "lecture", "texte": "Tu as ouvert ce cours il y a moins de deux jours."})

    if seance.origine != OrigineSeance.LECTURE_EN_COURS and _theme_deja_maitrise(
        seance.user, seance.cursus, seance.theme,
    ):
        # Dit pourquoi l'étape "méthode" manque : sans cette ligne, une séance sans
        # cours ressemble à un contenu qui manque plutôt qu'à une reconnaissance.
        raisons.append({
            "code": "maitrise",
            "texte": "Tu réussis déjà ce thème : on passe directement à la pratique.",
        })

    elif seance.theme_id:
        # Jamais répondu sur ce thème : c'est là qu'il y a le plus à gagner, et c'est
        # exactement ce que le parcours cherche en premier (voir _seance_depuis_parcours).
        deja_repondu = QuizAnswer.objects.filter(
            quiz_question__session__user=seance.user,
            quiz_question__competence_item__theme_id=seance.theme_id,
        ).exists()
        if not deja_repondu:
            raisons.append({"code": "jamais", "texte": "Tu ne l'as encore jamais travaillé."})

    return raisons


def prochaine_revision(seance):
    """
    Date à laquelle ce thème doit revenir (voir RevisionSchedule et les paliers de
    LEITNER_INTERVALS_JOURS) - le chiffre existait déjà, il n'était simplement jamais
    montré. Le dire en fin de séance ferme la boucle : l'élève sait que ce qu'il vient
    de rater lui reviendra, et n'a donc rien à noter de son côté.

    None quand il n'y a pas d'échéance : un thème jamais raté n'entre pas dans la file,
    et un thème gradué en sort (voir enregistrer_resultat_pour_revision). Dans les deux
    cas, annoncer une révision serait faux.
    """
    if not seance.theme_id:
        return None
    schedule = RevisionSchedule.objects.filter(
        user=seance.user, cursus=seance.cursus, theme_id=seance.theme_id,
    ).first()
    return schedule.due_at if schedule else None


def ajuster_duree_seance(user, cursus, minutes, date=None):
    """
    "Combien de temps as-tu ?" - recompose la séance du jour pour le temps que l'élève
    se donne, sans changer de thème.

    Un plan quotidien qui impose 25 minutes ne sert à rien les jours où l'élève en a
    dix : il ne fait rien du tout plutôt que moins. Le thème, lui, ne bouge pas - c'est
    la promesse de la journée, seule sa mise en œuvre se resserre ou s'étire (voir
    _construire_etapes pour la composition de chaque budget).

    Renvoie la séance, inchangée si la durée demandée n'est pas proposée, si la séance
    est déjà terminée, ou si le nouveau budget ne permet plus de vérifier quoi que ce
    soit (voir _contient_quiz) - mieux vaut garder la séance qui marche que la casser
    pour respecter un chiffre.
    """
    seance = seance_du_jour(user, cursus, date)
    if seance is None or minutes not in BUDGETS_SEANCE_MINUTES:
        return seance
    if seance.statut != StatutSeance.PROPOSEE or seance.budget_minutes == minutes:
        return seance

    etapes = _construire_etapes(
        cursus, seance.subject, theme=seance.theme, savoir=seance.savoir,
        cours_impose=seance.cours, budget_minutes=minutes, user=user,
    )
    if not _contient_quiz(etapes):
        return seance

    seance.etapes = etapes
    seance.budget_minutes = minutes
    seance.save(update_fields=["etapes", "budget_minutes"])
    return seance


def exercices_du_theme(cursus, subject, theme):
    """
    Combien d'exercices d'examen traitent ce thème, en tout - le chiffre qui justifie
    le lien "les 33 exercices sur ce thème" sous l'étape d'entraînement.

    La séance n'en propose qu'un ou deux (voir EXERCICES_PAR_SEANCE_MAX) : c'est un
    plafond de temps, pas une limite de contenu. Sans ce chiffre, l'élève n'a aucune
    idée de la profondeur disponible et croit que c'est tout ce qu'on a.
    """
    if theme is None or subject is None:
        return 0
    return len({
        (lesson_id, numero)
        for lesson_id, numero in Question.objects.filter(
            themes=theme, exercise__lesson__statut=StatutContenu.VALIDE,
            exercise__lesson__subject=subject, exercise__lesson__cursus=cursus,
        ).values_list("exercise__lesson_id", "exercise__numero_exercice")
    })
