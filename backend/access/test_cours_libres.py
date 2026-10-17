"""
Tous les cours sont libres en lecture (décision du 2026-10-14) ; seule la section « exercices d'application »
reste payante. Le verrou est SERVEUR : le texte des exercices ne doit apparaître nulle part dans la réponse
d'un lecteur sans abonnement (ni dans les sections, ni dans le Markdown compilé, ni dans l'aperçu public).
"""
import json
from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import (
    Cours, Cursus, Examen, Exercise, Lesson, LessonType, RappelDeMethode, StatutContenu, Subject,
)
from subscriptions.models import Subscription
from users.models import Profil, User

from .models import LectureProgress
from .services import a_acces_exercices_cours, has_access

ENONCE_1, SOLUTION_1 = "ENONCE_SECRET_UN", "SOLUTION_SECRET_UN"
ENONCE_2, SOLUTION_2 = "ENONCE_SECRET_DEUX", "SOLUTION_SECRET_DEUX"
SECRETS = (ENONCE_1, SOLUTION_1, ENONCE_2, SOLUTION_2)

SECTIONS = [
    {"type": "accroche", "contenu_markdown": "ACCROCHE_LIBRE"},
    {"type": "prerequis", "items": ["PREREQUIS_LIBRE"]},
    {"type": "regle", "titre": "La regle", "contenu_markdown": "REGLE_LIBRE", "variantes": []},
    {"type": "exemple_resolu", "enonce_markdown": "EXEMPLE_LIBRE", "etapes": [
        {"numero": 1, "action": "ETAPE_LIBRE", "justification": "Parce que.", "resultat_markdown": "R"}],
     "conclusion_markdown": "CONCLUSION_LIBRE"},
    {"type": "erreurs_classiques", "items": [
        {"erreur_markdown": "ERREUR_LIBRE", "pourquoi_faux": "Faux.", "correction_markdown": "Juste."}]},
    {"type": "exercices_application", "items": [
        {"numero": 1, "difficulte": "facile", "enonce_markdown": ENONCE_1, "solution_markdown": SOLUTION_1},
        {"numero": 2, "difficulte": "moyen", "enonce_markdown": ENONCE_2, "solution_markdown": SOLUTION_2}]},
    {"type": "synthese", "items_markdown": ["SYNTHESE_LIBRE"]},
]


