"""
Quotas quotidiens de téléchargement des PDF (voir access.quota).

Les tests tournent sur SQLite en mémoire (voir settings : le rôle Postgres n'a pas CREATE DATABASE) : la concurrence
n'y est vérifiée que dans la mesure où SQLite sérialise les écritures. Le verrouillage réel (UPDATE conditionnel
atomique) est vérifié à part sur PostgreSQL, voir le compte rendu.
"""
import tempfile
import threading
from datetime import datetime, timedelta, timezone as fuseau_utc
from pathlib import Path
from unittest import mock

from django.core import signing
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.test import RequestFactory, TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.cours_pdf import COMPLET, LIBRE
from catalog import cours_pdf
from catalog.models import Cours, Lesson, LessonType, StatutContenu
from subscriptions.models import Subscription
from users.models import User

from . import quota
from .models import CompteurQuota, ReglagesTelechargement, TelechargementPdf
from .test_cours_libres import SECTIONS, _Base
from .test_cours_pdf import _stockages


class _QuotaBase(_Base):
    """Un cours avec PDF déjà en cache (libre et complet), stockage dans un dossier temporaire."""

    NB_COURS = 6

    def setUp(self):
        super().setUp()
        cache.clear()
        self.dossier = tempfile.TemporaryDirectory()
        self.addCleanup(self.dossier.cleanup)
        surcharge = override_settings(STORAGES=_stockages(self.dossier.name))
        surcharge.enable()
        self.addCleanup(surcharge.disable)
        self.tous_les_cours = [self.cours] + [self._nouveau_cours(i) for i in range(1, self.NB_COURS)]
        for cours in self.tous_les_cours:
            for variante in (LIBRE, COMPLET):
                cours_pdf.stockage().save(cours_pdf.nom_fichier(cours, variante), ContentFile(f"PDF-{variante}".encode()))

    def _nouveau_cours(self, i):
        cours = Cours.objects.create(
            titre=f"Cours quota {i}", subject=self.subject, statut=StatutContenu.VALIDE, sections_raw=SECTIONS,
            external_id=f"cours-quota-{i}",
        )
        cours.compile_from_sections()
        cours.cursus.add(self.cursus_c)
        return cours

    def _pdf(self, cours, client=None, **extra):
        return (client or self.client).get(f"/access/cours/pdf/{cours.slug}/", **extra)

    def _statut(self, client=None, **extra):
        return (client or self.client).get("/access/telechargements/quota/", **extra)

    def _telecharger_tout(self, client, nombre=None):
        """Télécharge les cours un par un ; renvoie les codes HTTP."""
        return [self._pdf(c, client).status_code for c in self.tous_les_cours[:nombre]]


class ReglagesEtJourTests(TestCase):
    def test_valeurs_initiales(self):
        reglages = ReglagesTelechargement.charger()

        self.assertEqual(reglages.quota_visiteur, 3)
        self.assertEqual(reglages.quota_abonne, 12)
        self.assertEqual(reglages.fuseau, "Africa/Douala")

    def test_la_journee_change_a_minuit_heure_de_douala(self):
        reglages = ReglagesTelechargement.charger()

        avant, fin = quota.jour_et_reinitialisation(reglages, datetime(2026, 10, 24, 22, 59, tzinfo=fuseau_utc.utc))
        apres, _ = quota.jour_et_reinitialisation(reglages, datetime(2026, 10, 24, 23, 0, tzinfo=fuseau_utc.utc))

        self.assertEqual(str(avant), "2026-10-24")
        self.assertEqual(str(apres), "2026-10-25")
        self.assertEqual(fin.isoformat(), "2026-10-25T00:00:00+01:00")

    def test_un_fuseau_invalide_retombe_sur_celui_de_django(self):
        reglages = ReglagesTelechargement(fuseau="Nulle/Part")

        jour, _ = quota.jour_et_reinitialisation(reglages, datetime(2026, 10, 24, 23, 30, tzinfo=fuseau_utc.utc))

        self.assertEqual(str(jour), "2026-10-25")


