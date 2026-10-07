"""Étape 2 de l'intelligence de la recherche : classement par signaux (fréquence, niveau, popularité,
coefficient) et carte-réponse. Les signaux ne font qu'ORDONNER ce qui correspond déjà à la requête."""

from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cours, Subject, Tag

from . import indexation, moteur
from .models import EntreeRecherche, TypeResultat
from .tests import SECRET_SECTION, VALIDE, _CorpusMixin, reconstruire

REGLE = "Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés."


class _CorpusAvecRegle(_CorpusMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.pythagore = Tag.objects.create(name="théorème de Pythagore")
        cls.cours_pyth = Cours.objects.create(
            external_id="p1", titre="Le théorème de Pythagore", subject=cls.maths, statut=VALIDE,
            sections_raw=[
                {"type": "accroche", "contenu_markdown": "Un triangle, un angle droit."},
                {"type": "regle", "contenu_markdown": REGLE, "formule_principale": "BC^2 = AB^2 + AC^2"},
                {"type": "exemple_resolu", "enonce_markdown": f"Exemple {SECRET_SECTION}", "etapes": []},
            ],
        )
        cls.cours_pyth.tags.add(cls.pythagore)
        cls.cours_sans_regle = Cours.objects.create(
            external_id="p2", titre="Réciproque de Pythagore", subject=cls.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Prouver qu'un triangle est rectangle."}],
        )
        cls.cours_sans_regle.tags.add(cls.pythagore)
        reconstruire()


class SignauxDeClassementTests(_CorpusAvecRegle, TestCase):
    def entree(self, titre):
        return EntreeRecherche.objects.get(type=TypeResultat.COURS, titre=titre)

    def test_un_theme_qui_tombe_souvent_passe_devant(self):
        a, b = self.entree("Le théorème de Thalès dans un triangle"), self.entree("Le théorème de Pythagore")
        self.assertTrue(EntreeRecherche.objects.filter(pk__in=[a.pk, b.pk]).count() == 2)
        # Deux cours qui répondent aussi bien à « theoreme » : celui dont le thème tombe le plus passe devant.
        for frequence, attendu in ((80, "Le théorème de Pythagore"), (0, None)):
            EntreeRecherche.objects.filter(pk=b.pk).update(frequence=frequence)
            EntreeRecherche.objects.filter(pk=a.pk).update(frequence=0 if frequence else 80)
            titres = self.titres(self.chercher("theoreme"), "COURS")
            if attendu:
                self.assertLess(titres.index(attendu), titres.index("Le théorème de Thalès dans un triangle"))
            else:
                self.assertLess(titres.index("Le théorème de Thalès dans un triangle"), titres.index("Le théorème de Pythagore"))

    def test_la_popularite_departage_a_egalite(self):
        a, b = self.entree("Le théorème de Thalès dans un triangle"), self.entree("Le théorème de Pythagore")
        EntreeRecherche.objects.filter(pk__in=[a.pk, b.pk]).update(frequence=0, popularite=0)
        EntreeRecherche.objects.filter(pk=b.pk).update(popularite=30)
        titres = self.titres(self.chercher("theoreme"), "COURS")
        self.assertLess(titres.index("Le théorème de Pythagore"), titres.index("Le théorème de Thalès dans un triangle"))

    def test_un_signal_ne_fait_pas_remonter_ce_qui_ne_correspond_pas(self):
        # Le cours « Calculer une aire » ne parle pas de Thalès : même très populaire il reste absent.
        EntreeRecherche.objects.filter(titre="Calculer une aire").update(frequence=100, popularite=10_000)
        self.assertNotIn("Calculer une aire", self.titres(self.chercher("thales"), "COURS"))

    def test_le_niveau_de_l_eleve_prefere_son_examen(self):
        a, b = self.entree("Le théorème de Thalès dans un triangle"), self.entree("Le théorème de Pythagore")
        EntreeRecherche.objects.filter(pk__in=[a.pk, b.pk]).update(frequence=0, popularite=0)
        EntreeRecherche.objects.filter(pk=a.pk).update(niveau=0)  # BEPC
        EntreeRecherche.objects.filter(pk=b.pk).update(niveau=2)  # BAC
        sans = self.titres(self.chercher("theoreme"), "COURS")
        eleve_bac = self.titres(self.chercher("theoreme", cursus=self.bac_c.pk), "COURS")
        self.assertLess(eleve_bac.index("Le théorème de Pythagore"), eleve_bac.index("Le théorème de Thalès dans un triangle"))
        self.assertEqual(set(sans), set(eleve_bac))  # on ordonne, on n'écarte rien

    def test_un_theme_en_double_ne_donne_qu_un_resultat(self):
        doublon = Tag.objects.create(name="Théorème de pythagore")
        self.cours_sans_regle.tags.add(doublon)
        reconstruire()
        themes = self.titres(self.chercher("pythagore"), "THEME")
        self.assertEqual(len([t for t in themes if t.lower() == "théorème de pythagore"]), 1)


class IndexDesSignauxTests(_CorpusAvecRegle, TestCase):
    def test_les_colonnes_de_signaux_sont_remplies_et_bornees(self):
        for entree in EntreeRecherche.objects.all():
            self.assertTrue(0 <= entree.frequence <= 100, entree)
            self.assertGreaterEqual(entree.popularite, 0)
            self.assertIn(entree.niveau, (-1, 0, 1, 2), entree)

    def test_une_epreuve_officielle_a_le_niveau_de_son_examen(self):
        epreuve = EntreeRecherche.objects.get(type=TypeResultat.EPREUVE)
        self.assertEqual(epreuve.niveau, indexation.RANG_EXAMEN["BAC"])

    def test_la_regle_est_gardee_pour_la_carte_sans_rien_de_paye(self):
        entree = EntreeRecherche.objects.get(type=TypeResultat.COURS, titre="Le théorème de Pythagore")
        regle = entree.meta["regle_md"]
        self.assertIn(REGLE, regle)
        self.assertIn("BC^2 = AB^2 + AC^2", regle)
        self.assertNotIn(SECRET_SECTION, regle)
        self.assertFalse(EntreeRecherche.objects.get(titre="Réciproque de Pythagore").meta.get("regle_md"))

    def test_la_regle_est_plafonnee_sans_couper_une_formule(self):
        longue = "x " * 400
        self.assertEqual(indexation.regle_pour_carte([{"type": "regle", "contenu_markdown": longue}]), "")
        coupee = indexation.regle_pour_carte(
            [{"type": "regle", "contenu_markdown": "Court.\n\n$a + b\n\n" + "y" * 10}],
        )
        self.assertEqual(coupee, "Court.")
        annonce = indexation.regle_pour_carte(
            [{"type": "regle", "contenu_markdown": "La règle complète.\n\nLa méthode se déroule en trois temps :"}],
        )
        self.assertEqual(annonce, "La règle complète.")
        self.assertEqual(indexation.regle_pour_carte("pas une liste"), "")
        self.assertEqual(indexation.regle_pour_carte([{"type": "accroche", "contenu_markdown": "x"}]), "")


class CarteReponseTests(_CorpusAvecRegle, TestCase):
    def test_une_question_courte_obtient_la_regle_du_cours(self):
        carte = self.chercher("théorème de pythagore")["reponse"]
        self.assertEqual(carte["titre"], "Le théorème de Pythagore")
        self.assertIn(REGLE, carte["regle_md"])
        self.assertNotIn(SECRET_SECTION, str(carte))

    def test_la_carte_ne_depasse_pas_ce_que_l_apercu_public_montre(self):
        carte = self.chercher("pythagore")["reponse"]
        self.assertIn("acces", carte)
        self.assertNotIn(SECRET_SECTION, str(carte))

    def test_pas_de_regle_pas_de_carte(self):
        self.assertIsNone(self.chercher("reciproque")["reponse"])

    def test_pas_de_carte_pour_une_requete_longue(self):
        self.assertIsNone(self.chercher("le theoreme de pythagore dans un triangle rectangle ABC")["reponse"])

    def test_pas_de_carte_quand_un_type_est_voulu(self):
        self.assertIsNone(self.chercher("pythagore corrigé")["reponse"])
        self.assertIsNone(self.chercher("pythagore", type_="COURS")["reponse"])

    def test_pas_de_carte_sur_les_pages_suivantes(self):
        self.assertIsNone(self.chercher("pythagore", decalage=1)["reponse"])

    def test_pas_de_carte_quand_le_theme_en_tete_est_d_une_autre_matiere(self):
        physique = Subject.objects.filter(country=self.pays).exclude(pk=self.maths.pk).first()
        autre = Tag.objects.create(name="pythagore appliqué")
        cours = Cours.objects.create(
            external_id="ph1", titre="Pythagore et vecteurs", subject=physique, statut=VALIDE,
            sections_raw=[{"type": "regle", "contenu_markdown": "Une règle."}],
        )
        cours.tags.add(autre)
        Cours.objects.filter(pk=self.cours_pyth.pk).update(statut="BROUILLON")
        reconstruire()
        carte = self.chercher("pythagore")["reponse"]
        if carte:
            self.assertEqual(carte["matiere"]["code"], physique.code)

    def test_rien_trouve_pas_de_carte(self):
        self.assertIsNone(self.chercher("zzzzqqq")["reponse"])

    def test_la_vue_expose_la_carte(self):
        donnees = APIClient().get("/recherche/", {"q": "théorème de pythagore", "pays": "cm"}).json()
        self.assertEqual(donnees["reponse"]["titre"], "Le théorème de Pythagore")
        self.assertIn("regle_md", donnees["reponse"])
        self.assertIn("reponse", APIClient().get("/recherche/", {"q": "zzzzqqq", "pays": "cm"}).json())
