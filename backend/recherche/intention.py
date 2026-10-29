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
from itertools import product

from catalog.models import EQUIVALENTS_GCE, Cursus, Subject, resolve_examen_label

from . import synonymes, texte
from .models import TypeResultat

# Mots de la requête, ramenés comme le fait `texte.racine` (« corrigés » -> « corrige », « cours » -> « cour ») :
# les clés ci-dessous sont passées par `_racine` au chargement, jamais écrites à la main au singulier.
_racine = texte.racine


def _formes(mot):
    """Les radicaux que ce mot peut prendre dans une requête : celui du français (`texte.racine`) et celui de
    l'anglais (`texte.racine_en`, voir moteur._analyser) - la requête n'en a subi qu'un, selon sa langue."""
    return {_racine(mot), texte.racine_en(mot)}


# Chaque mot désigne un TUPLE de codes d'examen : « gce » seul vaut pour les deux niveaux du GCE,
# « ordinary » / « advanced » (ou « olevel » / « alevel » écrits d'un bloc) pour un seul.
MOTS_EXAMEN = {
    forme: codes
    for mot, codes in {
        "bac": ("BAC",), "baccalaureat": ("BAC",), "bepc": ("BEPC",), "brevet": ("BEPC",),
        "probatoire": ("PROBATOIRE",), "cap": ("CAP",),
        "gce": ("GCE_OL", "GCE_AL"),
        "ordinary": ("GCE_OL",), "olevel": ("GCE_OL",),
        "advanced": ("GCE_AL",), "alevel": ("GCE_AL",),
    }.items()
    for forme in _formes(mot)
}

# « o level » / « a level » s'écrivent en deux mots (« o-level » aussi : la ponctuation saute) : « o » et « a » seuls
# sont des séries (« bac a »), ils ne désignent un GCE que suivis de « level ». Même chose pour « ordinary level ».
_NIVEAUX_GCE = {"o": ("GCE_OL",), "ordinary": ("GCE_OL",), "a": ("GCE_AL",), "advanced": ("GCE_AL",)}

_EPREUVES = (TypeResultat.EPREUVE.value, TypeResultat.INEDITE.value)
MOTS_TYPE = {
    forme: types
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
    for forme in _formes(mot)
}

# Mots de type de l'anglais, appliqués SEULEMENT à une recherche en anglais (voir analyser) : « solution » est aussi
# un mot français de chimie (« solution tampon »), qu'il ne faut jamais prendre pour « corrigé ». « paper » reste un
# mot à chercher quand un numéro le suit (« paper 2 » est dans les titres, voir analyser).
MOTS_TYPE_EN = {
    forme: types
    for mot, types in {
        "solution": (TypeResultat.EPREUVE.value, TypeResultat.EXERCICE.value),
        "past": (TypeResultat.EPREUVE.value,),
        "paper": _EPREUVES,
        "exam": _EPREUVES,
        "mock": _EPREUVES,
        "lesson": (TypeResultat.COURS.value,),
        "course": (TypeResultat.COURS.value,),
        "exercise": (TypeResultat.EXERCICE.value,),
        "mcq": (TypeResultat.QUIZ.value,),
        "topic": (TypeResultat.THEME.value,),
    }.items()
    for forme in _formes(mot)
}
_MOT_PAPER = _formes("paper")

