"""Le défi de la semaine (R17) : choix figé, rotation, participation, bande anonyme publiée le dimanche, badges."""
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Country, Cursus, Examen, StatutContenu, Subject
from users.models import User

from . import defi
from .models import Blueprint, DefiSemaine, EpreuveInedite, TentativeInedite

LUNDI = date(2026, 11, 9)  # un lundi
DIMANCHE = LUNDI + timedelta(days=6)


def _mini(cursus, titre):
    sujet = Subject.objects.filter(code="MATHS").first() or Subject.objects.first()
    blueprint = Blueprint.objects.create(
        external_id=f"bp-{titre}", subject=sujet, titre=titre, sections_plan=[], duree_minutes=30, statut=StatutContenu.VALIDE,
    )
    blueprint.cursus.set([cursus])
    epreuve = EpreuveInedite.objects.create(
        blueprint=blueprint, external_id=f"ep-{titre}", subject=sujet, titre=titre, statut=StatutContenu.VALIDE,
        est_mini=True, published_at=timezone.now(),
    )
    epreuve.cursus.set([cursus])
    return epreuve


def _rendre(profil, epreuve, jour, note, chrono=True):
    """Une copie rendue ce jour-là (midi, heure locale), notée `note`."""
    midi = timezone.make_aware(datetime.combine(jour, datetime.min.time().replace(hour=12)))
    tentative = TentativeInedite.objects.create(profil=profil, epreuve=epreuve)
    TentativeInedite.objects.filter(pk=tentative.pk).update(
        submitted_at=midi, note_obtenue=Decimal(str(note)), exam_mode_started_at=midi - timedelta(minutes=30) if chrono else None,
    )
    return tentative


class DefiBase(TestCase):
    def setUp(self):
        country = Country.objects.get(code="CM")
        self.cursus = Cursus.objects.get(country=country, examen=Examen.BAC, series__code="C")
        self.m1 = _mini(self.cursus, "M1")
        self.m2 = _mini(self.cursus, "M2")
        self.user = User.objects.create_user(phone_number="677400101", password="x")
        self.profil = self.user.profils.first()

    _suivant = 0

    def _eleves(self, n):
        profils = []
        for _ in range(n):
            DefiBase._suivant += 1
            profils.append(User.objects.create_user(phone_number=f"6775{DefiBase._suivant:05d}", password="x").profils.first())
        return profils


class ChoixTests(DefiBase):
    def test_le_choix_est_fige_pour_la_semaine(self):
        premier = defi.defi_de_la_semaine(self.cursus, LUNDI)
        _mini(self.cursus, "M0")  # une mini ajoutée en cours de semaine ne change rien
        self.assertEqual(defi.defi_de_la_semaine(self.cursus, DIMANCHE).pk, premier.pk)
        self.assertEqual(DefiSemaine.objects.count(), 1)
        self.assertEqual(premier.debut, LUNDI)

    def test_on_fait_le_tour_avant_de_repeter(self):
        a = defi.defi_de_la_semaine(self.cursus, LUNDI).epreuve_id
        b = defi.defi_de_la_semaine(self.cursus, LUNDI + timedelta(days=7)).epreuve_id
        c = defi.defi_de_la_semaine(self.cursus, LUNDI + timedelta(days=14)).epreuve_id
        self.assertNotEqual(a, b)
        self.assertEqual(a, c)

    def test_sans_mini_publiee_pas_de_defi(self):
        EpreuveInedite.objects.update(statut=StatutContenu.BROUILLON)
        self.assertIsNone(defi.defi_de_la_semaine(self.cursus, LUNDI))
        self.assertIsNone(defi.etat_du_defi(self.profil, self.cursus, LUNDI))


class ParticipationTests(DefiBase):
    def test_releve_seulement_si_rendu_pendant_la_semaine(self):
        d = defi.defi_de_la_semaine(self.cursus, LUNDI)
        self.assertFalse(defi.etat_du_defi(self.profil, self.cursus, LUNDI)["releve"])
        _rendre(self.profil, d.epreuve, LUNDI - timedelta(days=1), 10)  # dimanche d'avant : hors semaine
        self.assertFalse(defi.etat_du_defi(self.profil, self.cursus, LUNDI)["releve"])
        _rendre(self.profil, d.epreuve, LUNDI + timedelta(days=2), 10)
        etat = defi.etat_du_defi(self.profil, self.cursus, LUNDI + timedelta(days=3))
        self.assertTrue(etat["releve"])
        self.assertEqual(etat["jours_restants"], 3)
        self.assertEqual(etat["titre"], d.epreuve.titre)

    def test_la_bande_n_est_publiee_que_le_dimanche(self):
        d = defi.defi_de_la_semaine(self.cursus, LUNDI)
        _rendre(self.profil, d.epreuve, LUNDI, 10)
        self.assertFalse(defi.etat_du_defi(self.profil, self.cursus, LUNDI + timedelta(days=5))["resultat_ouvert"])
        self.assertIsNone(defi.etat_du_defi(self.profil, self.cursus, LUNDI + timedelta(days=5))["bande"])
        etat = defi.etat_du_defi(self.profil, self.cursus, DIMANCHE)
        self.assertTrue(etat["resultat_ouvert"])
        self.assertEqual(etat["bande"], {"disponible": False, "bande": None})  # cohorte trop petite

    def test_la_semaine_derniere_n_apparait_que_si_l_eleve_y_a_pris_part(self):
        d = defi.defi_de_la_semaine(self.cursus, LUNDI)
        suivante = LUNDI + timedelta(days=7)
        self.assertIsNone(defi.etat_du_defi(self.profil, self.cursus, suivante)["precedent"])
        _rendre(self.profil, d.epreuve, LUNDI, 10)
        self.assertEqual(defi.etat_du_defi(self.profil, self.cursus, suivante)["precedent"]["titre"], d.epreuve.titre)


