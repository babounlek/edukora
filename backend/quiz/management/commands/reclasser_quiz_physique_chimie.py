"""
Décision utilisateur du 2026-11-02 : le banc de quiz n'a pas de matière « Physique-Chimie »
(PHYSIQUE_CHIMIE) ; il a PHYSIQUE, CHIMIE et PHYSIQUE_CHIMIE_TECH. Les 372 CompetenceItem
encore rattachés à PHYSIQUE_CHIMIE (Cameroun, 62 thèmes de 6 questions) sont reclassés, thème par
thème, d'après le contenu réel des énoncés : 26 thèmes en PHYSIQUE, 36 en CHIMIE.

Ne modifie que CompetenceItem.subject : ni l'id, ni l'external_id, ni le thème, ni les cours et
leçons rattachés à PHYSIQUE_CHIMIE. Idempotente (un item déjà reclassé n'est plus sélectionné) ;
un thème inconnu arrête tout sans rien écrire.

    python manage.py reclasser_quiz_physique_chimie            # simulation
    python manage.py reclasser_quiz_physique_chimie --apply
"""

from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Subject
from quiz.models import CompetenceItem

PHYSIQUE = {
    "photon", "optique géométrique", "nature d'une lentille", "mouvement rectiligne uniformément varié",
    "miroirs plans", "Mécanique newtonienne", "Longueur d'onde seuil", "Lois de conservation de Soddy",
    "Loi de décroissance radioactive", "Fusion nucléaire", "force", "dioptre", "désintégration radioactive",
    "cuve à ondes", "Cellules photoémissives", "Cellule photoélectrique", "angle de réfraction",
    "accélération", "réfraction de la lumière", "réflexion de la lumière", "Réaction nucléaire",
    "principe d'inertie", "réfraction limite", "référentiel galiléen", "œil", "équilibre d'un solide",
}
CHIMIE = {
    "pollution", "pollution agricole", "méthane", "impact environnemental", "hydrogénation",
    "hydrocarbures aromatiques", "humus", "formule N-P-K", "formule développée", "fertilité du sol",
    "fertilisation", "eutrophisation", "engrais", "engrais NPK", "engrais composé", "engrais binaire",
    "engrais azotés", "dihydrogène", "dérivés halogénés", "déchets plastiques", "chlorure d'hydrogène",
    "chloration", "catalyseur", "calcul de masse", "biodégradabilité", "azote", "Applications des polymères",
    "recyclage", "PVC", "pourcentage massique", "polyéthylène", "pétrole", "Sols", "étiquetage des engrais",
    "éléments fertilisants NPK", "encadrement",
}


class Command(BaseCommand):
    help = "Reclasse les quiz PHYSIQUE_CHIMIE (CM) en PHYSIQUE ou CHIMIE selon le thème."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--pays", default="CM")

    def handle(self, *args, **options):
        pays = options["pays"].upper()
        try:
            source = Subject.objects.get(code="PHYSIQUE_CHIMIE", country__code=pays)
            cibles = {
                "PHYSIQUE": Subject.objects.get(code="PHYSIQUE", country__code=pays),
                "CHIMIE": Subject.objects.get(code="CHIMIE", country__code=pays),
            }
        except Subject.DoesNotExist as exc:
            raise CommandError(f"Matière introuvable pour {pays} : {exc}")
        items = list(CompetenceItem.objects.filter(subject=source).select_related("theme"))
        inconnus = sorted({i.theme.name for i in items} - PHYSIQUE - CHIMIE)
        if inconnus:
            raise CommandError(f"Thèmes non classés (rien n'est écrit) : {inconnus}")
        par_cible = {"PHYSIQUE": [], "CHIMIE": []}
        for i in items:
            par_cible["PHYSIQUE" if i.theme.name in PHYSIQUE else "CHIMIE"].append(i.pk)
        bilan = Counter({k: len(v) for k, v in par_cible.items()})
        self.stdout.write(f"{pays} : {len(items)} item(s) PHYSIQUE_CHIMIE -> {dict(bilan)}")
        if not options["apply"]:
            self.stdout.write("Simulation : rien n'est écrit (--apply pour appliquer).")
            return
        with transaction.atomic():
            for code, pks in par_cible.items():
                if pks:
                    CompetenceItem.objects.filter(pk__in=pks).update(subject=cibles[code])
        reste = CompetenceItem.objects.filter(subject=source).count()
        self.stdout.write(self.style.SUCCESS(f"Reclassés. Reste en PHYSIQUE_CHIMIE : {reste}"))
