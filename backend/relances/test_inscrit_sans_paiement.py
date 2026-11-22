"""Inscrit sans paiement (voir relances.inscrit_sans_paiement) : deux messages après l'ouverture de l'écran d'abonnement,
deux au plus par période de 30 jours, puis rien."""
from datetime import date, datetime, timedelta
from io import StringIO
from unittest import mock
from zoneinfo import ZoneInfo

from django.core import mail
from django.core.management import call_command
from django.utils import timezone

from analytics.models import AnalyticsEvent, EventName
from catalog.models import Country, Cursus
from payments.models import ManualPayment, ManualPaymentStatus, StatutTransaction, Transaction
from subscriptions.models import Campagne, DureeMode, Plan, Subscription
from users.models import User

from . import inscrit_sans_paiement, services
from .management.commands.planifier_relances import passer_une_fois
from .models import FamilleRelance, RefusRelance, RelanceEnvoyee, TypeRelance
from .tests import RelancesTestCase

DOUALA = ZoneInfo("Africa/Douala")
# Un jeudi soir, dans la fenêtre d'envoi de l'ordonnanceur.
SOIR = datetime(2026, 12, 10, 17, 30, tzinfo=DOUALA)
# Rien, dans aucun des quatre textes, ne doit presser.
PRESSION = (
    "dernière chance", "plus que", "vite", "dépêche", "il reste", "jours avant", "expire", "offre",
    "last chance", "hurry", "days left", "only", "expires", "offer", "!",
)

envoyer = inscrit_sans_paiement.envoyer_relances_inscrit_sans_paiement


class InscritSansPaiementTestCase(RelancesTestCase):
    def setUp(self):
        super().setUp()
        # Un seul plan au mois pour cet examen, au prix connu du test.
        Plan.objects.filter(cursus=self.cursus, duration_mode=DureeMode.MENSUEL).update(is_active=False)
        self.plan_au_mois = Plan.objects.create(
            name="Au mois", cursus=self.cursus, price=2000, duration_mode=DureeMode.MENSUEL,
        )

    def inscrit(self, **options):
        """Un compte inscrit, adresse confirmée, sans abonnement et sans rappels demandés."""
        options.setdefault("abonne", False)
        options.setdefault("rappels", False)
        return self.eleve(**options)

    def ouvre(self, user, il_y_a, *, avant=SOIR, **proprietes):
        """Le compte a ouvert l'écran d'abonnement `il_y_a` avant `avant`."""
        evenement = AnalyticsEvent.objects.create(name=EventName.ABONNEMENT_OUVERT, user=user, properties=proprietes)
        AnalyticsEvent.objects.filter(pk=evenement.pk).update(created_at=avant - il_y_a)
        return evenement

    def inscrit_qui_a_ouvert(self, il_y_a=timedelta(days=1), **options):
        user = self.inscrit(**options)
        self.ouvre(user, il_y_a, cursus_id=self.cursus.pk)
        return user

    def traces(self, user):
        return list(RelanceEnvoyee.objects.filter(user=user).order_by("reference", "type").values_list("type", "reference"))


