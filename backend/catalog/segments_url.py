"""Les segments d'URL des pages publiques en anglais : `/en/cm/past-papers/x/read` au lieu de `/en/cm/epreuves/x/lire`.

Miroir Python de frontend/src/lib/i18n/segments.ts : même table (segments_url.json, copie de
frontend/src/lib/i18n/segments-url.json - un test échoue si les deux divergent), même algorithme. Le frontend
garde des routes françaises « internes » et ne traduit que l'adresse affichée ; ce module sert à tout ce qui
fabrique une URL publique côté serveur : sitemap, aperçus de liens, liens imprimés dans les PDF.

Un chemin n'est traduit que s'il correspond à une route connue (`patrons`) et seuls ses segments FIXES le
sont : un slug d'épreuve qui s'appellerait « cours » reste « cours ». Un chemin inconnu est rendu tel quel.
"""
import json
from pathlib import Path

_DONNEES = json.loads((Path(__file__).with_name("segments_url.json")).read_text(encoding="utf-8"))

SEGMENTS_EN = _DONNEES["segments"]
PATRONS_INTERNES = _DONNEES["patrons"]
SEGMENTS_FR = {en: fr for fr, en in SEGMENTS_EN.items()}
PREFIXE_EN = "/en"


def _decouper(chemin):
    return [s for s in chemin.split("/") if s]


def _dynamique(segment):
    return segment.startswith(":")


def _patron(patron, vers):
    return [s if (_dynamique(s) or vers == "fr") else SEGMENTS_EN.get(s, s) for s in _decouper(patron)]


_PATRONS_FR = [_patron(p, "fr") for p in PATRONS_INTERNES]
_PATRONS_EN = [_patron(p, "en") for p in PATRONS_INTERNES]


def _correspond(patron, segments):
    return len(patron) == len(segments) and all(_dynamique(p) or p == s for p, s in zip(patron, segments))


def _recomposer(segments, original):
    chemin = "/" + "/".join(segments)
    return chemin + "/" if len(original) > 1 and original.endswith("/") and chemin != "/" else chemin


def _traduire(chemin, patrons, table):
    segments = _decouper(chemin)
    for patron in patrons:
        if _correspond(patron, segments):
            return _recomposer(
                [s if _dynamique(p) else table.get(s, s) for p, s in zip(patron, segments)], chemin,
            )
    return chemin


def chemin_anglais(interne):
    """Chemin interne (français, sans préfixe) -> chemin public anglais, SANS le préfixe /en."""
    return _traduire(interne, _PATRONS_FR, SEGMENTS_EN)


def chemin_interne(anglais):
    """Chemin public anglais (sans préfixe /en) -> chemin interne français. Une forme française est rendue telle quelle."""
    return _traduire(anglais, _PATRONS_EN, SEGMENTS_FR)


def chemin_public(interne, langue):
    """Le chemin public d'une page dans une langue : `("/cm/cours", "en")` -> `/en/cm/lessons`."""
    if langue != "en":
        return interne
    traduit = chemin_anglais(interne)
    return PREFIXE_EN if traduit == "/" else f"{PREFIXE_EN}{traduit}"
