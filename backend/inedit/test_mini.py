"""Mini-inédites : construction (inedit.mini) et accès réservé aux abonnés (access.has_access_inedite)."""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Country, Cursus, Examen, StatutContenu, Subject
from subscriptions.models import InscriptionInedite, Subscription
from users.models import User

from . import mini
from .models import Blueprint, EpreuveInedite, ExerciceInedite, QuestionInedite


def _epreuve(country, cursus, titre, duree=120):
    sujet = Subject.objects.filter(code="MATHS").first() or Subject.objects.first()
    blueprint = Blueprint.objects.create(
        external_id=f"bp-{titre}", subject=sujet, titre=titre, sections_plan=[], duree_minutes=duree, statut=StatutContenu.VALIDE,
    )
    blueprint.cursus.set([cursus])
    epreuve = EpreuveInedite.objects.create(
        blueprint=blueprint, external_id=f"ep-{titre}", subject=sujet, titre=titre, statut=StatutContenu.VALIDE,
    )
    epreuve.cursus.set([cursus])
    return epreuve


def _ajouter_exercice(epreuve, numero, points="4", renvoi=False, nb_questions=2):
    exercice = ExerciceInedite.objects.create(epreuve=epreuve, numero_exercice=numero, points=points)
    for i in range(1, nb_questions + 1):
        QuestionInedite.objects.create(
            exercice=exercice, numero=str(i), ordre=i, points="2",
            enonce_markdown="D'après l'exercice 1, calculer." if renvoi else f"Question {numero}.{i}",
            corrige_markdown="Corrigé.",
        )
    return exercice


class ConstructionTests(TestCase):
    def setUp(self):
        self.country = Country.objects.get(code="CM")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        # Deux épreuves du même cursus, 120 min, chacune de 3 exercices de 4 points (le 3e renvoie à l'exercice 1).
        self.a = _epreuve(self.country, self.cursus, "A")
        self.b = _epreuve(self.country, self.cursus, "B")
        for epreuve in (self.a, self.b):
            _ajouter_exercice(epreuve, "1")
            _ajouter_exercice(epreuve, "2")
            _ajouter_exercice(epreuve, "3", renvoi=True)

    def test_un_exercice_qui_renvoie_a_un_autre_n_est_pas_retenu(self):
        self.a.blueprint.duree_minutes = 60  # 20 min par exercice : sous le seuil de durée
        self.a.blueprint.save()
        numeros = {c["exercice"].numero_exercice for c in mini.candidats(self.a)}
        self.assertEqual(numeros, {"1", "2"})

    def test_la_duree_est_proportionnelle_et_jamais_plafonnee_artificiellement(self):
        # 3 exercices de 4 pts sur 12 : 120 min x 4/12 = 40 min chacun -> dépasse 35 min, aucun candidat.
        self.assertEqual(mini.candidats(self.a), [])
        self.a.blueprint.duree_minutes = 60  # 20 min par exercice
        self.a.blueprint.save()
        self.b.blueprint.duree_minutes = 60
        self.b.blueprint.save()
        paires = mini.choisir_paires([self.a, self.b], 1)
        self.assertEqual(len(paires), 1)
        self.assertEqual(mini.duree_mini(*paires[0]), 40)

    def test_la_mini_est_une_vraie_epreuve_copiee_et_idempotente(self):
        for epreuve in (self.a, self.b):
            epreuve.blueprint.duree_minutes = 60
            epreuve.blueprint.save()
        rapport = mini.creer_pour_matiere(self.a.subject.code, 1)
        mini_epreuve = EpreuveInedite.objects.get(est_mini=True)
        self.assertEqual(len(rapport), 1)
        self.assertTrue(rapport[0][4])
        self.assertEqual(mini_epreuve.statut, StatutContenu.VALIDE)
        self.assertEqual(list(mini_epreuve.cursus.all()), [self.cursus])
        self.assertEqual([e.numero_exercice for e in mini_epreuve.exercices_ordonnes()], ["1", "2"])
        self.assertEqual(QuestionInedite.objects.filter(exercice__epreuve=mini_epreuve).count(), 4)
        self.assertEqual({s["epreuve"] for s in mini_epreuve.sources_mini}, {self.a.pk, self.b.pk})
        self.assertIn("Question", mini_epreuve.enonce_markdown)
        # les épreuves d'origine ne bougent pas
        self.assertEqual(self.a.exercices.count(), 3)
        # rejouer ne crée rien de plus
        rapport = mini.creer_pour_matiere(self.a.subject.code, 1)
        self.assertFalse(rapport[0][4])
        self.assertEqual(EpreuveInedite.objects.filter(est_mini=True).count(), 1)
        self.assertEqual(Blueprint.objects.filter(external_id__startswith="mini-bp-").count(), 1)

    def test_le_tirage_a_blanc_n_ecrit_rien(self):
        for epreuve in (self.a, self.b):
            epreuve.blueprint.duree_minutes = 60
            epreuve.blueprint.save()
        rapport = mini.creer_pour_matiere(self.a.subject.code, 1, a_blanc=True)
        self.assertEqual(len(rapport), 1)
        self.assertEqual(EpreuveInedite.objects.filter(est_mini=True).count(), 0)


class AccesAbonnesTests(TestCase):
    """La mini-inédite s'ouvre avec un abonnement actif au cursus, sans l'add-on ; l'épreuve complète exige l'add-on."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        self.cursus = Cursus.objects.get(country=self.country, examen=Examen.BAC, series__code="C")
        self.complete = _epreuve(self.country, self.cursus, "Complete")
        self.mini = _epreuve(self.country, self.cursus, "Mini")
        EpreuveInedite.objects.filter(pk=self.mini.pk).update(est_mini=True)
        self.mini.refresh_from_db()
        self.user = User.objects.create_user(phone_number="677400091", password="x")
        self.profil = self.user.profils.first()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def demarrer(self, epreuve):
        return self.client.post("/inedit/tentatives/", {"epreuve": epreuve.pk}, format="json")

    def abonner(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=30),
        )

    def test_sans_abonnement_la_mini_est_fermee(self):
        self.assertEqual(self.demarrer(self.mini).status_code, 403)

    def test_un_abonne_ouvre_la_mini_mais_pas_l_epreuve_complete(self):
        self.abonner()
        self.assertEqual(self.demarrer(self.mini).status_code, 201)
        self.assertEqual(self.demarrer(self.complete).status_code, 403)

    def test_l_addon_seul_n_ouvre_pas_la_mini(self):
        InscriptionInedite.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timezone.timedelta(days=30),
        )
        self.assertEqual(self.demarrer(self.mini).status_code, 403)
        self.assertEqual(self.demarrer(self.complete).status_code, 201)

    def test_la_fiche_dit_mini_et_has_access(self):
        self.abonner()
        data = self.client.get(f"/inedit/epreuves/{self.mini.slug}/").data
        self.assertTrue(data["est_mini"])
        self.assertTrue(data["has_access"])
        self.assertEqual(data["lesson_type_display"], "Mini-inédite")
        complete = self.client.get(f"/inedit/epreuves/{self.complete.slug}/").data
        self.assertFalse(complete["est_mini"])
        self.assertFalse(complete["has_access"])