class SelectionTests(InscritSansPaiementTestCase):
    def test_le_lendemain_un_message_au_compte_avec_le_lien_direct_et_le_prix(self):
        user = self.inscrit_qui_a_ouvert()

        self.assertEqual(envoyer(SOIR), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, [user.email])
        self.assertEqual(message.subject, "Ce qu'ouvre l'abonnement EduKora")
        self.assertIn("Bonjour Awa,", message.body)
        self.assertIn(f"/abonnement?cursus={self.cursus.pk}&profil={user.profils.first().pk}", message.body)
        self.assertIn("Il coûte 2 000 FCFA par mois.", message.body)
        self.assertIn("Aucun prélèvement automatique", message.body)
        self.assertIn("/relances/desabonner-offre/", message.body)
        self.assertNotIn("dernier message", message.body)
        self.assertEqual(message.reply_to, [services.settings.SUPPORT_EMAIL])
        # La trace porte la date de l'envoi, pas l'évènement ni l'examen.
        self.assertEqual(self.traces(user), [(TypeRelance.INSCRIT_SANS_PAIEMENT_1, "2026-12-10")])

    def test_rien_avant_vingt_heures_et_une_seule_fois_ensuite(self):
        self.inscrit_qui_a_ouvert(timedelta(hours=19))

        self.assertEqual(envoyer(SOIR), 0)
        self.assertEqual(envoyer(SOIR + timedelta(hours=1)), 1)
        self.assertEqual(envoyer(SOIR + timedelta(hours=2)), 0)
        self.assertEqual(envoyer(SOIR + timedelta(days=1)), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_le_dernier_message_entre_trois_et_sept_jours_puis_plus_rien(self):
        user = self.inscrit_qui_a_ouvert(timedelta(days=1))

        envoyes = [envoyer(SOIR + timedelta(days=jour)) for jour in range(10)]

        # Le lendemain de l'ouverture, puis quand elle a trois jours ; rien les jours suivants.
        self.assertEqual(envoyes, [1, 0, 1, 0, 0, 0, 0, 0, 0, 0])
        dernier = mail.outbox[1]
        self.assertEqual(dernier.subject, "Un dernier mot sur l'abonnement EduKora")
        self.assertIn("C'est notre dernier message à ce sujet.", dernier.body)
        self.assertEqual(self.traces(user), [
            (TypeRelance.INSCRIT_SANS_PAIEMENT_1, "2026-12-10"), (TypeRelance.INSCRIT_SANS_PAIEMENT_2, "2026-12-12"),
        ])

    def test_une_ouverture_de_plus_de_sept_jours_ne_declenche_rien(self):
        self.inscrit_qui_a_ouvert(timedelta(days=7, hours=1))
        self.assertEqual(envoyer(SOIR), 0)

    def test_pas_de_dernier_message_sans_premier(self):
        # L'ordonnanceur était arrêté pendant la première fenêtre : « notre dernier message » ne peut pas être le seul.
        self.inscrit_qui_a_ouvert(timedelta(days=4))
        self.assertEqual(envoyer(SOIR), 0)
        self.assertEqual(mail.outbox, [])

    def test_le_dernier_ne_suit_jamais_le_premier_de_moins_de_deux_jours(self):
        self.inscrit_qui_a_ouvert(timedelta(days=2, hours=23))

        self.assertEqual(envoyer(SOIR), 1)
        # Une heure plus tard l'ouverture a trois jours : pas deux messages le même soir, ni le lendemain.
        self.assertEqual(envoyer(SOIR + timedelta(hours=1)), 0)
        self.assertEqual(envoyer(SOIR + timedelta(days=1)), 0)
        self.assertEqual(envoyer(SOIR + timedelta(days=2)), 1)

    def test_c_est_la_derniere_ouverture_qui_compte(self):
        user = self.inscrit_qui_a_ouvert(timedelta(days=5))
        # Il vient de rouvrir l'écran : il est peut-être en train de payer.
        self.ouvre(user, timedelta(hours=2), cursus_id=self.cursus.pk)

        self.assertEqual(envoyer(SOIR), 0)
        self.assertEqual(envoyer(SOIR + timedelta(days=1)), 1)

    def test_le_reglage_rappels_ne_change_rien_comme_pour_le_paiement_non_abouti(self):
        self.inscrit_qui_a_ouvert(rappels=False)
        self.inscrit_qui_a_ouvert(rappels=True, email="autre@example.com")

        self.assertEqual(envoyer(SOIR), 2)


class PlafondTests(InscritSansPaiementTestCase):
    def soirs(self, user, jours):
        """Le compte rouvre l'écran tous les quatre jours, au matin ; l'ordonnanceur passe chaque soir."""
        for jour in range(jours):
            if jour % 4 == 0:
                self.ouvre(user, timedelta(hours=9), avant=SOIR + timedelta(days=jour), cursus_id=self.cursus.pk)
            envoyer(SOIR + timedelta(days=jour))
        return [date.fromisoformat(reference) for _type, reference in self.traces(user)]

    def test_deux_messages_en_trente_jours_meme_s_il_rouvre_l_ecran_huit_fois(self):
        user = self.inscrit()

        jours = self.soirs(user, 30)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(jours, [date(2026, 12, 11), date(2026, 12, 13)])

    def test_une_nouvelle_periode_apres_trente_jours_jamais_trois_messages_en_trente_jours(self):
        user = self.inscrit()

        jours = self.soirs(user, 75)

        self.assertGreater(len(jours), 2)
        self.assertEqual(len(mail.outbox), len(jours))
        for premier, troisieme in zip(jours, jours[2:]):
            self.assertGreaterEqual((troisieme - premier).days, 30)

    def test_changer_d_examen_ne_donne_pas_droit_a_un_message_de_plus(self):
        autre = Cursus.objects.filter(country__actif=True).exclude(pk=self.cursus.pk).first()
        if autre is None:
            self.skipTest("Un seul cursus actif dans la base de test.")
        user = self.inscrit_qui_a_ouvert()
        envoyer(SOIR)

        self.ouvre(user, timedelta(hours=21), avant=SOIR + timedelta(days=1), cursus_id=autre.pk)

        self.assertEqual(envoyer(SOIR + timedelta(days=1)), 0)


class ExclusionTests(InscritSansPaiementTestCase):
    def test_un_compte_invite_n_est_pas_relance(self):
        user = self.inscrit_qui_a_ouvert()
        User.objects.filter(pk=user.pk).update(est_invite=True)
        self.assertEqual(envoyer(SOIR), 0)

    def test_un_compte_desactive_n_est_pas_relance(self):
        user = self.inscrit_qui_a_ouvert()
        User.objects.filter(pk=user.pk).update(is_active=False)
        self.assertEqual(envoyer(SOIR), 0)

    def test_pas_d_adresse_confirmee_pas_de_message(self):
        self.inscrit_qui_a_ouvert(email_verifie=False)
        self.assertEqual(envoyer(SOIR), 0)

    def test_sans_ouverture_rattachee_au_compte_pas_de_message(self):
        self.inscrit()
        # Un visiteur anonyme a ouvert l'écran, et le compte a fait autre chose.
        self.ouvre(None, timedelta(days=1), cursus_id=self.cursus.pk)
        autre = self.inscrit(email="autre@example.com")
        evenement = self.ouvre(autre, timedelta(days=1))
        AnalyticsEvent.objects.filter(pk=evenement.pk).update(name=EventName.TARIFS_VUS)

        self.assertEqual(envoyer(SOIR), 0)

    def test_un_acces_en_cours_pas_de_message(self):
        user = self.inscrit_qui_a_ouvert()
        Subscription.objects.create(
            user=user, profil=user.profils.first(), cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )
        self.assertEqual(envoyer(SOIR), 0)

    def test_un_paiement_reussi_meme_ancien_pas_de_message(self):
        user = self.inscrit_qui_a_ouvert()
        self.transaction(user, StatutTransaction.SUCCESSFUL, timedelta(days=60))
        self.assertEqual(envoyer(SOIR), 0)

    def test_un_paiement_declare_en_verification_ou_valide_pas_de_message(self):
        for rang, statut in enumerate((ManualPaymentStatus.PENDING, ManualPaymentStatus.APPROVED)):
            user = self.inscrit_qui_a_ouvert(email=f"declare{rang}@example.com")
            ManualPayment.objects.create(
                user=user, profil=user.profils.first(), plan=self.plan_au_mois, operator="MTN", amount_expected=2000,
                amount_declared=2000, payer_phone_number="677000000", transaction_reference=f"REF{rang}", status=statut,
            )

        self.assertEqual(envoyer(SOIR), 0)

    def test_aucun_examen_connu_pas_de_message(self):
        user = self.inscrit(cursus=False)
        self.ouvre(user, timedelta(days=1))
        self.assertEqual(envoyer(SOIR), 0)

    def test_un_pays_ferme_pas_de_message(self):
        self.inscrit_qui_a_ouvert()
        Country.objects.filter(pk=self.cursus.country_id).update(actif=False)
        self.assertEqual(envoyer(SOIR), 0)

    def test_examen_passe_rien_a_vendre(self):
        self.inscrit_qui_a_ouvert()
        with mock.patch.object(inscrit_sans_paiement, "_examen_passe", return_value=True):
            self.assertEqual(envoyer(SOIR), 0)
        self.assertEqual(envoyer(SOIR), 1)

    def test_le_compte_qui_a_ouvert_le_lien_d_arret_ne_recoit_plus_rien(self):
        user = self.inscrit_qui_a_ouvert(rappels=True)
        envoyer(SOIR)

        reponse = self.client.get(f"/relances/desabonner-offre/{inscrit_sans_paiement.jeton_arret(user)}/")

        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Tu ne recevras plus de message au sujet de l&#x27;abonnement.")
        self.assertTrue(RefusRelance.objects.filter(user=user, famille=FamilleRelance.INSCRIT_SANS_PAIEMENT).exists())
        self.assertEqual(envoyer(SOIR + timedelta(days=2)), 0)
        # Définitif : une nouvelle ouverture, des mois plus tard, n'y change rien.
        self.ouvre(user, timedelta(days=1), avant=SOIR + timedelta(days=90), cursus_id=self.cursus.pk)
        self.assertEqual(envoyer(SOIR + timedelta(days=90)), 0)
        # Ses autres réglages ne sont pas touchés, et le lien se rouvre sans erreur.
        user.refresh_from_db()
        self.assertTrue(user.rappels_actifs)
        self.assertEqual(self.client.get(f"/relances/desabonner-offre/{inscrit_sans_paiement.jeton_arret(user)}/").status_code, 200)
        self.assertEqual(RefusRelance.objects.filter(user=user).count(), 1)

    def test_un_lien_d_arret_altere_ou_d_un_autre_message_est_refuse(self):
        user = self.inscrit_qui_a_ouvert()

        self.assertEqual(self.client.get("/relances/desabonner-offre/faux-jeton/").status_code, 400)
        self.assertEqual(
            self.client.get(f"/relances/desabonner-offre/{services.jeton_desabonnement(user)}/").status_code, 400,
        )
        self.assertFalse(RefusRelance.objects.exists())


class PrioritePaiementTests(InscritSansPaiementTestCase):
    def tentative(self, user, statut, il_y_a):
        transaction = Transaction.objects.create(
            user=user, profil=user.profils.first(), plan=self.plan_au_mois, amount=2000, phone_number="677000000",
            status=statut,
        )
        Transaction.objects.filter(pk=transaction.pk).update(created_at=SOIR - il_y_a)
        return transaction

    def test_une_tentative_de_paiement_a_reprendre_garde_la_priorite(self):
        user = self.inscrit_qui_a_ouvert()
        self.tentative(user, StatutTransaction.FAILED, timedelta(days=1))

        self.assertIsNotNone(services.paiement_a_reprendre(user, SOIR))
        self.assertEqual(envoyer(SOIR), 0)

    def test_un_seul_message_dans_le_tour_de_l_ordonnanceur_celui_du_paiement(self):
        user = self.inscrit_qui_a_ouvert()
        self.tentative(user, StatutTransaction.FAILED, timedelta(days=1))

        resultat = passer_une_fois(SOIR)

        self.assertEqual(resultat["paiement"], 1)
        self.assertEqual(resultat["inscrit_sans_paiement"], 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Ton paiement n'a pas abouti")


class CursusViseTests(InscritSansPaiementTestCase):
    def setUp(self):
        super().setUp()
        self.autre = Cursus.objects.filter(country__actif=True).exclude(pk=self.cursus.pk).first()
        if self.autre is None:
            self.skipTest("Un seul cursus actif dans la base de test.")

    def test_l_examen_de_l_ecran_ouvert_passe_avant_l_examen_declare(self):
        user = self.inscrit()
        self.ouvre(user, timedelta(days=1), cursus_id=self.autre.pk)

        self.assertEqual(envoyer(SOIR), 1)

        self.assertIn(f"/abonnement?cursus={self.autre.pk}&profil=", mail.outbox[0].body)
        self.assertIn(f"({self.autre})", mail.outbox[0].body)

    def test_sans_cursus_dans_l_evenement_l_examen_declare(self):
        user = self.inscrit()
        self.ouvre(user, timedelta(days=1))

        self.assertEqual(envoyer(SOIR), 1)

        self.assertIn(f"/abonnement?cursus={self.cursus.pk}&profil=", mail.outbox[0].body)

    def test_un_cursus_inconnu_ou_mal_forme_retombe_sur_l_examen_declare(self):
        user = self.inscrit()
        for valeur in (99999999, str(self.autre.pk), True, None):
            self.assertEqual(inscrit_sans_paiement.cursus_vise(user, {"cursus_id": valeur}), self.cursus)

    def test_le_lien_designe_le_profil_qui_prepare_cet_examen(self):
        user = self.inscrit()
        enfant = user.profils.create(prenom="Guyguy", cursus_prepare=self.autre)

        _sujet, corps = inscrit_sans_paiement.composer_relance_inscrit(
            user, self.autre, TypeRelance.INSCRIT_SANS_PAIEMENT_1,
        )

        self.assertIn(f"/abonnement?cursus={self.autre.pk}&profil={enfant.pk}", corps)


class EnvoiTests(InscritSansPaiementTestCase):
    def test_un_envoi_en_echec_n_est_pas_marque_fait(self):
        user = self.inscrit_qui_a_ouvert()
        with mock.patch.object(inscrit_sans_paiement, "_envoyer_email", side_effect=RuntimeError("smtp")):
            self.assertEqual(envoyer(SOIR), 0)

        self.assertEqual(self.traces(user), [])
        self.assertEqual(envoyer(SOIR), 1)

    def test_dry_run_compte_sans_rien_envoyer(self):
        user = self.inscrit_qui_a_ouvert()

        self.assertEqual(envoyer(SOIR, dry_run=True), 1)

        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.traces(user), [])

    def test_la_commande_compte_sans_envoyer(self):
        user = self.inscrit()
        self.ouvre(user, timedelta(days=1), avant=timezone.now(), cursus_id=self.cursus.pk)
        sortie = StringIO()

        call_command("envoyer_relances", "--seulement", "inscrit_sans_paiement", "--dry-run", stdout=sortie)

        self.assertIn("[dry-run] 1 relance(s) d'inscrit sans paiement.", sortie.getvalue())
        # « --seulement » : aucune autre relance n'est comptée.
        self.assertEqual(sortie.getvalue().count("[dry-run]"), 1)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.traces(user), [])


