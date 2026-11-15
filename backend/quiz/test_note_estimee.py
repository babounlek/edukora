from datetime import timedelta
from unittest import mock

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from subscriptions.models import Subscription

from . import note_estimee as ne
from .test_priorites import _Base


def _groupes(*specs):
    """Ce que renvoie groupes_par_frequence : (mince, lessons, nb_sessions, {nom: groupe}, tous_tag_ids)."""
    groupes = {nom: {"nom": nom, "tag_ids": {tag}, "nb_epreuves": nb} for nom, tag, nb in specs}
    return False, None, 10, groupes, {tag for _, tag, _ in specs}


class FourchetteTests(_Base):
    def _calculer(self, groupes, maitrise, blancs=()):
        if not getattr(self, "_maths", None):
            self._maths = self._matiere("maths", 5)
        with mock.patch.object(ne, "groupes_par_frequence", return_value=groupes), \
             mock.patch.object(ne, "maitrise_par_theme", return_value=maitrise), \
             mock.patch.object(ne, "_notes_des_examens_blancs", return_value=list(blancs)):
            return ne.note_estimee(self.profil, self.cursus)

    def test_une_fourchette_jamais_un_chiffre_exact(self):
        r = self._calculer(
            _groupes(("A", 1, 6), ("B", 2, 4)),
            [{"theme_id": 1, "reussies": 18, "total": 20}, {"theme_id": 2, "reussies": 10, "total": 20}],
        )
        m = r["matieres"][0]
        self.assertEqual(m["statut"], "estimee")
        self.assertGreaterEqual(m["haut"] - m["bas"], ne.LARGEUR_MIN_POINTS)
        self.assertNotIn("centre", m)  # le milieu ne sort pas
        self.assertTrue(0 <= m["bas"] < m["haut"] <= 20)

    def test_pas_assez_de_reponses_on_dit_combien_il_manque(self):
        r = self._calculer(_groupes(("A", 1, 6), ("B", 2, 4)), [{"theme_id": 1, "reussies": 3, "total": 5}])
        m = r["matieres"][0]
        self.assertEqual(m["statut"], "pas_assez")
        self.assertEqual((m["reponses"], m["reponses_min"]), (5, ne.REPONSES_MIN_MATIERE))
        self.assertIsNone(r["moyenne"])

    def test_pas_assez_de_couverture_meme_avec_beaucoup_de_reponses(self):
        # 40 réponses, mais sur un thème qui ne pèse que 10 % de la matière.
        r = self._calculer(_groupes(("A", 1, 1), ("B", 2, 9)), [{"theme_id": 1, "reussies": 30, "total": 40}])
        self.assertEqual(r["matieres"][0]["statut"], "pas_assez")

    def test_matiere_sans_theme_mesure(self):
        r = self._calculer(None, [])
        self.assertEqual(r["matieres"][0]["statut"], "sans_donnees")

    def test_un_eleve_fort_est_au_dessus_d_un_eleve_faible(self):
        groupes = _groupes(("A", 1, 5), ("B", 2, 5))
        fort = self._calculer(
            groupes, [{"theme_id": 1, "reussies": 19, "total": 20}, {"theme_id": 2, "reussies": 19, "total": 20}],
        )["matieres"][0]
        faible = self._calculer(
            groupes, [{"theme_id": 1, "reussies": 4, "total": 20}, {"theme_id": 2, "reussies": 4, "total": 20}],
        )["matieres"][0]
        self.assertGreater(fort["bas"], faible["haut"])

    def test_les_examens_blancs_recalent_et_elargissent(self):
        groupes = _groupes(("A", 1, 5), ("B", 2, 5))
        maitrise = [{"theme_id": 1, "reussies": 19, "total": 20}, {"theme_id": 2, "reussies": 19, "total": 20}]
        seul = self._calculer(groupes, maitrise)["matieres"][0]
        recale = self._calculer(groupes, maitrise, blancs=[6.0, 8.0])["matieres"][0]
        self.assertFalse(seul["calibre"])
        self.assertTrue(recale["calibre"])
        self.assertLess(recale["bas"], seul["bas"])  # un examen blanc à 7/20 ramène une maîtrise de quiz trop flatteuse
        self.assertGreater(recale["haut"] - recale["bas"], seul["haut"] - seul["bas"])
        # un seul examen blanc ne recale pas : trop peu pour contredire le quiz
        self.assertFalse(self._calculer(groupes, maitrise, blancs=[6.0])["matieres"][0]["calibre"])

    def test_peu_de_themes_tentes_donne_une_fourchette_plus_large(self):
        # Même taux de réussite, mais 20 % ou 100 % de la matière couverte : l'ignorance sur le reste élargit la fourchette.
        peu = self._calculer(
            _groupes(("A", 1, 2), ("B", 2, 4), ("C", 3, 4)), [{"theme_id": 1, "reussies": 24, "total": 30}],
        )["matieres"][0]
        tout = self._calculer(
            _groupes(("A", 1, 2), ("B", 2, 4), ("C", 3, 4)),
            [{"theme_id": 1, "reussies": 8, "total": 10}, {"theme_id": 2, "reussies": 8, "total": 10}, {"theme_id": 3, "reussies": 8, "total": 10}],
        )["matieres"][0]
        self.assertGreater(peu["haut"] - peu["bas"], tout["haut"] - tout["bas"])

    def test_les_themes_qui_rapportent_le_plus_de_points(self):
        groupes = _groupes(("Lourd et faible", 1, 8), ("Léger et faible", 2, 1), ("Lourd et maîtrisé", 3, 8))
        maitrise = [
            {"theme_id": 1, "reussies": 2, "total": 10}, {"theme_id": 2, "reussies": 2, "total": 10},
            {"theme_id": 3, "reussies": 10, "total": 10},
        ]
        m = self._calculer(groupes, maitrise)["matieres"][0]
        self.assertEqual(m["themes_rentables"][0]["theme"], "Lourd et faible")
        self.assertLessEqual(len(m["themes_rentables"]), ne.THEMES_RENTABLES)

    def test_la_moyenne_pese_les_coefficients(self):
        fort, _ = self._matiere("fort", 7)
        faible, _ = self._matiere("faible", 1)
        sorties = {fort.id: {"statut": "estimee", "bas": 16, "haut": 18}, faible.id: {"statut": "estimee", "bas": 4, "haut": 6}}

        def fausse(profil, cursus, subject, maitrise):
            base = {"subject_id": subject.id, "subject_label": subject.label, "subject_code": subject.code}
            return {**base, **sorties.get(subject.id, {"statut": "sans_donnees"})}

        with mock.patch.object(ne, "_matiere", side_effect=fausse), mock.patch.object(ne, "maitrise_par_theme", return_value=[]):
            moyenne = ne.note_estimee(self.profil, self.cursus)["moyenne"]
        self.assertEqual(moyenne["matieres"], 2)
        self.assertGreater(moyenne["bas"], 13)  # (7×16 + 1×4) / 8 = 14,5 : le coefficient 7 domine


