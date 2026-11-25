"""
Tirer les fiches des corrigés déjà validés.

Dans une question « Définis : scrutin, tontine… », le corrigé donne chaque définition sous la forme « **Terme** : … ».
On les relève, on les regroupe par terme (un même mot tombe plusieurs années), et on garde la rédaction la plus récente.
Rien n'est inventé ici : le texte d'une fiche est celui d'un corrigé de la plateforme, et la liste des sessions est celle
des épreuves où la question a été posée.

Le résultat est une proposition : les fiches naissent BROUILLON, un enseignant les relit (voir memos.models.Memo).
"""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from catalog.models import Question

from .gratuites import assurer_gratuites, fusionner_sessions
from .models import Memo, StatutMemo

QUESTION_DE_DEFINITION = re.compile(r"d[ée]fini", re.IGNORECASE)
LIGNE_DE_DEFINITION = re.compile(r"^\s*(?:[-*]\s+)?\*\*([^*\n]{2,60})\*\*\s*:\s*(.+)$", re.MULTILINE)
# Les intertitres d'un corrigé ont la même forme qu'une définition (« **Astuce** : … ») : ce ne sont pas des notions.
PAS_DES_NOTIONS = {
    "rappel de methode", "astuce", "piege", "attention", "reponse", "remarque", "erreur frequente", "a retenir", "bareme",
    "methode", "exemple", "conseil", "nb", "note",
}
DEFINITION_MIN = 25
FICHIER_CORRECTIONS = Path(__file__).resolve().parent / "donnees" / "corrections_extraites.json"


def _cle(terme):
    sans_accent = "".join(c for c in unicodedata.normalize("NFD", terme.lower()) if unicodedata.category(c) != "Mn")
    cle = re.sub(r"[^a-z0-9 ]", " ", sans_accent)
    # « La corruption » et « Corruption » sont la même notion.
    return re.sub(r"^(le|la|les|l|un|une|des)\s+", "", re.sub(r"\s+", " ", cle).strip())


def _propre(terme):
    terme = re.sub(r"^(le|la|les|l['’]|un|une|des)\s+", "", terme.strip(), flags=re.IGNORECASE).strip(" .:")
    return terme[:1].upper() + terme[1:]


def _phrase(texte):
    texte = texte.strip()
    texte = texte[:1].upper() + texte[1:]
    return texte if texte.endswith((".", "!", "?", "…")) else texte + "."


def corrections_de(subject):
    """Les retouches versionnées des fiches de cette matière (voir donnees/corrections_extraites.json), par terme."""
    toutes = json.loads(FICHIER_CORRECTIONS.read_text(encoding="utf-8"))
    return toutes.get(f"{subject.country.code.upper()}/{subject.code}", {})


def relever(subject):
    """Les notions définies dans les corrigés de cette matière : une entrée par terme, les plus souvent tombées d'abord."""
    notions = {}
    questions = (
        Question.objects.filter(exercise__lesson__subject=subject)
        .select_related("exercise__lesson")
        .prefetch_related("exercise__lesson__cursus", "themes")
    )
    for question in questions:
        if not QUESTION_DE_DEFINITION.search(question.enonce_markdown or ""):
            continue
        lesson = question.exercise.lesson
        for trouve in LIGNE_DE_DEFINITION.finditer(question.corrige_markdown or ""):
            terme, definition = trouve.group(1), trouve.group(2).strip()
            cle = _cle(terme)
            if not cle or cle in PAS_DES_NOTIONS or len(definition) < DEFINITION_MIN:
                continue
            notion = notions.setdefault(cle, {
                "terme": _propre(terme), "redactions": [], "sessions": [], "lessons": set(), "cursus": set(),
                "themes": Counter(),
            })
            notion["redactions"].append((lesson.year or 0, definition))
            if lesson.year:
                notion["sessions"] = fusionner_sessions(notion["sessions"], [
                    {"annee": lesson.year, "origine": lesson.origine, "cursus": [c.pk for c in lesson.cursus.all()]},
                ])
            notion["lessons"].add(lesson.pk)
            notion["cursus"].update(c.pk for c in lesson.cursus.all())
            notion["themes"].update(t.pk for t in question.themes.all())
    corrections = corrections_de(subject)
    relevees = []
    for cle, notion in notions.items():
        retouche = corrections.get(cle, {})
        relevees.append({
            "terme": retouche.get("terme", notion["terme"]),
            "definition": retouche.get("definition") or _phrase(max(notion["redactions"])[1]),
            "sessions": notion["sessions"],
            "lessons": sorted(notion["lessons"]),
            "cursus": sorted(notion["cursus"]),
            "theme_id": notion["themes"].most_common(1)[0][0] if notion["themes"] else None,
        })
    # Les notions tombées le plus souvent, puis le plus récemment, puis par ordre alphabétique.
    relevees.sort(key=lambda n: (-len(n["sessions"]), -max((s["annee"] for s in n["sessions"]), default=0), n["terme"]))
    return relevees


def enregistrer(subject, relevees):
    """
    Crée ou met à jour les fiches de la matière à partir du relevé : {"creees", "mises_a_jour", "laissees"}.
    Une fiche retouchée à la main n'est jamais réécrite ; une fiche publiée garde son statut et son texte relu (seules ses
    sessions et ses sources sont complétées). Sessions, sources et examens s'AJOUTENT à ceux d'une fiche qui prépare aussi
    d'autres examens (voir memos.redaction). Chaque examen garde quelques fiches lisibles sans abonnement.
    """
    bilan = {"creees": 0, "mises_a_jour": 0, "laissees": 0}
    existantes = {_cle(m.terme): m for m in Memo.objects.filter(subject=subject)}
    for rang, notion in enumerate(relevees):
        memo = existantes.get(_cle(notion["terme"]))
        if memo is None:
            memo = Memo.objects.create(
                subject=subject, terme=notion["terme"], definition=notion["definition"], sessions=notion["sessions"],
                theme_id=notion["theme_id"], ordre=(rang + 1) * 10, statut=StatutMemo.BROUILLON,
            )
            bilan["creees"] += 1
        elif memo.modifie_a_la_main:
            bilan["laissees"] += 1
        else:
            if memo.statut != StatutMemo.PUBLIE:
                memo.terme = notion["terme"]
                memo.definition = notion["definition"]
                memo.theme_id = notion["theme_id"]
            memo.sessions = fusionner_sessions(memo.sessions, notion["sessions"])
            memo.save()
            bilan["mises_a_jour"] += 1
        if not memo.modifie_a_la_main:
            memo.cursus.add(*notion["cursus"])
            memo.sources.add(*notion["lessons"])
    assurer_gratuites(subject)
    return bilan
