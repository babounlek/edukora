"""
Candidatures de revendeur : du brouillon à l'acceptation par l'équipe (voir docs-revendeurs/CAHIER-DES-CHARGES-CANDIDATURE.md).

Le candidat remplit sa candidature, prouve son numéro de versement par un code SMS, accepte la charte et l'envoie ;
l'équipe l'étudie dans l'admin. Rien n'est attribué avant l'acceptation : ni code, ni lien, ni commission.
"""
import logging
import random
import re
import unicodedata
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection
from django.db import transaction as db_transaction
from django.utils import timezone

from .models import (
    CHARTE_VERSION,
    REOUVERTURE_CANDIDATURE_JOURS,
    STATUTS_CANDIDATURE_OUVERTS,
    CandidatureRevendeur,
    Revendeur,
    StatutCandidature,
    StatutRevendeur,
    TypeRevendeur,
)

logger = logging.getLogger(__name__)


class CandidatureInvalide(Exception):
    """Une opération de candidature refusée. `code` est lisible par la machine (le front écrit la phrase)."""

    def __init__(self, code, message=""):
        super().__init__(message or code)
        self.code = code


_TEXTES_SMS = {
    "recue": {
        "fr": "Edukora : ta candidature de revendeur est bien reçue. L'équipe l'étudie et te répond bientôt.",
        "en": "Edukora: we've received your reseller application. The team will review it and get back to you soon.",
    },
    "complement": {
        "fr": "Edukora : ta candidature de revendeur a besoin d'un complément. Ouvre-la sur le site pour le voir.",
        "en": "Edukora: your reseller application needs more information. Open it on the site to see what's needed.",
    },
    "acceptee": {
        "fr": "Edukora : ta candidature est acceptée ! Ton espace revendeur est dans « Mon compte ». Ton code : {code}.",
        "en": "Edukora: your application is accepted! Your reseller area is in \"My account\". Your code: {code}.",
    },
    "refusee": {
        "fr": "Edukora : ta candidature de revendeur n'a pas été retenue. Ouvre-la sur le site pour en voir la raison.",
        "en": "Edukora: your reseller application wasn't accepted. Open it on the site to see why.",
    },
}


def _prevenir_candidat(candidature, cle, **variables):
    """SMS au candidat (numéro du compte, sinon numéro de versement vérifié) ; un échec d'envoi n'annule rien."""
    try:
        from users.phone import to_e164
        from users.sms_backends import get_sms_backend

        langue = "en" if getattr(candidature.user, "langue", "fr") == "en" else "fr"
        destinataire = candidature.user.phone_number or (
            to_e164(candidature.numero_versement) if candidature.numero_versement else None
        )
        if destinataire:
            get_sms_backend().send(destinataire, _TEXTES_SMS[cle][langue].format(**variables))
    except Exception:
        logger.exception("SMS de candidature (%s) non envoyé pour la candidature %s.", cle, candidature.pk)


def candidature_courante(user):
    """La candidature ouverte du compte, sinon la dernière."""
    ouverte = CandidatureRevendeur.objects.filter(user=user, statut__in=STATUTS_CANDIDATURE_OUVERTS).first()
    return ouverte or CandidatureRevendeur.objects.filter(user=user).first()


def raison_de_ne_pas_candidater(user, maintenant=None):
    """None si le compte peut commencer une candidature, sinon un code : deja_revendeur, candidature_ouverte, refus_recent."""
    maintenant = maintenant or timezone.now()
    if Revendeur.objects.filter(user=user).exists():
        return "deja_revendeur"
    if CandidatureRevendeur.objects.filter(user=user, statut__in=STATUTS_CANDIDATURE_OUVERTS).exists():
        return "candidature_ouverte"
    dernier_refus = (
        CandidatureRevendeur.objects.filter(user=user, statut=StatutCandidature.REFUSEE).order_by("-etudiee_le").first()
    )
    if (
        dernier_refus and dernier_refus.etudiee_le
        and maintenant < dernier_refus.etudiee_le + timedelta(days=REOUVERTURE_CANDIDATURE_JOURS)
    ):
        return "refus_recent"
    return None


CHAMPS_BROUILLON = (
    "type", "nom_affiche", "ville", "presentation", "etablissement", "fonction", "operateur_versement", "numero_versement",
)


