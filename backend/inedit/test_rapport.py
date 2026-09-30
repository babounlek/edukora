"""Rapport de fin d'épreuve : pertes par cause, temps par exercice, comparaison, liens de révision."""

from datetime import datetime, timedelta, timezone as fuseau
from decimal import Decimal

from django.test import SimpleTestCase
from django.utils import timezone

from . import rapport
from .models import TentativeInedite
from .test_notation import NotationAPITestCase

D = Decimal
DEBUT = datetime(2026, 9, 28, 9, 0, tzinfo=fuseau.utc)


def ligne(exercice, points, obtenus, *, traitee=True, cause="", minutes=None):
    return {
        "exercice": exercice, "points": D(str(points)), "obtenus": D(str(obtenus)), "traitee": traitee,
        "cause": cause, "quand": DEBUT + timedelta(minutes=minutes) if minutes is not None else None,
    }


class PertesParCauseTests(SimpleTestCase):
    def test_regroupe_les_points_perdus_par_cause_du_plus_lourd_au_plus_leger(self):
        resultat = rapport.pertes_par_cause([
            ligne("1", 4, 1, cause="CALCUL"),
            ligne("1", 2, 0, traitee=False),
            ligne("2", 3, 3),
            ligne("2", 2, 1, cause="METHODE"),
            ligne("2", 1, 0, cause="CALCUL"),
        ])

        self.assertEqual(resultat["total_perdu"], 7.0)
        self.assertEqual(
            [(c["cause"], c["points"]) for c in resultat["causes"]],
            [("CALCUL", 4.0), ("NON_TRAITEE", 2.0), ("METHODE", 1.0)],
        )

    def test_une_question_traitee_sans_cause_est_non_precisee(self):
        resultat = rapport.pertes_par_cause([ligne("1", 2, 1)])
        self.assertEqual(resultat["causes"][0]["cause"], "NON_PRECISEE")

    def test_le_manque_de_temps_prime_sur_non_traitee_quand_l_eleve_le_declare(self):
        resultat = rapport.pertes_par_cause([ligne("1", 2, 0, traitee=False, cause="TEMPS")])
        self.assertEqual(resultat["causes"][0]["cause"], "TEMPS")

    def test_rien_de_perdu(self):
        self.assertEqual(rapport.pertes_par_cause([ligne("1", 2, 2)]), {"total_perdu": 0.0, "causes": []})


class TempsParExerciceTests(SimpleTestCase):
    def test_attribue_chaque_intervalle_a_l_exercice_de_la_case_cochee(self):
        lignes = [
            ligne("1", 4, 4, minutes=10), ligne("1", 4, 4, minutes=20),
            ligne("2", 12, 6, minutes=60),  # 40 minutes pour l'exercice 2
        ]

        temps = rapport.temps_par_exercice(lignes, DEBUT)

        self.assertEqual([t["secondes"] for t in temps], [20 * 60, 40 * 60])
        self.assertEqual([t["part_du_temps"] for t in temps], [33, 67])
        self.assertEqual([t["part_des_points"] for t in temps], [40, 60])

    def test_rien_sans_chrono_ni_assez_de_cases_cochees(self):
        lignes = [ligne("1", 4, 4, minutes=10), ligne("1", 4, 4, minutes=20), ligne("2", 4, 4, minutes=30)]
        self.assertIsNone(rapport.temps_par_exercice(lignes, None))
        self.assertIsNone(rapport.temps_par_exercice(lignes[:2], DEBUT))

    def test_l_exercice_chronophage_est_celui_qui_coute_plus_de_temps_que_de_points(self):
        temps = [
            {"numero_exercice": "1", "secondes": 600, "part_du_temps": 15, "part_des_points": 40},
            {"numero_exercice": "2", "secondes": 3400, "part_du_temps": 85, "part_des_points": 60},
        ]
        self.assertEqual(rapport.exercice_chronophage(temps), "2")

    def test_pas_de_chronophage_quand_temps_et_points_s_equilibrent(self):
        temps = [
            {"numero_exercice": "1", "secondes": 1, "part_du_temps": 45, "part_des_points": 50},
            {"numero_exercice": "2", "secondes": 1, "part_du_temps": 55, "part_des_points": 50},
        ]
        self.assertIsNone(rapport.exercice_chronophage(temps))
        self.assertIsNone(rapport.exercice_chronophage(None))


