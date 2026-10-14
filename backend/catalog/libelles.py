import re


def joindre_fr(items):
    """Joint des éléments à la française : "C", "C et E", "C, D et E"."""
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return " et ".join(items)
    return f"{', '.join(items[:-1])} et {items[-1]}"


# Séries du GCE : pas de « Série X » dans le sous-système anglophone, la branche technique
# s'écrit « Technical » (« GCE A Level - Technical »).
LIBELLES_SERIES_GCE = {"GCE_TECHNICAL": "Technical"}


def libelle_series(codes):
    """« Série C » ou « Séries C, D et E » - le mot s'accorde ; None s'il n'y a aucune série."""
    codes = list(codes)
    if not codes:
        return None
    if all(c in LIBELLES_SERIES_GCE for c in codes):
        return " / ".join(LIBELLES_SERIES_GCE[c] for c in codes)
    return f"{'Séries' if len(codes) > 1 else 'Série'} {joindre_fr(codes)}"


def matiere_dans_titre(titre, matiere):
    """True si le titre nomme déjà la matière (« Mathématiques BAC C et E 2002 »)."""
    return bool(matiere) and matiere.casefold() in titre.casefold()


def public_dans_titre(titre, cursus_iterable):
    """True si le titre dit déjà le public visé : chaque examen et chaque série du cursus y figurent
    (« … BAC C, D et E 2026 », « … Probatoire C et E – Épreuve inédite n°2 ») - l'en-tête d'un PDF
    n'a alors pas à le répéter dessous."""
    cursus = list(cursus_iterable)
    if not cursus:
        return False
    texte = titre.casefold()
    if not all(c.display_examen().casefold() in texte for c in cursus):
        return False
    return all(re.search(rf"\b{re.escape(c.series.code)}\b", titre) for c in cursus if c.series)


def libelle_cursus(cursus_iterable):
    """Le public visé d'une épreuve, sans répéter l'examen : « BAC - Séries C, D, E et TI ».

    Les cursus sont regroupés par examen (ordre de première apparition conservé, doublons
    écartés) : une seule série donne « BAC - Série C », un cursus sans série reste « BEPC »,
    plusieurs examens se séparent par « · » (« Probatoire - Séries C et D · BAC - Série C »).
    """
    groupes = {}
    for c in cursus_iterable:
        codes = groupes.setdefault(c.display_examen(), [])
        if c.series and c.series.code not in codes:
            codes.append(c.series.code)
    morceaux = []
    for examen, codes in groupes.items():
        series = libelle_series(codes)
        morceaux.append(f"{examen} - {series}" if series else examen)
    return " · ".join(morceaux)
