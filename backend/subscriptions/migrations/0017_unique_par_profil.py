"""
Élargit la contrainte d'unicité de `Subscription`/`InscriptionInedite`/
`InscriptionRepetiteur` de (user, cursus) à (user, cursus, profil) - le grain
"resserré une fois l'achat pour un profil précis branché de bout en bout" annoncé
dans 0016_profil_additif. Pure contrainte, sans backfill : `profil` est déjà NOT
NULL sur les trois modèles depuis 0016, aucune ligne existante n'est concernée -
un compte à un seul profil (tous les comptes existants) n'en distingue aucun effet,
la contrainte élargie autorise seulement ce qui était jusqu'ici impossible : un
second abonnement sur le même cursus pour un second enfant du même compte.

Regroupe aussi deux `AlterField` sur `Plan.inclut_inedit`/`product_type` (aide en
ligne actualisée, retrait d'ADDON_INEDIT) restées en attente depuis le retrait de
l'achat séparé de l'add-on Épreuves Inédites (2026-09-30, voir ProductType) -
Django les détecte dans la même passe, pas de raison de les séparer.
"""

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0058_seed_exam_sessions_2026_date_fin'),
        ('subscriptions', '0016_profil_additif'),
        ('users', '0012_backfill_profil_depuis_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='inscriptioninedite',
            name='unique_inscription_inedite_per_cursus',
        ),
        migrations.RemoveConstraint(
            model_name='inscriptionrepetiteur',
            name='unique_inscription_repetiteur_per_cursus',
        ),
        migrations.RemoveConstraint(
            model_name='subscription',
            name='unique_subscription_per_cursus',
        ),
        migrations.AlterField(
            model_name='plan',
            name='inclut_inedit',
            field=models.BooleanField(default=False, help_text="Un Plan ABONNEMENT qui coche ceci active aussi l'add-on Épreuves Inédites (InscriptionInedite) en plus de l'abonnement, pour la même durée. Décision produit du 2026-08-09 (formule Max) puis du 2026-09-30 (seule voie restante : l'achat séparé de l'add-on, ProductType.ADDON_INEDIT, a été retiré) - Jusqu'à l'Examen coche systématiquement ce champ. N'a de sens que pour product_type=ABONNEMENT."),
        ),
        migrations.AlterField(
            model_name='plan',
            name='product_type',
            field=models.CharField(choices=[('ABONNEMENT', 'Abonnement cursus'), ('ADDON_REPETITEUR', 'Add-on Fiches Répétiteur')], default='ABONNEMENT', max_length=20),
        ),
        migrations.AddConstraint(
            model_name='inscriptioninedite',
            constraint=models.UniqueConstraint(fields=('user', 'cursus', 'profil'), name='unique_inscription_inedite_per_cursus_profil'),
        ),
        migrations.AddConstraint(
            model_name='inscriptionrepetiteur',
            constraint=models.UniqueConstraint(fields=('user', 'cursus', 'profil'), name='unique_inscription_repetiteur_per_cursus_profil'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'cursus', 'profil'), name='unique_subscription_per_cursus_profil'),
        ),
    ]
