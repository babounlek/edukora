from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuthIdentity, OTPCode, User


class AuthIdentityInline(admin.TabularInline):
    """
    En lecture seule : rattacher ou détacher une méthode de connexion à la main
    revient à donner ou retirer un accès au compte, ce qui doit passer par le
    parcours applicatif (preuve de possession) et jamais par une saisie d'admin.
    """

    model = AuthIdentity
    extra = 0
    can_delete = False
    readonly_fields = ["provider", "provider_uid", "email", "created_at", "last_used_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["phone_number"]
    list_display = ["phone_number", "email", "full_name", "pseudo", "referral_code", "referred_by", "is_staff", "is_active", "date_joined"]
    search_fields = ["phone_number", "email", "full_name", "pseudo", "referral_code"]
    inlines = [AuthIdentityInline]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Informations personnelles", {"fields": ("full_name", "pseudo", "email", "email_verified")}),
        ("Parrainage", {"fields": ("referral_code", "referred_by")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ["referral_code"]
    autocomplete_fields = ["referred_by"]
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2"),
        }),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    # ip_address affichée et cherchable : c'est par là qu'on constate une rafale
    # d'envois depuis une même source, et qu'on vérifie la distribution réelle des IP
    # avant d'ajuster OTP_MAX_PER_IP_PER_HOUR (voir settings.py, mise en garde CGNAT).
    list_display = ["destination", "canal", "code", "is_used", "attempts", "ip_address", "expires_at", "created_at"]
    # Filtrer par canal est le premier geste pour répondre à « combien de SMS
    # ai-je envoyés ? », la seule des deux questions qui engage de l'argent.
    list_filter = ["canal", "is_used"]
    search_fields = ["destination", "ip_address"]
    readonly_fields = [
        "canal", "destination", "code", "expires_at", "is_used", "attempts", "created_at",
        "ip_address",
    ]

    def has_add_permission(self, request):
        return False
