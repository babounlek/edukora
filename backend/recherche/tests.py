"""
Couvre les trois risques de la recherche globale : qu'elle trouve (accents, pluriels, fautes de
frappe, filtre d'examen), qu'elle ne fuite rien de payant (corrigés, sections de cours réservées,
énoncé de quiz), et que son journal de recherches vides ne retienne aucune donnée personnelle.
"""

from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import (
    Cours, Country, Cursus, Examen, Exercise, Lesson, LessonType, RappelDeMethode, StatutContenu, Subject, Tag,
)
from inedit.models import Blueprint, EpreuveInedite
from programme.models import Module, Savoir
from quiz.models import CompetenceItem
from subscriptions.models import Subscription
from users.models import User

from . import moteur, texte
from .indexation import reconstruire
from .models import EntreeRecherche, RechercheSansResultat, TermeRecherche, TypeResultat

VALIDE = StatutContenu.VALIDE
# Mots-témoins : présents UNIQUEMENT dans un contenu payant - s'ils remontent, l'index fuit.
SECRET_CORRIGE = "corrigesecretalpha"
SECRET_SECTION = "sectionsecretbeta"


class TexteTests(SimpleTestCase):
    def test_normaliser_retire_accents_casse_ligatures_et_elisions(self):
        self.assertEqual(texte.normaliser("L'Équation d'une DROITE"), "equation une droite")
        self.assertEqual(texte.normaliser("cœur & sœur"), "coeur soeur")
        self.assertEqual(texte.normaliser("Thalès"), "thales")

    def test_nettoyer_retire_formules_liens_et_marqueurs(self):
        brut = "Soit $x^2+1$ et $$\\frac{a}{b}$$. Voir [le cours](COURS_REF:abc) [COURS_LINK:12] **gras**."
        self.assertEqual(texte.nettoyer(brut), "Soit et . Voir le cours gras .")

    def test_nettoyer_tronque_au_dernier_mot(self):
        self.assertEqual(texte.nettoyer("un deux trois quatre", limite=11), "un deux")

    def test_apercu_ajoute_des_points_de_suspension_si_coupe(self):
        self.assertTrue(texte.apercu("mot " * 100, longueur=30).endswith("…"))
        self.assertEqual(texte.apercu("court"), "court")

    def test_racine_singularise_sans_toucher_aux_mots_courts_ni_aux_exceptions(self):
        self.assertEqual(texte.racine("equations"), "equation")
        self.assertEqual(texte.racine("bus"), "bus")
        self.assertEqual(texte.racine("2019"), "2019")
        self.assertEqual(texte.racine("maths"), "maths")

    def test_jetons_ecartent_les_mots_vides_et_gardent_la_serie(self):
        self.assertEqual(texte.jetons("la limite d'une suite de d"), ["limite", "suite", "d"])
        self.assertEqual(texte.jetons("maths maths"), ["maths"])

    def test_est_requis_exclut_les_jetons_courts(self):
        self.assertTrue(texte.est_requis("suite"))
        self.assertTrue(texte.est_requis("2019"))
        self.assertFalse(texte.est_requis("d"))
        self.assertFalse(texte.est_requis("ti"))

    def test_distance_compte_une_transposition_pour_un(self):
        self.assertEqual(texte.distance("equatoin", "equation", 2), 1)
        self.assertEqual(texte.distance("thales", "thales", 2), 0)
        self.assertGreater(texte.distance("abcdef", "uvwxyz", 2), 2)

    def test_extrait_trouve_le_passage_sans_tenir_compte_des_accents(self):
        source = "Avant. " * 20 + "Le théorème de Thalès relie les longueurs. " + "Après. " * 20
        passage = texte.extrait(source, ["theoreme"], longueur=80)
        self.assertIn("théorème de Thalès", passage)
        self.assertTrue(passage.startswith("…") and passage.endswith("…"))

    def test_extrait_vide_si_aucun_jeton_present(self):
        self.assertEqual(texte.extrait("rien à voir ici", ["thales"]), "")

    def test_ancre_exercice_suit_la_regle_du_frontend(self):
        self.assertEqual(texte.ancre_exercice("3a"), "exercice-3a")
        self.assertEqual(texte.ancre_exercice("Problème IIA"), "exercice-probleme-iia")
        self.assertEqual(texte.ancre_exercice(""), "exercice-sans-numero")


