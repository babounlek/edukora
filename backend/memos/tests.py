import json
from datetime import timedelta
from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from access.models import NoteLibre
from catalog.models import Cursus, Examen, Exercise, Lesson, LessonType, Question, StatutContenu, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from . import extraction, redaction, services
from .gratuites import fusionner_sessions
from .models import Memo, StatutMemo


class _Base(APITestCase):
    def setUp(self):
        maths = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.filter(examen=Examen.BEPC, country=maths.country).first()
        self.subject = Subject.objects.create(country=maths.country, code="ECM_TEST", label="Éducation Civique")
        self.user = User.objects.create_user(phone_number="677600001", password="x")
        self.profil = self.user.profils.first()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def memo(self, terme="Scrutin", **extra):
        champs = {
            "definition": "Ensemble des opérations par lesquelles les électeurs désignent leurs représentants.",
            "statut": StatutMemo.PUBLIE, "relu_par_enseignant": True,
            "sessions": [{"annee": 2019, "origine": "OFFICIEL"}],
        }
        champs.update(extra)
        m = Memo.objects.create(subject=self.subject, terme=terme, **champs)
        m.cursus.add(self.cursus)
        return m

    def abonner(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )


@override_settings(MEMOS_MONTRER_BROUILLONS=False)
class LectureTests(_Base):
    def test_a_draft_or_an_unreviewed_card_is_never_shown(self):
        self.memo("Publiée")
        self.memo("Brouillon", statut=StatutMemo.BROUILLON)
        # Publiée sans relecture : le modèle la remet en brouillon.
        non_relue = self.memo("Non relue", relu_par_enseignant=False)
        self.assertEqual(non_relue.statut, StatutMemo.BROUILLON)
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertEqual([f["terme"] for f in data["fiches"]], ["Publiée"])

    def test_without_a_subscription_only_free_cards_give_their_definition(self):
        self.memo("Gratuite", gratuit=True)
        self.memo("Payante")
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        par_terme = {f["terme"]: f for f in data["fiches"]}
        self.assertFalse(data["abonne"])
        self.assertIsNotNone(par_terme["Gratuite"]["definition"])
        self.assertIsNone(par_terme["Payante"]["definition"])
        self.assertTrue(par_terme["Payante"]["verrouillee"])
        # Le terme et les sessions restent visibles : c'est ce qui donne envie.
        self.assertEqual(par_terme["Payante"]["sessions"], [{"annee": 2019, "origine": "OFFICIEL"}])

    def test_a_subscriber_reads_everything_and_a_visitor_reads_the_free_ones(self):
        self.memo("Gratuite", gratuit=True)
        self.memo("Payante")
        visiteur = APIClient().get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertEqual(sum(1 for f in visiteur["fiches"] if f["definition"]), 1)
        self.abonner()
        abonne = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertTrue(abonne["abonne"])
        self.assertTrue(all(f["definition"] for f in abonne["fiches"]))

    def test_the_subjects_list_counts_cards_per_subject(self):
        self.memo("A", gratuit=True)
        self.memo("B")
        data = self.client.get(f"/memos/matieres/?cursus={self.cursus.pk}").data
        self.assertEqual(data["matieres"], [{
            "matiere_id": self.subject.pk, "matiere": "Éducation Civique", "matiere_code": "ECM_TEST",
            "total": 2, "gratuites": 1,
        }])
        self.assertEqual(self.client.get("/memos/matieres/").status_code, 400)


