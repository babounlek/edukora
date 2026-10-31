"""Mode CONTRÔLE côté base locale : l'énoncé visible côté élève a-t-il absorbé une réponse ? (§3 b et c)

Lecture seule, à lancer dans le shell Django du conteneur (comme extraire_base.py) :

    docker cp scripts/corpus/controle_base.py edukora-backend-1:/tmp/controle_base.py
    docker exec edukora-backend-1 python manage.py shell -c "exec(open('/tmp/controle_base.py').read())"
    docker cp edukora-backend-1:/tmp/controle_base.json <destination>

Un corrigé rédigé par EduKora dans `corrige_markdown` est NORMAL : seuls `enonce_markdown` et
`enonce_intro_markdown` sont examinés. Le rapport signale des indices, jamais une certitude.
"""
import json
import os
import re

from catalog.models import Exercise, Question

SORTIE = os.environ.get("CORPUS_CONTROLE_SORTIE", "/tmp/controle_base.json")
MOTIFS = [
    ("reponse_annoncee", re.compile(r"(?i)\b(r[ée]ponse\s+(?:correcte|attendue|exacte)|correct\s+answer|right\s+answer|answer\s*[:=]|bonne\s+r[ée]ponse)\b")),
    ("coche", re.compile("[✔✓☑✅]")),
    ("corrige_inline", re.compile(r"(?i)\b(corrig[ée]\s*:|solution\s*:|mark\s*scheme)")),
    ("rappel_dans_enonce", re.compile(r"###\s*Rappel de m[ée]thode")),
]


def _indices(texte):
    return [nom for nom, motif in MOTIFS if texte and motif.search(texte)]


trouvailles = []
for q in Question.objects.select_related("exercise__lesson").iterator(chunk_size=2000):
    marques = _indices(q.enonce_markdown or "")
    if marques:
        trouvailles.append({"modele": "Question", "id": q.id, "lesson": q.exercise.lesson_id,
                            "epreuve_source": q.exercise.lesson.epreuve_source, "indices": marques,
                            "extrait": (q.enonce_markdown or "")[:160]})
for e in Exercise.objects.select_related("lesson").iterator(chunk_size=2000):
    marques = _indices(e.enonce_intro_markdown or "")
    if marques:
        trouvailles.append({"modele": "Exercise", "id": e.id, "lesson": e.lesson_id,
                            "epreuve_source": e.lesson.epreuve_source, "indices": marques,
                            "extrait": (e.enonce_intro_markdown or "")[:160]})

with open(SORTIE, "w", encoding="utf-8") as fh:
    json.dump(trouvailles, fh, ensure_ascii=False)
print("RES controle_base :", len(trouvailles), "indice(s) ->", SORTIE)
