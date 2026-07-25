from django.utils import timezone

from subscriptions.models import Subscription


def has_access(user, obj):
    """
    Vrai si l'utilisateur a un abonnement actif donnant droit à ce contenu (Lesson ou
    Cours, tous deux exposent un `.cursus` M2M). Si `obj.cursus` est vide (Cours "toutes
    séries"), la notion est commune à tout cursus : n'importe quel abonnement actif suffit.
    """
    cursus_qs = obj.cursus.all()
    if not cursus_qs.exists():
        return Subscription.objects.filter(user=user, expires_at__gt=timezone.now()).exists()
    return Subscription.objects.filter(
        user=user, cursus__in=cursus_qs, expires_at__gt=timezone.now(),
    ).exists()
