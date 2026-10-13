"""
Coche CompetenceItem.est_vitrine pour la sélection de quiz gratuits : un thème par matière et par
cursus, jouable en entier sans abonnement (voir quiz.services.perimetre_est_vitrine).

La sélection vit ici, en clair, plutôt que dans l'admin : elle se rejoue à l'identique en
production (les ids de Cursus/Tag y diffèrent) et se relit d'un coup d'œil. Chaque entrée est
identifiée par des clés stables (pays, examen, série, code matière, nom du tag), jamais par un id.

    python manage.py definir_quiz_vitrine                 # simulation (annulée), affiche le résultat
    python manage.py definir_quiz_vitrine --appliquer     # aligne la base sur la sélection
    python manage.py definir_quiz_vitrine --retirer       # décoche tout ce qui est coché
    python manage.py definir_quiz_vitrine --ids           # simulation + ids des items gratuits obtenus

`--appliquer` ALIGNE : il coche les items de la sélection, décoche tout autre item déjà vitrine (la
sélection est la seule source de vérité : jamais coché à la main dans l'admin sans repasser ici),
puis ÉLAGUE : les items étant partagés entre cursus, la sélection rend gratuits d'autres thèmes que
ceux visés ; or un seul quiz est joué par (cursus, matière) - voir quiz.gratuits - donc tout item
qui n'appartient à aucun quiz retenu est décoché.

Choix (2026-10-13) : un thème par matière, pour les 8 matières les plus utiles de chaque cursus
(10 au BEPC) - Maths, Français, Anglais et Philosophie d'abord, puis par coefficient. Pour chaque
matière, le thème le plus souvent tombé aux épreuves officielles du cursus, de 5 à 14 items, sans
figure, hors thèmes génériques. Les 18 thèmes du 2026-10-12 laissaient le BEPC varié mais empilaient
5 à 7 thèmes de Maths dans chaque autre cursus : les items sont PARTAGÉS entre cursus
(CompetenceItem.cursus est M2M), donc un thème de Maths coché pour un cursus devenait gratuit dans
tous les autres. Une sélection à une matière par cursus, thèmes communs choisis les mêmes d'un
cursus à l'autre, évite ces cumuls.
Le périmètre d'un thème est tout ou rien : un thème offert l'est avec tous ses items VALIDE du
cursus, sans quoi perimetre_est_vitrine refuserait la session.
"""
from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Cursus, Tag
from quiz.gratuits import themes_gratuits_par_matiere
from quiz.models import CompetenceItem

