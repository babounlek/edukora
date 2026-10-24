"""
Erreurs d'envoi d'un code de connexion (SMS ou e-mail) : un message en français pour les
journaux et les anciens clients, MAIS aussi un code machine et, quand on le sait, la durée
d'attente. C'est le frontend qui écrit la phrase, dans la langue de la page : le serveur ne
connaît pas la langue de l'écran (test élève 2026-10-24 : « Merci de patienter… » en français
sur une page anglaise, sans dire combien de temps attendre).
"""

# Un code a été envoyé il y a moins d'une minute : `retry_after` = secondes restantes.
CODE_RENVOI_TROP_TOT = "code_renvoi_trop_tot"
# Trop de demandes depuis cette connexion (plafond par IP) : `retry_after` = secondes.
CODE_TROP_DE_DEMANDES = "code_trop_de_demandes"
# Le service d'envoi ne répond pas (panne du fournisseur ou plafond global) : `retry_after` quand on sait.
CODE_ENVOI_INDISPONIBLE = "envoi_indisponible"


class ErreurEnvoiCode(Exception):
    """Base des erreurs d'envoi de code : porte `code` et `retry_after` (secondes, ou None)."""

    code = CODE_ENVOI_INDISPONIBLE

    def __init__(self, message="", *, code=None, retry_after=None):
        super().__init__(message)
        if code is not None:
            self.code = code
        self.retry_after = retry_after
