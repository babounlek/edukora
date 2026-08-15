import random
from datetime import timedelta

from django.utils import timezone

from catalog.models import Difficulte, StatutContenu

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


def _items_eligibles(cursus, subject=None, theme=None):
    """
    Source unique du Mode Quiz depuis la bascule : CompetenceItem, jamais
    catalog.Question. Contrairement à l'ancien pool (Question extraite d'un Exercise,
    filtrée après coup par Question.references_missing_figure faute de mieux), un
    CompetenceItem est écrit dès l'origine pour se suffire seul - aucun filtre de
    rattrapage n'est nécessaire ici : statut=VALIDE est la seule porte d'entrée.
    """
    qs = CompetenceItem.objects.filter(statut=StatutContenu.VALIDE, cursus=cursus).distinct()
    if subject:
        qs = qs.filter(subject=subject)
    if theme:
        qs = qs.filter(theme=theme)
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


def generer_session(user, cursus, mode, subject=None, theme=None, n=10):
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
    """
    items = _items_eligibles(cursus, subject=subject, theme=theme)
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
