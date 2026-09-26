"""
Registre des agrégateurs de paiement. Le fournisseur par défaut se règle par
settings.PAYMENT_PROVIDER (env PAYMENT_PROVIDER, "campay" par défaut) ; une Transaction
mémorise le sien (Transaction.provider) pour que son suivi de statut reste correct même
après un changement de fournisseur par défaut.
"""

from django.conf import settings

from .base import PaiementFournisseurError, PaymentProvider, ResultatInitiation, ResultatStatut, StatutPaiement
from .campay import CampayProvider

_REGISTRE = {
    CampayProvider.name: CampayProvider,
}


def get_provider(name=None) -> PaymentProvider:
    name = name or getattr(settings, "PAYMENT_PROVIDER", "campay")
    try:
        return _REGISTRE[name]()
    except KeyError:
        raise PaiementFournisseurError(f"Fournisseur de paiement inconnu : {name!r}.") from None


def fournisseur_par_defaut() -> str:
    return getattr(settings, "PAYMENT_PROVIDER", "campay")


__all__ = [
    "PaiementFournisseurError", "PaymentProvider", "ResultatInitiation", "ResultatStatut",
    "StatutPaiement", "get_provider", "fournisseur_par_defaut",
]
