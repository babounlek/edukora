import re

from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

# Les routes que touche un compte invité (voir users.invites) : les épreuves inédites, et la séance d'un quiz gratuit.
CHEMINS_INVITE = ("/inedit/",)

# Du quiz, UNE LISTE FINE et non `/quiz/` en bloc : démarrer une séance, répondre, la terminer, la reprendre, la rejouer,
# refaire les ratées, relire une séance passée. Parcours, plan du jour, bilan, classement, réglages... n'ont pas de sens pour
# un compte sans identité, et un jeton se rejoue à la main. Le thème jouable reste borné par start_session : sans
# abonnement, seuls les thèmes gratuits (est_vitrine) démarrent.
CHEMINS_INVITE_QUIZ = re.compile(
    r"^/quiz/(?:"
    r"sessions/"
    r"|sessions/\d+/"
    r"|sessions/\d+/questions/\d+/(?:corrige|answer)/"
    r"|sessions/\d+/(?:refaire-ratees|completer)/"
    r"|en-cours/"
    r"|historique/\d+/(?:rejouer/)?"
    r")$"
)


def chemin_ouvert_aux_invites(path: str) -> bool:
    """Vrai si un compte invité a le droit d'appeler cette route (sinon : 403, voir JWTAuthenticationAvecInvites)."""
    return path.startswith(CHEMINS_INVITE) or CHEMINS_INVITE_QUIZ.match(path) is not None


class JWTAuthenticationAvecInvites(JWTAuthentication):
    """
    JWTAuthentication, plus un cloisonnement : un compte invité n'a de droits que sur `/inedit/` et sur les routes d'une
    séance de quiz (voir CHEMINS_INVITE_QUIZ).

    Le frontend ne lui joint son jeton que sur ces routes, mais un jeton se rejoue à la main : sans ce garde, il
    ouvrirait n'importe quelle route « connectée » (parcours, profil...) avec un compte sans identité. Un refus
    net (403) plutôt qu'un 401, qui déclencherait un refresh de session pour rien.
    """

    def authenticate(self, request):
        resultat = super().authenticate(request)
        if resultat is not None:
            user = resultat[0]
            if getattr(user, "est_invite", False) and not chemin_ouvert_aux_invites(request.path):
                raise PermissionDenied("Ce compte d'essai n'ouvre que les épreuves inédites et les quiz gratuits.")
        return resultat
