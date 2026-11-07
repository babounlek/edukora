from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from analytics.models import EventName

from .code_assistance import code_pour, user_id_depuis_code
from .management.commands import charger_aide
from .models import ArticleAide, CategorieAide


def creer_article(**surcharge):
    donnees = dict(
        slug="code-non-recu",
        categorie=CategorieAide.CONNEXION,
        titre_fr="Je ne reçois pas mon code",
        resume_fr="Où chercher le code de connexion.",
        corps_fr="Regarde dans tes spams.",
        mots_cles_fr="otp, sms",
    )
    donnees.update(surcharge)
    return ArticleAide.objects.create(**donnees)


class ApiAideTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_liste_sans_corps_et_sans_connexion(self):
        creer_article()
        creer_article(slug="brouillon", publie=False, titre_fr="Brouillon")
        reponse = self.client.get(reverse("aide:articles"))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual([a["slug"] for a in reponse.json()], ["code-non-recu"])
        self.assertNotIn("corps", reponse.json()[0])

    def test_anglais_et_repli_sur_le_francais(self):
        creer_article(titre_en="I do not get my code", resume_en="Where to look.", corps_en="Check spam.")
        creer_article(slug="seul-fr", titre_fr="Seulement français")
        liste = {a["slug"]: a for a in self.client.get(reverse("aide:articles"), {"langue": "en"}).json()}
        self.assertEqual(liste["code-non-recu"]["titre"], "I do not get my code")
        self.assertTrue(liste["code-non-recu"]["traduit"])
        self.assertEqual(liste["seul-fr"]["titre"], "Seulement français")
        self.assertFalse(liste["seul-fr"]["traduit"])

    def test_detail_avec_corps_voisins_et_404(self):
        creer_article()
        creer_article(slug="autre", titre_fr="Autre", ordre=5)
        creer_article(slug="paiement-x", categorie=CategorieAide.PAIEMENT, titre_fr="Paiement")
        detail = self.client.get(reverse("aide:article", args=["code-non-recu"])).json()
        self.assertEqual(detail["corps"], "Regarde dans tes spams.")
        self.assertEqual([v["slug"] for v in detail["voisins"]], ["autre"])
        self.assertEqual(self.client.get(reverse("aide:article", args=["inconnu"])).status_code, 404)
        creer_article(slug="cache", publie=False)
        self.assertEqual(self.client.get(reverse("aide:article", args=["cache"])).status_code, 404)

    def test_mon_code_demande_une_connexion(self):
        self.assertEqual(self.client.get(reverse("aide:mon-code")).status_code, 401)
        utilisateur = get_user_model().objects.create_user(phone_number="+237600000001")
        self.client.force_authenticate(utilisateur)
        code = self.client.get(reverse("aide:mon-code")).json()["code"]
        self.assertEqual(user_id_depuis_code(code), utilisateur.pk)

    def test_evenements_analytics_du_centre_d_aide_acceptes(self):
        for nom in (EventName.AIDE_ARTICLE_VU, EventName.AIDE_ARTICLE_UTILE, EventName.AIDE_CONTACT_CLIC):
            reponse = self.client.post("/analytics/events/", {"name": nom.value, "properties": {"slug": "x"}}, format="json")
            self.assertEqual(reponse.status_code, 201, nom)


class CodeAssistanceTests(TestCase):
    def test_aller_retour(self):
        for identifiant in (1, 35, 36, 1295, 123456):
            self.assertEqual(user_id_depuis_code(code_pour(identifiant)), identifiant)

    def test_tolere_la_casse_et_les_espaces(self):
        self.assertEqual(user_id_depuis_code(f"  {code_pour(77).lower()} "), 77)

    def test_une_faute_de_recopie_est_refusee(self):
        code = code_pour(4242)
        corps, controle = code.split("-")[1:]
        faux_controle = "0" if controle != "0" else "1"
        self.assertIsNone(user_id_depuis_code(f"EK-{corps}-{faux_controle}"))
        self.assertIsNone(user_id_depuis_code("n'importe quoi"))
        self.assertIsNone(user_id_depuis_code(""))
        self.assertIsNone(user_id_depuis_code(None))


