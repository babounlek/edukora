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


class ApercuAideTests(TestCase):
    """Aperçu d'un lien /aide/<article> collé dans WhatsApp : titre et résumé de l'article, pas la carte générique."""

    def setUp(self):
        creer_article(
            slug="comment-payer", categorie=CategorieAide.PAIEMENT, titre_fr="Comment payer {{site}} ?",
            resume_fr="Les étapes du paiement Mobile Money. Écris-nous au {{whatsapp}}.",
        )
        creer_article(
            slug="traduit", titre_fr="Un article traduit", resume_fr="Le résumé français.",
            titre_en="A translated article", resume_en="The English summary.", corps_en="Body",
        )

    def test_francais(self):
        html = self.client.get("/partage-apercu/aide/comment-payer").content.decode()
        self.assertIn('<html lang="fr">', html)
        self.assertIn("Comment payer ", html)
        self.assertNotIn("{{", html)
        self.assertIn("Les étapes du paiement Mobile Money.", html)
        self.assertIn("/aide/comment-payer", html)
        self.assertIn("/partage-image/aide/comment-payer.png", html)

    def test_anglais_traduit_et_non_traduit(self):
        html = self.client.get("/partage-apercu/en/help/traduit").content.decode()
        self.assertIn('<html lang="en">', html)
        self.assertIn("A translated article", html)
        self.assertIn("/en/help/traduit", html)
        # Non traduit : le texte français, mais le lien reste celui de la langue demandée.
        html = self.client.get("/partage-apercu/en/help/comment-payer").content.decode()
        self.assertIn("Les étapes du paiement Mobile Money.", html)
        self.assertIn("/en/help/comment-payer", html)

    def test_article_inconnu_ou_masque_retombe_sur_la_carte_generique(self):
        creer_article(slug="cache", publie=False, titre_fr="Article caché")
        for chemin in ("aide/n-existe-pas", "aide/cache"):
            html = self.client.get(f"/partage-apercu/{chemin}").content.decode()
            self.assertNotIn("Article caché", html)
            self.assertIn("/partage-image/defaut.png", html)

    def test_image_png(self):
        from io import BytesIO

        from PIL import Image

        reponse = self.client.get("/partage-image/aide/comment-payer.png")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(Image.open(BytesIO(reponse.content)).size, (1200, 630))
        self.assertEqual(self.client.get("/partage-image/aide/n-existe-pas.png").status_code, 404)

    def test_caddy_envoie_les_robots_vers_l_apercu_des_articles(self):
        from pathlib import Path

        chemin = Path(__file__).resolve().parents[2] / "docker" / "caddy" / "Caddyfile"
        if not chemin.exists():  # dans l'image backend, le dépôt n'est pas là
            self.skipTest("Caddyfile absent de cet environnement")
        caddyfile = chemin.read_text(encoding="utf-8")
        self.assertIn("mock-papers|aide|help)/[^/]+", caddyfile)


class RapportAideTests(TestCase):
    def evenement(self, nom, **props):
        from analytics.models import AnalyticsEvent

        AnalyticsEvent.objects.create(name=nom, properties=props)

    def test_lectures_avis_contacts_et_articles_a_reecrire(self):
        from .rapport import rapport_aide

        creer_article(slug="bon", titre_fr="Bon")
        creer_article(slug="mauvais", titre_fr="Mauvais")
        creer_article(slug="jamais-lu", titre_fr="Jamais lu")
        for _ in range(12):
            self.evenement(EventName.AIDE_ARTICLE_VU, slug="mauvais", categorie="connexion")
        for _ in range(4):
            self.evenement(EventName.AIDE_ARTICLE_VU, slug="bon", categorie="connexion")
        for utile in (True, True, True, True, True, True):
            self.evenement(EventName.AIDE_ARTICLE_UTILE, slug="bon", utile=utile)
        for utile in (False, False, False, True, False):
            self.evenement(EventName.AIDE_ARTICLE_UTILE, slug="mauvais", utile=utile)
        for _ in range(4):
            self.evenement(EventName.AIDE_CONTACT_CLIC, source="article", slug="mauvais")
        self.evenement(EventName.AIDE_CONTACT_CLIC, source="centre")
        self.evenement(EventName.SEARCH_NO_RESULTS, source="aide")
        self.evenement(EventName.SEARCH_NO_RESULTS, source="recherche")

        rapport = rapport_aide(30)
        lignes = {ligne["slug"]: ligne for ligne in rapport["articles"]}
        self.assertEqual(rapport["articles"][0]["slug"], "mauvais")  # le plus lu d'abord
        self.assertEqual((lignes["mauvais"]["vues"], lignes["mauvais"]["oui"], lignes["mauvais"]["non"]), (12, 1, 4))
        self.assertEqual(lignes["mauvais"]["taux_utile"], 20.0)
        self.assertEqual(lignes["mauvais"]["taux_contact"], 33.3)
        self.assertEqual(lignes["mauvais"]["a_reecrire"], ["jugé peu utile", "souvent suivi d'un message au support"])
        self.assertEqual(lignes["bon"]["a_reecrire"], [])  # 4 lectures : trop peu pour juger
        self.assertEqual(rapport["jamais_lus"], ["jamais-lu"])
        self.assertEqual(rapport["total_contacts"], 5)
        self.assertEqual(rapport["contacts_hors_article"], 1)
        self.assertEqual(rapport["recherches_sans_resultat"], 1)  # seule la source « aide » compte

    def test_fenetre_en_jours(self):
        from datetime import timedelta

        from django.utils import timezone

        from analytics.models import AnalyticsEvent

        from .rapport import rapport_aide

        creer_article(slug="bon", titre_fr="Bon")
        self.evenement(EventName.AIDE_ARTICLE_VU, slug="bon")
        AnalyticsEvent.objects.update(created_at=timezone.now() - timedelta(days=40))
        self.assertEqual(rapport_aide(30)["total_vues"], 0)
        self.assertEqual(rapport_aide(90)["total_vues"], 1)

    def test_commande_et_page_d_admin(self):
        from io import StringIO

        creer_article(slug="bon", titre_fr="Bon")
        sortie = StringIO()
        call_command("rapport_aide", "--jours", "7", stdout=sortie)
        self.assertIn("Centre d'aide - 7 derniers jours", sortie.getvalue())

        admin = get_user_model().objects.create_superuser(phone_number="+237600000097", password="x")
        self.client.force_login(admin)
        reponse = self.client.get(reverse("admin:aide_rapport"), {"jours": "90"})
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Le centre d&#x27;aide sert-il ?")
        self.assertContains(reponse, "Bon")
        self.assertEqual(self.client.get(reverse("admin:aide_rapport"), {"jours": "abc"}).status_code, 200)
