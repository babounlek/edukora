"""Prépare les tranches de cours GCE (5 thèmes par tranche) d'une ou plusieurs matières.

Pour une matière et un niveau, retient les NB thèmes qui ont des items de quiz VALIDES mais AUCUN cours, classés par fréquence
d'examen (nombre de questions de ce thème dans les épreuves du niveau), et écrit les tranches lues par les agents
(`consignes/CONSIGNES_COURS_GCE.md` + `CONSIGNES_COURS_GCE_AUTRES.md`) :

    backend/ingest/_gce_staging/cours_autres/<niveau>-<matiere>-<NN>.json

Chaque entrée : matiere_code, serie ("GCE O/L" ou "GCE A/L"), theme, nb_items_quiz, epreuve_source, nb_questions_ref, references
(1 à 3 vraies questions d'examen du thème, niveau et style à viser, jamais à copier).

À lancer dans le conteneur, avec des variables posées avant le script :

    CIBLES = [("GCE_ENGLISH", "ol"), ("GCE_HISTORY", "al")]
    NB = 25
    NUM0 = 1  # facultatif
    SORTIE = "/app/ingest/_gce_staging/cours_autres"
    exec(open("/tmp/preparer_cours_vague.py").read())
"""
import json
import os
import re

from catalog.models import Cours, Lesson, Question, Subject
from quiz.models import CompetenceItem

TAILLE_TRANCHE = 5
SERIES = {"ol": "GCE O/L", "al": "GCE A/L"}
EXAMENS = {"ol": "GCE_OL", "al": "GCE_AL"}
SLUGS = {
    "GCE_ADD_MATHS": "add-maths", "GCE_BIOLOGY": "biology", "GCE_CITIZENSHIP": "citizenship", "GCE_COMMERCE": "commerce",
    "GCE_COMPUTER_SCI": "computer-sci", "GCE_ECONOMICS": "economics", "GCE_ENGLISH": "english",
    "GCE_FOOD_NUTRITION": "food-nutrition", "GCE_FRENCH": "french", "GCE_GEOGRAPHY": "geography", "GCE_HISTORY": "history",
    "GCE_HUMAN_BIOLOGY": "human-biology", "GCE_GEOLOGY": "geology", "GCE_ICT": "ict", "GCE_PHILOSOPHY": "philosophy",
    "GCE_PM_MECHANICS": "pm-mechanics", "GCE_PM_STATISTICS": "pm-statistics", "GCE_RELIGION": "religion",
    "GCE_SBE_FRENCH": "sbe-french", "GCE_CHEMISTRY": "chemistry", "GCE_PHYSICS": "physics", "GCE_MATHS": "maths",
    "GCE_FURTHER_MATHS": "further-maths",
}


def references(tag, sujet, niveau):
    """Jusqu'à 3 questions d'examen du thème (leçons du niveau), de leçons distinctes, les plus récentes d'abord."""
    qs = (
        Question.objects.filter(
            themes=tag, exercise__lesson__subject=sujet, exercise__lesson__cursus__examen=EXAMENS[niveau],
        )
        .select_related("exercise__lesson").order_by("-exercise__lesson__year", "exercise__lesson__id", "id").distinct()
    )
    choisies, vues = [], set()
    for q in qs:
        texte = re.sub(r"\s+", " ", (q.enonce_markdown or "")).strip()
        lecon = q.exercise.lesson
        if not 40 <= len(texte) <= 700 or lecon.id in vues:
            continue
        vues.add(lecon.id)
        choisies.append({"epreuve_source": lecon.epreuve_source, "enonce": (q.enonce_markdown or "").strip()})
        if len(choisies) == 3:
            break
    return choisies, qs.count()


# Numéro de la première tranche écrite : 1 par défaut ; 2 quand la tranche 01 existe déjà (pilote), pour ne rien écraser.
NUM0 = globals().get("NUM0", 1)
bilan = []
for code, niveau in CIBLES:
    sujet = Subject.objects.get(code=code, country__code__iexact="cm")
    deja_couverts = set(Cours.objects.filter(subject=sujet).values_list("tags__id", flat=True))
    par_theme = {}
    for item in CompetenceItem.objects.filter(subject=sujet, statut="VALIDE").select_related("theme").prefetch_related("cursus"):
        if EXAMENS[niveau] not in {c.examen for c in item.cursus.all()}:
            continue
        par_theme.setdefault(item.theme_id, [item.theme, 0])[1] += 1
    candidats = []
    for tag, nb_items in par_theme.values():
        if tag.id in deja_couverts:
            continue
        refs, nb_questions = references(tag, sujet, niveau)
        if not refs:
            continue
        candidats.append((nb_questions, tag, nb_items, refs))
    candidats.sort(key=lambda x: (-x[0], x[1].name))
    retenus = candidats[:NB]
    os.makedirs(SORTIE, exist_ok=True)
    nb_tranches = 0
    for debut in range(0, len(retenus), TAILLE_TRANCHE):
        tranche = [
            {
                "matiere_code": code, "serie": SERIES[niveau], "theme": tag.name, "nb_items_quiz": nb_items,
                "epreuve_source": refs[0]["epreuve_source"], "nb_questions_ref": nb_q, "references": refs,
            }
            for nb_q, tag, nb_items, refs in retenus[debut: debut + TAILLE_TRANCHE]
        ]
        nom = f"{niveau}-{SLUGS[code]}-{debut // TAILLE_TRANCHE + NUM0:02d}.json"
        with open(os.path.join(SORTIE, nom), "w", encoding="utf-8") as f:
            json.dump(tranche, f, ensure_ascii=False, indent=2)
        nb_tranches += 1
    bilan.append((code, niveau, len(par_theme), len(candidats), len(retenus), nb_tranches))
    print("RES", code, niveau, "themes_avec_quiz", len(par_theme), "sans_cours", len(candidats), "retenus", len(retenus), "tranches", nb_tranches)
    for nb_q, tag, nb_items, refs in retenus[:8]:
        print("RES   ", nb_q, tag.name)
