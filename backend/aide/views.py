from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from .code_assistance import code_pour
from .models import ArticleAide


class AideThrottle(SimpleRateThrottle):
    """Plafond par compte (ou par adresse pour un visiteur) : route publique, mais bon marché."""

    scope = "aide"
    rate = "120/min"

    def get_cache_key(self, request, view):
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


def _langue(request):
    return "en" if (request.query_params.get("langue") or "").lower() == "en" else "fr"


def _champ(article, nom, langue):
    """Le texte dans la langue demandée, ou le français s'il n'est pas (encore) traduit - jamais un champ vide."""
    if langue == "en":
        valeur = getattr(article, f"{nom}_en")
        if valeur:
            return valeur
    return getattr(article, f"{nom}_fr")


def _resume(article, langue):
    return {
        "slug": article.slug,
        "categorie": article.categorie,
        "titre": _champ(article, "titre", langue),
        "resume": _champ(article, "resume", langue),
        "mots_cles": _champ(article, "mots_cles", langue),
        "populaire": article.populaire,
        "pages": article.pages(),
        "traduit": article.traduit,
    }


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([AideThrottle])
def liste_articles(request):
    """
    GET /aide-api/articles/[?langue=fr|en]

    Tous les articles publiés, SANS leur corps : une trentaine de lignes courtes que le frontend garde en
    mémoire pour chercher (sans accent, sans réseau) dans les titres, résumés et mots-clés. Le texte d'un
    article se lit à part (`detail_article`).
    """
    langue = _langue(request)
    articles = ArticleAide.objects.filter(publie=True)
    return Response([_resume(article, langue) for article in articles])


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@throttle_classes([AideThrottle])
def detail_article(request, slug):
    langue = _langue(request)
    try:
        article = ArticleAide.objects.get(slug=slug, publie=True)
    except ArticleAide.DoesNotExist:
        return Response({"error": "Article introuvable."}, status=404)
    donnees = _resume(article, langue)
    donnees["corps"] = _champ(article, "corps", langue)
    donnees["maj_le"] = article.maj_le.date().isoformat()
    # Voisins : les autres articles de la même rubrique, dans l'ordre éditorial.
    voisins = ArticleAide.objects.filter(publie=True, categorie=article.categorie).exclude(pk=article.pk)[:4]
    donnees["voisins"] = [_resume(v, langue) for v in voisins]
    return Response(donnees)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def mon_code(request):
    """GET /aide-api/mon-code/ : le code d'assistance du compte connecté, à glisser dans un message au support."""
    return Response({"code": code_pour(request.user.pk)})
