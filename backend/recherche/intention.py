"""
Comprendre ce que l'élève VEUT dire, avant de chercher des mots : « bac c maths 2019 » n'est pas quatre mots à
retrouver dans des titres, c'est un examen (BAC C), une matière (maths) et une année (2019) ; « corrigé » dans
« sujets bac c 2019 corrigés » dit quel TYPE de contenu il attend, il ne figure dans aucun titre.

Sans cela, chaque mot est exigé dans le contenu et une requête naturelle (« bepc 2024 maths corrigé ») ne donne
rien. Ici, ces mots d'intention sont retirés de la recherche par mots et deviennent :
  - des FILTRES (examen/série, matière, année), montrés à l'élève sous forme de pastilles qu'il peut retirer ;
  - des INDICATIONS de type (corrigé, sujet, cours, quiz...), qui n'écartent rien mais passent devant.

Rien n'est jamais deviné en silence : tout ce qui est compris est renvoyé (voir `Intention.en_clair`), et une
interprétation qui ne donne aucun résultat est abandonnée par le moteur (voir moteur.chercher).
"""

from dataclasses import dataclass, field

from catalog.models import Cursus, Subject, resolve_examen_label

from . import synonymes, texte
from .models import TypeResultat

# Mots de la requête, ramenés comme le fait `texte.racine` (« corrigés » -> « corrige », « cours » -> « cour ») :
# les clés ci-dessous sont passées par `_racine` au chargement, jamais écrites à la main au singulier.
_racine = texte.racine

MOTS_EXAMEN = {
    _racine(mot): code
    for mot, code in {
        "bac": "BAC", "baccalaureat": "BAC", "bepc": "BEPC", "brevet": "BEPC", "probatoire": "PROBATOIRE",
        "cap": "CAP", "gce": "GCE",
    }.items()
}

_EPREUVES = (TypeResultat.EPREUVE.value, TypeResultat.INEDITE.value)
MOTS_TYPE = {
    _racine(mot): types
    for mot, types in {
        "corrige": (TypeResultat.EPREUVE.value, TypeResultat.EXERCICE.value),
        "sujet": _EPREUVES,
        "epreuve": _EPREUVES,
        "annale": (TypeResultat.EPREUVE.value,),
        "exercice": (TypeResultat.EXERCICE.value,),
        "cours": (TypeResultat.COURS.value,),
        "lecon": (TypeResultat.COURS.value,),
        "fiche": (TypeResultat.COURS.value,),
        "quiz": (TypeResultat.QUIZ.value,),
        "qcm": (TypeResultat.QUIZ.value,),
        "question": (TypeResultat.QUIZ.value,),
        "theme": (TypeResultat.THEME.value,),
    }.items()
}

