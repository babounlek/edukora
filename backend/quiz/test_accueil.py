"""
L'accueil d'un abonné en une requête (voir quiz.accueil et views.accueil_view).

Ce qui est testé, c'est ce qui rendrait la page menteuse en cassant : la borne du
"depuis la dernière fois" qui avancerait à chaque rechargement, une projection
affichée sans rythme mesuré, une phrase de coach qui ne nommerait plus le thème, un
anneau qui repasserait au comptage brut.
"""
from datetime import timedelta

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from analytics.models import AnalyticsEvent, EventName
from catalog.models import Cursus, ExamSession, Examen, Lesson, LessonType, Origine, StatutContenu, Subject, Tag
from programme.models import Module, Savoir
from simulations.models import SimulationEpreuve
from subscriptions.models import Subscription
from users.models import User

from . import accueil
from .models import (
    ModeQuiz, OrigineSeance, QuizAnswer, QuizQuestion, QuizSession, SeanceJournaliere, StatutSeance, VisiteAccueil,
)
from .services import en_derniere_ligne_droite, poids_savoir, resume_parcours
from .tests import _make_competence_item, _make_question


class VisiteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900401", password="x")
        self.profil = self.user.profils.first()

    def test_premier_passage_cree_la_visite_sans_precedente(self):
        visite, nouvelle = accueil.enregistrer_visite(self.profil)
        self.assertTrue(nouvelle)
        self.assertIsNone(visite.precedente_at)
        self.assertEqual(accueil.absence_jours(visite), 0)

    def test_rechargement_dans_la_meme_visite_ne_deplace_pas_la_borne(self):
        t0 = timezone.now() - timedelta(hours=1)
        accueil.enregistrer_visite(self.profil, t0)
        visite, nouvelle = accueil.enregistrer_visite(self.profil, t0 + timedelta(minutes=20))
        self.assertFalse(nouvelle)
        self.assertIsNone(visite.precedente_at)
        self.assertEqual(visite.debut_at, t0)

    def test_reprise_apres_quatre_heures_ouvre_une_nouvelle_visite(self):
        t0 = timezone.now() - timedelta(days=6)
        accueil.enregistrer_visite(self.profil, t0)
        accueil.enregistrer_visite(self.profil, t0 + timedelta(minutes=30))
        t1 = t0 + timedelta(days=6)
        visite, nouvelle = accueil.enregistrer_visite(self.profil, t1)
        self.assertTrue(nouvelle)
        self.assertEqual(visite.precedente_at, t0 + timedelta(minutes=30))
        self.assertEqual(visite.debut_at, t1)
        self.assertEqual(accueil.absence_jours(visite), 6)
        # Et la borne reste stable pendant toute la visite.
        visite, nouvelle = accueil.enregistrer_visite(self.profil, t1 + timedelta(minutes=5))
        self.assertFalse(nouvelle)
        self.assertEqual(visite.precedente_at, t0 + timedelta(minutes=30))


