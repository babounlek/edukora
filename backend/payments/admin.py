import logging
from urllib.parse import urlparse

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Exists, OuterRef, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import (
    ManualPayment,
    ManualPaymentAlreadyReviewed,
    ManualPaymentRejectReason,
    ManualPaymentStatus,
    MobileMoneyAccount,
    Transaction,
)

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")

ACTION_VALIDER = "valider"
ACTION_REJETER = "rejeter"


class StatutFilter(admin.SimpleListFilter):
    """
    Remplace list_filter["status"] : par défaut la liste n'affiche que les paiements
    EN ATTENTE (le travail à faire), du plus ancien au plus récent. Une recherche
    sans filtre explicite porte sur tous les statuts - chercher une référence déjà
    traitée ne doit pas renvoyer « aucun résultat » à cause d'un filtre invisible.
    """

    title = "statut"
    parameter_name = "statut"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self._request = request

    def lookups(self, request, model_admin):
        return [
            (ManualPaymentStatus.PENDING, "En attente"),
            (ManualPaymentStatus.APPROVED, "Validés"),
            (ManualPaymentStatus.REJECTED, "Rejetés"),
            ("all", "Tous"),
        ]

    @staticmethod
    def effective(request, value):
        if value:
            return value
        return "all" if request.GET.get("q") else ManualPaymentStatus.PENDING

    def queryset(self, request, queryset):
        value = self.effective(request, self.value())
        if value == "all":
            return queryset
        if value in ManualPaymentStatus.values:
            return queryset.filter(status=value)
        return queryset

    def choices(self, changelist):
        current = self.effective(self._request, self.value())
        for lookup, title in self.lookup_choices:
            yield {
                "selected": current == str(lookup),
                "query_string": changelist.get_query_string({self.parameter_name: lookup}),
                "display": title,
            }


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "amount", "credit_applique", "status", "phone_number", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__phone_number", "provider", "provider_reference", "external_reference"]
    readonly_fields = ["external_reference", "provider", "provider_reference", "raw_response", "created_at", "updated_at"]


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
        "id", "decision_display", "user", "plan", "operator", "montant_display",
        "payer_phone_number", "reference_display", "preuve_miniature", "statut_display", "created_at",
    ]
    list_select_related = ["user", "plan", "reviewed_by"]
    list_filter = [StatutFilter, "operator", "plan__cursus"]
    actions = ["valider_selection", "rejeter_selection"]
    decision_confirm_template = "admin/payments/manualpayment/decision_confirm.html"
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

    @staticmethod
    def _proof_is_image(obj):
        return bool(obj.proof) and obj.proof.name.lower().endswith(IMAGE_EXTENSIONS)

    @admin.display(description="Capture")
    def preuve_miniature(self, obj):
        if not obj.proof:
            return "-"
        if self._proof_is_image(obj):
            # Ouverte en fenêtre superposée par le script de change_list.html (le lien
            # reste un href ordinaire : sans JavaScript, il ouvre l'image dans un onglet).
            return format_html(
                '<a class="mp-proof" href="{0}" target="_blank" rel="noopener noreferrer">'
                '<img src="{0}" alt="Capture" loading="lazy" style="height:44px; width:auto; border-radius:4px;"></a>',
                obj.proof.url,
            )
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Ouvrir</a>', obj.proof.url)

    @admin.display(description="Référence", ordering="transaction_reference")
    def reference_display(self, obj):
        if getattr(obj, "ref_vue", False):
            return format_html(
                '{} <span class="mp-badge mp-badge-warn" title="Cette référence apparaît dans un autre '
                'paiement (autre statut, autre opérateur ou nouvelle déclaration)">Réf. déjà vue</span>',
                obj.transaction_reference,
            )
        return obj.transaction_reference

    @admin.display(description="Statut", ordering="status")
    def statut_display(self, obj):
        classe = {
            ManualPaymentStatus.PENDING: "mp-badge-pending",
            ManualPaymentStatus.APPROVED: "mp-badge-ok",
            ManualPaymentStatus.REJECTED: "mp-badge-ko",
        }.get(obj.status, "")
        return format_html('<span class="mp-badge {}">{}</span>', classe, obj.get_status_display())

    @admin.display(description="Décision")
    def decision_display(self, obj):
        if obj.status == ManualPaymentStatus.PENDING:
            return format_html(
                '<a class="mp-btn mp-btn-ok" href="{}">Valider</a> <a class="mp-btn mp-btn-ko" href="{}">Rejeter</a>',
                self._decision_url(obj.pk, ACTION_VALIDER), self._decision_url(obj.pk, ACTION_REJETER),
            )
        qui = obj.reviewed_by.full_name or obj.reviewed_by.phone_number if obj.reviewed_by_id else "-"
        quand = timezone.localtime(obj.reviewed_at).strftime("%d/%m %H:%M") if obj.reviewed_at else ""
        motif = f" ({obj.get_rejection_reason_display()})" if obj.rejection_reason else ""
        return format_html('<span class="mp-muted">{}{} - {} {}</span>', obj.get_status_display(), motif, qui, quand)

    def _decision_url(self, pk, action):
        return reverse(f"{self.admin_site.name}:payments_manualpayment_decider", args=[pk, action])

    # ------------------------------------------------------------------ requêtes

    def get_queryset(self, request):
        # ref_vue : une autre déclaration porte la même référence (n'importe quel
        # statut/opérateur). Le signal ne bloque rien à lui seul - voir _alertes.
        autres = ManualPayment.objects.filter(
            transaction_reference=OuterRef("transaction_reference"),
        ).exclude(pk=OuterRef("pk"))
        return super().get_queryset(request).annotate(ref_vue=Exists(autres))

    def get_ordering(self, request):
        # File d'attente : le plus ancien d'abord (premier arrivé, premier servi) ;
        # l'historique reste du plus récent au plus ancien.
        if StatutFilter.effective(request, request.GET.get(StatutFilter.parameter_name)) == ManualPaymentStatus.PENDING:
            return ["created_at"]
        return ["-created_at"]

    # --------------------------------------------------------- décision (UI liste)

    def get_urls(self):
        custom = [
            path(
                "<int:pk>/decider/<str:action>/",
                self.admin_site.admin_view(self.decider_view),
                name="payments_manualpayment_decider",
            ),
        ]
        return custom + super().get_urls()

    @staticmethod
    def _alertes(payment):
        alertes = []
        if payment.amount_expected != payment.amount_declared:
            alertes.append(
                f"Montant incohérent : attendu {payment.amount_expected} FCFA, déclaré {payment.amount_declared} FCFA."
            )
        if getattr(payment, "ref_vue", False):
            alertes.append("Cette référence de transaction apparaît dans un autre paiement.")
        return alertes

    def _contexte_confirmation(self, request, action, items, **extra):
        opts = self.model._meta
        return {
            **self.admin_site.each_context(request),
            "opts": opts,
            "app_label": opts.app_label,
            "action": action,
            "verbe": "Valider" if action == ACTION_VALIDER else "Rejeter",
            "title": "Valider le paiement" if action == ACTION_VALIDER else "Rejeter le paiement",
            "items": items,
            "motifs": ManualPaymentRejectReason.choices,
            **extra,
        }

    @staticmethod
    def _item(payment, alertes):
        return {
            "payment": payment,
            "alertes": alertes,
            "proof_is_image": ManualPaymentAdmin._proof_is_image(payment),
        }

    def _appliquer(self, request, payment, action, reason="", comment=""):
        """Applique la décision via approve()/reject() - jamais un save() direct.
        Retourne True si la décision a été appliquée."""
        try:
            if action == ACTION_VALIDER:
                decided = ManualPayment.objects.get(pk=payment.pk).approve(admin_user=request.user)
                cible = "add-on Épreuves Inédites activé" if decided.inscription_inedite_id else "abonnement activé"
                messages.success(request, f"Paiement #{decided.pk} validé, {cible}.")
            else:
                decided = ManualPayment.objects.get(pk=payment.pk).reject(
                    admin_user=request.user, reason=reason, comment=comment,
                )
                messages.success(request, f"Paiement #{decided.pk} rejeté.")
            return True
        except ManualPaymentAlreadyReviewed:
            messages.warning(
                request,
                f"Paiement #{payment.pk} déjà traité entre-temps (par vous ou un autre administrateur) - "
                "rien n'a été modifié.",
            )
        except Exception:  # noqa: BLE001 - un échec (ex. SMS) ne doit pas interrompre un lot
            logger.exception("Décision paiement manuel #%s en échec", payment.pk)
            messages.error(
                request,
                f"Paiement #{payment.pk} : erreur inattendue, vérifiez son statut avant de recommencer.",
            )
        return False

    def _safe_next(self, request, candidate):
        if candidate and url_has_allowed_host_and_scheme(
            candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
        ):
            return candidate
        return reverse(f"{self.admin_site.name}:payments_manualpayment_changelist")

    def decider_view(self, request, pk, action):
        if action not in (ACTION_VALIDER, ACTION_REJETER):
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied

        payment = get_object_or_404(self.get_queryset(request), pk=pk)
        if request.method == "POST":
            suivant = self._safe_next(request, request.POST.get("next"))
        else:
            referer = request.META.get("HTTP_REFERER", "")
            # Le chemin + la requête du référent (filtres/recherche/page conservés).
            parsed = urlparse(referer)
            suivant = self._safe_next(request, f"{parsed.path}?{parsed.query}" if parsed.path else "")

        if payment.status != ManualPaymentStatus.PENDING:
            messages.warning(request, f"Paiement #{payment.pk} déjà traité - rien à faire.")
            return HttpResponseRedirect(suivant)

        erreur = ""
        reason = request.POST.get("rejection_reason", "")
        comment = request.POST.get("admin_comment", "").strip()
        if request.method == "POST":
            if action == ACTION_REJETER and reason not in ManualPaymentRejectReason.values:
                erreur = "Choisissez un motif de rejet."
            else:
                self._appliquer(request, payment, action, reason=reason, comment=comment)
                return HttpResponseRedirect(suivant)

        context = self._contexte_confirmation(
            request, action, [self._item(payment, self._alertes(payment))],
            bulk=False, next=suivant, erreur=erreur, reason=reason, comment=comment,
        )
        return TemplateResponse(request, self.decision_confirm_template, context)

    # ----------------------------------------------------------- actions groupées

    def _action_groupee(self, request, queryset, action):
        pendings = list(queryset.filter(status=ManualPaymentStatus.PENDING).select_related("user", "plan"))
        ignores = queryset.count() - len(pendings)

        if action == ACTION_VALIDER:
            # Pas de validation en lot d'un paiement à examiner de près : il se valide
            # un par un depuis sa ligne, preuve et alertes sous les yeux.
            eligibles = [p for p in pendings if not self._alertes(p)]
            exclus = [self._item(p, self._alertes(p)) for p in pendings if self._alertes(p)]
        else:
            eligibles, exclus = pendings, []

        if not eligibles:
            self.message_user(
                request,
                "Aucun paiement de la sélection ne peut être traité en lot "
                "(déjà traités, ou à examiner un par un).",
                messages.WARNING,
            )
            return None

        reason = request.POST.get("rejection_reason", "")
        comment = request.POST.get("admin_comment", "").strip()
        erreur = ""
        if request.POST.get("post") == "yes":
            if action == ACTION_REJETER and reason not in ManualPaymentRejectReason.values:
                erreur = "Choisissez un motif de rejet."
            else:
                ok = sum(self._appliquer(request, p, action, reason=reason, comment=comment) for p in eligibles)
                if len(eligibles) > 1:
                    verbe = "validés" if action == ACTION_VALIDER else "rejetés"
                    self.message_user(request, f"{ok} paiement(s) {verbe} sur {len(eligibles)}.", messages.INFO)
                return None

        context = self._contexte_confirmation(
            request, action, [self._item(p, []) for p in eligibles],
            bulk=True, exclus=exclus, ignores=ignores, erreur=erreur, reason=reason, comment=comment,
            title="Valider la sélection" if action == ACTION_VALIDER else "Rejeter la sélection",
            selected=[p.pk for p in eligibles],
            action_name="valider_selection" if action == ACTION_VALIDER else "rejeter_selection",
        )
        return TemplateResponse(request, self.decision_confirm_template, context)

    @admin.action(description="Valider les paiements sélectionnés", permissions=["change"])
    def valider_selection(self, request, queryset):
        return self._action_groupee(request, queryset, ACTION_VALIDER)

    @admin.action(description="Rejeter les paiements sélectionnés", permissions=["change"])
    def rejeter_selection(self, request, queryset):
        return self._action_groupee(request, queryset, ACTION_REJETER)

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