class SituerTests(SimpleTestCase):
    def test_rien_sous_l_effectif_minimal(self):
        self.assertIsNone(rapport.situer(D("12"), [10] * 19))

    def test_percentile_et_moyenne(self):
        autres = list(range(1, 21))  # 1 à 20
        situation = rapport.situer(D("15.5"), autres)

        self.assertEqual(situation["effectif"], 21)
        self.assertEqual(situation["percentile"], 75)
        self.assertEqual(situation["moyenne"], 10.5)

    def test_les_egalites_comptent_pour_moitie(self):
        self.assertEqual(rapport.situer(D("10"), [10] * 20)["percentile"], 50)


class CausePerteAPITests(NotationAPITestCase):
    def setUp(self):
        super().setUp()
        self.ouverte.criteres_notation = []
        self.ouverte.save(update_fields=["criteres_notation"])

    def donner_la_cause(self, cause, question=None):
        return self.client.post(self.url("noter", question or self.ouverte), {"cause_perte": cause}, format="json")

    def test_la_cause_se_donne_apres_le_corrige_et_revient_dans_la_question(self):
        self.client.post(self.url("noter", self.ouverte), {"points_obtenus": 1}, format="json")

        reponse = self.donner_la_cause("CALCUL")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["reponse"]["cause_perte"], "CALCUL")

    def test_la_cause_d_une_question_non_traitee_ne_la_rend_pas_traitee(self):
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})
        reponse = self.donner_la_cause("TEMPS")

        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(reponse.data["traitee"])
        resultat = self.client.post(self.url("completer")).data
        self.assertEqual(resultat["pertes"]["causes"][0]["cause"], "TEMPS")

    def test_cause_invalide_refusee_et_cause_vide_l_efface(self):
        self.client.post(self.url("noter", self.ouverte), {"points_obtenus": 1}, format="json")
        self.assertEqual(self.donner_la_cause("N_IMPORTE_QUOI").status_code, 400)
        self.donner_la_cause("METHODE")
        self.assertEqual(self.donner_la_cause("").data["reponse"]["cause_perte"], "")

    def test_la_cause_est_refusee_tant_que_le_corrige_est_masque(self):
        self.client.post(self.url("mode-examen"), {}, format="json")
        self.assertEqual(self.donner_la_cause("CALCUL").status_code, 403)

    def test_une_qcm_n_a_pas_de_cause_de_perte(self):
        self.assertEqual(self.donner_la_cause("CALCUL", self.qcm).status_code, 400)


class RapportDansLeResultatTests(NotationAPITestCase):
    def test_le_resultat_porte_les_pertes_les_liens_et_les_ids(self):
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})
        resultat = self.client.post(self.url("completer")).data

        self.assertEqual(resultat["pertes"]["causes"][0]["cause"], "NON_TRAITEE")
        self.assertEqual(resultat["cursus_id"], self.cursus.pk)
        self.assertIsNone(resultat["comparaison"])
        self.assertIsNone(resultat["temps_par_exercice"])  # entraînement libre : pas de chrono
        self.assertIn("theme_id", resultat["par_theme"][0])
        self.assertIn("theme_id", resultat["themes_a_reviser"][0])

    def test_le_temps_par_exercice_n_existe_qu_apres_avoir_coche_assez_de_questions_sous_chrono(self):
        self.client.post(self.url("mode-examen"), {}, format="json")
        resultat = self.client.post(self.url("completer")).data
        self.assertIsNone(resultat["temps_par_exercice"])

    def test_comparaison_avec_les_autres_candidats_de_la_meme_epreuve(self):
        from users.models import User

        for i in range(20):
            autre = User.objects.create_user(phone_number=f"6775500{i:02d}", password="x")
            TentativeInedite.objects.create(
                profil=autre.profils.first(), epreuve=self.epreuve, exam_mode_started_at=timezone.now(),
                submitted_at=timezone.now(), note_obtenue=D(str(i % 8)), bareme_snapshot=D("8"),
            )
        self.client.post(self.url("mode-examen"), {}, format="json")
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})

        resultat = self.client.post(self.url("completer")).data

        self.assertEqual(resultat["comparaison"]["effectif"], 21)
        self.assertIsNotNone(resultat["comparaison"]["percentile"])

    def test_pas_de_comparaison_pour_un_entrainement_libre(self):
        from users.models import User

        for i in range(20):
            autre = User.objects.create_user(phone_number=f"6775600{i:02d}", password="x")
            TentativeInedite.objects.create(
                profil=autre.profils.first(), epreuve=self.epreuve, exam_mode_started_at=timezone.now(),
                submitted_at=timezone.now(), note_obtenue=D("4"), bareme_snapshot=D("8"),
            )
        self.assertIsNone(self.client.post(self.url("completer")).data["comparaison"])