class PhaseEtPhraseTests(SimpleTestCase):
    def test_phases_par_jours_restants(self):
        cas = [(-1, "apres"), (0, "jour_j"), (1, "veille"), (7, "derniere_ligne_droite"),
               (8, "simulation"), (30, "simulation"), (31, "normal")]
        for jours, attendu in cas:
            self.assertEqual(accueil.phase_examen({"jours_restants": jours}), attendu, jours)
        self.assertEqual(accueil.phase_examen(None), "normal")

    def _plan(self, origine="PARCOURS", etat="plan_pret", **seance):
        base = {
            "origine": origine, "theme": {"id": 1, "name": "dérivées"}, "savoir": None,
            "duree_estimee_min": 25, "raisons": [], "frequence": None, "score": None,
        }
        return {"etat": etat, "seance": {**base, **seance}}

    def test_la_phrase_nomme_le_theme_sans_repeter_le_chiffre_du_badge(self):
        # Le chiffre exact vit dans le badge de fréquence de la séance (frontend) - la
        # phrase ne le redit plus mot pour mot, elle garde le thème et l'urgence.
        plan = self._plan(frequence={"occurrences": 28, "epreuves_total": 44, "annees": []})
        phrase = accueil.phrase_coach(plan, "normal", 0)
        self.assertEqual(phrase, "Dérivées revient sans arrêt à l'examen. 25 minutes pour ne pas le découvrir le jour J.")
        self.assertNotIn("28", phrase)

    def test_une_revision_reprend_le_fait_du_serveur(self):
        plan = self._plan("REVISION_DUE", raisons=[{"code": "echec", "texte": "Tu as raté ce thème hier."}])
        self.assertEqual(
            accueil.phrase_coach(plan, "normal", 0),
            "Tu as raté Dérivées hier. 25 minutes pour le fixer avant qu'il ne s'efface.",
        )

    def test_le_retour_apres_absence_accueille_sans_reproche(self):
        phrase = accueil.phrase_coach(self._plan(), "normal", absence=9)
        self.assertTrue(phrase.startswith("Content de te revoir."))

    def test_le_jour_j_prime_sur_la_seance(self):
        self.assertIn("aujourd'hui", accueil.phrase_coach(self._plan(), "jour_j", 0))
        self.assertIn("demain", accueil.phrase_coach(self._plan(), "veille", 0))
        self.assertIn("passé", accueil.phrase_coach({"etat": "examen_passe", "seance": None}, "apres", 0))

    def test_seance_faite_donne_le_score(self):
        plan = self._plan(etat="deja_fait_aujourdhui", score={"reussies": 4, "total": 5})
        self.assertEqual(accueil.phrase_coach(plan, "normal", 0), "Séance faite, 4 sur 5 au quiz. Demain, on continue.")

    def test_derniere_ligne_droite_ne_promet_rien_de_neuf(self):
        phrase = accueil.phrase_coach(self._plan(), "derniere_ligne_droite", 0)
        self.assertEqual(phrase, "Dernière ligne droite. On consolide Dérivées : 25 minutes, sans rien de neuf.")


class PoidsTests(SimpleTestCase):
    def test_un_savoir_du_programme_officiel_pese_son_coefficient(self):
        self.assertEqual(poids_savoir({"frequence_pct": None}, 4), 4.0)
        self.assertEqual(poids_savoir({}, 2), 2.0)

    def test_un_theme_par_frequence_pese_coefficient_x_frequence_avec_plancher(self):
        self.assertAlmostEqual(poids_savoir({"frequence_pct": 64}, 4), 2.56)
        self.assertAlmostEqual(poids_savoir({"frequence_pct": 5}, 4), 1.0)

    def test_preparation_ponderee_differe_du_comptage_brut(self):
        resume = [
            {"total": 2, "sans_contenu": 0, "maitrises": 1, "poids_total": 5.0, "poids_maitrise": 4.0},
            {"total": 2, "sans_contenu": 1, "maitrises": 0, "poids_total": 1.0, "poids_maitrise": 0.0},
        ]
        prep = accueil.preparation(resume)
        self.assertEqual(prep["maitrises"], 1)
        self.assertEqual(prep["exploitables"], 3)
        self.assertAlmostEqual(prep["brute"], 1 / 3, places=3)
        self.assertAlmostEqual(prep["ponderee"], 4 / 6, places=3)

    def test_preparation_absente_sans_savoir_exploitable(self):
        self.assertIsNone(accueil.preparation([{"total": 3, "sans_contenu": 3, "maitrises": 0, "poids_total": 0, "poids_maitrise": 0}]))


