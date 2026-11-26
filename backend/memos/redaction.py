"""
Importer des fiches RÉDIGÉES (memos/donnees/*.json), quand les corrigés ne donnent rien à extraire.

Le Probatoire et le BAC d'éducation civique ne posent pas de « Définis… » : leurs notions sont rédigées dans un fichier
versionné, chacune rattachée aux épreuves qui l'ont demandée. Rien n'est saisi à la main pour les années : elles sont
lues sur les épreuves nommées. Comme les fiches extraites, elles naissent BROUILLON et ne se publient que relues.
"""

import json
from pathlib import Path

from catalog.models import Lesson, Subject, Tag

from .extraction import _cle
from .gratuites import assurer_gratuites, fusionner_sessions
from .models import Memo, StatutMemo

DOSSIER = Path(__file__).resolve().parent / "donnees"


class FichierInvalide(ValueError):
    pass


def lire(nom):
    chemin = DOSSIER / f"{nom}.json"
    if not chemin.exists():
        raise FichierInvalide(f"Fichier introuvable : {chemin.name}")
    return json.loads(chemin.read_text(encoding="utf-8"))


CHAMPS_FACULTATIFS = ("exemple", "piege", "exercice", "reponse", "rubrique")


def _facultatifs(notion):
    return {champ: notion.get(champ, "") for champ in CHAMPS_FACULTATIFS}


def importer(donnees, dry_run=False):
    """{"creees", "completees", "mises_a_jour", "epreuves_absentes", "themes_absents", "ignorees"}."""
    subject = Subject.objects.filter(country__code__iexact=donnees["pays"], code=donnees["matiere"]).first()
    if subject is None:
        raise FichierInvalide("Matière introuvable pour ce pays.")
    # Un même titre peut désigner deux sujets d'une même session : on les prend tous.
    epreuves = {
        alias: list(Lesson.objects.filter(subject=subject, title=titre).prefetch_related("cursus"))
        for alias, titre in donnees["epreuves"].items()
    }
    bilan = {"creees": 0, "completees": 0, "mises_a_jour": 0, "ignorees": 0,
             "epreuves_absentes": sorted(donnees["epreuves"][a] for a, l in epreuves.items() if not l)}
    # Le thème d'une fiche est nommé dans le fichier ; il n'est jamais créé ici : un thème inconnu ne mènerait à rien.
    noms = {n["theme"] for n in donnees["notions"] if n.get("theme")}
    themes = {tag.name: tag for tag in Tag.objects.filter(name__in=noms)}
    bilan["themes_absents"] = sorted(noms - set(themes))
    existantes = {_cle(m.terme): m for m in Memo.objects.filter(subject=subject)}
    for rang, notion in enumerate(donnees["notions"]):
        inconnus = [a for a in notion["epreuves"] if a not in donnees["epreuves"]]
        if inconnus:
            raise FichierInvalide(f"« {notion['terme']} » cite des épreuves inconnues : {inconnus}")
        lessons = [l for a in notion["epreuves"] for l in epreuves[a]]
        if not lessons:
            # Aucune épreuve retrouvée : rien ne prouve que la notion est tombée, on ne crée pas la fiche.
            bilan["ignorees"] += 1
            continue
        sessions, cursus_ids = [], set()
        for lesson in lessons:
            ids = [c.pk for c in lesson.cursus.all()]
            cursus_ids.update(ids)
            if lesson.year:
                sessions = fusionner_sessions(sessions, [{"annee": lesson.year, "origine": lesson.origine, "cursus": ids}])
        memo = existantes.get(_cle(notion["terme"]))
        if dry_run:
            bilan["creees" if memo is None else "completees"] += 1
            continue
        if memo is None:
            memo = Memo.objects.create(
                subject=subject, terme=notion["terme"], definition=notion["definition"],
                sessions=sessions, ordre=1000 + rang * 10, statut=StatutMemo.BROUILLON,
                theme=themes.get(notion.get("theme")), **_facultatifs(notion),
            )
            existantes[_cle(notion["terme"])] = memo
            bilan["creees"] += 1
        else:
            # La fiche existe déjà (extraite pour un autre examen, ou d'un import précédent) : on lui ajoute des examens et
            # des sessions. Son texte n'est réécrit que si elle vient de ce fichier et n'a été ni retouchée ni publiée.
            vient_du_fichier = memo.ordre >= 1000
            if vient_du_fichier and not memo.modifie_a_la_main and memo.statut != StatutMemo.PUBLIE:
                memo.definition = notion["definition"]
                for champ, valeur in _facultatifs(notion).items():
                    setattr(memo, champ, valeur)
                bilan["mises_a_jour"] += 1
            else:
                bilan["completees"] += 1
            memo.sessions = fusionner_sessions(memo.sessions, sessions)
            # Le rattachement n'est pas du texte relu : il complète aussi une fiche publiée, sans jamais remplacer un thème posé.
            if memo.theme_id is None:
                memo.theme = themes.get(notion.get("theme"))
            memo.save()
        memo.cursus.add(*cursus_ids)
        memo.sources.add(*lessons)
    if not dry_run:
        assurer_gratuites(subject)
    return bilan
