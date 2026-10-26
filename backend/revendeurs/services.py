"""
Attribution des clients aux revendeurs et calcul des commissions (voir
docs-revendeurs/CAHIER-DES-CHARGES.md).

Deux points d'entrée côté reste du code :
- `attribuer_a_l_inscription` : appelé par les trois chemins de création de compte
  (téléphone, e-mail, Google), juste avant la résolution du code de parrainage ;
- `enregistrer_commission_securise` : appelé par `Transaction._confirmer_succes` et
  `ManualPayment.approve`, une fois l'accès activé.
"""
import logging
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.db import connection
from django.db import transaction as db_transaction
from django.utils import timezone

from .models import (
    DELAI_ACQUISITION_JOURS,
    FENETRE_COMMISSION_JOURS,
    AttributionRevendeur,
    Commission,
    Revendeur,
    SourceAttribution,
    StatutCommission,
    StatutRevendeur,
    TypeRevendeur,
)

logger = logging.getLogger(__name__)

DOUALA = ZoneInfo("Africa/Douala")


def _chiffres_locaux(numero):
    """Les 9 derniers chiffres d'un numéro, quel que soit son format (+237…, local, espaces)."""
    chiffres = "".join(c for c in (numero or "") if c.isdigit())
    return chiffres[-9:]


def _numeros_du_revendeur(revendeur):
    numeros = {_chiffres_locaux(revendeur.numero_versement), _chiffres_locaux(revendeur.user.phone_number)}
    numeros.discard("")
    return numeros


def _est_le_revendeur_lui_meme(revendeur, client, numero_payeur=""):
    """Auto-achat : le client est le revendeur, ou son numéro (compte ou payeur) est le sien."""
    if client.pk == revendeur.user_id:
        return True
    numeros = _numeros_du_revendeur(revendeur)
    candidats = {_chiffres_locaux(client.phone_number), _chiffres_locaux(numero_payeur)}
    candidats.discard("")
    return bool(numeros & candidats)


def trouver_revendeur_actif(code):
    code = (code or "").strip().upper()
    if not code:
        return None
    return Revendeur.objects.filter(code=code, statut=StatutRevendeur.ACTIF).select_related("user").first()


def attribuer_a_l_inscription(user, code):
    """
    Rattache un compte qui vient d'être créé au revendeur dont il a saisi le code.
    Retourne l'attribution, ou None quand le code n'est pas un code revendeur actif, quand
    le compte est le revendeur lui-même ou quand il est déjà attribué. Ne lève jamais :
    comme pour le code de parrainage, un code inutilisable est ignoré en silence plutôt que
    de faire échouer l'inscription.
    """
    revendeur = trouver_revendeur_actif(code)
    if revendeur is None or _est_le_revendeur_lui_meme(revendeur, user):
        return None
    attribution, _ = AttributionRevendeur.objects.get_or_create(
        client=user, defaults={"revendeur": revendeur, "source": SourceAttribution.INSCRIPTION},
    )
    return attribution


def a_deja_paye(user):
    """Un paiement validé existe, par l'un ou l'autre canal."""
    from payments.models import ManualPaymentStatus, StatutTransaction

    return (
        user.transactions.filter(status=StatutTransaction.SUCCESSFUL).exists()
        or user.manual_payments.filter(status=ManualPaymentStatus.APPROVED).exists()
    )


def rattacher_tardivement(user, code):
    """
    Rattachement d'un compte déjà existant, saisi avant son premier paiement. Refusé
    (None) dès qu'une attribution existe ou qu'un paiement a déjà été validé : le
    revendeur ne peut pas s'attribuer après coup un client déjà converti.
    """
    revendeur = trouver_revendeur_actif(code)
    if revendeur is None or _est_le_revendeur_lui_meme(revendeur, user):
        return None
    if AttributionRevendeur.objects.filter(client=user).exists() or a_deja_paye(user):
        return None
    return AttributionRevendeur.objects.create(client=user, revendeur=revendeur, source=SourceAttribution.PAIEMENT)


def _montant_encaisse(paiement):
    """Transaction : montant envoyé à l'agrégateur (déjà net du crédit). Paiement manuel : montant validé par l'admin."""
    from payments.models import Transaction

    if isinstance(paiement, Transaction):
        return paiement.amount, paiement.phone_number, False
    return paiement.amount_declared, paiement.payer_phone_number, paiement.amount_declared != paiement.amount_expected


def _debut_du_mois(maintenant):
    local = maintenant.astimezone(DOUALA)
    return local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def ventes_du_mois(revendeur, maintenant=None):
    """Nombre de ventes (commissions non annulées) du mois civil en cours, fuseau Africa/Douala."""
    maintenant = maintenant or timezone.now()
    return (
        Commission.objects.filter(revendeur=revendeur, created_at__gte=_debut_du_mois(maintenant))
        .exclude(statut=StatutCommission.ANNULEE).count()
    )


