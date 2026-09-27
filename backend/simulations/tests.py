"""Simulation d'épreuve officielle : durée, barème, chrono, notation, rapport, accès."""

from datetime import timedelta
from decimal import Decimal

from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Exercise, Lesson, LessonType, Question, StatutContenu, Subject, Tag
from quiz.models import RevisionSchedule
from subscriptions.models import Subscription
from users.models import User

from .cadre import charger_exercices, duree_minutes
from .models import SimulationEpreuve


class DureeMinutesTests(SimpleTestCase):
    def test_formats_courants_des_en_tetes(self):
        for texte, attendu in [
            ("3h", 180), ("2H", 120), ("1h30", 90), ("2 heures", 120), ("1 heure", 60),
            ("45 mn", 45), ("30 min", 30), ("3h (estimation)", 180), ("2h 15", 135),
        ]:
            self.assertEqual(duree_minutes(texte), attendu, texte)

    def test_illisible_ou_absent(self):
        for texte in ("", None, "variable", "toute la journée"):
            self.assertIsNone(duree_minutes(texte), texte)


class SimulationTestCase(TestCase):
    """Épreuve officielle de 2 h : exercice 1 (6 pts, deux thèmes), exercice 2 (14 pts)."""

    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.theme_a = Tag.objects.create(name="Suites")
        self.theme_b = Tag.objects.create(name="Probabilités")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2019", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, duree_epreuve="2h",
        )
        self.lesson.cursus.add(self.cursus)
        self.ex1 = self.exercice("1", "6", "Énoncé 1", "Corrigé 1", [self.theme_a])
        self.ex2 = self.exercice("2", "14", "Énoncé 2", "Corrigé 2", [self.theme_b])

        self.user = User.objects.create_user(phone_number="677800001", password="x")
        Subscription.objects.create(user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30))
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def exercice(self, numero, points, enonce, corrige, themes):
        exercice = Exercise.objects.create(
            lesson=self.lesson, numero_exercice=numero, points=points, statut=StatutContenu.VALIDE,
            enonce_markdown=enonce, corrige_markdown=corrige,
        )
        question = Question.objects.create(
            exercise=exercice, numero="1", ordre=1, enonce_markdown=enonce, corrige_markdown=corrige,
        )
        question.themes.set(themes)
        return exercice

    def demarrer(self, **extra):
        reponse = self.client.post("/simulations/", {"epreuve": self.lesson.pk, **extra}, format="json")
        self.assertEqual(reponse.status_code, 201, reponse.data)
        self.simulation = SimulationEpreuve.objects.get(pk=reponse.data["id"])
        return reponse.data

    def url(self, action="", exercice=None):
        base = f"/simulations/{self.simulation.pk}/"
        return base + (f"exercices/{exercice.pk}/{action}/" if exercice else (f"{action}/" if action else ""))


