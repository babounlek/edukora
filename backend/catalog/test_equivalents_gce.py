from django.test import TestCase
from django.urls import reverse

from inedit.models import Blueprint, EpreuveInedite

from .models import (
    EQUIVALENTS_GCE,
    Cours,
    Cursus,
    Examen,
    Langue,
    Lesson,
    LessonType,
    Origine,
    StatutContenu,
    Subject,
)


class EquivalentsGceTests(TestCase):
    """Matières jumelles (affichage seulement) et listes filtrées par langue d'interface."""

    def setUp(self):
        self.gce = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        self.bac = Cursus.objects.filter(country__code="CM", examen=Examen.BAC).first()
        self.maths_gce = Subject.objects.get(country__code="CM", code="GCE_MATHS")
        self.maths_fr = Subject.objects.get(country__code="CM", code="MATHS")
        self.l_gce = self._lesson(self.maths_gce, self.gce, "Mathematics GCE test")
        self.l_fr = self._lesson(self.maths_fr, self.bac, "Mathématiques BAC test")

    def _lesson(self, subject, cursus, titre):
        lesson = Lesson.objects.create(
            title=titre, subject=subject, year=2024, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(cursus)
        return lesson

    def _codes_matieres(self, **params):
        reponse = self.client.get(reverse("catalog:subject-list"), {"country": "cm", **params})
        self.assertEqual(reponse.status_code, 200)
        return {s["code"] for s in reponse.json()}

    # -- données ------------------------------------------------------------------------------------------

    def test_la_base_suit_la_table_des_equivalents(self):
        for code, equivalent in EQUIVALENTS_GCE.items():
            self.assertEqual(Subject.objects.get(country__code="CM", code=code).equivalent_code, equivalent, code)

    def test_chaque_equivalent_existe_comme_matiere_francophone(self):
        existants = set(Subject.objects.filter(country__code="CM", langue=Langue.FR).values_list("code", flat=True))
        self.assertEqual(set(EQUIVALENTS_GCE.values()) - existants, set())

    def test_les_matieres_francophones_n_ont_pas_de_jumelle(self):
        self.assertEqual(Subject.objects.filter(langue=Langue.FR).exclude(equivalent_code="").count(), 0)

    # -- liste des matières ---------------------------------------------------------------------------------

    def test_sans_filtre_les_deux_langues_apparaissent(self):
        codes = self._codes_matieres()
        self.assertIn("MATHS", codes)
        self.assertIn("GCE_MATHS", codes)

    def test_langue_fr_ne_garde_que_les_matieres_francophones(self):
        codes = self._codes_matieres(langue="fr")
        self.assertIn("MATHS", codes)
        self.assertFalse({c for c in codes if c.startswith("GCE_")})

    def test_langue_en_ne_garde_que_les_matieres_anglophones(self):
        codes = self._codes_matieres(langue="en")
        self.assertEqual(codes, {"GCE_MATHS"})

    def test_all_ou_valeur_inconnue_ne_filtrent_pas(self):
        for valeur in ("all", "toutes", "de"):
            codes = self._codes_matieres(langue=valeur)
            self.assertTrue({"MATHS", "GCE_MATHS"} <= codes, valeur)

    def test_un_examen_choisi_prime_sur_la_langue(self):
        # Le cursus du GCE fixe déjà la langue : ?langue=fr ne doit pas vider sa liste.
        codes = self._codes_matieres(cursus=self.gce.id, langue="fr")
        self.assertEqual(codes, {"GCE_MATHS"})

    def test_la_matiere_expose_sa_langue_et_sa_jumelle(self):
        reponse = self.client.get(reverse("catalog:subject-list"), {"country": "cm", "langue": "en"})
        (ligne,) = reponse.json()
        self.assertEqual(ligne["langue"], "en")
        self.assertEqual(ligne["equivalent_code"], "MATHS")

    # -- listes d'épreuves et de cours ---------------------------------------------------------------------

    def _titres_epreuves(self, **params):
        reponse = self.client.get(reverse("catalog:lesson-list"), {"country": "cm", **params})
        self.assertEqual(reponse.status_code, 200)
        return {e["title"] for e in reponse.json()["results"]}

    def test_epreuves_filtrees_par_langue_sans_examen(self):
        self.assertEqual(self._titres_epreuves(langue="en"), {"Mathematics GCE test"})
        self.assertEqual(self._titres_epreuves(langue="fr"), {"Mathématiques BAC test"})
        self.assertEqual(self._titres_epreuves(), {"Mathematics GCE test", "Mathématiques BAC test"})

    def test_les_inedites_suivent_la_langue_et_le_total(self):
        """Régression : build_inedit_queryset ignorait ?langue=, donc les inédites françaises gonflaient
        la liste et le total (count) d'un élève en anglais."""
        blueprint = Blueprint.objects.create(
            subject=self.maths_fr, titre="Blueprint langue",
            sections_plan=[{"section": "Exercice 1", "points": 20}], duree_minutes=120, bareme_total=20,
            statut=StatutContenu.VALIDE,
        )
        blueprint.cursus.set([self.bac])
        inedite = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=self.maths_fr, titre="Inédite BAC test", statut=StatutContenu.VALIDE,
        )
        inedite.cursus.set([self.bac])

        def liste(**params):
            reponse = self.client.get(reverse("catalog:lesson-list"), {"country": "cm", **params})
            self.assertEqual(reponse.status_code, 200)
            donnees = reponse.json()
            return donnees["count"], {e["title"] for e in donnees["results"]}

        self.assertEqual(liste(langue="en"), (1, {"Mathematics GCE test"}))
        self.assertEqual(liste(langue="fr"), (2, {"Mathématiques BAC test", "Inédite BAC test"}))
        self.assertEqual(liste()[0], 3)
        # Un examen choisi prime sur la langue, inédites comprises.
        self.assertEqual(liste(cursus=self.bac.id, langue="en")[0], 2)

    def test_chaque_examen_expose_sa_langue(self):
        """Le frontend ne propose que les examens de la langue de l'interface : GCE -> en, tout le reste -> fr."""
        reponse = self.client.get(reverse("catalog:cursus-list"), {"country": "cm"})
        self.assertEqual(reponse.status_code, 200)
        par_examen = {c["examen"]: c["langue"] for c in reponse.json()}
        self.assertEqual(par_examen[Examen.GCE_OL], "en")
        self.assertEqual(par_examen[Examen.BAC], "fr")
        for examen, langue in par_examen.items():
            self.assertEqual(langue, "en" if examen in (Examen.GCE_OL, Examen.GCE_AL) else "fr", examen)

    def test_le_total_annonce_par_une_puce_egale_les_lignes_de_la_liste(self):
        """Une puce « N épreuves / N cours » d'accueil appelle la liste avec la langue de l'interface :
        son `count` doit être exactement ce que la page de liste affichera, dans chaque langue."""
        for subject, cursus, slug in ((self.maths_gce, self.gce, "gce"), (self.maths_fr, self.bac, "bac")):
            for i in range(2):
                cours = Cours.objects.create(
                    titre=f"Cours {slug} {i}", subject=subject, statut=StatutContenu.VALIDE,
                    external_id=f"coherence-{slug}-{i}",
                )
                cours.cursus.add(cursus)

        for nom, langue, attendu in (("lesson-list", "en", 1), ("lesson-list", "fr", 1), ("cours-list", "en", 2), ("cours-list", "fr", 2)):
            donnees = self.client.get(reverse(f"catalog:{nom}"), {"country": "cm", "langue": langue}).json()
            self.assertEqual(donnees["count"], len(donnees["results"]), (nom, langue))
            self.assertEqual(donnees["count"], attendu, (nom, langue))
            codes = {ligne["subject"]["code"] for ligne in donnees["results"]}
            self.assertEqual(codes, {"GCE_MATHS"} if langue == "en" else {"MATHS"}, (nom, langue))

        # Le bas de page (/catalog/stats/) annonce les mêmes totaux que ces listes, dans chaque langue.
        for langue, corriges, cours in (("en", 1, 2), ("fr", 1, 2), (None, 2, 4)):
            params = {"langue": langue} if langue else {}
            stats = self.client.get(reverse("catalog:platform-stats"), params).json()
            self.assertEqual((stats["corriges_disponibles"], stats["cours_disponibles"]), (corriges, cours), langue)

    def test_epreuves_un_examen_choisi_prime_sur_la_langue(self):
        self.assertEqual(self._titres_epreuves(cursus=self.gce.id, langue="fr"), {"Mathematics GCE test"})

    def test_cours_filtres_par_langue_sans_examen(self):
        for subject, cursus, titre in ((self.maths_gce, self.gce, "Cours GCE"), (self.maths_fr, self.bac, "Cours BAC")):
            cours = Cours.objects.create(
                titre=titre, subject=subject, statut=StatutContenu.VALIDE, external_id=f"cours-{subject.code}",
            )
            cours.cursus.add(cursus)

        def titres(**params):
            reponse = self.client.get(reverse("catalog:cours-list"), {"country": "cm", **params})
            self.assertEqual(reponse.status_code, 200)
            return {c["titre"] for c in reponse.json()["results"]}

        self.assertEqual(titres(langue="en"), {"Cours GCE"})
        self.assertEqual(titres(langue="fr"), {"Cours BAC"})
        self.assertEqual(titres(), {"Cours GCE", "Cours BAC"})
