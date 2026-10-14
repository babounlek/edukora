"""
Les cours d'un examen (voir CoursListView et SubjectListView, règle q_cours_du_cursus) : ses cours directs, ses cours
recommandés et, pour la grande majorité qui n'a aucun examen rattaché, ceux dont une épreuve source est de cet examen.
Avant, la liste gardait TOUS les cours sans examen : 7 580 « cours » pour le BEPC, dont des leçons de niveau BAC.
"""
from django.test import TestCase
from django.urls import reverse

from .models import (
    Cours,
    Cursus,
    Examen,
    Exercise,
    Lesson,
    LessonType,
    Origine,
    RappelDeMethode,
    StatutContenu,
    Subject,
)


class CoursParExamenTests(TestCase):
    def setUp(self):
        self.bepc = Cursus.objects.get(country__code="CM", examen=Examen.BEPC, series__isnull=True)
        self.bac_c = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")

        # Une épreuve du BEPC et une du BAC C, chacune avec un exercice qui porte un rappel vers un cours.
        self.cours_source_bepc = self._cours_avec_source("Fractions (source BEPC)", self.bepc)
        self.cours_source_bac = self._cours_avec_source("Dérivées (source BAC C)", self.bac_c)
        # Un cours sans aucune épreuve source : proposé à tous les examens.
        self.cours_orphelin = self._cours("Notion sans source")
        # Un cours rattaché directement au BEPC, un cours recommandé pour lui.
        self.cours_direct = self._cours("Direct BEPC", cursus=self.bepc)
        self.cours_recommande = self._cours("Recommandé BEPC")
        self.cours_recommande.cursus_recommandes.add(self.bepc)

    def _cours(self, titre, cursus=None):
        cours = Cours.objects.create(
            external_id=f"ext-{titre}", titre=titre, subject=self.maths, statut=StatutContenu.VALIDE,
        )
        if cursus is not None:
            cours.cursus.add(cursus)
        return cours

    def _cours_avec_source(self, titre, cursus):
        cours = self._cours(titre)
        lesson = Lesson.objects.create(
            title=f"Épreuve {titre}", subject=self.maths, year=2024, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(cursus)
        exercice = Exercise.objects.create(lesson=lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
        RappelDeMethode.objects.create(
            exercise=exercice, external_id=f"rdm-{titre}", competence="x", contenu_markdown="x", cours=cours,
        )
        return cours

    def _titres(self, **params):
        reponse = self.client.get(reverse("catalog:cours-list"), {"country": "cm", **params})
        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.json()
        self.assertEqual(donnees["count"], len(donnees["results"]))
        return {c["titre"] for c in donnees["results"]}

    def test_la_liste_d_un_examen_suit_la_lignee_des_cours(self):
        titres = self._titres(cursus=self.bepc.id)

        self.assertEqual(titres, {"Fractions (source BEPC)", "Notion sans source", "Direct BEPC", "Recommandé BEPC"})

    def test_un_cours_d_un_autre_examen_n_entre_pas_dans_la_liste(self):
        self.assertNotIn("Dérivées (source BAC C)", self._titres(cursus=self.bepc.id))
        self.assertIn("Dérivées (source BAC C)", self._titres(cursus=self.bac_c.id))
        self.assertNotIn("Fractions (source BEPC)", self._titres(cursus=self.bac_c.id))

    def test_sans_examen_tous_les_cours_restent_listes(self):
        titres = self._titres()

        self.assertTrue({"Fractions (source BEPC)", "Dérivées (source BAC C)", "Notion sans source"} <= titres)

    def test_la_pastille_d_une_matiere_compte_comme_la_liste_qu_elle_ouvre(self):
        for cursus in (self.bepc, self.bac_c):
            matieres = self.client.get(
                reverse("catalog:subject-list"), {"country": "cm", "cursus": cursus.id, "langue": "fr"},
            ).json()
            pastille = next(m for m in matieres if m["code"] == "MATHS")["cours_count"]
            liste = self.client.get(
                reverse("catalog:cours-list"), {"country": "cm", "cursus": cursus.id, "subject": "MATHS"},
            ).json()["count"]
            self.assertEqual(pastille, liste, cursus.examen)
            self.assertGreater(liste, 0)

    def test_un_examen_du_gce_ne_propose_aucune_matiere_francaise_meme_avec_des_cours_sans_source(self):
        """Régression : un cours français sans épreuve source est proposé à tout examen ; ses matières ne doivent pas
        remonter sous un examen du GCE (558 « cours » dans les pastilles pour 119 dans la liste)."""
        gce = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        maths_gce = Subject.objects.get(country__code="CM", code="GCE_MATHS")
        cours_gce = Cours.objects.create(
            external_id="ext-gce", titre="GCE lesson", subject=maths_gce, statut=StatutContenu.VALIDE,
        )
        cours_gce.cursus.add(gce)

        matieres = self.client.get(reverse("catalog:subject-list"), {"country": "cm", "cursus": gce.id}).json()

        self.assertEqual({m["code"] for m in matieres}, {"GCE_MATHS"})
        self.assertEqual(sum(m["cours_count"] for m in matieres), 1)
        liste = self.client.get(reverse("catalog:cours-list"), {"country": "cm", "cursus": gce.id}).json()
        self.assertEqual(liste["count"], 1)
