"""
Coche Lesson.est_vitrine pour un corrigé gratuit par couple (cursus, matière) du BEPC, du Probatoire et du
BAC - le pendant francophone de definir_papers_vitrine (GCE), dont il reprend les règles : accès libre sans
abonnement ni connexion, sélection en clair ici (rejouable en production, où les ids diffèrent), clés stables
(pays, examen, titre exact) jamais un id.

    python manage.py definir_papers_vitrine_francophone                 # simulation (annulée)
    python manage.py definir_papers_vitrine_francophone --appliquer     # coche les papers de la sélection
    python manage.py definir_papers_vitrine_francophone --retirer       # décoche UNIQUEMENT la sélection

Proposition du 2026-11-02 : seuls les couples sans corrigé gratuit sont pourvus (les papers gratuits posés à
la main restent tels quels et ne sont jamais décochés). Règle de choix : sujet officiel, titre unique pour le
pays et l'examen, pas une épreuve pratique ; un paper commun à plusieurs séries (« C, D, E et TI ») couvre
toutes ses séries d'un coup ; à défaut le plus récent, de préférence entre 3 et 6 exercices.

Manques assumés, faute de sujet officiel complet : BAC Physique-Chimie C et E (seul un sujet d'établissement),
Probatoire Informatique TI (seul un examen blanc) et Probatoire Programmation TI (seul un sujet d'établissement).
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from .definir_papers_vitrine import _lesson_de

# (pays, examen, titre exact)
SELECTION = [
    ("CM", "BEPC", "Allemand BEPC 2025"),
    ("CM", "BEPC", "Anglais BEPC 2025"),
    ("CM", "BEPC", "Dessin BEPC 2026"),
    ("CM", "BEPC", "Espagnol BEPC 2026"),
    ("CM", "BEPC", "Français BEPC 2015 - Étude de texte"),
    ("CM", "BEPC", "Géographie BEPC 2026"),
    ("CM", "BEPC", "Histoire BEPC 2017"),
    ("CM", "BEPC", "Histoire BEPC 2025"),
    ("CM", "BEPC", "Informatique BEPC 2026"),
    ("CM", "BEPC", "Physique-Chimie-Technologie BEPC 2026"),
    ("CM", "BEPC", "Sciences de la Vie et de la Terre BEPC 2026"),
    ("CM", "BEPC", "Éducation Civique BEPC 2017"),
    ("CM", "BEPC", "Éducation physique et sportive BEPC 2025"),
    ("CM", "PROBATOIRE", "Allemand Probatoire A 2024 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Anglais Probatoire A, C, D et E 2015"),
    ("CM", "PROBATOIRE", "Anglais Probatoire A, C, D et TI 2022"),
    ("CM", "PROBATOIRE", "Chimie Probatoire A 2018 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Chimie Probatoire C 2004"),
    ("CM", "PROBATOIRE", "Chimie Probatoire C, D et E 2026"),
    ("CM", "PROBATOIRE", "Chimie Probatoire D et TI 2026"),
    ("CM", "PROBATOIRE", "Chimie Probatoire E 2003"),
    ("CM", "PROBATOIRE", "Dessin Probatoire A 2025"),
    ("CM", "PROBATOIRE", "Espagnol Probatoire A 2023 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Français Probatoire A 2024 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Français Probatoire C, D, E et TI 2025"),
    ("CM", "PROBATOIRE", "Géographie Probatoire A, C, D, E et TI 2022"),
    ("CM", "PROBATOIRE", "Histoire Probatoire A 2019 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Histoire Probatoire A 2021 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Histoire Probatoire C, D, E et TI 2019"),
    ("CM", "PROBATOIRE", "Histoire Probatoire C, D, E et TI 2024"),
    ("CM", "PROBATOIRE", "Informatique Probatoire A, C, D et E 2019 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Littérature Probatoire A, C, D, E et TI 2019 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Mathématiques Probatoire A 2026"),
    ("CM", "PROBATOIRE", "Mathématiques Probatoire C et E 2025"),
    ("CM", "PROBATOIRE", "Mathématiques Probatoire D 2025"),
    ("CM", "PROBATOIRE", "Philosophie Probatoire A 2025 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Philosophie Probatoire C, D, E et TI"),
    ("CM", "PROBATOIRE", "Physique Probatoire C et E 2026"),
    ("CM", "PROBATOIRE", "Physique Probatoire D et TI 2025"),
    ("CM", "PROBATOIRE", "Sciences Probatoire A 2025 - A4 Bilingue"),
    ("CM", "PROBATOIRE", "Sciences de la Vie et de la Terre Probatoire C et TI 2025"),
    ("CM", "PROBATOIRE", "Sciences de la Vie et de la Terre Probatoire D"),
    ("CM", "PROBATOIRE", "Systèmes d'Information Probatoire TI 2023"),
    ("CM", "PROBATOIRE", "Économie Probatoire TI 2017"),
    ("CM", "PROBATOIRE", "Éducation Civique Probatoire A, C, D, E et TI 2025"),
    ("CM", "PROBATOIRE", "Éducation physique et sportive Probatoire A, C, D, E et TI 2025"),
    ("CM", "BAC", "Allemand BAC A - A4 Bilingue 2025"),
    ("CM", "BAC", "Anglais BAC A 2025"),
    ("CM", "BAC", "Anglais BAC C, D, E et TI 2025"),
    ("CM", "BAC", "Chimie BAC TI 2023"),
    ("CM", "BAC", "Dessin BAC A, C, D, E et TI 2024"),
    ("CM", "BAC", "Espagnol BAC A 2025 - A4 Bilingue"),
    ("CM", "BAC", "Français BAC A 2024 - A4 Bilingue"),
    ("CM", "BAC", "Français BAC C, D, E et TI 2025"),
    ("CM", "BAC", "Géographie BAC A 2019 - A4 Bilingue"),
    ("CM", "BAC", "Géographie BAC A 2021 - A4 Bilingue"),
    ("CM", "BAC", "Géographie BAC C, D, E et TI 2017"),
    ("CM", "BAC", "Histoire BAC A 2021 - A4 Bilingue"),
    ("CM", "BAC", "Histoire BAC C, D, E et TI 2019"),
    ("CM", "BAC", "Histoire BAC C, D, E et TI 2020"),
    ("CM", "BAC", "Informatique BAC A, C, D et E 2020"),
    ("CM", "BAC", "Littérature BAC A - A4 Bilingue"),
    ("CM", "BAC", "Littérature BAC C, D, E et TI 2014"),
    ("CM", "BAC", "Mathématiques BAC D et TI 2025"),
    ("CM", "BAC", "Philosophie BAC A 2020 - A4 Bilingue"),
    ("CM", "BAC", "Philosophie BAC C, D, E et TI 2025"),
    ("CM", "BAC", "Physique BAC C et E 2024"),
    ("CM", "BAC", "Physique BAC D et TI 2021"),
    ("CM", "BAC", "Physique-Chimie BAC D et TI 2017"),
    ("CM", "BAC", "Programmation BAC TI 2019"),
    ("CM", "BAC", "Programmation BAC TI 2023"),
    ("CM", "BAC", "Réseaux, Internet et Sécurité Informatique BAC TI 2023"),
    ("CM", "BAC", "Sciences BAC A 2025 - A4 Bilingue"),
    ("CM", "BAC", "Sciences de la Vie et de la Terre BAC C et TI 2026"),
    ("CM", "BAC", "Sciences de la Vie et de la Terre BAC D 2024"),
    ("CM", "BAC", "Systèmes d'Information BAC TI"),
    ("CM", "BAC", "Éducation Civique BAC A, C, D, E et TI 2025"),
    ("CM", "BAC", "Éducation physique et sportive BAC A, C, D, E et TI 2020"),
    ("BJ", "BAC", "Mathématiques BAC A 2001"),
    ("CG", "BAC", "Mathématiques BAC C 2004"),
    ("CG", "BAC", "Physique-Chimie BAC C 2016"),
    ("CI", "BAC", "Mathématiques BAC A1 2015"),
    ("CI", "BAC", "Mathématiques BAC D 2014"),
]


class Command(BaseCommand):
    help = "Coche (ou décoche) est_vitrine sur la sélection francophone - voir la docstring du module."

    def add_arguments(self, parser):
        groupe = parser.add_mutually_exclusive_group()
        groupe.add_argument("--appliquer", action="store_true", help="Cocher est_vitrine sur la sélection.")
        groupe.add_argument("--retirer", action="store_true", help="Décocher est_vitrine sur la sélection (seulement elle).")

    @transaction.atomic
    def handle(self, *args, **options):
        retirer = options["retirer"]
        for cle in SELECTION:
            lesson = _lesson_de(*cle)
            if lesson.est_vitrine == (not retirer):
                self.stdout.write(f"{lesson.title} : déjà {'gratuit' if not retirer else 'payant'}")
                continue
            lesson.est_vitrine = not retirer
            lesson.save(update_fields=["est_vitrine"])
            self.stdout.write(f"{lesson.title} : {'gratuit' if not retirer else 'décoché'}")
        self.stdout.write(self.style.SUCCESS(
            f"{len(SELECTION)} papers {'décochés' if retirer else 'en accès libre'}.",
        ))
        if not (options["appliquer"] or retirer):
            transaction.set_rollback(True)
            self.stdout.write("(simulation : rien n'a été écrit)")
