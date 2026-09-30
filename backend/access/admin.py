from django.contrib import admin

from .models import LectureProgress


@admin.register(LectureProgress)
class LectureProgressAdmin(admin.ModelAdmin):
    list_display = ["profil", "lesson", "cours", "first_read_at", "last_read_at"]
    list_filter = ["first_read_at"]
    search_fields = ["profil__compte__phone_number", "lesson__title", "cours__titre"]
    readonly_fields = ["profil", "lesson", "cours", "first_read_at", "last_read_at"]

    def has_add_permission(self, request):
        return False
