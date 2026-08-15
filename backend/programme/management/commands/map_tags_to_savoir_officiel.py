import re
from collections import Counter

from django.core.management.base import BaseCommand

from catalog.ingestion import _normalize
from catalog.models import Tag
from programme.models import Savoir

# Règles ordonnées (tag_pattern, savoir_pattern) : pour un Tag dont le nom (normalisé -
# ASCII, minuscule, voir catalog.ingestion._normalize) matche `tag_pattern`, on ne
# retient que les Savoir dont le texte de recherche (titre du module + intitulé du
# savoir, même normalisation) matche `savoir_pattern`. Un tag qui matche `tag_pattern`
# mais dont aucun Savoir ne matche `savoir_pattern` (règle mal calibrée, ou notion hors
# du programme officiel simplifié - ex. algèbre abstraite avancée) reste simplement non
# rattaché, jamais forcé sur un mauvais savoir.
#
# La première règle qui matche gagne (ordre = spécificité décroissante nécessaire par
# endroits, ex. transformations complexes avant nombres complexes algébriques, pour ne
# pas laisser une notion géométrique se faire absorber par la règle algébrique plus
# générale qui la suit).
RULES = [
    # --- Nombres complexes : géométrique (points/transformations via affixes) avant
    # algébrique (sinon "affixe" et "similitude" seraient happés par la règle générale
    # "complexe" plus bas) ---
    (
        r"affixe|similitude|homothetie vectorielle|rotation (complexe|vectorielle|dans l.espace)|"
        r"translation complexe|ecriture complexe|centre d.une (rotation|similitude|symetrie)|"
        r"angle (d.une similitude|de rotation|oriente)|image d.un point par une (similitude|transformation|symetrie)|"
        r"image d.une courbe par une (similitude|transformation|isometrie)|image d.un cercle|"
        r"invariance.*similitude|nombres complexes et isometries|geometrie du plan complexe|"
        r"representation d.un complexe dans le plan|interpretation geometrique des complexes|"
        r"distance entre deux points d.affixes|involution (d.une reflexion)?|composee de|"
        r"decomposition (d.une rotation|en reflexions)|reflexion|isometrie|isometries|"
        r"groupe des isometries|classification des (isometries|symetries)|orbite.*transformation",
        r"nombres complexes ?: approche geometrique",
    ),
    (
        r"complexe|affixe|argument|conjugu|module d.un|racine (carree|cubique)s? d.un.*complexe|"
        r"racines? complexes?|forme (algebrique|trigonometrique|exponentielle)|puissances? de i|"
        r"racines? de l.unite|division par un nombre complexe|multiplication par le conjugue|"
        r"rationalisation d.un quotient complexe|quotient d.affixes|imaginaire pur|"
        r"discriminant complexe|equation (du second degre|complexe).*complexe|nombre complexe racine",
        r"nombres complexes ?: approche algebrique|nombres complexes ?: approche$",
    ),
    # --- Suites ---
    (
        r"\bsuite|recurrence|raison\b|terme general|convergen|point fixe.*suite|"
        r"majoration.*suite|minoration.*suite|encadrement.*suite|monotonie.*suite",
        r"suites? numeriques?",
    ),
    # --- Fonctions génériques (limites/continuité/dérivation/étude/courbes) ---
    (
        r"limite|continuit|deriv|extremum|extrema|tableau de variation|asymptote|branche (infinie|parabolique)|"
        r"point (d.inflexion|anguleux|critique)|tangente(?!.*trigonometr)|sens de variation|"
        r"parite|fonction (composee|affine|constante|rationnelle|homographique|reciproque|"
        r"valeur absolue|impaire|strictement)|croissance compare|forme indetermin|"
        r"domaine de definition|ensemble de definition|courbe representative|"
        r"representation graphique d.une fonction|zero d.une fonction|signe d.une (fonction|derivee)|"
        r"etude (de|complete d.une) fonction|synthese d.une etude de fonction|prolongement par continuite|"
        r"theoreme de la bijection|theoreme des valeurs intermediaires|raccordement de fonctions",
        r"fonctions?|derivees?|courbes? representatives?|etude des fonctions",
    ),
    # --- Logarithme / Exponentielle ---
    (r"logarithm|\bln\b", r"logarithmes?|ln ?neperien"),
    (r"exponentiel", r"exponentielles?"),
    # --- Primitives / Intégrales ---
    (r"primitive", r"primitives?"),
    (r"integral|integration|somme de riemann|relation de chasles", r"integrales?|calcul des integrales"),
    # --- Équations différentielles ---
    (r"equation different|\bedo\b|solution (generale|particuliere)", r"equations? differentielles?"),
    # --- Trigonométrie ---
    (
        r"trigonometri|identite trigonometrique|relation trigonometrique|equation trigonometrique|"
        r"valeurs remarquables de (cos|sin)|tracé? de courbe trigonometrique",
        r"trigonometrie",
    ),
    # --- Probabilités ---
    (
        r"probabilit|loi (binomiale|de probabilite|hypergeometrique)|variable aleatoire|esperance|"
        r"tirage|evenement|equiprobabilit|schema de bernoulli|univers.image|au moins un succes|"
        r"exactement un succes|repetition d.(experiences|epreuves)",
        r"probabilites",
    ),
    # --- Statistiques ---
    (
        r"statistique|effectif|moyenne (arithmetique|geometrique|ponderee|d.une serie)|median|ecart.type|"
        r"variance|histogramme|diagramme circulaire|serie statistique|classe modale|"
        r"tableau (croise|statistique)|nuage de points|ajustement|regression lineaire|"
        r"polygone des effectifs|centre de classe|regroupement de classes",
        r"statistiques?",
    ),
    # --- Dénombrement ---
    (
        r"denombrement|arrangements|combinaisons\b|factorielle|cardinaux d.ensembles|"
        r"principe multiplicatif|inclusion.exclusion",
        r"denombrement",
    ),
    # --- Théorie des graphes ---
    (r"\bgraphe", r"graphes?|theorie des graphes"),
    # --- Arithmétique ---
    (
        r"pgcd|ppmc|divisibilit|diviseur|nombres? premiers?|congruence|division euclidienne(?!.*polyn)|"
        r"bezout|algorithme d.euclide|arithmetique|reste modulo|multiples? de \d|"
        r"petit theoreme de fermat|lemme de gauss|somme de gauss",
        r"arithmetique",
    ),
    # --- Matrices ---
    (
        r"matrice|determinant d.une matrice|diagonalisation|theoreme de cayley|conjugaison matricielle|"
        r"identification (matricielle|de coefficients matriciels)",
        r"matrices et applications lineaires",
    ),
    # --- Espaces vectoriels / applications linéaires (algèbre, pas géométrie du plan) ---
    (
        r"espace vectoriel|sous.espace vectoriel|base (adaptee|orthonorm|du plan|d.un espace|d.un plan)|"
        r"famille (generatrice|libre)|dimension d.un espace|endomorphisme|noyau|image d.un endomorphisme|"
        r"automorphisme|isomorphisme d.espaces|somme directe|combinaison lineaire d.endomorphismes|"
        r"theoreme du rang|valeur propre|vecteur propre|espace propre|projecteur|"
        r"caracterisation de l.image d.un projecteur",
        r"espaces vectoriels",
    ),
    # --- Produit vectoriel / produit mixte ---
    (r"produit vectoriel|produit mixte", r"produit vectoriel"),
    # --- Barycentres ---
    (r"barycentre|isobarycentre", r"barycentres"),
    # --- Transformations affines du plan / applications affines (géométrie, pas algèbre abstraite) ---
    (
        r"application affine|transformation affine|translation(?!.*complexe)|"
        r"homothetie(?!.*vectorielle)|invariant d.une application affine|image d.une courbe par une application affine",
        r"transformations affines du plan|applications lineaires et applications affines",
    ),
    # --- Coniques ---
    (
        r"ellipse|hyperbole|parabole\b|foyer|directrice|excentricit|\bconique",
        r"coniques?",
    ),
    # --- Géométrie analytique du plan / vecteurs du plan ---
    (
        r"\bvecteur|coordonnees (d.un point|cartesiennes|d.intersection|d.un barycentre)|"
        r"droite (parallele|secante|paramétree|passant par)|equation (d.une droite|de droite)|"
        r"pente\b|coefficient directeur|colinearite|non.colinearite|alignement",
        r"geometrie analytique du plan|vecteurs du plan|coordonnees d.un vecteur|equations de droites",
    ),
    # --- Angles inscrits / polygones réguliers / arcs capables ---
    (
        r"angle inscrit|polygone regulier|arc capable|cocyclicit|concyclicit",
        r"angles inscrits|arcs capables|polygones regu",
    ),
    # --- Géométrie dans l'espace ---
    (
        r"sphere|plan (orthogonal|perpendiculaire)|orthogonalite|droite.*plan|intersection.*plan|"
        r"tetraedre|coplanarite|repere affine de l.espace|geometrie analytique dans l.espace|"
        r"geometrie de l.espace|geometrie vectorielle de l.espace",
        r"orthogonalite dans l.espace|geometrie analytique dans|spheres?",
    ),
    # --- Calcul littéral / second degré / équations-inéquations polynomiales (non complexe) ---
    (
        r"factorisation(?!.*complexe)|identites? remarquables?|second degre(?!.*complexe)|"
        r"discriminant(?!.*complexe)|trinome|racine[s]? (carree|d.un polynome)(?!.*complexe)|"
        r"developpement (algebrique|d.un produit)|calcul algebrique|simplification (algebrique|d.expression)|"
        r"polynome(?!.*complexe)|division euclidienne de polyn",
        r"calcul litteral|equations?,? ?inequations?|equations? et inequations?",
    ),
    # --- Thalès (collège/3e) ---
    (r"thales", r"thales"),
]

