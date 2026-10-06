"""
Tests de l'« intelligence » du moteur : ce qu'il comprend d'une requête naturelle (examen, matière, année,
type voulu), les équivalences de vocabulaire, la correction par la prononciation et la complétion pendant la
frappe. Les cas viennent de vraies requêtes d'élèves qui donnaient zéro résultat ou une mauvaise correction.
"""

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from catalog.models import Cours, Cursus, Examen, Subject, Tag
from . import intention, moteur, synonymes, texte
from .indexation import reconstruire
from .models import EntreeRecherche, TypeResultat
from .tests import VALIDE, _CorpusMixin


class PhonetiqueTests(SimpleTestCase):
    def test_des_graphies_qui_se_prononcent_pareil_ont_la_meme_cle(self):
        for a, b in (
            ("teoreme", "theoreme"), ("fotosyntese", "photosynthese"), ("hthales", "thales"), ("tales", "thales"),
            ("equasion", "equation"), ("derrivee", "derivee"), ("kilometre", "quilometre"),
        ):
            self.assertEqual(texte.phonetique(a), texte.phonetique(b), (a, b))

    def test_des_mots_differents_gardent_des_cles_differentes(self):
        for a, b in (("tales", "table"), ("thales", "tableau"), ("limite", "limace"), ("cercle", "cerceau")):
            self.assertNotEqual(texte.phonetique(a), texte.phonetique(b), (a, b))

    def test_robuste_aux_entrees_degenerees(self):
        for mot in ("", "123", "a", "---"):
            self.assertIsInstance(texte.phonetique(mot), str)


class SynonymesTests(SimpleTestCase):
    def test_equivalences_dans_les_deux_sens(self):
        self.assertEqual(synonymes.alternatives("cercle"), ["disque"])
        self.assertEqual(synonymes.alternatives("disque"), ["cercle"])

    def test_un_radical_elargit_a_toute_la_famille(self):
        self.assertEqual(synonymes.alternatives("derivee"), ["deriv"])
        self.assertEqual(synonymes.alternatives("derivation"), ["deriv"])
        self.assertIn("resolu", synonymes.alternatives("resoudre"))

    def test_une_abreviation_ne_s_etend_que_dans_un_sens(self):
        self.assertEqual(synonymes.alternatives("tp"), ["travaux pratiques"])
        self.assertEqual(synonymes.alternatives("travaux"), [])
        self.assertEqual(synonymes.alternatives("limite"), [])

    def test_une_lettre_seule_n_a_jamais_d_equivalent(self):
        self.assertEqual(synonymes.alternatives("d"), [])
        self.assertEqual(synonymes.alternatives("a"), [])

    def test_aucun_doublon_et_jamais_le_mot_lui_meme(self):
        for jeton in ("cercle", "derivee", "resoudre", "tp", "refraction"):
            formes = synonymes.alternatives(jeton)
            self.assertNotIn(jeton, formes)
            self.assertEqual(len(formes), len(set(formes)))

    def test_pas_d_equivalence_hasardeuse(self):
        # « aire » / « surface » ramènerait les surfaces équipotentielles de la physique.
        self.assertEqual(synonymes.alternatives("aire"), [])
        self.assertEqual(synonymes.alternatives("surface"), [])


