"""Relances d'absence (voir relances.absence) : deux messages, puis le silence - et le rappel quotidien qui se tait."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.core import mail
from django.utils import timezone

from quiz.models import JourXP, OrigineSeance, SeanceJournaliere, StatutSeance

from . import absence, services
from .activite import comptes_en_pause, jours_sans_travail
from .management.commands.planifier_relances import passer_une_fois
from .models import RelanceEnvoyee, TypeRelance
from .tests import RelancesTestCase

DOUALA = ZoneInfo("Africa/Douala")


class AbsenceTestCase(RelancesTestCase):
    def setUp(self):
        super().setUp()
        self.aujourdhui = timezone.localdate()

    def a_travaille(self, user, il_y_a):
        """Le dernier jour travaillé de l'élève est il y a `il_y_a` jours (des points gagnés ce jour-là)."""
        JourXP.objects.create(profil=user.profils.first(), jour=self.aujourdhui - timedelta(days=il_y_a), xp=20, objectif=50)

    def types_envoyes(self, user):
        return list(RelanceEnvoyee.objects.filter(user=user).order_by("envoyee_at").values_list("type", flat=True))


class ActiviteTests(AbsenceTestCase):
    def test_compte_depuis_le_dernier_jour_travaille_points_ou_seance(self):
        par_points, par_seance = self.eleve(), self.eleve()
        self.a_travaille(par_points, 4)
        SeanceJournaliere.objects.create(
            profil=par_seance.profils.first(), cursus=self.cursus, date=self.aujourdhui - timedelta(days=1),
            origine=OrigineSeance.PARCOURS, statut=StatutSeance.TERMINEE, etapes=[],
        )

        ecoules = jours_sans_travail([par_points.pk, par_seance.pk], self.aujourdhui)

        self.assertEqual(ecoules[par_points.pk][0], 4)
        self.assertEqual(ecoules[par_seance.pk][0], 1)
        self.assertEqual(comptes_en_pause([par_points.pk, par_seance.pk], self.aujourdhui), {par_points.pk})

    def test_un_compte_qui_n_a_jamais_travaille_est_compte_depuis_son_inscription(self):
        user = self.eleve()
        type(user).objects.filter(pk=user.pk).update(date_joined=timezone.now() - timedelta(days=5))

        self.assertEqual(jours_sans_travail([user.pk], self.aujourdhui)[user.pk][0], 5)


class RelancesAbsenceTests(AbsenceTestCase):
    def test_deux_jours_pleins_manques_un_message_et_plus_de_rappel_quotidien(self):
        user = self.eleve()
        self.a_travaille(user, 3)

        self.assertEqual(services.envoyer_rappels_seance(), 0)
        self.assertEqual(absence.envoyer_relances_absence(), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, [user.email])
        self.assertIn("Deux jours sans séance : rien de grave", message.body)
        self.assertIn("/relances/desabonner/", message.body)
        html, type_mime = message.alternatives[0]
        self.assertEqual(type_mime, "text/html")
        self.assertIn("Reprendre ma préparation", html)
        # Rejoué le même soir ou le lendemain (encore dans la fenêtre) : rien de plus.
        self.assertEqual(absence.envoyer_relances_absence(), 0)
        self.assertEqual(absence.envoyer_relances_absence(timezone.now() + timedelta(days=1)), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_un_seul_jour_manque_reste_un_rappel_ordinaire(self):
        user = self.eleve()
        self.a_travaille(user, 2)  # il a manqué hier : le jour de repos que la série pardonne

        self.assertEqual(absence.envoyer_relances_absence(), 0)
        self.assertEqual(services.envoyer_rappels_seance(), 1)
        self.assertEqual(self.types_envoyes(user), [TypeRelance.RAPPEL_SEANCE])

    def test_le_silence_entre_les_deux_messages(self):
        user = self.eleve()
        self.a_travaille(user, 6)

        self.assertEqual(absence.envoyer_relances_absence(), 0)
        self.assertEqual(services.envoyer_rappels_seance(), 0)
        self.assertEqual(mail.outbox, [])

    def test_une_semaine_manquee_le_dernier_message_puis_plus_rien(self):
        user = self.eleve()
        self.a_travaille(user, 8)

        self.assertEqual(absence.envoyer_relances_absence(), 1)
        self.assertIn("C'est notre dernier message", mail.outbox[0].body)
        self.assertEqual(self.types_envoyes(user), [TypeRelance.ABSENCE_2])

        # Les semaines suivantes : ni relance ni rappel, quel que soit le jour.
        for jours in (2, 10, 40):
            plus_tard = timezone.now() + timedelta(days=jours)
            self.assertEqual(absence.envoyer_relances_absence(plus_tard), 0)
            self.assertEqual(services.envoyer_rappels_seance(plus_tard), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_au_retour_le_rappel_reprend_et_une_nouvelle_absence_est_un_nouvel_episode(self):
        user = self.eleve()
        self.a_travaille(user, 3)
        absence.envoyer_relances_absence()

        # Il revient travailler aujourd'hui ; demain, c'est de nouveau le rappel ordinaire.
        self.a_travaille(user, 0)
        demain = timezone.now() + timedelta(days=1)
        self.assertEqual(absence.envoyer_relances_absence(demain), 0)
        self.assertEqual(services.envoyer_rappels_seance(demain), 1)

        # Puis il s'absente de nouveau : trois jours après son retour, une nouvelle première relance.
        dans_trois_jours = timezone.now() + timedelta(days=3)
        self.assertEqual(absence.envoyer_relances_absence(dans_trois_jours), 1)
        self.assertEqual(
            self.types_envoyes(user), [TypeRelance.ABSENCE_1, TypeRelance.RAPPEL_SEANCE, TypeRelance.ABSENCE_1],
        )

    def test_memes_conditions_que_le_rappel_quotidien(self):
        for refuse in (
            self.eleve(rappels=False), self.eleve(email_verifie=False), self.eleve(abonne=False), self.eleve(cursus=False),
        ):
            if refuse.cursus_prepare_id:
                self.a_travaille(refuse, 3)
            else:
                type(refuse).objects.filter(pk=refuse.pk).update(date_joined=timezone.now() - timedelta(days=3))

        self.assertEqual(absence.envoyer_relances_absence(), 0)
        self.assertEqual(mail.outbox, [])

    def test_en_anglais_pour_un_compte_en_anglais(self):
        user = self.eleve()
        type(user).objects.filter(pk=user.pk).update(langue="en")
        self.a_travaille(user, 3)

        absence.envoyer_relances_absence()

        self.assertIn("Two days without a session", mail.outbox[0].body)

    def test_un_essai_a_blanc_ne_trace_et_n_envoie_rien(self):
        user = self.eleve()
        self.a_travaille(user, 3)

        self.assertEqual(absence.envoyer_relances_absence(dry_run=True), 1)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.types_envoyes(user), [])


class PlanificateurAbsenceTests(AbsenceTestCase):
    def test_part_dans_la_fenetre_du_soir_seulement(self):
        user = self.eleve()
        jour = datetime(2026, 9, 28, tzinfo=DOUALA)
        JourXP.objects.create(profil=user.profils.first(), jour=(jour - timedelta(days=3)).date(), xp=20, objectif=50)

        self.assertEqual(passer_une_fois(jour.replace(hour=9))["absence"], 0)
        resultat = passer_une_fois(jour.replace(hour=17, minute=30))
        self.assertEqual((resultat["absence"], resultat["rappel"]), (1, 0))
        self.assertEqual(passer_une_fois(jour.replace(hour=18, minute=30))["absence"], 0)
        self.assertEqual(len(mail.outbox), 1)
