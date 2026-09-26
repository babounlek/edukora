"""
Port de paiement Mobile Money : le seul vocabulaire que le domaine (payments.models,
payments.views) connaît. Chaque agrégateur (CamPay, NoKash...) vit dans un adaptateur
de ce paquet qui traduit son API, ses statuts et ses erreurs vers ce contrat - jamais
l'inverse. Volontairement étroit : initier + vérifier le statut. Un webhook ou un
remboursement s'ajoutera quand un fournisseur réel l'exigera, pas avant.
"""

from dataclasses import dataclass, field
from typing import Any


class StatutPaiement:
    """
    Statuts normalisés, propres à Edukora. Les valeurs sont volontairement identiques à
    payments.models.StatutTransaction (les deux sont des chaînes stockées en base) : un
    adaptateur ne renvoie jamais que l'une de ces trois valeurs, jamais un statut brut
    d'agrégateur.
    """

    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class PaiementFournisseurError(Exception):
    """
    Toute défaillance d'un agrégateur (réseau, authentification, refus, réponse
    invalide). Les vues ne rattrapent que celle-ci : un adaptateur doit y convertir ses
    erreurs propres pour qu'une panne de fournisseur reste une réponse 502 exploitable
    plutôt qu'un 500.
    """


@dataclass(frozen=True)
class ResultatInitiation:
    reference_externe: str
    brut: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResultatStatut:
    statut: str  # une valeur de StatutPaiement
    brut: dict[str, Any] = field(default_factory=dict)


class PaymentProvider:
    """Contrat d'un agrégateur de paiement Mobile Money."""

    name: str

    def initier(self, *, montant, telephone, description, reference_interne) -> ResultatInitiation:
        """
        Déclenche une demande de collecte (non bloquante) auprès du payeur.
        `reference_interne` est l'identifiant Edukora (Transaction.external_reference),
        transmis à l'agrégateur pour le rapprochement.
        """
        raise NotImplementedError

    def verifier_statut(self, reference_externe) -> ResultatStatut:
        """
        Interroge l'agrégateur pour l'état réel d'une transaction - seule source de
        vérité pour confirmer un paiement (jamais un callback non vérifié).
        """
        raise NotImplementedError
