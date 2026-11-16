"""
L'avis laissé dans l'application (voir catalog.avis) : jamais public sans consentement ni relecture, demandé une seule
fois, et seulement après un usage réel.
"""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from quiz.models import ModeQuiz, QuizSession
from users.models import Profil, User

from .avis import SEUIL_QUIZ
from .models import Cursus, Examen, OrigineTemoignage, Temoignage


class AvisTests(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")
        self.user = User.objects.create_user(phone_number="677300001", password="x")
        self.profil = self.user.profils.first()
        self.profil.prenom = "Aïcha"
        self.profil.cursus_prepare = self.cursus
        self.profil.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _quiz_termines(self, n, profil=None):
        for _ in range(n):
            QuizSession.objects.create(
                profil=profil or self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE, completed_at=timezone.now(),
            )

    def _envoyer(self, **corps):
        base = {"origine": "ELEVE", "note": 5, "contenu": "Les corrigés m'ont aidée.", "prenom": "Aïcha",
                "consentement": True, "langue": "fr"}
        return self.client.post("/catalog/avis/", {**base, **corps}, format="json")

    # --- quand demander -----------------------------------------------------------------------

    def test_rien_n_est_demande_avant_le_troisieme_quiz(self):
        self._quiz_termines(SEUIL_QUIZ - 1)
        etat = self.client.get("/catalog/avis/").json()
        self.assertEqual((etat["eleve"], etat["parent"]), (False, False))
        self.assertEqual(self._envoyer().status_code, 409)
        self.assertFalse(Temoignage.objects.exists())

    def test_un_quiz_abandonne_ne_compte_pas(self):
        self._quiz_termines(SEUIL_QUIZ - 1)
        QuizSession.objects.create(profil=self.profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        self.assertFalse(self.client.get("/catalog/avis/").json()["eleve"])

    def test_au_troisieme_quiz_l_avis_est_demande_avec_le_prenom_et_l_examen(self):
        self._quiz_termines(SEUIL_QUIZ)
        etat = self.client.get("/catalog/avis/").json()
        self.assertTrue(etat["eleve"])
        self.assertEqual(etat["prenom"], "Aïcha")
        self.assertIn("BAC", etat["examen"])

    def test_un_visiteur_n_a_pas_acces(self):
        self.assertEqual(APIClient().get("/catalog/avis/").status_code, 401)

    def test_un_compte_invite_n_est_jamais_sollicite(self):
        self._quiz_termines(SEUIL_QUIZ)
        self.user.est_invite = True
        self.user.save(update_fields=["est_invite"])
        self.assertFalse(self.client.get("/catalog/avis/").json()["eleve"])
        self.assertEqual(self._envoyer().status_code, 409)

    # --- l'envoi ------------------------------------------------------------------------------

    def test_l_avis_arrive_en_brouillon_avec_prenom_et_examen_seulement(self):
        self._quiz_termines(SEUIL_QUIZ)
        self.assertEqual(self._envoyer().status_code, 201)
        avis = Temoignage.objects.get()
        self.assertFalse(avis.est_publie)
        self.assertEqual(avis.origine, OrigineTemoignage.ELEVE)
        self.assertEqual((avis.profil, avis.cursus, avis.langue), (self.profil, self.cursus, "fr"))
        self.assertEqual(avis.auteur_nom, "Aïcha")
        self.assertIn("BAC", avis.auteur_description)
        self.assertIsNotNone(avis.consentement_at)
        # Rien de public tant que personne n'a relu.
        self.assertEqual(self.client.get("/catalog/temoignages/").json(), [])

    def test_une_seule_fois_par_eleve(self):
        self._quiz_termines(SEUIL_QUIZ)
        self.assertEqual(self._envoyer().status_code, 201)
        self.assertFalse(self.client.get("/catalog/avis/").json()["eleve"])
        self.assertEqual(self._envoyer().status_code, 409)
        self.assertEqual(Temoignage.objects.count(), 1)

    def test_sans_la_case_l_avis_est_garde_mais_ne_se_publie_pas(self):
        self._quiz_termines(SEUIL_QUIZ)
        self.assertEqual(self._envoyer(consentement=False, prenom="").status_code, 201)
        avis = Temoignage.objects.get()
        self.assertIsNone(avis.consentement_at)
        self.assertEqual(avis.auteur_nom, "Élève")
        avis.est_publie = True
        with self.assertRaises(ValidationError):
            avis.full_clean()
        # Même publié de force (script, import), il ne sort pas.
        Temoignage.objects.filter(pk=avis.pk).update(est_publie=True)
        self.assertEqual(self.client.get("/catalog/temoignages/").json(), [])

    def test_une_case_cochee_par_une_valeur_non_booleenne_ne_vaut_pas_accord(self):
        self._quiz_termines(SEUIL_QUIZ)
        self.assertEqual(self._envoyer(consentement="false").status_code, 201)
        self.assertIsNone(Temoignage.objects.get().consentement_at)

    def test_une_note_seule_est_acceptee_mais_pas_publiable(self):
        self._quiz_termines(SEUIL_QUIZ)
        self.assertEqual(self._envoyer(contenu="").status_code, 201)
        avis = Temoignage.objects.get()
        self.assertEqual((avis.note, avis.contenu), (5, ""))
        self.assertFalse(avis.publiable)

    def test_le_prenom_refuse_un_numero_ou_une_adresse(self):
        self._quiz_termines(SEUIL_QUIZ)
        for prenom in ("677300001", "aicha@exemple.cm", "Aïcha 2", ""):
            self.assertEqual(self._envoyer(prenom=prenom).status_code, 400, prenom)
        self.assertFalse(Temoignage.objects.exists())
        self.assertEqual(self._envoyer(prenom="  Marie-Claire  ").status_code, 201)
        self.assertEqual(Temoignage.objects.get().auteur_nom, "Marie-Claire")

    def test_note_et_longueur_sont_bornees(self):
        self._quiz_termines(SEUIL_QUIZ)
        for corps in ({"note": 0}, {"note": 6}, {"note": "beaucoup"}, {"contenu": "x" * 601}, {"origine": "ADMIN"}):
            self.assertEqual(self._envoyer(**corps).status_code, 400, corps)
        self.assertFalse(Temoignage.objects.exists())

    # --- le parent ----------------------------------------------------------------------------

    def test_le_parent_donne_son_avis_a_part_de_celui_de_l_eleve(self):
        enfant = Profil.objects.create(compte=self.user, prenom="Junior", cursus_prepare=self.cursus)
        # Les quiz du compte comptent tous profils confondus pour le parent, pas pour l'élève actif.
        self._quiz_termines(SEUIL_QUIZ, profil=enfant)
        etat = self.client.get("/catalog/avis/").json()
        self.assertEqual((etat["eleve"], etat["parent"]), (False, True))

        self.assertEqual(self._envoyer(origine="PARENT", prenom="Brigitte", contenu="Mon fils révise seul.").status_code, 201)
        avis = Temoignage.objects.get()
        self.assertEqual((avis.origine, avis.auteur_nom, avis.auteur_description),
                         (OrigineTemoignage.PARENT, "Brigitte", "Parent d'élève"))
        self.assertFalse(self.client.get("/catalog/avis/").json()["parent"])
        self.assertEqual(self._envoyer(origine="PARENT").status_code, 409)

    # --- relecture et retrait -----------------------------------------------------------------

    def test_un_avis_relu_et_publie_sort_dans_sa_langue_sans_rien_dire_du_compte(self):
        self._quiz_termines(SEUIL_QUIZ)
        self._envoyer()
        avis = Temoignage.objects.get()
        avis.est_publie = True
        avis.full_clean()
        avis.save()
        publics = self.client.get("/catalog/temoignages/?langue=fr").json()
        self.assertEqual(len(publics), 1)
        self.assertEqual(set(publics[0]), {"id", "auteur_nom", "auteur_description", "contenu", "note"})
        self.assertEqual(self.client.get("/catalog/temoignages/?langue=en").json(), [])

    def test_supprimer_le_compte_depublie_l_avis_sans_le_supprimer(self):
        self._quiz_termines(SEUIL_QUIZ)
        self._envoyer()
        Temoignage.objects.update(est_publie=True)
        QuizSession.objects.all().delete()
        self.user.delete()
        avis = Temoignage.objects.get()
        self.assertFalse(avis.est_publie)
        self.assertIsNone(avis.profil)

    def test_l_admin_ne_peut_modifier_ni_la_provenance_ni_le_consentement(self):
        lecture_seule = admin.site._registry[Temoignage].readonly_fields
        for champ in ("origine", "profil", "consentement_at"):
            self.assertIn(champ, lecture_seule)

    def test_un_avis_saisi_dans_l_admin_se_publie_comme_avant(self):
        avis = Temoignage(auteur_nom="Awa", contenu="Très utile.", est_publie=True)
        avis.full_clean()
        avis.save()
        self.assertEqual(len(self.client.get("/catalog/temoignages/").json()), 1)