class VisiteurTests(_QuotaBase):
    def test_un_visiteur_telecharge_jusqu_a_la_limite_puis_est_refuse_en_appel_direct(self):
        codes = self._telecharger_tout(self.client, 5)

        self.assertEqual(codes, [200, 200, 200, 429, 429])
        refus = self._pdf(self.tous_les_cours[4])
        self.assertEqual(refus.json()["code"], "quota_depasse")
        self.assertEqual(refus.json()["restant"], 0)
        self.assertEqual(refus.json()["limite"], 3)
        self.assertEqual(refus.json()["profil"], "visiteur")
        self.assertTrue(int(refus["Retry-After"]) > 0)
        self.assertEqual(TelechargementPdf.objects.count(), 3)

    def test_redemander_le_meme_pdf_le_meme_jour_ne_coute_rien(self):
        for _ in range(6):
            self.assertEqual(self._pdf(self.cours).status_code, 200)

        self.assertEqual(TelechargementPdf.objects.count(), 1)
        self.assertEqual(self._statut().json()["restant"], 2)

    def test_les_en_tetes_disent_ce_qu_il_reste(self):
        reponse = self._pdf(self.cours)

        self.assertEqual(reponse["X-Quota-Limit"], "3")
        self.assertEqual(reponse["X-Quota-Remaining"], "2")
        self.assertIn("X-Quota-Reset", reponse)
        self.assertEqual(reponse["Cache-Control"], "private, no-store")

    def test_changer_de_user_agent_ou_d_entetes_ne_donne_pas_de_quota_en_plus(self):
        for i, cours in enumerate(self.tous_les_cours[:5]):
            self._pdf(cours, HTTP_USER_AGENT=f"Robot/{i}", HTTP_ACCEPT_LANGUAGE="en", HTTP_X_REAL_IP=f"8.8.8.{i}")

        self.assertEqual(TelechargementPdf.objects.count(), 3)

    def test_un_cookie_falsifie_n_est_pas_cru(self):
        client = APIClient()
        client.cookies[quota.COOKIE_VISITEUR] = "v:choisi-par-le-client"

        self._pdf(self.cours, client)

        self.assertFalse(TelechargementPdf.objects.filter(demandeur__contains="choisi").exists())
        self.assertIn(quota.COOKIE_VISITEUR, client.cookies)
        self.assertNotEqual(client.cookies[quota.COOKIE_VISITEUR].value, "v:choisi-par-le-client")

    def test_effacer_son_cookie_ne_donne_pas_un_quota_neuf_au_dela_du_plafond_d_identites(self):
        ReglagesTelechargement.objects.update_or_create(pk=1, defaults={"plafond_identites_reseau": 2})
        for _ in range(6):
            client = APIClient()  # cookie neuf à chaque fois
            self._telecharger_tout(client)

        # 2 identités reconnues (3 PDF chacune) + 1 quota commun pour tous les autres : 9 crédits, pas 18. Les
        # visiteurs du quota commun ne peuvent d'ailleurs redemander que les mêmes PDF (déjà livrés, donc gratuits).
        self.assertEqual(TelechargementPdf.objects.count(), 9)
        self.assertEqual(TelechargementPdf.objects.filter(demandeur__startswith="r:").count(), 3)

    def test_le_cookie_est_pose_http_only_et_signe(self):
        reponse = self._statut()

        morceau = reponse.cookies[quota.COOKIE_VISITEUR]
        self.assertTrue(morceau["httponly"])
        self.assertEqual(signing.loads(morceau.value, salt=quota._SEL_COOKIE, max_age=100).__len__(), 24)


