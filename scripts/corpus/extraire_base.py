"""Instantané en lecture seule de la base LOCALE pour le skill veille-corpus-epreuves.

Se lance dans le conteneur backend, sans rien modifier :

    docker cp scripts/corpus/extraire_base.py edukora-backend-1:/tmp/extraire_base.py
    docker exec edukora-backend-1 python manage.py shell -c "exec(open('/tmp/extraire_base.py').read())"
    docker cp edukora-backend-1:/tmp/corpus_base.json <destination>

Une ligne par Lesson (= une épreuve) : identité, rattachements, effectifs, présence réelle des fichiers
(PDF de sujet et figures) sur le stockage local. Aucune écriture en base.
"""
import json
import os

from catalog.models import Exercise, Figure, Lesson, Question

SORTIE = os.environ.get("CORPUS_BASE_SORTIE", "/tmp/corpus_base.json")


def _existe(champ):
    """Le fichier du FileField existe-t-il sur le stockage ? None si le champ est vide."""
    if not champ or not getattr(champ, "name", ""):
        return None
    try:
        return bool(champ.storage.exists(champ.name))
    except Exception:  # noqa: BLE001 - un stockage injoignable ne doit pas faire échouer l'instantané
        return None


lecons = Lesson.objects.select_related("subject", "subject__country").prefetch_related(
    "cursus__series", "cursus__country"
)
nb_exo = {}
for lid in Exercise.objects.values_list("lesson_id", flat=True):
    nb_exo[lid] = nb_exo.get(lid, 0) + 1
nb_q = {}
for lid in Question.objects.values_list("exercise__lesson_id", flat=True):
    nb_q[lid] = nb_q.get(lid, 0) + 1
figures = {}
for fig in Figure.objects.select_related("exercise").iterator():
    stat = figures.setdefault(fig.exercise.lesson_id, {"n": 0, "manquantes": 0})
    stat["n"] += 1
    if _existe(fig.image) is False:
        stat["manquantes"] += 1

lignes = []
for l in lecons.iterator(chunk_size=500):
    cursus = []
    for c in l.cursus.all():
        cursus.append({
            "pays": c.country.code if getattr(c, "country", None) else None,
            "examen": c.examen,
            "serie": c.series.code if c.series_id else None,
        })
    fig = figures.get(l.id, {"n": 0, "manquantes": 0})
    lignes.append({
        "id": l.id,
        "titre": l.title,
        "epreuve_source": l.epreuve_source,
        "annee": l.year,
        "type": l.lesson_type,
        "statut": l.statut,
        "publie": bool(l.published_at),
        "matiere": l.subject.code if l.subject_id else None,
        "matiere_label": l.subject.label if l.subject_id else None,
        "langue": l.subject.langue if l.subject_id else None,
        "codes_officiels": l.subject.codes_officiels if l.subject_id else None,
        "pays": l.subject.country.code if l.subject_id and l.subject.country_id else None,
        "origine": l.origine,
        "etablissement": l.etablissement,
        "institution": l.institution,
        "nature": l.nature_epreuve,
        "partie_francais": l.partie_epreuve_francais,
        "variante": l.variante_sujet,
        "paper": l.numero_paper,
        "code_officiel": l.code_matiere_officiel,
        "filiere_a": l.filiere_serie_a,
        "cursus": cursus,
        "nb_exercices": nb_exo.get(l.id, 0),
        "nb_questions": nb_q.get(l.id, 0),
        "nb_figures": fig["n"],
        "figures_sans_fichier": fig["manquantes"],
        "sujet_pdf": l.sujet_pdf.name if l.sujet_pdf else None,
        "sujet_pdf_existe": _existe(l.sujet_pdf),
    })

with open(SORTIE, "w", encoding="utf-8") as fh:
    json.dump(lignes, fh, ensure_ascii=False)
print("RES corpus_base :", len(lignes), "épreuves ->", SORTIE)
