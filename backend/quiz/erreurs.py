"""
« Mes erreurs » : les questions de quiz que l'élève a ratées et pas encore réussies.

Une question est dans la banque tant que sa DERNIÈRE réponse est fausse (une question ouverte
déclarée « partiel » ou « échec » compte comme fausse, voir QuizAnswer.est_correcte). Elle en
sort d'elle-même à la première bonne réponse : rien n'est stocké, la banque se relit sur
l'historique des réponses (voir quiz.services._historique_des_items, mêmes exclusions que la
maîtrise - ni rejeu, ni quiz chronométré).

Pourquoi un écran à part : avant lui, refaire ses questions ratées n'existait que sur l'écran de
résultat, pour le quiz qu'on venait de finir (voir quiz.services.session_des_ratees), et plus
jamais une fois la page quittée. L'erreur n'était pas un objet de travail.

Deux gestes :
- LIRE la banque : le total, par matière et par thème (GET /quiz/erreurs/) ;
- REFAIRE un paquet : une session de quiz ordinaire (mode PRATIQUE) faite des erreurs les plus
  ANCIENNES d'abord - celles du jour sont encore fraîches, une erreur de la semaine dernière est
  celle qui dira si la correction a tenu (POST /quiz/erreurs/refaire/). Ce n'est pas un rejeu :
  c'est une remédiation réelle, elle rapporte des points et compte pour la maîtrise, comme
  « refaire les ratées » d'une session.
"""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from catalog.models import Cursus, StatutContenu, Subject
from users.profils import profil_actif

from . import textes
from .models import CompetenceItem, ModeQuiz, QuizSession
from .services import _historique_des_items, creer_questions

# Un paquet tient en une dizaine de minutes : assez pour avancer, assez court pour être relancé.
PAQUET_DEFAUT = 10
PAQUET_MAX = 20
# Les thèmes cités sous une matière : de quoi reconnaître ses lacunes, pas une liste à dérouler.
THEMES_CITES_MAX = 3


def banque_d_erreurs(profil, cursus, subject=None):
    """
    [(item, jour de la dernière réponse)] : les items encore publiés dont la dernière réponse du
    profil est fausse, de l'erreur la plus ancienne à la plus récente. Un item dépublié depuis
    n'y figure pas : on ne saurait plus le servir.
    """
    rates = {
        item_id: jour
        for item_id, (jour, reussie) in _historique_des_items(profil, cursus).items()
        if not reussie
    }
    if not rates:
        return []
    items = CompetenceItem.objects.filter(pk__in=rates, statut=StatutContenu.VALIDE).select_related("subject", "theme")
    if subject is not None:
        items = items.filter(subject=subject)
    return sorted(((item, rates[item.pk]) for item in items), key=lambda paire: (paire[1], paire[0].pk))


def compter_erreurs(profil, cursus):
    """Le nombre de questions dans la banque - pour l'accueil, qui n'a besoin que de ce chiffre."""
    return len(banque_d_erreurs(profil, cursus))


def resume_des_erreurs(profil, cursus):
    """
    La banque, résumée pour l'écran : total, taille du prochain paquet, et par matière le nombre
    d'erreurs et les thèmes où elles se concentrent. Matières et thèmes triés par nombre
    d'erreurs décroissant : ce qui pèse le plus d'abord.
    """
    banque = banque_d_erreurs(profil, cursus)
    par_matiere = {}
    for item, _jour in banque:
        matiere = par_matiere.setdefault(item.subject_id, {
            "subject_id": item.subject_id,
            "subject_code": item.subject.code,
            "subject_label": item.subject.label,
            "nb": 0,
            "_themes": {},
        })
        matiere["nb"] += 1
        theme = matiere["_themes"].setdefault(item.theme_id, {"theme_id": item.theme_id, "theme": item.theme.name, "nb": 0})
        theme["nb"] += 1

    matieres = []
    for matiere in sorted(par_matiere.values(), key=lambda m: (-m["nb"], m["subject_label"])):
        themes = sorted(matiere.pop("_themes").values(), key=lambda th: (-th["nb"], th["theme"]))
        matiere["themes"] = themes[:THEMES_CITES_MAX]
        matiere["themes_total"] = len(themes)
        matieres.append(matiere)

    return {
        "total": len(banque),
        "paquet": min(PAQUET_DEFAUT, len(banque)),
        "plus_ancienne": banque[0][1].isoformat() if banque else None,
        "matieres": matieres,
    }