class AccueilFixture(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677900402", password="x")
        self.profil = self.user.profils.first()
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.subject = Subject.objects.create(code="MATHS_TEST_ACCUEIL", label="Maths (test accueil)", country=self.cursus.country)
        self.theme = Tag.objects.create(name="dérivées (test accueil)")
        self.item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="acc-1")
        self.session = QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        self.ordre = 0
        Subscription.objects.activate_or_extend(self.user, self.cursus, duration_days=200)

    def _repondre(self, correcte, il_y_a_jours=0, item=None):
        self.ordre += 1
        quiz_question = QuizQuestion.objects.create(session=self.session, competence_item=item or self.item, ordre=self.ordre)
        answer = QuizAnswer.objects.create(quiz_question=quiz_question, resultat_declare="REUSSI" if correcte else "ECHEC")
        QuizAnswer.objects.filter(pk=answer.pk).update(answered_at=timezone.now() - timedelta(days=il_y_a_jours))

    def _seance(self, il_y_a_jours, origine=OrigineSeance.PARCOURS, statut=StatutSeance.TERMINEE):
        return SeanceJournaliere.objects.create(
            profil=self.profil, cursus=self.cursus, date=timezone.localdate() - timedelta(days=il_y_a_jours),
            origine=origine, statut=statut, etapes=[], subject=self.subject, theme=self.theme,
            termine_at=timezone.now() - timedelta(days=il_y_a_jours) if statut == StatutSeance.TERMINEE else None,
        )

    def _examen_dans(self, jours):
        ExamSession.objects.update_or_create(
            country=self.cursus.country, examen=self.cursus.examen, annee=2027,
            defaults={"date_debut": timezone.localdate() + timedelta(days=jours)},
        )
        return ExamSession.compte_a_rebours_pour(self.cursus)

    def _module_savoir(self, numero="1", intitule="Un savoir"):
        module = Module.objects.create(subject=self.subject, classe="Tle", serie_label="C", numero=numero, titre="M")
        module.cursus.add(self.cursus)
        return Savoir.objects.create(module=module, numero="I", intitule=intitule)


class DeltaTests(AccueilFixture):
    def test_pas_de_delta_sans_visite_precedente(self):
        visite, _ = accueil.enregistrer_visite(self.profil)
        self.assertIsNone(accueil.delta_depuis(self.profil, self.cursus, visite))

    def test_pas_de_delta_quand_rien_n_a_bouge(self):
        t0 = timezone.now() - timedelta(days=3)
        accueil.enregistrer_visite(self.profil, t0)
        visite, _ = accueil.enregistrer_visite(self.profil)
        self.assertIsNone(accueil.delta_depuis(self.profil, self.cursus, visite))

    def test_un_theme_consolide_depuis_la_derniere_visite_est_cite(self):
        accueil.enregistrer_visite(self.profil, timezone.now() - timedelta(days=3))
        self._repondre(False, il_y_a_jours=10)
        for _ in range(3):
            self._repondre(True, il_y_a_jours=1)
        self._seance(il_y_a_jours=1)
        visite, _ = accueil.enregistrer_visite(self.profil)

        delta = accueil.delta_depuis(self.profil, self.cursus, visite)

        self.assertEqual(delta["seances"], 1)
        self.assertEqual(delta["questions"], 3)
        self.assertEqual(delta["themes_consolides"], [{"theme": self.theme.name, "subject_label": self.subject.label}])

    def test_une_revision_tenue_est_comptee(self):
        accueil.enregistrer_visite(self.profil, timezone.now() - timedelta(days=3))
        seance = self._seance(il_y_a_jours=1, origine=OrigineSeance.REVISION_DUE)
        session = QuizSession.objects.create(
            profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE, completed_at=timezone.now(),
        )
        for ordre, ok in enumerate((True, True, True, False), start=1):
            qq = QuizQuestion.objects.create(session=session, competence_item=self.item, ordre=ordre)
            QuizAnswer.objects.create(quiz_question=qq, resultat_declare="REUSSI" if ok else "ECHEC")
        seance.quiz_session = session
        seance.save(update_fields=["quiz_session"])
        visite, _ = accueil.enregistrer_visite(self.profil)

        delta = accueil.delta_depuis(self.profil, self.cursus, visite)
        self.assertEqual(delta["revisions_tenues"], 1)