class _CorpusMixin:
    """Un petit catalogue : une épreuve (BAC C) avec un exercice, un cours rattaché à cette épreuve,
    un cours « toutes séries », un thème portant un quiz, une épreuve inédite - et des contenus
    qui NE doivent PAS être indexés (brouillon, corrigé, section payante)."""

    @classmethod
    def setUpTestData(cls):
        cls.pays = Country.objects.get(code="CM")
        cls.maths = Subject.objects.get(country=cls.pays, code="MATHS")
        cls.bac_c = Cursus.objects.get(country=cls.pays, examen=Examen.BAC, series__code="C")
        cls.bepc = Cursus.objects.get(country=cls.pays, examen=Examen.BEPC, series__isnull=True)

        cls.thales = Tag.objects.create(name="théorème de Thalès")
        cls.limites = Tag.objects.create(name="limite d'une suite")

        cls.lesson = Lesson.objects.create(
            title="Mathématiques BAC C 2019", subject=cls.maths, lesson_type=LessonType.CORR, year=2019,
            statut=VALIDE, content_markdown=f"Énoncé et {SECRET_CORRIGE}",
        )
        cls.lesson.cursus.add(cls.bac_c)
        cls.lesson.themes.add(cls.thales)
        cls.exercice = Exercise.objects.create(
            lesson=cls.lesson, numero_exercice="1", statut=VALIDE,
            enonce_markdown="Soit un triangle ABC. Appliquer le théorème de Pythagore puis calculer l'aire.",
            corrige_markdown=f"Solution : {SECRET_CORRIGE}",
        )
        cls.exercice.themes.add(cls.thales)

        cls.cours_lie = Cours.objects.create(
            external_id="c1", titre="Le théorème de Thalès dans un triangle", subject=cls.maths, statut=VALIDE,
            sections_raw=[
                {"type": "accroche", "contenu_markdown": "Deux triangles emboîtés et des parallèles."},
                {"type": "exemple_resolu", "enonce_markdown": f"Exemple {SECRET_SECTION}", "etapes": []},
            ],
        )
        cls.cours_lie.tags.add(cls.thales)
        RappelDeMethode.objects.create(
            exercise=cls.exercice, external_id="rdm-1", competence="Thalès", contenu_markdown="x", cours=cls.cours_lie,
        )
        cls.cours_commun = Cours.objects.create(
            external_id="c2", titre="Calculer une aire", subject=cls.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Mesurer une surface."}],
        )
        cls.cours_bepc = Cours.objects.create(
            external_id="c3", titre="Les fractions au BEPC", subject=cls.maths, statut=VALIDE,
        )
        cls.cours_bepc.cursus.add(cls.bepc)
        Cours.objects.create(external_id="c4", titre="Brouillon sur Thalès", subject=cls.maths, statut=StatutContenu.BROUILLON)

        cls.item_1 = CompetenceItem.objects.create(
            theme=cls.limites, subject=cls.maths, statut=VALIDE,
            enonce_markdown="Calculer la limite de la suite $u_n$ quand n tend vers l'infini.", corrige_markdown="0",
        )
        cls.item_2 = CompetenceItem.objects.create(
            theme=cls.limites, subject=cls.maths, statut=VALIDE,
            enonce_markdown="Montrer que la suite géométrique converge.", corrige_markdown="ok",
        )
        for item in (cls.item_1, cls.item_2):
            item.cursus.add(cls.bac_c)

        blueprint = Blueprint.objects.create(subject=cls.maths, titre="Plan", statut=VALIDE)
        blueprint.cursus.add(cls.bac_c)
        blueprint.competences.add(cls.thales)
        cls.inedite = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=cls.maths, titre="Mathématiques Terminale C – Épreuve inédite n°1",
            statut=VALIDE,
        )
        cls.inedite.cursus.add(cls.bac_c)

        cls.abonne = User.objects.create_user(phone_number="677300001", password="x")
        Subscription.objects.create(
            user=cls.abonne, profil=cls.abonne.profils.first(), cursus=cls.bac_c,
            expires_at=timezone.now() + timedelta(days=5),
        )
        reconstruire()

    def chercher(self, requete, **kwargs):
        kwargs.setdefault("pays", self.pays)
        return moteur.chercher(requete, **kwargs)

    def titres(self, reponse, type_):
        for groupe in reponse["groupes"]:
            if groupe["type"] == type_:
                return [r["titre"] for r in groupe["resultats"]]
        return []

    def resultat(self, reponse, type_, titre):
        for groupe in reponse["groupes"]:
            if groupe["type"] == type_:
                for resultat in groupe["resultats"]:
                    if resultat["titre"] == titre:
                        return resultat
        self.fail(f"{type_} « {titre} » absent de la réponse")


