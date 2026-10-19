from django.test import TestCase
from django.urls import reverse

from catalog.models import Cursus, Examen

from .models import DureeMode, Plan, ProductType

NOM = "GCE O Level - Jusqu'à l'Examen"


class PlanGceOLevelTests(TestCase):
    """Plan semé par la migration 0019 : un abonnement par niveau, désactivé tant qu'on ne le met pas en vente."""

    def setUp(self):
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        self.plan = Plan.objects.get(cursus=self.cursus, product_type=ProductType.ABONNEMENT)

    def test_plan_seme_selon_la_grille_unique(self):
        self.assertEqual(self.plan.name, NOM)
        self.assertEqual(self.plan.price, 15000)
        self.assertEqual(self.plan.duration_mode, DureeMode.JUSQUA_EXAMEN)
        self.assertTrue(self.plan.inclut_inedit)

    def test_seme_desactive_donc_absent_du_catalogue(self):
        self.assertFalse(self.plan.is_active)
        reponse = self.client.get(reverse("subscriptions:plan-list"))
        self.assertEqual(reponse.status_code, 200)
        self.assertNotIn(self.plan.id, [p["id"] for p in reponse.json()])

    def test_jusqua_examen_inclut_toujours_les_inedites_meme_si_on_decoche(self):
        Plan.objects.filter(pk=self.plan.pk).update(inclut_inedit=False)
        plan = Plan.objects.get(pk=self.plan.pk)
        plan.is_active = True
        plan.save(update_fields=["is_active"])
        plan.refresh_from_db()
        self.assertTrue(plan.inclut_inedit)

    def test_un_plan_par_niveau_et_aucun_pour_les_cursus_sans_contenu(self):
        """Un plan O Level et un plan A Level, tous deux sur le cursus général (sans série ni branche technique)."""
        gce = Plan.objects.filter(cursus__examen__in=[Examen.GCE_OL, Examen.GCE_AL])
        self.assertEqual(gce.count(), 2)
        self.assertEqual({p.cursus.examen for p in gce}, {Examen.GCE_OL, Examen.GCE_AL})
        self.assertTrue(all(p.cursus.series_id is None for p in gce))

    def test_active_il_apparait_avec_prix_et_duree_calcules(self):
        Plan.objects.filter(pk=self.plan.pk).update(is_active=True)
        reponse = self.client.get(reverse("subscriptions:plan-list"), {"cursus": self.cursus.id})
        (ligne,) = reponse.json()
        self.assertEqual(ligne["name"], NOM)
        self.assertEqual(ligne["effective_price"], 15000)
        # Durée jusqu'à la fin de la session GCE (estimée sur 2027 depuis le calendrier 2026), toujours positive.
        self.assertGreaterEqual(ligne["effective_duration_days"], 1)
        self.assertEqual(ligne["prix_enfant_supplementaire"], 12000)
        self.assertEqual(ligne["cursus"]["examen"], "GCE_OL")
        self.assertTrue(ligne["inclut_inedit"])


NOM_AL = "GCE A Level - Jusqu'à l'Examen"


class PlanGceALevelTests(TestCase):
    """Plan semé par la migration 0021 : même grille que l'O Level, désactivé tant qu'on ne le met pas en vente."""

    def setUp(self):
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.GCE_AL, series__isnull=True)
        self.plan = Plan.objects.get(cursus=self.cursus, product_type=ProductType.ABONNEMENT)

    def test_plan_seme_selon_la_grille_unique(self):
        self.assertEqual(self.plan.name, NOM_AL)
        self.assertEqual(self.plan.price, 15000)
        self.assertEqual(self.plan.duration_mode, DureeMode.JUSQUA_EXAMEN)
        self.assertTrue(self.plan.inclut_inedit)

    def test_seme_desactive_donc_absent_du_catalogue(self):
        self.assertFalse(self.plan.is_active)
        reponse = self.client.get(reverse("subscriptions:plan-list"))
        self.assertEqual(reponse.status_code, 200)
        self.assertNotIn(self.plan.id, [p["id"] for p in reponse.json()])

    def test_active_il_apparait_avec_prix_et_duree_calcules(self):
        Plan.objects.filter(pk=self.plan.pk).update(is_active=True)
        reponse = self.client.get(reverse("subscriptions:plan-list"), {"cursus": self.cursus.id})
        (ligne,) = reponse.json()
        self.assertEqual(ligne["name"], NOM_AL)
        self.assertEqual(ligne["effective_price"], 15000)
        self.assertGreaterEqual(ligne["effective_duration_days"], 1)
        self.assertEqual(ligne["cursus"]["examen"], "GCE_AL")
        self.assertTrue(ligne["inclut_inedit"])
