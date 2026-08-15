from django import forms
from django.contrib import admin, messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    ManualPayment,
    ManualPaymentAlreadyReviewed,
    ManualPaymentStatus,
    MobileMoneyAccount,
    Transaction,
)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "amount", "status", "phone_number", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__phone_number", "campay_reference", "external_reference"]
    readonly_fields = ["external_reference", "campay_reference", "raw_response", "created_at", "updated_at"]


@admin.register(MobileMoneyAccount)
class MobileMoneyAccountAdmin(admin.ModelAdmin):
    list_display = ["operator", "phone_number", "account_name", "active", "updated_at"]
    list_filter = ["active", "operator"]


class ManualPaymentAdminForm(forms.ModelForm):
    class Meta:
        model = ManualPayment
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("status") == ManualPaymentStatus.REJECTED and not cleaned.get("rejection_reason"):
            self.add_error("rejection_reason", "Motif obligatoire pour rejeter un paiement.")
        return cleaned


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    """
    Toute la logique d'approbation/rejet passe par ManualPayment.approve()/reject()
    (models.py) - jamais un save() brut sur une transition de statut - pour
    bénéficier du même verrou anti double-clic/double-admin que le reste du module
    (voir save_model ci-dessous) et de l'activation d'abonnement partagée avec Campay.
    """

    form = ManualPaymentAdminForm

    list_display = [
        "id", "user", "plan", "operator", "montant_display", "payer_phone_number",
        "transaction_reference", "status", "created_at",
    ]
    list_filter = ["status", "operator", "plan__cursus"]
    search_fields = [
        "transaction_reference", "payer_phone_number", "user__phone_number", "user__full_name",
    ]
    date_hierarchy = "created_at"

    # Champs déclarés par l'utilisateur : jamais éditables depuis l'admin, qui ne
    # fait que trancher (voir get_readonly_fields). "proof_display" remplace le
    # champ brut "proof" pour offrir un lien cliquable plutôt que le chemin du fichier.
    DECLARED_FIELDS = [
        "user", "plan", "operator", "amount_expected", "amount_declared",
        "payer_phone_number", "transaction_reference", "paid_at", "proof_display", "declared_ip",
    ]
    DECISION_FIELDS = ["status", "rejection_reason", "admin_comment"]
    ALWAYS_READONLY = ["subscription", "inscription_inedite", "reviewed_by", "reviewed_at", "created_at", "updated_at"]

    fieldsets = (
        ("Déclaration de l'utilisateur", {"fields": tuple(DECLARED_FIELDS)}),
        ("Décision administrative", {"fields": tuple(DECISION_FIELDS)}),
        ("Suivi", {"fields": tuple(ALWAYS_READONLY)}),
    )

    @admin.display(description="Montant (attendu / déclaré)")
    def montant_display(self, obj):
        mismatch = obj.amount_expected != obj.amount_declared
        style = "color: #b91c1c; font-weight: 600;" if mismatch else ""
        return format_html(
            '<span style="{}">{} / {} FCFA</span>', style, obj.amount_expected, obj.amount_declared,
        )

    @admin.display(description="Preuve")
    def proof_display(self, obj):
        if not obj.proof:
            return "-"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">Voir la capture</a>', obj.proof.url,
        )

    def has_add_permission(self, request):
        # Un ManualPayment se crée uniquement via la déclaration utilisateur (API) -
        # jamais depuis l'admin, qui ne fait que trancher une déclaration existante.
        return False

    def has_delete_permission(self, request, obj=None):
        # Enregistrement financier - jamais supprimé, seulement rejeté (voir mission,
        # section 8 : toutes les opérations importantes doivent rester traçables).
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and obj.status != ManualPaymentStatus.PENDING:
            return self.DECLARED_FIELDS + self.DECISION_FIELDS + self.ALWAYS_READONLY
        return self.DECLARED_FIELDS + self.ALWAYS_READONLY

    def save_model(self, request, obj, form, change):
        if not change:
            return  # jamais atteint (has_add_permission=False) - garde-fou seulement

        previous_status = ManualPayment.objects.get(pk=obj.pk).status
        new_status = form.cleaned_data.get("status")
        if previous_status != ManualPaymentStatus.PENDING or new_status == previous_status:
            # Rien à trancher (ex. l'admin a juste modifié admin_comment sans changer
            # le statut, ou tente de re-décider un paiement déjà tranché - bloqué par
            # ailleurs via get_readonly_fields, mais on ne fait jamais confiance
            # uniquement à l'UI) : sauvegarde normale des champs libres seulement.
            super().save_model(request, obj, form, change)
            return

        try:
            if new_status == ManualPaymentStatus.APPROVED:
                decided = ManualPayment.objects.get(pk=obj.pk).approve(admin_user=request.user)
                cible = "add-on Épreuves Inédites activé" if decided.inscription_inedite_id else "abonnement activé"
                messages.success(request, f"Paiement #{decided.pk} validé, {cible}.")
            elif new_status == ManualPaymentStatus.REJECTED:
                decided = ManualPayment.objects.get(pk=obj.pk).reject(
                    admin_user=request.user,
                    reason=form.cleaned_data.get("rejection_reason"),
                    comment=form.cleaned_data.get("admin_comment", ""),
                )
                messages.success(request, f"Paiement #{decided.pk} rejeté.")
            else:
                super().save_model(request, obj, form, change)
                return
        except ManualPaymentAlreadyReviewed:
            messages.error(
                request,
                "Ce paiement a déjà été traité entre-temps (par vous ou un autre "
                "administrateur) - rien n'a été modifié.",
            )
            return

        obj.status = decided.status
        obj.reviewed_by = decided.reviewed_by
        obj.reviewed_at = decided.reviewed_at
        obj.subscription = decided.subscription
        obj.inscription_inedite = decided.inscription_inedite

    def changelist_view(self, request, extra_context=None):
        today = timezone.localdate()
        stats = ManualPayment.objects.aggregate(
            pending=Count("id", filter=Q(status=ManualPaymentStatus.PENDING)),
            rejected=Count("id", filter=Q(status=ManualPaymentStatus.REJECTED)),
            approved_today=Count(
                "id", filter=Q(status=ManualPaymentStatus.APPROVED, reviewed_at__date=today),
            ),
            total_approved_amount=Sum(
                "amount_declared", filter=Q(status=ManualPaymentStatus.APPROVED),
            ),
        )
        repartition = (
            ManualPayment.objects.filter(status=ManualPaymentStatus.APPROVED)
            .values("operator")
            .annotate(total=Sum("amount_declared"), n=Count("id"))
        )

        extra_context = extra_context or {}
        extra_context["manual_payment_stats"] = {
            "pending": stats["pending"] or 0,
            "rejected": stats["rejected"] or 0,
            "approved_today": stats["approved_today"] or 0,
            "total_approved_amount": stats["total_approved_amount"] or 0,
            "repartition": list(repartition),
        }
        return super().changelist_view(request, extra_context=extra_context)
