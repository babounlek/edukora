"""
Signaux de fraude évalués quand une commission est créée (voir services.enregistrer_commission).

Un signal ne refuse jamais rien : il RETIENT la commission (`a_verifier`) jusqu'à ce qu'un administrateur la libère
ou l'annule. Une école qui inscrit une classe le même jour, ou un cybercafé dont tous les clients paient depuis la
même connexion, déclenchent ces signaux à raison : la décision reste humaine. Les seuils sont dans models.py.
"""
from datetime import timedelta

from django.db.models import Count

from .models import (
    FRAUDE_MEME_IP_SEUIL,
    FRAUDE_MEME_PAYEUR_SEUIL,
    FRAUDE_NUMEROS_VOISINS_ECART,
    FRAUDE_PIC_INSCRIPTIONS_SEUIL,
    FRAUDE_REFUSES_SEUIL,
    AttributionRevendeur,
)


def _chiffres_locaux(numero):
    chiffres = "".join(c for c in (numero or "") if c.isdigit())
    return chiffres[-9:]


def _signal_meme_ip(revendeur, paiement, maintenant):
    from payments.models import ManualPayment

    ip = getattr(paiement, "declared_ip", None)
    if not ip:
        return None
    clients = (
        ManualPayment.objects.filter(
            declared_ip=ip, created_at__gte=maintenant - timedelta(hours=24),
            user__attribution_revendeur__revendeur=revendeur,
        ).values("user").distinct().count()
    )
    if clients >= FRAUDE_MEME_IP_SEUIL:
        return f"{clients} clients paient depuis la même adresse IP en 24 h"
    return None


def _signal_meme_payeur(revendeur, numero_payeur):
    from payments.models import ManualPayment, Transaction

    numero = _chiffres_locaux(numero_payeur)
    if not numero:
        return None
    manuels = ManualPayment.objects.filter(
        payer_phone_number=numero, user__attribution_revendeur__revendeur=revendeur,
    ).values_list("user_id", flat=True)
    campay = Transaction.objects.filter(
        phone_number=numero, user__attribution_revendeur__revendeur=revendeur,
    ).values_list("user_id", flat=True)
    clients = set(manuels) | set(campay)
    if len(clients) >= FRAUDE_MEME_PAYEUR_SEUIL:
        return f"{len(clients)} comptes clients réglés depuis le même numéro"
    return None


def _signal_numeros_voisins(revendeur, client):
    numero = _chiffres_locaux(client.phone_number)
    if not numero:
        return None
    ref = int(numero)
    voisins = 0
    autres = (
        AttributionRevendeur.objects.filter(revendeur=revendeur).exclude(client=client)
        .exclude(client__phone_number__isnull=True).values_list("client__phone_number", flat=True)
    )
    for autre in autres:
        chiffres = _chiffres_locaux(autre)
        if chiffres and 0 < abs(int(chiffres) - ref) <= FRAUDE_NUMEROS_VOISINS_ECART:
            voisins += 1
    if voisins >= 2:
        return "numéros de clients qui se suivent"
    return None


def _signal_refus(revendeur, maintenant):
    from payments.models import ManualPayment, ManualPaymentStatus

    refuses = ManualPayment.objects.filter(
        status=ManualPaymentStatus.REJECTED, created_at__gte=maintenant - timedelta(days=30),
        user__attribution_revendeur__revendeur=revendeur,
    ).aggregate(n=Count("id"))["n"]
    if refuses >= FRAUDE_REFUSES_SEUIL:
        return f"{refuses} paiements refusés parmi ses clients en 30 jours"
    return None


def _signal_pic_inscriptions(attribution):
    from django.utils import timezone

    debut = timezone.localtime(attribution.attribue_le).replace(hour=0, minute=0, second=0, microsecond=0)
    n = AttributionRevendeur.objects.filter(
        revendeur_id=attribution.revendeur_id, attribue_le__gte=debut, attribue_le__lt=debut + timedelta(days=1),
    ).count()
    if n >= FRAUDE_PIC_INSCRIPTIONS_SEUIL:
        return f"{n} clients rattachés le même jour"
    return None


def detecter_signaux(revendeur, client, attribution, paiement, numero_payeur, maintenant):
    """Les motifs (texte court, en français, pour l'administrateur) qui justifient de retenir cette commission."""
    signaux = (
        _signal_meme_ip(revendeur, paiement, maintenant),
        _signal_meme_payeur(revendeur, numero_payeur),
        _signal_numeros_voisins(revendeur, client),
        _signal_refus(revendeur, maintenant),
        _signal_pic_inscriptions(attribution),
    )
    return [s for s in signaux if s]
