"""
« Mes réussites » (R12, audit produit 2026-11-13) : les jalons atteints et le prochain, pour qu'une récompense se garde.

Rien n'est stocké : chaque jalon se relit sur un FAIT d'étude (une réponse juste, un examen blanc rendu, des thèmes solides,
le record de série), jamais sur un compteur de connexions. Un jalon atteint ne se perd donc pas : les faits sont durables,
et le record de série ne baisse jamais. Chaque jalon a un `code` (le texte est côté interface, par langue), une `valeur`
actuelle, une `cible` et `obtenu`.

Les premiers jalons sont RAPPROCHÉS (10 bonnes réponses, un thème solide, 3 jours de suite) : la collection s'ouvrait sur
« 100 bonnes réponses » et « 7 jours de suite », rien à décrocher pendant les deux premières semaines, celles où l'élève décide
s'il revient. Le quiz sans faute a ses jalons au lieu d'un bonus de points : il est fêté sans toucher à la règle « les points
récompensent la maîtrise, jamais le volume » (voir quiz.xp).
"""
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

from inedit.defi import defis_releves
from simulations.models import SimulationEpreuve
from users.profils import profil_actif

from . import serie, xp
from .models import CarteRevue, QuizAnswer, QuizQuestion
from .services import est_maitrise, maitrise_par_theme

# Un quiz ne compte « sans faute » qu'à partir de cette taille : c'est celle du plus court quiz proposé (5 questions, voir
# quiz.services.QUIZ_FIN_DE_SEANCE_N) ; en dessous, une ou deux questions réussies ne disent rien.
SANS_FAUTE_QUESTIONS_MIN = 5

# (code, famille, compteur, cible). L'ordre est celui de l'affichage, famille par famille, du plus proche au plus lointain.
JALONS = (
    ("premier_quiz", "quiz", "quiz", 1),
    ("bonnes_10", "quiz", "bonnes", 10),
    ("bonnes_50", "quiz", "bonnes", 50),
    ("bonnes_100", "quiz", "bonnes", 100),
    ("bonnes_500", "quiz", "bonnes", 500),
    ("sans_faute_1", "quiz", "sans_faute", 1),
    ("sans_faute_5", "quiz", "sans_faute", 5),
    ("themes_solides_1", "themes", "themes", 1),
    ("themes_solides_3", "themes", "themes", 3),
    ("themes_solides_10", "themes", "themes", 10),
    ("themes_solides_25", "themes", "themes", 25),
    ("cartes_10", "cartes", "cartes", 10),
    ("cartes_50", "cartes", "cartes", 50),
    ("erreurs_1", "erreurs", "erreurs", 1),
    ("erreurs_10", "erreurs", "erreurs", 10),
    ("erreurs_50", "erreurs", "erreurs", 50),
    ("premier_examen_blanc", "examens", "examens", 1),
    ("examens_blancs_5", "examens", "examens", 5),
    ("premier_defi", "defis", "defis", 1),
    ("defis_4", "defis", "defis", 4),
    ("serie_3", "serie", "serie", 3),
    ("serie_7", "serie", "serie", 7),
    ("serie_30", "serie", "serie", 30),
)


def _valeurs(profil):
    # Ni un rejeu ni un quiz chronométré : ils sont neutres pour les points et la maîtrise, ils le sont aussi pour les jalons.
    hors_rejeu = {"session__profil": profil, "session__rejeu_de__isnull": True, "session__chrono_actif": False}
    reponses = QuizAnswer.objects.filter(
        **{f"quiz_question__{cle}": valeur for cle, valeur in hors_rejeu.items()},
    ).select_related("quiz_question").order_by("answered_at", "pk")
    total = bonnes = 0
    bonnes_par_session = {}
    # Une erreur corrigée : une question ratée puis, plus tard, réussie (voir quiz.erreurs). Le fait reste acquis même si
    # elle est ratée de nouveau ensuite : un jalon ne se perd pas. Les réponses sont lues dans l'ordre du temps pour cela.
    ratees, corrigees = set(), set()
    for reponse in reponses:
        total += 1
        item_id = reponse.quiz_question.competence_item_id
        if reponse.est_correcte:
            bonnes += 1
            session_id = reponse.quiz_question.session_id
            bonnes_par_session[session_id] = bonnes_par_session.get(session_id, 0) + 1
            if item_id in ratees:
                corrigees.add(item_id)
        elif item_id is not None:
            ratees.add(item_id)
    # Sans faute : TOUTES les questions du quiz ont une bonne réponse - une question passée ou laissée en plan l'exclut.
    questions_par_session = dict(
        QuizQuestion.objects.filter(**hors_rejeu, session_id__in=bonnes_par_session)
        .values("session_id").annotate(n=Count("id")).values_list("session_id", "n"),
    )
    sans_faute = sum(
        1 for session_id, n in questions_par_session.items()
        if n >= SANS_FAUTE_QUESTIONS_MIN and bonnes_par_session[session_id] == n
    )
    themes_solides = sum(1 for t in maitrise_par_theme(profil) if est_maitrise(t["taux"], t["total"]))
    examens = SimulationEpreuve.objects.filter(profil=profil, submitted_at__isnull=False).count()
    etat_serie = serie.serie_de_jours(profil)
    return {
        "quiz": total, "bonnes": bonnes, "sans_faute": sans_faute, "themes": themes_solides, "examens": examens,
        # Une carte compte dès sa première revue, une fois pour toutes : c'est le nombre de cartes travaillées.
        "cartes": CarteRevue.objects.filter(profil=profil).count(),
        "erreurs": len(corrigees),
        "defis": defis_releves(profil),
        "serie": etat_serie["record"],
    }, etat_serie


def reussites_du_profil(profil):
    valeurs, etat_serie = _valeurs(profil)
    jalons = []
    for code, famille, compteur, cible in JALONS:
        valeur = valeurs[compteur]
        jalons.append({"code": code, "famille": famille, "cible": cible, "valeur": min(valeur, cible), "obtenu": valeur >= cible})
    # Le prochain jalon est le PLUS PROCHE d'être atteint, toutes familles confondues (à égalité, le premier de la liste) :
    # c'est celui qui donne envie d'une séance de plus, pas « 500 bonnes réponses » quand un thème solide est à une réponse.
    restants = [j for j in jalons if not j["obtenu"]]
    prochain = max(restants, key=lambda j: j["valeur"] / j["cible"], default=None)
    return {
        "niveau": xp.niveau_du_profil(profil),
        "jalons": jalons,
        "prochain": prochain["code"] if prochain else None,
        "serie": {"actuelle": etat_serie["jours"], "record": etat_serie["record"], "repos_pris": etat_serie["repos_pris"]},
    }


@api_view(["GET"])
def reussites_view(request):
    """GET /quiz/reussites/ - niveau, jalons, record de série du profil actif. Lecture seule, sans abonnement : ce sont ses propres faits."""
    return Response(reussites_du_profil(profil_actif(request)))
