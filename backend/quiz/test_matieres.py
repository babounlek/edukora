from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cursus, Difficulte, Examen, Lesson, LessonType, Origine, StatutContenu, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from .matieres import matieres_disponibles, restreindre_items, restreindre_matieres
from .models import ModeQuiz
from .priorites import priorites_examen
from .services import (
    _subjects_par_priorite, generer_session, matieres_pour_objectif, resume_parcours,
)
from .tests import _make_competence_item


class _Base(TestCase):
    """Un élève du GCE A Level (pas de séries) devant plusieurs matières."""

    def setUp(self):
        self.cursus = Cursus.objects.get(examen=Examen.GCE_AL, series__isnull=True)
        self.user = User.objects.create_user(phone_number="677400101", password="x")
        self.profil = self.user.profils.first()
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.compteur = 0
        self.maths = self._matiere("GCE_MATHS")
        self.physique = self._matiere("GCE_PHYSICS")
        self.histoire = self._matiere("GCE_HISTORY")

    def _matiere(self, code, nb_items=4):
        subject = Subject.objects.get(country=self.cursus.country, code=code)
        lesson = Lesson.objects.create(
            title=f"Paper {code}", subject=subject, year=2025, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(self.cursus)
        for _ in range(nb_items):
            self.compteur += 1
            _make_competence_item(
                subject, self.cursus, theme=Tag.objects.create(name=f"theme-{code}-{self.compteur}"),
                difficulte=Difficulte.MOYENNE, numero=str(self.compteur),
            )
        return subject

    def _choisir(self, *subjects):
        self.profil.matieres_passees.set(subjects)


class RestreindreTests(_Base):
    def test_sans_choix_tout_le_cursus(self):
        sujets = [self.maths, self.physique, self.histoire]
        self.assertEqual(restreindre_matieres(self.profil, sujets), sujets)
        self.assertEqual(restreindre_matieres(None, sujets), sujets)

    def test_un_choix_limite_aux_matieres_declarees_en_gardant_l_ordre(self):
        self._choisir(self.maths, self.histoire)
        resultat = restreindre_matieres(self.profil, [self.histoire, self.physique, self.maths])
        self.assertEqual(resultat, [self.histoire, self.maths])

    def test_un_choix_qui_ne_recoupe_rien_est_ignore(self):
        autre = Subject.objects.get(country=self.cursus.country, code="GCE_BIOLOGY")
        self._choisir(autre)
        sujets = [self.maths, self.physique]
        self.assertEqual(restreindre_matieres(self.profil, sujets), sujets)

    def test_items_du_diagnostic(self):
        class Item:
            def __init__(self, subject_id):
                self.subject_id = subject_id

        items = [Item(self.maths.id), Item(self.physique.id), Item(self.histoire.id)]
        self._choisir(self.physique)
        self.assertEqual([i.subject_id for i in restreindre_items(self.profil, items)], [self.physique.id])

    def test_matieres_disponibles_seulement_avec_du_contenu(self):
        codes = {m.code for m in matieres_disponibles(self.cursus)}
        self.assertEqual(codes, {"GCE_MATHS", "GCE_PHYSICS", "GCE_HISTORY"})


class CoachRespecteLesMatieresTests(_Base):
    def test_plan_du_jour_ne_retient_que_les_matieres_choisies(self):
        self.assertEqual({s.id for s in _subjects_par_priorite(self.profil, self.cursus)},
                         {self.maths.id, self.physique.id, self.histoire.id})
        self._choisir(self.maths, self.physique)
        self.assertEqual({s.id for s in _subjects_par_priorite(self.profil, self.cursus)},
                         {self.maths.id, self.physique.id})

    def test_objectif_de_la_semaine_propose_les_matieres_choisies(self):
        self._choisir(self.histoire)
        self.assertEqual([m.id for m in matieres_pour_objectif(self.cursus, self.profil)], [self.histoire.id])
        # Sans profil, toutes celles qui ont une banque de quiz.
        self.assertEqual(len(matieres_pour_objectif(self.cursus)), 3)

    def test_priorites_de_l_examen(self):
        self._choisir(self.maths)
        lignes = priorites_examen(self.profil, self.cursus)["matieres"]
        self.assertEqual([ligne["subject_id"] for ligne in lignes], [self.maths.id])
        self._choisir()
        self.assertEqual(len(priorites_examen(self.profil, self.cursus)["matieres"]), 3)

    def test_progression_par_matiere(self):
        self._choisir(self.physique)
        # Sans programme officiel, ces matières n'ont pas de ligne de progression : on vérifie
        # seulement que le résumé ne montre jamais une matière que l'élève n'a pas choisie.
        ids = {ligne["subject_id"] for ligne in resume_parcours(self.profil, self.cursus)}
        self.assertTrue(ids <= {self.physique.id})

    def test_diagnostic_n_interroge_que_les_matieres_choisies(self):
        self._choisir(self.maths, self.physique)
        session = generer_session(self.profil, self.cursus, ModeQuiz.DIAGNOSTIC, n=6)
        sujets = {qq.competence_item.subject_id for qq in session.quiz_questions.all()}
        self.assertEqual(sujets, {self.maths.id, self.physique.id})

    def test_un_eleve_du_bac_sans_choix_ne_change_pas(self):
        bac = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        sujet = Subject.objects.create(code="plain", label="Plain", country=bac.country)
        lesson = Lesson.objects.create(
            title="Épreuve plain", subject=sujet, year=2024, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(bac)
        self.assertEqual([s.id for s in _subjects_par_priorite(self.profil, bac)], [sujet.id])


class MatieresApiTests(_Base):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_liste_les_matieres_disponibles(self):
        reponse = self.client.get("/quiz/matieres/")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["choisies"], [])
        self.assertEqual({m["code"] for m in reponse.data["disponibles"]}, {"GCE_MATHS", "GCE_PHYSICS", "GCE_HISTORY"})

    def test_put_enregistre_le_choix(self):
        reponse = self.client.put("/quiz/matieres/", {"matieres": [self.maths.id, self.physique.id]}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["choisies"], sorted([self.maths.id, self.physique.id]))
        self.assertEqual(set(self.profil.matieres_passees.values_list("id", flat=True)), {self.maths.id, self.physique.id})

    def test_put_vide_revient_a_toutes_les_matieres(self):
        self._choisir(self.maths)
        reponse = self.client.put("/quiz/matieres/", {"matieres": []}, format="json")
        self.assertEqual(reponse.data["choisies"], [])
        self.assertFalse(self.profil.matieres_passees.exists())

    def test_put_refuse_une_matiere_sans_contenu_sur_ce_cursus(self):
        biologie = Subject.objects.get(country=self.cursus.country, code="GCE_BIOLOGY")
        reponse = self.client.put("/quiz/matieres/", {"matieres": [biologie.id]}, format="json")
        self.assertEqual(reponse.status_code, 400)
        self.assertFalse(self.profil.matieres_passees.exists())

    def test_put_refuse_une_charge_invalide(self):
        for charge in ({"matieres": "maths"}, {"matieres": [True]}, {}):
            self.assertEqual(self.client.put("/quiz/matieres/", charge, format="json").status_code, 400)

    def test_le_choix_d_un_autre_examen_est_preserve(self):
        bac = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        autre = Subject.objects.create(code="ancien", label="Ancien", country=bac.country)
        self.profil.matieres_passees.add(autre)
        self.client.put("/quiz/matieres/", {"matieres": [self.maths.id]}, format="json")
        self.assertEqual(
            set(self.profil.matieres_passees.values_list("id", flat=True)), {autre.id, self.maths.id},
        )

    def test_sans_cursus_declare(self):
        self.user.cursus_prepare = None
        self.user.save(update_fields=["cursus_prepare"])
        self.assertEqual(self.client.get("/quiz/matieres/").status_code, 400)

    def test_anonyme_refuse(self):
        self.assertIn(APIClient().get("/quiz/matieres/").status_code, (401, 403))
