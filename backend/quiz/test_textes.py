"""
Les textes que le serveur écrit lui-même pour l'élève (voir quiz.textes) : la phrase du coach, les raisons d'une
séance, les libellés d'étape. Ce qui casserait la promesse « l'interface anglaise est en anglais » : une clé sans
traduction, une traduction qui perd un chiffre, une phrase française sur l'accueil d'un élève du GCE.
"""
import re
import string
from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, ExamSession, Examen, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from . import accueil, textes
from .models import ModeQuiz, OrigineSeance, SeanceJournaliere
from .services import libelle_etape, raisons_de_la_seance
from .tests import _make_competence_item

# Mots qui n'existent qu'en français dans nos phrases : si l'un d'eux sort d'une phrase anglaise, elle est restée en français.
MOTS_FRANCAIS = re.compile(
    r"\b(tu|ton|ta|tes|toi|ce|cette|thème|séance|minutes pour|jour J|examen|sur|avec|pour|sans|déjà|une|des|les|du|reste|aujourd)\b",
    re.IGNORECASE,
)


def _champs(modele):
    return {nom for _, nom, _, _ in string.Formatter().parse(modele) if nom}


class CatalogueTests(SimpleTestCase):
    def test_chaque_texte_existe_dans_les_deux_langues_avec_les_memes_valeurs(self):
        for cle, variantes in textes.TEXTES.items():
            self.assertEqual(set(variantes), {textes.FR, textes.EN}, cle)
            self.assertEqual(_champs(variantes[textes.FR]), _champs(variantes[textes.EN]), cle)

    def test_les_tables_de_formulations_ont_autant_de_variantes_dans_les_deux_langues(self):
        for table in (textes.FINS_FREQUENCE_PROCHE, textes.FINS_FREQUENCE_LOIN, textes.FINS_REVISION, textes.ACCROCHES_FREQUENCE):
            self.assertEqual(len(table[textes.FR]), len(table[textes.EN]))
        for variante in textes.FINS_REVISION[textes.FR] + textes.FINS_REVISION[textes.EN]:
            self.assertEqual(_champs(variante), {"duree"})

    def test_langue_inconnue_ou_cle_en_francais_seulement_retombent_sur_le_francais(self):
        self.assertEqual(textes.texte("coach.fait", "de"), "Séance faite. Demain, on continue.")
        self.assertEqual(textes.langue_de(None), textes.FR)

    def test_libelles_d_origine(self):
        self.assertEqual(textes.origine("PARCOURS", textes.EN), "Pathway")
        self.assertEqual(textes.origine("PARCOURS", textes.FR), "Parcours")
        self.assertEqual(textes.origine("INCONNUE", textes.EN), "INCONNUE")


JOUR = date.fromordinal(3 * 246000)


class PhraseCoachAnglaisTests(SimpleTestCase):
    def _plan(self, origine="PARCOURS", **seance):
        base = {
            "origine": origine, "theme": {"id": 1, "name": "capacitors"}, "savoir": None,
            "duree_estimee_min": 22, "raisons": [], "frequence": None, "score": None,
        }
        return {"etat": "plan_pret", "seance": {**base, **seance}}

    def test_la_phrase_citee_par_l_utilisateur_existe_en_anglais(self):
        plan = self._plan(frequence={"occurrences": 40, "epreuves_total": 41}, ) | {"compte_a_rebours": {"jours_restants": 200}}
        # Le deuxième des trois mots-clés de la série « loin » est celui de la phrase signalée.
        phrases = {accueil.phrase_coach(plan, "normal", 0, jour=JOUR + timedelta(days=i), langue="en") for i in range(3)}
        self.assertIn("This topic comes up at almost every exam: 22 minutes so it doesn't catch you off guard.", phrases)
        for phrase in phrases:
            self.assertNotRegex(phrase, MOTS_FRANCAIS, phrase)

    def test_le_francais_ne_change_pas(self):
        plan = self._plan(frequence={"occurrences": 40, "epreuves_total": 41}) | {"compte_a_rebours": {"jours_restants": 200}}
        phrases = {accueil.phrase_coach(plan, "normal", 0, jour=JOUR + timedelta(days=i)) for i in range(3)}
        self.assertIn("Ce thème tombe presque à chaque examen : 22 minutes pour qu'il ne te surprenne pas.", phrases)

    def test_aucune_phrase_anglaise_ne_garde_de_francais(self):
        seances = [
            ("normal", self._plan()),
            ("normal", self._plan(origine="DIAGNOSTIC")),
            ("normal", self._plan(origine="LECTURE_EN_COURS")),
            ("normal", self._plan(origine="REVISION_DUE", raisons=[{"code": "echec", "texte": "You got this topic wrong yesterday."}])),
            ("normal", self._plan(origine="REVISION_DUE")),
            ("derniere_ligne_droite", self._plan()),
            ("normal", self._plan(theme=None)),
            ("normal", {"etat": "deja_fait_aujourdhui", "seance": {"score": {"reussies": 4, "total": 5}}}),
            ("normal", {"etat": "deja_fait_aujourdhui", "seance": {"score": None}}),
            ("normal", {"etat": "rien_a_proposer", "seance": None}),
            ("apres", {}), ("jour_j", {}), ("veille", {}),
        ]
        for phase, plan in seances:
            for absence, premiers_pas in ((0, False), (9, False), (9, True)):
                for i in range(3):
                    phrase = accueil.phrase_coach(
                        plan, phase, absence, premiers_pas_eleve=premiers_pas, jour=JOUR + timedelta(days=i), langue="en",
                    )
                    self.assertTrue(phrase.strip(), (phase, plan))
                    self.assertNotRegex(phrase, MOTS_FRANCAIS, (phase, phrase))
                    self.assertNotIn(" ", phrase)

    def test_le_constat_d_echec_est_repris_avec_deux_points_anglais(self):
        plan = self._plan(origine="REVISION_DUE", raisons=[{"code": "echec", "texte": "You got this topic wrong yesterday."}])
        phrase = accueil.phrase_coach(plan, "normal", 0, jour=JOUR, langue="en")
        self.assertTrue(phrase.startswith("You got this topic wrong yesterday: 22 minutes"), phrase)


