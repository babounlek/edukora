"""API de candidature : brouillon, vérification du numéro de versement par SMS, envoi, retrait."""
from datetime import timedelta

from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from payments.models import MobileMoneyOperator
from payments.serializers import PayerPhoneField
from users.otp_service import OTPCapReached, OTPInvalid, OTPSendFailed, OTPThrottled
from users.parent import exiger_mode_parent
from users.views import _client_ip, _erreur_envoi

from .candidatures import (
    CandidatureInvalide,
    candidature_courante,
    enregistrer_brouillon,
    envoyer_code_numero,
    raison_de_ne_pas_candidater,
    retirer_candidature,
    soumettre_candidature,
    verifier_numero,
)
from .models import (
    CHARTE_VERSION,
    REOUVERTURE_CANDIDATURE_JOURS,
    STATUTS_CANDIDATURE_OUVERTS,
    CandidatureRevendeur,
    StatutCandidature,
    TypeRevendeur,
)


class CandidatureEntreeSerializer(serializers.Serializer):
    """Champs d'un brouillon, tous facultatifs : le formulaire s'enregistre étape par étape."""

    type = serializers.ChoiceField(choices=TypeRevendeur.choices, required=False)
    nom_affiche = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)
    ville = serializers.CharField(max_length=100, required=False, allow_blank=True, trim_whitespace=True)
    presentation = serializers.CharField(max_length=1000, required=False, allow_blank=True, trim_whitespace=True)
    etablissement = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)
    fonction = serializers.CharField(max_length=100, required=False, allow_blank=True, trim_whitespace=True)
    operateur_versement = serializers.ChoiceField(choices=MobileMoneyOperator.choices, required=False, allow_blank=True)
    numero_versement = PayerPhoneField(required=False, allow_blank=True)


class CandidatureSerializer(serializers.ModelSerializer):
    numero_verifie = serializers.SerializerMethodField()
    motif = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    class Meta:
        model = CandidatureRevendeur
        fields = [
            "id", "statut", "type", "nom_affiche", "ville", "presentation", "etablissement", "fonction",
            "operateur_versement", "numero_versement", "numero_verifie", "motif", "code", "soumise_le", "etudiee_le",
        ]

    def get_numero_verifie(self, obj):
        return obj.numero_est_verifie

    def get_motif(self, obj):
        # Le motif d'un brouillon ou d'une candidature acceptée n'a pas de sens pour le candidat.
        return obj.motif if obj.statut in (StatutCandidature.A_COMPLETER, StatutCandidature.REFUSEE) else ""

    def get_code(self, obj):
        return obj.code_attribue if obj.statut == StatutCandidature.ACCEPTEE else ""


def _erreur(exc):
    return Response({"code": exc.code}, status=status.HTTP_400_BAD_REQUEST)


def _ouverte(request):
    return CandidatureRevendeur.objects.filter(user=request.user, statut__in=STATUTS_CANDIDATURE_OUVERTS).first()


@api_view(["GET", "PUT"])
def candidature(request):
    """Lire sa candidature (avec de quoi savoir s'il peut candidater) ou enregistrer son brouillon."""
    if request.method == "PUT":
        if (refus := exiger_mode_parent(request)) is not None:
            return refus
        entree = CandidatureEntreeSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        try:
            enregistree = enregistrer_brouillon(request.user, entree.validated_data)
        except CandidatureInvalide as exc:
            return _erreur(exc)
        return Response(CandidatureSerializer(enregistree).data)

    courante = candidature_courante(request.user)
    raison = raison_de_ne_pas_candidater(request.user)
    reouverture = None
    if raison == "refus_recent" and courante is not None and courante.etudiee_le:
        reouverture = courante.etudiee_le + timedelta(days=REOUVERTURE_CANDIDATURE_JOURS)
    return Response({
        "candidature": CandidatureSerializer(courante).data if courante else None,
        "peut_candidater": raison is None,
        "raison": raison,
        "reouverture_le": reouverture,
        "charte_version": CHARTE_VERSION,
    })


@api_view(["POST"])
def candidature_envoyer_code(request):
    """Envoie le code SMS qui prouve la possession du numéro de versement."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    courante = _ouverte(request)
    if courante is None:
        return Response({"code": "non_modifiable"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        envoyer_code_numero(courante, ip_address=_client_ip(request))
    except CandidatureInvalide as exc:
        return _erreur(exc)
    except OTPThrottled as exc:
        return _erreur_envoi(exc, 429)
    except (OTPCapReached, OTPSendFailed) as exc:
        return _erreur_envoi(exc, 503)
    return Response({"message": "Code envoyé par SMS."})


@api_view(["POST"])
def candidature_verifier_numero(request):
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    courante = _ouverte(request)
    if courante is None:
        return Response({"code": "non_modifiable"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        verifiee = verifier_numero(courante, str(request.data.get("code", "")).strip())
    except CandidatureInvalide as exc:
        return _erreur(exc)
    except OTPInvalid:
        return Response({"code": "code_invalide"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(CandidatureSerializer(verifiee).data)


@api_view(["POST"])
def candidature_soumettre(request):
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    courante = _ouverte(request)
    if courante is None:
        return Response({"code": "non_modifiable"}, status=status.HTTP_400_BAD_REQUEST)
    accepte = request.data.get("accepte") in (True, "true", "True", 1, "1")
    try:
        envoyee = soumettre_candidature(courante, str(request.data.get("charte_version", "")), accepte)
    except CandidatureInvalide as exc:
        return _erreur(exc)
    return Response(CandidatureSerializer(envoyee).data)


@api_view(["POST"])
def candidature_retirer(request):
    """Retire la candidature tant que l'équipe ne l'a pas tranchée (brouillon, à étudier ou complément demandé)."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    courante = _ouverte(request)
    if courante is None:
        return Response({"code": "non_modifiable"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        retiree = retirer_candidature(courante)
    except CandidatureInvalide as exc:
        return _erreur(exc)
    return Response(CandidatureSerializer(retiree).data)