def masquer_client(user):
    """
    Libellé d'un client montré à son revendeur : initiales et fin du numéro, jamais de
    coordonnées complètes (le revendeur voit qu'une vente a eu lieu, pas qui est l'élève).
    """
    parties = [p for p in (user.full_name or user.pseudo or "").split() if p]
    initiales = " ".join(f"{p[0].upper()}." for p in parties[:2])
    chiffres = "".join(c for c in (user.phone_number or "") if c.isdigit())
    if chiffres:
        suffixe = f"••{chiffres[-4:]}"
    elif user.email:
        suffixe = f"{user.email[0]}•••"
    else:
        suffixe = f"#{user.pk}"
    return f"{initiales} {suffixe}".strip()


def _taux_applicable(revendeur, maintenant):
    """Taux de base, ou taux de palier pour un commercial qui a déjà atteint son seuil ce mois-ci."""
    if (
        revendeur.type == TypeRevendeur.COMMERCIAL
        and revendeur.palier_seuil is not None
        and revendeur.palier_taux_pct is not None
    ):
        if ventes_du_mois(revendeur, maintenant) >= revendeur.palier_seuil:
            return revendeur.palier_taux_pct
    return revendeur.taux_base_pct


def enregistrer_commission(paiement, *, maintenant=None):
    """
    Crée la commission d'un paiement validé (`Transaction` SUCCESSFUL ou `ManualPayment`
    APPROVED), ou retourne None s'il n'y en a pas lieu. Idempotent : un second appel pour
    le même paiement retourne la commission existante.

    Pas de commission quand : le client n'est pas attribué, le revendeur est en attente ou
    résilié, la fenêtre de 12 mois est dépassée, le montant encaissé est nul (achat couvert
    par du crédit) ou le paiement est un auto-achat. Un revendeur suspendu, ou un montant
    manuel différent du montant attendu, donne une commission RETENUE (`a_verifier`).
    """
    from payments.models import Transaction

    maintenant = maintenant or timezone.now()
    source = "transaction" if isinstance(paiement, Transaction) else "manual_payment"

    existante = Commission.objects.filter(**{source: paiement}).first()
    if existante is not None:
        return existante

    client = paiement.user
    attribution = AttributionRevendeur.objects.filter(client=client).select_related("revendeur__user").first()
    if attribution is None:
        return None

    base, numero_payeur, montant_different = _montant_encaisse(paiement)
    if base <= 0:
        return None
    if maintenant > attribution.attribue_le + timedelta(days=FENETRE_COMMISSION_JOURS):
        return None

    with db_transaction.atomic():
        # Verrou sur le revendeur : deux paiements simultanés ne doivent pas lire le même
        # nombre de ventes du mois et rater le passage de palier. Sans effet sur SQLite
        # (tests), comme les autres verrous du projet.
        qs = Revendeur.objects.select_related("user")
        if connection.features.has_select_for_update:
            qs = qs.select_for_update(of=("self",))
        revendeur = qs.get(pk=attribution.revendeur_id)

        if revendeur.statut not in (StatutRevendeur.ACTIF, StatutRevendeur.SUSPENDU):
            return None
        if _est_le_revendeur_lui_meme(revendeur, client, numero_payeur):
            logger.warning("Auto-achat ignoré : paiement %s %s du revendeur %s.", source, paiement.pk, revendeur.pk)
            return None

        motifs = []
        if revendeur.statut == StatutRevendeur.SUSPENDU:
            motifs.append("revendeur suspendu")
        if montant_different:
            motifs.append("montant déclaré différent du montant attendu")

        taux = _taux_applicable(revendeur, maintenant)
        return Commission.objects.create(
            revendeur=revendeur, client=client, plan=paiement.plan,
            base_fcfa=base, taux_pct=taux, montant_fcfa=base * taux // 100,
            acquise_le=maintenant + timedelta(days=DELAI_ACQUISITION_JOURS),
            a_verifier=bool(motifs), motif_a_verifier=" ; ".join(motifs),
            **{source: paiement},
        )


def enregistrer_commission_securise(paiement):
    """
    Enveloppe appelée depuis les chemins de paiement. Une erreur de commission ne doit
    JAMAIS empêcher d'activer l'accès d'un client qui a payé : l'appel tourne dans un
    point de sauvegarde, l'erreur est journalisée (et remontée à Sentry) et le paiement
    suit son cours.
    """
    try:
        with db_transaction.atomic():
            return enregistrer_commission(paiement)
    except Exception:
        logger.exception("Calcul de commission revendeur en échec pour le paiement %s %s.", type(paiement).__name__, paiement.pk)
        return None