def session_des_erreurs(profil, cursus, subject=None, n=PAQUET_DEFAUT):
    """
    Une session de quiz faite des `n` erreurs les plus anciennes de la banque (d'une matière si
    `subject` est donné). Lève ValueError quand la banque est vide. La session porte la matière
    quand toutes ses questions en viennent, sinon aucune - comme un quiz multi-matières.
    """
    items = [item for item, _jour in banque_d_erreurs(profil, cursus, subject)[:n]]
    if not items:
        raise ValueError("Aucune erreur à refaire.")
    matieres = {item.subject_id for item in items}
    session = QuizSession.objects.create(
        profil=profil, cursus=cursus, mode=ModeQuiz.PRATIQUE,
        subject_id=matieres.pop() if len(matieres) == 1 else None,
    )
    creer_questions(session, items)
    return session


def _cursus_demande(request, valeur):
    """Le cursus visé : celui du paramètre, sinon l'examen préparé. (cursus, réponse d'erreur)."""
    if valeur:
        return get_object_or_404(Cursus.objects.select_related("country"), pk=valeur), None
    cursus = request.user.cursus_prepare
    if cursus is None:
        return None, Response({"error": "Aucun cursus déclaré."}, status=400)
    return cursus, None


@api_view(["GET"])
def erreurs_view(request):
    """
    GET /quiz/erreurs/?cursus= - la banque d'erreurs du profil actif (voir resume_des_erreurs).
    `cursus` optionnel, par défaut l'examen préparé. Aucun abonnement exigé pour LIRE : ce sont
    les réponses de l'élève lui-même ; refaire, en revanche, suit la règle d'accès du quiz.
    """
    cursus, erreur = _cursus_demande(request, request.GET.get("cursus"))
    if erreur is not None:
        return erreur
    return Response(resume_des_erreurs(profil_actif(request), cursus))


@api_view(["POST"])
def refaire_erreurs_view(request):
    """
    POST /quiz/erreurs/refaire/ {cursus?, subject?, n?} - ouvre une session faite des erreurs les
    plus anciennes (201). Même règle d'accès que start_session, revérifiée à chaque appel :
    abonnement actif sur le cursus, SAUF si toutes les questions du paquet sont du quiz gratuit
    (est_vitrine) - même exception que « refaire les ratées » ; pays désactivé = introuvable.
    """
    from .views import _has_active_subscription, _session_payload

    cursus, erreur = _cursus_demande(request, request.data.get("cursus"))
    if erreur is not None:
        return erreur
    langue = textes.langue_de(cursus)
    if not cursus.country.actif:
        return Response({"error": textes.texte("quiz.aucune_question", langue)}, status=404)

    subject = None
    if request.data.get("subject"):
        subject = get_object_or_404(Subject, pk=request.data["subject"])
    try:
        n = int(request.data.get("n") or PAQUET_DEFAUT)
    except (TypeError, ValueError):
        return Response({"error": "Nombre de questions invalide."}, status=400)
    n = max(1, min(n, PAQUET_MAX))

    profil = profil_actif(request)
    if not _has_active_subscription(request.user, cursus, profil):
        paquet = [item for item, _jour in banque_d_erreurs(profil, cursus, subject)[:n]]
        # Banque vide : on laisse session_des_erreurs répondre « rien à refaire » (400), plutôt qu'un faux « abonnement requis ».
        if paquet and not all(item.est_vitrine for item in paquet):
            return Response({"error": "Abonnement requis pour ce cursus."}, status=403)
    try:
        session = session_des_erreurs(profil, cursus, subject, n)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)
    return Response(_session_payload(session), status=201)
