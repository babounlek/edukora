"""
Comptes invités : essayer une inédite gratuite sans s'inscrire (voir users.invites et users.authentication).
"""
from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Country, StatutContenu, Tag
from inedit.models import TentativeInedite
from inedit.tests import _blueprint_payload, _make_published_epreuve
from inedit.ingestion import ingest_blueprint
from inedit.models import EpreuveInedite
from users import invites
from users.models import OTPCode, Profil, User


def _jeton(client):
    reponse = client.post("/auth/invite/")
    assert reponse.status_code == 201, reponse.data
    return reponse.data["access"]


class _Base(TestCase):
    def setUp(self):
        Tag.objects.create(name="Suites numériques")
        self.country = Country.objects.get(code="CM")
        self.offerte = _make_published_epreuve(self.country)
        self.offerte.est_gratuite = True
        self.offerte.save(update_fields=["est_gratuite"])
        blueprint, _ = ingest_blueprint(_blueprint_payload(external_id="bp-payante"), self.country)
        blueprint.statut = StatutContenu.VALIDE
        blueprint.save(update_fields=["statut"])
        self.payante = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=blueprint.subject, titre="Réservée", statut=StatutContenu.VALIDE,
        )
        self.payante.cursus.set(blueprint.cursus.all())
        self.client = APIClient()

    def auth(self, jeton):
        return {"HTTP_AUTHORIZATION": f"Bearer {jeton}"}


class CreationInviteTests(_Base):
    def test_cree_un_compte_sans_identite_et_un_jeton_sans_cookie(self):
        reponse = self.client.post("/auth/invite/")
        self.assertEqual(reponse.status_code, 201)
        self.assertIn("access", reponse.data)
        self.assertEqual(len(reponse.cookies), 0)  # aucune session : pas de refresh
        invite = User.objects.get(est_invite=True)
        self.assertIsNone(invite.phone_number)
        self.assertIsNone(invite.email)
        self.assertFalse(invite.has_usable_password())
        self.assertEqual(invite.profils.count(), 1)

    def test_le_plafond_par_ip_arrete_les_creations(self):
        with patch.object(invites, "MAX_PAR_IP_PAR_HEURE", 2):
            for _ in range(2):
                self.assertEqual(self.client.post("/auth/invite/", HTTP_X_FORWARDED_FOR="203.0.113.9").status_code, 201)
            self.assertEqual(self.client.post("/auth/invite/", HTTP_X_FORWARDED_FOR="203.0.113.9").status_code, 429)
            # Une autre IP n'est pas touchée.
            self.assertEqual(self.client.post("/auth/invite/", HTTP_X_FORWARDED_FOR="203.0.113.10").status_code, 201)

    def test_le_plafond_global_arrete_les_creations(self):
        with patch.object(invites, "MAX_GLOBAL_PAR_JOUR", 1):
            self.assertEqual(self.client.post("/auth/invite/").status_code, 201)
            self.assertEqual(self.client.post("/auth/invite/").status_code, 429)


class DroitsInviteTests(_Base):
    def test_joue_une_inedite_gratuite_du_debut_a_la_fin(self):
        jeton = _jeton(self.client)
        fiche = self.client.get(f"/inedit/epreuves/{self.offerte.slug}/", **self.auth(jeton))
        self.assertTrue(fiche.data["has_access"])

        creation = self.client.post("/inedit/tentatives/", {"epreuve": self.offerte.id}, **self.auth(jeton))
        self.assertEqual(creation.status_code, 201)
        # La même copie est reprise, jamais une seconde.
        self.assertEqual(
            self.client.post("/inedit/tentatives/", {"epreuve": self.offerte.id}, **self.auth(jeton)).data["id"],
            creation.data["id"],
        )
        fin = self.client.post(f"/inedit/tentatives/{creation.data['id']}/completer/", **self.auth(jeton))
        self.assertEqual(fin.status_code, 200)

    def test_une_inedite_payante_reste_fermee(self):
        jeton = _jeton(self.client)
        reponse = self.client.post("/inedit/tentatives/", {"epreuve": self.payante.id}, **self.auth(jeton))
        self.assertEqual(reponse.status_code, 403)

    def test_le_jeton_n_ouvre_rien_hors_inedit(self):
        jeton = _jeton(self.client)
        self.assertEqual(self.client.get("/auth/me/", **self.auth(jeton)).status_code, 403)
        # Du quiz, seules les routes d'une séance sont ouvertes (voir test_invites_quiz) : pas le parcours.
        self.assertEqual(self.client.get("/quiz/parcours/", **self.auth(jeton)).status_code, 403)

    def test_un_jeton_falsifie_ou_d_un_compte_reel_n_est_pas_un_invite(self):
        self.assertIsNone(invites.invite_du_jeton("n-importe-quoi"))
        reel = User.objects.create_user(phone_number="677900001", password="x")
        from rest_framework_simplejwt.tokens import AccessToken

        self.assertIsNone(invites.invite_du_jeton(str(AccessToken.for_user(reel))))

    def test_compte_comme_un_visiteur_pour_les_quotas_de_pdf(self):
        from access import quota

        jeton = _jeton(self.client)
        request = APIClient().get("/inedit/mes-tentatives/", **self.auth(jeton)).wsgi_request
        self.assertEqual(quota.contexte(request).profil_type, quota.VISITEUR)


