import random
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from access.models import LectureProgress
from catalog.models import Cours, Difficulte, StatutContenu, Subject
from programme.models import Module

# Miroir volontaire de lib/maitrise.ts SEUIL_MAITRISE (frontend) - resume_parcours a
# besoin de classer chaque savoir pour produire un histogramme (voir sa docstring), ce
# que construire_parcours ne fait jamais (il ne renvoie que des taux bruts, le
# classement restant une décision d'affichage). Aucun partage de constante possible
# entre les deux bases de code : si l'une change, l'autre doit suivre à la main.
SEUIL_MAITRISE = 70

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
    apparaît quand même (`cours=None`, `has_quiz=False`) plutôt que d'être masqué - la
    structure du programme doit rester visible même incomplète (cas du BEPC
    aujourd'hui), pas seulement les savoirs déjà couverts. C'est au frontend de
    griser une étape sans contenu, jamais à cette fonction de la faire disparaître.
    """
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
            # Le premier Cours publié qui couvre ce savoir (voir Cours.tags ->
            # Tag.savoir_officiel) - même relation que le niveau 2 de
            # quiz.views._cours_pour_competence, ici interrogée directement par
            # Savoir plutôt que déduite d'un CompetenceItem particulier.
            cours = (
                Cours.objects.visibles()
                .filter(subject=subject, tags__savoir_officiel=savoir)
                .filter(Q(cursus=cursus) | Q(cursus__isnull=True))
                .distinct()
                .order_by("id")
                .first()
            )
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
                "cours": {"slug": cours.slug, "titre": cours.titre} if cours else None,
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