class IntentionTests(_CorpusMixin, TestCase):
    def analyser(self, requete, sans=()):
        jetons = moteur._analyser(requete)
        return intention.analyser(jetons, self.pays, frozenset(sans))

    def test_examen_serie_matiere_et_annee(self):
        i = self.analyser("bac c maths 2019")
        self.assertEqual(i.cursus_ids, [self.bac_c.id])
        self.assertEqual(i.cursus_libelle, "BAC C")
        self.assertEqual(i.matiere_codes, ["MATHS"])
        self.assertEqual(i.annees, [2019])
        self.assertEqual(i.restants, [])

    def test_plusieurs_series_a_la_suite(self):
        i = self.analyser("bac c e maths")
        self.assertEqual(len(i.cursus_ids), 2)
        self.assertEqual(i.cursus_libelle, "BAC C, E")

    def test_un_examen_sans_serie_vise_toutes_ses_series(self):
        i = self.analyser("bac")
        self.assertGreater(len(i.cursus_ids), 4)
        self.assertEqual(i.cursus_libelle, "BAC")

    def test_bepc_n_a_pas_de_serie(self):
        i = self.analyser("brevet maths")
        self.assertEqual(i.cursus_ids, [self.bepc.id])

    def test_les_mots_de_type_sont_retires_quand_il_reste_autre_chose(self):
        i = self.analyser("sujets bac c 2019 corrigés")
        self.assertEqual(i.types, ("EPREUVE", "INEDITE", "EXERCICE"))
        self.assertEqual(sorted(i.mots_type), ["corrige", "sujet"])
        self.assertEqual(i.restants, [])

    def test_un_mot_de_type_seul_reste_un_mot_a_chercher(self):
        for requete in ("corrigé", "cours", "quiz"):
            i = self.analyser(requete)
            self.assertEqual(i.types, (), requete)
            self.assertTrue(i.restants, requete)

    def test_sujet_zero_et_examen_blanc_gardent_leurs_mots(self):
        zero = self.analyser("sujet zero maths")
        self.assertEqual(zero.types, ("EPREUVE", "INEDITE"))
        self.assertIn("sujet", zero.restants)
        self.assertIn("zero", zero.restants)
        blanc = self.analyser("examen blanc")
        self.assertIn("blanc", blanc.restants)
        self.assertEqual(blanc.types, ("EPREUVE", "INEDITE"))

    def test_retirer_une_partie_la_rend_a_la_recherche_par_mots(self):
        i = self.analyser("bac c maths 2019", sans={"cursus", "annee"})
        self.assertEqual(i.cursus_ids, [])
        self.assertEqual(i.annees, [])
        self.assertEqual(i.matiere_codes, ["MATHS"])
        self.assertEqual(sorted(i.restants), ["2019", "bac", "c"])

    def test_la_matiere_la_plus_longue_gagne(self):
        i = self.analyser("physique chimie bac c")
        self.assertEqual(i.matiere_codes, ["PHYSIQUE_CHIMIE"])
        seule = self.analyser("physique")
        self.assertIn("PHYSIQUE", seule.matiere_codes)
        self.assertIn("PHYSIQUE_CHIMIE", seule.matiere_codes)

    def test_une_requete_ordinaire_ne_comprend_rien(self):
        i = self.analyser("theoreme de thales")
        self.assertTrue(i.vide())
        self.assertEqual(i.restants, ["theoreme", "thale"])

    def test_une_annee_hors_programme_n_en_est_pas_une(self):
        self.assertEqual(self.analyser("1234").annees, [])
        self.assertEqual(self.analyser("2019").annees, [2019])

    def test_une_serie_sans_examen_n_est_pas_interpretee(self):
        i = self.analyser("maths c")
        self.assertEqual(i.cursus_ids, [])
        self.assertIn("c", i.restants)