class RattachementTests(_Base):
    def _copie_d_invite(self):
        jeton = _jeton(self.client)
        creation = self.client.post("/inedit/tentatives/", {"epreuve": self.offerte.id}, **self.auth(jeton))
        invite = User.objects.get(est_invite=True)
        return jeton, creation.data["id"], invite

    def _inscrire(self, numero, jeton=None):
        with patch("users.otp_service.get_sms_backend"):
            self.client.post("/auth/otp/request/", {"phone_number": numero})
        code = OTPCode.objects.get(destination=f"+237{numero}").code
        extra = {"HTTP_X_INVITE_TOKEN": jeton} if jeton else {}
        return self.client.post("/auth/otp/verify/", {"phone_number": numero, "code": code}, **extra)

    def test_un_compte_neuf_herite_de_la_copie(self):
        jeton, tentative_id, invite = self._copie_d_invite()
        profil_invite = invite.profils.get()

        reponse = self._inscrire("677900010", jeton)
        self.assertEqual(reponse.status_code, 200)

        user = User.objects.get(phone_number="+237677900010")
        self.assertFalse(User.objects.filter(pk=invite.pk).exists())  # l'invité a disparu
        self.assertEqual(user.profils.count(), 1)
        self.assertEqual(user.profils.get().pk, profil_invite.pk)  # son profil est celui de l'invité
        self.assertTrue(TentativeInedite.objects.filter(pk=tentative_id, profil__compte=user).exists())
        # Et le vrai jeton ouvre la copie.
        lue = self.client.get(
            f"/inedit/tentatives/{tentative_id}/", HTTP_AUTHORIZATION=f"Bearer {reponse.data['access']}",
        )
        self.assertEqual(lue.status_code, 200)
        # Le jeton d'invité ne désigne plus personne.
        self.assertIsNone(invites.invite_du_jeton(jeton))

    def test_un_compte_deja_utilise_recoit_les_copies_sur_son_profil(self):
        existant = User.objects.create_user(phone_number="677900020", password="x")
        profil = existant.profils.get()
        # Une activité d'élève : ce profil n'est plus « vierge ».
        TentativeInedite.objects.create(profil=profil, epreuve=self.offerte)
        jeton, tentative_id, invite = self._copie_d_invite()

        reponse = self._inscrire("677900020", jeton)
        self.assertEqual(reponse.status_code, 200)

        self.assertFalse(User.objects.filter(pk=invite.pk).exists())
        self.assertEqual(existant.profils.count(), 1)
        self.assertEqual(TentativeInedite.objects.get(pk=tentative_id).profil_id, profil.pk)

    def test_sans_jeton_d_invite_rien_ne_change(self):
        _, _, invite = self._copie_d_invite()
        self._inscrire("677900030")
        self.assertTrue(User.objects.filter(pk=invite.pk).exists())

    def test_un_jeton_invalide_ne_bloque_pas_la_connexion(self):
        reponse = self._inscrire("677900040", "jeton-invalide")
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("access", reponse.data)

    def test_une_erreur_de_rattachement_ne_bloque_pas_la_connexion(self):
        jeton, _, invite = self._copie_d_invite()
        with patch.object(invites, "rattacher", side_effect=RuntimeError("boum")):
            reponse = self._inscrire("677900050", jeton)
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(User.objects.filter(pk=invite.pk).exists())

    def test_un_invite_ne_se_rattache_pas_a_un_autre_invite(self):
        _, _, invite = self._copie_d_invite()
        autre = invites.creer_invite()
        invites.rattacher(invite, autre)
        self.assertTrue(User.objects.filter(pk=invite.pk).exists())

    def test_le_profil_d_un_compte_avec_activite_n_est_pas_vierge(self):
        user = User.objects.create_user(phone_number="677900060", password="x")
        profil = user.profils.get()
        self.assertTrue(invites._profil_vierge(profil))
        TentativeInedite.objects.create(profil=profil, epreuve=self.offerte)
        self.assertFalse(invites._profil_vierge(profil))


class PurgeInvitesTests(TestCase):
    def test_supprime_les_invites_abandonnes_seulement(self):
        vieux = invites.creer_invite()
        User.objects.filter(pk=vieux.pk).update(date_joined=timezone.now() - timedelta(days=61))
        recent = invites.creer_invite()
        reel = User.objects.create_user(phone_number="677900070", password="x")
        User.objects.filter(pk=reel.pk).update(date_joined=timezone.now() - timedelta(days=400))

        call_command("purger_invites")

        self.assertFalse(User.objects.filter(pk=vieux.pk).exists())
        self.assertTrue(User.objects.filter(pk=recent.pk).exists())
        self.assertTrue(User.objects.filter(pk=reel.pk).exists())
        self.assertEqual(Profil.objects.filter(compte=vieux.pk).count(), 0)
