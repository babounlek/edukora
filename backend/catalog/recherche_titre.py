"""
Recherche de titre insensible aux accents, sans extension `unaccent` (la base de test est SQLite).

La liste des épreuves filtrait par `title__icontains` : « mathematique » ne trouvait pas « Mathématiques BEPC
2026 » (test élève 2026-10-24). Le motif ci-dessous remplace chaque voyelle par la classe de ses variantes
accentuées ; il ne sert QUE sur les titres (courts) - le texte des épreuves reste en `icontains`, que les index
trigramme de Lesson.Meta.indexes accélèrent et qu'une expression régulière désactiverait.
"""
import re
import unicodedata

_VARIANTES = {
    "a": "aàâäáã",
    "e": "eéèêë",
    "i": "iîïíì",
    "o": "oôöóòõ",
    "u": "uùûüú",
    "c": "cç",
    "n": "nñ",
    "y": "yÿý",
}


def _sans_accent(caractere):
    return unicodedata.normalize("NFD", caractere)[:1]


def motif_sans_accent(terme):
    """Expression régulière (à passer à `__iregex`) qui reconnaît `terme` avec ou sans accents."""
    morceaux = []
    for caractere in terme.strip():
        base = _sans_accent(caractere).lower()
        variantes = _VARIANTES.get(base)
        morceaux.append(f"[{variantes}]" if variantes else re.escape(caractere))
    return "".join(morceaux)