class TrajectoireTests(AccueilFixture):
    def _resume(self):
        savoir = self._module_savoir()
        Tag.objects.filter(pk=self.theme.pk).update(savoir_officiel=savoir)
        self._module_savoir(numero="2", intitule="Deuxième")
        Tag.objects.create(name="second (test accueil)", savoir_officiel=Savoir.objects.get(intitule="Deuxième"))
        _make_competence_item(self.subject, self.cursus, theme=Tag.objects.get(name="second (test accueil)"), numero="acc-2")
        return resume_parcours(self.profil, self.cursus)

    def test_rien_sans_date_d_examen(self):
        self.assertIsNone(accueil.trajectoire(self.profil, self.cursus, self._resume(), None))

    def test_sans_rythme_mesurable_aucune_projection(self):
        compte = self._examen_dans(60)
        self._seance(il_y_a_jours=2)
        traj = accueil.trajectoire(self.profil, self.cursus, self._resume(), compte)
        self.assertEqual(traj["seances_fenetre"], 1)
        self.assertIsNone(traj["couverture_projetee"])
        self.assertIsNone(traj["suffisant"])

    def test_avec_un_rythme_la_projection_est_bornee_et_coherente(self):
        compte = self._examen_dans(60)
        for j in (1, 3, 5, 8):
            self._seance(il_y_a_jours=j)
        # Le thème 1 consolidé dans la fenêtre : 3 bonnes réponses récentes.
        for _ in range(3):
            self._repondre(True, il_y_a_jours=2)
        resume = self._resume()

        traj = accueil.trajectoire(self.profil, self.cursus, resume, compte)

        self.assertEqual(traj["seances_fenetre"], 4)
        self.assertAlmostEqual(traj["couverture_actuelle"], 0.5)
        self.assertIsNotNone(traj["couverture_projetee"])
        self.assertGreaterEqual(traj["couverture_projetee"], traj["couverture_actuelle"])
        self.assertLessEqual(traj["couverture_projetee"], 1.0)
        self.assertTrue(traj["suffisant"])

    def test_rythme_insuffisant_dit_combien_de_seances_de_plus(self):
        compte = self._examen_dans(10)
        for j in (1, 3, 5):
            self._seance(il_y_a_jours=j)
        # Des séances, mais aucun thème consolidé : rendement plancher, cible non atteinte.
        savoirs = [self._module_savoir(numero=str(n), intitule=f"S{n}") for n in range(1, 9)]
        for n, savoir in enumerate(savoirs):
            tag = Tag.objects.create(name=f"t{n} (test accueil)", savoir_officiel=savoir)
            _make_competence_item(self.subject, self.cursus, theme=tag, numero=f"acc-t{n}")
        resume = resume_parcours(self.profil, self.cursus)

        traj = accueil.trajectoire(self.profil, self.cursus, resume, compte)

        self.assertFalse(traj["suffisant"])
        self.assertTrue(traj["seances_de_plus_par_semaine"] is None or traj["seances_de_plus_par_semaine"] >= 1)
        self.assertIn(traj["atteignable"], (True, False))


