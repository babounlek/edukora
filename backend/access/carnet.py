"""
« Mes notes » : la forme commune des entrées du carnet (une note posée sur une section, ou une note libre rattachée
à une matière). Voir access.models.MarqueEtude et access.models.NoteLibre.
"""


def _date(d):
    return d.isoformat() if d else None


def entree_marque(marque):
    doc = marque.cours or marque.lesson
    return {
        "genre": "marque",
        "id": marque.pk,
        "cle": marque.cle,
        "compris": marque.compris,
        "signet": marque.signet,
        "note": marque.note,
        "updated_at": marque.updated_at,
        "type": "cours" if marque.cours_id else "epreuve",
        "titre": doc.titre if marque.cours_id else doc.title,
        "slug": doc.slug,
        "country": doc.subject.country.code.lower(),
        "matiere": doc.subject.label,
        "matiere_id": doc.subject_id,
        "citation": "",
        "revision_due": _date(marque.revision_due),
        "epingle": marque.epingle,
    }


def entree_note_libre(note):
    return {
        "genre": "libre",
        "id": note.pk,
        "cle": "",
        "compris": False,
        "signet": False,
        "note": note.note,
        "updated_at": note.updated_at,
        "type": "libre",
        "titre": "",
        "slug": "",
        "country": note.subject.country.code.lower(),
        "matiere": note.subject.label,
        "matiere_id": note.subject_id,
        "citation": note.citation,
        "revision_due": _date(note.revision_due),
        "epingle": note.epingle,
    }