class LibellesEtapeTests(SimpleTestCase):
    ETAPES = [
        {"type": "cours", "libelle": "Relire la méthode", "slug": "s", "titre": "t"},
        {"type": "quiz", "libelle": "12 questions", "mode": ModeQuiz.PRATIQUE, "n": 12},
        {"type": "quiz", "libelle": "15 questions pour situer ton niveau", "mode": ModeQuiz.DIAGNOSTIC, "n": 15},
        {"type": "exercice", "libelle": "Exercice 3 - Physics GCE A Level 2023 - Paper 2", "numero_exercice": "3",
         "lesson_title": "Physics GCE A Level 2023 - Paper 2"},
    ]

    def test_en_francais_le_libelle_recalcule_est_celui_qui_etait_stocke(self):
        for etape in self.ETAPES:
            self.assertEqual(libelle_etape(etape, "fr"), etape["libelle"])

    def test_en_anglais(self):
        attendus = ["Review the method", "12 questions", "15 questions to find your level",
                    "Exercise 3 - Physics GCE A Level 2023 - Paper 2"]
        self.assertEqual([libelle_etape(e, "en") for e in self.ETAPES], attendus)

    def test_exercice_verrouille_ne_dit_pas_l_epreuve(self):
        exercice = self.ETAPES[3]
        self.assertEqual(libelle_etape(exercice, "fr", verrouillee=True), "Un exercice tombé à l'examen")
        self.assertEqual(libelle_etape(exercice, "en", verrouillee=True), "An exercise from a past exam")

    def test_etape_inconnue_garde_son_libelle(self):
        self.assertEqual(libelle_etape({"type": "autre", "libelle": "x"}, "en"), "x")


class AccueilGceEnAnglaisTests(TestCase):
    """L'accueil d'un élève du GCE : tout ce que le serveur écrit est en anglais, celui d'un élève du BAC reste en français."""

    def setUp(self):
        self.client = APIClient()

    def _eleve(self, telephone, cursus):
        user = User.objects.create_user(phone_number=telephone, password="x")
        user.cursus_prepare = cursus
        user.save(update_fields=["cursus_prepare"])
        subject = Subject.objects.create(code=f"S_{telephone}", label=f"Subject {telephone}", country=cursus.country)
        _make_competence_item(subject, cursus, theme=Tag.objects.create(name=f"theme {telephone}"), numero=f"t-{telephone}")
        Subscription.objects.activate_or_extend(user, cursus, duration_days=200)
        ExamSession.objects.update_or_create(
            country=cursus.country, examen=cursus.examen, annee=2027,
            defaults={"date_debut": timezone.localdate() + timedelta(days=90), "date_fin": timezone.localdate() + timedelta(days=100)},
        )
        self.client.force_authenticate(user=user)
        return user

    def test_eleve_du_gce_tout_en_anglais(self):
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        self._eleve("677900501", cursus)
        data = self.client.get(reverse("quiz:accueil")).json()
        self.assertEqual(data["plan"]["etat"], "plan_pret")
        self.assertNotRegex(data["phrase_coach"], MOTS_FRANCAIS, data["phrase_coach"])
        seance = data["plan"]["seance"]
        for raison in seance["raisons"]:
            self.assertNotRegex(raison["texte"], MOTS_FRANCAIS, raison["texte"])
        for etape in seance["etapes"]:
            self.assertNotRegex(etape["libelle"], MOTS_FRANCAIS, etape["libelle"])
        self.assertEqual(seance["origine_display"], textes.origine(seance["origine"], "en"))

    def test_eleve_du_bac_reste_en_francais(self):
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self._eleve("677900502", cursus)
        data = self.client.get(reverse("quiz:accueil")).json()
        self.assertEqual(data["plan"]["etat"], "plan_pret")
        self.assertRegex(data["phrase_coach"], r"[àâçéèêôù]|\b(tu|ton|ta|On)\b")
        for raison in data["plan"]["seance"]["raisons"]:
            self.assertRegex(raison["texte"], r"\b(tu|ton|ta|On|Ce|Tu)\b")

    def test_raisons_d_une_seance_de_calibrage_en_anglais(self):
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.GCE_AL, series__isnull=True)
        user = User.objects.create_user(phone_number="677900503", password="x")
        seance = SeanceJournaliere.objects.create(
            profil=user.profils.first(), cursus=cursus, date=timezone.localdate(), origine=OrigineSeance.DIAGNOSTIC, etapes=[],
        )
        self.assertEqual(
            raisons_de_la_seance(seance),
            [{"code": "calibrage", "texte": "We don't know yet where you stand - these questions are there to find out."}],
        )
