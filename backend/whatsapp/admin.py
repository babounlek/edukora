from django.contrib import admin

from .models import OptIn


@admin.register(OptIn)
class OptInAdmin(admin.ModelAdmin):
    list_display = ["user", "opted_in_at", "opted_out_at", "is_active"]
    list_filter = ["opted_out_at"]
    search_fields = ["user__phone_number"]
    readonly_fields = ["user", "opted_in_at", "opted_out_at"]

    @admin.display(boolean=True, description="Actif")
    def is_active(self, obj):
        return obj.is_active

    def has_add_permission(self, request):
        return False
