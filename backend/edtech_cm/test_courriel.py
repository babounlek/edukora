"""Le gabarit commun des e-mails (voir edtech_cm.courriel)."""

from django.conf import settings
from django.test import SimpleTestCase

from . import courriel


class CourrielTests(SimpleTestCase):
    def message(self, **options):
        c = courriel.Courriel(
            courriel.FR, salutation="Bonjour Awa,", titre="Un titre", apercu="L'aperçu",
            bouton=("Ouvrir", "https://exemple.test/page?a=1&b=2"), raison="Tu reçois ce message parce que.",
            arret=("L'arrêter en un clic", "https://exemple.test/arret/jeton/"), **options,
        )
        return c.paragraphe("Environ 25 minutes, choisies pour toi.", gras="25 minutes") \
            .liste(["un", "deux"]).encart(["Un fait.", "Un autre fait."]).intertitre("Junior").code("123456")

    def test_le_texte_brut_reprend_tout_le_message_dans_l_ordre(self):
        texte = self.message().texte()

        attendus = [
            "Bonjour Awa,", "Un titre", "Environ 25 minutes, choisies pour toi.", "- un\n- deux",
            "Un fait.\nUn autre fait.", "■ Junior", "123456", "Ouvrir : https://exemple.test/page?a=1&b=2",
            "Une question ? Réponds simplement à ce message.",
            "Tu reçois ce message parce que.\nL'arrêter en un clic : https://exemple.test/arret/jeton/",
        ]
        positions = [texte.index(a) for a in attendus]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("L'aperçu", texte)

    def test_le_html_porte_la_marque_et_les_memes_faits(self):
        html = self.message().html()

        self.assertIn(f'src="{settings.FRONTEND_URL}/pwa-192.png"', html)
        self.assertIn("#0a6745", html)
        self.assertIn("Réussis ton examen", html)
        for fait in ("Bonjour Awa,", "Un titre", "<strong>25 minutes</strong>", "Un autre fait.", "Junior", "123456",
                     "L&#x27;aperçu"):
            self.assertIn(fait, html)
        self.assertIn('href="https://exemple.test/page?a=1&amp;b=2"', html)
        self.assertIn('href="https://exemple.test/arret/jeton/"', html)
        self.assertIn(f"mailto:{settings.SUPPORT_EMAIL}", html)
        self.assertNotIn("{{", html)
        self.assertNotIn("{%", html)

    def test_le_texte_des_blocs_est_echappe_dans_le_html(self):
        c = courriel.Courriel(courriel.FR)
        c.paragraphe("<script>x</script> et 25 minutes", gras="25 minutes").encart(["<b>gras</b>"])

        html = c.html()

        self.assertNotIn("<script>x", html)
        self.assertIn("&lt;script&gt;x&lt;/script&gt; et <strong>25 minutes</strong>", html)
        self.assertIn("&lt;b&gt;gras&lt;/b&gt;", html)

    def test_sans_bouton_ni_question_rien_n_en_reste(self):
        c = courriel.Courriel(courriel.FR, question=False).paragraphe("Seul.")

        self.assertEqual(c.texte(), "Seul.")
        html = c.html()
        self.assertNotIn("Le bouton ne s", html)
        self.assertNotIn("mailto:", html)

    def test_en_anglais(self):
        c = courriel.Courriel(courriel.EN, bouton=("Open", "https://exemple.test/"))

        self.assertIn("Open: https://exemple.test/", c.texte())
        self.assertIn("A question? Just reply to this message.", c.texte())
        html = c.html()
        self.assertIn('lang="en"', html)
        self.assertIn("Pass your exam", html)
        self.assertIn("Can&#x27;t see the button?", html)

    def test_montant_et_salutation(self):
        self.assertEqual(courriel.montant_fcfa(2000), "2 000")
        self.assertEqual(courriel.montant_fcfa(15000), "15 000")
        self.assertEqual(courriel.montant_fcfa(500), "500")

        class Compte:
            full_name = "Awa Mballa"
            pseudo = ""

        self.assertEqual(courriel.salutation(Compte()), "Bonjour Awa,")
        self.assertEqual(courriel.salutation(Compte(), courriel.EN), "Hello Awa,")
        Compte.full_name = ""
        self.assertEqual(courriel.salutation(Compte()), "Bonjour,")
