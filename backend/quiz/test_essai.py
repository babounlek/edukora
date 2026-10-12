"""
Essai gratuit sans compte (voir quiz.essai) : un visiteur anonyme joue un thème entièrement vitrine,
et RIEN d'autre - jamais un item payant, jamais le corrigé avant sa réponse, jamais d'écriture.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag, TypeReponse

from .models import CompetenceItem, QuizAnswer, QuizQuestion, QuizSession
from .tests import _make_competence_item


class EssaiGratuitTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="theme-essai")
        self.items = [
            _make_competence_item(self.subject, self.cursus, theme=self.theme, numero=f"e{i}", est_vitrine=True)
            for i in range(3)
        ]
        self.client = APIClient()  # jamais authentifié

    def _payant(self):
        theme = Tag.objects.create(name="theme-payant")
        return _make_competence_item(self.subject, self.cursus, theme=theme, numero="p1")

    def _demarrer(self, **extra):
        corps = {"cursus": self.cursus.id, "subject": self.subject.id, "theme": self.theme.id, **extra}
        return self.client.post("/quiz/essais/demarrer/", corps, format="json")

    # --- liste des essais -------------------------------------------------------------------

    def test_liste_montre_un_theme_entierement_gratuit_sans_connexion(self):
        reponse = self.client.get("/quiz/essais/")

        self.assertEqual(reponse.status_code, 200)
        essai = next(e for e in reponse.json() if e["theme"] == self.theme.id)
        self.assertEqual(essai["cursus"], self.cursus.id)
        self.assertEqual(essai["nb_questions"], 3)
        self.assertEqual(essai["subject_code"], "MATHS")

    def test_liste_ecarte_un_theme_dont_un_seul_item_est_payant(self):
        _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="intrus")  # non vitrine

        theme_ids = [e["theme"] for e in self.client.get("/quiz/essais/").json()]

        self.assertNotIn(self.theme.id, theme_ids)

    def test_liste_ecarte_un_theme_payant(self):
        payant = self._payant()

        theme_ids = [e["theme"] for e in self.client.get("/quiz/essais/").json()]

        self.assertNotIn(payant.theme_id, theme_ids)

    # --- démarrage --------------------------------------------------------------------------

    def test_demarrer_sans_connexion_renvoie_les_questions_sans_corrige(self):
        reponse = self._demarrer(n=2)

        self.assertEqual(reponse.status_code, 201)
        corps = reponse.json()
        self.assertEqual(corps["total_questions"], 2)
        self.assertTrue(corps["essai"])
        ids_gratuits = {i.id for i in self.items}
        for question in corps["questions"]:
            self.assertIn(question["id"], ids_gratuits)
            for secret in ("corrige_markdown", "reponse_correcte", "reponse"):
                self.assertNotIn(secret, question)

    def test_demarrer_n_enregistre_aucune_session(self):
        self._demarrer()

        self.assertFalse(QuizSession.objects.exists())
        self.assertFalse(QuizQuestion.objects.exists())

    def test_demarrer_refuse_un_theme_payant(self):
        payant = self._payant()

        reponse = self.client.post(
            "/quiz/essais/demarrer/", {"cursus": self.cursus.id, "theme": payant.theme_id}, format="json",
        )

        self.assertEqual(reponse.status_code, 403)

    def test_demarrer_refuse_toute_la_matiere_quand_un_seul_theme_est_gratuit(self):
        self._payant()

        reponse = self.client.post(
            "/quiz/essais/demarrer/", {"cursus": self.cursus.id, "subject": self.subject.id}, format="json",
        )

        self.assertEqual(reponse.status_code, 403)

    def test_demarrer_plafonne_le_nombre_de_questions(self):
        reponse = self._demarrer(n=500)

        self.assertEqual(reponse.status_code, 201)
        self.assertEqual(reponse.json()["total_questions"], 3)  # l'essai n'en compte que 3

    def test_demarrer_tolere_des_parametres_absurdes(self):
        reponse = self.client.post("/quiz/essais/demarrer/", {"cursus": "abc", "theme": "x"}, format="json")

        self.assertEqual(reponse.status_code, 404)

    # --- réponse ----------------------------------------------------------------------------

    def test_repondre_qcm_juste_et_faux(self):
        item = _make_competence_item(
            self.subject, self.cursus, theme=self.theme, numero="qcm", est_vitrine=True,
            type_reponse=TypeReponse.QCM, reponse_correcte="b",
            choix=[{"lettre": "a", "texte": "1"}, {"lettre": "b", "texte": "2"}],
        )
        base = {"cursus": self.cursus.id, "item": item.id}

        juste = self.client.post("/quiz/essais/repondre/", {**base, "reponse_choisie": "b"}, format="json").json()
        faux = self.client.post("/quiz/essais/repondre/", {**base, "reponse_choisie": "a"}, format="json").json()

        self.assertTrue(juste["reponse"]["est_correcte"])
        self.assertFalse(faux["reponse"]["est_correcte"])
        self.assertEqual(faux["reponse_correcte"], "b")
        self.assertIn("Corrigé qcm", faux["corrige_markdown"])
        self.assertEqual(faux["reponse"]["xp_gagne"], 0)

    def test_repondre_ouverte_suit_l_auto_evaluation(self):
        base = {"cursus": self.cursus.id, "item": self.items[0].id}

        reussi = self.client.post("/quiz/essais/repondre/", {**base, "resultat_declare": "REUSSI"}, format="json").json()
        echec = self.client.post("/quiz/essais/repondre/", {**base, "resultat_declare": "ECHEC"}, format="json").json()

        self.assertTrue(reussi["reponse"]["est_correcte"])
        self.assertFalse(echec["reponse"]["est_correcte"])

    def test_repondre_n_ecrit_rien(self):
        self.client.post(
            "/quiz/essais/repondre/",
            {"cursus": self.cursus.id, "item": self.items[0].id, "resultat_declare": "REUSSI"}, format="json",
        )

        self.assertFalse(QuizAnswer.objects.exists())

    def test_repondre_refuse_les_entrees_invalides(self):
        base = {"cursus": self.cursus.id, "item": self.items[0].id}

        self.assertEqual(self.client.post("/quiz/essais/repondre/", base, format="json").status_code, 400)
        self.assertEqual(
            self.client.post("/quiz/essais/repondre/", {**base, "resultat_declare": "BOF"}, format="json").status_code,
            400,
        )

    def test_repondre_refuse_un_item_payant_ou_un_mauvais_cursus(self):
        payant = self._payant()
        autre = Cursus.objects.get(country__code="CM", examen=Examen.BEPC)

        sur_payant = self.client.post(
            "/quiz/essais/repondre/",
            {"cursus": self.cursus.id, "item": payant.id, "resultat_declare": "REUSSI"}, format="json",
        )
        mauvais_cursus = self.client.post(
            "/quiz/essais/repondre/",
            {"cursus": autre.id, "item": self.items[0].id, "resultat_declare": "REUSSI"}, format="json",
        )

        self.assertEqual(sur_payant.status_code, 404)
        self.assertEqual(mauvais_cursus.status_code, 404)

    def test_repondre_refuse_un_item_non_valide(self):
        brouillon = _make_competence_item(
            self.subject, self.cursus, theme=self.theme, numero="brouillon", est_vitrine=True, statut="BROUILLON",
        )

        reponse = self.client.post(
            "/quiz/essais/repondre/",
            {"cursus": self.cursus.id, "item": brouillon.id, "resultat_declare": "REUSSI"}, format="json",
        )

        self.assertEqual(reponse.status_code, 404)

    # --- corrigé ----------------------------------------------------------------------------

    def test_corrige_d_une_question_gratuite(self):
        reponse = self.client.get(f"/quiz/essais/corrige/?cursus={self.cursus.id}&item={self.items[0].id}")

        self.assertEqual(reponse.status_code, 200)
        self.assertIn("Corrigé e0", reponse.json()["corrige_markdown"])

    def test_corrige_d_une_question_payante_est_refuse(self):
        payant = self._payant()

        reponse = self.client.get(f"/quiz/essais/corrige/?cursus={self.cursus.id}&item={payant.id}")

        self.assertEqual(reponse.status_code, 404)

    def test_aucune_route_de_l_essai_ne_touche_a_un_item_non_gratuit(self):
        # Garde-fou global : la base ne doit contenir aucun item gratuit créé par ces appels.
        self._demarrer()
        self.assertEqual(CompetenceItem.objects.filter(est_vitrine=True).count(), 3)