class AbonnesTests(_QuotaBase):
    def test_un_abonne_actif_a_le_quota_abonne(self):
        ReglagesTelechargement.objects.update_or_create(pk=1, defaults={"quota_abonne": 5})
        self._abonner(self.cursus_c)
        self.client.force_authenticate(user=self.user)

        codes = self._telecharger_tout(self.client)

        self.assertEqual(codes, [200] * 5 + [429])
        self.assertEqual(self._statut().json()["profil"], "abonne")

    def test_un_abonnement_expire_ne_donne_pas_le_quota_abonne(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self._telecharger_tout(self.client, 4), [200, 200, 200, 429])
        self.assertEqual(self._statut().json()["profil"], "connecte")

    def test_un_connecte_sans_abonnement_a_le_quota_visiteur(self):
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self._telecharger_tout(self.client, 4), [200, 200, 200, 429])

    def test_un_abonne_n_est_pas_soumis_aux_plafonds_reseau_ni_au_budget_anonyme(self):
        ReglagesTelechargement.objects.update_or_create(
            pk=1, defaults={"plafond_reseau": 1, "plafond_reseau_large": 1, "budget_global_anonyme": 1, "quota_abonne": 4},
        )
        self._abonner(self.cursus_c)
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self._telecharger_tout(self.client, 4), [200] * 4)

    def test_le_quota_est_decide_par_le_serveur_pas_par_un_en_tete_du_client(self):
        self.client.credentials(HTTP_X_ABONNE="1", HTTP_X_QUOTA_LIMIT="999")
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self._telecharger_tout(self.client, 4), [200, 200, 200, 429])

    def test_deux_comptes_ont_des_compteurs_independants(self):
        autre = User.objects.create_user(phone_number="677100302", password="x")
        client_autre = APIClient()
        client_autre.force_authenticate(user=autre)
        self.client.force_authenticate(user=self.user)

        premier = self._telecharger_tout(self.client, 4)
        second = self._telecharger_tout(client_autre, 4)

        self.assertEqual(premier, [200, 200, 200, 429])
        self.assertEqual(second, [200, 200, 200, 429])

    def test_deux_visiteurs_independants_ont_chacun_leur_quota(self):
        a, b = APIClient(), APIClient()

        self.assertEqual(self._telecharger_tout(a, 4), [200, 200, 200, 429])
        self.assertEqual(self._telecharger_tout(b, 4), [200, 200, 200, 429])


class ReinitialisationTests(_QuotaBase):
    def _a(self, *args):
        return mock.patch("django.utils.timezone.now", return_value=datetime(*args, tzinfo=fuseau_utc.utc))

    def test_le_quota_repart_a_zero_au_changement_de_jour_a_douala(self):
        with self._a(2026, 10, 24, 22, 30):  # 23 h 30 à Douala
            self.assertEqual(self._telecharger_tout(self.client, 4), [200, 200, 200, 429])
        with self._a(2026, 10, 24, 22, 59):  # 23 h 59 : toujours le même jour
            self.assertEqual(self._pdf(self.tous_les_cours[3]).status_code, 429)
        with self._a(2026, 10, 24, 23, 1):  # 00 h 01 à Douala
            self.assertEqual(self._pdf(self.tous_les_cours[3]).status_code, 200)
            self.assertEqual(self._statut().json()["restant"], 2)

    def test_l_heure_du_navigateur_n_est_pas_prise_en_compte(self):
        with self._a(2026, 10, 24, 12, 0):
            self._telecharger_tout(self.client, 3)
            reponse = self._pdf(self.tous_les_cours[3], HTTP_DATE="Sat, 01 Jan 2050 00:00:00 GMT", HTTP_X_TIMEZONE="Pacific/Kiritimati")

        self.assertEqual(reponse.status_code, 429)

    def test_l_etat_donne_l_heure_de_remise_a_zero(self):
        with self._a(2026, 10, 24, 12, 0):
            donnees = self._statut().json()

        self.assertEqual(donnees["reinitialisation"], "2026-10-25T00:00:00+01:00")
        self.assertEqual(donnees["fuseau"], "Africa/Douala")


