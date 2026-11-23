"""
Lecteur d'étude : marques personnelles (compris / signet / note) posées sur les
sections d'un cours ou d'une épreuve - voir access.models.MarqueEtude.
"""
import re
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from catalog.models import Lesson
from quiz.services import LEITNER_INTERVALS_JOURS

from .models import MarqueEtude, NoteLibre

NOTE_MAX = 2000
CLE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,59}$")


class MarqueInvalide(ValueError):
    pass


def _champ(cible):
    return "lesson" if isinstance(cible, Lesson) else "cours"


def enregistrer_marque(profil, cible, cle, compris=None, signet=None, note=None):
    """
    Met à jour les champs FOURNIS (None = inchangé) de la marque de `profil` sur la
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

    marque, _ = MarqueEtude.objects.get_or_create(profil=profil, cle=cle, **{_champ(cible): cible})
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


def marques_du_document(profil, cible):
    return MarqueEtude.objects.filter(profil=profil, **{_champ(cible): cible})


# --- Notes libres (rattachées à une matière) et révision des notes ---

CITATION_MAX = 1000
A_REVOIR_MAX = 20
NOUVELLES_PAR_JOUR = 5


def creer_note_libre(profil, subject, note, citation=""):
    note = str(note or "").strip()
    citation = str(citation or "").strip()
    if not note:
        raise MarqueInvalide("La note est vide.")
    if len(note) > NOTE_MAX:
        raise MarqueInvalide(f"Note trop longue ({NOTE_MAX} caractères maximum).")
    if len(citation) > CITATION_MAX:
        citation = citation[:CITATION_MAX]
    return NoteLibre.objects.create(profil=profil, subject=subject, note=note, citation=citation)


def modifier_note_libre(note_libre, note):
    note = str(note or "").strip()
    if not note:
        raise MarqueInvalide("La note est vide.")
    if len(note) > NOTE_MAX:
        raise MarqueInvalide(f"Note trop longue ({NOTE_MAX} caractères maximum).")
    note_libre.note = note
    note_libre.save(update_fields=["note", "updated_at"])
    return note_libre


def notes_a_revoir(profil, limite=A_REVOIR_MAX, matiere_id=None):
    """
    Les notes dont la révision est due (jamais révisées, ou échéance arrivée), les plus en retard d'abord :
    (total dû, [entrée du carnet]). Les signets sans texte n'en font pas partie : il n'y a rien à relire.
    """
    from .carnet import entree_marque, entree_note_libre  # import tardif : carnet importe ce module

    aujourdhui = timezone.localdate()
    marques = MarqueEtude.objects.filter(profil=profil).exclude(note="")
    libres = NoteLibre.objects.filter(profil=profil)
    if matiere_id is not None:
        marques = marques.filter(Q(lesson__subject_id=matiere_id) | Q(cours__subject_id=matiere_id))
        libres = libres.filter(subject_id=matiere_id)

    # Les notes déjà vues dont l'échéance est arrivée passent toujours : ce sont des rappels, pas de la nouveauté.
    dues_m = marques.filter(revision_due__lte=aujourdhui)
    dues_l = libres.filter(revision_due__lte=aujourdhui)
    # Les notes jamais révisées arrivent au compte-gouttes (NOUVELLES_PAR_JOUR par jour) : sinon un élève qui a quarante
    # notes anciennes en voyait vingt d'un coup le premier jour. Une révision CHOISIE d'une matière n'est pas plafonnée.
    neuves_m = marques.filter(revision_due__isnull=True)
    neuves_l = libres.filter(revision_due__isnull=True)
    if matiere_id is None:
        deja = (
            MarqueEtude.objects.filter(profil=profil, revision_debut=aujourdhui).count()
            + NoteLibre.objects.filter(profil=profil, revision_debut=aujourdhui).count()
        )
        quota = max(0, NOUVELLES_PAR_JOUR - deja)
    else:
        quota = limite

    neuves = (
        [entree_marque(m) for m in neuves_m.select_related("lesson__subject__country", "cours__subject__country")[:quota]]
        + [entree_note_libre(n) for n in neuves_l.select_related("subject__country")[:quota]]
    )[:quota]
    dues = [entree_marque(m) for m in dues_m.select_related("lesson__subject__country", "cours__subject__country")[:limite]]
    dues += [entree_note_libre(n) for n in dues_l.select_related("subject__country")[:limite]]
    dues.sort(key=lambda e: e["revision_due"])  # la plus en retard d'abord
    total = dues_m.count() + dues_l.count() + min(neuves_m.count() + neuves_l.count(), quota)
    return total, (dues + neuves)[:limite]


def noter_revue(profil, genre, pk, savais):
    """
    Enregistre la révision d'une note. `genre` : « marque » ou « libre ». « Je m'en souviens » monte d'un palier (une note
    nouvelle entre à J+3), « à revoir » revient demain. Même règle que les cartes de cours : une révision anticipée d'une
    note sue ne change rien. Renvoie l'objet, ou None s'il n'existe pas (ou n'est pas à ce profil).
    """
    modele = {"marque": MarqueEtude, "libre": NoteLibre}.get(genre)
    if modele is None:
        return None
    obj = modele.objects.filter(profil=profil, pk=pk).first()
    if obj is None:
        return None
    aujourdhui = timezone.localdate()
    if savais and obj.revision_due is not None and obj.revision_due > aujourdhui:
        return obj
    dernier = len(LEITNER_INTERVALS_JOURS) - 1
    if not savais:
        palier = 0
    elif obj.revision_due is None:
        palier = 1
    else:
        palier = min(obj.revision_palier + 1, dernier)
    if obj.revision_debut is None:
        obj.revision_debut = aujourdhui
    obj.revision_palier = palier
    obj.revision_due = aujourdhui + timedelta(days=LEITNER_INTERVALS_JOURS[palier])
    obj.save(update_fields=["revision_palier", "revision_due", "revision_debut"])
    return obj
