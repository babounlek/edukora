from django.contrib import admin

from .models import RelanceEnvoyee


@admin.register(RelanceEnvoyee)
class RelanceEnvoyeeAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "reference", "canal", "envoyee_at")
    list_filter = ("type", "canal")
    search_fields = ("user__email", "user__phone_number")
    readonly_fields = ("user", "type", "reference", "canal", "envoyee_at")