class ComptageTests(_QuotaBase):
    def test_head_ne_livre_rien_et_ne_consomme_rien(self):
        reponse = self.client.head(f"/access/cours/pdf/{self.cours.slug}/")

        self.assertEqual(reponse.status_code, 405)
        self.assertFalse(TelechargementPdf.objects.exists())

    def test_options_ne_consomme_rien(self):
        self.client.options(f"/access/cours/pdf/{self.cours.slug}/")

        self.assertFalse(TelechargementPdf.objects.exists())

    def test_une_requete_partielle_sans_unite_consomme_un_credit_puis_les_reprises_sont_gratuites(self):
        premiere = self._pdf(self.cours, HTTP_RANGE="bytes=3-")
        reprise = self._pdf(self.cours, HTTP_RANGE="bytes=5-")

        self.assertEqual(premiere.status_code, 200)
        self.assertEqual(reprise.status_code, 200)
        self.assertEqual(TelechargementPdf.objects.count(), 1)

    def test_on_ne_recupere_pas_un_pdf_par_tranches_sans_consommer(self):
        for cours in self.tous_les_cours[:5]:
            self._pdf(cours, HTTP_RANGE="bytes=1-")

        self.assertEqual(TelechargementPdf.objects.count(), 3)

    def test_une_erreur_avant_l_envoi_rend_le_credit(self):
        class _Casse:
            def __init__(self, vrai):
                self.vrai = vrai

            def __getattr__(self, nom):
                return getattr(self.vrai, nom)

            def open(self, *args, **kwargs):
                raise OSError("disque")

        vrai = cours_pdf.stockage()
        with mock.patch.object(cours_pdf, "stockage", return_value=_Casse(vrai)):
            with self.assertRaises(OSError):
                self._pdf(self.cours)

        self.assertFalse(TelechargementPdf.objects.exists())
        self.assertEqual(self._statut().json()["restant"], 3)

    def test_une_page_html_ou_json_ne_consomme_pas(self):
        self.client.get(f"/access/cours/read/{self.cours.slug}/")
        self.client.get(f"/access/cours/preview/{self.cours.slug}/")
        self._statut()
        self._statut()

        self.assertFalse(TelechargementPdf.objects.exists())
        self.assertEqual(self._statut().json()["restant"], 3)

    def test_un_cours_inconnu_ne_consomme_pas(self):
        self.assertEqual(self.client.get("/access/cours/pdf/n-existe-pas/").status_code, 404)

        self.assertFalse(TelechargementPdf.objects.exists())
        self.assertEqual(self._statut().json()["restant"], 3)

    def test_les_routes_protegees_sans_connexion_sont_refusees_sans_toucher_au_quota(self):
        for chemin in ("/fiches/1/sujet.pdf", "/fiches/1/corrige.pdf", "/inedit/epreuves/1/sujet.pdf",
                       "/quiz/sessions/1/sujet.pdf", "/quiz/sessions/1/corrige.pdf"):
            self.assertEqual(self.client.get(chemin).status_code, 401, chemin)

        self.assertFalse(TelechargementPdf.objects.exists())
        self.assertEqual(self._statut().json()["restant"], 3)

    def test_les_routes_protegees_d_un_autre_ou_inexistantes_donnent_404_sans_consommer(self):
        self.client.force_authenticate(user=self.user)
        for chemin in ("/fiches/999/sujet.pdf", "/quiz/sessions/999/sujet.pdf"):
            self.assertEqual(self.client.get(chemin).status_code, 404, chemin)
        # Pas d'accès à l'add-on Épreuves Inédites : refusé avant tout calcul de quota.
        self.assertIn(self.client.get("/inedit/epreuves/999/sujet.pdf").status_code, (403, 404))

        self.assertFalse(TelechargementPdf.objects.exists())
        self.assertEqual(self._statut().json()["restant"], 3)

    def test_un_refus_est_compte_dans_les_statistiques_agregees_sans_ligne_de_journal(self):
        self._telecharger_tout(self.client, 5)

        refus = CompteurQuota.objects.get(portee="refus_quota_depasse")
        atteint = CompteurQuota.objects.get(portee="quota_atteint")
        self.assertEqual(refus.nombre, 2)
        self.assertEqual(atteint.nombre, 1)
        self.assertEqual(TelechargementPdf.objects.count(), 3)

    def test_aucune_donnee_personnelle_dans_le_journal(self):
        self.client.force_authenticate(user=self.user)
        self._pdf(self.cours, REMOTE_ADDR="203.0.113.7", HTTP_USER_AGENT="Mozilla/5.0 test", HTTP_AUTHORIZATION="Bearer secret")

        brut = " ".join(
            f"{l.demandeur} {l.document} {l.type_demandeur}" for l in TelechargementPdf.objects.all()
        ) + " ".join(f"{c.portee} {c.cle}" for c in CompteurQuota.objects.all())
        for interdit in ("203.0.113.7", "Mozilla", "secret", self.user.phone_number):
            self.assertNotIn(interdit, brut)

    def test_quota_desactive_les_telechargements_ne_sont_plus_limites(self):
        ReglagesTelechargement.objects.update_or_create(pk=1, defaults={"actif": False})

        self.assertEqual(self._telecharger_tout(self.client), [200] * len(self.tous_les_cours))
        self.assertFalse(TelechargementPdf.objects.exists())
        self.assertNotIn("X-Quota-Limit", self._pdf(self.cours))

    def test_la_generation_n_est_pas_lancee_quand_il_n_y_a_plus_de_credit(self):
        self._telecharger_tout(self.client, 3)
        sans_pdf = self._nouveau_cours(99)

        with mock.patch.object(cours_pdf, "mettre_en_file") as file_attente:
            reponse = self._pdf(sans_pdf)

        self.assertEqual(reponse.status_code, 429)
        file_attente.assert_not_called()

    def test_la_preparation_d_un_pdf_ne_consomme_pas(self):
        sans_pdf = self._nouveau_cours(98)  # aucun PDF en cache : le serveur répond 202 et lance la génération

        with mock.patch.object(cours_pdf, "mettre_en_file", return_value=cours_pdf.EN_PREPARATION):
            reponse = self._pdf(sans_pdf)

        self.assertEqual(reponse.status_code, 202)
        self.assertFalse(TelechargementPdf.objects.exists())
        self.assertEqual(self._statut().json()["restant"], 3)

    def test_les_messages_sont_en_anglais_pour_un_navigateur_anglophone(self):
        self._telecharger_tout(self.client, 3)

        refus = self._pdf(self.tous_les_cours[3], HTTP_ACCEPT_LANGUAGE="en-GB,en;q=0.9")

        self.assertIn("daily limit", refus.json()["error"])
        self.assertIn("limite quotidienne", self._pdf(self.tous_les_cours[3]).json()["error"])


