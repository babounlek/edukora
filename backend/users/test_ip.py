"""Adresse réelle du demandeur (voir users.ip) : derrière Cloudflare, c'est l'élève, pas le nœud du réseau."""

from django.test import RequestFactory, SimpleTestCase

from .ip import client_ip


class ClientIpTests(SimpleTestCase):
    def _requete(self, **meta):
        return RequestFactory().get("/", **meta)

    def test_l_en_tete_pose_par_caddy_prime(self):
        # X-Forwarded-For se termine par l'adresse de Cloudflare ; X-Client-IP porte celle de l'élève.
        requete = self._requete(
            HTTP_X_CLIENT_IP="41.202.5.5", HTTP_X_FORWARDED_FOR="41.202.5.5, 172.70.1.1", REMOTE_ADDR="172.18.0.3",
        )
        self.assertEqual(client_ip(requete), "41.202.5.5")

    def test_sans_cet_en_tete_la_derniere_entree_de_x_forwarded_for(self):
        requete = self._requete(HTTP_X_FORWARDED_FOR="1.2.3.4, 41.202.5.5", REMOTE_ADDR="172.18.0.3")
        self.assertEqual(client_ip(requete), "41.202.5.5")

    def test_un_en_tete_illisible_est_ignore(self):
        requete = self._requete(HTTP_X_CLIENT_IP="pas-une-ip", REMOTE_ADDR="41.202.6.6")
        self.assertEqual(client_ip(requete), "41.202.6.6")

    def test_ipv6(self):
        self.assertEqual(client_ip(self._requete(HTTP_X_CLIENT_IP="2001:db8::1")), "2001:db8::1")

    def test_rien_d_exploitable(self):
        self.assertIsNone(client_ip(self._requete(HTTP_X_FORWARDED_FOR="pas-une-ip")))
