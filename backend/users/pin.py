"""
Codes PIN à 4 chiffres : un par profil (enfant) et un « PIN parent » par compte.

Un PIN à 4 chiffres arrête un frère ou une sœur curieux, pas un attaquant déterminé :
c'est le bon niveau pour ce besoin (comme les profils protégés d'un compte de streaming).
Il est donc stocké haché (jamais en clair), vérifié côté serveur, et protégé contre les
essais en rafale par un blocage temporaire après quelques erreurs.
"""

import re
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

PIN_RE = re.compile(r"^\d{4}$")
MAX_ECHECS = 5
BLOCAGE = timedelta(minutes=5)


class PinInvalide(Exception):
    pass


class PinBloque(Exception):
    def __init__(self, secondes):
        self.secondes = secondes
        super().__init__(f"Trop d'essais. Réessaie dans {max(1, (secondes + 59) // 60)} min.")


class _Champs:
    def __init__(self, hash_, echecs, bloque):
        self.hash, self.echecs, self.bloque = hash_, echecs, bloque


PROFIL = _Champs("pin_hash", "pin_echecs", "pin_bloque_jusqua")
PARENT = _Champs("pin_parent_hash", "pin_parent_echecs", "pin_parent_bloque_jusqua")


def format_valide(pin):
    return isinstance(pin, str) and bool(PIN_RE.match(pin))


def est_defini(obj, champs):
    return bool(getattr(obj, champs.hash))


def definir(obj, champs, pin):
    if not format_valide(pin):
        raise ValueError("Le code doit contenir exactement 4 chiffres.")
    setattr(obj, champs.hash, make_password(pin))
    setattr(obj, champs.echecs, 0)
    setattr(obj, champs.bloque, None)
    obj.save(update_fields=[champs.hash, champs.echecs, champs.bloque])


def effacer(obj, champs):
    setattr(obj, champs.hash, "")
    setattr(obj, champs.echecs, 0)
    setattr(obj, champs.bloque, None)
    obj.save(update_fields=[champs.hash, champs.echecs, champs.bloque])


def verifier(obj, champs, pin):
    """Lève PinBloque si le blocage court, PinInvalide si le code est faux ; retourne None sinon."""
    maintenant = timezone.now()
    bloque = getattr(obj, champs.bloque)
    if bloque is not None and bloque > maintenant:
        raise PinBloque(int((bloque - maintenant).total_seconds()))

    if format_valide(pin) and check_password(pin, getattr(obj, champs.hash)):
        if getattr(obj, champs.echecs) or bloque is not None:
            setattr(obj, champs.echecs, 0)
            setattr(obj, champs.bloque, None)
            obj.save(update_fields=[champs.echecs, champs.bloque])
        return

    echecs = getattr(obj, champs.echecs) + 1
    if echecs >= MAX_ECHECS:
        setattr(obj, champs.echecs, 0)
        setattr(obj, champs.bloque, maintenant + BLOCAGE)
    else:
        setattr(obj, champs.echecs, echecs)
    obj.save(update_fields=[champs.echecs, champs.bloque])
    raise PinInvalide("Code incorrect.")
