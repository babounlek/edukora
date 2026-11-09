"""Mode CONTRÔLE côté base locale : un PDF candidat est-il déjà en base ? (lecture seule)

À lancer dans le shell Django du conteneur, par `corpus.py base-doublons` (qui copie ce fichier, `similarite.py` et
le JSON des candidats, puis récupère les lignes préfixées `@@`) :

    docker exec edukora-backend-1 python manage.py shell -c "exec(open('/tmp/comparer_base.py').read())"

Entrée  : /tmp/candidats_base.json = {"annee_min": 2019, "candidats": {"nom": "texte du PDF", ...}}
Sortie  : une ligne `@@` + JSON par candidat (les lignes de journal SQL du shell sont ignorées par l'appelant).
Ne lit que les énoncés (intro d'exercice et questions) des Lessons ; n'écrit rien.
"""
import json
import sys

sys.path.insert(0, "/tmp")

import similarite  # noqa: E402
from catalog.models import Lesson  # noqa: E402

DONNEES = json.load(open("/tmp/candidats_base.json", encoding="utf-8"))
CANDIDATS = {nom: similarite.sequences(texte) for nom, texte in DONNEES["candidats"].items()}
MEILLEURS = {nom: [] for nom in CANDIDATS}

for lecon in Lesson.objects.filter(year__gte=DONNEES.get("annee_min", 2019)).prefetch_related("exercises__questions").iterator(chunk_size=200):
    morceaux = []
    for exercice in lecon.exercises.all():
        morceaux.append(exercice.enonce_intro_markdown or "")
        morceaux.extend(q.enonce_markdown or "" for q in exercice.questions.all())
    base = similarite.sequences(" ".join(morceaux))
    if not base:
        continue
    for nom, candidat in CANDIDATS.items():
        cc, cb, n = similarite.comparer(candidat, base)
        if n >= similarite.SEUIL_PLANCHER:
            MEILLEURS[nom].append({"lesson": lecon.id, "titre": lecon.title[:80], "annee": lecon.year,
                                   "origine": lecon.origine, "couvert_candidat": cc, "couvert_base": cb,
                                   "niveau": similarite.niveau(cc, cb, n)})

for nom, lignes in MEILLEURS.items():
    lignes.sort(key=lambda r: max(r["couvert_candidat"], r["couvert_base"]), reverse=True)
    print("@@" + json.dumps({"candidat": nom, "meilleurs": lignes[:3]}, ensure_ascii=False))