class StatutTests(_QuotaBase):
    def test_le_statut_est_lisible_par_un_visiteur_et_ne_consomme_rien(self):
        donnees = self._statut().json()

        self.assertEqual(donnees["limite"], 3)
        self.assertEqual(donnees["utilise"], 0)
        self.assertEqual(donnees["restant"], 3)
        self.assertEqual(donnees["profil"], "visiteur")
        self.assertTrue(donnees["actif"])

    def test_le_statut_suit_les_telechargements_et_signale_les_documents_deja_pris(self):
        self._pdf(self.cours)

        donnees = self._statut(QUERY_STRING=f"doc=cours:{self.cours.slug}&doc=cours:{self.tous_les_cours[1].slug}&doc=n:importe").json()

        self.assertEqual(donnees["utilise"], 1)
        self.assertEqual(donnees["restant"], 2)
        self.assertEqual(donnees["gratuits"], [f"cours:{self.cours.slug}"])

    def test_le_statut_d_un_visiteur_epuise_est_a_zero(self):
        self._telecharger_tout(self.client, 3)

        donnees = self._statut().json()

        self.assertEqual(donnees["restant"], 0)
        self.assertEqual(donnees["utilise"], 3)


class PlafondsReseauTests(_QuotaBase):
    def test_deux_visiteurs_sur_la_meme_connexion_ont_chacun_leur_quota(self):
        a, b = APIClient(), APIClient()

        self.assertEqual(self._telecharger_tout(a, 3, ), [200, 200, 200])
        self.assertEqual(
            [self._pdf(c, b, REMOTE_ADDR="127.0.0.1").status_code for c in self.tous_les_cours[:3]], [200, 200, 200],
        )

    def test_le_plafond_du_reseau_est_fini(self):
        ReglagesTelechargement.objects.update_or_create(pk=1, defaults={"plafond_reseau": 4})
        a, b = APIClient(), APIClient()
        self._telecharger_tout(a, 3)

        codes = self._telecharger_tout(b, 3)

        self.assertEqual(codes, [200, 429, 429])
        self.assertEqual(self._pdf(self.tous_les_cours[1], b).json()["code"], "plafond_reseau")

    def test_les_entrees_de_gauche_de_x_forwarded_for_sont_ignorees(self):
        ReglagesTelechargement.objects.update_or_create(pk=1, defaults={"plafond_reseau": 3, "plafond_identites_reseau": 100})
        total = 0
        for i in range(5):
            client = APIClient()
            faux = f"10.0.0.{i}, 5.5.5.5"  # le proxy de confiance a écrit la dernière entrée : 5.5.5.5
            total += [self._pdf(c, client, HTTP_X_FORWARDED_FOR=faux).status_code for c in self.tous_les_cours[:3]].count(200)

        self.assertEqual(total, 3)

    def test_des_reseaux_differents_ne_se_bloquent_pas(self):
        ReglagesTelechargement.objects.update_or_create(pk=1, defaults={"plafond_reseau": 3, "plafond_reseau_large": 1000})
        total = 0
        for i in range(3):
            client = APIClient()
            total += [self._pdf(c, client, HTTP_X_FORWARDED_FOR=f"198.51.{i}.9").status_code for c in self.tous_les_cours[:3]].count(200)

        self.assertEqual(total, 9)

    def test_changer_d_adresse_dans_un_meme_bloc_ne_contourne_pas_le_plafond_large(self):
        ReglagesTelechargement.objects.update_or_create(
            pk=1, defaults={"plafond_reseau": 1000, "plafond_reseau_large": 6, "plafond_identites_reseau": 1000},
        )
        total = 0
        for i in range(10):
            client = APIClient()
            total += [self._pdf(c, client, HTTP_X_FORWARDED_FOR=f"192.0.2.{i + 1}").status_code for c in self.tous_les_cours[:3]].count(200)

        self.assertEqual(total, 6)

    def test_ipv6_un_meme_prefixe_64_est_un_meme_reseau(self):
        a = quota._reseaux("2001:db8:1:2:aaaa::1")
        b = quota._reseaux("2001:db8:1:2:bbbb::9")
        c = quota._reseaux("2001:db8:1:3::1")

        self.assertEqual(a[0], b[0])
        self.assertNotEqual(a[0], c[0])
        self.assertEqual(a[1], c[1])  # même /48

    def test_le_budget_global_des_anonymes_coupe_les_anonymes_mais_pas_les_abonnes(self):
        ReglagesTelechargement.objects.update_or_create(
            pk=1, defaults={"budget_global_anonyme": 2, "plafond_reseau": 1000, "plafond_reseau_large": 1000},
        )
        anonymes = [self._pdf(self.cours, APIClient(), HTTP_X_FORWARDED_FOR=f"203.0.113.{i}") for i in range(4)]
        self._abonner(self.cursus_c)
        abonne = APIClient()
        abonne.force_authenticate(user=self.user)

        self.assertEqual([r.status_code for r in anonymes], [200, 200, 429, 429])
        self.assertEqual(anonymes[2].json()["code"], "budget_global")
        self.assertEqual(self._pdf(self.cours, abonne).status_code, 200)

    def test_les_comptes_sans_abonnement_comptent_dans_le_plafond_du_reseau(self):
        ReglagesTelechargement.objects.update_or_create(pk=1, defaults={"plafond_reseau": 4})
        total = 0
        for i in range(4):
            utilisateur = User.objects.create_user(phone_number=f"67710040{i}", password="x")
            client = APIClient()
            client.force_authenticate(user=utilisateur)
            total += self._telecharger_tout(client, 3).count(200)

        self.assertEqual(total, 4)