def enregistrer_brouillon(user, donnees):
    """
    Crée ou met à jour la candidature ouverte du compte avec les champs fournis. Changer le numéro de versement
    annule la vérification : le code SMS prouve la possession d'UN numéro, pas du suivant.
    """
    candidature = CandidatureRevendeur.objects.filter(user=user, statut__in=STATUTS_CANDIDATURE_OUVERTS).first()
    if candidature is None:
        raison = raison_de_ne_pas_candidater(user)
        if raison:
            raise CandidatureInvalide(raison)
        candidature = CandidatureRevendeur(user=user)
    elif not candidature.modifiable:
        raise CandidatureInvalide("non_modifiable")

    for champ in CHAMPS_BROUILLON:
        if champ in donnees:
            setattr(candidature, champ, donnees[champ])
    if candidature.numero_versement != candidature.numero_verifie:
        candidature.numero_verifie_le = None
    candidature.save()
    return candidature


def envoyer_code_numero(candidature, ip_address=None):
    """SMS de vérification du numéro de versement, avec les garde-fous de la connexion (délai, plafond par IP, plafond global)."""
    from users.otp_service import request_otp
    from users.phone import to_e164

    if not candidature.modifiable:
        raise CandidatureInvalide("non_modifiable")
    if not candidature.numero_versement:
        raise CandidatureInvalide("numero_manquant")
    request_otp(to_e164(candidature.numero_versement), ip_address=ip_address)


def verifier_numero(candidature, code):
    """Prouve la possession du numéro de versement. Lève `OTPInvalid` si le code est faux ou expiré."""
    from users.otp_service import consume_otp
    from users.phone import to_e164

    if not candidature.modifiable:
        raise CandidatureInvalide("non_modifiable")
    if not candidature.numero_versement:
        raise CandidatureInvalide("numero_manquant")
    consume_otp(to_e164(candidature.numero_versement), code)
    candidature.numero_verifie = candidature.numero_versement
    candidature.numero_verifie_le = timezone.now()
    candidature.save(update_fields=["numero_verifie", "numero_verifie_le", "updated_at"])
    return candidature


def _proposer_code(nom):
    """Quelques lettres du nom et deux chiffres, sans collision avec un revendeur ni un code de parrainage."""
    from users.models import User

    sans_accents = unicodedata.normalize("NFD", nom or "").encode("ascii", "ignore").decode()
    lettres = re.sub(r"[^A-Z]", "", sans_accents.upper())[:5] or "REV"
    for _ in range(50):
        code = f"{lettres}{random.randint(10, 99)}"
        if not Revendeur.objects.filter(code=code).exists() and not User.objects.filter(referral_code=code).exists():
            return code
    return f"{lettres}{random.randint(100, 999)}"[:10]


def _alertes(candidature):
    """Signaux pour l'équipe : un numéro de versement déjà connu n'est pas refusé, il est signalé."""
    alertes = []
    numero = candidature.numero_versement
    for r in Revendeur.objects.filter(numero_versement=numero).exclude(user=candidature.user):
        alertes.append(f"numéro de versement déjà utilisé par le revendeur {r.nom_affiche} ({r.code})")
    autres = (
        CandidatureRevendeur.objects.filter(numero_versement=numero).exclude(pk=candidature.pk).exclude(user=candidature.user)
        .exclude(statut__in=(StatutCandidature.BROUILLON, StatutCandidature.RETIREE))
    )
    for a in autres:
        alertes.append(f"numéro de versement déjà indiqué dans la candidature de {a.nom_affiche} ({a.get_statut_display().lower()})")
    return "\n".join(alertes)


def soumettre_candidature(candidature, charte_version, accepte, maintenant=None):
    """
    Envoie la candidature à l'équipe : champs complets, numéro de versement vérifié, charte acceptée dans sa version
    en vigueur. Vaut aussi renvoi après une demande de complément.
    """
    maintenant = maintenant or timezone.now()
    if not candidature.modifiable:
        raise CandidatureInvalide("non_modifiable")
    obligatoires = [
        candidature.nom_affiche, candidature.ville, candidature.presentation,
        candidature.operateur_versement, candidature.numero_versement,
    ]
    if candidature.type == TypeRevendeur.ECOLE_CENTRE:
        obligatoires += [candidature.etablissement, candidature.fonction]
    if not candidature.type or not all(obligatoires):
        raise CandidatureInvalide("champs_manquants")
    if not candidature.numero_est_verifie:
        raise CandidatureInvalide("numero_non_verifie")
    if not accepte or charte_version != CHARTE_VERSION:
        raise CandidatureInvalide("charte_non_acceptee")

    candidature.charte_version = CHARTE_VERSION
    candidature.charte_acceptee_le = maintenant
    candidature.statut = StatutCandidature.SOUMISE
    candidature.soumise_le = maintenant
    candidature.motif = ""
    candidature.alertes = _alertes(candidature)
    if not candidature.code_attribue:
        candidature.code_attribue = _proposer_code(candidature.nom_affiche)
    candidature.save()
    _prevenir_candidat(candidature, "recue")
    return candidature


