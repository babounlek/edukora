"""
Le profil actif d'une requête - la personne qui étudie, distincte du compte connecté
(voir la docstring de `users.models.Profil`).

`profil_actif(request)` est LE point d'entrée que toute vue "par élève" doit appeler
- jamais `request.user.profils.first()` directement ailleurs, précisément pour que
tout ce qui lit la claim `profil_id` du token (voir `activer_profil_view`) tienne en
un seul endroit.
"""


def profil_actif(request):
    """
    Le profil sur lequel porte cette requête.

    Lit d'abord la claim `profil_id` de l'access token (posée par
    `POST /auth/profils/<id>/activer/`, voir `users.views.activer_profil_view`) -
    `request.auth` est l'`AccessToken` validé par `JWTAuthentication`, qui expose ses
    claims en accès dict (`.get()`). Retombe sur `request.user.profils.first()` dès
    que cette claim est absente, invalide, ou pointe sur un profil n'appartenant plus
    à ce compte - jamais d'erreur, toujours un repli silencieux : c'est exactement le
    comportement d'avant cette bascule, celui que voit encore l'immense majorité des
    comptes (un seul profil, jamais de claim posée) et celui des appels de test qui
    authentifient via `force_authenticate(user=...)` sans `token=` (`request.auth`
    reste alors `None`).

    Ne renvoie jamais None pour un compte normalement créé : la migration de
    backfill (0012) garantit qu'aucun compte existant n'en est dépourvu, et
    `UserManager._create_user` (chemin unique de création d'un compte, voir sa
    docstring) en crée un par défaut pour tout nouveau compte, quel que soit le
    fournisseur (OTP, Google, e-mail, admin, script).

    Renvoie None pour un visiteur anonyme (`AnonymousUser` n'a pas de `.profils`) -
    plusieurs vues per-élève (ex. catalog.views, `AllowAny`) restent accessibles sans
    connexion, avec un simple repli sur "rien à lire/écrire pour ce visiteur".
    """
    if not request.user.is_authenticated:
        return None
    auth = getattr(request, "auth", None)
    profil_id = auth.get("profil_id") if auth else None
    if profil_id:
        profil = request.user.profils.filter(pk=profil_id).first()
        if profil is not None:
            return profil
    return request.user.profils.first()