class LessonSujetPublicTests(_QuotaBase):
    def setUp(self):
        super().setUp()
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        surcharge = override_settings(MEDIA_ROOT=self.media.name)
        surcharge.enable()
        self.addCleanup(surcharge.disable)
        (Path(self.media.name) / "sujets_pdf").mkdir()
        self.lessons = []
        for i in range(5):
            (Path(self.media.name) / "sujets_pdf" / f"s{i}.pdf").write_bytes(f"%PDF-sujet-{i}".encode())
            self.lessons.append(Lesson.objects.create(
                title=f"Epreuve {i}", subject=self.subject, lesson_type=LessonType.CORR,
                statut=StatutContenu.VALIDE, sujet_pdf=f"sujets_pdf/s{i}.pdf",
            ))

    def _sujet(self, lesson, client=None, **extra):
        return (client or self.client).get(f"/access/lessons/{lesson.pk}/sujet.pdf", **extra)

    def test_le_sujet_public_est_servi_et_compte_dans_le_quota(self):
        codes = [self._sujet(l).status_code for l in self.lessons[:4]]

        self.assertEqual(codes, [200, 200, 200, 429])
        reponse = self._sujet(self.lessons[0])
        self.assertEqual(b"".join(reponse.streaming_content), b"%PDF-sujet-0")
        self.assertEqual(reponse["Content-Type"], "application/pdf")

    def test_le_quota_est_partage_entre_cours_et_sujets(self):
        self._pdf(self.cours)
        self._pdf(self.tous_les_cours[1])
        self.assertEqual(self._sujet(self.lessons[0]).status_code, 200)
        self.assertEqual(self._sujet(self.lessons[1]).status_code, 429)

    def test_un_sujet_sans_pdf_ou_inexistant_donne_404_sans_consommer(self):
        sans = Lesson.objects.create(title="Sans", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE)

        self.assertEqual(self._sujet(sans).status_code, 404)
        self.assertEqual(self.client.get("/access/lessons/99999/sujet.pdf").status_code, 404)
        self.assertFalse(TelechargementPdf.objects.exists())

    def test_l_api_n_expose_plus_l_adresse_directe_du_fichier(self):
        detail = self.client.get(f"/catalog/lessons/{self.lessons[0].slug}/")
        liste = self.client.get("/catalog/lessons/")

        self.assertEqual(detail.status_code, 200)
        self.assertEqual(liste.status_code, 200)
        for reponse in (detail, liste):
            brut = reponse.content.decode()
            self.assertNotIn("/media/sujets_pdf", brut)
            self.assertNotIn("sujets_pdf/s0.pdf", brut)
        self.assertTrue(detail.json()["sujet_pdf_url"].endswith(f"/access/lessons/{self.lessons[0].pk}/sujet.pdf"))

    def test_la_lecture_en_ligne_donne_la_route_et_pas_le_fichier(self):
        lesson = self.lessons[0]
        lesson.est_vitrine = True
        lesson.save(update_fields=["est_vitrine"])

        reponse = self.client.get(f"/access/read/{lesson.slug}/")

        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.json()["sujet_pdf_url"].endswith(f"/access/lessons/{lesson.pk}/sujet.pdf"))
        self.assertNotIn("sujets_pdf/s0.pdf", reponse.content.decode())

    def test_le_caddyfile_bloque_l_acces_direct_aux_sujets(self):
        caddyfile = Path(__file__).resolve().parents[2] / "docker" / "caddy" / "Caddyfile"
        if not caddyfile.exists():
            self.skipTest("Caddyfile absent du conteneur")
        texte = caddyfile.read_text(encoding="utf-8")

        self.assertIn("@pdf_sujets_prives path /media/sujets_pdf/*", texte)
        self.assertLess(texte.index("@pdf_sujets_prives"), texte.index("handle_path /media/*"))


