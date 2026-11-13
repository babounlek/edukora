"""« Mes erreurs » (voir quiz.erreurs) : la banque des questions ratées et pas encore réussies, et le paquet à refaire."""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen, StatutContenu, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from .erreurs import PAQUET_DEFAUT, PAQUET_MAX, banque_d_erreurs, compter_erreurs, resume_des_erreurs, session_des_erreurs
from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession
from .tests import _make_competence_item


class ErreursFixture(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677610001", password="x")
        self.profil = self.user.profils.first()
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")
        self.physique = Subject.objects.get(country__code="CM", code="PHYSIQUE")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.derivation = Tag.objects.create(name="dérivation")
        self.limites = Tag.objects.create(name="limites")
        self.optique = Tag.objects.create(name="optique")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def item(self, numero, subject=None, theme=None, **kwargs):
        return _make_competence_item(subject or self.maths, self.cursus, theme=theme or self.derivation, numero=numero, **kwargs)

    def repondre(self, item, resultat, il_y_a_jours=0, **session):
        """Une réponse à `item` dans une session neuve, datée d'il y a `il_y_a_jours` jours."""
        quiz = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE, **session)
        question = QuizQuestion.objects.create(session=quiz, competence_item=item, ordre=1)
        reponse = QuizAnswer.objects.create(quiz_question=question, resultat_declare=resultat)
        QuizAnswer.objects.filter(pk=reponse.pk).update(answered_at=timezone.now() - timedelta(days=il_y_a_jours))
        return quiz

    def abonner(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )


class BanqueTests(ErreursFixture):
    def test_une_question_y_est_tant_que_sa_derniere_reponse_est_fausse(self):
        ratee, rattrapee, reussie, partielle, jamais = (self.item(f"e{i}") for i in range(5))
        self.repondre(ratee, "ECHEC", il_y_a_jours=3)
        self.repondre(rattrapee, "ECHEC", il_y_a_jours=3)
        self.repondre(rattrapee, "REUSSI", il_y_a_jours=1)
        self.repondre(reussie, "REUSSI", il_y_a_jours=2)
        self.repondre(partielle, "PARTIEL", il_y_a_jours=2)

        banque = [item for item, _jour in banque_d_erreurs(self.profil, self.cursus)]

        self.assertEqual(banque, [ratee, partielle])
        self.assertNotIn(jamais, banque)
        self.assertEqual(compter_erreurs(self.profil, self.cursus), 2)

    def test_une_rechute_y_fait_revenir_la_question(self):
        item = self.item("e1")
        self.repondre(item, "REUSSI", il_y_a_jours=5)
        self.repondre(item, "ECHEC", il_y_a_jours=1)

        self.assertEqual(compter_erreurs(self.profil, self.cursus), 1)

    def test_les_plus_anciennes_erreurs_d_abord(self):
        recente, ancienne = self.item("e1"), self.item("e2")
        self.repondre(recente, "ECHEC", il_y_a_jours=0)
        self.repondre(ancienne, "ECHEC", il_y_a_jours=6)

        self.assertEqual([item for item, _jour in banque_d_erreurs(self.profil, self.cursus)], [ancienne, recente])

    def test_ni_rejeu_ni_quiz_chronometre_ni_question_depubliee_ni_autre_profil(self):
        origine = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        self.repondre(self.item("rejeu"), "ECHEC", rejeu_de=origine)
        self.repondre(self.item("chrono"), "ECHEC", chrono_actif=True)
        self.repondre(self.item("depubliee", statut=StatutContenu.BROUILLON), "ECHEC")
        autre = User.objects.create_user(phone_number="677610002", password="x").profils.first()
        etrangere = self.item("autre")
        quiz = QuizSession.objects.create(profil=autre, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        QuizAnswer.objects.create(
            quiz_question=QuizQuestion.objects.create(session=quiz, competence_item=etrangere, ordre=1),
            resultat_declare="ECHEC",
        )

        self.assertEqual(banque_d_erreurs(self.profil, self.cursus), [])

    def test_le_resume_range_matieres_et_themes_par_nombre_d_erreurs(self):
        for i in range(3):
            self.repondre(self.item(f"d{i}"), "ECHEC")
        self.repondre(self.item("l0", theme=self.limites), "ECHEC")
        self.repondre(self.item("o0", subject=self.physique, theme=self.optique), "ECHEC", il_y_a_jours=4)

        resume = resume_des_erreurs(self.profil, self.cursus)

        self.assertEqual(resume["total"], 5)
        self.assertEqual(resume["paquet"], 5)
        self.assertEqual(resume["plus_ancienne"], (timezone.localdate() - timedelta(days=4)).isoformat())
        self.assertEqual([(m["subject_code"], m["nb"]) for m in resume["matieres"]], [("MATHS", 4), ("PHYSIQUE", 1)])
        self.assertEqual(
            [(th["theme"], th["nb"]) for th in resume["matieres"][0]["themes"]], [("dérivation", 3), ("limites", 1)],
        )
        self.assertEqual(resume["matieres"][0]["themes_total"], 2)

    def test_le_paquet_propose_est_plafonne(self):
        for i in range(PAQUET_DEFAUT + 3):
            self.repondre(self.item(f"p{i}"), "ECHEC")

        resume = resume_des_erreurs(self.profil, self.cursus)

        self.assertEqual(resume["total"], PAQUET_DEFAUT + 3)
        self.assertEqual(resume["paquet"], PAQUET_DEFAUT)


class SessionTests(ErreursFixture):
    def test_la_session_reprend_les_plus_anciennes_dans_l_ordre(self):
        items = [self.item(f"s{i}") for i in range(4)]
        for jours, item in zip((1, 4, 2, 3), items):
            self.repondre(item, "ECHEC", il_y_a_jours=jours)

        session = session_des_erreurs(self.profil, self.cursus, n=3)

        self.assertEqual(session.mode, ModeQuiz.PRATIQUE)
        self.assertIsNone(session.rejeu_de_id)
        self.assertEqual(session.subject, self.maths)
        self.assertEqual(
            [q.competence_item_id for q in session.quiz_questions.order_by("ordre")],
            [items[1].pk, items[3].pk, items[2].pk],
        )

    def test_une_matiere_peut_etre_visee_et_un_paquet_mixte_n_en_porte_aucune(self):
        self.repondre(self.item("m0"), "ECHEC")
        optique = self.item("o0", subject=self.physique, theme=self.optique)
        self.repondre(optique, "ECHEC")

        mixte = session_des_erreurs(self.profil, self.cursus)
        ciblee = session_des_erreurs(self.profil, self.cursus, subject=self.physique)

        self.assertIsNone(mixte.subject)
        self.assertEqual(mixte.quiz_questions.count(), 2)
        self.assertEqual(ciblee.subject, self.physique)
        self.assertEqual([q.competence_item_id for q in ciblee.quiz_questions.all()], [optique.pk])

    def test_rien_a_refaire(self):
        with self.assertRaises(ValueError):
            session_des_erreurs(self.profil, self.cursus)

    def test_une_bonne_reponse_dans_la_session_sort_la_question_de_la_banque(self):
        self.abonner()
        item = self.item("s0")
        self.repondre(item, "ECHEC", il_y_a_jours=2)
        session = session_des_erreurs(self.profil, self.cursus)
        question = session.quiz_questions.get()

        reponse = self.client.post(
            f"/quiz/sessions/{session.pk}/questions/{question.pk}/answer/", {"resultat_declare": "REUSSI"}, format="json",
        )

        self.assertEqual(reponse.status_code, 200, reponse.data)
        self.assertEqual(compter_erreurs(self.profil, self.cursus), 0)


class ApiTests(ErreursFixture):
    def test_lire_sa_banque_ne_demande_pas_d_abonnement(self):
        self.repondre(self.item("a0"), "ECHEC")

        reponse = self.client.get(f"/quiz/erreurs/?cursus={self.cursus.pk}")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["total"], 1)

    def test_sans_parametre_c_est_l_examen_prepare_et_sans_examen_c_est_une_erreur(self):
        self.repondre(self.item("a0"), "ECHEC")
        self.assertEqual(self.client.get("/quiz/erreurs/").data["total"], 1)

        self.user.cursus_prepare = None
        self.user.save(update_fields=["cursus_prepare"])
        self.assertEqual(self.client.get("/quiz/erreurs/").status_code, 400)

    def test_refaire_exige_un_abonnement_actif(self):
        self.repondre(self.item("a0"), "ECHEC")
        avant = QuizSession.objects.count()

        reponse = self.client.post("/quiz/erreurs/refaire/", {"cursus": self.cursus.pk}, format="json")

        self.assertEqual(reponse.status_code, 403)
        self.assertEqual(QuizSession.objects.count(), avant)

    def test_refaire_les_erreurs_du_quiz_gratuit_reste_ouvert_sans_abonnement(self):
        self.repondre(self.item("a0", est_vitrine=True), "ECHEC")

        reponse = self.client.post("/quiz/erreurs/refaire/", {"cursus": self.cursus.pk}, format="json")

        self.assertEqual(reponse.status_code, 201)

    def test_refaire_ouvre_une_session_bornee(self):
        self.abonner()
        for i in range(PAQUET_MAX + 5):
            self.repondre(self.item(f"a{i}"), "ECHEC")

        par_defaut = self.client.post("/quiz/erreurs/refaire/", {"cursus": self.cursus.pk}, format="json")
        trop = self.client.post("/quiz/erreurs/refaire/", {"cursus": self.cursus.pk, "n": 500}, format="json")
        invalide = self.client.post("/quiz/erreurs/refaire/", {"cursus": self.cursus.pk, "n": "beaucoup"}, format="json")

        self.assertEqual(par_defaut.status_code, 201)
        self.assertEqual(par_defaut.data["total_questions"], PAQUET_DEFAUT)
        self.assertEqual(trop.data["total_questions"], PAQUET_MAX)
        self.assertEqual(invalide.status_code, 400)

    def test_refaire_une_seule_matiere(self):
        self.abonner()
        self.repondre(self.item("m0"), "ECHEC")
        self.repondre(self.item("o0", subject=self.physique, theme=self.optique), "ECHEC")

        reponse = self.client.post(
            "/quiz/erreurs/refaire/", {"cursus": self.cursus.pk, "subject": self.physique.pk}, format="json",
        )

        self.assertEqual(reponse.status_code, 201)
        self.assertEqual(reponse.data["total_questions"], 1)
        self.assertEqual(reponse.data["subject"], self.physique.pk)

    def test_banque_vide_rien_a_refaire(self):
        self.abonner()

        reponse = self.client.post("/quiz/erreurs/refaire/", {"cursus": self.cursus.pk}, format="json")

        self.assertEqual(reponse.status_code, 400)

    def test_l_accueil_porte_le_nombre_d_erreurs(self):
        self.abonner()
        self.repondre(self.item("a0"), "ECHEC")
        self.repondre(self.item("a1"), "PARTIEL")

        self.assertEqual(self.client.get("/quiz/accueil/").data["erreurs_total"], 2)