# Matières que l'élève nomme, par les mots qu'il emploie (de un à trois). Une matière « famille » couvre
# plusieurs codes : « physique » vaut aussi pour les épreuves de Physique-Chimie (voir
# catalog.models.SUBJECT_FAMILIES, même raisonnement).
_PHYSIQUE_CHIMIE = ("PHYSIQUE_CHIMIE", "PHYSIQUE_CHIMIE_TECH")
_INFORMATIQUE = ("INFORMATIQUE", "PROGRAMMATION", "SYSTEMES_INFORMATION", "RESEAUX_SECURITE")
_ALIAS_BRUTS = {
    ("maths",): ("MATHS",),
    ("math",): ("MATHS",),
    ("mathematiques",): ("MATHS",),
    ("svt",): ("SVT", "SCIENCES"),
    ("sciences",): ("SCIENCES", "SVT"),
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

# Matières nommées en anglais, comprises SEULEMENT dans une recherche en anglais (voir analyser) : « bio » ou « econ »
# changeraient sinon le sens de requêtes françaises (« bio » est aussi le début de « biochimie »). La matière
# anglaise est la JUMELLE de la française (voir EQUIVALENTS_GCE, ajoutée plus bas) : « physics » désigne Physique ET
# Physics, et le filtre de langue fait le tri.
_ALIAS_EN_BRUTS = {
    ("mathematics",): ("MATHS",),
    ("physics",): ("PHYSIQUE",) + _PHYSIQUE_CHIMIE,
    ("phys",): ("PHYSIQUE",) + _PHYSIQUE_CHIMIE,
    ("chemistry",): ("CHIMIE",) + _PHYSIQUE_CHIMIE,
    ("chem",): ("CHIMIE",) + _PHYSIQUE_CHIMIE,
    ("biology",): ("SVT", "SCIENCES"),
    ("bio",): ("SVT", "SCIENCES"),
    ("history",): ("HISTOIRE", "HISTOIRE_GEO"),
    ("geography",): ("GEOGRAPHIE", "HISTOIRE_GEO"),
    ("geog",): ("GEOGRAPHIE", "HISTOIRE_GEO"),
    ("english",): ("ANGLAIS",),
    ("french",): ("FRANCAIS",),
    ("economics",): ("ECONOMIE",),
    ("econ",): ("ECONOMIE",),
    ("accounting",): ("ECONOMIE",),
    ("commerce",): ("ECONOMIE",),
    ("philosophy",): ("PHILOSOPHIE",),
    ("logic",): ("PHILOSOPHIE",),
    ("literature",): ("LITTERATURE",),
    ("computer", "science"): _INFORMATIQUE,
    ("ict",): _INFORMATIQUE,
    ("citizenship",): ("EDUCATION_CIVIQUE",),
    ("technical", "drawing"): ("DESSIN",),
}

# Les matières GCE (voir catalog.models.EQUIVALENTS_GCE) rejoignent les codes de leur jumelle francophone : « maths »
# vaut pour MATHS et pour les Mathematics du GCE. Le filtre de langue du moteur dit lesquelles on voit.
_JUMELLES_GCE = {}
for _gce, _fr in EQUIVALENTS_GCE.items():
    _JUMELLES_GCE.setdefault(_fr, []).append(_gce)


def _avec_jumelles(alias):
    return {cle: codes + tuple(g for c in codes for g in _JUMELLES_GCE.get(c, ()) if g not in codes) for cle, codes in alias.items()}


def _cles_alias(mots):
    """Toutes les clés qu'un alias à plusieurs mots peut prendre selon le radical appliqué à chaque mot."""
    return {tuple(combinaison) for combinaison in product(*(sorted(_formes(m)) for m in mots))}


def _table_alias(alias):
    return {cle_racine: codes for cle, codes in _avec_jumelles(alias).items() for cle_racine in _cles_alias(cle)}


ALIAS_MATIERES = _table_alias(_ALIAS_BRUTS)
ALIAS_MATIERES_EN = _table_alias(_ALIAS_EN_BRUTS)
LONGUEUR_ALIAS_MAX = max(len(cle) for cle in {**ALIAS_MATIERES, **ALIAS_MATIERES_EN})

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


def _position_examen(jetons):
    """(position, codes d'examen, nombre de mots) du premier mot d'examen, ou None. « gce » seul vaut pour les deux
    niveaux ; « gce o level », « o level », « a level », « ordinary level » en nomment un seul (et consomment
    « level », que les titres écrivent aussi : « Chemistry GCE O Level 2020 »)."""
    for i, jeton in enumerate(jetons):
        suivants = jetons[i + 1 : i + 3]
        if jeton in MOTS_EXAMEN:
            codes, longueur = MOTS_EXAMEN[jeton], 1
            # « gce o level » : le niveau précise lequel des deux GCE.
            if jeton == "gce" and len(suivants) == 2 and suivants[0] in _NIVEAUX_GCE and suivants[1] == "level":
                return i, _NIVEAUX_GCE[suivants[0]], 3
            # « ordinary level » / « advanced level » : « level » fait partie du nom.
            if suivants[:1] == ["level"] and jeton in _NIVEAUX_GCE:
                return i, codes, 2
            return i, codes, longueur
        if jeton in ("o", "a") and suivants[:1] == ["level"]:
            return i, _NIVEAUX_GCE[jeton], 2
    return None


def _cursus_et_series(jetons, pays, consommes):
    """Un mot d'examen (« bac », « bepc ») suivi, ou non, de séries (« c », « d », « ti ») : renvoie
    (ids des cursus, libellé) et marque les mots consommés. Sans série, tous les cursus de cet examen."""
    trouve = _position_examen(jetons)
    if trouve is None:
        return [], ""
    position, codes, longueur = trouve
    cursus = [
        c for c in Cursus.objects.filter(country=pays, examen__in=codes).select_related("series", "country")
    ]
    if not cursus:
        return [], ""
    # Seules les séries courtes (A, C, D, E, TI) s'écrivent en une lettre ou deux : les spécialités techniques
    # (« comptabilité gestion »...) ne se confondent pas avec un mot de la requête.
    par_serie = {c.series.code.lower(): c for c in cursus if c.series_id and len(c.series.code) <= 3}
    consommes.update(range(position, position + longueur))
    choisis, suivant = [], position + longueur
    while suivant < len(jetons) and jetons[suivant] in par_serie:
        choisis.append(par_serie[jetons[suivant]])
        consommes.add(suivant)
        suivant += 1
    # Un mot qui couvre deux niveaux (« gce ») ne peut pas prendre le libellé d'un seul des deux.
    examen = resolve_examen_label(pays, codes[0]) if len(codes) == 1 else "GCE"
    if choisis:
        return [c.id for c in choisis], f"{examen} {', '.join(c.series.code for c in choisis)}"
    return [c.id for c in cursus], examen


def _libelle_matiere(gardes, sujets, langue, mots):
    """Le libellé de la pastille « matière ». Une matière et ses jumelles GCE (« maths » : Mathématiques et
    Mathematics) ne font qu'une : on prend le nom de celle de la langue de l'interface (« Mathematics » en anglais),
    sinon celui de la française. Plusieurs matières distinctes (« physique » : Physique et Physique-Chimie) :
    le mot de l'élève lui-même."""
    base = gardes[0]
    if all(EQUIVALENTS_GCE.get(c) == base for c in gardes[1:]):
        dans_la_langue = [c for c in gardes if sujets[c][1] == langue] if langue else []
        return sujets[(dans_la_langue or [base])[0]][0]
    de_la_langue = [c for c in gardes if sujets[c][1] == langue] if langue else []
    if len(de_la_langue) == 1:
        return sujets[de_la_langue[0]][0]
    return " ".join(mots).capitalize()


def _matiere(jetons, pays, consommes, langue=None):
    """La première matière nommée (le plus long alias d'abord : « physique chimie » avant « physique »)."""
    sujets = {s.code: (s.label, s.langue) for s in Subject.objects.filter(country=pays)}
    alias = {**ALIAS_MATIERES, **ALIAS_MATIERES_EN} if langue == "en" else ALIAS_MATIERES
    for debut in range(len(jetons)):
        if debut in consommes:
            continue
        for taille in range(min(LONGUEUR_ALIAS_MAX, len(jetons) - debut), 0, -1):
            plage = range(debut, debut + taille)
            if any(i in consommes for i in plage):
                continue
            codes = alias.get(tuple(jetons[i] for i in plage))
            gardes = [c for c in (codes or ()) if c in sujets]
            if not gardes:
                continue
            consommes.update(plage)
            return gardes, _libelle_matiere(gardes, sujets, langue, [jetons[i] for i in plage])
    return [], ""


def analyser(jetons, pays, sans=frozenset(), langue=None):
    """
    Sépare les `jetons` d'une requête (déjà normalisés, au singulier approximatif) en intention et mots à
    chercher. `sans` : parties à NE PAS interpréter (voir PARTIES) - l'élève a retiré la pastille correspondante,
    le mot redevient un mot comme un autre. `langue` : celle de la recherche ; en anglais, les mots de type
    (« lesson », « past papers »...) et les matières nommées en anglais (« chem », « bio ») sont aussi compris.
    """
    mots_type_connus = {**MOTS_TYPE, **MOTS_TYPE_EN} if langue == "en" else MOTS_TYPE
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
        intention.matiere_codes, intention.matiere_libelle = _matiere(jetons, pays, consommes, langue)

    # Les mots de TYPE (« corrigé », « cours ») ne sont retirés que s'il reste autre chose à chercher : une
    # requête qui n'est QUE « cours » cherche le mot « cours ».
    types, mots_type = [], []
    if "type" not in sans:
        # « examen blanc » : comme « sujet zéro », une origine d'épreuve écrite dans le titre - le mot reste à
        # chercher, on indique seulement qu'on veut des épreuves.
        if "blanc" in jetons:
            types.extend(t for t in _EPREUVES if t not in types)
        for i, jeton in enumerate(jetons):
            if i in consommes or jeton not in mots_type_connus:
                continue
            # « sujet zéro » est une origine d'épreuve, écrite telle quelle dans l'index : les deux mots restent
            # à chercher (ils sont dans le titre), et l'on indique seulement qu'on veut des épreuves.
            if jeton == _racine("sujet") and i + 1 < len(jetons) and jetons[i + 1] == "zero":
                types.extend(t for t in _EPREUVES if t not in types)
                continue
            # « paper 2 » : le mot est dans les titres (« Chemistry GCE O Level 2020 - Paper 2 »), il reste à chercher.
            if jeton in _MOT_PAPER and i + 1 < len(jetons) and jetons[i + 1].isdigit() and len(jetons[i + 1]) <= 2:
                types.extend(t for t in _EPREUVES if t not in types)
                continue
            types.extend(t for t in mots_type_connus[jeton] if t not in types)
            mots_type.append(jeton)
            consommes.add(i)

    restants = [j for i, j in enumerate(jetons) if i not in consommes]
    reste_utile = any(synonymes.est_requis(j) for j in restants)
    if types and not (reste_utile or intention.filtres()):
        # Rien d'autre à chercher : « cours », « quiz »... redeviennent des mots.
        types, mots_type = [], []
        restants = [j for i, j in enumerate(jetons) if i not in consommes or jetons[i] in mots_type_connus]
    intention.restants = restants
    intention.types = tuple(types)
    intention.mots_type = mots_type
    return intention