class ChargerAideTests(TestCase):
    def test_les_articles_livres_sont_valides_et_chargeables(self):
        """Les fichiers du dépôt eux-mêmes : en-têtes complets, rubriques connues, pas de montant en dur."""
        call_command("charger_aide", stdout=_Vide())
        self.assertGreaterEqual(ArticleAide.objects.count(), 25)
        for article in ArticleAide.objects.all():
            self.assertTrue(article.corps_fr.strip(), article.slug)
            self.assertNotRegex(article.corps_fr + article.corps_en, r"\d[\d  ]*\s?(FCFA|XAF|F CFA)", f"montant en dur dans {article.slug}")
            if article.traduit:
                self.assertTrue(article.resume_en and article.corps_en, article.slug)

    def test_idempotent(self):
        call_command("charger_aide", stdout=_Vide())
        nombre = ArticleAide.objects.count()
        call_command("charger_aide", stdout=_Vide())
        self.assertEqual(ArticleAide.objects.count(), nombre)

    def test_n_ecrase_pas_une_retouche_de_l_admin_sauf_forcer(self):
        call_command("charger_aide", stdout=_Vide())
        article = ArticleAide.objects.first()
        titre_fichier = article.titre_fr
        ArticleAide.objects.filter(pk=article.pk).update(titre_fr="Retouché", modifie_a_la_main=True)
        call_command("charger_aide", stdout=_Vide())
        self.assertEqual(ArticleAide.objects.get(pk=article.pk).titre_fr, "Retouché")
        call_command("charger_aide", "--forcer", stdout=_Vide())
        retabli = ArticleAide.objects.get(pk=article.pk)
        self.assertEqual(retabli.titre_fr, titre_fichier)
        self.assertFalse(retabli.modifie_a_la_main)

    def test_a_blanc_n_ecrit_rien(self):
        call_command("charger_aide", "--a-blanc", stdout=_Vide())
        self.assertEqual(ArticleAide.objects.count(), 0)

    def test_en_tete_invalide_refuse(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as dossier:
            Path(dossier, "casse.md").write_text("pas d'en-tête", encoding="utf-8")
            ancien = charger_aide.DOSSIER
            charger_aide.DOSSIER = Path(dossier)
            try:
                with self.assertRaises(CommandError):
                    charger_aide.lire_articles()
            finally:
                charger_aide.DOSSIER = ancien


class AdminAideTests(TestCase):
    def test_retrouver_un_compte_depuis_son_code(self):
        modele = get_user_model()
        admin = modele.objects.create_superuser(phone_number="+237600000099", password="x")
        eleve = modele.objects.create_user(phone_number="+237600000002")
        client = self.client
        client.force_login(admin)
        reponse = client.get(reverse("admin:aide_retrouver_compte"), {"code": code_pour(eleve.pk)})
        self.assertEqual(reponse.status_code, 302)
        self.assertIn(str(eleve.pk), reponse["Location"])
        self.assertEqual(client.get(reverse("admin:aide_retrouver_compte"), {"code": "EK-ZZ-0"}).status_code, 404)

    def test_une_sauvegarde_dans_l_admin_marque_l_article_retouche(self):
        modele = get_user_model()
        admin = modele.objects.create_superuser(phone_number="+237600000098", password="x")
        article = creer_article()
        self.client.force_login(admin)
        reponse = self.client.post(
            reverse("admin:aide_articleaide_change", args=[article.pk]),
            {
                "slug": article.slug, "categorie": article.categorie, "ordre": 1, "publie": "on",
                "titre_fr": "Titre corrigé", "resume_fr": "r", "corps_fr": "c", "mots_cles_fr": "",
                "titre_en": "", "resume_en": "", "corps_en": "", "mots_cles_en": "", "pages_liees": "",
            },
        )
        self.assertEqual(reponse.status_code, 302)
        article.refresh_from_db()
        self.assertEqual(article.titre_fr, "Titre corrigé")
        self.assertTrue(article.modifie_a_la_main)


class _Vide:
    def write(self, *_):
        pass

    def flush(self):
        pass


class SitemapAideTests(TestCase):
    def test_page_d_aide_bilingue_et_articles_selon_la_traduction(self):
        from django.conf import settings

        creer_article(slug="en-francais-seulement")
        creer_article(slug="traduit", titre_en="Translated", resume_en="r", corps_en="c")
        creer_article(slug="brouillon", publie=False)
        xml = self.client.get(reverse("sitemap-chunk", args=[1])).content.decode()
        base = settings.FRONTEND_URL
        self.assertIn(f"<loc>{base}/aide</loc>", xml)
        self.assertIn(f"<loc>{base}/en/help</loc>", xml)
        self.assertIn(f"<loc>{base}/aide/en-francais-seulement</loc>", xml)
        self.assertNotIn("/en/help/en-francais-seulement", xml)
        self.assertIn(f"<loc>{base}/en/help/traduit</loc>", xml)
        self.assertNotIn("/aide/brouillon", xml)
