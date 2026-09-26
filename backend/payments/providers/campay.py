"""Adaptateur CamPay du port PaymentProvider. Traduit uniquement ; la logique HTTP reste dans payments.campay_client."""

import logging

from payments import campay_client

from .base import PaymentProvider, PaiementFournisseurError, ResultatInitiation, ResultatStatut, StatutPaiement

logger = logging.getLogger(__name__)

# Statuts documentés par CamPay -> statuts Edukora. Tout statut absent de cette table
# est traité comme PENDING (et journalisé) : mieux vaut relancer un polling qu'écrire en
# base un statut inconnu, ou pire, activer un accès sur une valeur mal comprise.
_STATUTS = {
    "PENDING": StatutPaiement.PENDING,
    "SUCCESSFUL": StatutPaiement.SUCCESSFUL,
    "FAILED": StatutPaiement.FAILED,
}


class CampayProvider(PaymentProvider):
    name = "campay"

    def initier(self, *, montant, telephone, description, reference_interne):
        reponse = campay_client.init_collect(
            amount=montant,
            phone_number=telephone,
            description=description,
            external_reference=str(reference_interne),
        )
        return ResultatInitiation(reference_externe=reponse.get("reference", ""), brut=reponse)

    def verifier_statut(self, reference_externe):
        reponse = campay_client.get_transaction_status(reference_externe)
        brut = reponse.get("status")
        statut = _STATUTS.get(brut)
        if statut is None:
            logger.warning("Statut CamPay inconnu %r pour %s : traité comme PENDING.", brut, reference_externe)
            statut = StatutPaiement.PENDING
        return ResultatStatut(statut=statut, brut=reponse)


__all__ = ["CampayProvider", "PaiementFournisseurError"]
