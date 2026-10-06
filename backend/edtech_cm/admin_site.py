from django.contrib import admin
from django.contrib.admin.apps import AdminConfig

# Apps épinglées en tête de l'accueil admin et du menu latéral, dans cet ordre ; les
# autres restent triées alphabétiquement. "payments" : la validation des paiements
# manuels est l'action admin la plus fréquente, elle ne doit pas exiger de défiler.
APPS_EN_TETE = ["payments"]


class EdukoraAdminSite(admin.AdminSite):
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        rang = {label: i for i, label in enumerate(APPS_EN_TETE)}
        return sorted(app_list, key=lambda app: rang.get(app["app_label"], len(rang)))


class EdukoraAdminConfig(AdminConfig):
    default_site = "edtech_cm.admin_site.EdukoraAdminSite"