class FourchetteToujoursValideTests(_Base):
    def test_fourchette_toujours_assez_large_et_dans_0_20(self):
        for centre, ecart in ((10, 0), (0.2, 0.1), (19.8, 0.1), (20, 0), (0, 0)):
            bas, haut = ne._fourchette(centre, ecart)
            self.assertTrue(0 <= bas < haut <= 20, (centre, ecart, bas, haut))
            self.assertGreaterEqual(haut - bas, ne.LARGEUR_MIN_POINTS)


class NoteEstimeeAPITests(_Base):
    def setUp(self):
        super().setUp()
        self._matiere("maths", 5)
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=5),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @override_settings(NOTE_ESTIMEE_ACTIVE=False)
    def test_invisible_pour_un_eleve_tant_que_non_validee(self):
        self.assertEqual(self.client.get("/quiz/note-estimee/").json(), {"actif": False})

    @override_settings(NOTE_ESTIMEE_ACTIVE=False)
    def test_visible_du_personnel_pour_la_relecture(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        r = self.client.get("/quiz/note-estimee/").json()
        self.assertTrue(r["actif"])
        self.assertTrue(r["relecture"])

    @override_settings(NOTE_ESTIMEE_ACTIVE=True)
    def test_visible_de_l_eleve_une_fois_validee(self):
        r = self.client.get("/quiz/note-estimee/").json()
        self.assertTrue(r["actif"])
        self.assertFalse(r["relecture"])
        self.assertIn("matieres", r)

    @override_settings(NOTE_ESTIMEE_ACTIVE=True)
    def test_sans_abonnement_rien(self):
        Subscription.objects.all().delete()
        self.assertEqual(self.client.get("/quiz/note-estimee/").json(), {"actif": False})

    def test_exige_une_connexion(self):
        self.assertIn(APIClient().get("/quiz/note-estimee/").status_code, (401, 403))
