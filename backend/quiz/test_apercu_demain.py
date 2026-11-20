"""Aperçu de demain (voir quiz.services.apercu_de_demain) : seulement ce qui sera réellement dû, jamais une prédiction."""
from datetime import timedelta

from django.utils import timezone

from catalog.models import Cours, StatutContenu

from . import cartes
from .models import CarteRevue, RevisionSchedule
from .services import APERCU_DEMAIN_THEMES_MAX, apercu_de_demain
from .test_erreurs import ErreursFixture


class ApercuDeDemainTests(ErreursFixture):
    def setUp(self):
        super().setUp()
        self.aujourdhui = timezone.localdate()

    def _suivi(self, theme, dans, subject=None):
        return RevisionSchedule.objects.create(
            profil=self.profil, cursus=self.cursus, subject=subject or self.maths, theme=theme,
            palier=0, due_at=self.aujourdhui + timedelta(days=dans),
        )

    def test_rien_a_annoncer_pour_un_eleve_sans_echeance(self):
        self.assertEqual(apercu_de_demain(self.profil, self.cursus), {"themes": [], "themes_total": 0, "cartes": 0})

    def test_annonce_les_themes_dus_demain_pas_ceux_d_apres(self):
        self._suivi(self.derivation, dans=1)
        self._suivi(self.limites, dans=5)

        apercu = apercu_de_demain(self.profil, self.cursus)

        self.assertEqual(apercu["themes"], [{"theme": "dérivation", "subject_label": self.maths.label}])
        self.assertEqual(apercu["themes_total"], 1)

    def test_un_theme_en_retard_passe_devant_et_la_liste_est_bornee(self):
        self._suivi(self.derivation, dans=1)
        self._suivi(self.limites, dans=-3)  # déjà en retard : il sera encore dû demain
        self._suivi(self.optique, dans=0, subject=self.physique)

        apercu = apercu_de_demain(self.profil, self.cursus)

        self.assertEqual(apercu["themes"][0]["theme"], "limites")
        self.assertEqual(len(apercu["themes"]), APERCU_DEMAIN_THEMES_MAX)
        self.assertEqual(apercu["themes_total"], 3)

    def test_compte_les_cartes_de_revision_dues_demain(self):
        sections = [{"type": "regle", "titre": "Règle", "contenu_markdown": "Texte."}]
        for n in range(3):
            cours = Cours.objects.create(
                external_id=f"apercu-{n}", titre=f"Cours {n}", subject=self.maths, sections_raw=sections,
                statut=StatutContenu.VALIDE,
            )
            # Ratée : revient demain. Sue : revient dans trois jours.
            cartes.noter(self.profil, cours, "regle", n == 0)

        self.assertEqual(CarteRevue.objects.filter(profil=self.profil).count(), 3)
        self.assertEqual(apercu_de_demain(self.profil, self.cursus)["cartes"], 2)

    def test_ne_montre_pas_les_echeances_d_un_autre_profil(self):
        from users.models import User

        autre = User.objects.create_user(phone_number="677610099", password="x").profils.first()
        RevisionSchedule.objects.create(
            profil=autre, cursus=self.cursus, subject=self.maths, theme=self.derivation, palier=0,
            due_at=self.aujourdhui + timedelta(days=1),
        )

        self.assertEqual(apercu_de_demain(self.profil, self.cursus)["themes_total"], 0)
