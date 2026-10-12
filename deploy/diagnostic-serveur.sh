#!/usr/bin/env bash
# État du serveur, EN LECTURE SEULE : rien n'est modifié, rien n'est redémarré.
# À lancer sur le Droplet, depuis le clone du dépôt ; la sortie est conçue pour pouvoir être
# collée telle quelle (elle n'affiche AUCUN secret, adresse e-mail ni numéro de téléphone :
# seulement des noms de variables, des modes et des compteurs).
#
#   deploy/diagnostic-serveur.sh
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1

titre() { printf '\n== %s ==\n' "$1"; }

titre "Dépôt"
git rev-parse --short HEAD 2>&1
git status --short 2>&1 | head -10
echo "(lignes ci-dessus = fichiers modifiés localement sur le serveur ; vide = propre)"
cat .deploy/current_tag 2>/dev/null && echo "(version déployée par deploy.sh)" || echo "Pas de .deploy/current_tag : jamais déployé par deploy.sh"

titre "Système"
echo "Disque / :"; df -h / | tail -1
echo "Mémoire :"; free -m | sed -n '1,2p'
echo "Docker :"; docker --version
echo "Région/taille : $(curl -fsS --max-time 3 http://169.254.169.254/metadata/v1/region 2>/dev/null || echo inconnue)"

titre "Conteneurs"
docker compose ps --format 'table {{.Service}}\t{{.Image}}\t{{.Status}}' 2>&1

titre ".env (noms et modes seulement, jamais de valeurs secrètes)"
if [ -f .env ]; then
  stat -c 'droits %a, propriétaire %U' .env
  for cle in DEBUG ALLOW_TEST_DATA CAMPAY_ENVIRONMENT SMS_BACKEND WHATSAPP_BACKEND EMAIL_BACKEND SITE_DOMAIN SPACES_REGION SPACES_BUCKET SENTRY_DSN ROBOTS_TAG; do
    valeur="$(grep -E "^$cle=" .env | tail -1 | cut -d= -f2- | tr -d '\r')"
    case "$cle" in
      SENTRY_DSN) [ -n "$valeur" ] && echo "$cle = (renseigné)" || echo "$cle = (vide)" ;;
      *) echo "$cle = ${valeur:-(absent)}" ;;
    esac
  done
  for cle in SECRET_KEY DB_PASSWORD CAMPAY_APP_USERNAME CAMPAY_APP_PASSWORD SPACES_ACCESS_KEY_ID SPACES_SECRET_ACCESS_KEY EMAIL_HOST_PASSWORD LMT_API_KEY LMT_SECRET WHATSAPP_ACCESS_TOKEN GOOGLE_CLIENT_ID; do
    grep -qE "^$cle=.+" .env && echo "$cle : renseigné" || echo "$cle : ABSENT ou vide"
  done
else
  echo ".env introuvable"
fi

titre "Base de données et contenu"
docker compose exec -T backend python manage.py shell -c '
from django.db import connection
from django.apps import apps
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone
from datetime import timedelta

ex = MigrationExecutor(connection)
plan = ex.migration_plan(ex.loader.graph.leaf_nodes())
print("Migrations non appliquées :", len(plan))

def n(label):
    try:
        return apps.get_model(label).objects.count()
    except Exception as exc:
        return "ERREUR %s" % type(exc).__name__

for label in [
    "catalog.Country", "catalog.Cursus", "catalog.Subject", "catalog.Tag",
    "catalog.Lesson", "catalog.Cours", "catalog.Exercise", "catalog.Question", "catalog.RappelDeMethode",
    "quiz.CompetenceItem", "inedit.Blueprint", "inedit.EpreuveInedite", "inedit.QuestionInedite",
    "programme.Module", "programme.Savoir", "recherche.EntreeRecherche",
    "subscriptions.Plan", "payments.MobileMoneyAccount",
]:
    print("%-30s %s" % (label, n(label)))

print()
User = apps.get_model("users.User")
print("Comptes (total)              ", User.objects.count())
print("  dont staff                 ", User.objects.filter(is_staff=True).count())
print("  dont superusers            ", User.objects.filter(is_superuser=True).count())
print("  dont marqués test (seed)   ", User.objects.filter(email__contains="+edukora-test-").count())
print("  avec téléphone             ", User.objects.exclude(phone_number__isnull=True).count())
print("  inscrits depuis 7 jours    ", User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count())
for label in ["users.Profil", "subscriptions.Subscription", "subscriptions.InscriptionInedite",
              "payments.Transaction", "payments.ManualPayment", "quiz.QuizSession", "analytics.AnalyticsEvent"]:
    print("%-30s %s" % (label, n(label)))

Transaction = apps.get_model("payments.Transaction")
from django.db.models import Count
print("Transactions par statut      ", dict(Transaction.objects.values_list("status").annotate(c=Count("id")).order_by()))
print("Transactions provider        ", dict(Transaction.objects.values_list("provider").annotate(c=Count("id")).order_by()))
Plan = apps.get_model("subscriptions.Plan")
print("Plans actifs JUSQUA_EXAMEN   ", Plan.objects.filter(is_active=True, duration_mode="JUSQUA_EXAMEN").count())
' 2>&1 | grep -vE '^\([0-9.]+\) ' | tail -60

titre "Dossier ingest sur le serveur"
du -sh backend/ingest 2>/dev/null || echo "backend/ingest absent"
ls backend/ingest 2>/dev/null | head -10

titre "Sauvegardes"
docker compose logs --tail 5 backup 2>&1 | tail -6

titre "Fin (aucune modification effectuée)"