# Matières que l'élève nomme, par les mots qu'il emploie (de un à trois). Une matière « famille » couvre
# plusieurs codes : « physique » vaut aussi pour les épreuves de Physique-Chimie (voir
# catalog.models.SUBJECT_FAMILIES, même raisonnement).
_PHYSIQUE_CHIMIE = ("PHYSIQUE_CHIMIE", "PHYSIQUE_CHIMIE_TECH")
_INFORMATIQUE = ("INFORMATIQUE", "PROGRAMMATION", "SYSTEMES_INFORMATION", "RESEAUX_SECURITE")
_ALIAS_BRUTS = {
    ("maths",): ("MATHS",),
    ("math",): ("MATHS",),
    ("mathematiques",): ("MATHS",),
    ("svt",): ("SVT",),
    ("physique", "chimie", "technologie"): ("PHYSIQUE_CHIMIE_TECH",),
    ("pct",): ("PHYSIQUE_CHIMIE_TECH", "PHYSIQUE_CHIMIE"),
    ("physique", "chimie"): ("PHYSIQUE_CHIMIE",),
    ("physique",): ("PHYSIQUE",) + _PHYSIQUE_CHIMIE,
    ("chimie",): ("CHIMIE",) + _PHYSIQUE_CHIMIE,
    ("histoire", "geographie"): ("HISTOIRE_GEO",),
    ("histoire", "geo"): ("HISTOIRE_GEO",),
    ("histoire",): ("HISTOIRE", "HISTOIRE_GEO"),
    ("geographie",): ("GEOGRAPHIE", "HISTOIRE_GEO"),
    ("geo",): ("GEOGRAPHIE", "HISTOIRE_GEO"),
    ("francais",): ("FRANCAIS",),
    ("anglais",): ("ANGLAIS",),
    ("allemand",): ("ALLEMAND",),
    ("espagnol",): ("ESPAGNOL",),
    ("philosophie",): ("PHILOSOPHIE",),
    ("philo",): ("PHILOSOPHIE",),
    ("informatique",): _INFORMATIQUE,
    ("info",): _INFORMATIQUE,
    ("programmation",): ("PROGRAMMATION",),
    ("economie",): ("ECONOMIE",),
    ("eco",): ("ECONOMIE",),
    ("droit",): ("DROIT",),
    ("eps",): ("EPS",),
    ("litterature",): ("LITTERATURE",),
    ("dessin",): ("DESSIN",),
    ("education", "civique"): ("EDUCATION_CIVIQUE",),
    ("ecm",): ("EDUCATION_CIVIQUE",),
}
ALIAS_MATIERES = {tuple(_racine(m) for m in cle): codes for cle, codes in _ALIAS_BRUTS.items()}
LONGUEUR_ALIAS_MAX = max(len(cle) for cle in ALIAS_MATIERES)

ANNEE_MIN, ANNEE_MAX = 1980, 2035
# Dans quel ordre l'élève peut retirer ce qui a été compris : voir Intention.en_clair.
PARTIES = ("cursus", "matiere", "annee", "type")


@dataclass
class Intention:
    restants: list = field(default_factory=list)  # jetons qu'il reste à chercher par mots
    cursus_ids: list = field(default_factory=list)
    cursus_libelle: str = ""
    matiere_codes: list = field(default_factory=list)
    matiere_libelle: str = ""
    annees: list = field(default_factory=list)
    types: tuple = ()
    mots_type: list = field(default_factory=list)

    def filtres(self):
        return bool(self.cursus_ids or self.matiere_codes or self.annees)

    def vide(self):
        return not (self.filtres() or self.types)

    def en_clair(self):
        """Ce qui a été compris, pour l'afficher : chaque `partie` est ce que `sans=` permet de retirer."""
        return {
            "cursus": {"libelle": self.cursus_libelle, "ids": self.cursus_ids} if self.cursus_ids else None,
            "matiere": {"libelle": self.matiere_libelle, "codes": self.matiere_codes} if self.matiere_codes else None,
            "annees": self.annees,
            "types": list(self.types),
            "mots_type": self.mots_type,
        }


def _cursus_et_series(jetons, pays, consommes):
    """Un mot d'examen (« bac », « bepc ») suivi, ou non, de séries (« c », « d », « ti ») : renvoie
    (ids des cursus, libellé) et marque les mots consommés. Sans série, tous les cursus de cet examen."""
    position = next((i for i, j in enumerate(jetons) if j in MOTS_EXAMEN), None)
    if position is None:
        return [], ""
    code = MOTS_EXAMEN[jetons[position]]
    cursus = [
        c for c in Cursus.objects.filter(country=pays, examen=code).select_related("series", "country")
    ]
    if not cursus:
        return [], ""
    # Seules les séries courtes (A, C, D, E, TI) s'écrivent en une lettre ou deux : les spécialités techniques
    # (« comptabilité gestion »...) ne se confondent pas avec un mot de la requête.
    par_serie = {c.series.code.lower(): c for c in cursus if c.series_id and len(c.series.code) <= 3}
    consommes.add(position)
    choisis, suivant = [], position + 1
    while suivant < len(jetons) and jetons[suivant] in par_serie:
        choisis.append(par_serie[jetons[suivant]])
        consommes.add(suivant)
        suivant += 1
    examen = resolve_examen_label(pays, code)
    if choisis:
        return [c.id for c in choisis], f"{examen} {', '.join(c.series.code for c in choisis)}"
    return [c.id for c in cursus], examen


