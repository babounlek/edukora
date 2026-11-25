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


ORIGINES_NOTE = ("quiz", "fiche")


SOURCE_MAX = 300
IMAGE_MAX_OCTETS = 8 * 1024 * 1024  # ce que le serveur accepte de lire ; le client réduit bien avant
IMAGE_COTE_MAX = 1600
IMAGE_PIXELS_MAX = 40_000_000
IMAGES_PAR_PROFIL_MAX = 200


def source_valide(source):
    """Une adresse INTERNE seulement (/cours/…, /epreuves/…, /quiz/session/…) : jamais un lien écrit à la main vers l'extérieur."""
    source = str(source or "").strip()
    if not source.startswith("/") or source.startswith("//") or len(source) > SOURCE_MAX:
        return ""
    if chr(92) in source or "://" in source or any(c.isspace() for c in source):
        return ""
    return source


def creer_note_libre(profil, subject, note, citation="", origine="", source="", avec_image=False, theme_id=None):
    note = str(note or "").strip()
    citation = str(citation or "").strip()
    # Un passage gardé tel quel (ou une photo seule) est déjà une note : le texte peut rester vide.
    if not note and not citation and not avec_image:
        raise MarqueInvalide("La note est vide.")
    if len(note) > NOTE_MAX:
        raise MarqueInvalide(f"Note trop longue ({NOTE_MAX} caractères maximum).")
    if len(citation) > CITATION_MAX:
        citation = citation[:CITATION_MAX]
    origine = origine if origine in ORIGINES_NOTE else ""
    from catalog.models import Tag

    theme = Tag.objects.filter(pk=theme_id).first() if str(theme_id or "").isdigit() else None
    return NoteLibre.objects.create(
        profil=profil, subject=subject, note=note, citation=citation, origine=origine, source=source_valide(source),
        theme=theme,
    )


NOTES_DU_THEME_MAX = 5


def notes_du_theme(profil, theme_id, limite=NOTES_DU_THEME_MAX):
    """Les notes de l'élève sur ce thème (texte ou passage gardé), les épinglées puis les plus récentes : (total, [notes])."""
    if not str(theme_id or "").isdigit():
        return 0, []
    qs = NoteLibre.objects.filter(profil=profil, theme_id=int(theme_id)).select_related("subject__country")
    total = qs.count()
    notes = list(qs.order_by("-epingle", "-updated_at")[:limite])
    return total, notes


def resume_des_notes(profil):
    """
    Le bloc « Mes notes » de l'accueil : combien l'élève en a, et la dernière (une épinglée d'abord) en clair.
    {total, derniere: {texte, matiere, matiere_code, matiere_id, epingle} | None}.
    """
    libres = NoteLibre.objects.filter(profil=profil)
    marques = MarqueEtude.objects.filter(profil=profil).filter(Q(signet=True) | ~Q(note=""))
    note = libres.select_related("subject").order_by("-epingle", "-updated_at").first()
    derniere = None
    if note is not None and (note.note or note.citation):
        derniere = {
            "texte": (note.note or note.citation)[:280],
            "matiere": note.subject.label,
            "matiere_code": note.subject.code,
            "matiere_id": note.subject_id,
            "epingle": note.epingle,
        }
    return {"total": libres.count() + marques.count(), "derniere": derniere}


def total_notes_dues(profil):
    """Combien de notes sont à réviser aujourd'hui (même compte que l'accueil) : pour les rappels du jour."""
    if profil is None:
        return 0
    return notes_a_revoir(profil, limite=1)[0]


def modifier_note_libre(note_libre, note, avec_image=False):
    note = str(note or "").strip()
    if not note and not note_libre.citation and not note_libre.image and not avec_image:
        raise MarqueInvalide("La note est vide.")
    if len(note) > NOTE_MAX:
        raise MarqueInvalide(f"Note trop longue ({NOTE_MAX} caractères maximum).")
    note_libre.note = note
    note_libre.save(update_fields=["note", "updated_at"])
    return note_libre


def enregistrer_image_note(note_libre, fichier):
    """
    Joint une photo à la note : vérifiée par Pillow (jamais confiance au type annoncé), remise à l'endroit, réduite à
    IMAGE_COTE_MAX px, ré-encodée en JPEG (les métadonnées, position GPS comprise, disparaissent). Remplace la précédente.
    """
    import io

    from django.core.files.base import ContentFile
    from PIL import Image, ImageOps, UnidentifiedImageError

    if fichier is None:
        raise MarqueInvalide("Aucune image reçue.")
    if fichier.size > IMAGE_MAX_OCTETS:
        raise MarqueInvalide("Image trop lourde.")
    if not note_libre.image and NoteLibre.objects.filter(profil=note_libre.profil).exclude(image="").count() >= IMAGES_PAR_PROFIL_MAX:
        raise MarqueInvalide("Trop de notes avec une image : retires-en quelques-unes d'abord.")
    try:
        image = Image.open(fichier)
        if image.format not in ("JPEG", "PNG", "WEBP"):
            raise MarqueInvalide("Format d'image non pris en charge (JPEG, PNG ou WebP).")
        if image.width * image.height > IMAGE_PIXELS_MAX:
            raise MarqueInvalide("Image trop grande.")
        image = ImageOps.exif_transpose(image)
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
            fond = Image.new("RGB", image.size, (255, 255, 255))
            fond.paste(image, mask=image.split()[-1])
            image = fond
        else:
            image = image.convert("RGB")
        image.thumbnail((IMAGE_COTE_MAX, IMAGE_COTE_MAX))
        tampon = io.BytesIO()
        image.save(tampon, format="JPEG", quality=82, optimize=True)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise MarqueInvalide("Ce fichier n'est pas une image lisible.")
    if note_libre.image:
        note_libre.image.delete(save=False)
    note_libre.image.save("note.jpg", ContentFile(tampon.getvalue()), save=False)
    note_libre.save(update_fields=["image", "updated_at"])
    return note_libre


def retirer_image_note(note_libre):
    if note_libre.image:
        note_libre.image.delete(save=False)
        note_libre.save(update_fields=["image", "updated_at"])
    return note_libre


def notes_a_revoir(profil, limite=A_REVOIR_MAX, matiere_id=None):
    """
    Les notes dont la révision est due (jamais révisées, ou échéance arrivée), les plus en retard d'abord :
    (total dû, [entrée du carnet]). Les signets sans texte n'en font pas partie : il n'y a rien à relire.
    """
    from .carnet import entree_marque, entree_note_libre  # import tardif : carnet importe ce module

    aujourdhui = timezone.localdate()
    marques = MarqueEtude.objects.filter(profil=profil).exclude(note="")
    # Un passage gardé sans texte (citation seule) n'a rien à retrouver de mémoire : il reste dans les dossiers, pas en révision.
    libres = NoteLibre.objects.filter(profil=profil).exclude(note="")
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


def epingler(profil, genre, pk, epingle):
    """Épingle ou désépingle une note (« marque » ou « libre ») de ce profil. None si elle n'existe pas."""
    modele = {"marque": MarqueEtude, "libre": NoteLibre}.get(genre)
    obj = modele.objects.filter(profil=profil, pk=pk).first() if modele else None
    if obj is None:
        return None
    obj.epingle = bool(epingle)
    # `updated_at` ne bouge pas : épingler n'est pas écrire, la note ne doit pas sauter en tête de la liste récente.
    modele.objects.filter(pk=obj.pk).update(epingle=obj.epingle)
    return obj