class DebitTests(_QuotaBase):
    def test_un_robot_qui_martele_est_ralenti_avant_meme_le_quota(self):
        from rest_framework import status

        with override_settings(THROTTLE_PDF_ACTIF=True), mock.patch.object(quota.QuotaThrottle, "rate", "3/min"):
            cache.clear()
            codes = [self._statut().status_code for _ in range(5)]

        self.assertEqual(codes[:3], [200, 200, 200])
        self.assertEqual(codes[3:], [status.HTTP_429_TOO_MANY_REQUESTS] * 2)


class PurgeTests(TestCase):
    def test_la_purge_supprime_le_vieux_journal_et_garde_le_recent(self):
        reglages = ReglagesTelechargement.charger()
        aujourdhui, _ = quota.jour_et_reinitialisation(reglages)
        vieux = aujourdhui - timedelta(days=reglages.retention_jours + 5)
        TelechargementPdf.objects.create(jour=vieux, demandeur="v:a", type_demandeur="visiteur", document="cours:1")
        TelechargementPdf.objects.create(jour=aujourdhui, demandeur="v:a", type_demandeur="visiteur", document="cours:2")
        CompteurQuota.objects.create(jour=vieux, portee="demandeur", cle="v:a", nombre=3)

        call_command("purger_telechargements", verbosity=0)

        self.assertEqual(list(TelechargementPdf.objects.values_list("document", flat=True)), ["cours:2"])
        self.assertFalse(CompteurQuota.objects.exists())

    def test_les_statistiques_s_affichent(self):
        from io import StringIO

        sortie = StringIO()
        call_command("stats_telechargements", stdout=sortie)

        self.assertIn("PDF délivrés", sortie.getvalue())


