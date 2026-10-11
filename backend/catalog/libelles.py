def joindre_fr(items):
    """Joint des éléments à la française : "C", "C et E", "C, D et E"."""
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return " et ".join(items)
    return f"{', '.join(items[:-1])} et {items[-1]}"


def libelle_series(codes):
    """« Série C » ou « Séries C, D et E » - le mot s'accorde ; None s'il n'y a aucune série."""
    codes = list(codes)
    if not codes:
        return None
    return f"{'Séries' if len(codes) > 1 else 'Série'} {joindre_fr(codes)}"


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
