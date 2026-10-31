"""Référentiel du « devrait exister » (§4.3 du prompt).

GCE : les matières et codes officiels du Board (miroir de `CODES_OFFICIELS_GCE`, backend/catalog/models.py ;
un test vérifie que les deux restent synchrones). Francophone : pas de liste officielle consultable, la grille
se déduit des années réellement observées (voir `grille_francophone`).
"""
import re

CODES_OFFICIELS_GCE = {
    "GCE_ACCOUNTING": {"GCE_OL": "0505", "GCE_AL": "0705"},
    "GCE_BIOLOGY": {"GCE_OL": "0510", "GCE_AL": "0710"},
    "GCE_CHEMISTRY": {"GCE_OL": "0515", "GCE_AL": "0715"},
    "GCE_COMMERCE": {"GCE_OL": "0520"},
    "GCE_ECONOMICS": {"GCE_OL": "0525", "GCE_AL": "0725"},
    "GCE_ENGLISH": {"GCE_OL": "0530", "GCE_AL": "0730"},
    "GCE_LITERATURE": {"GCE_OL": "0535", "GCE_AL": "0735"},
    "GCE_CINEMATIC_ART": {"GCE_AL": "0736"},
    "GCE_FOOD_NUTRITION": {"GCE_OL": "0540", "GCE_AL": "0740"},
    "GCE_FRENCH": {"GCE_OL": "0545", "GCE_AL": "0745"},
    "GCE_SBE_FRENCH": {"GCE_OL": "0546", "GCE_AL": "0746"},
    "GCE_GEOGRAPHY": {"GCE_OL": "0550", "GCE_AL": "0750"},
    "GCE_GEOLOGY": {"GCE_OL": "0555", "GCE_AL": "0755"},
    "GCE_HISTORY": {"GCE_OL": "0560", "GCE_AL": "0760"},
    "GCE_CITIZENSHIP": {"GCE_OL": "0562"},
    "GCE_HUMAN_BIOLOGY": {"GCE_OL": "0565"},
    "GCE_MATHS": {"GCE_OL": "0570"},
    "GCE_ADD_MATHS": {"GCE_OL": "0575"},
    "GCE_PHYSICS": {"GCE_OL": "0580", "GCE_AL": "0780"},
    "GCE_RELIGION": {"GCE_OL": "0585", "GCE_AL": "0785"},
    "GCE_LOGIC": {"GCE_OL": "0590"},
    "GCE_COMPUTER_SCI": {"GCE_OL": "0595", "GCE_AL": "0795"},
    "GCE_PM_MECHANICS": {"GCE_AL": "0765"},
    "GCE_PM_STATISTICS": {"GCE_AL": "0770"},
    "GCE_FURTHER_MATHS": {"GCE_AL": "0775"},
    "GCE_PHILOSOPHY": {"GCE_AL": "0790"},
    "GCE_ICT": {"GCE_AL": "0796"},
}

# Période de référence par défaut (§4.3) ; les années antérieures sont comptées à part (D3).
PERIODE_DEFAUT = (2019, 2025)
SESSION_EN_COURS = 2026

# D5 : hors périmètre et hors priorité, ni cherchés ni comptés dans les taux de couverture.
HORS_PERIMETRE = ("LCN", "LANGUES_NATIONALES", "CHINOIS", "ARABE", "DESSIN", "MUSIQUE", "TVEE")

# Matières que le corpus range sous un autre code selon l'épreuve : une cellule attendue est satisfaite si l'une
# des matières équivalentes est présente (même examen, série, année). Histoire et Géographie sont deux matières
# distinctes ; « HISTOIRE_GEO » n'existe que pour une épreuve réellement combinée.
EQUIVALENCES = {
    "HISTOIRE_GEO": ("HISTOIRE", "GEOGRAPHIE"),
    "HISTOIRE": ("HISTOIRE_GEO",),
    "GEOGRAPHIE": ("HISTOIRE_GEO",),
    "SVT": ("SCIENCES",),
    "SCIENCES": ("SVT",),
}

# Matières GCE dont le P3 est pratique : comptées à part (sujets du jour et spécimens souvent absents).
P3_PRATIQUES = {
    "GCE_BIOLOGY", "GCE_CHEMISTRY", "GCE_PHYSICS", "GCE_GEOLOGY", "GCE_ICT", "GCE_COMPUTER_SCI",
    "GCE_FOOD_NUTRITION",
}


def matieres_gce(niveau):
    """Codes de matière attendus à un niveau (GCE_OL ou GCE_AL), selon la liste du Board."""
    return sorted(m for m, codes in CODES_OFFICIELS_GCE.items() if niveau in codes)


def code_board(matiere, niveau):
    return CODES_OFFICIELS_GCE.get(matiere, {}).get(niveau)


def synchrone_avec_le_code(chemin_models):
    """Vrai si ce miroir est identique à CODES_OFFICIELS_GCE de backend/catalog/models.py."""
    with open(chemin_models, encoding="utf-8") as fh:
        source = fh.read()
    bloc = re.search(r"CODES_OFFICIELS_GCE = \{(.*?)\n\}", source, re.S)
    if not bloc:
        return False
    trouves = {}
    for m in re.finditer(r'"(GCE_[A-Z_]+)": \{([^}]*)\}', bloc.group(1)):
        trouves[m.group(1)] = dict(re.findall(r'"(GCE_[OA]L)": "(\d{4})"', m.group(2)))
    return trouves == CODES_OFFICIELS_GCE


def hors_perimetre(matiere):
    code = str(matiere or "").upper()
    return any(code == m or code.startswith(m + "_") for m in HORS_PERIMETRE)


def grille_francophone(observations, periode=PERIODE_DEFAUT):
    """
    Déduit les cellules attendues du sous-système francophone.

    `observations` : itérable de (examen, serie, matiere, annee) pour les épreuves OFFICIELLES.
    Une clé (examen, serie, matiere) est « attendue » pour chaque année de la période si elle a été observée
    sur au moins deux années de cette période (jamais une série ou un intitulé supposé équivalent d'un autre).
    Les années attendues vont de `periode[0]` à la session en cours incluse.
    Retourne l'ensemble des (examen, serie, matiere, annee) attendus.
    """
    debut, fin = periode
    par_cle = {}
    for examen, serie, matiere, annee in observations:
        if annee and debut <= annee <= SESSION_EN_COURS:
            par_cle.setdefault((examen, serie, matiere), set()).add(annee)
    attendus = set()
    for (examen, serie, matiere), annees in par_cle.items():
        if len({a for a in annees if debut <= a <= fin}) >= 2:
            for a in range(debut, SESSION_EN_COURS + 1):
                attendus.add((examen, serie, matiere, a))
    return attendus
