from django.http import FileResponse, HttpResponse, JsonResponse
from django.test import RequestFactory, SimpleTestCase

from .etag import EtagJsonMiddleware


def _passer(reponse):
    return EtagJsonMiddleware(lambda request: reponse)


class EtagJsonMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.fabrique = RequestFactory()

    def _json(self, corps=None):
        return JsonResponse(corps or {"a": 1})

    def test_pose_etag_et_cache_control_prive_sur_un_get_json(self):
        reponse = _passer(self._json())(self.fabrique.get("/x/"))
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse["ETag"])
        self.assertEqual(sorted(p.strip() for p in reponse["Cache-Control"].split(",")), ["no-cache", "private"])

    def test_304_sans_corps_quand_l_etag_correspond(self):
        etag = _passer(self._json())(self.fabrique.get("/x/"))["ETag"]
        reponse = _passer(self._json())(self.fabrique.get("/x/", HTTP_IF_NONE_MATCH=etag))
        self.assertEqual(reponse.status_code, 304)
        self.assertEqual(reponse.content, b"")
        self.assertEqual(reponse["ETag"], etag)

    def test_200_complet_quand_le_corps_a_change(self):
        etag = _passer(self._json({"a": 1}))(self.fabrique.get("/x/"))["ETag"]
        reponse = _passer(self._json({"a": 2}))(self.fabrique.get("/x/", HTTP_IF_NONE_MATCH=etag))
        self.assertEqual(reponse.status_code, 200)
        self.assertNotEqual(reponse["ETag"], etag)

    def test_deux_corps_differents_ont_deux_etags(self):
        """Garantie entre comptes : la même URL servie avec des données différentes (has_access, is_read...)
        ne peut jamais produire un 304 qui ferait réafficher à un compte le corps d'un autre."""
        a = _passer(self._json({"has_access": True}))(self.fabrique.get("/x/"))["ETag"]
        b = _passer(self._json({"has_access": False}))(self.fabrique.get("/x/"))["ETag"]
        self.assertNotEqual(a, b)

    def test_ne_touche_pas_au_cache_control_d_une_vue(self):
        reponse = self._json()
        reponse["Cache-Control"] = "public, max-age=300"
        reponse = _passer(reponse)(self.fabrique.get("/x/"))
        self.assertEqual(reponse["Cache-Control"], "public, max-age=300")

    def test_laisse_passer_no_store(self):
        reponse = self._json()
        reponse["Cache-Control"] = "private, no-store"
        reponse = _passer(reponse)(self.fabrique.get("/x/"))
        self.assertFalse(reponse.has_header("ETag"))

    def test_ignore_les_post_les_erreurs_les_fichiers_et_le_html(self):
        self.assertFalse(_passer(self._json())(self.fabrique.post("/x/")).has_header("ETag"))
        self.assertFalse(_passer(JsonResponse({"e": 1}, status=404))(self.fabrique.get("/x/")).has_header("ETag"))
        self.assertFalse(_passer(HttpResponse("<p>x</p>"))(self.fabrique.get("/x/")).has_header("ETag"))
        pdf = FileResponse(iter([b"%PDF"]), content_type="application/pdf")
        self.assertFalse(_passer(pdf)(self.fabrique.get("/x/")).has_header("ETag"))
        flux = HttpResponse(content_type="application/json")
        flux.streaming = True
        flux._iterator = iter([b"{}"])  # pragma: no cover - réponse non bufferisable
        self.assertFalse(_passer(flux)(self.fabrique.get("/x/")).has_header("ETag"))
