"""
GET /catalog/accueil/?country=cm&langue=fr : ce que la vitrine de l'accueil affiche en chiffres et en témoignages, en UN
appel (audit de l'accueil du 2026-11-15, R9). Elle en faisait quatre : la liste des épreuves, celle des cours et celle des
matières, chacune pour n'en lire que le total, puis les témoignages.

Les chiffres ne sont pas recomptés ici : la vue interroge les vues des listes elles-mêmes, avec les mêmes paramètres et
la même session. Une puce « 1 565 épreuves corrigées » mène à une liste qui affiche 1 565 : recompter à part (autre
filtre de langue, inédites oubliées, matières masquées d'un abonné) finirait par dire un autre nombre que la liste.
"""
import copy

from django.http import QueryDict
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .views import CoursListView, LessonListView, SubjectListView, TemoignageListView


def _donnees(vue, request, **params):
    """Les données que `vue` répond à `request` avec ces paramètres d'adresse, sans passer par le réseau."""
    sous_requete = copy.copy(request._request)
    adresse = QueryDict(mutable=True)
    adresse.update({cle: valeur for cle, valeur in params.items() if valeur})
    sous_requete.GET = adresse
    return vue.as_view()(sous_requete).data


class AccueilView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        perimetre = {
            "country": request.query_params.get("country") or "",
            "langue": request.query_params.get("langue") or "",
        }
        return Response({
            "epreuves": _donnees(LessonListView, request, **perimetre)["count"],
            "cours": _donnees(CoursListView, request, **perimetre)["count"],
            "matieres": len(_donnees(SubjectListView, request, **perimetre)),
            "temoignages": _donnees(TemoignageListView, request),
        })
