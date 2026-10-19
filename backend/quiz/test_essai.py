"""
Essai gratuit sans compte (voir quiz.essai) : un visiteur anonyme joue un thème entièrement vitrine,
et RIEN d'autre - jamais un item payant, jamais le corrigé avant sa réponse, jamais d'écriture.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, Subject, Tag, TypeReponse

from .models import CompetenceItem, QuizAnswer, QuizQuestion, QuizSession
from .gratuits import themes_gratuits_par_matiere
from .tests import _make_competence_item, _make_lesson_avec_themes


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

    def test_chaque_essai_expose_la_langue_de_son_examen(self):
        """Le frontend filtre les essais sur la langue de l'interface : GCE -> en, BAC -> fr."""
        maths_gce = Subject.objects.get(country__code="CM", code="GCE_MATHS")
        gce = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        theme_gce = Tag.objects.create(name="theme-essai-gce")
        for i in range(3):
            _make_competence_item(maths_gce, gce, theme=theme_gce, numero=f"g{i}", est_vitrine=True)

        par_cursus = {e["cursus"]: e["langue"] for e in self.client.get("/quiz/essais/").json()}

        self.assertEqual(par_cursus[self.cursus.id], "fr")
        self.assertEqual(par_cursus[gce.id], "en")

    def test_les_examens_suivent_l_ordre_du_parcours_scolaire_et_non_l_alphabet(self):
        """BEPC avant le Probatoire avant le BAC : alphabétique, la liste s'ouvrait sur « BAC - A » (test élève P1)."""
        bepc = Cursus.objects.get(country__code="CM", examen=Examen.BEPC)
        maths_bepc = Subject.objects.get(country__code="CM", code="MATHS")
        theme_bepc = Tag.objects.create(name="theme-essai-bepc")
        for i in range(3):
            _make_competence_item(maths_bepc, bepc, theme=theme_bepc, numero=f"b{i}", est_vitrine=True)

        ordre = []
        for essai in self.client.get("/quiz/essais/").json():
            if essai["cursus"] not in ordre:
                ordre.append(essai["cursus"])

        self.assertLess(ordre.index(bepc.id), ordre.index(self.cursus.id))

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


class UnThemeParMatiereTests(TestCase):
    """Les items sont partagés entre cursus : sans tri, un thème coché pour un cursus devenait
    gratuit dans tous les autres et la liste empilait plusieurs thèmes de la même matière."""

    def setUp(self):
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")
        self.anglais = Subject.objects.get(country__code="CM", code="ANGLAIS")
        self.bac_c = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.bac_d = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.client = APIClient()

    def _theme_gratuit(self, sujet, cursus, nom, numero):
        theme = Tag.objects.create(name=nom)
        for i in range(2):
            _make_competence_item(sujet, cursus, theme=theme, numero=f"{numero}{i}", est_vitrine=True)
        return theme

    def test_garde_le_theme_le_plus_frequent_du_cursus(self):
        rare = self._theme_gratuit(self.maths, self.bac_c, "theme-rare", "r")
        frequent = self._theme_gratuit(self.maths, self.bac_c, "theme-frequent", "f")
        _make_lesson_avec_themes(self.maths, self.bac_c, "Épreuve 1", [[frequent], [rare]])
        _make_lesson_avec_themes(self.maths, self.bac_c, "Épreuve 2", [[frequent]])
        _make_lesson_avec_themes(self.maths, self.bac_c, "Épreuve 3", [[frequent]])

        essais = [e for e in self.client.get("/quiz/essais/").json() if e["cursus"] == self.bac_c.id]

        self.assertEqual([e["theme"] for e in essais if e["subject_code"] == "MATHS"], [frequent.id])

    def test_un_theme_partage_entre_deux_cursus_ne_double_pas_une_matiere(self):
        # Même item dans C et D : un second thème de Maths coché pour D n'empile pas deux thèmes en D.
        partage = Tag.objects.create(name="theme-partage")
        for i in range(2):
            _make_competence_item(
                self.maths, [self.bac_c, self.bac_d], theme=partage, numero=f"p{i}", est_vitrine=True,
            )
        propre_a_d = self._theme_gratuit(self.maths, self.bac_d, "theme-propre-d", "d")
        _make_lesson_avec_themes(self.maths, self.bac_d, "Épreuve D", [[propre_a_d]])

        en_d = [
            e for e in self.client.get("/quiz/essais/").json()
            if e["cursus"] == self.bac_d.id and e["subject_code"] == "MATHS"
        ]

        self.assertEqual(len(en_d), 1)
        self.assertEqual(en_d[0]["theme"], propre_a_d.id)

    def test_deux_matieres_gardent_chacune_leur_theme(self):
        maths = self._theme_gratuit(self.maths, self.bac_c, "theme-maths", "m")
        anglais = self._theme_gratuit(self.anglais, self.bac_c, "theme-anglais", "a")

        essais = {e["subject_code"]: e["theme"] for e in self.client.get("/quiz/essais/").json() if e["cursus"] == self.bac_c.id}

        self.assertEqual(essais, {"MATHS": maths.id, "ANGLAIS": anglais.id})

    def test_themes_gratuits_par_matiere_ignore_un_theme_a_moitie_gratuit(self):
        theme = Tag.objects.create(name="theme-mitige")
        _make_competence_item(self.maths, self.bac_c, theme=theme, numero="g1", est_vitrine=True)
        _make_competence_item(self.maths, self.bac_c, theme=theme, numero="g2")  # payant

        self.assertEqual(themes_gratuits_par_matiere([self.bac_c.id]), [])

    def test_un_theme_gratuit_non_retenu_ne_se_joue_pas(self):
        # Deux thèmes entièrement gratuits pour (BAC C, Maths) : seul le plus fréquent est le quiz
        # gratuit de la matière. L'autre reste coché (un item partagé), mais il n'est ni proposé ni jouable.
        rare = self._theme_gratuit(self.maths, self.bac_c, "theme-rare-2", "x")
        frequent = self._theme_gratuit(self.maths, self.bac_c, "theme-frequent-2", "y")
        _make_lesson_avec_themes(self.maths, self.bac_c, "Épreuve A", [[frequent]])
        _make_lesson_avec_themes(self.maths, self.bac_c, "Épreuve B", [[frequent], [rare]])
        item_rare = CompetenceItem.objects.filter(theme=rare).first()
        base = {"cursus": self.bac_c.id, "subject": self.maths.id}

        retenu = self.client.post("/quiz/essais/demarrer/", {**base, "theme": frequent.id}, format="json")
        ecarte = self.client.post("/quiz/essais/demarrer/", {**base, "theme": rare.id}, format="json")
        reponse = self.client.post(
            "/quiz/essais/repondre/",
            {"cursus": self.bac_c.id, "item": item_rare.id, "resultat_declare": "REUSSI"}, format="json",
        )
        corrige = self.client.get(f"/quiz/essais/corrige/?cursus={self.bac_c.id}&item={item_rare.id}")

        self.assertEqual(retenu.status_code, 201)
        self.assertEqual(ecarte.status_code, 403)
        self.assertEqual(reponse.status_code, 404)
        self.assertEqual(corrige.status_code, 404)
