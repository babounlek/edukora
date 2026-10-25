"""
XP hors quiz et niveaux (voir quiz.xp) : lire et faire rapportent un peu, une seule fois par objet, avec un plafond par
jour - de quoi encourager sans qu'on puisse gonfler le compteur en cochant tout d'un coup.
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cours, Cursus, Examen, Lesson, LessonType, StatutContenu, Subject
from subscriptions.models import Subscription
from users.models import User

from . import xp
from .models import GainXP, SourceXP
from .tests import _make_question


class ActiviteFixture(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900777", password="x")
        self.profil = self.user.profils.first()
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )
        self.cours = Cours.objects.create(
            external_id="cours-xp", titre="Les limites", subject=self.subject, statut=StatutContenu.VALIDE,
        )
        self.cours.cursus.add(self.cursus)
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def comprendre(self, cle, compris=True):
        return self.client.put(
            "/access/etude/", {"cours": self.cours.slug, "cle": cle, "compris": compris}, format="json",
        )

    def exercice(self, numero):
        return _make_question(self.lesson, numero).exercise

    def faire(self, exercice, fait=True):
        return self.client.post(f"/access/exercices/{exercice.pk}/fait/", {"fait": fait}, format="json")


class ExerciceTests(ActiviteFixture):
    def test_un_exercice_declare_fait_rapporte_une_fois(self):
        exercice = self.exercice("1")

        reponse = self.faire(exercice)

        self.assertEqual(reponse.json()["xp_gagne"], xp.XP_EXERCICE)
        self.assertEqual(reponse.json()["xp_jour"]["xp"], xp.XP_EXERCICE)
        self.assertEqual(GainXP.objects.get().source, SourceXP.EXERCICE)

    def test_le_decocher_puis_le_recocher_ne_rapporte_rien_de_plus(self):
        exercice = self.exercice("1")
        self.faire(exercice)
        self.faire(exercice, fait=False)

        reponse = self.faire(exercice)

        self.assertEqual(reponse.json()["xp_gagne"], 0)
        self.assertEqual(GainXP.objects.count(), 1)

    def test_le_plafond_du_jour_borne_les_gains_hors_quiz(self):
        gagnes = [self.faire(self.exercice(str(n))).json()["xp_gagne"] for n in range(1, 6)]

        # 5 + 5 + 5 = plafond de 15 ; les suivants ne rapportent rien.
        self.assertEqual(gagnes, [5, 5, 5, 0, 0])
        self.assertEqual(xp.etat_du_jour(self.profil)["xp"], xp.PLAFOND_ACTIVITE_JOUR)

    def test_decocher_ne_rapporte_ni_ne_retire_rien(self):
        exercice = self.exercice("1")
        self.faire(exercice)

        reponse = self.faire(exercice, fait=False)

        self.assertEqual(reponse.json()["xp_gagne"], 0)
        self.assertEqual(xp.etat_du_jour(self.profil)["xp"], xp.XP_EXERCICE)


class CoursTests(ActiviteFixture):
    def test_une_section_comprise_rapporte_une_fois(self):
        premiere = self.comprendre("regle").json()
        self.comprendre("regle", compris=False)
        seconde = self.comprendre("regle").json()

        self.assertEqual(premiere["xp_gagne"], xp.XP_COURS_SECTION)
        self.assertNotIn("xp_gagne", seconde)
        self.assertEqual(GainXP.objects.filter(source=SourceXP.COURS).count(), 1)

    def test_deux_sections_rapportent_chacune(self):
        self.comprendre("regle")
        self.comprendre("exemple_resolu")

        self.assertEqual(xp.etat_du_jour(self.profil)["xp"], 2 * xp.XP_COURS_SECTION)

    def test_un_signet_ou_une_note_ne_rapportent_rien(self):
        self.client.put("/access/etude/", {"cours": self.cours.slug, "cle": "regle", "signet": True}, format="json")
        self.client.put("/access/etude/", {"cours": self.cours.slug, "cle": "regle", "note": "à revoir"}, format="json")

        self.assertFalse(GainXP.objects.exists())

    def test_une_section_d_epreuve_ne_rapporte_rien(self):
        self.client.put(
            "/access/etude/", {"lesson": self.lesson.slug, "cle": "exercice-1", "compris": True}, format="json",
        )

        self.assertFalse(GainXP.objects.exists())


class NiveauTests(ActiviteFixture):
    def test_un_profil_neuf_est_au_niveau_un(self):
        niveau = xp.niveau_du_profil(self.profil)

        self.assertEqual(niveau, {"rang": 1, "xp_total": 0, "seuil": 0, "seuil_suivant": 60})

    def test_le_niveau_suit_l_xp_cumulee_et_ne_redescend_pas(self):
        jour = timezone.localdate()
        GainXP.objects.create(profil=self.profil, jour=jour, source=SourceXP.SEANCE, points=60)

        self.assertEqual(xp.niveau_du_profil(self.profil)["rang"], 2)
        GainXP.objects.create(profil=self.profil, jour=jour, source=SourceXP.SEANCE, points=140)
        niveau = xp.niveau_du_profil(self.profil)
        self.assertEqual((niveau["rang"], niveau["xp_total"], niveau["seuil_suivant"]), (3, 200, 500))

    def test_au_sommet_il_n_y_a_pas_de_seuil_suivant(self):
        GainXP.objects.create(profil=self.profil, jour=timezone.localdate(), source=SourceXP.SEANCE, points=1000)

        niveau = xp.niveau_du_profil(self.profil)

        self.assertEqual(niveau["rang"], len(xp.NIVEAUX))
        self.assertIsNone(niveau["seuil_suivant"])

    def test_l_etat_du_jour_porte_le_niveau(self):
        self.assertEqual(xp.etat_du_jour(self.profil)["niveau"]["rang"], 1)
