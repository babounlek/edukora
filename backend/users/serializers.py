from rest_framework import serializers

from .email_service import normalize_email
from .models import User
from .phone import to_e164, to_local

# Le frontend envoie toujours le format local à 9 chiffres (voir le champ de saisie
# de LoginPage) : ce contrat d'API est conservé tel quel, la conversion en E.164 se
# fait ici, à l'entrée. Le format international est accepté en plus, pour un client
# futur qui saisirait l'indicatif.
PHONE_REGEX = r"^(\+?237)?6\d{8}$"


class NormalizedPhoneField(serializers.RegexField):
    """
    Valide la saisie puis la convertit en E.164 - de sorte qu'aucune vue n'ait à se
    demander sous quel format lui arrive un numéro, et que le format de stockage ne
    fuie jamais dans le contrat d'API.
    """

    def __init__(self, **kwargs):
        super().__init__(regex=PHONE_REGEX, **kwargs)

    def to_internal_value(self, data):
        return to_e164(super().to_internal_value(data))


class OTPRequestSerializer(serializers.Serializer):
    phone_number = NormalizedPhoneField()


class OTPVerifySerializer(serializers.Serializer):
    phone_number = NormalizedPhoneField()
    code = serializers.RegexField(regex=r"^\d{6}$")
    referral_code = serializers.CharField(required=False, allow_blank=True, max_length=10)


class NormalizedEmailField(serializers.EmailField):
    """
    Même rôle que NormalizedPhoneField : le format de stockage ne fuit pas dans le
    contrat d'API, et aucune vue n'a à se demander sous quelle casse lui arrive une
    adresse. Voir users.email_service.normalize_email pour le choix de tout mettre en
    minuscules, partie locale comprise.
    """

    def to_internal_value(self, data):
        return normalize_email(super().to_internal_value(data))


class EmailCodeRequestSerializer(serializers.Serializer):
    email = NormalizedEmailField()


class EmailCodeVerifySerializer(serializers.Serializer):
    email = NormalizedEmailField()
    code = serializers.RegexField(regex=r"^\d{6}$")
    referral_code = serializers.CharField(required=False, allow_blank=True, max_length=10)


class EmailLinkConfirmSerializer(serializers.Serializer):
    email = NormalizedEmailField()
    code = serializers.RegexField(regex=r"^\d{6}$")


class PhoneChangeRequestSerializer(serializers.Serializer):
    phone_number = NormalizedPhoneField()


class PhoneChangeConfirmSerializer(serializers.Serializer):
    phone_number = NormalizedPhoneField()
    code = serializers.RegexField(regex=r"^\d{6}$")


class UserSerializer(serializers.ModelSerializer):
    filleuls_count = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    auth_methods = serializers.SerializerMethodField()
    credit_parrainage_disponible = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "phone_number", "email", "email_verified", "full_name", "pseudo",
            "date_joined", "referral_code", "filleuls_count", "auth_methods",
            "credit_parrainage_disponible",
        ]

    def get_phone_number(self, obj):
        """
        Rendu au format local à 9 chiffres, pas en E.164, bien que ce soit désormais
        le format de stockage : le frontend l'affiche tel quel (Header, AccountPage)
        et s'en sert pour préremplir le champ Mobile Money de SubscribePage, que
        payments valide en format local. Changer la sortie ici casserait ce
        préremplissage sans rien apporter à l'utilisateur, qui reconnaît son numéro
        sous la forme qu'il compose.
        """
        return to_local(obj.phone_number)

    def get_auth_methods(self, obj):
        """Fournisseurs déjà rattachés, pour que le compte puisse afficher ce qui reste à lier."""
        return sorted({identity.provider for identity in obj.identities.all()})

    def get_filleuls_count(self, obj):
        return obj.filleuls.count()

    def get_credit_parrainage_disponible(self, obj):
        """Solde de crédit parrainage encore dépensable (voir
        subscriptions.models.solde_credit_parrainage) - affiché au checkout pour que
        la remise appliquée par payments.initiate_payment ne surprenne jamais."""
        from subscriptions.models import solde_credit_parrainage

        return solde_credit_parrainage(obj)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "pseudo"]

    def validate_pseudo(self, value):
        # Chaîne vide normalisée en None : le champ est unique en base, deux comptes
        # ayant chacun "" (contrairement à NULL, une valeur comme une autre pour une
        # contrainte unique) entreraient en collision au premier qui essaierait de
        # l'enregistrer après un autre - voir le help_text du champ sur le modèle.
        return value or None
