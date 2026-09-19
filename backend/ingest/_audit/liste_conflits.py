from collections import defaultdict

from catalog.management.commands.fusionner_tags_doublons import _related_count
from catalog.models import Tag
from catalog.tunnel import tag_key

g = defaultdict(list)
for t in Tag.objects.select_related("savoir_officiel__module__subject").order_by("id"):
    g[tag_key(t.name)].append(t)
i = 0
for tags in g.values():
    if len(tags) > 1 and len({t.savoir_officiel_id for t in tags if t.savoir_officiel_id}) > 1:
        i += 1
        parts = []
        for t in tags:
            s = t.savoir_officiel
            lab = f"{s.module.subject.code[:5]} {s.module.classe}{s.module.serie_label} M{s.module.numero} {s.intitule[:28]}" if s else "-"
            parts.append(f"{t.name!r}({_related_count(t)}) [{lab}]")
        print(f"{i:3} | " + " || ".join(parts))
