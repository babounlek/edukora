"""
Refonte du compte utilisateur en une seule migration : numéro nullable, stockage
E.164, adresse e-mail, et table des identités de connexion.

Volontairement schéma + données dans un même fichier : convertir les numéros au
format international n'est pas une étape optionnelle qu'on pourrait déployer plus
tard, c'est ce qui rend les lignes existantes conformes au champ qui vient d'être
altéré. Les séparer laisserait une fenêtre - même courte - où toute la base porte
des numéros invalides au regard du validateur du modèle.

Réversible : la marche arrière reconvertit les numéros camerounais au format local
et supprime les identités `phone` recréées à l'aller. Une identité tierce
(Google/passkey) créée après coup ferait en revanche perdre son moyen de connexion
à l'utilisateur - la marche arrière n'a de sens qu'immédiatement après l'aller,
avant toute nouvelle méthode branchée.
"""

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

# Dupliqué de users.phone.to_e164 plutôt qu'importé : une migration doit rester
# figée dans le temps, alors que le module applicatif évoluera (nouveaux pays,
# nouvelles règles). L'importer ferait réécrire l'histoire des bases déjà migrées.
CM_DIAL_CODE = "237"


def _to_e164(raw):
    if not raw:
        return None
    cleaned = "".join(c for c in str(raw) if c.isdigit() or c == "+")
    if cleaned.startswith("+"):
        return cleaned
    if cleaned.startswith(CM_DIAL_CODE) and len(cleaned) > len(CM_DIAL_CODE):
        return f"+{cleaned}"
    return f"+{CM_DIAL_CODE}{cleaned.lstrip('0')}"


def _to_local(raw):
    if not raw:
        return ""
    digits = str(raw).lstrip("+")
    return digits[len(CM_DIAL_CODE):] if digits.startswith(CM_DIAL_CODE) else digits


def passer_en_e164(apps, schema_editor):
    User = apps.get_model("users", "User")
    OTPCode = apps.get_model("users", "OTPCode")

    for user in User.objects.exclude(phone_number__startswith="+").iterator():
        # Chaîne vide -> NULL : le champ est unique et nullable désormais, or deux
        # comptes portant "" entreraient en collision là où deux NULL coexistent.
        User.objects.filter(pk=user.pk).update(phone_number=_to_e164(user.phone_number))

    for otp in OTPCode.objects.exclude(phone_number__startswith="+").iterator():
        OTPCode.objects.filter(pk=otp.pk).update(phone_number=_to_e164(otp.phone_number) or "")


def creer_identites_telephone(apps, schema_editor):
    """
    Chaque compte existant reçoit son identité `phone`, de sorte qu'aucun compte
    n'existe sans identité. Le code d'authentification à venir peut ainsi traiter
    l'absence d'identité comme une anomalie, jamais comme un cas de transition à
    supporter indéfiniment.
    """
    User = apps.get_model("users", "User")
    AuthIdentity = apps.get_model("users", "AuthIdentity")

    AuthIdentity.objects.bulk_create(
        [
            AuthIdentity(user_id=user.pk, provider="phone", provider_uid=user.phone_number)
            for user in User.objects.exclude(phone_number=None).iterator()
        ],
        batch_size=500,
        ignore_conflicts=True,
    )


def revenir_au_format_local(apps, schema_editor):
    User = apps.get_model("users", "User")
    OTPCode = apps.get_model("users", "OTPCode")

    for user in User.objects.filter(phone_number__startswith=f"+{CM_DIAL_CODE}").iterator():
        User.objects.filter(pk=user.pk).update(phone_number=_to_local(user.phone_number))
    for otp in OTPCode.objects.filter(phone_number__startswith=f"+{CM_DIAL_CODE}").iterator():
        OTPCode.objects.filter(pk=otp.pk).update(phone_number=_to_local(otp.phone_number))


def supprimer_identites_telephone(apps, schema_editor):
    apps.get_model("users", "AuthIdentity").objects.filter(provider="phone").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_otpcode_ip_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True,
                help_text="Facultatif. Renseigné par l'utilisateur ou remonté par un fournisseur tiers.",
                max_length=254,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(
                default=False,
                help_text="Vrai uniquement si un fournisseur a attesté l'adresse, ou après vérification par lien.",
            ),
        ),
        migrations.AlterField(
            model_name="otpcode",
            name="phone_number",
            field=models.CharField(max_length=16),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                help_text="Numéro au format international E.164, ex : +237677123456.",
                max_length=16,
                null=True,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Le numéro doit être au format international, ex : +237677123456.",
                        regex="^\\+[1-9]\\d{7,14}$",
                    )
                ],
            ),
        ),
        # Après l'élargissement des deux colonnes à 16 caractères, jamais avant :
        # "+237" + 9 chiffres ne tient pas dans le max_length=9 d'origine.
        migrations.RunPython(passer_en_e164, revenir_au_format_local),
        migrations.CreateModel(
            name="AuthIdentity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        choices=[
                            ("phone", "Téléphone (OTP)"),
                            ("google", "Google"),
                            ("apple", "Apple"),
                            ("email", "E-mail (lien magique)"),
                            ("passkey", "Clé d'accès"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "provider_uid",
                    models.CharField(
                        help_text="Identifiant stable chez le fournisseur : numéro E.164 pour `phone`, `sub` OpenID pour Google/Apple, identifiant de credential pour une passkey.",
                        max_length=255,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        help_text="Adresse telle que remontée par le fournisseur, conservée pour audit - l'adresse faisant foi pour le compte reste User.email.",
                        max_length=254,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="identities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "identité de connexion",
                "verbose_name_plural": "identités de connexion",
                "ordering": ["provider", "-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "provider"],
                        name="users_authi_user_id_4be3b9_idx",
                    )
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("provider", "provider_uid"),
                        name="unique_identity_per_provider",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("provider", "passkey"), _negated=True),
                        fields=("user", "provider"),
                        name="unique_provider_per_user_except_passkey",
                    ),
                ],
            },
        ),
        # En dernier : dépend à la fois de la table AuthIdentity et des numéros déjà
        # convertis, puisque provider_uid recopie le numéro au format canonique.
        migrations.RunPython(creer_identites_telephone, supprimer_identites_telephone),
    ]
