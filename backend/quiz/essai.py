"""
Essai gratuit du Quiz pour un visiteur SANS compte : les thèmes cochés CompetenceItem.est_vitrine
(voir la commande definir_quiz_vitrine) se jouent en entier, sans connexion.

Aucune QuizSession ici : une session appartient à un profil, et un visiteur n'en a pas. Le serveur
ne garde donc rien - il tire les items, puis corrige à la demande, une question à la fois. Le
navigateur conserve le quiz en cours (voir frontend/src/lib/quizEssai.ts) et calcule le score.
Conséquences assumées : pas d'XP, pas de série, pas de file de révision, pas de PDF - ce qui
n'existe que pour un élève connu.

Ce que le visiteur ne reçoit JAMAIS : un item qui n'est pas entièrement vitrine. Chaque route
revérifie, indépendamment du client, que l'item (ou le périmètre entier) est gratuit. Même
principe que quiz.views.start_session pour un connecté non abonné.
"""
import random

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from catalog.models import Cursus, Examen, StatutContenu, Subject, Tag, TypeReponse

from .models import CompetenceItem, ModeQuiz, ResultatDeclare
from .gratuits import themes_gratuits_par_matiere
from .services import _items_eligibles, perimetre_est_vitrine
from .views import _competence_item_corrige, _cursus_display

# Même ordre pédagogique que le frontend (lib/cursus.ts, EXAMEN_ORDER) : collège, intermédiaire, lycée, puis le GCE.
ORDRE_EXAMENS = {
    code: i for i, code in enumerate([Examen.BEPC, Examen.PROBATOIRE, Examen.BAC, Examen.GCE_OL, Examen.GCE_AL])
}

# Un thème offert compte 5 à 9 items : 15 laisse de la marge sans autoriser de gros tirages.
ESSAI_N_MAX = 15
ESSAI_N_DEFAUT = 10


class EssaiThrottle(SimpleRateThrottle):
    """Plafond par adresse IP (par compte si connecté) : ces routes sont publiques et chacune
    lit la base. 120 par minute laissent passer un élève qui enchaîne, pas un robot. Le taux est
    porté par la classe, comme pour recherche.views.RechercheThrottle."""

    scope = "quiz_essai"
    rate = "120/min"

    def get_cache_key(self, request, view):
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


def _payload_item(item, ordre, cursus_id, reponse=None):
    """Même forme que quiz.views._question_payload pour un CompetenceItem, dont l'`id` est celui de
    l'item lui-même (il n'y a pas de QuizQuestion). Le corrigé n'y figure que si `reponse` est
    fournie : jamais avant que le visiteur ait répondu."""
    payload = {
        "id": item.id,
        "ordre": ordre,
        "enonce_markdown": item.enonce_markdown,
        "type_reponse": item.type_reponse,
        "choix": item.choix,
        "theme": item.theme.name,
        "theme_id": item.theme_id,
        "subject_code": item.subject.code,
        "subject_label": item.subject.label,
    }
    if reponse is not None:
        payload["corrige_markdown"] = _competence_item_corrige(item, [cursus_id])
        payload["reponse_correcte"] = item.reponse_correcte
        payload["reponse"] = reponse
    return payload


def _item_gratuit(request, source):
    """L'item demandé, à condition qu'il soit publié, dans le cursus annoncé d'un pays actif ET du
    quiz gratuit retenu pour sa matière dans ce cursus (un seul par matière et par cursus, voir
    quiz.gratuits) - 404 sinon, sans distinguer « n'existe pas » de « n'est pas gratuit »."""
    item = get_object_or_404(
        CompetenceItem.objects.select_related("theme", "subject"),
        pk=source.get("item"), cursus=source.get("cursus"), cursus__country__actif=True,
        statut=StatutContenu.VALIDE, est_vitrine=True,
    )
    retenus = {(g["subject"], g["theme"]) for g in themes_gratuits_par_matiere([_entier(source.get("cursus"))])}
    if (item.subject_id, item.theme_id) not in retenus:
        raise Http404
    return item