@override_settings(MEMOS_MONTRER_BROUILLONS=False)
class ApercuTests(_Base):
    def test_a_visitor_previews_a_few_free_published_cards_and_never_a_paid_or_draft_one(self):
        for i in range(5):
            self.memo(f"Gratuite {i}", gratuit=True, ordre=i)
        self.memo("Payante", ordre=0)
        self.memo("Brouillon", gratuit=True, ordre=0, statut=StatutMemo.BROUILLON)
        data = APIClient().get("/memos/apercu/?pays=cm").data
        self.assertEqual([f["terme"] for f in data["fiches"]], ["Gratuite 0", "Gratuite 1", "Gratuite 2"])
        self.assertTrue(all(f["definition"] for f in data["fiches"]))
        self.assertEqual(data["fiches"][0]["cursus_id"], self.cursus.pk)
        self.assertEqual(data["total"], 6)

    def test_the_preview_of_an_exam_never_shows_another_exams_cards(self):
        self.memo("Gratuite", gratuit=True)
        autre = Cursus.objects.exclude(pk=self.cursus.pk).filter(country=self.cursus.country).first()
        data = APIClient().get(f"/memos/apercu/?pays=cm&cursus={autre.pk}").data
        self.assertEqual(data, {"total": 0, "fiches": []})
        self.assertEqual(APIClient().get("/memos/apercu/").status_code, 400)


@override_settings(MEMOS_MONTRER_BROUILLONS=False)
class GarderTests(_Base):
    def test_keeping_a_card_makes_a_review_note_once(self):
        memo = self.memo(gratuit=True, exemple="Exemple : l'élection présidentielle.")
        r = self.client.post(f"/memos/fiches/{memo.pk}/garder/")
        self.assertEqual(r.status_code, 201)
        note = NoteLibre.objects.get()
        # Le terme est le recto de la carte de révision, la définition son verso.
        self.assertEqual((note.citation, note.origine, note.subject_id), ("Scrutin", "fiche", self.subject.pk))
        self.assertIn("Exemple", note.note)
        self.assertEqual(self.client.post(f"/memos/fiches/{memo.pk}/garder/").status_code, 200)
        self.assertEqual(NoteLibre.objects.count(), 1)
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertTrue(data["fiches"][0]["gardee"])

    def test_a_locked_card_cannot_be_kept_and_a_visitor_cannot_keep(self):
        memo = self.memo()
        self.assertEqual(self.client.post(f"/memos/fiches/{memo.pk}/garder/").status_code, 403)
        self.assertEqual(APIClient().post(f"/memos/fiches/{memo.pk}/garder/").status_code, 401)
        self.abonner()
        self.assertEqual(self.client.post(f"/memos/fiches/{memo.pk}/garder/").status_code, 201)


class SessionsParExamenTests(_Base):
    def test_each_exam_only_sees_its_own_years(self):
        autre = Cursus.objects.exclude(pk=self.cursus.pk).filter(country=self.cursus.country).first()
        memo = self.memo(gratuit=True, sessions=[
            {"annee": 2018, "origine": "OFFICIEL", "cursus": [self.cursus.pk]},
            {"annee": 2021, "origine": "OFFICIEL", "cursus": [autre.pk]},
        ])
        memo.cursus.add(autre)
        bepc = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        lycee = self.client.get(f"/memos/fiches/?cursus={autre.pk}&matiere={self.subject.pk}").data
        self.assertEqual(bepc["fiches"][0]["sessions"], [{"annee": 2018, "origine": "OFFICIEL"}])
        self.assertEqual(lycee["fiches"][0]["sessions"], [{"annee": 2021, "origine": "OFFICIEL"}])

    def test_merging_sessions_keeps_one_entry_per_year_with_all_its_exams(self):
        self.assertEqual(
            fusionner_sessions([{"annee": 2018, "origine": "OFFICIEL", "cursus": [1]}], [{"annee": 2018, "origine": "OFFICIEL", "cursus": [2]}]),
            [{"annee": 2018, "origine": "OFFICIEL", "cursus": [1, 2]}],
        )


