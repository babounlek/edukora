"""
Le moteur lit l'anglais (voir texte.racine_en, synonymes._variantes_orthographe, intention) : radicaux, mots vides,
orthographe britannique / américaine, « o level », « paper 2 », mots de type et matières nommées en anglais. Rien de
cela ne doit changer le sens d'une requête française.
"""
from django.test import SimpleTestCase, TestCase

from catalog.models import (
    Cours, Cursus, Examen, Exercise, Langue, Lesson, LessonType, Origine, StatutContenu, Subject, Tag,
)

from . import intention as comprendre
from . import moteur, synonymes, texte
from .indexation import _libelle_exercice, reconstruire
from .models import TypeResultat
from .test_langue import _CorpusBilingue


class RadicauxAnglaisTests(SimpleTestCase):
    def test_pluriels_et_terminaisons(self):
        attendus = {
            "acids": "acid", "equations": "equation", "forces": "force", "gases": "gas", "boxes": "box",
            "reaches": "reach", "properties": "property", "balancing": "balanc", "heating": "heat",
            "heated": "heat", "reduced": "reduc", "neutralisation": "neutralis", "neutralization": "neutraliz",
            "neutralising": "neutralis", "neutralized": "neutraliz", "exercises": "exercis",
        }
        for brut, radical in attendus.items():
            self.assertEqual(texte.racine_en(brut), radical, brut)

    def test_ce_qui_ne_se_coupe_pas(self):
        for mot in ("series", "species", "analysis", "maths", "gas", "class", "mass", "string", "using", "2019", "rise"):
            self.assertEqual(texte.racine_en(mot), mot, mot)

    def test_jamais_un_radical_de_moins_de_trois_lettres(self):
        for mot in ("sed", "ring", "need", "speed", "named"):
            self.assertGreaterEqual(len(texte.racine_en(mot)), 3, mot)

    def test_le_radical_reste_un_debut_du_mot_du_catalogue(self):
        # La correspondance se fait par début de mot : « heat » doit trouver « heating », « react » « reaction ».
        for brut, mot_du_catalogue in (("heating", "heating"), ("reacting", "reaction"), ("neutralising", "neutralisation")):
            self.assertTrue(mot_du_catalogue.startswith(texte.racine_en(brut)), brut)


class MotsVidesEtOrthographeTests(SimpleTestCase):
    def test_mots_vides_anglais(self):
        self.assertEqual(texte.jetons("how to balance equations"), ["balance", "equations"])
        self.assertEqual(texte.jetons("lesson on acids"), ["lesson", "acids"])
        self.assertEqual(texte.jetons("what is the mole"), ["mole"])

    def test_des_mots_francais_qui_se_cherchent_ne_sont_pas_des_mots_vides(self):
        for mot in ("are", "or", "an", "as", "do"):
            self.assertEqual(texte.jetons(mot), [mot], mot)

    def test_ise_ize(self):
        self.assertEqual(synonymes.alternatives("neutralis"), ["neutraliz"])
        self.assertEqual(synonymes.alternatives("neutraliz"), ["neutralis"])
        self.assertEqual(synonymes.alternatives("organisation"), ["organization"])
        self.assertEqual(synonymes.alternatives("polymerized"), ["polymerised"])

    def test_orthographe_britannique(self):
        self.assertEqual(synonymes.alternatives("colour"), ["color"])
        self.assertEqual(synonymes.alternatives("color"), ["colour"])
        self.assertEqual(synonymes.alternatives("aluminum"), ["aluminium"])
        self.assertEqual(synonymes.alternatives("sulphur"), ["sulfur"])

    def test_pas_de_fausse_equivalence(self):
        # « liter » et « labor » commenceraient « literature » et « laboratory » : volontairement absents.
        self.assertEqual(synonymes.alternatives("litre"), [])
        self.assertEqual(synonymes.alternatives("labour"), [])
        self.assertEqual(synonymes.alternatives("this"), [])


