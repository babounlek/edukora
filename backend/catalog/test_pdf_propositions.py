"""Les propositions d'une QCM dans les PDF de quiz et de fiches : sans elles, l'énoncé imprimé ne se lit pas."""
import re

import markdown
from django.test import SimpleTestCase

from .pdf_textes import EXTENSIONS_MARKDOWN_QUIZ, bonne_reponse_markdown, propositions_markdown, textes_pdf
from .sujet_pdf import _italicize_quotes, _protect_math, _restore_math

CHOIX = [
    {"lettre": "a", "texte": "Un navigateur"},
    {"lettre": "b", "texte": "Un antivirus"},
    {"lettre": "c", "texte": "Un traitement de texte"},
    {"lettre": "d", "texte": "Un système d'exploitation"},
]


def _html(md):
    """La même chaîne que quiz.pdf._render_html et fiches.pdf._render_html."""
    protege, spans = _protect_math(md)
    return _restore_math(markdown.markdown(_italicize_quotes(protege), extensions=EXTENSIONS_MARKDOWN_QUIZ), spans)


class PropositionsMarkdownTests(SimpleTestCase):
    def test_chaque_proposition_porte_sa_lettre_en_majuscule_dans_lordre_enregistre(self):
        md = propositions_markdown(CHOIX)

        positions = [md.index(f"**{lettre}.** ") for lettre in "ABCD"]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("**D.** Un système d'exploitation", md)

    def test_une_question_ouverte_ne_produit_rien(self):
        self.assertEqual(propositions_markdown([]), "")
        self.assertEqual(propositions_markdown(None), "")

    def test_une_proposition_vide_ou_mal_formee_est_ignoree(self):
        md = propositions_markdown([{"lettre": "a", "texte": "  "}, "b", {"lettre": "c", "texte": "Reste"}])

        self.assertNotIn("**A.**", md)
        self.assertIn("**C.** Reste", md)

    def test_un_saut_de_ligne_ne_sort_pas_le_texte_de_sa_proposition(self):
        md = propositions_markdown([{"lettre": "a", "texte": "Première ligne\nseconde ligne"}])

        self.assertIn("**A.** Première ligne seconde ligne", md)

    def test_chaque_proposition_ouvre_sur_une_case_vide(self):
        md = propositions_markdown(CHOIX)

        self.assertEqual(md.count("<span class='case'></span>**"), 4)
        self.assertNotIn("cochee", md)

    def test_seule_la_case_de_la_lettre_demandee_sort_cochee(self):
        md = propositions_markdown(CHOIX, cochee="d")

        self.assertEqual(md.count("cochee"), 1)
        self.assertIn("<span class='case cochee'></span>**D.**", md)
        self.assertEqual(md.count("<span class='case'></span>**"), 3)

    def test_une_cle_qui_ne_designe_aucune_proposition_ne_coche_rien(self):
        self.assertNotIn("cochee", propositions_markdown(CHOIX, cochee="e"))
        self.assertNotIn("cochee", propositions_markdown(CHOIX, cochee=""))


class PropositionsHtmlTests(SimpleTestCase):
    def test_le_bloc_garde_sa_classe_et_rend_une_liste(self):
        html = _html("Quel logiciel installer en premier ?\n\n" + propositions_markdown(CHOIX))

        # _italicize_quotes ne doit pas avoir mis la classe en italique (class=*"propositions"*).
        self.assertRegex(html, r"""<div class=["']propositions["']>""")
        self.assertNotIn("markdown=", html)
        self.assertEqual(html.count("<li>"), 4)
        self.assertIn("<strong>D.</strong> Un système d'exploitation", html)

    def test_les_cases_arrivent_dans_le_html_juste_avant_la_lettre(self):
        # Le gabarit vise « .case + strong » : la case doit rester un élément, collé à la lettre.
        html = _html(propositions_markdown(CHOIX, cochee="d"))

        self.assertEqual(len(re.findall(r"""<li><span class=["']case["']></span><strong>[ABC]\.</strong>""", html)), 3)
        self.assertRegex(html, r"""<li><span class=["']case cochee["']></span><strong>D\.</strong>""")

    def test_le_markdown_et_les_formules_dune_proposition_sont_rendus(self):
        html = _html(propositions_markdown([
            {"lettre": "a", "texte": "$-3<k<3$"},
            {"lettre": "b", "texte": "`<?php` au début et `?>` à la fin"},
            {"lettre": "c", "texte": "Le mot « base » veut dire **simple**"},
        ]))

        self.assertIn("$-3&lt;k&lt;3$", html)  # la formule arrive intacte à KaTeX, jamais comme une balise
        self.assertIn("<code>&lt;?php</code>", html)
        self.assertIn("<strong>simple</strong>", html)
        self.assertEqual(html.count("<li>"), 3)

    def test_un_enonce_sans_proposition_est_rendu_comme_avant(self):
        md = "Calculer $f'(x)$.\n\n| a | b |\n|---|---|\n| 1 | 2 |"
        protege, spans = _protect_math(md)
        avant = _restore_math(
            markdown.markdown(_italicize_quotes(protege), extensions=["tables", "fenced_code", "nl2br"]), spans,
        )

        self.assertEqual(_html(md), avant)


class BonneReponseMarkdownTests(SimpleTestCase):
    def test_nomme_la_lettre_dans_la_langue_du_pdf(self):
        self.assertEqual(bonne_reponse_markdown(CHOIX, "d", textes_pdf("fr")), "**Bonne réponse : D**")
        self.assertEqual(bonne_reponse_markdown(CHOIX, "d", textes_pdf("en")), "**Correct answer: D**")

    def test_ne_dit_rien_quand_la_cle_ne_designe_aucune_proposition(self):
        tx = textes_pdf("fr")

        self.assertEqual(bonne_reponse_markdown(CHOIX, "", tx), "")
        self.assertEqual(bonne_reponse_markdown(CHOIX, "e", tx), "")
        self.assertEqual(bonne_reponse_markdown([], "a", tx), "")
