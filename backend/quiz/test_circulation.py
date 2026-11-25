"""
Les données circulent entre les modules (audit du 2026-11-25, rapport 18) : séance, copies d'examen blanc, maîtrise,
bilan du parent, rappels, passages d'un contenu à l'autre, avis après la séance et page de la semaine.
"""

from datetime import timedelta

from django.utils import timezone

from access.models import ExerciceFait
from analytics.models import AnalyticsEvent, EventName
from analytics.semaine import avis_des_seances, demander_avis_seance, point_de_la_semaine
from catalog.models import Cours, StatutContenu, Tag
from inedit.models import TentativeInedite, TentativeReponse
from inedit.test_notation import NotationAPITestCase
from memos.models import Memo, StatutMemo
from relances.bilan_parent import composer_bilan_parent
from relances.services import destinataires_rappel_seance
from relances.tests import RelancesTestCase
from simulations.tests import SimulationTestCase
from subscriptions.models import Subscription
from users.models import User

from .definitions import jours_actifs
from .models import JourXP, SeanceJournaliere, SignalementQuestion, StatutSeance
from .services import _exercices_pour_theme, maitrise_par_theme, progression_par_theme


class SeanceSansRediteTests(SimulationTestCase):
    def exercices(self, theme):
        return [
            e["exercise_id"]
            for e in _exercices_pour_theme(self.cursus, self.lesson.subject, theme, 2, profil=self.profil)
        ]

    def test_un_exercice_deja_fait_est_ecarte_tant_qu_il_en_reste_d_autres(self):
        theme = self.ex1.questions.first().themes.first()
        question = self.ex2.questions.first()
        question.themes.add(theme)
        self.assertEqual(sorted(self.exercices(theme)), sorted([self.ex1.pk, self.ex2.pk]))

        ExerciceFait.objects.create(profil=self.profil, exercise=self.ex1)

        self.assertEqual(self.exercices(theme), [self.ex2.pk])

    def test_quand_tout_est_fait_les_exercices_reviennent(self):
        theme = self.ex1.questions.first().themes.first()
        ExerciceFait.objects.create(profil=self.profil, exercise=self.ex1)

        self.assertIn(self.ex1.pk, self.exercices(theme))


class AnnalesCirculentTests(SimulationTestCase):
    def test_la_liste_ne_garde_que_l_examen_prepare(self):
        from catalog.models import Cursus, Examen

        self.demarrer()
        self.user.cursus_prepare = Cursus.objects.get(country__code="CM", examen=Examen.BEPC)
        self.user.save(update_fields=["cursus_prepare"])
        self.assertEqual(self.client.get("/simulations/mes-simulations/").data, [])

        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.assertEqual(len(self.client.get("/simulations/mes-simulations/").data), 1)

    def test_le_resultat_dit_si_chaque_theme_a_un_quiz_et_un_cours(self):
        self.demarrer()
        self.client.post(self.url("mode-examen"))

        themes = self.client.post(self.url("completer")).data["themes_a_reviser"]

        self.assertTrue(themes)
        self.assertEqual({(t["a_quiz"], t["a_cours"]) for t in themes}, {(False, False)})

    def test_une_copie_libre_et_vide_ne_programme_rien(self):
        self.demarrer()

        resultat = self.client.post(self.url("completer")).data

        self.assertEqual(resultat["themes_a_reviser"], [])


class QcmDeCopieDansLaMaitriseTests(NotationAPITestCase):
    def rendre(self, *, conditions_reelles):
        if conditions_reelles:
            TentativeInedite.objects.filter(pk=self.tentative.pk).update(exam_mode_started_at=timezone.now())
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})
        self.client.post(self.url("completer"))

    def test_un_qcm_en_conditions_reelles_compte(self):
        self.rendre(conditions_reelles=True)

        maitrise = maitrise_par_theme(self.profil, self.cursus)

        self.assertEqual([(m["theme"], m["total"], m["reussies"]) for m in maitrise], [("Suites numériques", 1, 1)])
        stats, _, _ = progression_par_theme(self.profil, self.cursus)
        self.assertEqual(sum(s["total"] for s in stats.values()), 1)

    def test_l_entrainement_libre_et_les_questions_notees_par_l_eleve_ne_comptent_pas(self):
        self.rendre(conditions_reelles=False)
        self.assertEqual(maitrise_par_theme(self.profil, self.cursus), [])

        TentativeInedite.objects.filter(pk=self.tentative.pk).update(exam_mode_started_at=timezone.now())
        TentativeReponse.objects.filter(tentative=self.tentative).delete()
        TentativeReponse.objects.create(tentative=self.tentative, question=self.ouverte, points_obtenus=4)
        self.assertEqual(maitrise_par_theme(self.profil, self.cursus), [])


