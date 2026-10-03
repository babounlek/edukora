"""
XP et objectif du jour (voir quiz.xp) : ce qui rendrait le compteur menteur en cassant -
une réponse qui rapporterait deux fois, un thème dû dont le bonus se perdrait, un objectif
changé qui ferait retomber une série déjà gagnée.
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from analytics.models import AnalyticsEvent, EventName
from catalog.models import Cursus, Examen, Subject, Tag, TypeReponse
from subscriptions.models import Subscription
from users.models import User

from . import xp
from .models import (
    GainXP, JourXP, ModeQuiz, OrigineSeance, QuizAnswer, QuizQuestion, QuizSession, RevisionSchedule,
    SeanceJournaliere, StatutSeance,
)
from .serie import semaine_courante, serie_de_jours
from .services import terminer_seance
from .tests import _make_competence_item

CHOIX = [{"lettre": "a", "texte": "2x"}, {"lettre": "b", "texte": "x"}]


class XpFixture(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900501", password="x")
        self.profil = self.user.profils.first()
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.subject = Subject.objects.create(code="MATHS_TEST_XP", label="Maths (test xp)", country=self.cursus.country)
        self.theme = Tag.objects.create(name="limites (test xp)")
        Subscription.objects.activate_or_extend(self.user, self.cursus, duration_days=200)
        self.session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        self.ordre = 0
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def qcm(self, numero):
        return _make_competence_item(
            self.subject, self.cursus, theme=self.theme, numero=numero, type_reponse=TypeReponse.QCM,
            choix=CHOIX, reponse_correcte="a",
        )

    def ouverte(self, numero):
        return _make_competence_item(self.subject, self.cursus, theme=self.theme, numero=numero)

    def question(self, item):
        self.ordre += 1
        return QuizQuestion.objects.create(session=self.session, competence_item=item, ordre=self.ordre)

    def repondre(self, quiz_question, **corps):
        url = f"/quiz/sessions/{self.session.id}/questions/{quiz_question.id}/answer/"
        return self.client.post(url, corps, format="json")

    def xp_du_jour(self):
        return xp.etat_du_jour(self.profil)["xp"]


class BaremeTests(XpFixture):
    def test_qcm_juste_du_premier_essai_rapporte_dix(self):
        reponse = self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        self.assertEqual(reponse.json()["reponse"]["xp_gagne"], xp.XP_QCM_JUSTE)
        self.assertEqual(self.xp_du_jour(), xp.XP_QCM_JUSTE)

    def test_une_reponse_fausse_ne_rapporte_ni_ne_retire_rien(self):
        self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        reponse = self.repondre(self.question(self.qcm("2")), reponse_choisie="b")
        self.assertEqual(reponse.json()["reponse"]["xp_gagne"], 0)
        self.assertEqual(self.xp_du_jour(), xp.XP_QCM_JUSTE)

    def test_question_ouverte_rapporte_moins_selon_l_auto_evaluation(self):
        self.assertEqual(
            self.repondre(self.question(self.ouverte("1")), resultat_declare="REUSSI").json()["reponse"]["xp_gagne"], 5,
        )
        self.assertEqual(
            self.repondre(self.question(self.ouverte("2")), resultat_declare="PARTIEL").json()["reponse"]["xp_gagne"], 2,
        )
        self.assertEqual(
            self.repondre(self.question(self.ouverte("3")), resultat_declare="ECHEC").json()["reponse"]["xp_gagne"], 0,
        )

    def test_rejouer_la_requete_ne_credite_rien_de_plus(self):
        quiz_question = self.question(self.qcm("1"))
        self.repondre(quiz_question, reponse_choisie="a")
        self.repondre(quiz_question, reponse_choisie="a")
        self.assertEqual(GainXP.objects.count(), 1)
        self.assertEqual(self.xp_du_jour(), xp.XP_QCM_JUSTE)

    def test_corriger_une_erreur_en_repondant_de_nouveau_ne_rapporte_rien(self):
        quiz_question = self.question(self.qcm("1"))
        self.repondre(quiz_question, reponse_choisie="b")
        self.repondre(quiz_question, reponse_choisie="a")
        self.assertEqual(GainXP.objects.count(), 0)

    def test_un_meme_item_ne_rapporte_qu_une_fois_par_jour(self):
        item = self.qcm("1")
        self.repondre(self.question(item), reponse_choisie="a")
        deuxieme = self.repondre(self.question(item), reponse_choisie="a")
        self.assertEqual(deuxieme.json()["reponse"]["xp_gagne"], 0)
        self.assertEqual(self.xp_du_jour(), xp.XP_QCM_JUSTE)

    def test_theme_du_en_revision_rapporte_un_bonus(self):
        RevisionSchedule.objects.create(
            profil=self.profil, cursus=self.cursus, subject=self.subject, theme=self.theme,
            palier=0, due_at=timezone.localdate(),
        )
        reponse = self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        self.assertEqual(reponse.json()["reponse"]["xp_gagne"], xp.XP_QCM_JUSTE + xp.BONUS_REVISION)
        self.assertTrue(GainXP.objects.get().bonus_revision)

    def test_theme_pas_encore_du_ne_donne_pas_de_bonus(self):
        RevisionSchedule.objects.create(
            profil=self.profil, cursus=self.cursus, subject=self.subject, theme=self.theme,
            palier=0, due_at=timezone.localdate() + timedelta(days=2),
        )
        reponse = self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        self.assertEqual(reponse.json()["reponse"]["xp_gagne"], xp.XP_QCM_JUSTE)

    def test_pas_de_bonus_sur_une_reponse_fausse_meme_si_le_theme_est_du(self):
        RevisionSchedule.objects.create(
            profil=self.profil, cursus=self.cursus, subject=self.subject, theme=self.theme,
            palier=0, due_at=timezone.localdate(),
        )
        reponse = self.repondre(self.question(self.qcm("1")), reponse_choisie="b")
        self.assertEqual(reponse.json()["reponse"]["xp_gagne"], 0)

    def test_le_payload_de_la_session_relit_le_gain(self):
        self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        session = self.client.get(f"/quiz/sessions/{self.session.id}/").json()
        self.assertEqual(session["questions"][0]["reponse"]["xp_gagne"], xp.XP_QCM_JUSTE)


class SeanceEtObjectifTests(XpFixture):
    def seance(self, ordre=1):
        return SeanceJournaliere.objects.create(
            profil=self.profil, cursus=self.cursus, date=timezone.localdate(), origine=OrigineSeance.PARCOURS,
            ordre=ordre, statut=StatutSeance.PROPOSEE, etapes=[],
        )

    def test_terminer_la_seance_rapporte_le_bonus_une_fois(self):
        seance = self.seance()
        terminer_seance(seance)
        terminer_seance(seance)
        self.assertEqual(self.xp_du_jour(), xp.XP_SEANCE)

    def test_une_seance_supplementaire_ne_rapporte_pas_un_second_bonus(self):
        terminer_seance(self.seance(ordre=1))
        terminer_seance(self.seance(ordre=2))
        self.assertEqual(self.xp_du_jour(), xp.XP_SEANCE)

    def test_atteindre_l_objectif_est_note_une_seule_fois(self):
        xp.definir_objectif(self.profil, 10)
        self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        self.repondre(self.question(self.qcm("2")), reponse_choisie="a")
        etat = xp.etat_du_jour(self.profil)
        self.assertTrue(etat["atteint"])
        self.assertEqual(etat["xp"], 20)
        self.assertEqual(AnalyticsEvent.objects.filter(name=EventName.OBJECTIF_XP_ATTEINT).count(), 1)

    def test_la_reponse_dit_si_elle_a_fait_franchir_l_objectif(self):
        xp.definir_objectif(self.profil, 10)
        premiere = self.repondre(self.question(self.qcm("1")), reponse_choisie="a").json()
        seconde = self.repondre(self.question(self.qcm("2")), reponse_choisie="a").json()
        fausse = self.repondre(self.question(self.qcm("3")), reponse_choisie="b").json()
        self.assertTrue(premiere["objectif_atteint_maintenant"])
        self.assertEqual(premiere["xp_jour"]["xp"], 10)
        self.assertFalse(seconde["objectif_atteint_maintenant"])
        self.assertFalse(fausse["objectif_atteint_maintenant"])

    def test_la_session_expose_l_xp_du_jour(self):
        self.assertEqual(self.client.get(f"/quiz/sessions/{self.session.id}/").json()["xp_jour"]["objectif"], 20)

    def test_objectif_par_defaut_vingt(self):
        etat = xp.etat_du_jour(self.profil)
        self.assertEqual((etat["objectif"], etat["xp"], etat["atteint"]), (20, 0, False))
        self.assertEqual(etat["objectifs_possibles"], [10, 20, 30])

    def test_monter_l_objectif_ne_retire_pas_un_jour_deja_atteint(self):
        xp.definir_objectif(self.profil, 10)
        self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        xp.definir_objectif(self.profil, 30)
        self.assertTrue(xp.etat_du_jour(self.profil)["atteint"])

    def test_baisser_l_objectif_peut_faire_atteindre_le_jour(self):
        self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        self.assertFalse(xp.etat_du_jour(self.profil)["atteint"])
        xp.definir_objectif(self.profil, 10)
        self.assertTrue(xp.etat_du_jour(self.profil)["atteint"])

    def test_les_jours_passes_gardent_leur_objectif(self):
        hier = timezone.localdate() - timedelta(days=1)
        JourXP.objects.create(profil=self.profil, jour=hier, xp=20, objectif=20, atteint=True)
        xp.definir_objectif(self.profil, 30)
        self.assertEqual(JourXP.objects.get(jour=hier).objectif, 20)
        self.assertEqual(xp.jours_atteints(self.profil), {hier})

    def test_un_objectif_hors_liste_est_refuse(self):
        with self.assertRaises(ValueError):
            xp.definir_objectif(self.profil, 25)

    def test_endpoint_objectif(self):
        reponse = self.client.post("/quiz/xp/objectif/", {"objectif": 30}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json()["objectif"], 30)
        self.profil.refresh_from_db()
        self.assertEqual(self.profil.objectif_xp_quotidien, 30)
        self.assertTrue(AnalyticsEvent.objects.filter(name=EventName.OBJECTIF_XP_CHOISI).exists())
        self.assertEqual(self.client.post("/quiz/xp/objectif/", {"objectif": 25}, format="json").status_code, 400)
        self.assertEqual(self.client.post("/quiz/xp/objectif/", {}, format="json").status_code, 400)
        self.assertEqual(self.client.get("/quiz/xp/objectif/").json()["objectif"], 30)

    def test_le_resultat_de_session_dit_ce_que_le_quiz_a_rapporte(self):
        self.repondre(self.question(self.qcm("1")), reponse_choisie="a")
        resultat = self.client.post(f"/quiz/sessions/{self.session.id}/completer/").json()
        self.assertEqual(resultat["xp"]["session"]["reponses"], xp.XP_QCM_JUSTE)
        self.assertEqual(resultat["xp"]["jour"]["xp"], xp.XP_QCM_JUSTE)


class SerieEtXpTests(XpFixture):
    def test_un_jour_d_objectif_atteint_compte_pour_la_serie_sans_seance(self):
        aujourdhui = timezone.localdate()
        for decalage in (0, 1, 2):
            JourXP.objects.create(
                profil=self.profil, jour=aujourdhui - timedelta(days=decalage), xp=20, objectif=20, atteint=True,
            )
        serie = serie_de_jours(self.profil)
        self.assertEqual(serie["jours"], 3)
        self.assertTrue(serie["actif_aujourdhui"])

    def test_un_jour_d_xp_sous_l_objectif_ne_compte_pas(self):
        JourXP.objects.create(profil=self.profil, jour=timezone.localdate(), xp=10, objectif=20, atteint=False)
        self.assertFalse(serie_de_jours(self.profil)["actif_aujourdhui"])

    def test_la_semaine_va_du_lundi_au_dimanche(self):
        mercredi = timezone.localdate().replace(year=2026, month=9, day=30)  # un mercredi
        lundi = mercredi - timedelta(days=2)
        semaine = semaine_courante({lundi, mercredi}, mercredi)
        self.assertEqual(len(semaine), 7)
        self.assertEqual(semaine[0]["date"], lundi.isoformat())
        self.assertEqual([j["fait"] for j in semaine], [True, False, True, False, False, False, False])
        self.assertEqual([j["aujourdhui"] for j in semaine], [False, False, True, False, False, False, False])

    def test_la_serie_expose_la_semaine(self):
        self.assertEqual(len(serie_de_jours(self.profil)["semaine"]), 7)

    def test_le_plan_du_jour_expose_l_xp(self):
        plan = self.client.get("/quiz/plan-du-jour/").json()
        self.assertEqual(plan["xp"]["objectif"], 20)
        self.assertIn("semaine", plan["serie"])
