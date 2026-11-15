"""
« Mes réussites » (R12, audit produit 2026-11-13) : les jalons atteints et le prochain, pour qu'une récompense se garde.

Rien n'est stocké : chaque jalon se relit sur un FAIT d'étude (une réponse juste, un examen blanc rendu, des thèmes solides,
le record de série), jamais sur un compteur de connexions. Un jalon atteint ne se perd donc pas : les faits sont durables,
et le record de série ne baisse jamais. Chaque jalon a un `code` (le texte est côté interface, par langue), une `valeur`
actuelle, une `cible` et `obtenu`.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from inedit.defi import defis_releves
from simulations.models import SimulationEpreuve
from users.profils import profil_actif

from . import serie, xp
from .models import QuizAnswer
from .services import est_maitrise, maitrise_par_theme

# (code, famille, cible). L'ordre est celui de l'affichage, famille par famille.
JALONS = (
    ("premier_quiz", "quiz", 1),
    ("bonnes_100", "quiz", 100),
    ("bonnes_500", "quiz", 500),
    ("themes_solides_10", "themes", 10),
    ("themes_solides_25", "themes", 25),
    ("premier_examen_blanc", "examens", 1),
    ("examens_blancs_5", "examens", 5),
    ("premier_defi", "defis", 1),
    ("defis_4", "defis", 4),
    ("serie_7", "serie", 7),
    ("serie_30", "serie", 30),
)


def _valeurs(profil):
    reponses = QuizAnswer.objects.filter(
        quiz_question__session__profil=profil,
        quiz_question__session__rejeu_de__isnull=True,
        quiz_question__session__chrono_actif=False,
    ).select_related("quiz_question")
    total = bonnes = 0
    for reponse in reponses:
        total += 1
        bonnes += 1 if reponse.est_correcte else 0
    themes_solides = sum(1 for t in maitrise_par_theme(profil) if est_maitrise(t["taux"], t["total"]))
    examens = SimulationEpreuve.objects.filter(profil=profil, submitted_at__isnull=False).count()
    etat_serie = serie.serie_de_jours(profil)
    return {
        "quiz": total, "bonnes": bonnes, "themes": themes_solides, "examens": examens,
        "defis": defis_releves(profil),
        "serie": etat_serie["record"],
    }, etat_serie


def _valeur_du_jalon(code, famille, valeurs):
    if code.startswith("bonnes_"):
        return valeurs["bonnes"]
    return valeurs[famille]


def reussites_du_profil(profil):
    valeurs, etat_serie = _valeurs(profil)
    jalons = []
    for code, famille, cible in JALONS:
        valeur = _valeur_du_jalon(code, famille, valeurs)
        jalons.append({"code": code, "famille": famille, "cible": cible, "valeur": min(valeur, cible), "obtenu": valeur >= cible})
    prochain = next((j for j in jalons if not j["obtenu"]), None)
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