class IndexationTests(_CorpusMixin, TestCase):
    def test_chaque_type_est_indexe_et_les_brouillons_sont_exclus(self):
        compte = lambda type_: EntreeRecherche.objects.filter(type=type_).count()  # noqa: E731
        self.assertEqual(compte(TypeResultat.COURS), 3)
        self.assertEqual(compte(TypeResultat.EPREUVE), 1)
        self.assertEqual(compte(TypeResultat.EXERCICE), 1)
        self.assertEqual(compte(TypeResultat.QUIZ), 2)
        self.assertEqual(compte(TypeResultat.INEDITE), 1)
        self.assertFalse(EntreeRecherche.objects.filter(titre__icontains="Brouillon").exists())

    def test_aucun_contenu_payant_n_est_indexe(self):
        for entree in EntreeRecherche.objects.all():
            for champ in (entree.cles_norm, entree.texte_norm, entree.apercu, str(entree.meta)):
                self.assertNotIn(SECRET_CORRIGE, champ)
                self.assertNotIn(SECRET_SECTION, champ)
        # ...mais l'énoncé et l'accroche, publics, le sont.
        epreuve = EntreeRecherche.objects.get(type=TypeResultat.EPREUVE)
        self.assertIn(" pythagore ", epreuve.texte_norm)
        cours = EntreeRecherche.objects.get(type=TypeResultat.COURS, objet_id=self.cours_lie.pk)
        self.assertIn(" emboites ", cours.texte_norm)

    def test_la_reconstruction_est_idempotente(self):
        avant = EntreeRecherche.objects.count()
        reconstruire()
        self.assertEqual(EntreeRecherche.objects.count(), avant)
        self.assertEqual(
            EntreeRecherche.cursus.through.objects.count(),
            EntreeRecherche.cursus.through.objects.values("entreerecherche_id", "cursus_id").distinct().count(),
        )

    def test_un_cours_sans_cursus_herite_de_celui_de_son_epreuve_source(self):
        entree = EntreeRecherche.objects.get(type=TypeResultat.COURS, objet_id=self.cours_lie.pk)
        self.assertFalse(entree.tous_cursus)
        self.assertEqual(list(entree.cursus.values_list("id", flat=True)), [self.bac_c.id])

    def test_un_cours_sans_cursus_ni_epreuve_source_est_propose_a_tous(self):
        entree = EntreeRecherche.objects.get(type=TypeResultat.COURS, objet_id=self.cours_commun.pk)
        self.assertTrue(entree.tous_cursus)

    def test_un_theme_n_existe_qu_avec_assez_de_contenu(self):
        # « limite d'une suite » : 2 questions de quiz. « théorème de Thalès » : 1 cours + 1 exercice.
        self.assertTrue(EntreeRecherche.objects.filter(type=TypeResultat.THEME, objet_id=self.limites.pk).exists())
        theme = EntreeRecherche.objects.get(type=TypeResultat.THEME, objet_id=self.thales.pk)
        self.assertEqual((theme.meta["nb_cours"], theme.meta["nb_exercices"], theme.meta["nb_quiz"]), (1, 1, 0))
        seul = Tag.objects.create(name="un seul cours")
        self.cours_commun.tags.add(seul)
        reconstruire([TypeResultat.THEME])
        self.assertFalse(EntreeRecherche.objects.filter(type=TypeResultat.THEME, objet_id=seul.pk).exists())

    def test_un_pays_desactive_disparait_de_l_index(self):
        Country.objects.filter(pk=self.pays.pk).update(actif=False)
        reconstruire()
        self.assertEqual(EntreeRecherche.objects.count(), 0)

    def test_reconstruire_un_seul_type_laisse_les_autres(self):
        avant = EntreeRecherche.objects.exclude(type=TypeResultat.QUIZ).count()
        reconstruire([TypeResultat.QUIZ])
        self.assertEqual(EntreeRecherche.objects.exclude(type=TypeResultat.QUIZ).count(), avant)

    def test_le_rattachement_au_programme_officiel_n_est_ni_indexe_ni_expose(self):
        # Tag.savoir_officiel est peu fiable : l'indexer ferait remonter un thème sur un sujet sans rapport.
        module = Module.objects.create(
            subject=self.maths, classe="Tle", serie_label="C", numero="1", titre="Orthogonalité dans l'espace",
        )
        savoir = Savoir.objects.create(module=module, intitule="Produit scalaire")
        Tag.objects.filter(pk=self.thales.pk).update(savoir_officiel=savoir)
        reconstruire([TypeResultat.THEME])
        entree = EntreeRecherche.objects.get(type=TypeResultat.THEME, objet_id=self.thales.pk)
        self.assertNotIn("orthogonalite", entree.cles_norm)
        self.assertNotIn("scalaire", entree.cles_norm)
        self.assertNotIn("savoir", entree.meta)
        self.assertEqual(self.chercher("orthogonalite", type_="THEME")["total"], 0)

    def test_le_vocabulaire_est_construit(self):
        self.assertTrue(TermeRecherche.objects.filter(terme="thales").exists())

    def test_commande_indexer_recherche(self):
        sortie = StringIO()
        call_command("indexer_recherche", "--si-vide", stdout=sortie)
        self.assertIn("déjà présent", sortie.getvalue())
        sortie = StringIO()
        call_command("indexer_recherche", "--types", "QUIZ", stdout=sortie)
        self.assertIn("Terminé", sortie.getvalue())


