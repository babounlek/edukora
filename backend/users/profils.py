"""
Le profil actif d'une requête - la personne qui étudie, distincte du compte connecté
(voir la docstring de `users.models.Profil`).

`profil_actif(request)` est LE point d'entrée que toute vue "par élève" doit appeler
- jamais `request.user.profils.first()` directement ailleurs, pour que le jour où la
bascule de profil (JWT + `POST /auth/profils/<id>/activer/`) existe, un seul endroit
change. Pour l'instant, avant cette bascule, un compte a par construction un seul
profil actif possible : celui-là.
"""


def profil_actif(request):
    """
    Le profil sur lequel porte cette requête. Aujourd'hui : toujours le premier
    profil du compte connecté (`request.user.profils.first()`), puisqu'aucun
    mécanisme ne permet encore d'en choisir un autre - un compte n'a jamais qu'un
    seul profil tant qu'il n'en a pas ajouté volontairement un second, et aucune vue
    n'existe encore pour en ajouter un. Une fois la bascule de profil en place (claim
    `profil_id` du token, voir le plan), c'est ICI et seulement ici que la lecture de
    cette claim remplacera le `.first()` - aucun appelant n'aura à changer.

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
    return request.user.profils.first()
