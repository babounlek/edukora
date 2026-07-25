from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "amount", "status", "phone_number", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__phone_number", "campay_reference", "external_reference"]
    readonly_fields = ["external_reference", "campay_reference", "raw_response", "created_at", "updated_at"]