class DemarrageTests(SimulationTestCase):
    def test_le_payload_a_la_forme_d_une_tentative_avec_un_exercice_par_bloc(self):
        data = self.demarrer()

        self.assertEqual(data["source"], "officielle")
        self.assertEqual(data["granularite"], "exercice")
        self.assertEqual(data["duree_minutes"], 120)
        self.assertEqual(data["bareme"], 20.0)
        self.assertFalse(data["bareme_estime"])
        self.assertEqual([e["numero_exercice"] for e in data["exercices"]], ["1", "2"])
        bloc = data["exercices"][0]["questions"][0]
        self.assertEqual((bloc["id"], bloc["points"], bloc["type_reponse"]), (self.ex1.pk, 6.0, "OUVERTE"))
        self.assertEqual(bloc["enonce_markdown"], "Énoncé 1")

    def test_refuse_sans_abonnement_au_cursus(self):
        Subscription.objects.all().delete()
        reponse = self.client.post("/simulations/", {"epreuve": self.lesson.pk}, format="json")
        self.assertEqual(reponse.status_code, 403)

    def test_une_epreuve_vitrine_se_simule_sans_abonnement(self):
        Subscription.objects.all().delete()
        Lesson.objects.filter(pk=self.lesson.pk).update(est_vitrine=True)
        self.assertEqual(self.client.post("/simulations/", {"epreuve": self.lesson.pk}, format="json").status_code, 201)

    def test_refuse_un_brouillon_ou_un_contenu_qui_n_est_pas_une_annale(self):
        Lesson.objects.filter(pk=self.lesson.pk).update(lesson_type=LessonType.FICHE)
        self.assertEqual(self.client.post("/simulations/", {"epreuve": self.lesson.pk}, format="json").status_code, 404)

    def test_refuse_une_epreuve_sans_exercices(self):
        Exercise.objects.filter(lesson=self.lesson).delete()
        self.assertEqual(self.client.post("/simulations/", {"epreuve": self.lesson.pk}, format="json").status_code, 400)

    def test_la_simulation_d_un_autre_eleve_est_introuvable(self):
        self.demarrer()
        autre = User.objects.create_user(phone_number="677800002", password="x")
        self.client.force_authenticate(user=autre)
        self.assertEqual(self.client.get(self.url()).status_code, 404)


class BaremeTests(SimulationTestCase):
    def test_un_exercice_sans_points_lisibles_rend_le_bareme_estime_pour_toute_l_epreuve(self):
        Exercise.objects.filter(pk=self.ex2.pk).update(points="")
        data = self.demarrer()

        self.assertTrue(data["bareme_estime"])
        # Tous les exercices pèsent autant : jamais une note sur un total tronqué à 6 points.
        self.assertEqual([e["questions"][0]["points"] for e in data["exercices"]], [1.0, 1.0])

    def test_les_points_illisibles_sont_ignores_par_charger_exercices(self):
        Exercise.objects.filter(pk=self.ex1.pk).update(points="beaucoup")
        self.assertEqual([e.points for e in charger_exercices(self.lesson)], ["", ""])


class ChronoEtCorrigeTests(SimulationTestCase):
    def test_le_mode_examen_masque_le_corrige_et_la_note(self):
        self.demarrer()
        self.client.post(self.url("mode-examen"), {}, format="json")

        data = self.client.get(self.url()).data

        self.assertFalse(data["correction_disponible"])
        self.assertIsNone(data["notation"])
        self.assertNotIn("corrige_markdown", data["exercices"][0]["questions"][0])

    def test_le_libre_donne_le_corrige_des_le_debut(self):
        data = self.demarrer()
        self.assertTrue(data["correction_disponible"])
        self.assertEqual(data["exercices"][0]["questions"][0]["corrige_markdown"], "Corrigé 1")

    def test_pas_de_chrono_sans_duree_lisible(self):
        Lesson.objects.filter(pk=self.lesson.pk).update(duree_epreuve="")
        self.demarrer()
        self.assertEqual(self.client.post(self.url("mode-examen"), {}, format="json").status_code, 400)

    def test_le_mode_papier_exige_un_pdf(self):
        self.demarrer()
        self.assertEqual(self.client.post(self.url("mode-examen"), {"papier": True}, format="json").status_code, 400)

    def test_le_chrono_ne_se_lance_plus_apres_une_premiere_reponse(self):
        self.demarrer()
        self.client.post(self.url("noter", self.ex1), {"traitee": True}, format="json")
        self.assertEqual(self.client.post(self.url("mode-examen"), {}, format="json").status_code, 409)

    def test_le_temps_ecoule_rend_la_copie_toute_seule(self):
        self.demarrer()
        self.client.post(self.url("mode-examen"), {}, format="json")
        SimulationEpreuve.objects.filter(pk=self.simulation.pk).update(
            exam_mode_started_at=timezone.now() - timedelta(minutes=121),
        )

        data = self.client.get(self.url()).data

        self.assertIsNotNone(data["submitted_at"])
        self.assertTrue(data["correction_disponible"])


