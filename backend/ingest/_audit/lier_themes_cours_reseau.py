"""Rattache aux Cours existants les Tags (thèmes) de la leçon informatique-bac-ti-2021-blanc qui n'avaient aucun cours
sous ce nom : ajoute le Tag à Cours.tags (DB) et à meta.tags du JSON source. DRY=1 : simulation."""
import json
import os
from pathlib import Path

from catalog.models import Cours, Tag

DRY = os.environ.get("DRY") == "1"
# (sous-chaîne du titre du cours (insensible à la casse)) -> Tags à lui ajouter
REGLES = [
    ("ipconfig", ["ipconfig /all", "commandes réseau Windows"]),
    ("supports de transmission", ["câbles réseau"]),
    ("connecteurs", ["câbles réseau", "connecteurs fibre optique"]),
    ("technologies d'accès à internet", ["technologies d'accès à Internet"]),
    ("recherche par guillemets", ["opérateurs de recherche avancée"]),
    ("intitle", ["opérateurs de recherche avancée"]),
    ("guillemets", ["opérateurs de recherche avancée"]),
    ("classes d'adresses", ["classes d'adresses IPv4", "masque par défaut"]),
    ("emprunt de bits", ["emprunt de bits"]),
    ("plage d'adresses utilisables", ["plage d'adresses utilisables"]),
    ("nombre d'hôtes", ["masque /27"]),
    ("ping", ["protocole ICMP"]),
    ("césar", ["cryptographie"]),
    ("nombre maximal de machines", ["masque /27"]),
    ("(google)", ["Google"]),
]
SRC = {}
for f in Path("/app/ingest").glob("*/*/*_cours*.json"):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except ValueError:
        continue
    if isinstance(d, dict) and d.get("cours_id"):
        SRC[d["cours_id"]] = (f, d)

ajouts = 0
for sous_chaine, noms in REGLES:
    for c in Cours.objects.filter(titre__icontains=sous_chaine, statut="VALIDE", subject__code__in=["RESEAUX_SECURITE", "INFORMATIQUE", "SYSTEMES_INFORMATION"]):
        for nom in noms:
            tag = Tag.objects.filter(name=nom).first()
            if tag is None:
                print("TAG ABSENT", nom); continue
            if c.tags.filter(pk=tag.pk).exists():
                continue
            print(f"+ {nom!r} -> cours #{c.pk} {c.titre[:70]!r}")
            ajouts += 1
            if not DRY:
                c.tags.add(tag)
                src = SRC.get(c.external_id)
                if src:
                    f, d = src
                    tags = d.setdefault("meta", {}).setdefault("tags", [])
                    if nom not in tags:
                        tags.append(nom)
                        f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("ajouts:", ajouts, "(simulation)" if DRY else "")
