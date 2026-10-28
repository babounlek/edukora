"""Purge des comptes de test : users.purge_test et la commande purger_donnees_test (deploy/SPEC-PURGE-DONNEES-TEST.md)."""
import json
import os
import tempfile
from datetime import date, timedelta
from io import StringIO
from unittest import mock

from django.apps import apps
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone

from access.models import CompteurQuota, TelechargementPdf
from analytics.models import AnalyticsEvent, EventName
from catalog.models import Cursus, Examen, Tag
from payments.models import ManualPayment, ManualPaymentStatus, MobileMoneyOperator, _activer_acces
from quiz.models import JourXP
from revendeurs.models import Revendeur, TypeRevendeur
from subscriptions.models import DureeMode, Plan, ProductType, Subscription
from subscriptions.models import ParrainageRecompense
from users import purge_test
from users.models import Profil, User


def compte(email, nom="", staff=False, superuser=False):
    return User.objects.create_user(
        phone_number=None, email=email, full_name=nom, is_staff=staff, is_superuser=superuser,
        rappels_actifs=False,
    )


def perimetre_pour(*users, **options):
    return purge_test.charger_perimetre({
        "version": 1,
        "comptes": [{"user_id": u.pk, "identifiant_sha256": purge_test.empreinte_identifiant(u)} for u in users],
        "options": options,
    })


def empreinte_tables():
    """Nombre de lignes de TOUS les modèles + identifiants des tables d'usage, pour prouver une absence d'écriture."""
    releve = {m._meta.label: m.objects.count() for m in apps.get_models()}
    for m in (User, ManualPayment, Subscription, AnalyticsEvent, Session, CompteurQuota, TelechargementPdf, Profil):
        releve[f"ids:{m._meta.label}"] = sorted(m.objects.values_list("pk", flat=True))
    return releve