class DureeEstimeeTests(SimulationTestCase):
    """Une annale qui n'annonce pas sa propre durée peut en hériter d'une autre session de la même
    (matière, examen, série, nature d'épreuve, partie) - jamais aveuglément, voir
    cadre.duree_minutes_pour_lesson."""

    def setUp(self):
        super().setUp()
        # self.lesson porte déjà "2h" (voir SimulationTestCase) : effacée pour tester l'inférence.
        Lesson.objects.filter(pk=self.lesson.pk).update(duree_epreuve="")
        self.lesson.refresh_from_db()

    def soeur(self, duree, year, *, cursus=None, nature="", partie=""):
        soeur = Lesson.objects.create(
            title=f"Maths BAC C {year}", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, duree_epreuve=duree, year=year,
            nature_epreuve=nature, partie_epreuve_francais=partie,
        )
        soeur.cursus.add(cursus or self.cursus)
        return soeur

    def test_une_seule_soeur_connue_suffit(self):
        self.soeur("4h", 2020)

        data = self.demarrer()

        self.assertEqual(data["duree_minutes"], 240)
        self.assertTrue(data["duree_estimee"])

    def test_unanimite_sur_plusieurs_annees(self):
        for annee in (2018, 2020, 2022, 2024):
            self.soeur("4h", annee)

        data = self.demarrer()

        self.assertEqual(data["duree_minutes"], 240)
        self.assertTrue(data["duree_estimee"])

    def test_accord_de_deux_des_trois_dernieres_annees_suffit(self):
        self.soeur("4h", 2022)
        self.soeur("4h", 2023)
        self.soeur("3h", 2024)  # la plus récente, isolée - pas encore assez pour l'emporter

        data = self.demarrer()

        self.assertEqual(data["duree_minutes"], 240)
        self.assertTrue(data["duree_estimee"])

    def test_une_unique_session_recente_divergente_ne_l_emporte_pas(self):
        """Le cas réellement observé en base (Physique BAC C) : 4h pendant des années, "1h" sur
        la seule session la plus récente - presque toujours une faute de saisie de l'en-tête
        source, jamais un vrai changement à suivre aveuglément."""
        for annee in (2019, 2020, 2021, 2022, 2023):
            self.soeur("4h", annee)
        self.soeur("1h", 2026)

        data = self.demarrer()

        self.assertEqual(data["duree_minutes"], 240)
        self.assertTrue(data["duree_estimee"])

    def test_un_desaccord_reel_ne_devine_rien(self):
        self.soeur("4h", 2022)
        self.soeur("3h", 2023)
        self.soeur("2h", 2024)

        data = self.demarrer()

        self.assertIsNone(data["duree_minutes"])
        self.assertFalse(data["duree_estimee"])
        self.assertEqual(self.client.post(self.url("mode-examen"), {}, format="json").status_code, 400)

    def test_une_autre_nature_d_epreuve_n_est_jamais_comptee(self):
        self.soeur("1h", 2024, nature="PRATIQUE")  # l'épreuve pratique ne dure pas comme la théorique
        self.soeur("4h", 2020)

        data = self.demarrer()

        self.assertEqual(data["duree_minutes"], 240)

    def test_deux_series_dont_l_historique_diverge_restent_sans_duree(self):
        autre_cursus = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        self.lesson.cursus.add(autre_cursus)
        self.soeur("4h", 2020, cursus=self.cursus)   # historique de la série C : 4h
        self.soeur("3h", 2020, cursus=autre_cursus)  # historique de la série D : 3h

        data = self.demarrer()

        self.assertIsNone(data["duree_minutes"])
        self.assertFalse(data["duree_estimee"])

    def test_sa_propre_duree_l_emporte_toujours_sur_l_inference(self):
        Lesson.objects.filter(pk=self.lesson.pk).update(duree_epreuve="3h")
        self.soeur("4h", 2020)

        data = self.demarrer()

        self.assertEqual(data["duree_minutes"], 180)
        self.assertFalse(data["duree_estimee"])