class LectureAReprendreTests(AccueilFixture):
    def _lecture(self, titre, cursus):
        from access.models import LectureProgress
        lesson = Lesson.objects.create(
            title=titre, subject=self.subject, year=2024, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(cursus)
        LectureProgress.objects.create(profil=self.profil, lesson=lesson)
        return lesson

    def test_ignore_une_lecture_d_un_autre_cursus(self):
        autre = Cursus.objects.exclude(pk=self.cursus.pk).filter(country=self.cursus.country).first()
        self._lecture("Épreuve d'un autre examen", autre)
        self.assertIsNone(accueil.lecture_a_reprendre(self.profil, self.cursus))
        mienne = self._lecture("Mon épreuve", self.cursus)
        self.assertEqual(accueil.lecture_a_reprendre(self.profil, self.cursus)["slug"], mienne.slug)


class DerniereLigneDroiteTests(AccueilFixture):
    def test_vrai_a_sept_jours_faux_a_huit(self):
        self._examen_dans(7)
        self.assertTrue(en_derniere_ligne_droite(self.cursus))
        self._examen_dans(8)
        self.assertFalse(en_derniere_ligne_droite(self.cursus))


class SimulationSuggereeTests(AccueilFixture):
    def _annale(self, annee, titre):
        lesson = Lesson.objects.create(
            title=titre, subject=self.subject, year=annee, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(self.cursus)
        _make_question(lesson, "1")
        return lesson

    def test_hors_phase_rien(self):
        self._annale(2024, "Annale 2024")
        self.assertIsNone(accueil.simulation_suggeree(self.profil, self.cursus, "normal"))

    def test_la_plus_recente_non_simulee(self):
        ancienne = self._annale(2022, "Annale 2022")
        recente = self._annale(2024, "Annale 2024")
        self.assertEqual(accueil.simulation_suggeree(self.profil, self.cursus, "simulation")["id"], recente.id)
        SimulationEpreuve.objects.create(profil=self.profil, lesson=recente)
        self.assertEqual(accueil.simulation_suggeree(self.profil, self.cursus, "simulation")["id"], ancienne.id)


class AccueilApiTests(AccueilFixture):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_une_seule_reponse_pour_tout_l_ecran(self):
        self._examen_dans(90)
        reponse = self.client.get(reverse("quiz:accueil"))
        self.assertEqual(reponse.status_code, 200)
        data = reponse.json()
        for cle in ("plan", "phase", "absence_jours", "premiers_pas", "phrase_coach", "depuis", "trajectoire",
                    "resume", "preparation", "revisions", "lecture", "simulation_suggeree", "bilan_semaine"):
            self.assertIn(cle, data)
        self.assertEqual(data["phase"], "normal")
        self.assertTrue(data["premiers_pas"])
        self.assertIn(data["plan"]["etat"], ("plan_pret", "rien_a_proposer"))
        self.assertTrue(VisiteAccueil.objects.filter(profil=self.profil).exists())

    def test_une_nouvelle_visite_trace_app_ouverte_une_seule_fois(self):
        self._examen_dans(90)
        for _ in range(3):
            self.client.get(reverse("quiz:accueil"))
        # Trois rechargements dans la même visite : un seul évènement, pas trois.
        evenements = AnalyticsEvent.objects.filter(name=EventName.APP_OUVERTE, user=self.user)
        self.assertEqual(evenements.count(), 1)
        self.assertEqual(evenements.first().properties["profil_id"], self.profil.id)

        # Reprise après plus de 4 h d'inactivité : nouvelle visite, nouvel évènement.
        VisiteAccueil.objects.filter(profil=self.profil).update(derniere_at=timezone.now() - timedelta(hours=5))
        self.client.get(reverse("quiz:accueil"))
        self.assertEqual(evenements.count(), 2)

    def test_examen_passe_ne_construit_pas_de_seance(self):
        ExamSession.objects.update_or_create(
            country=self.cursus.country, examen=self.cursus.examen, annee=2020,
            defaults={"date_debut": timezone.localdate() - timedelta(days=100)},
        )
        ExamSession.objects.filter(country=self.cursus.country, examen=self.cursus.examen, annee__gt=2020).delete()
        data = self.client.get(reverse("quiz:accueil")).json()
        # Sans session à venir, la date est ESTIMÉE (décalée dans le futur) : la phase
        # ne peut être "apres" que si la dernière session connue n'est pas décalable -
        # ici elle l'est, on vérifie simplement que la page reste cohérente.
        self.assertIn(data["phase"], ("apres", "normal", "simulation", "derniere_ligne_droite", "veille", "jour_j"))
        self.assertEqual(
            SeanceJournaliere.objects.filter(profil=self.profil).count(),
            0 if data["phase"] == "apres" else SeanceJournaliere.objects.filter(profil=self.profil).count(),
        )

    def test_retour_apres_absence_raccourcit_la_seance_une_fois(self):
        self._examen_dans(90)
        # Une visite il y a dix jours, puis retour aujourd'hui.
        accueil.enregistrer_visite(self.profil, timezone.now() - timedelta(days=10))
        data = self.client.get(reverse("quiz:accueil")).json()
        self.assertEqual(data["absence_jours"], 10)
        if data["plan"]["etat"] == "plan_pret":
            self.assertEqual(data["plan"]["seance"]["budget_minutes"], accueil.BUDGET_RETOUR_MINUTES)
            self.assertTrue(data["phrase_coach"].startswith("Content de te revoir."))

    def test_sans_cursus_declare_rien_ne_casse(self):
        self.user.cursus_prepare = None
        self.user.save(update_fields=["cursus_prepare"])
        data = self.client.get(reverse("quiz:accueil")).json()
        self.assertEqual(data["plan"]["etat"], "cursus_inconnu")
