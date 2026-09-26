"""
Lecteur d'étude : marques personnelles (compris / signet / note) posées sur les
sections d'un cours ou d'une épreuve - voir access.models.MarqueEtude.
"""
import re

from catalog.models import Lesson

from .models import MarqueEtude

NOTE_MAX = 2000
CLE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,59}$")


class MarqueInvalide(ValueError):
    pass


def _champ(cible):
    return "lesson" if isinstance(cible, Lesson) else "cours"


def enregistrer_marque(user, cible, cle, compris=None, signet=None, note=None):
    """
    Met à jour les champs FOURNIS (None = inchangé) de la marque de `user` sur la
    section `cle` de `cible` (Lesson ou Cours), puis supprime la ligne si plus rien n'y
    reste - un signet retiré sans note ni "compris" ne doit pas laisser une ligne vide
    qui gonflerait le carnet. Renvoie la marque, ou None si elle a disparu.
    """
    if not CLE_RE.match(cle or ""):
        raise MarqueInvalide("Section invalide.")
    if note is not None:
        note = str(note).strip()
        if len(note) > NOTE_MAX:
            raise MarqueInvalide(f"Note trop longue ({NOTE_MAX} caractères maximum).")

    marque, _ = MarqueEtude.objects.get_or_create(user=user, cle=cle, **{_champ(cible): cible})
    if compris is not None:
        marque.compris = bool(compris)
    if signet is not None:
        marque.signet = bool(signet)
    if note is not None:
        marque.note = note

    if not (marque.compris or marque.signet or marque.note):
        marque.delete()
        return None
    marque.save()
    return marque


def marques_du_document(user, cible):
    return MarqueEtude.objects.filter(user=user, **{_champ(cible): cible})