class BandeTests(DefiBase):
    def _cohorte(self, notes):
        d = defi.defi_de_la_semaine(self.cursus, LUNDI)
        for profil, note in zip(self._eleves(len(notes)), notes):
            _rendre(profil, d.epreuve, LUNDI + timedelta(days=1), note)
        return d

    def test_quart_superieur_et_moitie_superieure(self):
        d = self._cohorte(list(range(1, 31)))  # 30 participants : notes 1 à 30
        _rendre(self.profil, d.epreuve, LUNDI + timedelta(days=1), 29)
        self.assertEqual(defi.bande(self.profil, d)["bande"], "quart")
        autre = self._eleves(1)[0]
        _rendre(autre, d.epreuve, LUNDI + timedelta(days=1), 18)
        self.assertEqual(defi.bande(autre, d)["bande"], "moitie")

    def test_la_moitie_basse_se_tait(self):
        d = self._cohorte(list(range(5, 35)))
        _rendre(self.profil, d.epreuve, LUNDI + timedelta(days=1), 1)
        self.assertEqual(defi.bande(self.profil, d), {"disponible": True, "bande": None})

    def test_hors_chrono_ne_compte_pas_dans_la_bande(self):
        d = self._cohorte(list(range(1, 31)))
        _rendre(self.profil, d.epreuve, LUNDI + timedelta(days=1), 30, chrono=False)
        self.assertEqual(defi.bande(self.profil, d), {"disponible": True, "bande": None})
        self.assertTrue(defi.a_releve(self.profil, d))  # mais le défi est relevé

    def test_aucune_note_d_autrui_dans_la_reponse(self):
        d = self._cohorte(list(range(1, 31)))
        _rendre(self.profil, d.epreuve, DIMANCHE, 30)
        etat = defi.etat_du_defi(self.profil, self.cursus, DIMANCHE)
        self.assertEqual(set(etat["bande"]), {"disponible", "bande"})


class BadgesTests(DefiBase):
    def test_compte_les_semaines_relevees_une_seule_fois(self):
        self.assertEqual(defi.defis_releves(self.profil), 0)
        d1 = defi.defi_de_la_semaine(self.cursus, LUNDI)
        _rendre(self.profil, d1.epreuve, LUNDI, 10)
        _rendre(self.profil, d1.epreuve, LUNDI + timedelta(days=1), 12)  # deux copies, un seul défi
        self.assertEqual(defi.defis_releves(self.profil), 1)
        d2 = defi.defi_de_la_semaine(self.cursus, LUNDI + timedelta(days=7))
        _rendre(self.profil, d2.epreuve, LUNDI + timedelta(days=8), 10)
        self.assertEqual(defi.defis_releves(self.profil), 2)

    def test_une_copie_rendue_hors_semaine_ne_compte_pas(self):
        d = defi.defi_de_la_semaine(self.cursus, LUNDI)
        _rendre(self.profil, d.epreuve, LUNDI + timedelta(days=9), 10)
        self.assertEqual(defi.defis_releves(self.profil), 0)

    def test_les_jalons_de_reussites_les_portent(self):
        from quiz.reussites import reussites_du_profil

        d = defi.defi_de_la_semaine(self.cursus, LUNDI)
        _rendre(self.profil, d.epreuve, LUNDI, 10)
        jalons = {j["code"]: j for j in reussites_du_profil(self.profil)["jalons"]}
        self.assertTrue(jalons["premier_defi"]["obtenu"])
        self.assertFalse(jalons["defis_4"]["obtenu"])
        self.assertEqual(jalons["defis_4"]["valeur"], 1)


class DefiAPITests(DefiBase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_renvoie_le_defi_du_cursus(self):
        with mock.patch("django.utils.timezone.localdate", return_value=LUNDI):
            reponse = self.client.get("/inedit/defi-semaine/", {"cursus": self.cursus.pk})
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json()["defi"]["debut"], LUNDI.isoformat())
        self.assertFalse(reponse.json()["defi"]["releve"])

    def test_cursus_inconnu_ou_absent(self):
        self.assertEqual(self.client.get("/inedit/defi-semaine/", {"cursus": 999999}).status_code, 404)
        self.assertEqual(self.client.get("/inedit/defi-semaine/").status_code, 404)

    def test_exige_une_connexion(self):
        self.assertIn(APIClient().get("/inedit/defi-semaine/", {"cursus": self.cursus.pk}).status_code, (401, 403))
