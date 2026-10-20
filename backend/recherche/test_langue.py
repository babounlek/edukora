"""
Recherche et langue de l'interface (voir recherche.moteur.chercher) : sans examen visé, seuls les contenus de la
langue demandée sont cherchés ; `autre_langue` dit ce que l'autre langue aurait ; un examen visé fixe la langue.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cours, Cursus, Examen, StatutContenu, Subject, Tag

from . import moteur
from .indexation import reconstruire
from .models import EntreeRecherche, RechercheSansResultat, TypeResultat
from .tests import _CorpusMixin

EN_COURS = "Thales and similar triangles"
FR_THEME = "théorème de Thalès"
EN_THEME = "similar triangles"


class _CorpusBilingue(_CorpusMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.maths_gce = Subject.objects.get(country=cls.pays, code="GCE_MATHS")
        cls.gce = Cursus.objects.get(country=cls.pays, examen=Examen.GCE_OL, series__isnull=True)
        cls.cours_en = Cours.objects.create(
            external_id="c-en", titre=EN_COURS, subject=cls.maths_gce, statut=StatutContenu.VALIDE,
        )
        cls.cours_en.cursus.add(cls.gce)
        # Un thème n'est indexé qu'avec un quiz ou au moins deux contenus (voir indexation.THEME_MIN_CONTENUS).
        autre_cours_en = Cours.objects.create(
            external_id="c-en-2", titre="Similarity and scale factors", subject=cls.maths_gce, statut=StatutContenu.VALIDE,
        )
        autre_cours_en.cursus.add(cls.gce)
        theme_en = Tag.objects.create(name=EN_THEME)
        cls.cours_en.tags.add(theme_en)
        autre_cours_en.tags.add(theme_en)
        reconstruire()


class LangueMoteurTests(_CorpusBilingue, TestCase):
    def test_en_anglais_seul_le_contenu_anglais_est_cherche(self):
        reponse = self.chercher("thales", langue="en")

        self.assertEqual(self.titres(reponse, TypeResultat.COURS), [EN_COURS])
        self.assertEqual(reponse["langue"], "en")

    def test_en_francais_le_contenu_anglais_est_ecarte(self):
        reponse = self.chercher("thales", langue="fr")

        self.assertNotIn(EN_COURS, self.titres(reponse, TypeResultat.COURS))
        self.assertIn("Le théorème de Thalès dans un triangle", self.titres(reponse, TypeResultat.COURS))
        self.assertEqual(reponse["langue"], "fr")

    def test_sans_langue_toutes_les_langues(self):
        reponse = self.chercher("thales")

        titres = self.titres(reponse, TypeResultat.COURS)
        self.assertIn(EN_COURS, titres)
        self.assertIn("Le théorème de Thalès dans un triangle", titres)
        self.assertIsNone(reponse["langue"])
        self.assertEqual(reponse["autre_langue"], 0)

    def test_une_langue_inconnue_ne_filtre_pas(self):
        reponse = self.chercher("thales", langue="de")

        self.assertIn(EN_COURS, self.titres(reponse, TypeResultat.COURS))
        self.assertIsNone(reponse["langue"])

    def test_autre_langue_egale_ce_que_l_autre_langue_donnerait(self):
        en_francais = self.chercher("thales", langue="fr")
        en_anglais = self.chercher("thales", langue="en")

        # Peu de résultats dans la langue : on annonce exactement ce que l'autre recherche renverrait.
        self.assertEqual(en_francais["autre_langue"], en_anglais["total"])
        self.assertEqual(en_anglais["autre_langue"], en_francais["total"])
        self.assertGreater(en_francais["autre_langue"], 0)

    def test_aucun_indice_quand_aucune_langue_n_a_le_mot(self):
        self.assertEqual(self.chercher("zzzzqqq", langue="en")["autre_langue"], 0)
        self.assertEqual(self.chercher("zzzzqqq", langue="fr")["autre_langue"], 0)

    def test_un_examen_choisi_fixe_la_langue(self):
        reponse = self.chercher("thales", cursus=self.bac_c.id, langue="en")

        titres = self.titres(reponse, TypeResultat.COURS)
        self.assertNotIn(EN_COURS, titres)
        self.assertIn("Le théorème de Thalès dans un triangle", titres)
        self.assertIsNone(reponse["langue"])

    def test_elargir_les_examens_garde_la_langue(self):
        reponse = self.chercher("thales", cursus=self.bac_c.id, elargir=True, langue="en")

        self.assertEqual(self.titres(reponse, TypeResultat.COURS), [EN_COURS])
        self.assertEqual(reponse["langue"], "en")

    def test_les_autres_examens_restent_dans_la_langue_de_l_examen_choisi(self):
        # Examen français choisi, peu de résultats : le compte « d'autres examens » ne ramène pas de GCE.
        reponse = self.chercher("similar", cursus=self.bac_c.id, langue="fr")

        self.assertEqual(reponse["autres_cursus"], 0)

    def test_suggestions_sans_requete_dans_la_langue(self):
        en = [s["titre"] for s in self.chercher("", langue="en")["suggestions"]]
        fr = [s["titre"] for s in self.chercher("", langue="fr")["suggestions"]]

        self.assertEqual(en, [EN_THEME])
        self.assertNotIn(EN_THEME, fr)
        self.assertIn(FR_THEME, fr)

    def test_les_suggestions_d_un_examen_gce_restent_en_anglais(self):
        """Test élève Gogo (GCE O Level, interface anglaise) : les suggestions de la page de recherche étaient françaises.
        Avec un cursus, les thèmes « de tous les examens » (en français, au plus fort poids) entraient dans la liste ;
        la recherche normale écarte déjà l'autre langue (voir moteur._recherche), les suggestions non."""
        EntreeRecherche.objects.filter(type=TypeResultat.THEME, titre=FR_THEME).update(tous_cursus=True)

        titres = [s["titre"] for s in self.chercher("", cursus=self.gce.id, langue="en")["suggestions"]]

        self.assertEqual(titres, [EN_THEME])
        self.assertNotIn(FR_THEME, titres)

    def test_les_completions_d_un_examen_gce_restent_en_anglais(self):
        """Même défaut que les suggestions : les thèmes « de tous les examens » (français) entraient dans les compléments."""
        EntreeRecherche.objects.filter(type=TypeResultat.THEME, titre=FR_THEME).update(tous_cursus=True)

        textes = [c["texte"] for c in moteur.completer("theor", pays=self.pays, cursus=self.gce.id, langue="en")]

        self.assertNotIn(FR_THEME, textes)
        self.assertEqual([c["texte"] for c in moteur.completer("simil", pays=self.pays, cursus=self.gce.id, langue="en")], [EN_THEME])

    def test_les_suggestions_d_un_examen_francais_ne_recoivent_pas_de_theme_anglais(self):
        bac_c = Cursus.objects.get(country=self.pays, examen=Examen.BAC, series__code="C")

        titres = [s["titre"] for s in self.chercher("", cursus=bac_c.id, langue="fr")["suggestions"]]

        self.assertNotIn(EN_THEME, titres)
        self.assertIn(FR_THEME, titres)

    def test_completions_dans_la_langue(self):
        self.assertEqual([c["texte"] for c in moteur.completer("simil", pays=self.pays, langue="en")], [EN_THEME])
        self.assertEqual(moteur.completer("simil", pays=self.pays, langue="fr"), [])
        self.assertEqual([c["texte"] for c in moteur.completer("simil", pays=self.pays)], [EN_THEME])