class ConcurrenceTests(TransactionTestCase):
    """Des requêtes simultanées du MÊME demandeur ne dépassent jamais le quota."""

    def test_des_requetes_simultanees_ne_depassent_pas_le_quota(self):
        visiteur = "a" * 24
        cookie = signing.dumps(visiteur, salt=quota._SEL_COOKIE)
        resultats, erreurs = [], []
        depart = threading.Barrier(8)

        def tache(i):
            try:
                requete = RequestFactory().get("/x", REMOTE_ADDR="192.0.2.50")
                requete.user = AnonymousUser()
                requete.COOKIES = {quota.COOKIE_VISITEUR: cookie}
                depart.wait(timeout=10)
                resultats.append(quota.autoriser(requete, f"cours:{i}").autorise)
            except Exception as exc:  # SQLite verrouille parfois la table : jamais un dépassement
                erreurs.append(exc)
            finally:
                connection.close()

        fils = [threading.Thread(target=tache, args=(i,)) for i in range(8)]
        for f in fils:
            f.start()
        for f in fils:
            f.join(timeout=30)

        accordes = sum(1 for r in resultats if r)
        self.assertLessEqual(accordes, 3)
        self.assertEqual(TelechargementPdf.objects.count(), accordes)
        self.assertLessEqual(
            CompteurQuota.objects.filter(portee="demandeur").values_list("nombre", flat=True).first() or 0, 3,
        )
        self.assertGreaterEqual(accordes, 1, erreurs)

    def test_la_meme_requete_en_double_ne_coute_qu_un_credit(self):
        visiteur = "b" * 24
        cookie = signing.dumps(visiteur, salt=quota._SEL_COOKIE)
        for _ in range(4):
            requete = RequestFactory().get("/x", REMOTE_ADDR="192.0.2.51")
            requete.user = AnonymousUser()
            requete.COOKIES = {quota.COOKIE_VISITEUR: cookie}
            decision = quota.autoriser(requete, "cours:1")
            self.assertTrue(decision.autorise)

        self.assertEqual(TelechargementPdf.objects.count(), 1)
        self.assertEqual(CompteurQuota.objects.get(portee="demandeur").nombre, 1)