class BilanDuParentTests(NotationAPITestCase):
    def test_le_bilan_cite_la_note_de_l_examen_blanc_et_compte_le_jour(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.client.post(self.url("answer", self.qcm), {"reponse_choisie": "b"})
        self.client.post(self.url("noter", self.ouverte), {"points_obtenus": 2}, format="json")
        self.client.post(self.url("completer"))

        _sujet, corps = composer_bilan_parent(self.user)

        self.assertIn("Examens blancs", corps)
        self.assertIn(self.epreuve.titre, corps)
        self.assertIn("sur 8", corps)
        self.assertIn("1 jour de révision sur 7", corps)
        self.assertNotIn("n'a pas révisé", corps)

    def test_des_points_suffisent_a_faire_un_jour_actif(self):
        aujourdhui = timezone.localdate()
        JourXP.objects.create(profil=self.profil, jour=aujourdhui, xp=5, objectif=50)

        self.assertEqual(jours_actifs(self.profil, aujourdhui - timedelta(days=6), aujourdhui), {aujourdhui})


class RappelObjectifAtteintTests(RelancesTestCase):
    def test_l_e_mail_se_tait_quand_l_objectif_du_jour_est_atteint(self):
        user = self.eleve()
        self.assertIn(user, destinataires_rappel_seance())

        JourXP.objects.create(profil=user.profils.first(), jour=timezone.localdate(), xp=60, objectif=50, atteint=True)

        self.assertNotIn(user, destinataires_rappel_seance())


class LiensEntreContenusTests(SimulationTestCase):
    def test_d_un_cours_vers_les_epreuves_ou_la_notion_est_tombee(self):
        theme = self.ex1.questions.first().themes.first()
        cours = Cours.objects.create(
            subject=self.lesson.subject, titre="Les suites", slug="les-suites-circulation", statut=StatutContenu.VALIDE,
        )
        cours.tags.add(theme)

        data = self.client.get(f"/catalog/cours/{cours.slug}/epreuves/?cursus={self.cursus.pk}").data

        self.assertEqual(data["total"], 1)
        self.assertEqual(data["epreuves"][0]["slug"], self.lesson.slug)

    def test_une_epreuve_ne_propose_que_les_themes_qui_ont_un_quiz(self):
        from quiz.tests import _make_competence_item

        theme = self.ex1.questions.first().themes.first()
        self.assertEqual(self.client.get(f"/catalog/lessons/{self.lesson.slug}/quiz/").data["themes"], [])

        _make_competence_item(self.lesson.subject, self.cursus, theme=theme, numero="1")
        data = self.client.get(f"/catalog/lessons/{self.lesson.slug}/quiz/?cursus={self.cursus.pk}").data

        self.assertEqual(data["cursus_id"], self.cursus.pk)
        self.assertEqual([t["theme_id"] for t in data["themes"]], [theme.pk])

    def test_une_fiche_dit_ou_elle_se_trouve_et_mene_a_son_theme(self):
        theme = Tag.objects.create(name="Scrutin circulation")
        memo = Memo.objects.create(
            subject=self.lesson.subject, terme="Scrutin", definition="Opérations de vote.", theme=theme,
            statut=StatutMemo.PUBLIE, relu_par_enseignant=True, gratuit=True,
        )
        memo.cursus.add(self.cursus)
        memo.sources.add(self.lesson)

        self.assertEqual(
            self.client.get(f"/memos/fiches/{memo.pk}/").data,
            {"matiere_id": self.lesson.subject_id, "cursus_ids": [self.cursus.pk]},
        )
        fiche = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.lesson.subject_id}").data["fiches"][0]
        self.assertEqual(fiche["theme"], {"id": theme.pk, "nom": theme.name, "a_quiz": False, "a_cours": False})
        self.assertEqual([s["slug"] for s in fiche["sources"]], [self.lesson.slug])

        self.client.post(f"/memos/fiches/{memo.pk}/garder/")
        self.client.post(f"/memos/fiches/{memo.pk}/garder/")
        self.assertEqual(AnalyticsEvent.objects.filter(name=EventName.FICHE_GARDEE).count(), 1)


class AvisEtPointDeLaSemaineTests(NotationAPITestCase):
    def terminer_des_seances(self, n):
        for i in range(n):
            SeanceJournaliere.objects.create(
                profil=self.profil, cursus=self.cursus, date=timezone.localdate() - timedelta(days=i),
                statut=StatutSeance.TERMINEE, termine_at=timezone.now(),
            )

    def test_la_question_arrive_a_la_troisieme_seance_et_une_seule_fois(self):
        self.terminer_des_seances(2)
        self.assertFalse(demander_avis_seance(self.user, self.profil))
        SeanceJournaliere.objects.create(
            profil=self.profil, cursus=self.cursus, date=timezone.localdate() - timedelta(days=9),
            statut=StatutSeance.TERMINEE, termine_at=timezone.now(),
        )
        self.assertEqual(self.client.get("/analytics/avis-seance/").data, {"demander": True})

        reponse = self.client.post(
            "/analytics/events/", {"name": "seance_avis", "properties": {"avis": "non", "motif": "trop_difficile"}},
            format="json",
        )

        self.assertEqual(reponse.status_code, 201)
        self.assertFalse(demander_avis_seance(self.user, self.profil))
        avis = avis_des_seances(timezone.now() - timedelta(days=1))
        self.assertEqual((avis["total"], avis["part_oui"]), (1, 0))
        self.assertEqual(avis["motifs"], [{"libelle": "Trop difficile", "nombre": 1}])

    def test_la_page_de_la_semaine_montre_les_signalements_avec_leur_enonce(self):
        from quiz.tests import _make_competence_item

        item = _make_competence_item(
            self.epreuve.subject, self.cursus, theme=Tag.objects.create(name="signalé"), numero="1",
        )
        SignalementQuestion.objects.create(
            profil=self.profil, competence_item=item, competence_item_id_garde=item.pk, motif="REPONSE_FAUSSE",
        )
        self.assertEqual(point_de_la_semaine()["signalements"]["lignes"][0]["enonce"], item.enonce_markdown)

        admin = User.objects.create_superuser(phone_number="677400999", password="x")
        self.client.force_login(admin)
        page = self.client.get("/admin/analytics/analyticsevent/semaine/")

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "La séance aide-t-elle ?")
        self.assertContains(page, item.subject.label)
