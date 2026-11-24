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


PAGE_CARNET = 20


def _sans_accent(s):
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower()


def _a_reviser(entree, maintenant_iso):
    return bool(entree["note"]) and entree["revision_due"] is not None and entree["revision_due"] <= maintenant_iso


def resumer_dossiers(carnet, maintenant):
    """Un résumé par matière : de quoi afficher la grille des dossiers sans envoyer les notes."""
    iso = maintenant.isoformat()
    dossiers = {}
    for e in carnet:
        d = dossiers.setdefault(
            e["matiere_id"],
            {"matiere_id": e["matiere_id"], "matiere": e["matiere"], "total": 0, "a_reviser": 0, "epingles": 0,
             "avec_note": 0, "updated_at": e["updated_at"]},
        )
        d["total"] += 1
        d["epingles"] += 1 if e["epingle"] else 0
        d["avec_note"] += 1 if e["note"] else 0
        d["a_reviser"] += 1 if _a_reviser(e, iso) else 0
        if e["updated_at"] > d["updated_at"]:
            d["updated_at"] = e["updated_at"]
    # Les dossiers où il y a quelque chose à réviser d'abord, puis les plus récemment touchés.
    return sorted(dossiers.values(), key=lambda d: (d["a_reviser"] == 0, -d["updated_at"].timestamp()))


def filtrer_carnet(carnet, matiere_id=None, filtre="tout", q="", tri="recent", maintenant=None):
    """Filtre (matière, genre, recherche sans accent) puis trie : épinglées en tête, puis récentes ou « à réviser »."""
    aiguille = _sans_accent((q or "").strip())
    gardees = []
    for e in carnet:
        if matiere_id is not None and e["matiere_id"] != matiere_id:
            continue
        if filtre == "notes" and not e["note"] and e["genre"] != "libre":
            continue
        if filtre == "signets" and not e["signet"]:
            continue
        if filtre == "epinglees" and not e["epingle"]:
            continue
        if aiguille and aiguille not in _sans_accent(f'{e["note"]} {e["titre"]} {e["matiere"]} {e["cle"]} {e["citation"]}'):
            continue
        gardees.append(e)
    gardees.sort(key=lambda e: e["updated_at"], reverse=True)
    if tri == "a_reviser" and maintenant is not None:
        iso = maintenant.isoformat()
        gardees.sort(key=lambda e: (not _a_reviser(e, iso), e["revision_due"] or "9999"))
    gardees.sort(key=lambda e: not e["epingle"])
    return gardees
