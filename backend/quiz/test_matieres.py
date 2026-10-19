from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Cursus, Difficulte, Examen, Lesson, LessonType, Origine, StatutContenu, Subject, Tag
from subscriptions.models import Subscription
from users.models import User

from .matieres import (
    avertissements_inscription, matieres_disponibles, matieres_officielles, regles_inscription,
    restreindre_items, restreindre_matieres, sujets_a_afficher,
)
from .models import ModeQuiz
from .priorites import priorites_examen
from .services import (
    _subjects_par_priorite, generer_session, matieres_pour_objectif, resume_parcours,
)
from .tests import _make_competence_item


class _Base(TestCase):
    """Un élève du GCE A Level (pas de séries) devant plusieurs matières."""

    def setUp(self):
        self.cursus = Cursus.objects.get(examen=Examen.GCE_AL, series__isnull=True)
        self.user = User.objects.create_user(phone_number="677400101", password="x")
        self.profil = self.user.profils.first()
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.compteur = 0
        self.maths = self._matiere("GCE_MATHS")
        self.physique = self._matiere("GCE_PHYSICS")
        self.histoire = self._matiere("GCE_HISTORY")

    def _matiere(self, code, nb_items=4):
        subject = Subject.objects.get(country=self.cursus.country, code=code)
        lesson = Lesson.objects.create(
            title=f"Paper {code}", subject=subject, year=2025, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(self.cursus)
        for _ in range(nb_items):
            self.compteur += 1
            _make_competence_item(
                subject, self.cursus, theme=Tag.objects.create(name=f"theme-{code}-{self.compteur}"),
                difficulte=Difficulte.MOYENNE, numero=str(self.compteur),
            )
        return subject

    def _choisir(self, *subjects):
        self.profil.matieres_passees.set(subjects)


class RestreindreTests(_Base):
    def test_sans_choix_tout_le_cursus(self):
        sujets = [self.maths, self.physique, self.histoire]
        self.assertEqual(restreindre_matieres(self.profil, sujets), sujets)
        self.assertEqual(restreindre_matieres(None, sujets), sujets)

    def test_un_choix_limite_aux_matieres_declarees_en_gardant_l_ordre(self):
        self._choisir(self.maths, self.histoire)
        resultat = restreindre_matieres(self.profil, [self.histoire, self.physique, self.maths])
        self.assertEqual(resultat, [self.histoire, self.maths])

    def test_un_choix_qui_ne_recoupe_rien_est_ignore(self):
        autre = Subject.objects.get(country=self.cursus.country, code="GCE_BIOLOGY")
        self._choisir(autre)
        sujets = [self.maths, self.physique]
        self.assertEqual(restreindre_matieres(self.profil, sujets), sujets)

    def test_items_du_diagnostic(self):
        class Item:
            def __init__(self, subject_id):
                self.subject_id = subject_id

        items = [Item(self.maths.id), Item(self.physique.id), Item(self.histoire.id)]
        self._choisir(self.physique)
        self.assertEqual([i.subject_id for i in restreindre_items(self.profil, items)], [self.physique.id])

    def test_matieres_disponibles_seulement_avec_du_contenu(self):
        codes = {m.code for m in matieres_disponibles(self.cursus)}
        self.assertEqual(codes, {"GCE_MATHS", "GCE_PHYSICS", "GCE_HISTORY"})


class VoirSeulementMesMatieresTests(_Base):
    """L'interrupteur d'affichage (Profil.voir_seulement_mes_matieres), distinct de l'inscription."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cursus_id = self.cursus.id

    def _eteindre(self):
        self.profil.voir_seulement_mes_matieres = False
        self.profil.save(update_fields=["voir_seulement_mes_matieres"])

    def test_actif_par_defaut(self):
        self.assertTrue(self.profil.voir_seulement_mes_matieres)
        self.assertTrue(self.client.get("/quiz/matieres/").data["seulement_mes_matieres"])

    def test_eteint_le_coach_revoit_tout_le_cursus_sans_toucher_a_l_inscription(self):
        self._choisir(self.maths)
        sujets = [self.maths, self.physique, self.histoire]
        self.assertEqual(restreindre_matieres(self.profil, sujets), [self.maths])
        self._eteindre()
        self.assertEqual(restreindre_matieres(self.profil, sujets), sujets)
        self.assertEqual(set(self.profil.matieres_passees.values_list("id", flat=True)), {self.maths.id})

    def test_put_de_l_interrupteur_seul_ne_modifie_pas_les_matieres(self):
        self._choisir(self.maths, self.physique)
        reponse = self.client.put("/quiz/matieres/", {"seulement_mes_matieres": False}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(reponse.data["seulement_mes_matieres"])
        self.assertEqual(reponse.data["choisies"], sorted([self.maths.id, self.physique.id]))
        self.profil.refresh_from_db()
        self.assertFalse(self.profil.voir_seulement_mes_matieres)

    def test_put_des_matieres_seules_ne_touche_pas_l_interrupteur(self):
        self._eteindre()
        self.client.put("/quiz/matieres/", {"matieres": [self.maths.id]}, format="json")
        self.profil.refresh_from_db()
        self.assertFalse(self.profil.voir_seulement_mes_matieres)

    def test_put_refuse_un_interrupteur_non_booleen(self):
        for valeur in ("non", 0, None):
            reponse = self.client.put("/quiz/matieres/", {"seulement_mes_matieres": valeur}, format="json")
            self.assertEqual(reponse.status_code, 400, valeur)

    def test_sujets_a_afficher(self):
        self.assertIsNone(sujets_a_afficher(self.profil, self.cursus_id))  # rien de choisi
        self._choisir(self.maths, self.histoire)
        self.assertEqual(sujets_a_afficher(self.profil, self.cursus_id), {self.maths.id, self.histoire.id})
        self.assertIsNone(sujets_a_afficher(self.profil, None))
        self.assertIsNone(sujets_a_afficher(self.profil, "abc"))
        self.assertIsNone(sujets_a_afficher(None, self.cursus_id))
        autre = Cursus.objects.get(examen=Examen.GCE_OL, series__isnull=True)
        self.assertIsNone(sujets_a_afficher(self.profil, autre.id))  # pas l'examen préparé
        self._eteindre()
        self.assertIsNone(sujets_a_afficher(self.profil, self.cursus_id))

    def test_un_choix_sans_contenu_sur_l_examen_ne_vide_pas_les_listes(self):
        self._choisir(Subject.objects.get(country=self.cursus.country, code="GCE_BIOLOGY"))
        self.assertIsNone(sujets_a_afficher(self.profil, self.cursus_id))

    def test_pastilles_de_matiere_du_catalogue(self):
        self._choisir(self.maths)
        codes = lambda: {s["code"] for s in self.client.get("/catalog/subjects/", {"cursus": self.cursus_id}).json()}
        self.assertEqual(codes(), {"GCE_MATHS"})
        self._eteindre()
        self.assertEqual(codes(), {"GCE_MATHS", "GCE_PHYSICS", "GCE_HISTORY"})

    def test_liste_des_epreuves(self):
        self._choisir(self.maths)
        titres = lambda **p: {
            e["title"] for e in self.client.get("/catalog/lessons/", {"cursus": self.cursus_id, **p}).json()["results"]
        }
        self.assertEqual(titres(), {"Paper GCE_MATHS"})
        # Une matière demandée explicitement n'est jamais masquée.
        self.assertEqual(titres(subject="GCE_PHYSICS"), {"Paper GCE_PHYSICS"})
        self._eteindre()
        self.assertEqual(titres(), {"Paper GCE_MATHS", "Paper GCE_PHYSICS", "Paper GCE_HISTORY"})

    def test_get_dit_si_les_listes_sont_reellement_reduites(self):
        reponse = self.client.get("/quiz/matieres/").data
        self.assertEqual((reponse["affichage_restreint"], reponse["nb_affichees"]), (False, 0))  # rien de choisi
        self._choisir(self.maths, self.histoire)
        reponse = self.client.get("/quiz/matieres/").data
        self.assertEqual((reponse["affichage_restreint"], reponse["nb_affichees"]), (True, 2))
        self._eteindre()
        reponse = self.client.get("/quiz/matieres/").data
        self.assertEqual((reponse["affichage_restreint"], reponse["nb_affichees"]), (False, 0))
        self.assertEqual(len(reponse["choisies"]), 2)  # l'inscription est intacte

    def test_visiteur_anonyme_voit_tout(self):
        self._choisir(self.maths)
        reponse = APIClient().get("/catalog/subjects/", {"cursus": self.cursus_id})
        self.assertEqual({s["code"] for s in reponse.json()}, {"GCE_MATHS", "GCE_PHYSICS", "GCE_HISTORY"})

    def test_matieres_du_quiz(self):
        self._choisir(self.maths)
        codes = lambda: {s["code"] for s in self.client.get("/quiz/subjects/", {"cursus": self.cursus_id}).json()}
        self.assertEqual(codes(), {"GCE_MATHS"})
        self._eteindre()
        self.assertEqual(codes(), {"GCE_MATHS", "GCE_PHYSICS", "GCE_HISTORY"})


class CoachRespecteLesMatieresTests(_Base):
    def test_plan_du_jour_ne_retient_que_les_matieres_choisies(self):
        self.assertEqual({s.id for s in _subjects_par_priorite(self.profil, self.cursus)},
                         {self.maths.id, self.physique.id, self.histoire.id})
        self._choisir(self.maths, self.physique)
        self.assertEqual({s.id for s in _subjects_par_priorite(self.profil, self.cursus)},
                         {self.maths.id, self.physique.id})

    def test_objectif_de_la_semaine_propose_les_matieres_choisies(self):
        self._choisir(self.histoire)
        self.assertEqual([m.id for m in matieres_pour_objectif(self.cursus, self.profil)], [self.histoire.id])
        # Sans profil, toutes celles qui ont une banque de quiz.
        self.assertEqual(len(matieres_pour_objectif(self.cursus)), 3)

    def test_priorites_de_l_examen(self):
        self._choisir(self.maths)
        lignes = priorites_examen(self.profil, self.cursus)["matieres"]
        self.assertEqual([ligne["subject_id"] for ligne in lignes], [self.maths.id])
        self._choisir()
        self.assertEqual(len(priorites_examen(self.profil, self.cursus)["matieres"]), 3)

    def test_progression_par_matiere(self):
        self._choisir(self.physique)
        # Sans programme officiel, ces matières n'ont pas de ligne de progression : on vérifie
        # seulement que le résumé ne montre jamais une matière que l'élève n'a pas choisie.
        ids = {ligne["subject_id"] for ligne in resume_parcours(self.profil, self.cursus)}
        self.assertTrue(ids <= {self.physique.id})

    def test_diagnostic_n_interroge_que_les_matieres_choisies(self):
        self._choisir(self.maths, self.physique)
        session = generer_session(self.profil, self.cursus, ModeQuiz.DIAGNOSTIC, n=6)
        sujets = {qq.competence_item.subject_id for qq in session.quiz_questions.all()}
        self.assertEqual(sujets, {self.maths.id, self.physique.id})

    def test_un_eleve_du_bac_sans_choix_ne_change_pas(self):
        bac = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        sujet = Subject.objects.create(code="plain", label="Plain", country=bac.country)
        lesson = Lesson.objects.create(
            title="Épreuve plain", subject=sujet, year=2024, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(bac)
        self.assertEqual([s.id for s in _subjects_par_priorite(self.profil, bac)], [sujet.id])


class MatieresApiTests(_Base):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_liste_les_matieres_disponibles(self):
        reponse = self.client.get("/quiz/matieres/")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["choisies"], [])
        self.assertEqual({m["code"] for m in reponse.data["disponibles"]}, {"GCE_MATHS", "GCE_PHYSICS", "GCE_HISTORY"})

    def test_put_enregistre_le_choix(self):
        reponse = self.client.put("/quiz/matieres/", {"matieres": [self.maths.id, self.physique.id]}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["choisies"], sorted([self.maths.id, self.physique.id]))
        self.assertEqual(set(self.profil.matieres_passees.values_list("id", flat=True)), {self.maths.id, self.physique.id})

    def test_put_vide_revient_a_toutes_les_matieres(self):
        self._choisir(self.maths)
        reponse = self.client.put("/quiz/matieres/", {"matieres": []}, format="json")
        self.assertEqual(reponse.data["choisies"], [])
        self.assertFalse(self.profil.matieres_passees.exists())

    def test_put_refuse_une_matiere_que_le_board_ne_propose_pas_a_ce_niveau_et_sans_contenu(self):
        # Commerce n'existe qu'au O Level, et n'a aucun contenu sur le cursus A Level.
        commerce = Subject.objects.get(country=self.cursus.country, code="GCE_COMMERCE")
        reponse = self.client.put("/quiz/matieres/", {"matieres": [commerce.id]}, format="json")
        self.assertEqual(reponse.status_code, 400)
        self.assertFalse(self.profil.matieres_passees.exists())

    def test_put_accepte_une_matiere_du_board_meme_sans_contenu(self):
        # Biology est une matière officielle de l'A Level : on peut la déclarer avant qu'EduKora la couvre.
        biologie = Subject.objects.get(country=self.cursus.country, code="GCE_BIOLOGY")
        reponse = self.client.put("/quiz/matieres/", {"matieres": [biologie.id]}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["choisies"], [biologie.id])
        ligne = next(m for m in reponse.data["officielles"] if m["code"] == "GCE_BIOLOGY")
        self.assertFalse(ligne["couverte"])
        self.assertEqual(ligne["code_officiel"], "0710")

    def test_put_refuse_une_charge_invalide(self):
        for charge in ({"matieres": "maths"}, {"matieres": [True]}, {}):
            self.assertEqual(self.client.put("/quiz/matieres/", charge, format="json").status_code, 400)

    def test_le_choix_d_un_autre_examen_est_preserve(self):
        bac = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        autre = Subject.objects.create(code="ancien", label="Ancien", country=bac.country)
        self.profil.matieres_passees.add(autre)
        self.client.put("/quiz/matieres/", {"matieres": [self.maths.id]}, format="json")
        self.assertEqual(
            set(self.profil.matieres_passees.values_list("id", flat=True)), {autre.id, self.maths.id},
        )

    def test_sans_cursus_declare(self):
        self.user.cursus_prepare = None
        self.user.save(update_fields=["cursus_prepare"])
        self.assertEqual(self.client.get("/quiz/matieres/").status_code, 400)

    def test_anonyme_refuse(self):
        self.assertIn(APIClient().get("/quiz/matieres/").status_code, (401, 403))


OL_COMPLET = ("GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS", "GCE_PHYSICS", "GCE_CHEMISTRY", "GCE_BIOLOGY")


class ReglesInscriptionTests(TestCase):
    """Règles d'inscription du GCE Board (quiz.matieres.REGLES_INSCRIPTION_GCE) : elles préviennent, jamais ne bloquent."""

    def setUp(self):
        self.ol = Cursus.objects.get(examen=Examen.GCE_OL, series__isnull=True)
        self.al = Cursus.objects.get(examen=Examen.GCE_AL, series__isnull=True)

    def _sujets(self, *codes):
        return [Subject.objects.get(country=self.ol.country, code=c) for c in codes]

    def _codes(self, avertissements):
        return [(a["code"], a.get("matiere")) for a in avertissements]

    def test_regles_par_niveau(self):
        ol, al = regles_inscription(self.ol), regles_inscription(self.al)
        self.assertEqual((ol["minimum"], ol["maximum"]), (6, 11))
        self.assertEqual(set(ol["obligatoires"]), {"GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS"})
        self.assertEqual(ol["derniere"], "GCE_RELIGION")
        self.assertEqual((al["minimum"], al["maximum"], al["obligatoires"]), (None, 5, ()))

    def test_pas_de_regles_hors_branche_generale_du_gce(self):
        technique = Cursus.objects.get(examen=Examen.GCE_OL, series__code="GCE_TECHNICAL")
        bac = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        for cursus in (technique, bac, None):
            self.assertIsNone(regles_inscription(cursus))
            self.assertEqual(matieres_officielles(cursus), [])
            self.assertEqual(avertissements_inscription(cursus, self._sujets("GCE_MATHS")), [])

    def test_matieres_officielles_selon_le_niveau(self):
        ol = {m.code for m in matieres_officielles(self.ol)}
        al = {m.code for m in matieres_officielles(self.al)}
        self.assertEqual((len(ol), len(al)), (21, 20))
        self.assertIn("GCE_MATHS", ol)
        self.assertNotIn("GCE_PM_MECHANICS", ol)
        self.assertIn("GCE_PM_MECHANICS", al)
        self.assertNotIn("GCE_MATHS", al)
        self.assertNotIn("GCE_TECH_DRAWING", ol | al)  # aucune des deux listes du Board

    def test_un_choix_vide_ne_donne_aucun_avertissement(self):
        self.assertEqual(avertissements_inscription(self.ol, []), [])

    def test_trop_peu_de_matieres_et_obligatoires_manquantes(self):
        resultat = avertissements_inscription(self.ol, self._sujets("GCE_PHYSICS", "GCE_CHEMISTRY", "GCE_BIOLOGY"))
        self.assertIn(("minimum", None), self._codes(resultat))
        self.assertEqual(
            {a["matiere"] for a in resultat if a["code"] == "obligatoire"}, {"GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS"},
        )
        minimum = next(a for a in resultat if a["code"] == "minimum")
        self.assertEqual((minimum["attendu"], minimum["actuel"]), (6, 3))

    def test_une_inscription_complete_sans_avertissement(self):
        self.assertEqual(avertissements_inscription(self.ol, self._sujets(*OL_COMPLET)), [])

    def test_onzieme_matiere_doit_etre_religious_studies(self):
        onze = OL_COMPLET + ("GCE_GEOGRAPHY", "GCE_HISTORY", "GCE_ECONOMICS", "GCE_LITERATURE", "GCE_COMMERCE")
        sans = avertissements_inscription(self.ol, self._sujets(*onze))
        self.assertEqual(self._codes(sans), [("derniere_matiere", "GCE_RELIGION")])
        avec = avertissements_inscription(self.ol, self._sujets(*onze[:-1], "GCE_RELIGION"))
        self.assertEqual(avec, [])

    def test_plus_de_onze_matieres(self):
        douze = OL_COMPLET + ("GCE_GEOGRAPHY", "GCE_HISTORY", "GCE_ECONOMICS", "GCE_LITERATURE", "GCE_COMMERCE", "GCE_RELIGION")
        resultat = avertissements_inscription(self.ol, self._sujets(*douze))
        self.assertEqual([a["code"] for a in resultat], ["maximum"])
        self.assertEqual((resultat[0]["attendu"], resultat[0]["actuel"]), (11, 12))

    def test_a_level_cinq_matieres_au_plus_et_aucune_obligatoire(self):
        def al(*codes):
            return [Subject.objects.get(country=self.al.country, code=c) for c in codes]

        ok = avertissements_inscription(self.al, al("GCE_PM_MECHANICS", "GCE_PHYSICS", "GCE_CHEMISTRY"))
        self.assertEqual(ok, [])
        six = avertissements_inscription(
            self.al, al("GCE_PM_MECHANICS", "GCE_PHYSICS", "GCE_CHEMISTRY", "GCE_BIOLOGY", "GCE_ECONOMICS", "GCE_HISTORY"),
        )
        self.assertEqual([a["code"] for a in six], ["maximum"])
        self.assertEqual((six[0]["attendu"], six[0]["actuel"]), (5, 6))


class InscriptionApiTests(TestCase):
    """GET/PUT /quiz/matieres/ au O Level : règles, matières du Board, avertissements."""

    def setUp(self):
        self.cursus = Cursus.objects.get(examen=Examen.GCE_OL, series__isnull=True)
        self.user = User.objects.create_user(phone_number="677400202", password="x")
        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        self.profil = self.user.profils.first()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _id(self, code):
        return Subject.objects.get(country=self.cursus.country, code=code).id

    def test_get_donne_les_regles_et_les_matieres_du_board(self):
        reponse = self.client.get("/quiz/matieres/")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual((reponse.data["regles"]["minimum"], reponse.data["regles"]["maximum"]), (6, 11))
        officielles = {m["code"]: m for m in reponse.data["officielles"]}
        self.assertEqual(len(officielles), 21)
        self.assertTrue(officielles["GCE_ENGLISH"]["obligatoire"])
        self.assertFalse(officielles["GCE_PHYSICS"]["obligatoire"])
        self.assertEqual(officielles["GCE_BIOLOGY"]["code_officiel"], "0510")
        self.assertEqual(reponse.data["avertissements"], [])

    def test_une_matiere_sans_contenu_est_marquee_non_couverte(self):
        officielles = {m["code"]: m for m in self.client.get("/quiz/matieres/").data["officielles"]}
        self.assertFalse(officielles["GCE_HUMAN_BIOLOGY"]["couverte"])

    def test_put_hors_regles_est_accepte_avec_avertissements(self):
        reponse = self.client.put("/quiz/matieres/", {"matieres": [self._id("GCE_PHYSICS")]}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["choisies"], [self._id("GCE_PHYSICS")])
        codes = {a["code"] for a in reponse.data["avertissements"]}
        self.assertEqual(codes, {"minimum", "obligatoire"})
        self.assertTrue(self.profil.matieres_passees.filter(code="GCE_PHYSICS").exists())

    def test_put_complet_sans_avertissement(self):
        ids = [self._id(c) for c in OL_COMPLET]
        reponse = self.client.put("/quiz/matieres/", {"matieres": ids}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["avertissements"], [])

    def test_get_relit_les_avertissements_du_choix_enregistre(self):
        self.client.put("/quiz/matieres/", {"matieres": [self._id("GCE_MATHS")]}, format="json")
        reponse = self.client.get("/quiz/matieres/")
        self.assertIn("minimum", {a["code"] for a in reponse.data["avertissements"]})

    def test_put_refuse_une_matiere_d_un_autre_niveau(self):
        reponse = self.client.put("/quiz/matieres/", {"matieres": [self._id("GCE_PM_MECHANICS")]}, format="json")
        self.assertEqual(reponse.status_code, 400)
        self.assertFalse(self.profil.matieres_passees.exists())

    def test_branche_technique_sans_regles(self):
        technique = Cursus.objects.get(examen=Examen.GCE_OL, series__code="GCE_TECHNICAL")
        self.user.cursus_prepare = technique
        self.user.save(update_fields=["cursus_prepare"])
        reponse = self.client.get("/quiz/matieres/")
        self.assertEqual(reponse.status_code, 200)
        self.assertIsNone(reponse.data["regles"])
        self.assertEqual(reponse.data["officielles"], [])
        self.assertEqual(reponse.data["avertissements"], [])