def _matiere(jetons, pays, consommes):
    """La première matière nommée (le plus long alias d'abord : « physique chimie » avant « physique »)."""
    existantes = {s.code: s.label for s in Subject.objects.filter(country=pays)}
    for debut in range(len(jetons)):
        if debut in consommes:
            continue
        for taille in range(min(LONGUEUR_ALIAS_MAX, len(jetons) - debut), 0, -1):
            plage = range(debut, debut + taille)
            if any(i in consommes for i in plage):
                continue
            codes = ALIAS_MATIERES.get(tuple(jetons[i] for i in plage))
            gardes = [c for c in (codes or ()) if c in existantes]
            if not gardes:
                continue
            consommes.update(plage)
            libelle = existantes[gardes[0]] if len(gardes) == 1 else " ".join(jetons[i] for i in plage).capitalize()
            return gardes, libelle
    return [], ""


def analyser(jetons, pays, sans=frozenset()):
    """
    Sépare les `jetons` d'une requête (déjà normalisés, au singulier approximatif) en intention et mots à
    chercher. `sans` : parties à NE PAS interpréter (voir PARTIES) - l'élève a retiré la pastille correspondante,
    le mot redevient un mot comme un autre.
    """
    consommes = set()
    intention = Intention()

    if "annee" not in sans:
        for i, jeton in enumerate(jetons):
            if jeton.isdigit() and len(jeton) == 4 and ANNEE_MIN <= int(jeton) <= ANNEE_MAX:
                intention.annees.append(int(jeton))
                consommes.add(i)
    if "cursus" not in sans:
        intention.cursus_ids, intention.cursus_libelle = _cursus_et_series(jetons, pays, consommes)
    if "matiere" not in sans:
        intention.matiere_codes, intention.matiere_libelle = _matiere(jetons, pays, consommes)

    # Les mots de TYPE (« corrigé », « cours ») ne sont retirés que s'il reste autre chose à chercher : une
    # requête qui n'est QUE « cours » cherche le mot « cours ».
    types, mots_type = [], []
    if "type" not in sans:
        # « examen blanc » : comme « sujet zéro », une origine d'épreuve écrite dans le titre - le mot reste à
        # chercher, on indique seulement qu'on veut des épreuves.
        if "blanc" in jetons:
            types.extend(t for t in _EPREUVES if t not in types)
        for i, jeton in enumerate(jetons):
            if i in consommes or jeton not in MOTS_TYPE:
                continue
            # « sujet zéro » est une origine d'épreuve, écrite telle quelle dans l'index : les deux mots restent
            # à chercher (ils sont dans le titre), et l'on indique seulement qu'on veut des épreuves.
            if jeton == _racine("sujet") and i + 1 < len(jetons) and jetons[i + 1] == "zero":
                types.extend(t for t in _EPREUVES if t not in types)
                continue
            types.extend(t for t in MOTS_TYPE[jeton] if t not in types)
            mots_type.append(jeton)
            consommes.add(i)

    restants = [j for i, j in enumerate(jetons) if i not in consommes]
    reste_utile = any(synonymes.est_requis(j) for j in restants)
    if types and not (reste_utile or intention.filtres()):
        # Rien d'autre à chercher : « cours », « quiz »... redeviennent des mots.
        types, mots_type = [], []
        restants = [j for i, j in enumerate(jetons) if i not in consommes or jetons[i] in MOTS_TYPE]
    intention.restants = restants
    intention.types = tuple(types)
    intention.mots_type = mots_type
    return intention