class MoteurIntelligentTests(_CorpusMixin, TestCase):
    def test_une_requete_naturelle_ne_donne_plus_zero(self):
        # Avant : « corrigé » n'est dans aucun titre, il était pourtant exigé.
        for requete in ("maths 2019 corrigé", "sujets bac c 2019 corrigés", "bac c maths 2019"):
            reponse = self.chercher(requete)
            self.assertIn("Mathématiques BAC C 2019", self.titres(reponse, "EPREUVE"), requete)

    def test_ce_qui_est_compris_est_renvoye(self):
        intention_ = self.chercher("bac c maths 2019")["intention"]
        self.assertEqual(intention_["cursus"]["libelle"], "BAC C")
        self.assertEqual(intention_["matiere"]["libelle"], "Mathématiques")
        self.assertEqual(intention_["annees"], [2019])
        self.assertFalse(intention_["ignoree"])

    def test_le_type_voulu_ouvre_la_liste(self):
        reponse = self.chercher("corrigé thales")
        self.assertEqual(reponse["groupes"][0]["type"], "EPREUVE")
        self.assertIn("COURS", [g["type"] for g in reponse["groupes"]])  # jamais le seul type renvoyé

    def test_sans_intention_l_ordre_des_groupes_est_celui_d_avant(self):
        types = [g["type"] for g in self.chercher("thales")["groupes"]]
        self.assertEqual(types, sorted(types, key=lambda t: ["THEME", "COURS", "EPREUVE", "INEDITE", "EXERCICE", "QUIZ"].index(t)))

    def test_l_examen_nomme_remplace_celui_de_l_eleve(self):
        # L'élève prépare le BEPC mais écrit « bac c » : on le croit sur parole.
        reponse = self.chercher("bac c maths 2019", cursus=self.bepc.id)
        self.assertIn("Mathématiques BAC C 2019", self.titres(reponse, "EPREUVE"))

    def test_une_interpretation_sans_resultat_est_abandonnee(self):
        Cours.objects.create(
            external_id="c-hist", titre="L'histoire des triangles et de Thalès", subject=self.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Un récit."}],
        )
        reconstruire([TypeResultat.COURS])
        reponse = self.chercher("histoire thales")
        # « histoire » est une matière : sans cours d'histoire, l'interprétation ne donne rien, on cherche les mots.
        self.assertTrue(reponse["intention"]["ignoree"])
        self.assertIn("L'histoire des triangles et de Thalès", self.titres(reponse, "COURS"))

    def test_retirer_la_pastille_rend_les_mots(self):
        reponse = self.chercher("bac c maths 2019", sans=["cursus", "annee", "matiere"])
        self.assertIsNone(reponse["intention"]["cursus"])
        self.assertEqual(reponse["intention"]["annees"], [])

    def test_des_filtres_seuls_suffisent_a_une_recherche(self):
        reponse = self.chercher("2019")
        self.assertGreater(reponse["total"], 0)
        self.assertEqual(self.titres(reponse, "EPREUVE"), ["Mathématiques BAC C 2019"])

    def test_la_correction_par_la_prononciation_prefere_thales_a_table(self):
        # « tales » est à une lettre de « table » comme de « thales » : la prononciation tranche.
        Cours.objects.create(
            external_id="c-table", titre="La table de multiplication", subject=self.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Table et table encore."}],
        )
        reconstruire([TypeResultat.COURS])
        reponse = self.chercher("teoreme de tales")
        self.assertIn("thales", reponse["corrige"])
        self.assertNotIn("table", reponse["corrige"])
        self.assertIn("théorème de Thalès", self.titres(reponse, "THEME"))

    def test_les_fautes_d_oreille_sont_corrigees(self):
        Tag.objects.create(name="photosynthèse")
        cours = Cours.objects.create(
            external_id="c-photo", titre="La photosynthèse", subject=Subject.objects.get(country=self.pays, code="SVT"),
            statut=VALIDE, sections_raw=[{"type": "accroche", "contenu_markdown": "Les plantes captent la lumière."}],
        )
        reconstruire([TypeResultat.COURS])
        for faute in ("fotosyntese", "photosintese"):
            reponse = self.chercher(faute)
            self.assertIn(cours.titre, self.titres(reponse, "COURS"), faute)
        self.assertIn("Thalès", " ".join(self.titres(self.chercher("hthales"), "THEME")))

    def test_un_synonyme_retrouve_le_contenu(self):
        Cours.objects.create(
            external_id="c-disque", titre="Aire du disque", subject=self.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Un rayon, pi, un carré."}],
        )
        reconstruire([TypeResultat.COURS])
        reponse = self.chercher("aire cercle")
        self.assertIn("Aire du disque", self.titres(reponse, "COURS"))
        # Et l'inverse.
        self.assertIn("Aire du disque", self.titres(self.chercher("aire disque"), "COURS"))

    def test_un_synonyme_vaut_un_peu_moins_que_le_mot_tape(self):
        Cours.objects.create(
            external_id="c-cercle", titre="Aire du cercle", subject=self.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Un rayon."}],
        )
        Cours.objects.create(
            external_id="c-disque", titre="Aire du disque", subject=self.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Un rayon."}],
        )
        reconstruire([TypeResultat.COURS])
        titres = self.titres(self.chercher("aire cercle"), "COURS")
        self.assertEqual(titres[:2], ["Aire du cercle", "Aire du disque"])

    def test_les_abreviations_s_etendent(self):
        Cours.objects.create(
            external_id="c-tp", titre="Réussir ses travaux pratiques", subject=self.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Matériel et consignes."}],
        )
        reconstruire([TypeResultat.COURS])
        self.assertIn("Réussir ses travaux pratiques", self.titres(self.chercher("tp"), "COURS"))

    def test_un_mot_inconnu_et_sans_prononciation_proche_ne_donne_rien(self):
        reponse = self.chercher("pourquoi le ciel est bleu")
        self.assertEqual(reponse["total"], 0)
        self.assertTrue(reponse["suggestions"])


