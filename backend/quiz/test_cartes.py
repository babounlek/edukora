"""Cartes de révision (R18) : lecture des cartes dans le cours, revue à la répétition espacée, cartes dues."""
from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cours, Country, StatutContenu, Subject
from users.models import User

from . import cartes
from .models import CarteRevue

SECTIONS = [
    {"type": "accroche", "contenu_markdown": "Accroche."},
    {"type": "regle", "titre": "Dérivée d'un produit", "formule_principale": "(uv)' = u'v + uv'", "contenu_markdown": "On dérive chaque facteur."},
    {"type": "erreurs_classiques", "items": [
        {"erreur_markdown": "Écrire (uv)' = u'v'", "pourquoi_faux": "Le produit ne se dérive pas facteur par facteur.", "correction_markdown": "Utiliser u'v + uv'."},
        "Une erreur en texte brut, sans verso.",
        {"erreur_markdown": "Oublier le signe", "pourquoi_faux": "", "correction_markdown": ""},
    ]},
]


def _cours(sections=SECTIONS, statut=StatutContenu.VALIDE, ext="c1"):
    sujet = Subject.objects.filter(code="MATHS", country__code="CM").first() or Subject.objects.first()
    return Cours.objects.create(external_id=ext, titre=f"Cours {ext}", subject=sujet, sections_raw=sections, statut=statut)


class CartesDuCoursTests(TestCase):
    def test_la_regle_puis_les_erreurs_exploitables(self):
        liste = cartes.cartes_du_cours(_cours())
        self.assertEqual([c["cle"] for c in liste], ["regle", "erreur-0"])
        self.assertEqual(liste[0]["recto"], "Dérivée d'un produit")
        self.assertIn("u'v + uv'", liste[0]["verso"])
        self.assertIn("On dérive chaque facteur.", liste[0]["verso"])
        self.assertIn("Le produit ne se dérive pas", liste[1]["verso"])
        self.assertIn("**→** Utiliser u'v + uv'.", liste[1]["verso"])

    def test_un_cours_sans_regle_ni_erreur_n_a_pas_de_carte(self):
        self.assertEqual(cartes.cartes_du_cours(_cours([{"type": "accroche", "contenu_markdown": "x"}], ext="c2")), [])


class RevueTests(TestCase):
    def setUp(self):
        self.cours = _cours()
        self.user = User.objects.create_user(phone_number="677400201", password="x")
        self.profil = self.user.profils.first()
        self.aujourdhui = timezone.localdate()

    def test_une_carte_sue_entre_a_j_plus_3(self):
        revue = cartes.noter(self.profil, self.cours, "regle", True)
        self.assertEqual((revue.palier, revue.due_at), (1, self.aujourdhui + timedelta(days=3)))

    def test_une_carte_ratee_revient_demain(self):
        revue = cartes.noter(self.profil, self.cours, "regle", False)
        self.assertEqual((revue.palier, revue.due_at), (0, self.aujourdhui + timedelta(days=1)))

    def test_une_carte_due_et_sue_monte_d_un_palier(self):
        CarteRevue.objects.create(profil=self.profil, cours=self.cours, cle="regle", palier=1, due_at=self.aujourdhui)
        revue = cartes.noter(self.profil, self.cours, "regle", True)
        self.assertEqual((revue.palier, revue.due_at), (2, self.aujourdhui + timedelta(days=7)))

    def test_une_revue_anticipee_ne_fait_pas_monter(self):
        demain = self.aujourdhui + timedelta(days=2)
        CarteRevue.objects.create(profil=self.profil, cours=self.cours, cle="regle", palier=1, due_at=demain)
        revue = cartes.noter(self.profil, self.cours, "regle", True)
        self.assertEqual((revue.palier, revue.due_at), (1, demain))

    def test_le_dernier_palier_ne_depasse_pas(self):
        CarteRevue.objects.create(profil=self.profil, cours=self.cours, cle="regle", palier=4, due_at=self.aujourdhui)
        self.assertEqual(cartes.noter(self.profil, self.cours, "regle", True).palier, 4)

    def test_une_cle_inconnue_n_enregistre_rien(self):
        self.assertIsNone(cartes.noter(self.profil, self.cours, "erreur-9", True))
        self.assertEqual(CarteRevue.objects.count(), 0)

    def test_les_cartes_dues_les_plus_en_retard_d_abord(self):
        CarteRevue.objects.create(profil=self.profil, cours=self.cours, cle="regle", due_at=self.aujourdhui)
        CarteRevue.objects.create(profil=self.profil, cours=self.cours, cle="erreur-0", due_at=self.aujourdhui - timedelta(days=2))
        CarteRevue.objects.create(profil=self.profil, cours=self.cours, cle="erreur-5", due_at=self.aujourdhui - timedelta(days=9))  # n'existe plus
        total, liste = cartes.cartes_dues(self.profil)
        self.assertEqual(total, 3)
        self.assertEqual([c["cle"] for c in liste], ["erreur-0", "regle"])
        self.assertEqual(liste[0]["cours"]["slug"], self.cours.slug)

    def test_une_carte_non_due_n_est_pas_proposee(self):
        CarteRevue.objects.create(profil=self.profil, cours=self.cours, cle="regle", due_at=self.aujourdhui + timedelta(days=1))
        self.assertEqual(cartes.cartes_dues(self.profil), (0, []))

    def test_chaque_profil_a_ses_revues(self):
        autre = User.objects.create_user(phone_number="677400202", password="x").profils.first()
        cartes.noter(autre, self.cours, "regle", False)
        self.assertEqual(cartes.cartes_avec_etat(self.profil, self.cours)[0]["etat"], "nouvelle")