def _entier(valeur):
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return None


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([EssaiThrottle])
def liste_essais(request):
    """
    GET /quiz/essais/ - les essais gratuits proposables : UN thème par (cursus, matière), le plus
    fréquent aux épreuves du cursus (voir quiz.gratuits.themes_gratuits_par_matiere - sans ce tri,
    les items partagés entre cursus empilaient plusieurs thèmes de la même matière).
    """
    actifs = list(Cursus.objects.filter(country__actif=True).values_list("id", flat=True))
    complets = [(g["cursus"], g["subject"], g["theme"], g["nb_questions"]) for g in themes_gratuits_par_matiere(actifs)]

    cursus = {c.id: c for c in Cursus.objects.filter(id__in={c[0] for c in complets}).select_related("country", "series")}
    matieres = {s.id: s for s in Subject.objects.filter(id__in={c[1] for c in complets})}
    themes = {t.id: t for t in Tag.objects.filter(id__in={c[2] for c in complets})}

    essais = [
        {
            # `langue` (fr | en, dérivée de l'examen) : le frontend ne propose que les essais de la langue de
            # l'interface (voir lib/cursusLangue.ts) - un visiteur en anglais n'a pas à voir « BAC - A » d'abord.
            "cursus": c, "cursus_display": _cursus_display(cursus[c]), "langue": cursus[c].langue,
            "subject": s, "subject_label": matieres[s].label, "subject_code": matieres[s].code,
            "theme": t, "theme_name": themes[t].name, "nb_questions": n,
        }
        for c, s, t, n in complets
    ]
    # L'ordre des cursus est celui du parcours scolaire (BEPC, Probatoire, BAC, puis le GCE), puis la série - ni
    # alphabétique, qui ouvrait la liste sur « BAC - A » et reléguait le BEPC en 6e pastille (test élève P1), ni celui des ids.
    rang = {
        c.id: i
        for i, c in enumerate(sorted(cursus.values(), key=lambda x: (ORDRE_EXAMENS.get(x.examen, len(ORDRE_EXAMENS)), x.examen, x.series.code if x.series else "")))
    }
    essais.sort(key=lambda e: (rang[e["cursus"]], e["subject_label"]))
    return Response(essais)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([EssaiThrottle])
def demarrer_essai(request):
    """
    POST /quiz/essais/demarrer/ {cursus, subject?, theme, n?} - tire les questions d'un essai gratuit. Même
    forme de réponse qu'une QuizSession (id 0 : rien n'est enregistré) pour que le lecteur de quiz
    du frontend la lise telle quelle. 403 si le périmètre demandé n'est pas ENTIÈREMENT gratuit.
    """
    cursus = get_object_or_404(Cursus.objects.select_related("country", "series"), pk=_entier(request.data.get("cursus")))
    if not cursus.country.actif:
        return Response({"error": "Ce cursus n'est pas disponible."}, status=404)

    subject_id, theme_id = _entier(request.data.get("subject")), _entier(request.data.get("theme"))
    subject = get_object_or_404(Subject, pk=subject_id) if subject_id else None
    theme = get_object_or_404(Tag, pk=theme_id) if theme_id else None

    if not perimetre_est_vitrine(cursus, subject=subject, theme=theme):
        return Response({"error": "Cet essai n'est pas gratuit : abonnement requis."}, status=403)

    n = min(max(_entier(request.data.get("n")) or ESSAI_N_DEFAUT, 1), ESSAI_N_MAX)
    items = _items_eligibles(cursus, subject=subject, theme=theme)
    tires = random.sample([i.id for i in items], min(n, len(items)))
    par_id = CompetenceItem.objects.filter(pk__in=tires).select_related("theme", "subject").in_bulk()
    selection = [par_id[i] for i in tires]
    return Response({
        "id": 0,
        "essai": True,
        "mode": ModeQuiz.PRATIQUE,
        "cursus": cursus.id,
        "subject": subject.id if subject else None,
        "cursus_display": _cursus_display(cursus),
        "started_at": timezone.now(),
        "completed_at": None,
        "total_questions": len(selection),
        "questions": [_payload_item(item, ordre, cursus.id) for ordre, item in enumerate(selection, start=1)],
    }, status=201)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([EssaiThrottle])
def corrige_essai(request):
    """GET /quiz/essais/corrige/?cursus=&item= - le corrigé d'une question ouverte, avant que le
    visiteur ne s'auto-évalue (comme quiz.views.reveal_corrige pour une session)."""
    item = _item_gratuit(request, request.GET)
    return Response({
        "corrige_markdown": _competence_item_corrige(item, [_entier(request.GET.get("cursus"))]),
        "reponse_correcte": item.reponse_correcte,
    })


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([EssaiThrottle])
def repondre_essai(request):
    """
    POST /quiz/essais/repondre/ {cursus, item, reponse_choisie | resultat_declare} - corrige une
    réponse, sans rien enregistrer. QCM : comparaison objective à reponse_correcte ; question
    ouverte : auto-évaluation du visiteur après avoir vu le corrigé (voir QuizAnswer.est_correcte).
    """
    item = _item_gratuit(request, request.data)
    cursus_id = _entier(request.data.get("cursus"))

    if item.type_reponse == TypeReponse.QCM:
        choisie = str(request.data.get("reponse_choisie") or "")
        if not choisie:
            return Response({"error": "reponse_choisie est requis pour une question QCM."}, status=400)
        reponse = {
            "reponse_choisie": choisie, "resultat_declare": "",
            "est_correcte": choisie == item.reponse_correcte, "xp_gagne": 0,
        }
    else:
        resultat = request.data.get("resultat_declare")
        if resultat not in ResultatDeclare.values:
            return Response(
                {"error": f"resultat_declare invalide : {resultat!r}. Attendu {ResultatDeclare.values}."}, status=400,
            )
        reponse = {
            "reponse_choisie": "", "resultat_declare": resultat,
            "est_correcte": resultat == ResultatDeclare.REUSSI, "xp_gagne": 0,
        }
    return Response(_payload_item(item, _entier(request.data.get("ordre")) or 0, cursus_id, reponse))
