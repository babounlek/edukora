"""
Le code d'assistance : un identifiant court qu'un élève (ou son parent) peut dicter ou écrire dans
WhatsApp pour que le support retrouve son compte sans lui demander son téléphone ni son e-mail.

Ce n'est PAS un secret ni une preuve d'identité : il ne donne aucun accès, il désigne seulement un
compte pour quelqu'un qui est déjà dans l'admin. Il est donc réversible (l'identifiant en base 36)
avec une clé de contrôle d'un caractère, qui attrape les fautes de recopie, pas les malveillants.
"""

import re

_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_FORMAT = re.compile(r"^EK-([0-9A-Z]+)-([0-9A-Z])$")


def _base36(n):
    if n == 0:
        return "0"
    chiffres = ""
    while n:
        n, reste = divmod(n, 36)
        chiffres = _ALPHABET[reste] + chiffres
    return chiffres


def _controle(corps):
    # Somme pondérée par la position : une inversion de deux caractères change presque toujours le résultat.
    total = sum((i + 1) * _ALPHABET.index(c) for i, c in enumerate(corps))
    return _ALPHABET[total % 36]


def code_pour(user_id):
    corps = _base36(int(user_id))
    return f"EK-{corps}-{_controle(corps)}"


def user_id_depuis_code(code):
    """L'identifiant du compte, ou None si le code est mal formé ou si sa clé de contrôle ne correspond pas."""
    trouve = _FORMAT.match((code or "").strip().upper())
    if not trouve:
        return None
    corps, controle = trouve.groups()
    if _controle(corps) != controle:
        return None
    return int(corps, 36)