class PurgeTestBase(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.plan = Plan.objects.create(
            name="Jusqu'à l'examen", cursus=self.cursus, price=15000, duration_days=30,
            duration_mode=DureeMode.JUSQUA_EXAMEN, product_type=ProductType.ABONNEMENT, inclut_inedit=True,
        )
        self.admin = compte("admin@exemple.test", "Admin réel", staff=True, superuser=True)
        self.reel = compte("vrai@exemple.test", "Vraie personne")
        self.cible = compte("cible@exemple.test", "Compte de recette")
        self.cible2 = compte("cible2@exemple.test", "Autre compte de recette")
        # Un compte au marqueur strict mais HORS périmètre : ne doit jamais être touché.
        self.marque = compte("moi+edukora-test-eleve-abonne@exemple.local", "[TEST] Élève abonné")
        for u in (self.reel, self.cible, self.cible2, self.marque):
            self.donnees_usage(u)
        # Contenu pédagogique témoin.
        self.tag = Tag.objects.create(name="tag-temoin-purge")
        self.tag_id = self.tag.pk  # delete() remet pk à None sur l'instance

    def donnees_usage(self, user, statut=ManualPaymentStatus.APPROVED):
        profil = user.profils.first()
        _activer_acces(self.plan, user, profil=profil)
        paiement = ManualPayment.objects.create(
            user=user, profil=profil, plan=self.plan, operator=MobileMoneyOperator.MTN,
            amount_expected=15000, amount_declared=15000, payer_phone_number="600000000",
            transaction_reference=f"TEST-{user.pk:06d}", status=statut,
        )
        AnalyticsEvent.objects.create(name=EventName.QUIZ_STARTED, user=user)
        JourXP.objects.create(profil=profil, jour=date.today(), xp=10, objectif=20)
        CompteurQuota.objects.create(jour=date.today(), portee="demandeur", cle=f"p:{profil.pk}", nombre=1)
        TelechargementPdf.objects.create(jour=date.today(), demandeur=f"p:{profil.pk}", type_demandeur="profil", document="x")
        session = SessionStore()
        session["_auth_user_id"] = str(user.pk)
        session.create()
        return paiement

    def tout(self, *users):
        return perimetre_pour(*users, paiements=True, paiements_approuves=True, quotas=True, analytics=True)


class PerimetreTests(PurgeTestBase):
    def test_champ_inconnu_ou_option_inconnue_refuse(self):
        with self.assertRaises(purge_test.Refus):
            purge_test.charger_perimetre({"version": 1, "comptes": [], "intrus": 1})
        with self.assertRaises(purge_test.Refus):
            purge_test.charger_perimetre({"version": 1, "comptes": [], "options": {"tout": True}})
        with self.assertRaises(purge_test.Refus):
            purge_test.charger_perimetre({"version": 1, "comptes": [], "options": {"paiements_approuves": True}})

    def test_periemetre_vide_ne_fait_rien(self):
        avant = empreinte_tables()
        rapport = purge_test.simuler(purge_test.charger_perimetre({"version": 1, "comptes": []}))
        self.assertEqual(rapport["statut"], "ok")
        self.assertEqual(rapport["lignes_par_modele"], {})
        self.assertEqual(avant, empreinte_tables())


class SimulationTests(PurgeTestBase):
    def test_simulation_ne_modifie_aucune_donnee(self):
        avant = empreinte_tables()
        rapport = purge_test.simuler(self.tout(self.cible, self.cible2))
        self.assertEqual(rapport["statut"], "ok")
        self.assertEqual(rapport["lignes_par_modele"]["users.User"], 2)
        self.assertEqual(rapport["comptes"]["supprimes"], 0)  # c'est une simulation
        self.assertTrue(rapport["jeton"])
        self.assertEqual(avant, empreinte_tables())

    def test_le_jeton_est_stable_tant_que_rien_ne_change(self):
        p = self.tout(self.cible)
        self.assertEqual(purge_test.simuler(p)["jeton"], purge_test.simuler(p)["jeton"])


class ExecutionTests(PurgeTestBase):
    def executer(self, perimetre):
        jeton = purge_test.simuler(perimetre)["jeton"]
        return purge_test.executer(perimetre, jeton)

    def test_supprime_les_comptes_cibles_et_leurs_donnees(self):
        profil_cible = self.cible.profils.first()
        rapport = self.executer(self.tout(self.cible))
        self.assertEqual(rapport["comptes"]["supprimes"], 1)
        self.assertFalse(User.objects.filter(pk=self.cible.pk).exists())
        self.assertFalse(ManualPayment.objects.filter(user_id=self.cible.pk).exists())
        self.assertFalse(Subscription.objects.filter(user_id=self.cible.pk).exists())
        self.assertFalse(AnalyticsEvent.objects.filter(user_id=self.cible.pk).exists())  # option analytics
        self.assertFalse(JourXP.objects.filter(profil_id=profil_cible.pk).exists())
        self.assertFalse(CompteurQuota.objects.filter(cle=f"p:{profil_cible.pk}").exists())
        self.assertFalse(TelechargementPdf.objects.filter(demandeur=f"p:{profil_cible.pk}").exists())
        self.assertFalse(any(s.get_decoded().get("_auth_user_id") == str(self.cible.pk) for s in Session.objects.all()))

    def test_les_autres_comptes_sont_intacts(self):
        autres = (self.admin, self.reel, self.cible2, self.marque)
        avant = {u.pk: (ManualPayment.objects.filter(user=u).count(), Subscription.objects.filter(user=u).count(),
                        AnalyticsEvent.objects.filter(user=u).count()) for u in autres}
        sessions_avant = Session.objects.count()
        self.executer(self.tout(self.cible))
        for u in autres:
            self.assertTrue(User.objects.filter(pk=u.pk).exists())
            self.assertEqual(avant[u.pk], (ManualPayment.objects.filter(user=u).count(),
                                           Subscription.objects.filter(user=u).count(),
                                           AnalyticsEvent.objects.filter(user=u).count()))
        self.assertEqual(Session.objects.count(), sessions_avant - 1)  # seule la session du compte ciblé

    def test_un_compte_au_marqueur_strict_hors_perimetre_n_est_pas_touche(self):
        self.executer(self.tout(self.cible))
        self.assertTrue(User.objects.filter(pk=self.marque.pk).exists())

    def test_le_contenu_pedagogique_et_les_reglages_sont_conserves(self):
        avant = purge_test.empreinte_protegee()
        self.executer(self.tout(self.cible, self.cible2))
        self.assertEqual(avant, purge_test.empreinte_protegee())
        self.assertTrue(Tag.objects.filter(pk=self.tag_id).exists())
        self.assertTrue(Plan.objects.filter(pk=self.plan.pk).exists())

    def test_un_changement_du_contenu_pendant_la_purge_annule_tout(self):
        vrai_appliquer = purge_test._appliquer

        def appliquer_et_toucher_au_contenu(users, perimetre):
            comptes = vrai_appliquer(users, perimetre)
            self.tag.delete()
            return comptes

        p = self.tout(self.cible)
        jeton = purge_test.simuler(p)["jeton"]
        with mock.patch.object(purge_test, "_appliquer", appliquer_et_toucher_au_contenu):
            with self.assertRaises(purge_test.Echec):
                purge_test.executer(p, jeton)
        self.assertTrue(User.objects.filter(pk=self.cible.pk).exists())
        self.assertTrue(Tag.objects.filter(pk=self.tag_id).exists())

    def test_une_erreur_au_milieu_ne_laisse_aucune_purge_partielle(self):
        p = self.tout(self.cible)
        jeton = purge_test.simuler(p)["jeton"]
        avant = empreinte_tables()
        with mock.patch.object(purge_test, "_sessions_des_comptes", side_effect=RuntimeError("panne")):
            with self.assertRaises(RuntimeError):
                purge_test.executer(p, jeton)  # paiements et événements déjà supprimés dans la transaction
        self.assertEqual(avant, empreinte_tables())

    def test_une_seconde_execution_ne_supprime_rien_de_plus(self):
        p = self.tout(self.cible)
        self.executer(p)
        apres_la_premiere = empreinte_tables()
        rapport = self.executer(p)  # le compte n'existe plus : ignoré, pas une erreur
        self.assertEqual(rapport["comptes"]["ignores_absents"], [self.cible.pk])
        self.assertEqual(rapport["comptes"]["supprimes"], 0)
        self.assertEqual(rapport["lignes_par_modele"], {})
        self.assertEqual(apres_la_premiere, empreinte_tables())

    def test_jeton_perime_si_les_donnees_changent_apres_la_simulation(self):
        p = self.tout(self.cible)
        jeton = purge_test.simuler(p)["jeton"]
        JourXP.objects.create(profil=self.cible.profils.first(), jour=date.today() - timedelta(days=1), xp=5, objectif=20)
        with self.assertRaises(purge_test.Refus):
            purge_test.executer(p, jeton)
        self.assertTrue(User.objects.filter(pk=self.cible.pk).exists())

    def test_un_mauvais_jeton_est_refuse(self):
        with self.assertRaises(purge_test.Refus):
            purge_test.executer(self.tout(self.cible), "0" * 20)
        self.assertTrue(User.objects.filter(pk=self.cible.pk).exists())

    def test_les_fichiers_d_usage_sont_listes_jamais_supprimes(self):
        ManualPayment.objects.filter(user=self.cible).update(proof="preuves/cible.png")
        p = self.tout(self.cible)
        with mock.patch("django.core.files.storage.Storage.delete") as suppression:
            rapport = self.executer(p)
        self.assertIn("payments.ManualPayment.proof: preuves/cible.png", rapport["fichiers_d_usage_listes_non_supprimes"])
        suppression.assert_not_called()


class GardesTests(PurgeTestBase):
    def refus(self, perimetre):
        rapport = purge_test.simuler(perimetre)
        self.assertEqual(rapport["statut"], "refuse")
        self.assertEqual(rapport["lignes_par_modele"], {})
        return rapport["refus"]

    def test_un_administrateur_n_est_jamais_supprimable(self):
        self.assertTrue(any("administrateur" in r for r in self.refus(perimetre_pour(self.admin))))
        with self.assertRaises(purge_test.Refus):
            purge_test.executer(perimetre_pour(self.admin), "x")
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_un_administrateur_dans_une_liste_mixte_bloque_toute_la_purge(self):
        avant = empreinte_tables()
        self.refus(self.tout(self.cible, self.admin))
        self.assertEqual(avant, empreinte_tables())

    def test_identifiant_different_refuse(self):
        p = self.tout(self.cible)
        p["comptes"][0]["identifiant_sha256"] = "0" * 64
        self.assertTrue(any("ne correspond pas" in r for r in self.refus(p)))

    def test_paiements_presents_sans_l_option_refuse(self):
        self.assertTrue(any("option « paiements »" in r for r in self.refus(perimetre_pour(self.cible))))

    def test_paiement_valide_sans_confirmation_explicite_refuse(self):
        r = self.refus(perimetre_pour(self.cible, paiements=True))
        self.assertTrue(any("paiements_approuves" in x for x in r))

    def test_un_compte_sans_paiement_se_purge_sans_option(self):
        neuf = compte("neuf@exemple.test")
        rapport = purge_test.executer(perimetre_pour(neuf), purge_test.simuler(perimetre_pour(neuf))["jeton"])
        self.assertEqual(rapport["comptes"]["supprimes"], 1)

    def test_filleul_cible_d_un_vrai_parrain_refuse_et_le_credit_survit(self):
        credit = ParrainageRecompense.objects.create(
            parrain=self.reel, filleul=self.cible, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
            manual_payment=ManualPayment.objects.get(user=self.cible),
        )
        self.assertTrue(any("parrainage" in r for r in self.refus(self.tout(self.cible))))
        self.assertTrue(ParrainageRecompense.objects.filter(pk=credit.pk).exists())

    def test_parrainage_entre_deux_comptes_cibles_est_accepte(self):
        ParrainageRecompense.objects.create(
            parrain=self.cible2, filleul=self.cible, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
            manual_payment=ManualPayment.objects.get(user=self.cible),
        )
        p = self.tout(self.cible, self.cible2)
        self.assertEqual(purge_test.simuler(p)["statut"], "ok")

    def test_un_revendeur_n_est_pas_supprime_par_la_purge(self):
        Revendeur.objects.create(user=self.cible, type=TypeRevendeur.COMMERCIAL, nom_affiche="R", code="RTEST001")
        self.assertTrue(any("revendeur" in r.lower() for r in self.refus(self.tout(self.cible))))

    def test_paiement_d_un_compte_hors_perimetre_sur_un_profil_cible_refuse(self):
        profil = self.cible.profils.first()
        ManualPayment.objects.filter(user=self.cible).update(user=self.reel, profil=profil)
        self.assertTrue(any("hors périmètre" in r for r in self.refus(self.tout(self.cible))))

    def test_un_modele_absent_de_cette_version_est_ignore_et_signale(self):
        vrai = purge_test.modele

        def sans_revendeurs(label):
            return None if label.startswith("revendeurs.") else vrai(label)

        with mock.patch.object(purge_test, "modele", sans_revendeurs):
            rapport = purge_test.simuler(self.tout(self.cible))
        self.assertEqual(rapport["statut"], "ok")
        self.assertTrue(any("revendeurs.Revendeur absent" in a for a in rapport["avertissements"]))

    def test_verifier_apres_purge(self):
        p = self.tout(self.cible)
        self.assertEqual(purge_test.verifier(p)["statut"], "echec")
        purge_test.executer(p, purge_test.simuler(p)["jeton"])
        self.assertEqual(purge_test.verifier(p)["statut"], "ok")


class CommandeTests(PurgeTestBase):
    def ecrire_perimetre(self, perimetre):
        fichier = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump({"version": 1, "comptes": perimetre["comptes"], "options": perimetre["options"]}, fichier)
        fichier.close()
        self.addCleanup(os.unlink, fichier.name)
        return fichier.name

    def lancer(self, *args):
        sortie = StringIO()
        call_command("purger_donnees_test", *args, stdout=sortie)
        return sortie.getvalue()

    def jeton(self, chemin):
        return json.loads(self.lancer("simuler", "--perimetre", chemin, "--json"))["jeton"]

    @override_settings(DEBUG=True)
    def test_perimetre_marque_exclut_les_administrateurs_et_ne_supprime_rien(self):
        self.admin.email = "admin+edukora-test-x@exemple.local"
        self.admin.full_name = "[TEST] Admin"
        self.admin.save()
        avant = empreinte_tables()
        proposition = json.loads(self.lancer("perimetre", "--marque"))
        ids = [c["user_id"] for c in proposition["comptes"]]
        self.assertEqual(ids, [self.marque.pk])
        self.assertEqual(avant, empreinte_tables())

    @override_settings(DEBUG=False)
    def test_hors_debug_sans_garde_la_commande_refuse_avec_le_code_2(self):
        chemin = self.ecrire_perimetre(self.tout(self.cible))
        jeton = self.jeton(chemin)
        for env, options in [
            ({}, ["--confirme-production", "--sauvegarde", "avant-1.dump"]),  # ALLOW_TEST_DATA absent
            ({"ALLOW_TEST_DATA": "1"}, ["--sauvegarde", "avant-1.dump"]),  # pas de --confirme-production
            ({"ALLOW_TEST_DATA": "1"}, ["--confirme-production"]),  # pas de sauvegarde
            ({"ALLOW_TEST_DATA": "1"}, ["--confirme-production", "--sauvegarde", "avant-1.dump"]),  # non vérifiée
            ({"ALLOW_TEST_DATA": "1", "PURGE_SAUVEGARDE_VERIFIEE": "autre.dump"},
             ["--confirme-production", "--sauvegarde", "avant-1.dump"]),
        ]:
            with mock.patch.dict(os.environ, env, clear=False):
                os.environ.pop("PURGE_SAUVEGARDE_VERIFIEE", None) if "PURGE_SAUVEGARDE_VERIFIEE" not in env else None
                if "ALLOW_TEST_DATA" not in env:
                    os.environ.pop("ALLOW_TEST_DATA", None)
                with self.assertRaises(CommandError) as ctx:
                    self.lancer("executer", "--perimetre", chemin, "--jeton", jeton, *options)
                self.assertEqual(ctx.exception.returncode, 2)
        self.assertTrue(User.objects.filter(pk=self.cible.pk).exists())

    @override_settings(DEBUG=False)
    def test_hors_debug_avec_toutes_les_gardes_la_purge_s_execute(self):
        chemin = self.ecrire_perimetre(self.tout(self.cible))
        jeton = self.jeton(chemin)
        env = {"ALLOW_TEST_DATA": "1", "PURGE_SAUVEGARDE_VERIFIEE": "avant-20261101-100000-0123abcd.dump"}
        with mock.patch.dict(os.environ, env):
            sortie = self.lancer("executer", "--perimetre", chemin, "--jeton", jeton, "--confirme-production",
                                 "--sauvegarde", "avant-20261101-100000-0123abcd.dump", "--json")
        self.assertEqual(json.loads(sortie)["comptes"]["supprimes"], 1)
        self.assertFalse(User.objects.filter(pk=self.cible.pk).exists())
        self.assertIn("ok", self.lancer("verifier", "--perimetre", chemin, "--json"))

    @override_settings(DEBUG=True)
    def test_une_simulation_refusee_sort_avec_le_code_2(self):
        chemin = self.ecrire_perimetre(perimetre_pour(self.admin))
        with self.assertRaises(CommandError) as ctx:
            self.lancer("simuler", "--perimetre", chemin)
        self.assertEqual(ctx.exception.returncode, 2)

    @override_settings(DEBUG=True)
    def test_fichier_de_perimetre_illisible_sort_avec_le_code_2(self):
        with self.assertRaises(CommandError) as ctx:
            self.lancer("simuler", "--perimetre", "/inexistant/perimetre.json")
        self.assertEqual(ctx.exception.returncode, 2)


class VerrouTests(TestCase):
    def test_un_verrou_deja_pris_refuse_la_purge_sans_rien_ecrire(self):
        """SQLite (tests) n'a pas de verrou consultatif : on simule la réponse de PostgreSQL."""
        faux = mock.MagicMock()
        faux.vendor = "postgresql"
        faux.cursor.return_value.__enter__.return_value.fetchone.return_value = (False,)
        with mock.patch.object(purge_test, "connection", faux):
            with self.assertRaises(purge_test.VerrouPris):
                purge_test.simuler(purge_test.charger_perimetre({"version": 1, "comptes": []}))
