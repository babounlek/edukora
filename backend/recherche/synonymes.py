"""
Équivalences de vocabulaire de la recherche : ce qu'un élève écrit et ce que le catalogue dit ne sont pas
toujours les mêmes mots (« cercle » / « disque », « résoudre » / « résolution », « tp »).

Liste ÉCRITE À LA MAIN, volontairement courte et prudente : une équivalence fausse fait remonter des résultats
sans rapport (« aire » / « surface » aurait ramené les surfaces équipotentielles de la physique), une équivalence
manquante coûte seulement un résultat de moins. Elle s'enrichit à partir du journal des recherches sans résultat
(voir RechercheSansResultat, lisible dans l'admin) : un mot qui revient souvent sans rien trouver est un candidat.

Deux sortes d'équivalences :
  - GROUPES : mots interchangeables dans les deux sens. Un mot suivi de « * » est un RADICAL : il couvre tout mot
    qui commence ainsi (« deriv* » : dérivée, dérivation, dériver) et sert de forme de recherche élargie. La
    recherche se faisant déjà par DÉBUT de mot, un radical n'est utile que là où deux mots de la même famille
    divergent avant leur fin (dérivée / dérivation).
  - ABREVIATIONS : sens unique. « tp » cherche aussi « travaux pratiques », mais « travaux pratiques » ne cherche
    pas « tp » - une abréviation courte élargirait sinon la recherche à tout mot qui commence pareil.
"""

import re

from . import texte

GROUPES = (
    ("cercle", "disque"),
    ("resou*", "resolu*"),
    # Familles de mots qui divergent avant leur fin.
    ("deriv*",),
    ("integr*",),
    ("factori*",),
    ("logarithm*",),
    ("trigonometri*",),
    ("radioactiv*",),
    ("continu*",),
    ("converg*",),
    ("diverg*",),
    ("symetri*",),
    ("geometri*",),
    ("demonstr*",),
    ("conjug*",),
    ("multipl*",),
    ("divis*",),
    ("electri*",),
    ("magnet*",),
    ("refraction", "snell"),
    # Orthographe britannique / américaine (le GCE écrit « sulphur », les manuels américains « sulfur »). Les
    # terminaisons -ise / -ize sont reliées par _variantes_orthographe. Écartés : « litre / liter » et
    # « labour / labor », dont la forme américaine commence « literature » et « laboratory ».
    ("colour", "color"),
    ("sulphur", "sulfur"),
    ("aluminium", "aluminum"),
    ("metre", "meter"),
    ("centre", "center"),
    ("grey", "gray"),
    ("fibre", "fiber"),
    ("behaviour", "behavior"),
)

ABREVIATIONS = {
    # Mathématiques
    "ln": ("logarithme neperien",),
    "exp": ("exponentielle",),
    "cos": ("cosinus",),
    "sin": ("sinus",),
    "tan": ("tangente",),
    "lim": ("limite",),
    "vect": ("vecteur",),
    "fct": ("fonction",),
    "eq": ("equation",),
    "trigo": ("trigonometrie",),
    # Matières
    "geo": ("geographie",),
    "hist": ("histoire",),
    "philo": ("philosophie",),
    "litt": ("litterature",),
    "info": ("informatique",),
    "eco": ("economie",),
    "ecm": ("education civique",),
    "eps": ("education physique",),
    "pct": ("physique chimie technologie",),
    # Vie de classe
    "tp": ("travaux pratiques",),
    "dm": ("devoir maison",),
    "compo": ("composition",),
    "redac": ("redaction",),
    "dissert": ("dissertation",),
    # Sciences
    "adn": ("acide desoxyribonucleique",),
    "arn": ("acide ribonucleique",),
}


def _correspond(jeton, membre):
    if membre.endswith("*"):
        return jeton.startswith(membre[:-1])
    return jeton == membre


_IS_IZ = re.compile(r"i([sz])(e|es|ed|ing|ation|ations|er|ers)?$")


def _variantes_orthographe(jeton):
    """L'autre orthographe anglaise d'un mot en -ise / -ize (« neutralise » / « neutralize », « organisation » /
    « organization »), ou d'un radical qui s'y termine (« neutralis » / « neutraliz », voir texte.racine_en)."""
    if len(jeton) < 6:
        return []
    trouve = _IS_IZ.search(jeton)
    if not trouve:
        return []
    autre = "z" if trouve.group(1) == "s" else "s"
    return [jeton[: trouve.start(1)] + autre + jeton[trouve.end(1):]]


def alternatives(jeton):
    """Formes de recherche équivalentes à `jeton` (déjà ramené au singulier approximatif), sans lui-même ni
    doublon - vide quand le mot n'a pas d'équivalent connu. Un jeton d'une seule lettre n'en a jamais :
    « d » ou « a » désignent une série, pas un synonyme."""
    if len(jeton) < 2:
        return []
    trouvees = []

    def ajouter(forme):
        if forme != jeton and forme not in trouvees:
            trouvees.append(forme)

    for groupe in GROUPES:
        if any(_correspond(jeton, membre) for membre in groupe):
            for membre in groupe:
                ajouter(membre.rstrip("*"))
    for forme in ABREVIATIONS.get(jeton, ()):
        ajouter(forme)
    for forme in _variantes_orthographe(jeton):
        ajouter(forme)
    return trouvees


def est_requis(jeton):
    """Un jeton est « requis » (il doit être présent pour qu'un résultat soit retenu) s'il est assez long
    (voir texte.est_requis) OU si c'est une abréviation connue : « tp » est court, mais il veut dire
    « travaux pratiques », et une requête qui n'est que « tp » doit chercher cela."""
    return texte.est_requis(jeton) or jeton in ABREVIATIONS