class NotationTests(SimulationTestCase):
    def noter(self, exercice, points):
        return self.client.post(self.url("noter", exercice), {"points_obtenus": points}, format="json")

    def test_la_note_est_sur_le_bareme_de_l_epreuve_et_non_traite_vaut_zero(self):
        self.demarrer()
        reponse = self.noter(self.ex1, 4.5)

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["notation"]["note"], 4.5)
        self.assertEqual(reponse.data["notation"]["bareme"], 20.0)
        self.assertTrue(reponse.data["traitee"])
        resultat = self.client.post(self.url("completer")).data
        self.assertEqual(resultat["note"], 4.5)
        self.assertEqual(resultat["note_sur_20"], 4.5)
        self.assertEqual(resultat["questions_non_traitees"], 1)
        self.assertEqual(resultat["mode"], "libre")

    def test_les_points_sont_bornes_par_le_bareme_de_l_exercice(self):
        self.demarrer()
        self.assertEqual(self.noter(self.ex1, 6.5).status_code, 400)
        self.assertEqual(self.noter(self.ex1, -1).status_code, 400)
        self.assertEqual(self.noter(self.ex1, "abc").status_code, 400)
        self.assertEqual(self.noter(self.ex1, "5,5").status_code, 200)

    def test_noter_est_refuse_tant_que_le_corrige_est_masque(self):
        self.demarrer()
        self.client.post(self.url("mode-examen"), {}, format="json")
        self.assertEqual(self.noter(self.ex1, 3).status_code, 403)
        self.assertEqual(
            self.client.post(self.url("noter", self.ex1), {"traitee": True}, format="json").status_code, 200,
        )

    def test_apres_la_soumission_on_note_et_la_note_stockee_suit(self):
        self.demarrer()
        self.client.post(self.url("mode-examen"), {}, format="json")
        self.client.post(self.url("noter", self.ex1), {"traitee": True}, format="json")
        resultat = self.client.post(self.url("completer")).data
        self.assertEqual(resultat["note"], 0.0)
        self.assertEqual(resultat["questions_a_noter"], 1)
        self.assertEqual(resultat["mode"], "examen")

        self.noter(self.ex1, 6)

        self.simulation.refresh_from_db()
        self.assertEqual(self.simulation.note_obtenue, Decimal("6.00"))
        self.assertEqual(self.simulation.score_obtenu, 30)

    def test_retirer_une_case_apres_la_soumission_est_refuse(self):
        self.demarrer()
        self.client.post(self.url("noter", self.ex1), {"traitee": True}, format="json")
        self.client.post(self.url("completer"))
        reponse = self.client.post(self.url("noter", self.ex1), {"traitee": False}, format="json")
        self.assertEqual(reponse.status_code, 409)

    def test_corps_vide_et_exercice_inconnu(self):
        self.demarrer()
        self.assertEqual(self.client.post(self.url("noter", self.ex1), {}, format="json").status_code, 400)
        autre = Exercise.objects.create(
            lesson=Lesson.objects.create(title="Autre", subject=self.subject, lesson_type=LessonType.CORR),
            numero_exercice="1", statut=StatutContenu.VALIDE,
        )
        self.assertEqual(self.client.post(self.url("noter", autre), {"traitee": True}, format="json").status_code, 404)


