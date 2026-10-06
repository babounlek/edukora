from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from catalog.models import Country

from . import moteur


class RechercheThrottle(SimpleRateThrottle):
    """
    Plafond par compte (ou par adresse IP pour un visiteur) : la recherche est la route publique
    la plus coûteuse (un balayage de l'index à chaque appel), et le champ de saisie en lance une à
    chaque pause de frappe. 240 par minute laissent passer un élève qui tape vite, pas un robot.
    Le taux est porté par la classe (attribut `rate`) : aucun réglage global à ajouter.
    """

    scope = "recherche"
    rate = "240/min"

    def get_cache_key(self, request, view):
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


def _entier(valeur):
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return None


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([RechercheThrottle])
def rechercher(request):
    """
    GET /recherche/?q=...&pays=cm[&cursus=<id>][&matiere=<code>][&type=COURS][&limite=][&decalage=]
                          [&elargir=true][&exact=true][&sans=cursus,annee][&rapide=true]

    Ouverte aux visiteurs anonymes (la recherche sert aussi à décider de s'abonner) : elle ne
    renvoie que de l'identité de contenu (titre, matière, examen, année), jamais un corrigé - voir
    recherche.models.EntreeRecherche. `rapide=true` : appel de saisie en direct, jamais compté dans
    le journal des recherches sans résultat (voir recherche.moteur.journaliser_vide).
    """
    params = request.query_params
    pays = Country.objects.filter(code__iexact=params.get("pays", ""), actif=True).first()
    if pays is None:
        return Response({"error": "Pays inconnu ou indisponible."}, status=400)

    type_ = (params.get("type") or "").upper() or None
    matiere = params.get("matiere") or None
    decalage = _entier(params.get("decalage")) or 0
    reponse = moteur.chercher(
        params.get("q", ""), pays=pays, utilisateur=request.user, cursus=_entier(params.get("cursus")),
        matiere=matiere, type_=type_, limite=_entier(params.get("limite")) or moteur.LIMITE_DEFAUT,
        decalage=decalage, elargir=params.get("elargir") == "true", corriger_auto=params.get("exact") != "true",
        sans=[p for p in params.get("sans", "").split(",") if p],
    )

    # Un zéro n'est un manque du catalogue que s'il ne vient pas d'un filtre : ni type ni matière
    # choisis, et rien de proposé dans les autres examens.
    manque_du_catalogue = (
        reponse["total"] == 0 and reponse["indexe"] and not reponse["trop_court"] and reponse["q"]
        and not type_ and not matiere and not decalage and reponse["autres_cursus"] == 0
    )
    if manque_du_catalogue and params.get("rapide") != "true":
        moteur.journaliser_vide(reponse["q"], pays.code)
    return Response(reponse)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([RechercheThrottle])
def completer(request):
    """
    GET /recherche/completer/?q=...&pays=cm[&cursus=<id>]

    Ce que l'élève est peut-être en train d'écrire (voir recherche.moteur.completer) : une poignée
    d'intitulés de thèmes, appelée à chaque pause de frappe. Même plafond d'appels que la recherche.
    """
    pays = Country.objects.filter(code__iexact=request.query_params.get("pays", ""), actif=True).first()
    if pays is None:
        return Response({"error": "Pays inconnu ou indisponible."}, status=400)
    completions = moteur.completer(
        request.query_params.get("q", ""), pays=pays, cursus=_entier(request.query_params.get("cursus")),
    )
    return Response({"completions": completions})
