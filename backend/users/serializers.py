from django.utils import timezone
from rest_framework import serializers

from catalog.models import Cursus, ExamSession
from catalog.serializers import CursusSerializer

from .email_service import normalize_email
from .models import Profil, User
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
    cursus_prepare = CursusSerializer(read_only=True)
    compte_a_rebours = serializers.SerializerMethodField()
    a_un_abonnement_actif = serializers.SerializerMethodField()
    rappels_invite_refusee = serializers.SerializerMethodField()
    profil_actif = serializers.SerializerMethodField()
    pin_parent_actif = serializers.SerializerMethodField()
    session_restreinte = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "phone_number", "email", "email_verified", "full_name", "pseudo",
            "date_joined", "referral_code", "filleuls_count", "auth_methods",
            "credit_parrainage_disponible", "cursus_prepare", "compte_a_rebours",
            "a_un_abonnement_actif", "rappels_actifs", "rappels_invite_refusee",
            "profil_actif", "pin_parent_actif", "session_restreinte",
        ]

    def get_rappels_invite_refusee(self, obj):
        return obj.rappels_invite_refusee_at is not None

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
        """
        Solde de crédit parrainage encore dépensable (voir
        subscriptions.models.solde_credit_parrainage) - mécanisme gelé depuis le
        2026-09-28 (parrainage redevenu un simple partage de lien, sans récompense
        d'aucun côté), conservé uniquement pour que les crédits déjà accordés avant
        cette date restent affichés et dépensables au checkout.
        """
        from subscriptions.models import solde_credit_parrainage

        return solde_credit_parrainage(obj)

    def get_compte_a_rebours(self, obj):
        """
        Jours restants avant l'examen préparé, ou None tant que l'utilisateur n'a rien
        déclaré (voir User.cursus_prepare) - le frontend n'a alors simplement rien à
        afficher, jamais un compte à rebours vers une date par défaut.
        """
        if obj.cursus_prepare is None:
            return None
        return ExamSession.compte_a_rebours_pour(obj.cursus_prepare)

    def get_a_un_abonnement_actif(self, obj):
        """
        Vrai dès qu'un abonnement est actif, sur n'importe quel cursus - sert au
        Header à masquer l'entrée "Tarifs" : un menu qui propose en permanence
        d'acheter ce qu'on a déjà acheté n'est plus une navigation, c'est du bruit.

        Volontairement pas scopé à `cursus_prepare` : l'entrée de menu est globale,
        et un élève abonné sur un cursus voisin n'a pas plus besoin qu'un autre qu'on
        lui repropose la page Tarifs à chaque écran.
        """
        from subscriptions.models import Subscription

        return Subscription.objects.filter(user=obj, expires_at__gt=timezone.now()).exists()

    def get_pin_parent_actif(self, obj):
        return bool(obj.pin_parent_hash)

    def get_session_restreinte(self, obj):
        from .parent import session_restreinte

        request = self.context.get("request")
        if request is None or getattr(request.user, "pk", None) != obj.pk:
            return False
        return session_restreinte(request)

    def get_profil_actif(self, obj):
        """
        L'enfant actif pour `obj` - voir users.profils.profil_actif, LE point d'entrée
        qui lit la claim `profil_id` du token.

        `profil_actif(request)` lit `request.user`, pas `obj` : les deux coïncident
        pour la quasi-totalité des appelants (me_view, etc., où `obj` EST
        `request.user`), mais pas dans les vues de connexion (otp_verify_view,
        google_signin_view, email_code_verify_view) - `AllowAny`, `request.user` y
        est encore anonyme au moment où le token de `obj` vient tout juste d'être émis
        dans la même réponse. Aucune claim n'existe alors de toute façon (le token
        n'a pas encore été utilisé une seule fois) : `obj.profils.first()` y est
        donc la seule réponse correcte, jamais None via profil_actif(request).
        """
        from .profils import profil_actif

        request = self.context.get("request")
        if request is not None and getattr(request.user, "pk", None) == obj.pk:
            profil = profil_actif(request)
        else:
            profil = obj.profils.first()
        return ProfilSerializer(profil).data if profil is not None else None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    # Explicite plutôt que déduit du modèle : `allow_null` (on doit pouvoir effacer sa
    # déclaration) et la vérification du pays actif ci-dessous ne sont pas ce que
    # ModelSerializer génèrerait tout seul.
    cursus_prepare = serializers.PrimaryKeyRelatedField(
        queryset=Cursus.objects.select_related("country"), required=False, allow_null=True,
    )

    # Écrit par le frontend quand l'élève écarte l'invitation (True) ou la rouvre (False) :
    # on stocke le moment, pas le booléen - voir User.rappels_invite_refusee_at.
    rappels_invite_refusee = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["full_name", "pseudo", "cursus_prepare", "rappels_actifs", "rappels_invite_refusee"]

    def validate_rappels_actifs(self, value):
        # Des rappels envoyés à une adresse non confirmée arriveraient chez quelqu'un qui n'a
        # rien demandé - la confirmation par code (voir users.account) est la seule preuve
        # que l'adresse est bien celle de l'élève.
        if value and not (self.instance and self.instance.email_verified):
            raise serializers.ValidationError("Ajoute et confirme d'abord une adresse e-mail.")
        return value

    def update(self, instance, validated_data):
        refusee = validated_data.pop("rappels_invite_refusee", None)
        if refusee is not None:
            instance.rappels_invite_refusee_at = timezone.now() if refusee else None
            instance.save(update_fields=["rappels_invite_refusee_at"])
        return super().update(instance, validated_data)

    def validate_cursus_prepare(self, value):
        # Même règle que les vues publiques (voir VisibleQuerySet.visibles et
        # quiz.views.start_session) : un pays désactivé n'a pas de contenu visible,
        # déclarer préparer un de ses examens n'amènerait l'utilisateur nulle part.
        if value is not None and not value.country.actif:
            raise serializers.ValidationError("Ce cursus n'est pas disponible.")
        return value

    def validate_pseudo(self, value):
        # Chaîne vide normalisée en None : le champ est unique en base, deux comptes
        # ayant chacun "" (contrairement à NULL, une valeur comme une autre pour une
        # contrainte unique) entreraient en collision au premier qui essaierait de
        # l'enregistrer après un autre - voir le help_text du champ sur le modèle.
        return value or None


class ProfilSerializer(serializers.ModelSerializer):
    """
    L'enfant pour qui un abonnement est acheté - voir Profil.prenom. Réutilisé par
    subscriptions.serializers.SubscriptionSerializer pour afficher, sur chaque
    abonnement, à qui il appartient (voir AccesPage.tsx, qui regroupe par profil).
    """

    pin_actif = serializers.SerializerMethodField()
    connexion_active = serializers.SerializerMethodField()

    class Meta:
        model = Profil
        fields = ["id", "prenom", "ordre", "pin_actif", "connexion_active"]

    def get_pin_actif(self, obj):
        return bool(obj.pin_hash)

    def get_connexion_active(self, obj):
        return bool(obj.connexion_phone)


class ProfilWriteSerializer(serializers.ModelSerializer):
    """
    Création/renommage d'un profil. `prenom` obligatoire et non vide ici,
    contrairement au modèle (blank=True, pour ne jamais bloquer le backfill
    automatique d'un compte migré) : la fonctionnalité "nommer chaque abonnement"
    n'a de sens que si un nom est effectivement saisi.
    """

    class Meta:
        model = Profil
        fields = ["id", "prenom"]

    def validate_prenom(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Le prénom ne peut pas être vide.")
        return value