class MoteurTests(_CorpusMixin, TestCase):
    def test_trouve_sans_tenir_compte_des_accents_ni_du_pluriel(self):
        for requete in ("thales", "Thalès", "théorème thales", "theoremes de thales"):
            reponse = self.chercher(requete)
            self.assertIn("Le théorème de Thalès dans un triangle", self.titres(reponse, "COURS"), requete)
            self.assertIn("théorème de Thalès", self.titres(reponse, "THEME"), requete)

    def test_un_theme_etiquete_retrouve_l_epreuve_et_l_exercice(self):
        reponse = self.chercher("thales")
        self.assertEqual(self.titres(reponse, "EPREUVE"), ["Mathématiques BAC C 2019"])
        self.assertEqual(self.titres(reponse, "EXERCICE"), ["Exercice 1 · Mathématiques BAC C 2019"])
        self.assertEqual(self.titres(reponse, "INEDITE"), ["Mathématiques Terminale C – Épreuve inédite n°1"])

    def test_retrouve_une_notion_par_le_texte_public_d_un_enonce(self):
        reponse = self.chercher("pythagore")
        self.assertEqual(self.titres(reponse, "EPREUVE"), ["Mathématiques BAC C 2019"])
        extrait = self.resultat(reponse, "EXERCICE", "Exercice 1 · Mathématiques BAC C 2019")["apercu"]
        self.assertIn("Pythagore", extrait)

    def test_l_extrait_d_un_theme_etiquete_nomme_le_theme(self):
        reponse = self.chercher("thales")
        epreuve = self.resultat(reponse, "EPREUVE", "Mathématiques BAC C 2019")
        self.assertEqual(epreuve["apercu"], "Thème : théorème de Thalès")

    def test_ne_trouve_jamais_un_mot_present_seulement_dans_un_contenu_payant(self):
        for secret in (SECRET_CORRIGE, SECRET_SECTION):
            self.assertEqual(self.chercher(secret)["total"], 0, secret)

    def test_ne_trouve_pas_un_brouillon(self):
        self.assertNotIn("Brouillon sur Thalès", self.titres(self.chercher("brouillon"), "COURS"))

    def test_corrige_une_faute_de_frappe(self):
        reponse = self.chercher("thalez")
        self.assertEqual(reponse["corrige"], "thales")
        self.assertIn("théorème de Thalès", self.titres(reponse, "THEME"))

    def test_une_correction_garde_les_accents_des_autres_mots(self):
        reponse = self.chercher("théorème thalez")
        self.assertEqual(reponse["corrige"], "théorème thales")

    def test_la_correction_peut_etre_refusee(self):
        reponse = self.chercher("thalez", corriger_auto=False)
        self.assertIsNone(reponse["corrige"])
        self.assertEqual(reponse["total"], 0)

    def test_pas_de_correction_quand_la_recherche_aboutit(self):
        self.assertIsNone(self.chercher("thales")["corrige"])

    def test_requete_trop_courte(self):
        for requete in ("", "d", "ti"):
            reponse = self.chercher(requete)
            self.assertEqual(reponse["total"], 0, requete)
        self.assertTrue(self.chercher("d")["trop_court"])
        self.assertFalse(self.chercher("")["trop_court"])

    def test_filtre_d_examen_et_elargissement(self):
        # Au BAC C : le cours du BEPC est masqué, mais on dit qu'il en existe un ailleurs.
        reponse = self.chercher("fractions", cursus=self.bac_c.id)
        self.assertEqual(reponse["total"], 0)
        self.assertEqual(reponse["autres_cursus"], 1)
        # Au BEPC : trouvé.
        self.assertEqual(self.titres(self.chercher("fractions", cursus=self.bepc.id), "COURS"), ["Les fractions au BEPC"])
        # Élargi : trouvé aussi.
        self.assertEqual(
            self.titres(self.chercher("fractions", cursus=self.bac_c.id, elargir=True), "COURS"), ["Les fractions au BEPC"],
        )

    def test_un_contenu_de_tous_les_examens_passe_le_filtre(self):
        self.assertEqual(self.titres(self.chercher("aire", cursus=self.bepc.id), "COURS"), ["Calculer une aire"])

    def test_filtre_par_matiere_et_par_type(self):
        self.assertEqual(self.chercher("thales", matiere="PHYSIQUE")["total"], 0)
        reponse = self.chercher("thales", type_="COURS")
        self.assertEqual([g["type"] for g in reponse["groupes"]], ["COURS"])

    def test_repartition_par_matiere_et_filtre_sans_la_perdre(self):
        """« tangente » existe en maths et en physique : la répartition reste visible quand on choisit
        l'une des deux, pour pouvoir changer d'un clic."""
        physique = Subject.objects.get(country=self.pays, code="PHYSIQUE")
        Cours.objects.create(
            external_id="c-phys", titre="La tangente de la boussole", subject=physique, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Un courant et une aiguille."}],
        )
        Cours.objects.create(
            external_id="c-math", titre="Tangente à une courbe", subject=self.maths, statut=VALIDE,
            sections_raw=[{"type": "accroche", "contenu_markdown": "Une dérivée."}],
        )
        reconstruire([TypeResultat.COURS])

        tout = self.chercher("tangente")
        self.assertEqual({m["code"]: m["total"] for m in tout["matieres"]}, {"MATHS": 1, "PHYSIQUE": 1})
        self.assertEqual(sum(m["total"] for m in tout["matieres"]), tout["total"])

        maths = self.chercher("tangente", matiere="MATHS")
        self.assertEqual(self.titres(maths, "COURS"), ["Tangente à une courbe"])
        self.assertEqual(maths["total"], 1)
        # La répartition n'a pas bougé : on peut encore passer à la physique.
        self.assertEqual({m["code"]: m["total"] for m in maths["matieres"]}, {"MATHS": 1, "PHYSIQUE": 1})

    def test_une_matiere_inconnue_ne_donne_rien(self):
        reponse = self.chercher("thales", matiere="NIMPORTEQUOI")
        self.assertEqual(reponse["total"], 0)
        self.assertEqual(reponse["groupes"], [])

    def test_pagination_d_un_groupe(self):
        premiere = self.chercher("suite", type_="QUIZ", limite=1)
        self.assertEqual(premiere["groupes"][0]["total"], 1)  # deux questions, UN thème

    def test_les_questions_d_un_meme_theme_forment_un_seul_resultat(self):
        reponse = self.chercher("suite geometrique")
        quiz = self.resultat(reponse, "QUIZ", "limite d'une suite")
        self.assertEqual(quiz["nb"], 1)
        reponse = self.chercher("suite")
        # Le thème « limite d'une suite » est déjà proposé comme thème : pas de doublon côté quiz.
        self.assertIn("limite d'une suite", self.titres(reponse, "THEME"))
        self.assertEqual(self.titres(reponse, "QUIZ"), [])

    def test_une_notion_du_texte_d_un_quiz_est_retrouvee_sans_son_theme(self):
        reponse = self.chercher("converge")
        self.assertEqual(self.titres(reponse, "QUIZ"), ["limite d'une suite"])

    def test_acces_visiteur_anonyme_et_abonne(self):
        anonyme = self.chercher("thales")
        self.assertEqual(self.resultat(anonyme, "COURS", "Le théorème de Thalès dans un triangle")["acces"], "verrouille")
        self.assertEqual(self.resultat(anonyme, "EPREUVE", "Mathématiques BAC C 2019")["acces"], "verrouille")
        self.assertIsNone(self.resultat(anonyme, "THEME", "théorème de Thalès")["acces"])

        abonne = self.chercher("thales", utilisateur=self.abonne)
        self.assertEqual(self.resultat(abonne, "COURS", "Le théorème de Thalès dans un triangle")["acces"], "ouvert")
        self.assertEqual(self.resultat(abonne, "EPREUVE", "Mathématiques BAC C 2019")["acces"], "ouvert")

    def test_une_epreuve_vitrine_est_libre_pour_tous(self):
        Lesson.objects.filter(pk=self.lesson.pk).update(est_vitrine=True)
        reconstruire([TypeResultat.EPREUVE])
        self.assertEqual(self.resultat(self.chercher("thales"), "EPREUVE", "Mathématiques BAC C 2019")["acces"], "libre")

    def test_un_abonne_a_un_autre_cursus_n_a_pas_acces(self):
        autre = User.objects.create_user(phone_number="677300002", password="x")
        Subscription.objects.create(
            user=autre, profil=autre.profils.first(), cursus=self.bepc, expires_at=timezone.now() + timedelta(days=5),
        )
        reponse = self.chercher("thales", utilisateur=autre)
        self.assertEqual(self.resultat(reponse, "EPREUVE", "Mathématiques BAC C 2019")["acces"], "verrouille")

    def test_l_enonce_d_une_question_de_quiz_n_est_montre_qu_a_qui_peut_la_jouer(self):
        anonyme = self.chercher("converge")
        self.assertEqual(self.resultat(anonyme, "QUIZ", "limite d'une suite")["apercu"], "")
        abonne = self.chercher("converge", utilisateur=self.abonne)
        self.assertIn("converge", self.resultat(abonne, "QUIZ", "limite d'une suite")["apercu"])

    def test_inedite_expose_son_slug_et_reste_verrouillee(self):
        titre = "Mathématiques Terminale C – Épreuve inédite n°1"
        resultat = self.resultat(self.chercher("inedite terminale"), "INEDITE", titre)
        self.assertEqual(resultat["details"]["slug"], self.inedite.slug)
        self.assertEqual(resultat["acces"], "verrouille")

    def test_les_liens_d_un_theme_visent_le_cursus_de_l_eleve(self):
        entree = EntreeRecherche.objects.get(type=TypeResultat.THEME, objet_id=self.limites.pk)
        entree.cursus.add(self.bepc)
        reponse = self.chercher("limite", cursus=self.bepc.id, elargir=True)
        theme = self.resultat(reponse, "THEME", "limite d'une suite")
        self.assertEqual(theme["cursus_cible"], self.bepc.id)
        self.assertEqual(theme["details"]["tag_id"], self.limites.pk)
        self.assertEqual(theme["details"]["nb_quiz"], 2)

    def test_une_recherche_vide_propose_des_themes(self):
        reponse = self.chercher("xyzzyq")
        self.assertEqual(reponse["total"], 0)
        self.assertTrue(reponse["suggestions"])
        self.assertTrue(all(s["type"] == "THEME" for s in reponse["suggestions"]))

    def test_les_suggestions_ecartent_les_etiquettes_de_niveau(self):
        # « Terminale C » est rattaché à beaucoup de contenus (donc riche) mais n'est pas une notion.
        niveau = Tag.objects.create(name="Terminale C")
        for _ in range(3):
            item = CompetenceItem.objects.create(
                theme=niveau, subject=self.maths, statut=VALIDE, enonce_markdown="Question.", corrige_markdown="ok",
            )
            item.cursus.add(self.bac_c)
        reconstruire([TypeResultat.THEME])
        self.assertTrue(EntreeRecherche.objects.filter(type=TypeResultat.THEME, objet_id=niveau.pk).exists())
        titres = [s["titre"] for s in self.chercher("xyzzyq")["suggestions"]]
        self.assertTrue(titres)
        self.assertNotIn("Terminale C", titres)

    def test_sans_requete_la_page_recoit_des_themes_a_proposer(self):
        for requete in ("", "   "):
            reponse = self.chercher(requete)
            self.assertEqual(reponse["total"], 0, requete)
            self.assertFalse(reponse["trop_court"], requete)
            self.assertTrue(reponse["suggestions"], requete)
            self.assertTrue(all(s["type"] == "THEME" for s in reponse["suggestions"]))

    def test_les_themes_proposes_sans_requete_suivent_l_examen(self):
        # Le thème « limite d'une suite » n'existe qu'au BAC C ; au BEPC il ne doit pas être proposé.
        au_bepc = [s["titre"] for s in self.chercher("", cursus=self.bepc.id)["suggestions"]]
        self.assertNotIn("limite d'une suite", au_bepc)
        au_bac = [s["titre"] for s in self.chercher("", cursus=self.bac_c.id)["suggestions"]]
        self.assertIn("limite d'une suite", au_bac)

    def test_une_requete_courte_ne_recoit_pas_de_suggestions(self):
        self.assertEqual(self.chercher("d")["suggestions"], [])

    def test_les_details_n_exposent_jamais_les_cursus_d_acces(self):
        reponse = self.chercher("thales")
        for groupe in reponse["groupes"]:
            for resultat in groupe["resultats"]:
                self.assertNotIn("acces_ids", resultat["details"])

    def test_index_vide(self):
        EntreeRecherche.objects.all().delete()
        reponse = self.chercher("thales")
        self.assertFalse(reponse["indexe"])
        self.assertEqual(reponse["total"], 0)

    def test_le_nombre_de_requetes_ne_depend_pas_du_nombre_de_resultats(self):
        """Pas de N+1 : afficher 1 ou 40 résultats par groupe coûte le même nombre de requêtes."""
        with CaptureQueriesContext(connection) as un:
            self.chercher("thales", limite=1)
        with CaptureQueriesContext(connection) as quarante:
            self.chercher("thales", limite=40)
        self.assertEqual(len(un), len(quarante))
        self.assertLess(len(un), 30)