class IntentionAnglaiseTests(TestCase):
    def setUp(self):
        from catalog.models import Country

        self.pays = Country.objects.get(code="CM")
        # Chaque niveau du GCE a sa branche générale et sa branche technique : nommer le niveau les prend toutes.
        self.ol = sorted(Cursus.objects.filter(country=self.pays, examen=Examen.GCE_OL).values_list("id", flat=True))
        self.al = sorted(Cursus.objects.filter(country=self.pays, examen=Examen.GCE_AL).values_list("id", flat=True))

    def lire(self, requete, langue="en", sans=frozenset()):
        jetons = moteur._analyser(requete, langue)
        return comprendre.analyser(jetons, self.pays, sans, langue)

    def test_o_level_et_a_level_en_deux_mots(self):
        i = self.lire("o level chemistry 2020")
        self.assertEqual(sorted(i.cursus_ids), self.ol)
        self.assertEqual(i.cursus_libelle, "GCE O Level")
        self.assertEqual(i.matiere_libelle, "Chemistry")
        self.assertEqual(i.annees, [2020])
        self.assertEqual(i.restants, [])
        self.assertEqual(sorted(self.lire("a level physics").cursus_ids), self.al)

    def test_gce_seul_ou_precise_par_son_niveau(self):
        self.assertEqual(sorted(self.lire("gce chemistry").cursus_ids), sorted(self.ol + self.al))
        self.assertEqual(sorted(self.lire("gce o level biology").cursus_ids), self.ol)
        self.assertEqual(sorted(self.lire("gce a level biology").cursus_ids), self.al)
        self.assertEqual(sorted(self.lire("ordinary level physics").cursus_ids), self.ol)

    def test_une_serie_a_reste_une_serie(self):
        i = self.lire("bac a maths", langue="fr")
        self.assertEqual(i.cursus_libelle, "BAC A")

    def test_les_matieres_jumelles_prennent_le_nom_de_la_langue(self):
        self.assertEqual(self.lire("maths", "en").matiere_libelle, "Mathematics")
        self.assertEqual(self.lire("maths", "fr").matiere_libelle, "Mathématiques")
        self.assertEqual(self.lire("maths", None).matiere_libelle, "Mathématiques")
        codes = self.lire("maths", "en").matiere_codes
        self.assertEqual(codes[0], "MATHS")
        self.assertIn("GCE_MATHS", codes)

    def test_matieres_nommees_en_anglais_seulement_en_anglais(self):
        self.assertEqual(self.lire("biology", "en").matiere_libelle, "Biology")
        self.assertEqual(self.lire("bio", "en").matiere_libelle, "Biology")
        self.assertEqual(self.lire("bio", "fr").matiere_codes, [])
        self.assertEqual(self.lire("econ", "fr").matiere_codes, [])
        self.assertEqual(self.lire("computer science", "en").matiere_libelle, "Computer science")

    def test_mots_de_type_anglais(self):
        i = self.lire("past papers physics")
        # « past » vise les épreuves, « paper » les épreuves et les inédites : les deux sont consommés.
        self.assertIn(TypeResultat.EPREUVE.value, i.types)
        self.assertEqual(i.restants, [])
        i = self.lire("lesson on acids")
        self.assertEqual(i.types, (TypeResultat.COURS.value,))
        self.assertEqual(i.restants, ["acid"])

    def test_paper_suivi_d_un_numero_reste_un_mot_a_chercher(self):
        i = self.lire("maths 2019 paper 2")
        self.assertIn("paper", i.restants)
        self.assertIn("2", i.restants)
        self.assertEqual(i.annees, [2019])

    def test_solution_est_un_mot_francais_de_chimie(self):
        i = self.lire("solution tampon", "fr")
        self.assertEqual(i.types, ())
        self.assertEqual(i.restants, ["solution", "tampon"])
        # En anglais, « solutions » demande des corrigés.
        self.assertEqual(self.lire("mathematics solutions", "en").types, (TypeResultat.EPREUVE.value, TypeResultat.EXERCICE.value))

    def test_un_mot_de_type_seul_reste_un_mot(self):
        self.assertEqual(self.lire("lessons").types, ())
        self.assertEqual(self.lire("lessons").restants, ["lesson"])