class _Base(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus_c = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.cursus_d = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        self.cours = Cours.objects.create(
            titre="Resolution d'equations", subject=self.subject, statut=StatutContenu.VALIDE, sections_raw=SECTIONS,
        )
        self.cours.compile_from_sections()
        self.cours.cursus.add(self.cursus_c)
        self.user = User.objects.create_user(phone_number="677100301", password="x")
        self.profil = self.user.profils.first()
        self.client = APIClient()

    def _abonner(self, cursus, jours=1, profil=None):
        Subscription.objects.create(
            user=self.user, profil=profil or self.profil, cursus=cursus, expires_at=timezone.now() + timedelta(days=jours),
        )

    def _lire(self, cours=None, *, connecte=True):
        if connecte:
            self.client.force_authenticate(user=self.user)
        return self.client.get(f"/access/cours/read/{(cours or self.cours).slug}/")

    def assertSansSecret(self, response):
        brut = json.dumps(response.json(), ensure_ascii=False)
        for secret in SECRETS:
            self.assertNotIn(secret, brut)


class LectureLibreTests(_Base):
    def test_un_visiteur_anonyme_lit_le_cours_sans_les_exercices(self):
        reponse = self._lire(connecte=False)

        self.assertEqual(reponse.status_code, 200)
        self.assertSansSecret(reponse)
        for libre in ("ACCROCHE_LIBRE", "REGLE_LIBRE", "EXEMPLE_LIBRE", "ERREUR_LIBRE", "SYNTHESE_LIBRE"):
            self.assertIn(libre, json.dumps(reponse.json(), ensure_ascii=False))
        self.assertIn("EXEMPLE_LIBRE", reponse.json()["content_markdown"])
        self.assertIn("SYNTHESE_LIBRE", reponse.json()["content_markdown"])
        self.assertFalse(reponse.json()["exercices_acces"])
        self.assertFalse(LectureProgress.objects.filter(cours=self.cours).exists())

    def test_un_connecte_sans_abonnement_lit_aussi_et_son_suivi_est_enregistre(self):
        reponse = self._lire()

        self.assertEqual(reponse.status_code, 200)
        self.assertSansSecret(reponse)
        self.assertFalse(reponse.json()["exercices_acces"])
        self.assertTrue(LectureProgress.objects.filter(profil=self.profil, cours=self.cours).exists())

    def test_la_section_verrouillee_garde_sa_place_et_annonce_son_contenu_sans_le_donner(self):
        sections = self._lire(connecte=False).json()["sections"]

        self.assertEqual(
            [s["type"] for s in sections],
            ["accroche", "prerequis", "regle", "exemple_resolu", "erreurs_classiques", "exercices_application", "synthese"],
        )
        verrou = sections[5]
        self.assertTrue(verrou["verrouille"])
        self.assertEqual(verrou["nb_exercices"], 2)
        self.assertEqual(verrou["difficultes"], ["facile", "moyen"])
        self.assertEqual(verrou["items"], [])

    def test_le_markdown_compile_sans_les_exercices_garde_le_reste_dans_l_ordre(self):
        contenu = self._lire(connecte=False).json()["content_markdown"]

        self.assertLess(contenu.index("ERREUR_LIBRE"), contenu.index("SYNTHESE_LIBRE"))

    def test_l_apercu_public_ne_montre_pas_les_exercices_mais_montre_le_reste_du_cours(self):
        reponse = self.client.get(f"/access/cours/preview/{self.cours.slug}/")

        self.assertEqual(reponse.status_code, 200)
        self.assertSansSecret(reponse)
        self.assertIn("EXEMPLE_LIBRE", reponse.json()["preview_markdown"])

    def test_un_cours_cite_par_une_epreuve_gratuite_ne_libere_pas_ses_exercices(self):
        gratuite = Lesson.objects.create(
            title="Epreuve gratuite", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, est_vitrine=True,
        )
        exercice = Exercise.objects.create(lesson=gratuite, numero_exercice="1", statut=StatutContenu.VALIDE)
        RappelDeMethode.objects.create(
            exercise=exercice, external_id="rdm-test-libre", competence="T", contenu_markdown="C.", cours=self.cours,
        )

        reponse = self._lire(connecte=False)

        self.assertEqual(reponse.status_code, 200)
        self.assertSansSecret(reponse)
        self.assertFalse(a_acces_exercices_cours(AnonymousUser(), self.cours))


class ExercicesReservesAuxAbonnesTests(_Base):
    def test_un_abonne_du_cursus_a_les_exercices_et_leurs_solutions(self):
        self._abonner(self.cursus_c)

        reponse = self._lire()
        brut = json.dumps(reponse.json(), ensure_ascii=False)

        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.json()["exercices_acces"])
        for secret in SECRETS:
            self.assertIn(secret, brut)
        section = next(s for s in reponse.json()["sections"] if s["type"] == "exercices_application")
        self.assertFalse(section.get("verrouille", False))
        self.assertEqual(len(section["items"]), 2)
        self.assertIn(ENONCE_1, reponse.json()["content_markdown"])

    def test_un_abonne_d_un_autre_cursus_n_a_pas_les_exercices(self):
        self._abonner(self.cursus_d)

        reponse = self._lire()

        self.assertSansSecret(reponse)
        self.assertFalse(reponse.json()["exercices_acces"])

    def test_un_abonnement_expire_ne_donne_pas_les_exercices(self):
        self._abonner(self.cursus_c, jours=-1)

        reponse = self._lire()

        self.assertSansSecret(reponse)
        self.assertFalse(reponse.json()["exercices_acces"])

    def test_l_abonnement_d_un_autre_profil_du_compte_ne_donne_pas_les_exercices(self):
        autre = Profil.objects.create(compte=self.user, prenom="Zaza", ordre=1)
        self._abonner(self.cursus_c, profil=autre)

        reponse = self._lire()  # profil actif = le premier profil, sans abonnement à son nom

        self.assertSansSecret(reponse)

    def test_un_cours_sans_cursus_se_deverrouille_avec_n_importe_quel_abonnement_actif(self):
        commun = Cours.objects.create(
            external_id="cours-test-commun", titre="Notion commune", subject=self.subject,
            statut=StatutContenu.VALIDE, sections_raw=SECTIONS,
        )
        commun.compile_from_sections()

        self.assertSansSecret(self._lire(commun))
        self._abonner(self.cursus_d)
        self.assertTrue(self._lire(commun).json()["exercices_acces"])


class RegleServiceTests(_Base):
    def test_un_cours_est_toujours_lisible(self):
        self.assertTrue(has_access(AnonymousUser(), self.cours))
        self.assertTrue(has_access(self.user, self.cours, self.profil))

    def test_les_exercices_demandent_un_abonnement_du_cursus(self):
        self.assertFalse(a_acces_exercices_cours(AnonymousUser(), self.cours))
        self.assertFalse(a_acces_exercices_cours(self.user, self.cours, self.profil))
        self._abonner(self.cursus_c)
        self.assertTrue(a_acces_exercices_cours(self.user, self.cours, self.profil))


class ListesEtEtudeTests(_Base):
    def test_la_liste_publique_des_cours_ne_les_presente_plus_comme_verrouilles(self):
        reponse = self.client.get("/catalog/cours/")

        ligne = next(c for c in reponse.json()["results"] if c["slug"] == self.cours.slug)
        self.assertTrue(ligne["has_access"])
        self.assertEqual(ligne["apercu_contenu"]["exercices_count"], 2)

    def test_le_detail_d_un_cours_est_lisible_sans_abonnement(self):
        reponse = self.client.get(f"/catalog/cours/{self.cours.slug}/")

        self.assertTrue(reponse.json()["has_access"])
        self.assertSansSecret(reponse)

    def test_un_connecte_sans_abonnement_peut_annoter_un_cours(self):
        self.client.force_authenticate(user=self.user)

        reponse = self.client.get(f"/access/etude/?cours={self.cours.slug}")

        self.assertEqual(reponse.status_code, 200)
