from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import OTPCode, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["phone_number"]
    list_display = ["phone_number", "full_name", "referral_code", "referred_by", "is_staff", "is_active", "date_joined"]
    search_fields = ["phone_number", "full_name", "referral_code"]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Informations personnelles", {"fields": ("full_name",)}),
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
    list_display = ["phone_number", "code", "is_used", "attempts", "expires_at", "created_at"]
    list_filter = ["is_used"]
    search_fields = ["phone_number"]
    readonly_fields = ["phone_number", "code", "expires_at", "is_used", "attempts", "created_at"]

    def has_add_permission(self, request):
        return False