class MoteurAnglaisTests(_CorpusBilingue, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        chimie = Subject.objects.get(country=cls.pays, code="GCE_CHEMISTRY")
        cls.cours_acides = Cours.objects.create(
            external_id="c-acides", titre="Acids, bases and neutralisation", subject=chimie,
            statut=StatutContenu.VALIDE,
        )
        cls.cours_acides.cursus.add(cls.gce)
        cls.epreuve = Lesson.objects.create(
            title="Chemistry GCE O Level 2020 - Paper 1", subject=chimie, lesson_type=LessonType.CORR, year=2020,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL, content_markdown="Question 1",
        )
        cls.epreuve.cursus.add(cls.gce)
        reconstruire()

    def titres_cours(self, requete, langue="en"):
        return self.titres(self.chercher(requete, langue=langue), TypeResultat.COURS)

    def test_les_deux_orthographes_trouvent_le_meme_cours(self):
        for requete in ("neutralisation", "neutralization", "neutralise", "neutralize", "neutralising acids"):
            self.assertIn("Acids, bases and neutralisation", self.titres_cours(requete), requete)

    def test_le_pluriel_anglais_trouve_le_singulier(self):
        self.assertIn("Acids, bases and neutralisation", self.titres_cours("acid"))
        self.assertIn("Acids, bases and neutralisation", self.titres_cours("acids"))

    def test_une_phrase_anglaise_naturelle(self):
        reponse = self.chercher("lesson on acids", langue="en")

        self.assertIn("Acids, bases and neutralisation", self.titres(reponse, TypeResultat.COURS))
        self.assertEqual(reponse["groupes"][0]["type"], TypeResultat.COURS.value)
        self.assertEqual(reponse["intention"]["types"], [TypeResultat.COURS.value])

    def test_past_papers_met_les_epreuves_devant(self):
        reponse = self.chercher("past papers chemistry 2020", langue="en")

        self.assertEqual(reponse["groupes"][0]["type"], TypeResultat.EPREUVE.value)
        self.assertIn("Chemistry GCE O Level 2020 - Paper 1", self.titres(reponse, TypeResultat.EPREUVE))
        self.assertEqual(reponse["intention"]["matiere"]["libelle"], "Chemistry")
        self.assertEqual(reponse["intention"]["annees"], [2020])

    def test_o_level_chemistry_filtre_l_examen_et_la_matiere(self):
        reponse = self.chercher("o level chemistry 2020", langue="en")

        self.assertEqual(reponse["intention"]["cursus"]["libelle"], "GCE O Level")
        self.assertEqual(self.titres(reponse, TypeResultat.EPREUVE), ["Chemistry GCE O Level 2020 - Paper 1"])

    def test_un_examen_gce_nomme_ne_laisse_pas_entrer_le_francais(self):
        # Les contenus « de tous les examens » (en français) n'entrent pas dans une recherche GCE.
        reponse = self.chercher("a level triangles", langue="en")

        titres = [r["titre"] for g in reponse["groupes"] for r in g["resultats"]]
        self.assertNotIn("Le théorème de Thalès dans un triangle", titres)

    def test_une_requete_francaise_n_est_pas_lue_comme_de_l_anglais(self):
        # « solution » reste un mot à chercher en français, jamais « corrigé ».
        reponse = self.chercher("solution", langue="fr")
        self.assertEqual(reponse["intention"]["types"], [])


class LibellesDuServeurTests(SimpleTestCase):
    def test_le_mot_suit_la_langue_du_contenu(self):
        self.assertEqual(_libelle_exercice("3"), "Exercice 3")
        self.assertEqual(_libelle_exercice("3", Langue.FR), "Exercice 3")
        self.assertEqual(_libelle_exercice("3", Langue.EN), "Exercise 3")

    def test_un_repere_qui_n_est_pas_un_nombre_est_garde_tel_quel(self):
        self.assertEqual(_libelle_exercice("B1", Langue.EN), "B1")
        self.assertEqual(_libelle_exercice("Problème", Langue.FR), "Problème")

    def test_sans_numero(self):
        self.assertEqual(_libelle_exercice("", Langue.EN), "Exercise")
        self.assertEqual(_libelle_exercice(None, Langue.FR), "Exercice")

    def test_entete_d_exercice_traduit_pour_un_contenu_anglais(self):
        self.assertEqual(texte.traduire_entete_exercice("**Exercice 3 (7 points)**", "en"), "**Exercise 3 (7 marks)**")
        self.assertEqual(texte.traduire_entete_exercice("**Exercice 1 (1 point)**", Langue.EN), "**Exercise 1 (1 mark)**")
        self.assertEqual(texte.traduire_entete_exercice("**Exercice 2 (2,5 points)**", "en"), "**Exercise 2 (2.5 marks)**")

    def test_entete_sans_bareme(self):
        self.assertEqual(
            texte.traduire_entete_exercice("**Exercice 1** Multiple choice questions", "en"),
            "**Exercise 1** Multiple choice questions",
        )

    def test_texte_public_traduit_le_preambule_et_l_enonce_qui_repete_l_entete(self):
        saut = chr(10)
        public = texte.enonce_public("**Exercice 3 (10 points)**", "**Exercice 3 (10 points)** Organic compounds", "en")
        self.assertEqual(public, "**Exercise 3 (10 marks)**" + saut + "**Exercise 3 (10 marks)** Organic compounds")
        # Un contenu français, ou sans langue, reste tel quel.
        francais = texte.enonce_public("**Exercice 3 (10 points)**", "Soit un triangle", "fr")
        self.assertEqual(francais, "**Exercice 3 (10 points)**" + saut + "Soit un triangle")
        self.assertEqual(texte.enonce_public(None, None, "en"), saut)

    def test_entete_d_exercice_inchange_en_francais_ou_hors_debut(self):
        entete = "**Exercice 3 (7 points)**"
        self.assertEqual(texte.traduire_entete_exercice(entete, "fr"), entete)
        self.assertEqual(texte.traduire_entete_exercice(entete, None), entete)
        # Seul l'en-tête en tête de texte : la consigne qui suit n'est jamais touchée.
        saut = chr(10) * 2
        corps = "**Exercice 3 (7 points)**" + saut + "Voir Exercice 4 (sic)."
        self.assertEqual(
            texte.traduire_entete_exercice(corps, "en"), "**Exercise 3 (7 marks)**" + saut + "Voir Exercice 4 (sic).",
        )
        self.assertEqual(texte.traduire_entete_exercice("Voir **Exercice 3 (7 points)**", "en"), "Voir **Exercice 3 (7 points)**")
        self.assertEqual(texte.traduire_entete_exercice("", "en"), "")
        self.assertIsNone(texte.traduire_entete_exercice(None, "en"))


class TitresEtExtraitsDansLaLangueDuContenuTests(_CorpusBilingue, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        chimie = Subject.objects.get(country=cls.pays, code="GCE_CHEMISTRY")
        cls.epreuve = Lesson.objects.create(
            title="Chemistry GCE O Level 2020 - Paper 2", subject=chimie, lesson_type=LessonType.CORR, year=2020,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL, content_markdown="Question 1",
        )
        cls.epreuve.cursus.add(cls.gce)
        Exercise.objects.create(
            lesson=cls.epreuve, numero_exercice="1", statut=StatutContenu.VALIDE,
            enonce_intro_markdown="**Exercice 1 (10 points)**",
            enonce_markdown="State the name of the reaction between an acid and an alkali.",
        )
        Exercise.objects.create(
            lesson=cls.epreuve, numero_exercice="B1", statut=StatutContenu.VALIDE,
            enonce_markdown="Calculate the mass of one mole of water.",
        )
        theme = Exercise.objects.create(
            lesson=cls.epreuve, numero_exercice="2", statut=StatutContenu.VALIDE, enonce_markdown="Describe the procedure.",
        )
        theme.themes.add(Tag.objects.create(name="titration"))
        reconstruire()

    def titres_exercices(self, requete, langue):
        return self.titres(self.chercher(requete, langue=langue), TypeResultat.EXERCICE)

    def test_un_exercice_du_gce_s_intitule_exercise(self):
        titres = self.titres_exercices("acid alkali", "en")

        self.assertEqual(titres, ["Exercise 1 · Chemistry GCE O Level 2020 - Paper 2"])

    def test_un_repere_non_numerique_est_inchange(self):
        self.assertEqual(self.titres_exercices("mole water", "en"), ["B1 · Chemistry GCE O Level 2020 - Paper 2"])

    def test_un_exercice_francais_garde_exercice(self):
        titres = self.titres_exercices("pythagore", "fr")

        self.assertEqual(titres, ["Exercice 1 · Mathématiques BAC C 2019"])

    def test_le_detail_porte_le_meme_libelle(self):
        resultat = self.resultat(
            self.chercher("acid alkali", langue="en"), TypeResultat.EXERCICE, "Exercise 1 · Chemistry GCE O Level 2020 - Paper 2",
        )

        self.assertEqual(resultat["details"]["libelle"], "Exercise 1")

    def test_les_mots_exercise_et_exercice_se_cherchent_dans_leur_langue(self):
        # Le titre porte le mot de sa langue : « exercise » trouve les exercices du GCE...
        en = self.chercher("exercise 1 chemistry", langue="en")
        self.assertIn("Exercise 1 · Chemistry GCE O Level 2020 - Paper 2", self.titres(en, TypeResultat.EXERCICE))
        # ... et « exercice » ceux du programme français.
        fr = self.chercher("exercice 1 maths", langue="fr")
        self.assertIn("Exercice 1 · Mathématiques BAC C 2019", self.titres(fr, TypeResultat.EXERCICE))

    def test_extrait_par_theme_dans_la_langue_du_contenu(self):
        # Le mot cherché n'est ni dans le titre ni dans l'énoncé : seul le thème étiqueté explique le résultat.
        en = self.chercher("titration", langue="en")
        apercus = [r["apercu"] for g in en["groupes"] if g["type"] == "EXERCICE" for r in g["resultats"]]
        self.assertIn("Topic: titration", apercus)

        fr = self.chercher("thales", langue="fr")
        apercus = [r["apercu"] for g in fr["groupes"] if g["type"] == "EXERCICE" for r in g["resultats"]]
        self.assertTrue(any(a.startswith("Thème : ") for a in apercus), apercus)

    def test_l_entete_francais_des_donnees_est_traduit_dans_l_apercu(self):
        # Le titre explique la correspondance : l'aperçu est celui de l'index (ouverture de l'énoncé).
        en = self.chercher("exercise 1 chemistry", langue="en")
        apercus = [r["apercu"] for g in en["groupes"] if g["type"] == "EXERCICE" for r in g["resultats"]]
        self.assertTrue(any(a.startswith("Exercise 1 (10 marks)") for a in apercus), apercus)
        self.assertFalse(any("Exercice" in a for a in apercus), apercus)

    def test_l_entete_est_traduit_aussi_dans_l_extrait(self):
        # Le mot cherché n'est que dans l'énoncé : l'extrait est relu dans la source, en-tête compris.
        en = self.chercher("alkali", langue="en")
        apercus = [r["apercu"] for g in en["groupes"] for r in g["resultats"]]
        self.assertFalse(any("Exercice" in a for a in apercus), apercus)