class RapportEtRevisionsTests(SimulationTestCase):
    def test_les_pertes_par_cause_et_les_liens_de_revision(self):
        self.demarrer()
        self.client.post(self.url("noter", self.ex1), {"points_obtenus": 3}, format="json")
        self.client.post(self.url("noter", self.ex1), {"cause_perte": "CALCUL"}, format="json")

        resultat = self.client.post(self.url("completer")).data

        causes = {c["cause"]: c["points"] for c in resultat["pertes"]["causes"]}
        self.assertEqual(causes, {"NON_TRAITEE": 14.0, "CALCUL": 3.0})
        self.assertEqual(resultat["cursus_id"], self.cursus.pk)
        self.assertEqual({t["theme"] for t in resultat["themes_a_reviser"]}, {"Suites", "Probabilités"})
        self.assertTrue(all("theme_id" in t for t in resultat["themes_a_reviser"]))

    def test_un_exercice_laisse_de_cote_planifie_la_revision_de_ses_themes(self):
        self.demarrer()
        self.client.post(self.url("noter", self.ex1), {"points_obtenus": 6}, format="json")
        self.client.post(self.url("completer"))

        planifies = set(RevisionSchedule.objects.filter(user=self.user).values_list("theme__name", flat=True))
        self.assertEqual(planifies, {"Probabilités"})

    def test_rendre_deux_fois_ne_replanifie_pas(self):
        from unittest import mock

        self.demarrer()
        self.client.post(self.url("completer"))
        with mock.patch("simulations.views.enregistrer_resultat_pour_revision") as enregistrer:
            self.client.post(self.url("completer"))
        enregistrer.assert_not_called()

    def test_un_exercice_ne_fait_revenir_que_ses_themes_principaux(self):
        tags = [Tag.objects.create(name=f"Notion {i}") for i in range(6)]
        exercice = Exercise.objects.create(
            lesson=self.lesson, numero_exercice="3", points="0", statut=StatutContenu.VALIDE,
        )
        for i, tag in enumerate(tags):
            question = Question.objects.create(exercise=exercice, numero=str(i), ordre=i, enonce_markdown="q", corrige_markdown="c")
            question.themes.set([tag, tags[0]])  # tags[0] partout : le plus fréquent

        adaptes = {e.numero_exercice: e for e in charger_exercices(self.lesson)}
        themes = adaptes["3"].questions.all()[0].themes.all()

        self.assertEqual(len(themes), 3)
        self.assertEqual(themes[0].name, "Notion 0")

    def test_la_comparaison_apparait_avec_assez_de_candidats_en_conditions_reelles(self):
        for i in range(20):
            autre = User.objects.create_user(phone_number=f"6778100{i:02d}", password="x")
            SimulationEpreuve.objects.create(
                user=autre, lesson=self.lesson, exam_mode_started_at=timezone.now(),
                submitted_at=timezone.now(), note_obtenue=Decimal(str(i % 15)), bareme_snapshot=Decimal("20"),
            )
        self.demarrer()
        self.client.post(self.url("mode-examen"), {}, format="json")
        self.client.post(self.url("noter", self.ex1), {"traitee": True}, format="json")
        self.client.post(self.url("completer"))
        self.client.post(self.url("noter", self.ex1), {"points_obtenus": 6}, format="json")

        resultat = self.client.post(self.url("completer")).data

        self.assertEqual(resultat["comparaison"]["effectif"], 21)


class MesSimulationsTests(SimulationTestCase):
    def test_liste_les_simulations_de_l_eleve_seulement(self):
        self.demarrer()
        autre = User.objects.create_user(phone_number="677800003", password="x")
        SimulationEpreuve.objects.create(user=autre, lesson=self.lesson)

        data = self.client.get("/simulations/mes-simulations/").data

        self.assertEqual([s["id"] for s in data], [self.simulation.pk])


class MarquesTests(SimulationTestCase):
    def test_marquer_a_revoir_bascule(self):
        self.demarrer()
        premiere = self.client.post(self.url("marquer", self.ex1)).data
        self.assertEqual(premiere["questions_marquees"], [self.ex1.pk])
        seconde = self.client.post(self.url("marquer", self.ex1)).data
        self.assertEqual(seconde["questions_marquees"], [])