class JournalDesRecherchesVidesTests(TestCase):
    def test_compte_une_requete_normalisee(self):
        self.assertTrue(moteur.journaliser_vide("Équation  du 3e degré", "CM"))
        self.assertTrue(moteur.journaliser_vide("equation du 3e degre", "cm"))
        ligne = RechercheSansResultat.objects.get()
        self.assertEqual(ligne.requete, "equation du 3e degre")
        self.assertEqual(ligne.nb, 2)

    def test_refuse_numeros_et_adresses(self):
        for requete in ("699 12 34 56", "mon numero 699123456", "moi@example.com", "ab", ""):
            self.assertFalse(moteur.journaliser_vide(requete, "cm"), requete)
        self.assertFalse(RechercheSansResultat.objects.exists())

    def test_refuse_une_phrase_collee(self):
        self.assertFalse(moteur.journaliser_vide("un deux trois quatre cinq six sept huit neuf dix", "cm"))

    def test_une_annee_est_acceptee(self):
        self.assertTrue(moteur.journaliser_vide("bac c maths 2019", "cm"))

    def test_la_table_est_bornee(self):
        RechercheSansResultat.objects.bulk_create(
            [RechercheSansResultat(requete=f"requete{i}", pays_code="cm") for i in range(moteur.JOURNAL_MAX_LIGNES)],
        )
        self.assertFalse(moteur.journaliser_vide("nouvelle requete", "cm"))
        # Une requête déjà connue continue de compter.
        self.assertTrue(moteur.journaliser_vide("requete1", "cm"))