COMPILED_RULES = [(re.compile(tp), re.compile(sp)) for tp, sp in RULES]


class Command(BaseCommand):
    help = (
        "Passe de curation semi-automatique : rattache les Tag maths (Cameroun) déjà "
        "en base à un Savoir officiel via des règles de correspondance mot-clé, sans "
        "jamais deviner - un tag qui ne matche aucune règle, ou dont plusieurs Savoir "
        "candidats restent après désambiguïsation par l'usage réel (le(s) Cursus des "
        "Question/Lesson qui portent ce tag), reste non rattaché et listé pour revue "
        "manuelle plutôt que d'être forcé sur un savoir probable. Jamais d'écrasement "
        "d'un Tag déjà rattaché (voir catalog.ingestion._link_tags_to_savoir, même "
        "règle). Toujours par --dry-run d'abord."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="N'écrit rien en base, affiche seulement le rapport.")
        parser.add_argument("--country", default="CM", help="Code pays (défaut CM - seul pays avec un référentiel programme aujourd'hui).")
        parser.add_argument("--subject", default="MATHS", help="Code matière (défaut MATHS).")
        parser.add_argument("--verbose-unmapped", action="store_true", help="Détaille chaque tag non rattaché (sinon, juste un décompte par cause).")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        country_code = options["country"]
        subject_code = options["subject"]

        savoirs = list(Savoir.objects.select_related("module").all())
        for s in savoirs:
            s._search_text = _normalize(f"{s.module.titre} {s.intitule}")

        tags = (
            Tag.objects.filter(
                savoir_officiel__isnull=True,
                lessons_as_theme__subject__country__code=country_code,
                lessons_as_theme__subject__code=subject_code,
            )
            .distinct()
            .order_by("name")
        )

        mapped = 0
        no_rule = 0
        no_savoir_for_rule = 0
        ambiguous = Counter()
        ambiguous_detail = []
        per_savoir = Counter()

        for tag in tags:
            normalized_name = _normalize(tag.name)

            tag_pattern_matched = None
            candidates = []
            for tag_re, savoir_re in COMPILED_RULES:
                if tag_re.search(normalized_name):
                    tag_pattern_matched = tag_re.pattern
                    candidates = [s for s in savoirs if savoir_re.search(s._search_text)]
                    if candidates:
                        break

            if tag_pattern_matched is None:
                no_rule += 1
                continue
            if not candidates:
                no_savoir_for_rule += 1
                continue

            if len(candidates) > 1:
                # Désambiguïsation par l'usage réel : à quel(s) Cursus ce tag est-il
                # déjà associé (via les Question/Lesson qui le portent) ? On ne retient
                # que les Savoir dont le Module partage au moins un de ces Cursus.
                used_cursus_ids = (
                    set(tag.lessons_as_theme.values_list("cursus", flat=True))
                    | set(tag.questions_as_theme.values_list("exercise__lesson__cursus", flat=True))
                )
                used_cursus_ids.discard(None)
                if used_cursus_ids:
                    narrowed = [s for s in candidates if s.module.cursus.filter(pk__in=used_cursus_ids).exists()]
                    if len(narrowed) == 1:
                        candidates = narrowed

            if len(candidates) != 1:
                key = f"{len(candidates)} candidats pour la règle {tag_pattern_matched!r}"
                ambiguous[key] += 1
                ambiguous_detail.append(f"{tag.name!r} -> " + ", ".join(f"{s.module.classe}/{s.module.serie_label}/M{s.module.numero}/{s.numero}:{s.intitule}" for s in candidates))
                continue

            savoir = candidates[0]
            per_savoir[str(savoir)] += 1
            mapped += 1
            self.stdout.write(f"{'[dry-run] ' if dry_run else ''}{tag.name!r} -> {savoir.module.classe}/{savoir.module.serie_label or '-'} M{savoir.module.numero} : {savoir}")
            if not dry_run:
                tag.savoir_officiel = savoir
                tag.save(update_fields=["savoir_officiel"])

        total = tags.count()
        unmapped_total = no_rule + no_savoir_for_rule + sum(ambiguous.values())
        self.stdout.write(self.style.SUCCESS(
            f"\n{mapped}/{total} tag(s) rattaché(s)"
            + (" (dry-run, rien n'a été écrit)" if dry_run else "")
            + f". {unmapped_total} non rattaché(s) :"
            f" {no_rule} sans règle applicable, {no_savoir_for_rule} règle sans savoir correspondant, "
            f"{sum(ambiguous.values())} ambigus après désambiguïsation par l'usage.",
        ))
        if ambiguous:
            self.stdout.write(self.style.WARNING("\nCas ambigus par cause :"))
            for cause, count in ambiguous.most_common():
                self.stdout.write(f"  - {cause} : {count}")
            if options["verbose_unmapped"]:
                self.stdout.write(self.style.WARNING("\nDétail des cas ambigus :"))
                for line in ambiguous_detail:
                    self.stdout.write(f"  - {line}")
        if per_savoir:
            self.stdout.write(self.style.SUCCESS("\nRépartition par savoir (top 15) :"))
            for savoir_str, count in per_savoir.most_common(15):
                self.stdout.write(f"  - {savoir_str} : {count}")
