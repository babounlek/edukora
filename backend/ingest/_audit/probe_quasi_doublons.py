from collections import defaultdict

from catalog.models import Cours, Exercise, Lesson, Question, Tag
from catalog.tunnel import tag_key
from quiz.models import CompetenceItem

groupes = defaultdict(list)
for t in Tag.objects.all():
    groupes[tag_key(t.name)].append(t)
groupes = {k: v for k, v in groupes.items() if len(v) > 1}

# matières utilisées par tag
sujets = defaultdict(set)
liens = (
    (Lesson.themes.through, "tag_id", "lesson__subject_id"),
    (Exercise.themes.through, "tag_id", "exercise__lesson__subject_id"),
    (Question.themes.through, "tag_id", "question__exercise__lesson__subject_id"),
    (Cours.tags.through, "tag_id", "cours__subject_id"),
)
for through, tf, sf in liens:
    for tid, sid in through.objects.values_list(tf, sf).distinct():
        sujets[tid].add(sid)
for tid, sid in CompetenceItem.objects.values_list("theme_id", "subject_id").distinct():
    sujets[tid].add(sid)

sures, conflit_savoir, multi_matieres, sans_usage = [], [], [], []
for cle, tags in groupes.items():
    savoirs = {t.savoir_officiel_id for t in tags if t.savoir_officiel_id}
    matieres = set()
    for t in tags:
        matieres |= sujets[t.id]
    if len(savoirs) > 1:
        conflit_savoir.append(tags)
    elif len(matieres) > 1:
        multi_matieres.append(tags)
    else:
        sures.append(tags)

print("groupes quasi-doublons:", len(groupes), "| tags concernés:", sum(len(v) for v in groupes.values()))
print("  fusionnables (une seule matière, pas de conflit savoir):", len(sures), "->", sum(len(v) - 1 for v in sures), "tags à supprimer")
print("  conflit savoir_officiel:", len(conflit_savoir))
print("  plusieurs matières (collision de sens possible):", len(multi_matieres))
import random
random.seed(3)
print("--- échantillon fusionnables")
for tags in random.sample(sures, 25):
    print("  ", [t.name for t in tags])
print("--- échantillon multi-matières")
for tags in random.sample(multi_matieres, min(15, len(multi_matieres))):
    print("  ", [t.name for t in tags])