# (pays, examen, série ou None, code matière, nom exact du Tag)
SELECTION = [
    # BEPC
    ("CM", "BEPC", None, "MATHS", "identité remarquable"),
    ("CM", "BEPC", None, "ANGLAIS", "connecteurs logiques"),
    ("CM", "BEPC", None, "FRANCAIS", "passé simple"),
    ("CM", "BEPC", None, "PHYSIQUE_CHIMIE_TECH", "masse molaire"),
    ("CM", "BEPC", None, "ALLEMAND", "compréhension écrite"),
    ("CM", "BEPC", None, "ESPAGNOL", "versión"),
    ("CM", "BEPC", None, "GEOGRAPHIE", "sous-développement"),
    ("CM", "BEPC", None, "HISTOIRE", "décolonisation"),
    ("CM", "BEPC", None, "SVT", "sida"),
    ("CM", "BEPC", None, "INFORMATIQUE", "algorithmique"),
    # BAC série A
    ("CM", "BAC", "A", "PHILOSOPHIE", "explication de texte"),
    ("CM", "BAC", "A", "ANGLAIS", "texte à trous"),
    ("CM", "BAC", "A", "FRANCAIS", "champ lexical"),
    ("CM", "BAC", "A", "MATHS", "tableau de variation"),
    ("CM", "BAC", "A", "ALLEMAND", "antonymes"),
    ("CM", "BAC", "A", "ESPAGNOL", "compréhension de texte"),
    ("CM", "BAC", "A", "LITTERATURE", "figures de style"),
    ("CM", "BAC", "A", "GEOGRAPHIE", "puissances économiques"),
    # BAC série C
    ("CM", "BAC", "C", "MATHS", "tableau de variation"),
    ("CM", "BAC", "C", "ANGLAIS", "collocations"),
    ("CM", "BAC", "C", "PHILOSOPHIE", "épistémologie"),
    ("CM", "BAC", "C", "FRANCAIS", "figures de style"),
    ("CM", "BAC", "C", "CHIMIE", "pKa"),
    ("CM", "BAC", "C", "INFORMATIQUE", "SQL"),
    ("CM", "BAC", "C", "LITTERATURE", "discussion argumentée"),
    ("CM", "BAC", "C", "SVT", "méiose"),
    # BAC série D
    ("CM", "BAC", "D", "MATHS", "tableau de variation"),
    ("CM", "BAC", "D", "ANGLAIS", "collocations"),
    ("CM", "BAC", "D", "PHILOSOPHIE", "dissertation philosophique"),
    ("CM", "BAC", "D", "FRANCAIS", "connecteurs logiques"),
    ("CM", "BAC", "D", "SVT", "Lymphocyte T4"),
    ("CM", "BAC", "D", "CHIMIE", "pKa"),
    ("CM", "BAC", "D", "INFORMATIQUE", "SQL"),
    ("CM", "BAC", "D", "LITTERATURE", "dissertation littéraire"),
    # BAC série E
    ("CM", "BAC", "E", "MATHS", "tableau de variation"),
    ("CM", "BAC", "E", "ANGLAIS", "question tags"),
    ("CM", "BAC", "E", "PHILOSOPHIE", "plan dialectique"),
    ("CM", "BAC", "E", "FRANCAIS", "figures de style"),
    ("CM", "BAC", "E", "PHYSIQUE", "Mouvement circulaire uniforme"),
    ("CM", "BAC", "E", "INFORMATIQUE", "SQL"),
    ("CM", "BAC", "E", "LITTERATURE", "discussion argumentée"),
    ("CM", "BAC", "E", "EDUCATION_CIVIQUE", "Union Africaine"),
    # BAC série TI
    ("CM", "BAC", "TI", "MATHS", "équation différentielle"),
    ("CM", "BAC", "TI", "ANGLAIS", "question tags"),
    ("CM", "BAC", "TI", "PHILOSOPHIE", "dissertation philosophique"),
    ("CM", "BAC", "TI", "FRANCAIS", "connecteurs logiques"),
    ("CM", "BAC", "TI", "SYSTEMES_INFORMATION", "base de données"),
    ("CM", "BAC", "TI", "PROGRAMMATION", "SQL"),
    ("CM", "BAC", "TI", "LITTERATURE", "dissertation littéraire"),
    ("CM", "BAC", "TI", "PHYSIQUE", "radioactivité"),
    # PROBATOIRE série A
    ("CM", "PROBATOIRE", "A", "PHILOSOPHIE", "plan dialectique"),
    ("CM", "PROBATOIRE", "A", "FRANCAIS", "conjugaison"),
    ("CM", "PROBATOIRE", "A", "MATHS", "tableau de variation"),
    ("CM", "PROBATOIRE", "A", "ANGLAIS", "voix passive"),
    ("CM", "PROBATOIRE", "A", "LITTERATURE", "méthode de la contraction"),
    ("CM", "PROBATOIRE", "A", "ALLEMAND", "verbes modaux"),
    ("CM", "PROBATOIRE", "A", "ESPAGNOL", "compréhension de texte"),
    ("CM", "PROBATOIRE", "A", "GEOGRAPHIE", "croissance démographique"),
    # PROBATOIRE série C
    ("CM", "PROBATOIRE", "C", "MATHS", "tableau de variation"),
    ("CM", "PROBATOIRE", "C", "ANGLAIS", "voix passive"),
    ("CM", "PROBATOIRE", "C", "FRANCAIS", "connecteurs logiques"),
    ("CM", "PROBATOIRE", "C", "PHILOSOPHIE", "plan dialectique"),
    ("CM", "PROBATOIRE", "C", "LITTERATURE", "méthode de la contraction"),
    ("CM", "PROBATOIRE", "C", "PHYSIQUE", "lentille convergente"),
    ("CM", "PROBATOIRE", "C", "CHIMIE", "oxydoréduction"),
    ("CM", "PROBATOIRE", "C", "GEOGRAPHIE", "tectonique des plaques"),
    # PROBATOIRE série D
    ("CM", "PROBATOIRE", "D", "MATHS", "tableau de variation"),
    ("CM", "PROBATOIRE", "D", "ANGLAIS", "voix passive"),
    ("CM", "PROBATOIRE", "D", "FRANCAIS", "connecteurs logiques"),
    ("CM", "PROBATOIRE", "D", "PHILOSOPHIE", "plan dialectique"),
    ("CM", "PROBATOIRE", "D", "SVT", "photosynthèse"),
    ("CM", "PROBATOIRE", "D", "LITTERATURE", "méthode de la contraction"),
    ("CM", "PROBATOIRE", "D", "CHIMIE", "oxydoréduction"),
    ("CM", "PROBATOIRE", "D", "GEOGRAPHIE", "subduction"),
    # PROBATOIRE série E
    ("CM", "PROBATOIRE", "E", "MATHS", "tableau de variation"),
    ("CM", "PROBATOIRE", "E", "ANGLAIS", "question tags"),
    ("CM", "PROBATOIRE", "E", "FRANCAIS", "connecteurs logiques"),
    ("CM", "PROBATOIRE", "E", "PHILOSOPHIE", "plan dialectique"),
    ("CM", "PROBATOIRE", "E", "LITTERATURE", "méthode de la contraction"),
    ("CM", "PROBATOIRE", "E", "CHIMIE", "oxydoréduction"),
    ("CM", "PROBATOIRE", "E", "GEOGRAPHIE", "volcanisme"),
    ("CM", "PROBATOIRE", "E", "INFORMATIQUE", "conversion d'unités"),
    # PROBATOIRE série TI
    ("CM", "PROBATOIRE", "TI", "ANGLAIS", "voix passive"),
    ("CM", "PROBATOIRE", "TI", "FRANCAIS", "émetteur et récepteur"),
    ("CM", "PROBATOIRE", "TI", "PHILOSOPHIE", "plan dialectique"),
    ("CM", "PROBATOIRE", "TI", "LITTERATURE", "méthode de la contraction"),
    ("CM", "PROBATOIRE", "TI", "PROGRAMMATION", "bibliothèque standard"),
    ("CM", "PROBATOIRE", "TI", "GEOGRAPHIE", "gaz à effet de serre"),
    ("CM", "PROBATOIRE", "TI", "INFORMATIQUE", "processeur"),
    ("CM", "PROBATOIRE", "TI", "PHYSIQUE", "relation de conjugaison"),
]


