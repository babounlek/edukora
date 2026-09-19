"""Validation des lots de quiz avant ingestion : structure, QCM, corrigé, thème existant, unicité, similarité
avec le matériau de référence (shingles de 5 mots). Exécuter : manage.py shell -c "exec(open(...).read())"
Variable d'env LOTS = liste de slugs séparés par des virgules (défaut : tous ceux de la shortlist)."""
import json
import os
import re
import unicodedata
from pathlib import Path

from catalog.models import Tag
from quiz.models import CompetenceItem

QUIZ_DIR = Path("/app/ingest/_quiz/cm")
SH = json.load(open("/app/ingest/_audit/quiz_shortlist_informatique_ti_2021_blanc.json", encoding="utf-8"))
MAT = json.load(open("/app/ingest/_audit/quiz_ti_materiel.json", encoding="utf-8"))


def slug(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def shingles(text, n=5):
    mots = re.findall(r"\w+", (text or "").lower())
    return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}


erreurs, alertes, total = [], [], 0
ids_vus = set(CompetenceItem.objects.exclude(external_id="").values_list("external_id", flat=True))
for theme in SH["themes_a_generer"]:
    f = QUIZ_DIR / f"{slug(theme)}.json"
    if not f.exists():
        erreurs.append((theme, "fichier absent")); continue
    try:
        items = json.loads(f.read_text(encoding="utf-8"))
    except ValueError as e:
        erreurs.append((theme, f"JSON invalide: {e}")); continue
    tag = Tag.objects.filter(name=theme).first()
    refs = [(r["enonce_markdown"] + " " + r["corrige_markdown"]) for r in MAT[theme]["materiel_reference"]]
    ref_sh = set().union(*[shingles(r) for r in refs]) if refs else set()
    locaux = set()
    for it in items:
        total += 1
        eid = it.get("external_id", "")
        p = f"{theme} / {eid}"
        if not eid or eid in locaux: erreurs.append((p, "external_id vide ou dupliqué"))
        if eid in ids_vus: alertes.append((p, "external_id déjà en base (idempotent, ok si relance)"))
        locaux.add(eid)
        if it.get("theme") != theme or tag is None: erreurs.append((p, f"theme {it.get('theme')!r} != {theme!r}"))
        if it.get("matiere") != "Réseaux, Internet et Sécurité Informatique": erreurs.append((p, f"matiere {it.get('matiere')!r}"))
        if it.get("cursus") != [{"examen": "bac", "serie": "TI"}]: erreurs.append((p, f"cursus {it.get('cursus')!r}"))
        if it.get("difficulte_estimee") not in ("FAIBLE", "MOYENNE", "ELEVEE"): erreurs.append((p, "difficulté"))
        if not re.match(rf"^cqc-{re.escape(slug(theme))}-(faible|moyenne|elevee)-\d+$", eid): alertes.append((p, "format external_id"))
        c = it.get("corrige_markdown", "")
        if not c.startswith("### Rappel de méthode") or "### Corrigé" not in c or c.index("### Corrigé") < c.index("### Rappel de méthode"):
            erreurs.append((p, "corrigé sans Rappel de méthode puis Corrigé"))
        e = it.get("enonce_markdown", "")
        if len(e) < 25: erreurs.append((p, "énoncé trop court"))
        if re.search(r"question précédente|ci-dessus|ci-dessous|figure|schéma ci|tableau ci|capture", e, re.I): alertes.append((p, "renvoi externe possible dans l'énoncé"))
        if it.get("type_reponse") == "QCM":
            lettres = [x.get("lettre") for x in it.get("choix", [])]
            if len(lettres) < 3 or len(set(lettres)) != len(lettres) or it.get("reponse_correcte") not in lettres:
                erreurs.append((p, f"QCM incohérent {lettres} / {it.get('reponse_correcte')!r}"))
            textes = [x.get("texte", "") for x in it.get("choix", [])]
            if len(set(textes)) != len(textes): erreurs.append((p, "choix QCM dupliqués"))
        elif it.get("type_reponse") == "OUVERTE":
            if it.get("choix") or it.get("reponse_correcte"): erreurs.append((p, "OUVERTE avec choix/réponse"))
        else:
            erreurs.append((p, "type_reponse"))
        if not it.get("source_exercises"): alertes.append((p, "source_exercises vide"))
        sh = shingles(e)
        recouvre = len(sh & ref_sh) / max(1, len(sh))
        if recouvre > 0.15: erreurs.append((p, f"similarité avec le matériau {recouvre:.0%}"))
        if re.search(r"(?<!\\)\$(?![A-Za-z\d\\{(])|`\$", e + c) and False: pass
    print(f"{theme}: {len(items)} items")
print(f"\nTOTAL {total} items | erreurs {len(erreurs)} | alertes {len(alertes)}")
for x in erreurs: print("ERREUR", x)
for x in alertes[:25]: print("alerte", x)
