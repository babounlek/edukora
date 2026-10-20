"""Les formules LaTeX remises dans le HTML d'un PDF de sujet sont echappees : « $-3<k<3$ » ne doit jamais devenir une balise HTML."""
import markdown
from django.test import SimpleTestCase

from .sujet_pdf import _protect_math, _restore_math


class RestoreMathEchappeTests(SimpleTestCase):
    def _html(self, md):
        protege, spans = _protect_math(md)
        return _restore_math(markdown.markdown(protege, extensions=["tables", "nl2br"]), spans)

    def test_inequality_with_a_letter_after_the_sign_is_not_an_html_tag(self):
        html = self._html("a) $k<6$\nb) $-3<k<3$\nc) $-6<k<6$\nd) $k<-6$ or $k>6$")
        self.assertNotIn("<k", html)
        self.assertEqual(html.count("&lt;"), 6)
        self.assertEqual(html.count("c) "), 1)  # les options suivantes ne sont pas avalees

    def test_ampersand_of_a_matrix_is_escaped_and_plain_text_is_untouched(self):
        html = self._html("Soit $\begin{pmatrix}1&2\\3&4\end{pmatrix}$ et $$a\leq b$$ avec 3 < 4.")
        self.assertIn("1&amp;2", html)
        self.assertIn("a\leq b", html)
        self.assertIn("3 &lt; 4", html)
