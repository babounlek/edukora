import random
import unicodedata
from collections import Counter, defaultdict
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from access.models import LectureProgress
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

# Gros corpus (BAC C/D Maths : 41-44 épreuves) : le plancher fixe de 2 laisserait
# ~390 thèmes, une liste qu'aucun élève ne parcourt jusqu'au bout. Au-delà de ce
# nombre d'épreuves, le plancher devient proportionnel (10 %, soit 5 pour 44
# épreuves) ; en dessous, le plancher fixe est conservé tel quel.
PARCOURS_FREQUENCE_GROS_CORPUS = 30
PARCOURS_FREQUENCE_PLANCHER_PCT = 10

from .models import CompetenceItem, ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, RevisionSchedule

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
    (voir Savoir.tags, et le cas réel documenté dans _cours_pour_competence côté vues) :
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

    if mince:
        plancher = 1
    elif nb_sessions >= PARCOURS_FREQUENCE_GROS_CORPUS:
        plancher = max(
            PARCOURS_FREQUENCE_OCCURRENCES_MIN, -(-nb_sessions * PARCOURS_FREQUENCE_PLANCHER_PCT // 100),
        )
    else:
        plancher = PARCOURS_FREQUENCE_OCCURRENCES_MIN

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
            # quiz.views._cours_pour_competence, ici interrogée directement par
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
        compteurs = {"maitrises": 0, "en_revision": 0, "a_decouvrir": 0, "sans_contenu": 0}
        for s in savoirs:
            if not s["has_quiz"] and not s["cours"]:
                compteurs["sans_contenu"] += 1
            elif s["taux"] is not None and s["taux"] >= SEUIL_MAITRISE:
                compteurs["maitrises"] += 1
            elif s["en_revision"]:
                compteurs["en_revision"] += 1
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