class VueRechercheTests(_CorpusMixin, TestCase):
    def setUp(self):
        self.client = APIClient()

    def get(self, **params):
        params.setdefault("pays", "cm")
        return self.client.get("/recherche/", params)

    def test_pays_inconnu(self):
        self.assertEqual(self.get(q="thales", pays="zz").status_code, 400)
        self.assertEqual(self.client.get("/recherche/", {"q": "thales"}).status_code, 400)

    def test_ouverte_aux_visiteurs_anonymes(self):
        reponse = self.get(q="thales")
        self.assertEqual(reponse.status_code, 200)
        self.assertGreater(reponse.json()["total"], 0)

    def test_forme_de_la_reponse(self):
        donnees = self.get(q="thales").json()
        for cle in ("q", "corrige", "indexe", "trop_court", "total", "groupes", "autres_cursus", "suggestions"):
            self.assertIn(cle, donnees)
        self.assertEqual([g["type"] for g in donnees["groupes"]], ["THEME", "COURS", "EPREUVE", "INEDITE", "EXERCICE"])
        resultat = donnees["groupes"][1]["resultats"][0]
        for cle in ("id", "type", "titre", "apercu", "matiere", "cursus", "acces", "details", "cursus_cible"):
            self.assertIn(cle, resultat)

    def test_les_parametres_invalides_ne_font_pas_planter(self):
        self.assertEqual(self.get(q="thales", cursus="abc", limite="x", decalage="-3", type="nimporte").status_code, 200)

    def test_utilisateur_connecte_voit_son_acces(self):
        self.client.force_authenticate(user=self.abonne)
        donnees = self.get(q="thales", type="COURS").json()
        self.assertEqual(donnees["groupes"][0]["resultats"][0]["acces"], "ouvert")

    def test_une_recherche_validee_sans_resultat_est_journalisee(self):
        self.get(q="xyzzyq")
        self.assertEqual(RechercheSansResultat.objects.get().requete, "xyzzyq")

    def test_la_saisie_en_direct_n_est_jamais_journalisee(self):
        self.get(q="xyzzyq", rapide="true")
        self.assertFalse(RechercheSansResultat.objects.exists())

    def test_un_zero_du_aux_filtres_n_est_pas_un_manque_du_catalogue(self):
        self.get(q="thales", matiere="PHYSIQUE")
        self.get(q="thales", type="QUIZ")
        # Rien dans l'examen choisi, mais un cours existe au BEPC : ce n'est pas un trou du catalogue.
        self.get(q="fractions", cursus=self.bac_c.id)
        self.assertFalse(RechercheSansResultat.objects.exists())

    def test_la_page_vide_ne_journalise_rien_et_propose_des_themes(self):
        donnees = self.get(q="").json()
        self.assertTrue(donnees["suggestions"])
        self.assertFalse(RechercheSansResultat.objects.exists())

    def test_une_requete_trop_courte_n_est_pas_journalisee(self):
        self.get(q="d")
        self.assertFalse(RechercheSansResultat.objects.exists())

    def test_les_evenements_de_mesure_sont_acceptes_sans_texte_saisi(self):
        for nom in ("recherche_lancee", "recherche_resultat_clique"):
            reponse = self.client.post(
                "/analytics/events/", {"name": nom, "properties": {"source": "palette", "type": "COURS", "rang": 1}},
                format="json",
            )
            self.assertEqual(reponse.status_code, 201, nom)

    def test_exact_desactive_la_correction(self):
        self.assertEqual(self.get(q="thalez").json()["corrige"], "thales")
        self.assertIsNone(self.get(q="thalez", exact="true").json()["corrige"])
