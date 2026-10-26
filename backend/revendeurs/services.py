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

from .fraude import detecter_signaux
from .models import (
    DELAI_ACQUISITION_JOURS,
    SEUIL_VERSEMENT_FCFA,
    FENETRE_COMMISSION_JOURS,
    AttributionRevendeur,
    Commission,
    Revendeur,
    SourceAttribution,
    StatutCommission,
    StatutRevendeur,
    StatutVersement,
    TypeRevendeur,
    Versement,
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
        # Accompagnement déclaré : le revendeur a avancé la somme depuis son numéro. Ce numéro payeur n'est alors
        # pas un auto-achat ; mais il doit bien être le sien, sinon la déclaration est douteuse (voir plus bas).
        avance_par_revendeur = bool(getattr(paiement, "paye_par_revendeur", False))
        numero_a_tester = "" if avance_par_revendeur else numero_payeur
        if _est_le_revendeur_lui_meme(revendeur, client, numero_a_tester):
            logger.warning("Auto-achat ignoré : paiement %s %s du revendeur %s.", source, paiement.pk, revendeur.pk)
            return None

        motifs = []
        if revendeur.statut == StatutRevendeur.SUSPENDU:
            motifs.append("revendeur suspendu")
        if montant_different:
            motifs.append("montant déclaré différent du montant attendu")
        payeur_pour_signaux = numero_payeur
        if avance_par_revendeur:
            if _chiffres_locaux(numero_payeur) in _numeros_du_revendeur(revendeur):
                # Un revendeur qui avance pour plusieurs parents paie toujours du même numéro : normal.
                payeur_pour_signaux = ""
            else:
                motifs.append("payé par le revendeur selon le client, mais depuis un autre numéro que le sien")
        motifs.extend(detecter_signaux(revendeur, client, attribution, paiement, payeur_pour_signaux, maintenant))

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


# --- Versements ---------------------------------------------------------------------------------


class VersementImpossible(Exception):
    """Une opération de versement refusée, avec une raison lisible par l'administrateur."""


def _periode(maintenant):
    return maintenant.astimezone(DOUALA).strftime("%Y-%m")


def commissions_a_verser(revendeur, maintenant=None):
    """Acquises, libres de tout drapeau, et pas encore dans un versement."""
    maintenant = maintenant or timezone.now()
    return Commission.objects.filter(
        revendeur=revendeur, statut=StatutCommission.ACTIVE, a_verifier=False,
        acquise_le__lte=maintenant, versement__isnull=True,
    )


def reprises_dues(revendeur):
    """Commissions déjà payées puis annulées pour fraude, pas encore déduites d'un versement."""
    return Commission.objects.filter(
        revendeur=revendeur, statut=StatutCommission.ANNULEE, versement__isnull=False, reprise_dans__isnull=True,
    )


def preparer_versement(revendeur, *, maintenant=None, seuil=SEUIL_VERSEMENT_FCFA):
    """
    Réserve les commissions acquises d'un revendeur dans un versement à payer. Retourne
    `(versement, None)`, ou `(None, raison)` quand rien n'est à faire : en dessous du seuil le solde est reporté, un
    revendeur suspendu ou sans numéro de versement n'est pas payé, un seul versement à la fois reste en cours.
    Les reprises dues (fraude après paiement) sont déduites du montant.
    """
    maintenant = maintenant or timezone.now()
    with db_transaction.atomic():
        qs = Revendeur.objects.all()
        if connection.features.has_select_for_update:
            qs = qs.select_for_update()
        revendeur = qs.get(pk=revendeur.pk)

        if revendeur.statut == StatutRevendeur.EN_ATTENTE:
            return None, "compte pas encore activé"
        if revendeur.statut == StatutRevendeur.SUSPENDU:
            return None, "revendeur suspendu"
        if not revendeur.numero_versement:
            return None, "numéro de versement manquant"
        if Versement.objects.filter(revendeur=revendeur, statut=StatutVersement.PREPARE).exists():
            return None, "un versement est déjà préparé"

        commissions = list(commissions_a_verser(revendeur, maintenant).select_for_update())
        brut = sum(c.montant_fcfa for c in commissions)
        if brut == 0:
            return None, "rien à verser"
        reprises = list(reprises_dues(revendeur).select_for_update())
        total_reprises = sum(c.montant_fcfa for c in reprises)
        net = brut - total_reprises
        if net < seuil:
            return None, f"{max(net, 0)} FCFA à verser, sous le seuil de {seuil} FCFA (reporté)"

        versement = Versement.objects.create(
            revendeur=revendeur, periode=_periode(maintenant), montant_brut=brut, montant_reprises=total_reprises,
            montant_net=net, operateur=revendeur.operateur_versement, numero=revendeur.numero_versement,
            prepare_le=maintenant,
        )
        Commission.objects.filter(pk__in=[c.pk for c in commissions]).update(versement=versement)
        Commission.objects.filter(pk__in=[c.pk for c in reprises]).update(reprise_dans=versement)
        return versement, None


def preparer_versements(revendeurs, *, maintenant=None, seuil=SEUIL_VERSEMENT_FCFA):
    """Prépare le versement de chaque revendeur. Retourne `(versements, ignores)`, `ignores` = [(revendeur, raison)]."""
    versements, ignores = [], []
    for revendeur in revendeurs:
        versement, raison = preparer_versement(revendeur, maintenant=maintenant, seuil=seuil)
        if versement is not None:
            versements.append(versement)
        else:
            ignores.append((revendeur, raison))
    return versements, ignores


def marquer_paye(versement, par, reference, *, frais_retrait=0, maintenant=None):
    """
    PREPARE -> PAYE, une fois le Mobile Money envoyé. La référence de la transaction est obligatoire : c'est la preuve
    que le versement a eu lieu. Les commissions réglées passent à PAYEE.
    """
    reference = (reference or "").strip()
    if not reference:
        raise VersementImpossible("La référence de la transaction Mobile Money est obligatoire.")
    maintenant = maintenant or timezone.now()
    with db_transaction.atomic():
        qs = Versement.objects.all()
        if connection.features.has_select_for_update:
            qs = qs.select_for_update()
        verrouille = qs.get(pk=versement.pk)
        if verrouille.statut != StatutVersement.PREPARE:
            raise VersementImpossible(f"Versement #{verrouille.pk} déjà {verrouille.get_statut_display().lower()}.")
        verrouille.statut = StatutVersement.PAYE
        verrouille.reference_mobile_money = reference
        verrouille.frais_retrait = frais_retrait
        verrouille.paye_par = par
        verrouille.paye_le = maintenant
        verrouille.save(update_fields=["statut", "reference_mobile_money", "frais_retrait", "paye_par", "paye_le"])
        verrouille.commissions.filter(statut=StatutCommission.ACTIVE).update(statut=StatutCommission.PAYEE)
    _prevenir(verrouille)
    return verrouille


def annuler_versement(versement):
    """PREPARE -> ANNULE : les commissions et les reprises réservées redeviennent disponibles."""
    with db_transaction.atomic():
        qs = Versement.objects.all()
        if connection.features.has_select_for_update:
            qs = qs.select_for_update()
        verrouille = qs.get(pk=versement.pk)
        if verrouille.statut != StatutVersement.PREPARE:
            raise VersementImpossible(f"Versement #{verrouille.pk} déjà {verrouille.get_statut_display().lower()}.")
        verrouille.commissions.update(versement=None)
        verrouille.reprises.update(reprise_dans=None)
        verrouille.statut = StatutVersement.ANNULE
        verrouille.save(update_fields=["statut"])
    return verrouille


def exporter_csv(versements):
    """Fichier à charger dans l'outil de paiement groupé Mobile Money : une ligne par versement préparé."""
    import csv
    import io

    sortie = io.StringIO()
    ecrivain = csv.writer(sortie)
    ecrivain.writerow(["reference", "operateur", "numero", "montant_fcfa", "beneficiaire", "periode"])
    for v in versements:
        ecrivain.writerow([f"EDK-V{v.pk}", v.operateur, v.numero, v.montant_net, v.revendeur.nom_affiche, v.periode])
    return sortie.getvalue()


def _prevenir(versement):
    """SMS au revendeur ; un échec d'envoi ne défait jamais un versement déjà payé."""
    telephone = versement.revendeur.user.phone_number
    if not telephone:
        return
    try:
        from users.sms_backends import get_sms_backend

        get_sms_backend().send(
            telephone,
            f"Edukora : ton versement de {versement.montant_net} FCFA ({versement.periode}) a été envoyé "
            f"(réf. {versement.reference_mobile_money}).",
        )
    except Exception:
        logger.exception("SMS de versement non envoyé pour le versement %s.", versement.pk)