class TexteTests(InscritSansPaiementTestCase):
    def composer(self, user, type_):
        return inscrit_sans_paiement.composer_relance_inscrit(user, self.cursus, type_)

    def test_le_premier_message_dit_ce_que_l_abonnement_ouvre(self):
        user = self.inscrit()

        sujet, corps = self.composer(user, TypeRelance.INSCRIT_SANS_PAIEMENT_1)

        self.assertEqual(sujet, "Ce qu'ouvre l'abonnement EduKora")
        for element in ("corrigés détaillés", "exercices d'application", "quiz", "épreuves inédites"):
            self.assertIn(element, corps)
        self.assertIn(f"({self.cursus})", corps)
        self.assertIn("Mobile Money", corps)
        self.assertIn(inscrit_sans_paiement.lien_arret(user), corps)

    def test_le_second_message_dit_que_c_est_le_dernier(self):
        user = self.inscrit()

        sujet, corps = self.composer(user, TypeRelance.INSCRIT_SANS_PAIEMENT_2)

        self.assertEqual(sujet, "Un dernier mot sur l'abonnement EduKora")
        self.assertIn("C'est notre dernier message à ce sujet.", corps)
        self.assertIn("Il coûte 2 000 FCFA par mois.", corps)
        self.assertIn("Aucun prélèvement automatique", corps)
        self.assertIn(f"/abonnement?cursus={self.cursus.pk}&profil={user.profils.first().pk}", corps)
        self.assertIn(inscrit_sans_paiement.lien_arret(user), corps)

    def test_en_anglais_pour_un_compte_en_anglais(self):
        user = self.inscrit()
        User.objects.filter(pk=user.pk).update(langue="en")
        user.refresh_from_db()

        sujet, corps = self.composer(user, TypeRelance.INSCRIT_SANS_PAIEMENT_1)
        dernier_sujet, dernier = self.composer(user, TypeRelance.INSCRIT_SANS_PAIEMENT_2)

        self.assertEqual(sujet, "What the EduKora subscription opens")
        self.assertEqual(dernier_sujet, "A last word about the EduKora subscription")
        self.assertIn("This is our last message about it.", dernier)
        self.assertNotIn("last message", corps)
        for texte in (corps, dernier):
            self.assertIn("Hello Awa,", texte)
            for element in ("detailed solutions", "practice exercises", "quizzes", "original mock papers"):
                self.assertIn(element, texte)
            self.assertIn("It costs 2 000 FCFA per month.", texte)
            self.assertIn("No automatic charge", texte)
            self.assertIn(f"/abonnement?cursus={self.cursus.pk}&profil={user.profils.first().pk}", texte)
            self.assertIn(inscrit_sans_paiement.lien_arret(user), texte)
            self.assertNotIn("Bonjour", texte)

    def test_rien_ne_presse_dans_aucun_des_quatre_textes(self):
        user = self.inscrit()
        for langue in ("fr", "en"):
            User.objects.filter(pk=user.pk).update(langue=langue)
            user.refresh_from_db()
            for type_ in inscrit_sans_paiement.TYPES:
                sujet, corps = self.composer(user, type_)
                # Les liens portent un jeton signé, au contenu arbitraire : le registre se juge sur le texte.
                lu = "\n".join(ligne for ligne in f"{sujet}\n{corps}".casefold().split("\n") if "http" not in ligne)
                for mot in PRESSION:
                    self.assertNotIn(mot, lu, f"« {mot} » dans le message {type_} en {langue}")
                self.assertNotRegex(lu, r"\d+ (jours?|days?)")

    def test_le_prix_cite_est_celui_du_plan_hors_campagne(self):
        user = self.inscrit()
        Plan.objects.filter(pk=self.plan_au_mois.pk).update(price=2500)
        Campagne.objects.create(
            nom="Offre fondateurs", pourcentage=20, debut=timezone.now() - timedelta(days=1),
            fin=timezone.now() + timedelta(days=10),
        )
        self.assertEqual(Plan.objects.get(pk=self.plan_au_mois.pk).tarif().prix, 2000)

        _sujet, corps = self.composer(user, TypeRelance.INSCRIT_SANS_PAIEMENT_1)

        self.assertIn("Il coûte 2 500 FCFA par mois.", corps)

    def test_sans_plan_au_mois_sans_ambiguite_aucun_prix_n_est_cite(self):
        user = self.inscrit()
        Plan.objects.create(name="Au mois bis", cursus=self.cursus, price=3000, duration_mode=DureeMode.MENSUEL)
        _sujet, deux_prix = self.composer(user, TypeRelance.INSCRIT_SANS_PAIEMENT_1)
        Plan.objects.filter(cursus=self.cursus, duration_mode=DureeMode.MENSUEL).update(is_active=False)
        _sujet, aucun_plan = self.composer(user, TypeRelance.INSCRIT_SANS_PAIEMENT_1)

        for corps in (deux_prix, aucun_plan):
            self.assertNotIn("FCFA", corps)
            self.assertIn("Aucun prélèvement automatique", corps)


class PlanificateurTests(InscritSansPaiementTestCase):
    def test_le_message_part_dans_la_fenetre_de_fin_d_apres_midi(self):
        self.inscrit_qui_a_ouvert(timedelta(days=1, hours=12))

        matin = SOIR.replace(hour=9)
        self.assertEqual(passer_une_fois(matin)["inscrit_sans_paiement"], 0)
        self.assertEqual(passer_une_fois(SOIR)["inscrit_sans_paiement"], 1)
        self.assertEqual(passer_une_fois(SOIR.replace(hour=18))["inscrit_sans_paiement"], 0)
        self.assertEqual(len(mail.outbox), 1)