class LangueVueTests(_CorpusBilingue, TestCase):
    def setUp(self):
        self.client = APIClient()

    def get(self, **params):
        params.setdefault("pays", "cm")
        return self.client.get("/recherche/", params)

    def test_le_parametre_langue_filtre(self):
        donnees = self.get(q="thales", langue="en").json()

        self.assertEqual([r["titre"] for g in donnees["groupes"] if g["type"] == "COURS" for r in g["resultats"]], [EN_COURS])
        self.assertEqual(donnees["langue"], "en")
        self.assertIn("autre_langue", donnees)

    def test_langue_en_majuscules_ou_inconnue(self):
        self.assertEqual(self.get(q="thales", langue="EN").json()["langue"], "en")
        self.assertIsNone(self.get(q="thales", langue="zz").json()["langue"])

    def test_un_zero_comble_par_l_autre_langue_n_est_pas_un_manque_du_catalogue(self):
        avant = RechercheSansResultat.objects.count()
        donnees = self.get(q="similar", langue="fr").json()  # rien en français, mais le GCE a « similar triangles »

        self.assertEqual(donnees["total"], 0)
        self.assertGreater(donnees["autre_langue"], 0)
        self.assertEqual(RechercheSansResultat.objects.count(), avant)

    def test_un_vrai_zero_reste_journalise(self):
        avant = RechercheSansResultat.objects.count()
        self.get(q="zzzzqqq", langue="fr")

        self.assertEqual(RechercheSansResultat.objects.count(), avant + 1)

    def test_completer_suit_la_langue(self):
        reponse = self.client.get("/recherche/completer/", {"q": "simil", "pays": "cm", "langue": "fr"})
        self.assertEqual(reponse.json()["completions"], [])
        reponse = self.client.get("/recherche/completer/", {"q": "simil", "pays": "cm", "langue": "en"})
        self.assertEqual([c["texte"] for c in reponse.json()["completions"]], [EN_THEME])
