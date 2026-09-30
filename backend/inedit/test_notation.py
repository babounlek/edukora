"""Note sur barème d'une TentativeInedite (voir inedit.notation) et endpoint noter_question."""

from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Country, Cursus, Examen, Tag
from subscriptions.models import InscriptionInedite
from users.models import User

from . import notation
from .models import QuestionInedite, TentativeInedite, TentativeReponse
from .tests import _make_published_epreuve


class RepartitionPointsTests(TestCase):
    def test_partage_par_quarts_sans_reste(self):
        parts = notation._repartir(Decimal("4"), 3)
        self.assertEqual(parts, [Decimal("1.5"), Decimal("1.25"), Decimal("1.25")])
        self.assertEqual(sum(parts), Decimal("4"))

    def test_partage_au_centieme_quand_les_quarts_ne_suffisent_pas(self):
        parts = notation._repartir(Decimal("1"), 8)
        self.assertEqual(sum(parts), Decimal("1"))
        self.assertTrue(all(p > 0 for p in parts))

    def test_points_illisibles_ou_negatifs_valent_zero(self):
        self.assertEqual(notation.parse_points("2,5"), Decimal("2.5"))
        self.assertEqual(notation.parse_points(" 10 "), Decimal("10"))
        self.assertEqual(notation.parse_points("beaucoup"), Decimal("0"))
        self.assertEqual(notation.parse_points("-3"), Decimal("0"))
        self.assertEqual(notation.parse_points(""), Decimal("0"))