class CartesAPITests(TestCase):
    def setUp(self):
        self.cours = _cours()
        self.user = User.objects.create_user(phone_number="677400203", password="x")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_lecture_puis_revue_puis_etat(self):
        r = self.client.get(f"/quiz/cartes/cours/{self.cours.slug}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([c["etat"] for c in r.json()["cartes"]], ["nouvelle", "nouvelle"])
        r = self.client.post(f"/quiz/cartes/cours/{self.cours.slug}/regle/", {"savais": True}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["palier"], 1)
        etats = {c["cle"]: c["etat"] for c in self.client.get(f"/quiz/cartes/cours/{self.cours.slug}/").json()["cartes"]}
        self.assertEqual(etats, {"regle": "planifiee", "erreur-0": "nouvelle"})

    def test_savais_doit_etre_un_booleen(self):
        r = self.client.post(f"/quiz/cartes/cours/{self.cours.slug}/regle/", {"savais": "oui"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_carte_ou_cours_inconnus(self):
        self.assertEqual(self.client.post(f"/quiz/cartes/cours/{self.cours.slug}/erreur-9/", {"savais": True}, format="json").status_code, 404)
        self.assertEqual(self.client.get("/quiz/cartes/cours/nexiste-pas/").status_code, 404)

    def test_un_cours_non_publie_est_introuvable(self):
        brouillon = _cours(statut=StatutContenu.BROUILLON, ext="c3")
        self.assertEqual(self.client.get(f"/quiz/cartes/cours/{brouillon.slug}/").status_code, 404)

    def test_dues(self):
        self.client.post(f"/quiz/cartes/cours/{self.cours.slug}/regle/", {"savais": False}, format="json")
        self.assertEqual(self.client.get("/quiz/cartes/dues/").json(), {"total": 0, "cartes": []})  # due demain
        with mock.patch("django.utils.timezone.localdate", return_value=timezone.localdate() + timedelta(days=1)):
            r = self.client.get("/quiz/cartes/dues/").json()
        self.assertEqual(r["total"], 1)
        self.assertEqual(r["cartes"][0]["cle"], "regle")

    def test_exige_une_connexion(self):
        self.assertIn(APIClient().get("/quiz/cartes/dues/").status_code, (401, 403))