def _items_de(pays, examen, serie, code_matiere, nom_tag):
    cursus = Cursus.objects.filter(country__code=pays, examen=examen)
    cursus = cursus.filter(series__code=serie) if serie else cursus.filter(series__isnull=True)
    cursus = cursus.first()
    if cursus is None:
        raise CommandError(f"Cursus introuvable : {pays} {examen} {serie or ''}".strip())
    try:
        theme = Tag.objects.get(name=nom_tag)
    except Tag.DoesNotExist:
        raise CommandError(f"Tag introuvable : {nom_tag!r}") from None
    items = CompetenceItem.objects.filter(
        statut="VALIDE", cursus=cursus, subject__code=code_matiere, theme=theme,
    )
    return cursus, items


class Command(BaseCommand):
    help = "Aligne les quiz gratuits (est_vitrine) sur la sélection - voir la docstring du module."

    def add_arguments(self, parser):
        groupe = parser.add_mutually_exclusive_group()
        groupe.add_argument("--appliquer", action="store_true", help="Aligner est_vitrine sur la sélection.")
        groupe.add_argument("--retirer", action="store_true", help="Décocher est_vitrine partout.")
        groupe.add_argument("--ids", action="store_true", help="Afficher les ids des items gratuits obtenus.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["retirer"]:
            retires = CompetenceItem.objects.filter(est_vitrine=True).update(est_vitrine=False)
            self.stdout.write(self.style.SUCCESS(f"{retires} items décochés, plus aucun quiz gratuit."))
            return

        voulus = set()
        for cle in SELECTION:
            cursus, items = _items_de(*cle)
            ids = set(items.values_list("id", flat=True))
            if not ids:
                raise CommandError(f"Aucun item VALIDE pour {cle} - sélection périmée ?")
            voulus |= ids
            self.stdout.write(f"{cursus} | {cle[3]} | {cle[4]} : {len(ids)} items")

        # 1. La sélection, et rien d'autre : tout item déjà gratuit hors sélection est décoché.
        avant = CompetenceItem.objects.filter(est_vitrine=True).count()
        CompetenceItem.objects.filter(id__in=voulus).update(est_vitrine=True)
        CompetenceItem.objects.filter(est_vitrine=True).exclude(id__in=voulus).update(est_vitrine=False)

        # 2. Élagage : les items étant partagés entre cursus, la sélection rend gratuits d'autres
        # thèmes que ceux visés. Un seul quiz est joué par (cursus, matière) - voir
        # quiz.gratuits.themes_gratuits_par_matiere - donc tout item qui n'appartient à aucun de ces
        # quiz retenus ne sert plus à rien : il est décoché (sinon la recherche l'annoncerait gratuit).
        cursus_ids = list(CompetenceItem.objects.filter(est_vitrine=True).values_list("cursus", flat=True).distinct())
        retenus = themes_gratuits_par_matiere(cursus_ids)
        gardes = set()
        for g in retenus:
            gardes |= set(CompetenceItem.objects.filter(
                statut="VALIDE", cursus=g["cursus"], subject=g["subject"], theme=g["theme"],
            ).values_list("id", flat=True))
        elagues = CompetenceItem.objects.filter(est_vitrine=True).exclude(id__in=gardes).update(est_vitrine=False)

        par_cursus = Counter(g["cursus"] for g in retenus)
        for cursus in Cursus.objects.filter(id__in=par_cursus).order_by("examen", "series__code"):
            self.stdout.write(f"  {cursus} : {par_cursus[cursus.id]} quiz gratuits (un par matière)")
        total = CompetenceItem.objects.filter(est_vitrine=True).count()
        self.stdout.write(self.style.SUCCESS(
            f"{len(SELECTION)} thèmes sélectionnés -> {len(retenus)} quiz gratuits (cursus x matière), "
            f"{total} items ({avant} avant ; {elagues} élagués).",
        ))
        if options["ids"]:
            self.stdout.write("IDS " + ",".join(str(i) for i in sorted(CompetenceItem.objects.filter(est_vitrine=True).values_list("id", flat=True))))
        if not options["appliquer"]:
            transaction.set_rollback(True)
            self.stdout.write("(simulation : rien n'a été écrit)")