class NotationAPITestCase(TestCase):
    """Épreuve : un exercice de 8 points, une QCM (bonne réponse « b ») et une ouverte."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="Suites numériques")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.epreuve = _make_published_epreuve(self.country)
        self.user = User.objects.create_user(phone_number="677400090", password="x")
        self.profil = self.user.profils.first()
        InscriptionInedite.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tentative = TentativeInedite.objects.create(profil=self.profil, epreuve=self.epreuve)
        self.exercice = self.epreuve.exercices.get()
        self.qcm = self.exercice.questions.get(numero="1")
        self.ouverte = self.exercice.questions.get(numero="2")

    def url(self, action, question=None, tentative=None):
        tentative = tentative or self.tentative
        if question is None:
            return f"/inedit/tentatives/{tentative.id}/{action}/"
        return f"/inedit/tentatives/{tentative.id}/questions/{question.id}/{action}/"

    @property
    def detail_url(self):
        return f"/inedit/tentatives/{self.tentative.id}/"

    def donner_une_grille(self):
        self.ouverte.criteres_notation = [
            {"libelle": "Formule correcte", "points": 1},
            {"libelle": "Application numérique", "points": 1.5},
        ]
        self.ouverte.save(update_fields=["criteres_notation"])

    def ajouter_questions_ouvertes(self, nombre):
        for i in range(nombre):
            QuestionInedite.objects.create(
                exercice=self.exercice, numero=str(10 + i), ordre=10 + i,
                enonce_markdown="Q ?", corrige_markdown="Corrigé.",
            )

    def passer_en_mode_examen(self):
        self.client.post(self.url("mode-examen"))
        self.tentative.refresh_from_db()


class BaremeEtScoreTests(NotationAPITestCase):
    def test_le_bareme_reparti_egalement_est_signale_comme_estime(self):
        data = self.client.get(self.detail_url).data  # /inedit/tentatives/<id>/
        self.assertEqual(data["bareme"], 8.0)
        self.assertTrue(data["bareme_estime"])
        points = [q["points"] for q in data["exercices"][0]["questions"]]
        self.assertEqual(points, [4.0, 4.0])
        self.assertTrue(all(q["bareme_estime"] for q in data["exercices"][0]["questions"]))

    def test_traiter_seulement_les_questions_faciles_ne_donne_plus_100_pour_cent(self):
        self.ajouter_questions_ouvertes(2)  # 4 questions x 2 points
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})

        data = self.client.post(self.url("completer")).data

        self.assertEqual(data["note"], 2.0)
        self.assertEqual(data["bareme"], 8.0)
        self.assertEqual(data["score"], 25)
        self.assertEqual(data["note_sur_20"], 5.0)
        self.assertEqual(data["questions_non_traitees"], 3)

    def test_une_tentative_vierge_vaut_zero_et_non_pas_aucune_note(self):
        data = self.client.post(self.url("completer")).data

        self.assertEqual(data["note"], 0.0)
        self.assertEqual(data["score"], 0)
        self.assertTrue(data["definitive"])
        self.tentative.refresh_from_db()
        self.assertEqual(self.tentative.note_obtenue, Decimal("0"))
        self.assertEqual(self.tentative.bareme_snapshot, Decimal("8"))

    def points_par_numero(self):
        data = self.client.get(self.detail_url).data
        return {q["numero"]: q for q in data["exercices"][0]["questions"]}

    def test_le_bareme_annonce_dans_l_enonce_l_emporte_sur_la_repartition_egale(self):
        # « (1,5 pt) » et « (6,5 points) » : ce que l'élève lit sur son sujet (total 8).
        self.qcm.enonce_markdown = "QCM ? (1,5 pt)"
        self.qcm.save(update_fields=["enonce_markdown"])
        self.ouverte.enonce_markdown = "Question ouverte. (6,5 points)"
        self.ouverte.save(update_fields=["enonce_markdown"])

        par_numero = self.points_par_numero()

        self.assertEqual(par_numero["1"]["points"], 1.5)
        self.assertEqual(par_numero["2"]["points"], 6.5)
        self.assertFalse(par_numero["1"]["bareme_estime"])
        self.assertFalse(par_numero["2"]["bareme_estime"])

    def test_un_bareme_annonce_partiel_laisse_le_reste_estime(self):
        self.qcm.enonce_markdown = "QCM ? (3 pts)"
        self.qcm.save(update_fields=["enonce_markdown"])

        par_numero = self.points_par_numero()

        self.assertEqual(par_numero["1"]["points"], 3.0)
        self.assertFalse(par_numero["1"]["bareme_estime"])
        self.assertEqual(par_numero["2"]["points"], 5.0)
        self.assertTrue(par_numero["2"]["bareme_estime"])

    def test_un_bareme_annonce_incoherent_avec_l_exercice_est_ignore(self):
        # 6 + 6 = 12 > 8 points pour l'exercice : mieux vaut estimer que d'afficher un total faux.
        self.qcm.enonce_markdown = "QCM ? (6 pts)"
        self.qcm.save(update_fields=["enonce_markdown"])
        self.ouverte.enonce_markdown = "Ouverte. (6 pts)"
        self.ouverte.save(update_fields=["enonce_markdown"])

        par_numero = self.points_par_numero()

        self.assertEqual(par_numero["1"]["points"], 4.0)
        self.assertTrue(par_numero["1"]["bareme_estime"])

    def test_les_points_explicites_d_une_question_restent_et_le_reste_est_reparti(self):
        self.ouverte.points = Decimal("2.5")
        self.ouverte.save(update_fields=["points"])

        data = self.client.get(self.detail_url).data

        par_numero = {q["numero"]: q for q in data["exercices"][0]["questions"]}
        self.assertEqual(par_numero["2"]["points"], 2.5)
        self.assertFalse(par_numero["2"]["bareme_estime"])
        self.assertEqual(par_numero["1"]["points"], 5.5)
        self.assertTrue(par_numero["1"]["bareme_estime"])
        self.assertEqual(data["bareme"], 8.0)


class NoterQuestionTests(NotationAPITestCase):
    def setUp(self):
        super().setUp()
        self.donner_une_grille()

    def test_les_criteres_coches_donnent_les_points_et_mettent_la_note_a_jour(self):
        response = self.client.post(self.url("noter", self.ouverte), {"criteres_valides": [0, 1]}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["reponse"]["points_obtenus"], 2.5)
        self.assertEqual(response.data["notation"]["note"], 2.5)
        self.assertEqual(response.data["notation"]["bareme"], 8.0)
        self.assertTrue(response.data["traitee"])
        reponse = TentativeReponse.objects.get(tentative=self.tentative, question=self.ouverte)
        self.assertEqual(reponse.points_obtenus, Decimal("2.50"))
        self.assertEqual(reponse.resultat_declare, "REUSSI")

    def test_un_critere_partiel_donne_un_resultat_partiel(self):
        self.client.post(self.url("noter", self.ouverte), {"criteres_valides": [0]}, format="json")

        reponse = TentativeReponse.objects.get(tentative=self.tentative, question=self.ouverte)
        self.assertEqual(reponse.points_obtenus, Decimal("1.00"))
        self.assertEqual(reponse.resultat_declare, "PARTIEL")

    def test_indice_de_critere_invalide(self):
        for invalide in ([5], [-1], [0, 0], "0", [True]):
            response = self.client.post(self.url("noter", self.ouverte), {"criteres_valides": invalide}, format="json")
            self.assertEqual(response.status_code, 400, invalide)

    def test_points_directs_refuses_quand_la_question_a_une_grille(self):
        response = self.client.post(self.url("noter", self.ouverte), {"points_obtenus": 1}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_criteres_refuses_quand_la_question_n_a_pas_de_grille(self):
        self.ouverte.criteres_notation = []
        self.ouverte.save(update_fields=["criteres_notation"])

        response = self.client.post(self.url("noter", self.ouverte), {"criteres_valides": [0]}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_saisie_directe_bornee_par_le_bareme_de_la_question(self):
        self.ouverte.criteres_notation = []
        self.ouverte.points = Decimal("4")
        self.ouverte.save(update_fields=["criteres_notation", "points"])

        self.assertEqual(self.client.post(self.url("noter", self.ouverte), {"points_obtenus": "2,75"}).status_code, 200)
        self.assertEqual(self.client.post(self.url("noter", self.ouverte), {"points_obtenus": 4.5}).status_code, 400)
        self.assertEqual(self.client.post(self.url("noter", self.ouverte), {"points_obtenus": -1}).status_code, 400)
        self.assertEqual(self.client.post(self.url("noter", self.ouverte), {"points_obtenus": "abc"}).status_code, 400)
        reponse = TentativeReponse.objects.get(tentative=self.tentative, question=self.ouverte)
        self.assertEqual(reponse.points_obtenus, Decimal("2.75"))

    def test_une_qcm_ne_se_note_pas(self):
        response = self.client.post(self.url("noter", self.qcm), {"traitee": True}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_corps_vide_refuse(self):
        self.assertEqual(self.client.post(self.url("noter", self.ouverte), {}, format="json").status_code, 400)

    def test_noter_ne_touche_pas_a_la_tentative_d_un_autre_eleve(self):
        autre = User.objects.create_user(phone_number="677400091", password="x")
        self.client.force_authenticate(user=autre)
        response = self.client.post(self.url("noter", self.ouverte), {"traitee": True}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_le_palier_de_revision_n_avance_qu_a_la_premiere_notation(self):
        with mock.patch("inedit.views.enregistrer_resultat_pour_revision") as enregistrer:
            self.client.post(self.url("noter", self.ouverte), {"criteres_valides": [0]}, format="json")
            self.client.post(self.url("noter", self.ouverte), {"criteres_valides": [0, 1]}, format="json")
            self.client.post(self.url("noter", self.ouverte), {"criteres_valides": []}, format="json")

        self.assertEqual(enregistrer.call_count, 1)


class ModeExamenEtNotationTests(NotationAPITestCase):
    def setUp(self):
        super().setUp()
        self.donner_une_grille()
        self.passer_en_mode_examen()

    def test_traiter_une_question_est_possible_pendant_l_examen_sans_reveler_le_corrige(self):
        response = self.client.post(self.url("noter", self.ouverte), {"traitee": True}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["traitee"])
        self.assertIsNone(response.data["notation"])
        self.assertNotIn("corrige_markdown", response.data)
        self.assertNotIn("criteres_notation", response.data)

    def test_noter_est_refuse_tant_que_le_corrigé_est_masque(self):
        response = self.client.post(self.url("noter", self.ouverte), {"criteres_valides": [0, 1]}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(TentativeReponse.objects.filter(tentative=self.tentative).exists())

    def test_ni_la_note_ni_la_grille_ne_fuitent_dans_le_payload_de_la_tentative(self):
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})

        data = self.client.get(self.detail_url).data

        self.assertIsNone(data["notation"])
        for question in data["exercices"][0]["questions"]:
            self.assertNotIn("criteres_notation", question)
            self.assertNotIn("points_obtenus", question.get("reponse", {}))
        # Le barème total, lui, est connu : ce n'est pas la solution.
        self.assertEqual(data["bareme"], 8.0)

    def test_retirer_une_question_traitee_pendant_l_examen(self):
        self.client.post(self.url("noter", self.ouverte), {"traitee": True}, format="json")

        response = self.client.post(self.url("noter", self.ouverte), {"traitee": False}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["traitee"])
        self.assertFalse(TentativeReponse.objects.filter(tentative=self.tentative).exists())

    def test_apres_la_soumission_on_note_et_la_note_stockee_suit(self):
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})
        self.client.post(self.url("noter", self.ouverte), {"traitee": True}, format="json")
        resultat = self.client.post(self.url("completer")).data
        # La QCM pèse 5,5 (8 points moins les 2,5 de la grille de l'ouverte) ; l'ouverte est
        # traitée mais pas encore notée.
        self.assertEqual(resultat["note"], 5.5)
        self.assertEqual(resultat["questions_a_noter"], 1)
        self.assertFalse(resultat["definitive"])

        response = self.client.post(self.url("noter", self.ouverte), {"criteres_valides": [0]}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["notation"]["note"], 6.5)
        self.assertTrue(response.data["notation"]["definitive"])
        self.tentative.refresh_from_db()
        self.assertEqual(self.tentative.note_obtenue, Decimal("6.50"))
        self.assertEqual(self.tentative.score_obtenu, 81)

    def test_apres_la_soumission_on_peut_declarer_une_question_faite_sur_papier(self):
        self.client.post(self.url("completer"))

        response = self.client.post(self.url("noter", self.ouverte), {"traitee": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["traitee"])
        self.assertEqual(response.data["notation"]["questions_a_noter"], 1)

        # ... mais jamais la retirer : l'élève ne réécrit pas sa copie rendue.
        response = self.client.post(self.url("noter", self.ouverte), {"traitee": False}, format="json")
        self.assertEqual(response.status_code, 409)

    def test_apres_la_soumission_les_criteres_et_le_bareme_sont_servis(self):
        self.client.post(self.url("completer"))

        data = self.client.get(self.detail_url).data

        ouverte = next(q for q in data["exercices"][0]["questions"] if q["numero"] == "2")
        self.assertEqual(len(ouverte["criteres_notation"]), 2)
        self.assertEqual(data["notation"]["note"], 0.0)
        self.assertEqual(data["notation"]["questions_non_traitees"], 2)
