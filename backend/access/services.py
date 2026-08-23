from django.utils import timezone

from subscriptions.models import DureeMode, InscriptionInedite, InscriptionRepetiteur, Subscription


def has_access(user, obj):
    """
    Vrai si l'utilisateur a un abonnement actif donnant droit à ce contenu (Lesson ou
    Cours, tous deux exposent un `.cursus` M2M). Si `obj.cursus` est vide (Cours "toutes
    séries"), la notion est commune à tout cursus : n'importe quel abonnement actif suffit.

    Une Lesson "vitrine" (voir Lesson.est_vitrine) court-circuite tout ça : accès libre
    pour n'importe qui, y compris un visiteur anonyme - jamais évalué contre Subscription
    en dessous, qui ne sait rien faire d'un utilisateur non authentifié.
    """
    if getattr(obj, "est_vitrine", False):
        return True
    if not user.is_authenticated:
        return False

    cursus_qs = obj.cursus.all()
    if not cursus_qs.exists():
        return Subscription.objects.filter(user=user, expires_at__gt=timezone.now()).exists()
    return Subscription.objects.filter(
        user=user, cursus__in=cursus_qs, expires_at__gt=timezone.now(),
    ).exists()


def has_access_inedite(user, obj):
    """
    Miroir de has_access, pour l'add-on Épreuves Inédites (voir
    subscriptions.models.InscriptionInedite). `obj.cursus` est un M2M comme Lesson.cursus
    (une épreuve inédite peut cibler plusieurs séries à la fois, ex. Maths BAC C/E) - pas
    de fallback "cursus vide" comme has_access (une EpreuveInedite a toujours ≥1 cursus,
    imposé par inedit.ingestion). Seule différence volontaire restante avec has_access :
    aucun court-circuit `est_vitrine` - décision produit "corrigé gaté comme le reste"
    (audit "Épreuves Inédites") : cette app n'a aucune notion de contenu vitrine,
    énoncé/tentative/corrigé sont gatés uniformément.
    """
    if not user.is_authenticated:
        return False
    return InscriptionInedite.objects.filter(
        user=user, cursus__in=obj.cursus.all(), expires_at__gt=timezone.now(),
    ).exists()


def has_access_jusqua_examen(user, cursus):
    """
    Vrai si l'utilisateur a un abonnement actif de palier Jusqu'à l'Examen sur ce
    cursus - distinct de has_access, qui accepte n'importe quel palier (y compris
    Mensuel) pour le contenu de base. Réservé aux fonctionnalités pensées comme
    argument de vente propre à ce palier (ex. classement des thèmes les plus fréquents
    aux examens, voir catalog.views.ThemesFrequentsView) - ne jamais l'utiliser pour
    gater l'accès au contenu de base, qui reste has_access.
    """
    if not user.is_authenticated:
        return False
    return Subscription.objects.filter(
        user=user, cursus=cursus, expires_at__gt=timezone.now(), duration_mode=DureeMode.JUSQUA_EXAMEN,
    ).exists()


def has_access_fiches(user, cursus):
    """
    Vrai si l'utilisateur a un accès actif à l'add-on Fiches (répétiteur) pour ce cursus
    (voir subscriptions.models.InscriptionRepetiteur). `cursus` est directement une
    instance Cursus (pas un objet exposant `.cursus`, contrairement à has_access/
    has_access_inedite) : fiches.models.FicheGeneree cible toujours un seul cursus (une
    fiche est générée pour un cursus précis, jamais plusieurs séries à la fois), donc pas
    de M2M à traverser ici. Aucune notion de vitrine, même choix que has_access_inedite -
    l'outil de génération de fiches est entièrement gaté par cet add-on.
    """
    if not user.is_authenticated:
        return False
    return InscriptionRepetiteur.objects.filter(
        user=user, cursus=cursus, expires_at__gt=timezone.now(),
    ).exists()
