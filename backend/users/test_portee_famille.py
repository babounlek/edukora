"""
Portée « famille » des listes d'accès (abonnements, inédites, répétiteur) - voir users.parent.portee_famille.

Un enfant qui ouvre « Mes accès » ne doit pas lire les abonnements et les jours restants de ses frères quand le
parent a défini un code parent. Sans code parent, rien ne change (le code est facultatif).
"""

from datetime import timedelta

from django.utils import timezone

from catalog.models import Cursus, Examen
from subscriptions.models import DureeMode, InscriptionInedite, InscriptionRepetiteur, Subscription

from . import pin as pin_module
from .parent import creer_jeton
from .test_pin import FamilleTestCase, _client_pour

URLS = ("/subscriptions/mine/", "/inedit/mes-inscriptions/", "/fiches/mes-inscriptions/")


def _profils_de(reponse):
    donnees = reponse.data["results"] if isinstance(reponse.data, dict) and "results" in reponse.data else reponse.data
    return {ligne["profil"]["id"] if isinstance(ligne.get("profil"), dict) else ligne.get("profil") for ligne in donnees}


class PorteeFamilleTests(FamilleTestCase):
    def setUp(self):
        super().setUp()
        cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        fin = timezone.now() + timedelta(days=60)
        for profil in (self.aine, self.cadet):
            Subscription.objects.create(
                user=self.parent, profil=profil, cursus=cursus, expires_at=fin, duration_mode=DureeMode.JUSQUA_EXAMEN,
            )
            InscriptionInedite.objects.create(user=self.parent, profil=profil, cursus=cursus, expires_at=fin)
            InscriptionRepetiteur.objects.create(user=self.parent, profil=profil, cursus=cursus, expires_at=fin)
        self.client_cadet = _client_pour(self.parent, self.cadet)

    def definir_code_parent(self):
        pin_module.definir(self.parent, pin_module.PARENT, "4321")

    def entete_parent(self):
        return {"HTTP_X_PARENT_TOKEN": creer_jeton(self.parent)}

    def test_sans_code_parent_tout_reste_ouvert(self):
        for url in URLS:
            reponse = self.client_cadet.get(url)
            self.assertEqual(reponse.status_code, 200, url)
            self.assertEqual(_profils_de(reponse), {self.aine.id, self.cadet.id}, url)

    def test_avec_code_parent_un_enfant_ne_voit_que_son_profil(self):
        self.definir_code_parent()
        for url in URLS:
            reponse = self.client_cadet.get(url)
            self.assertEqual(reponse.status_code, 200, url)
            self.assertEqual(_profils_de(reponse), {self.cadet.id}, url)

    def test_en_mode_parent_toute_la_famille_reste_visible_sans_parametre(self):
        self.definir_code_parent()
        for url in URLS:
            reponse = self.client_cadet.get(url, **self.entete_parent())
            self.assertEqual(_profils_de(reponse), {self.aine.id, self.cadet.id}, url)

    def test_tous_demande_le_code_parent(self):
        self.definir_code_parent()
        for url in URLS:
            reponse = self.client_cadet.get(url, {"tous": "1"})
            self.assertEqual(reponse.status_code, 403, url)
            self.assertEqual(reponse.data["code"], "parent_requis", url)

    def test_tous_avec_le_jeton_parent_donne_toute_la_famille(self):
        self.definir_code_parent()
        for url in URLS:
            reponse = self.client_cadet.get(url, {"tous": "1"}, **self.entete_parent())
            self.assertEqual(reponse.status_code, 200, url)
            self.assertEqual(_profils_de(reponse), {self.aine.id, self.cadet.id}, url)

    def test_tous_sans_code_parent_reste_ouvert(self):
        for url in URLS:
            reponse = self.client_cadet.get(url, {"tous": "1"})
            self.assertEqual(reponse.status_code, 200, url)
            self.assertEqual(_profils_de(reponse), {self.aine.id, self.cadet.id}, url)

    def test_une_session_enfant_restreinte_ne_voit_jamais_les_autres(self):
        client = _client_pour(self.parent, self.cadet, restreint=True)
        for url in URLS:
            reponse = client.get(url, **self.entete_parent())
            self.assertEqual(_profils_de(reponse), {self.cadet.id}, url)
            interdit = client.get(url, {"tous": "1"}, **self.entete_parent())
            self.assertEqual(interdit.status_code, 403, url)
            self.assertEqual(interdit.data["code"], "session_restreinte", url)