class RedactionTests(_Base):
    def _epreuve(self, titre, annee, cursus):
        lesson = Lesson.objects.create(
            title=titre, subject=self.subject, year=annee, origine="OFFICIEL", lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        return lesson

    def _donnees(self, notions):
        return {
            "pays": self.subject.country.code, "matiere": self.subject.code,
            "epreuves": {"A": "Épreuve A", "X": "Épreuve absente"}, "notions": notions,
        }

    def test_written_cards_are_drafts_whose_years_come_from_the_cited_papers(self):
        autre = Cursus.objects.exclude(pk=self.cursus.pk).filter(country=self.cursus.country).first()
        self._epreuve("Épreuve A", 2019, autre)
        deja = self.memo("Syndicat", definition="Texte déjà relu du BEPC.", sessions=[
            {"annee": 2018, "origine": "OFFICIEL", "cursus": [self.cursus.pk]},
        ])
        bilan = redaction.importer(self._donnees([
            {"terme": "Dictature", "definition": "Un régime qui concentre tous les pouvoirs.", "epreuves": ["A"]},
            {"terme": "Syndicat", "definition": "Autre rédaction.", "epreuves": ["A"]},
            {"terme": "Sans preuve", "definition": "Rien ne montre que c'est tombé.", "epreuves": ["X"]},
        ]))
        self.assertEqual((bilan["creees"], bilan["completees"], bilan["ignorees"]), (1, 1, 1))
        self.assertEqual(bilan["epreuves_absentes"], ["Épreuve absente"])
        neuve = Memo.objects.get(terme="Dictature")
        self.assertEqual((neuve.statut, neuve.relu_par_enseignant, neuve.gratuit), (StatutMemo.BROUILLON, False, True))
        self.assertEqual(neuve.sessions, [{"annee": 2019, "origine": "OFFICIEL", "cursus": [autre.pk]}])
        deja.refresh_from_db()
        # La fiche relue du BEPC garde son texte et son statut ; elle gagne l'autre examen et ses années.
        self.assertEqual((deja.definition, deja.statut), ("Texte déjà relu du BEPC.", StatutMemo.PUBLIE))
        self.assertEqual({c.pk for c in deja.cursus.all()}, {self.cursus.pk, autre.pk})
        self.assertEqual([s["annee"] for s in deja.sessions], [2018, 2019])
        # Rejouable sans doublon.
        self.assertEqual(redaction.importer(self._donnees([
            {"terme": "Dictature", "definition": "Un régime qui concentre tous les pouvoirs.", "epreuves": ["A"]},
        ]))["creees"], 0)

    def test_a_theme_named_in_the_file_attaches_published_cards_too_and_never_replaces_one(self):
        self._epreuve("Épreuve A", 2019, self.cursus)
        thales = Tag.objects.create(name="thème de test A")
        deja_pose = Tag.objects.create(name="thème de test B")
        publiee = self.memo("Publiée sans thème", definition="Texte déjà relu.")
        rattachee = self.memo("Déjà rattachée", definition="Texte déjà relu.", theme=deja_pose)
        bilan = redaction.importer(self._donnees([
            {"terme": terme, "theme": theme, "definition": "Une définition assez longue.", "epreuves": ["A"]}
            for terme, theme in [
                ("Publiée sans thème", thales.name), ("Déjà rattachée", thales.name),
                ("Neuve", thales.name), ("Orpheline", "thème qui n'existe pas"),
            ]
        ]))
        self.assertEqual(bilan["themes_absents"], ["thème qui n'existe pas"])
        publiee.refresh_from_db()
        rattachee.refresh_from_db()
        self.assertEqual((publiee.theme, publiee.statut, publiee.definition), (thales, StatutMemo.PUBLIE, "Texte déjà relu."))
        self.assertEqual(rattachee.theme, deja_pose)
        self.assertEqual(Memo.objects.get(terme="Neuve").theme, thales)
        self.assertIsNone(Memo.objects.get(terme="Orpheline").theme)

    def test_the_shipped_file_is_consistent(self):
        donnees = redaction.lire("education_civique_lycee")
        termes = [n["terme"] for n in donnees["notions"]]
        self.assertEqual(len(termes), len(set(termes)))
        for n in donnees["notions"]:
            self.assertTrue(n["epreuves"] and set(n["epreuves"]) <= set(donnees["epreuves"]), n["terme"])
            self.assertGreaterEqual(len(n["definition"]), 60, n["terme"])


class ExtractionTests(_Base):
    def _question(self, annee, corrige, enonce="Définis : scrutin, tontine.", origine="OFFICIEL"):
        lesson = Lesson.objects.create(
            title=f"ECM {annee} {origine}", subject=self.subject, year=annee, origine=origine,
            lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(self.cursus)
        exercice = Exercise.objects.create(lesson=lesson, numero_exercice="1")
        return Question.objects.create(exercise=exercice, numero="1", ordre=1, enonce_markdown=enonce, corrige_markdown=corrige)

    def test_definitions_are_read_from_the_solutions_and_grouped_by_term(self):
        self._question(2018, "### Rappel de méthode\nCourt.\n\n**Scrutin** : ancienne rédaction de la définition du scrutin.")
        self._question(
            2019,
            "**Astuce** : ne pas confondre avec autre chose du tout.\n"
            "**Le scrutin** : ensemble des opérations par lesquelles les électeurs votent\n"
            "- **Tontine** : association d'entraide financière entre ses membres.",
        )
        self._question(2020, "**Hors sujet** : cette ligne n'est pas une définition demandée.", enonce="Cite deux symboles.")
        relevees = extraction.relever(self.subject)
        self.assertEqual([n["terme"] for n in relevees], ["Scrutin", "Tontine"])
        scrutin = relevees[0]
        self.assertEqual([s["annee"] for s in scrutin["sessions"]], [2018, 2019])
        # La rédaction la plus récente, terminée par un point.
        self.assertEqual(scrutin["definition"], "Ensemble des opérations par lesquelles les électeurs votent.")

    def test_generated_cards_are_drafts_and_manual_edits_are_kept(self):
        self._question(2019, "**Scrutin** : ensemble des opérations par lesquelles les électeurs votent.")
        bilan = extraction.enregistrer(self.subject, extraction.relever(self.subject))
        self.assertEqual(bilan["creees"], 1)
        memo = Memo.objects.get()
        self.assertEqual((memo.statut, memo.relu_par_enseignant, memo.gratuit), (StatutMemo.BROUILLON, False, True))
        self.assertEqual(list(memo.cursus.all()), [self.cursus])
        memo.definition = "Texte corrigé par l'enseignant."
        memo.modifie_a_la_main = True
        memo.save()
        bilan = extraction.enregistrer(self.subject, extraction.relever(self.subject))
        self.assertEqual(bilan["laissees"], 1)
        memo.refresh_from_db()
        self.assertEqual(memo.definition, "Texte corrigé par l'enseignant.")

    def test_a_versioned_correction_rewrites_a_draft_but_never_a_published_card(self):
        self._question(2019, "**Referendum** : consultation directe du peuple, dans le texte ci-dessus.")
        extraction.enregistrer(self.subject, extraction.relever(self.subject))
        retouche = {"referendum": {"terme": "Référendum", "definition": "Consultation directe du peuple."}}
        with patch.object(extraction, "corrections_de", return_value=retouche):
            self.assertEqual(extraction.enregistrer(self.subject, extraction.relever(self.subject))["creees"], 0)
            memo = Memo.objects.get()
            self.assertEqual((memo.terme, memo.definition), ("Référendum", "Consultation directe du peuple."))
            Memo.objects.filter(pk=memo.pk).update(
                statut=StatutMemo.PUBLIE, relu_par_enseignant=True, definition="Texte relu.", terme="Referendum",
            )
            extraction.enregistrer(self.subject, extraction.relever(self.subject))
        memo.refresh_from_db()
        self.assertEqual((memo.terme, memo.definition), ("Referendum", "Texte relu."))

    def test_the_shipped_corrections_keep_each_card_matched_to_its_term(self):
        toutes = json.loads(extraction.FICHIER_CORRECTIONS.read_text(encoding="utf-8"))
        for matiere, retouches in toutes.items():
            if matiere.startswith("_"):
                continue
            for cle, retouche in retouches.items():
                self.assertEqual(extraction._cle(cle), cle)
                self.assertEqual(extraction._cle(retouche.get("terme", cle)), cle)

    def test_the_shipped_method_cards_are_complete_and_fit_in_a_note(self):
        fichiers = {
            "maths_bepc_methodes": {"Calcul", "Géométrie", "Repère", "Statistiques"},
            "pct_bepc": {"Chimie", "Physique", "Technologie"},
            "info_bepc": {"Matériel et réseaux", "Données et fichiers", "Algorithmique", "Usages du numérique"},
            "svt_bepc": {"Génétique", "Microbes, maladies et défense", "Fonctionnement du corps", "Environnement et géologie"},
            "histoire_bepc": {"Cameroun", "Conquête et colonisation", "Décolonisation", "Le monde au XIXe siècle", "Guerres et crises"},
            "geographie_bepc": {"Population", "Économie et développement", "Milieu et environnement"},
            "francais_bepc": {"Compréhension", "Vocabulaire", "Grammaire", "Orthographe", "Expression écrite"},
            "eps_bepc": {"Athlétisme", "Gymnastique"},
            "anglais_bepc": {"Grammaire", "Vocabulaire", "Compréhension", "Rédaction"},
            "dessin_bepc": {"Couleurs", "Dessin à consignes"},
            "allemand_bepc": {"Grammaire", "Vocabulaire", "Compréhension", "Traduction", "Rédaction"},
            "espagnol_bepc": {"Conjugaison", "Grammaire", "Vocabulaire", "Compréhension", "Traduction", "Rédaction"},
            "maths_probatoire_d": {"Trigonométrie", "Géométrie", "Fonctions", "Algèbre", "Suites", "Statistiques", "Dénombrement"},
            "chimie_probatoire_cde": {"Chimie organique", "Oxydoréduction et piles", "Dosages et expériences", "Engrais"},
            "svt_probatoire_d": {"Cellule et génétique", "Enzymes", "Santé et immunité", "Énergie et métabolisme", "Écologie et cycles", "Énergie solaire et climat", "Géologie"},
            "physique_probatoire_d_ti": {"Optique", "Énergie électrique", "Électromagnétisme", "Électrostatique", "Énergie mécanique", "Chaleur et rayonnement", "Mesures et démarche"},
            "anglais_probatoire": {"Grammaire", "Vocabulaire", "Phrases à compléter", "Compréhension", "Rédaction"},
            "education_civique_bepc": {"Symboles et patrie", "État et exécutif", "Parlement", "Justice et diplomatie", "Élections et démocratie", "Économie et vie associative", "Méthode"},
            "gce_maths_o_level": {"Number", "Algebra", "Sets and logic", "Graphs and functions", "Geometry and trigonometry", "Statistics and probability", "Vectors and matrices"},
            "gce_physics_o_level": {"Mechanics", "Thermal physics", "Waves and optics", "Electricity and magnetism", "Atomic physics"},
            "gce_chemistry_o_level": {"Atoms and bonding", "Moles and equations", "Acids, bases and salts", "Electrolysis and redox", "Organic chemistry", "Rates and energy", "Practical chemistry"},
            "gce_biology_o_level": {"Cells and transport", "Nutrition", "Transport", "Respiration and excretion", "Coordination and response", "Reproduction and genetics", "Ecology", "Practical biology"},
            "gce_human_biology_o_level": {"Cells and genetics", "Nutrition and digestion", "Blood and circulation", "Breathing and excretion", "Coordination and support", "Reproduction", "Health and hygiene"},
            "gce_english_o_level": {"Grammar", "Vocabulary and idioms", "Sounds and spelling", "Comprehension", "Writing"},
            "gce_computer_science_o_level": {"Data representation", "Hardware", "Software and operating systems", "Algorithms and programming", "Networks and security", "Applications", "Systems development"},
            "gce_geography_o_level": {"Map reading", "Physical geography", "Weather and climate", "Agriculture and resources", "Population and settlement", "Industry, transport and trade", "Environment and hazards"},
            "gce_additional_maths_o_level": {"Algebra", "Functions and graphs", "Trigonometry", "Calculus", "Vectors and matrices", "Statistics and probability", "Mechanics"},
            "gce_history_o_level": {"Colonial Cameroon", "Independent Cameroon", "Africa", "Europe and the world wars", "International organisations"},
            "gce_economics_o_level": {"Basic concepts", "Demand, supply and prices", "Production and business", "Money and banking", "Public finance", "National income and development", "International trade"},
            "maths_bac_cd": {"Nombres complexes", "Suites", "Analyse", "Géométrie", "Algèbre linéaire", "Probabilités et statistiques", "Arithmétique"},
            "physique_bac_cd": {"Physique nucléaire et quantique", "Ondes et optique", "Mécanique", "Oscillations", "Électricité", "Mesures et incertitudes", "Champs et particules"},
            "chimie_bac_cd": {"Chimie organique", "Dosages et expériences", "Cinétique", "Chimie générale", "Acides et bases"},
            "svt_bac_cd": {"Génétique", "Neurophysiologie et régulations", "Cellule et métabolisme", "Reproduction", "Immunologie", "Méthode", "Géologie et évolution"},
            "anglais_bac": {"Rédaction", "Grammaire", "Vocabulaire", "Phrases à compléter", "Compréhension"},
            "philosophie_bac": {"Méthode", "L'homme et la conscience", "La connaissance et la science", "La morale et la politique", "La culture et la société"},
            "informatique_bac": {"Réseaux et sécurité", "Bases de données", "Applications", "Systèmes et matériel", "Algorithmique et programmation", "Données et codage"},
            "maths_bac_a": {"Probabilités", "Statistiques", "Algèbre", "Analyse", "Suites"},
            "allemand_bac": {"Compréhension", "Traduction", "Vocabulaire", "Grammaire", "Rédaction"},
            "espagnol_bac": {"Compréhension", "Traduction", "Rédaction", "Grammaire", "Vocabulaire", "Conjugaison"},
            "programmation_bac_ti": {"Algorithmique", "Langage C", "Web et JavaScript", "Structures de données"},
            "systemes_information_bac_ti": {"Modélisation", "Système d'information", "Bases de données", "SQL"},
            "histoire_bac": {"Méthode", "Cameroun", "Afrique", "Monde"},
            "geographie_bac": {"Méthode", "Afrique", "Cameroun", "Grandes puissances", "Monde et mondialisation"},
            "francais_bac": {"Compréhension", "Méthode", "Langue"},
            "litterature_bac": {"Méthode", "Notions", "Genres", "Courants et mouvements"},
            "philosophie_probatoire": {"Étude de texte", "Dissertation", "Culture philosophique"},
            "litterature_probatoire": {"Discussion", "Dissertation", "Contraction", "Commentaire"},
            "francais_probatoire": {"Sémantique", "Stylistique", "Morphosyntaxe", "Communication"},
            "informatique_probatoire": {"Algorithmique et programmation", "Sécurité et système", "Multimédia", "Web", "Systèmes d'information"},
            "allemand_probatoire": {"Compréhension", "Traduction", "Grammaire", "Expression écrite", "Lexique"},
            "espagnol_probatoire": {"Traduction", "Expression écrite", "Compréhension", "Grammaire"},
            "histoire_probatoire": {"Méthode", "Cameroun", "Afrique", "Révolutions et impérialisme", "Première Guerre mondiale", "Chine"},
            "geographie_probatoire": {"Méthode", "Environnement", "Agriculture et industrie", "Milieux et risques naturels", "Population et migrations"},
            "maths_probatoire_a": {"Équations et systèmes", "Statistiques", "Fonctions", "Dénombrement", "Problèmes concrets"},
            "sciences_probatoire_a": {"Génétique", "Nutrition et santé", "Immunité", "Reproduction et cellule", "Environnement et biotechnologie"},
            "physique_chimie_probatoire_a": {"Chimie des champs et environnement", "Chimie organique", "Mécanique", "Optique", "Énergie et ondes"},
            "gce_commerce_o_level": {"Trade and Production", "Documents and Payments", "Business Calculations", "Foreign Trade", "Aids to Trade", "Retail and Wholesale"},
            "gce_citizenship_o_level": {"Society and Environment", "State and Government", "Civic Life and Rights", "Economy and Welfare"},
            "gce_food_nutrition_o_level": {"Foods and Baking", "Nutrition and Health", "Hygiene and Preservation", "Cooking Principles", "Meal Planning and Service"},
            "gce_religious_studies_o_level": {"Love and Family", "Moral Choices", "Society and Justice", "Religious Groups and Beliefs", "The Bible", "Islam"},
            "gce_french_o_level": {"Translation and essay", "Verbs and tenses", "Pronouns and determiners", "Words and expressions", "Agreement"},
            "gce_sbe_french_o_level": {"Citizenship and morals", "Physical education", "French: language and literature", "French: writing"},
            "gce_logic_o_level": {"Syllogisms", "Propositions and inference", "Conditional arguments", "Fallacies", "Symbolic logic", "Principles and definitions"},
            "gce_literature_o_level": {"Characters", "Poetry", "Literary devices", "Extract questions"},
            "gce_geology_o_level": {"Minerals", "Igneous and metamorphic rocks", "Earthquakes", "Structural geology"},
            "gce_pm_mechanics_a_level": {"Algebra and Functions", "Vectors, Matrices and Complex Numbers", "Calculus and Numerical Methods", "Trigonometry", "Mechanics: Forces and Energy", "Mechanics: Motion", "Series and Binomial"},
            "gce_pm_statistics_a_level": {"Data and correlation", "Probability and random variables", "Algebra and series", "Trigonometry and complex numbers", "Calculus and numerical methods", "Sampling and testing", "Vectors and matrices"},
            "gce_physics_a_level": {"Mechanics and measurement", "Matter and thermal physics", "Electricity and fields", "Waves and optics", "Atomic and nuclear physics", "Options"},
            "gce_chemistry_a_level": {"Equilibria and Redox", "Bonding and States", "Moles and Atomic Structure", "Organic Chemistry", "Energetics and Kinetics", "Inorganic Chemistry"},
            "gce_biology_a_level": {"Genetics and biotechnology", "Animal physiology", "Plant biology", "Cells and enzymes", "Respiration and photosynthesis", "Ecology and evolution"},
            "gce_english_a_level": {"Summary and editing", "Prescribed texts", "Composition", "Grammar", "Vocabulary"},
            "gce_french_a_level": {"Conjugation and agreement", "Vocabulary", "Literary terms and poetry", "Grammar", "Essay writing"},
            "gce_computer_science_a_level": {"Databases", "Data representation", "Computer architecture", "Operating systems", "Algorithms and data structures", "Programming", "Logic and Boolean algebra"},
            "gce_ict_a_level": {"Data and logic", "Networks", "Hardware and operating systems", "Systems and projects", "Databases", "Spreadsheets"},
            "gce_history_a_level": {"Reunification and the Federation", "West Africa and European conquest", "Europe and America", "Cameroon, 1916 to 1959", "International relations", "Cameroon before 1916", "Africa in the 20th century"},
            "gce_philosophy_a_level": {"Western philosophy", "Categorical logic", "Arguments and fallacies", "Symbolic logic", "Ethics", "African philosophy"},
            "gce_economics_a_level": {"National income", "Basic concepts", "Firms and markets", "Demand, supply and prices", "Public finance", "Money and banking", "International trade"},
            "gce_geography_a_level": {"Landforms and drainage", "Geography of Cameroon", "Maps, statistics and fieldwork", "Population and settlement", "Economic geography", "Climate, soils and ecosystems"},
            "gce_further_maths_a_level": {"Differential equations", "Calculus", "Mechanics", "Vectors and polar curves", "Complex numbers and hyperbolics", "Algebra and proof", "Probability"},
            "gce_literature_a_level": {"Set-book essays", "Drama extracts", "Unseen poetry", "Language and creative tasks", "Unseen prose"},
            "gce_religious_studies_a_level": {"Essay skills", "Old Testament", "African Traditional Religion", "Philosophy of religion", "Islam", "New Testament"},
            "gce_food_nutrition_a_level": {"Food and society", "Nutrition and health", "Nutrients", "Digestion and enzymes", "Food science", "Food safety and water"},
            "gce_geology_a_level": {"Earth, space and tectonics", "Water and economic geology", "Crystals and minerals", "Igneous rocks and volcanoes", "Sedimentary and metamorphic rocks", "Stratigraphy and structures"},
        }
        for nom, rubriques in fichiers.items():
            donnees = redaction.lire(nom)
            notions = donnees["notions"]
            self.assertEqual(len({n["terme"] for n in notions}), len(notions), nom)
            for n in notions:
                for champ in ("definition", "exemple", "piege", "exercice", "reponse"):
                    self.assertTrue(n.get(champ), f"{n['terme']} : {champ}")
                self.assertIn(n["rubrique"], rubriques)
                self.assertTrue(set(n["epreuves"]) <= set(donnees["epreuves"]), n["terme"])
                note = f"{n['definition']}\n\n{n['exemple']}\n\n**Piège** : {n['piege']}"
                self.assertLessEqual(len(note), 2000, n["terme"])

    @override_settings(MEMOS_MONTRER_BROUILLONS=True)
    def test_in_development_drafts_show_flagged_as_to_review(self):
        m = Memo.objects.create(subject=self.subject, terme="Brouillon", definition="Une définition encore à relire par un enseignant.", gratuit=True)
        m.cursus.add(self.cursus)
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertTrue(data["fiches"][0]["a_relire"])
        self.assertEqual(services.visibles().count(), 1)


@override_settings(MEMOS_MONTRER_BROUILLONS=False)
class FicheDeMethodeTests(_Base):
    BLOCS = {"piege": "Oublier les parenthèses.", "exercice": "Factorise x² - 1.", "reponse": "(x - 1)(x + 1)",
             "rubrique": "Calcul"}

    def fiches(self):
        return self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data["fiches"]

    def test_the_blocks_are_served_with_a_readable_card_and_hidden_on_a_locked_one(self):
        self.memo("Gratuite", gratuit=True, **self.BLOCS)
        self.memo("Payante", **self.BLOCS)
        par_terme = {f["terme"]: f for f in self.fiches()}
        for champ, valeur in self.BLOCS.items():
            self.assertEqual(par_terme["Gratuite"][champ], valeur)
        for champ in ("piege", "exercice", "reponse"):
            self.assertEqual(par_terme["Payante"][champ], "")
        # La rubrique reste : une fiche verrouillée se range avec les autres.
        self.assertEqual(par_terme["Payante"]["rubrique"], "Calcul")

    def test_a_kept_method_card_carries_its_trap_but_not_the_exercise(self):
        fiche = self.memo("Gratuite", gratuit=True, **self.BLOCS)
        self.client.post(f"/memos/fiches/{fiche.pk}/garder/")
        note = NoteLibre.objects.get().note
        self.assertIn("**Piège** : Oublier les parenthèses.", note)
        self.assertNotIn("Factorise", note)
        self.assertNotIn("(x - 1)(x + 1)", note)

    def test_a_gce_card_kept_in_the_notes_names_its_trap_in_english(self):
        fiche = self.memo("How do you factorise?", gratuit=True, **self.BLOCS)
        fiche.cursus.set([Cursus.objects.get(examen=Examen.GCE_OL, country=self.subject.country, series=None)])
        self.client.post(f"/memos/fiches/{fiche.pk}/garder/")
        note = NoteLibre.objects.get().note
        self.assertIn("**The trap**: Oublier les parenthèses.", note)
        self.assertNotIn("Piège", note)

    def test_two_papers_of_the_same_year_are_told_apart_by_their_number(self):
        fiche = self.memo("Gratuite", gratuit=True)
        for numero in (1, 2):
            lesson = Lesson.objects.create(
                title=f"Maths 2024 - Paper {numero}", subject=self.subject, year=2024, numero_paper=numero,
                lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
            )
            lesson.cursus.add(self.cursus)
            fiche.sources.add(lesson)
        sources = self.fiches()[0]["sources"]
        self.assertEqual(sorted((s["annee"], s["paper"]) for s in sources), [(2024, 1), (2024, 2)])