class CompletionTests(_CorpusMixin, TestCase):
    def test_complete_avec_les_themes(self):
        for debut in ("thal", "theoreme tha", "théorème de tha"):
            textes = [c["texte"] for c in moteur.completer(debut, pays=self.pays)]
            self.assertIn("théorème de Thalès", textes, debut)

    def test_donne_la_matiere(self):
        completion = moteur.completer("thal", pays=self.pays)[0]
        self.assertEqual(completion["matiere"], "Mathématiques")

    def test_une_saisie_trop_courte_ne_complete_rien(self):
        for debut in ("", " ", "t"):
            self.assertEqual(moteur.completer(debut, pays=self.pays), [], debut)

    def test_suit_l_examen(self):
        au_bepc = [c["texte"] for c in moteur.completer("limite", pays=self.pays, cursus=self.bepc.id)]
        au_bac = [c["texte"] for c in moteur.completer("limite", pays=self.pays, cursus=self.bac_c.id)]
        self.assertNotIn("limite d'une suite", au_bepc)
        self.assertIn("limite d'une suite", au_bac)

    def test_ecarte_les_etiquettes_de_niveau_et_les_doublons(self):
        Tag.objects.create(name="Terminale C")
        tag = Tag.objects.create(name="limites")
        for _ in range(2):
            from quiz.models import CompetenceItem  # noqa: PLC0415 - fixture locale

            item = CompetenceItem.objects.create(
                theme=Tag.objects.get(name="Terminale C"), subject=self.maths, statut=VALIDE,
                enonce_markdown="Q.", corrige_markdown="ok",
            )
            item.cursus.add(self.bac_c)
        item = CompetenceItem.objects.create(
            theme=tag, subject=self.maths, statut=VALIDE, enonce_markdown="Q.", corrige_markdown="ok",
        )
        item.cursus.add(self.bac_c)
        reconstruire([TypeResultat.THEME])
        self.assertEqual(moteur.completer("termin", pays=self.pays), [])
        textes = [c["texte"] for c in moteur.completer("limit", pays=self.pays)]
        self.assertEqual(len(textes), len(set(t.lower() for t in textes)))

    def test_respecte_la_limite(self):
        for i in range(12):
            tag = Tag.objects.create(name=f"suite numéro {i}")
            Cours.objects.create(external_id=f"cs{i}", titre=f"Suite {i}", subject=self.maths, statut=VALIDE).tags.add(tag)
            Cours.objects.create(external_id=f"cs{i}b", titre=f"Suite bis {i}", subject=self.maths, statut=VALIDE).tags.add(tag)
        reconstruire()
        self.assertEqual(len(moteur.completer("suite num", pays=self.pays)), moteur.NB_COMPLETIONS)

    def test_le_point_d_entree(self):
        client = APIClient()
        reponse = client.get("/recherche/completer/", {"q": "thal", "pays": "cm"})
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("théorème de Thalès", [c["texte"] for c in reponse.json()["completions"]])
        self.assertEqual(client.get("/recherche/completer/", {"q": "thal", "pays": "zz"}).status_code, 400)
        self.assertEqual(client.get("/recherche/completer/", {"q": "thal", "pays": "cm", "cursus": "x"}).status_code, 200)


class VueIntelligenteTests(_CorpusMixin, TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_la_reponse_porte_l_intention(self):
        donnees = self.client.get("/recherche/", {"q": "bac c maths 2019", "pays": "cm"}).json()
        self.assertEqual(donnees["intention"]["cursus"]["libelle"], "BAC C")

    def test_sans_retire_ce_qui_a_ete_compris(self):
        donnees = self.client.get("/recherche/", {"q": "bac c maths 2019", "pays": "cm", "sans": "cursus,annee,nimporte"}).json()
        self.assertIsNone(donnees["intention"]["cursus"])
        self.assertEqual(donnees["intention"]["annees"], [])

    def test_une_requete_reussie_grace_a_l_intention_n_est_pas_journalisee(self):
        from .models import RechercheSansResultat

        self.client.get("/recherche/", {"q": "maths 2019 corrigé", "pays": "cm"})
        self.assertFalse(RechercheSansResultat.objects.exists())
