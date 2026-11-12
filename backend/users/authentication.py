from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

# Les seules routes que touche un compte invité (voir users.invites) : les épreuves inédites.
CHEMINS_INVITE = ("/inedit/",)


class JWTAuthenticationAvecInvites(JWTAuthentication):
    """
    JWTAuthentication, plus un cloisonnement : un compte invité n'a de droits que sur `/inedit/`.

    Le frontend ne lui joint son jeton que sur ces routes, mais un jeton se rejoue à la main : sans ce garde, il
    ouvrirait n'importe quelle route « connectée » (quiz, parcours, profil...) avec un compte sans identité. Un refus
    net (403) plutôt qu'un 401, qui déclencherait un refresh de session pour rien.
    """

    def authenticate(self, request):
        resultat = super().authenticate(request)
        if resultat is not None:
            user = resultat[0]
            if getattr(user, "est_invite", False) and not request.path.startswith(CHEMINS_INVITE):
                raise PermissionDenied("Ce compte d'essai n'ouvre que les épreuves inédites gratuites.")
        return resultat