def retirer_candidature(candidature):
    """Le candidat retire sa candidature, tant que l'équipe ne l'a pas tranchée."""
    if candidature.statut not in STATUTS_CANDIDATURE_OUVERTS:
        raise CandidatureInvalide("non_modifiable")
    candidature.statut = StatutCandidature.RETIREE
    candidature.save(update_fields=["statut", "updated_at"])
    return candidature


def _etudiable(candidature):
    if candidature.statut != StatutCandidature.SOUMISE:
        raise CandidatureInvalide(
            "deja_traitee", f"Candidature #{candidature.pk} : statut {candidature.get_statut_display().lower()}.",
        )


def accepter_candidature(candidature, par, maintenant=None):
    """Crée la fiche revendeur (ACTIF) avec le code attribué, reprend la charte acceptée et prévient le candidat."""
    maintenant = maintenant or timezone.now()
    with db_transaction.atomic():
        qs = CandidatureRevendeur.objects.all()
        if connection.features.has_select_for_update:
            qs = qs.select_for_update()
        candidature = qs.select_related("user").get(pk=candidature.pk)
        _etudiable(candidature)
        if Revendeur.objects.filter(user=candidature.user).exists():
            raise CandidatureInvalide("deja_revendeur", "Ce compte est déjà revendeur.")
        if not candidature.numero_est_verifie:
            raise CandidatureInvalide("numero_non_verifie", "Le numéro de versement n'est pas vérifié.")
        code = (candidature.code_attribue or "").strip().upper()
        try:
            with db_transaction.atomic():
                revendeur = Revendeur.objects.create(
                    user=candidature.user, type=candidature.type, nom_affiche=candidature.nom_affiche, code=code,
                    statut=StatutRevendeur.ACTIF, operateur_versement=candidature.operateur_versement,
                    numero_versement=candidature.numero_versement, contrat_accepte_le=candidature.charte_acceptee_le,
                    charte_version=candidature.charte_version,
                )
        except ValidationError as exc:
            raise CandidatureInvalide("code_invalide", f"Code « {code} » refusé : {'; '.join(exc.messages)}") from exc
        except IntegrityError as exc:
            raise CandidatureInvalide("code_invalide", f"Code « {code} » déjà utilisé.") from exc
        candidature.statut = StatutCandidature.ACCEPTEE
        candidature.code_attribue = code
        candidature.revendeur = revendeur
        candidature.etudiee_par = par
        candidature.etudiee_le = maintenant
        candidature.save()
    _prevenir_candidat(candidature, "acceptee", code=code)
    return revendeur


def refuser_candidature(candidature, par, maintenant=None):
    """Refus : le motif (saisi avant l'action) est montré au candidat."""
    _etudiable(candidature)
    if not candidature.motif.strip():
        raise CandidatureInvalide("motif_obligatoire", "Saisis d'abord le motif.")
    candidature.statut = StatutCandidature.REFUSEE
    candidature.etudiee_par = par
    candidature.etudiee_le = maintenant or timezone.now()
    candidature.save()
    _prevenir_candidat(candidature, "refusee")
    return candidature


def demander_complement(candidature, par, maintenant=None):
    """Renvoie la candidature au candidat avec la question (le motif saisi avant l'action)."""
    _etudiable(candidature)
    if not candidature.motif.strip():
        raise CandidatureInvalide("motif_obligatoire", "Saisis d'abord la question à poser.")
    candidature.statut = StatutCandidature.A_COMPLETER
    candidature.etudiee_par = par
    candidature.etudiee_le = maintenant or timezone.now()
    candidature.save()
    _prevenir_candidat(candidature, "complement")
    return candidature
