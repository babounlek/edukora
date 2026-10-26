"""
Adaptateurs par type de contenu : tout ce que le moteur doit savoir d'un exercice, d'un cours ou
d'un item de quiz sans connaître leurs modèles. Chacun RÉUTILISE l'ingestion existante
(`catalog.ingestion`, `quiz.ingestion`) pour la création et la mise à jour : aucune règle de
normalisation n'est réécrite ici.

Interface commune : charger / retrouver / projeter / structure_modifiee / appliquer / porte /
retirer / reintegrer / lessons_touchees.
"""
import copy
from pathlib import Path

from catalog.ingestion import (
    ContexteSync,
    IngestionError,
    chercher_exercice_existant,
    ingest_cours,
    ingest_exercise,
    mettre_a_jour_cours,
)
from catalog.models import Cours, Exercise, Lesson, StatutContenu
from catalog.tunnel import _TITRE_RAPPEL
from quiz.ingestion import (
    _country_code_from_quiz_ingest_path,
    _resolve_country,
    ingest_competence_item,
    mettre_a_jour_item,
)
from quiz.models import CompetenceItem

from . import empreintes as emp
from . import projection as proj


class AdaptateurErreur(Exception):
    """Erreur attribuable au contenu du lot (JSON, référence introuvable...), jamais au moteur."""


class Contexte:
    def __init__(self, entry, data, chemin_json):
        self.entry = entry
        self.data = data
        self.chemin_json = chemin_json
        self.source_dir = chemin_json.parent


def chemin_dans_lot(racine_lot, rel):
    """Chemin d'un fichier du lot, confiné à `<lot>/ingest` (ni absolu, ni `..`, ni lien sortant)."""
    base = (Path(racine_lot) / "ingest").resolve()
    if not rel or Path(rel).is_absolute() or rel.startswith(("/", "\\")):
        raise AdaptateurErreur(f"chemin refusé (absolu ou vide) : {rel!r}")
    chemin = (base / rel).resolve()
    if base not in chemin.parents:
        raise AdaptateurErreur(f"chemin refusé (hors du lot) : {rel!r}")
    return chemin


def _charger_fichier(entry, racine_lot):
    chemin = chemin_dans_lot(racine_lot, entry["fichier"])
    if not chemin.is_file():
        raise AdaptateurErreur(f"fichier du lot introuvable : {entry['fichier']}")
    try:
        data, _ = emp.lire_json(chemin)
    except ValueError as exc:
        raise AdaptateurErreur(f"{entry['fichier']} : {exc}") from exc
    return data, chemin


class _Base:
    type = ""

    def charger(self, entry, racine_lot):
        data, chemin = _charger_fichier(entry, racine_lot)
        return Contexte(entry, copy.deepcopy(data), chemin)

    def structure_modifiee(self, obj, ctx):
        return []

    def porte(self, obj):
        """Ensemble de raisons BLOQUANTES portées par l'objet (vide = rien à signaler)."""
        return set()

    def lessons_touchees(self, obj):
        return set()

    def retrouver_par_cle(self, cle):
        """L'objet désigné par sa clé naturelle seule (retrait d'un contenu jamais journalisé), ou None."""
        return None

    def _statut(self, obj, statut):
        obj.statut = statut
        obj.save(update_fields=["statut", "updated_at"])

    def retirer(self, obj):
        self._statut(obj, StatutContenu.REJETE)

    def reintegrer(self, obj):
        self._statut(obj, StatutContenu.VALIDE)


class ExerciceAdaptateur(_Base):
    type = emp.TYPE_EXERCICE
    modele = Exercise

    def retrouver_par_cle(self, cle):
        try:
            return chercher_exercice_existant(cle, None, pays=cle.get("pays") or None)
        except (IngestionError, KeyError, ValueError):
            return None

    def retrouver(self, ctx):
        try:
            return chercher_exercice_existant(ctx.data, ctx.source_dir)
        except (IngestionError, KeyError, ValueError) as exc:
            raise AdaptateurErreur(f"{ctx.entry['fichier']} : {exc}") from exc

    def projeter(self, obj):
        return proj.projeter_exercice(obj)

    def structure_modifiee(self, obj, ctx):
        """Éléments présents en base mais absents du JSON : jamais supprimés (cascade sur les copies élèves)."""
        problemes = []
        numeros_json = {str(q.get("numero") or i) for i, q in enumerate(ctx.data.get("questions") or [], start=1)}
        for q in obj.questions.all():
            if q.numero not in numeros_json:
                problemes.append(f"question {q.numero} absente du JSON (suppression refusée)")
        ids_figures = {
            (f.get("id") or f"fig-{i}")
            for i, f in enumerate(ctx.data.get("figures") or [], start=1)
            if isinstance(f, dict) and (f.get("fichier") or f.get("nom_fichier"))
        }
        for fig in obj.figures.all():
            if fig.external_id not in ids_figures:
                problemes.append(f"figure {fig.external_id} absente du JSON (suppression refusée)")
        ids_rappels = {
            r.get("id")
            for q in ctx.data.get("questions") or []
            for r in (q.get("rappels_de_methode") or [])
            if isinstance(r, dict) and r.get("id")
        }
        for r in obj.rappels_de_methode.all():
            if ids_rappels and r.external_id not in ids_rappels:
                problemes.append(f"rappel {r.external_id} absent du JSON (suppression refusée)")
        return problemes

    def appliquer(self, ctx, obj, sync):
        try:
            exercice, cree = ingest_exercise(
                ctx.data, source_dir=ctx.source_dir, exiger_themes=True, sync=sync,
            )
        except IngestionError as exc:
            raise AdaptateurErreur(f"{ctx.entry['fichier']} : {exc}") from exc
        return exercice, cree

    def porte(self, obj):
        """
        Mêmes règles BLOQUANTES que `catalog.tunnel.blocked_lessons`, mais bornées à CET exercice :
        un défaut hérité d'un autre exercice de la même épreuve ne doit ni bloquer l'ajout d'un
        exercice sain, ni passer inaperçu s'il vient de cet exercice.
        """
        raisons = set()
        sans_theme = [q.numero for q in obj.questions.filter(themes__isnull=True)]
        if sans_theme:
            raisons.add(f"{len(sans_theme)} question(s) sans thème (ex. {', '.join(sans_theme[:5])})")
        if obj.rappels_de_methode.exists() and not _TITRE_RAPPEL.findall(obj.corrige_markdown or ""):
            raisons.add("rappel(s) de méthode jamais affiché(s) (aucun titre `### Rappel de méthode` dans le corrigé)")
        for q in obj.questions.filter(type_reponse="QCM"):
            lettres = {c.get("lettre") for c in (q.choix or []) if isinstance(c, dict)}
            if len(lettres) < 2 or q.reponse_correcte not in lettres:
                raisons.add(f"question {q.numero} : QCM incohérent")
        return raisons

    def lessons_touchees(self, obj):
        return {obj.lesson_id}

    def _statut(self, obj, statut):
        super()._statut(obj, statut)
        obj.lesson.compile_from_exercises()


class CoursAdaptateur(_Base):
    type = emp.TYPE_COURS
    modele = Cours

    def retrouver_par_cle(self, cle):
        cours_id = str(cle.get("cours_id") or "").strip()
        return Cours.objects.filter(external_id=cours_id).first() if cours_id else None

    def retrouver(self, ctx):
        cours_id = str(ctx.data.get("cours_id") or "").strip()
        return Cours.objects.filter(external_id=cours_id).first() if cours_id else None

    def projeter(self, obj):
        return proj.projeter_cours(obj)

    def appliquer(self, ctx, obj, sync):
        try:
            if obj is None:
                cours, cree = ingest_cours(ctx.data, source_dir=ctx.source_dir)
                if not cree:
                    # Dédoublonné par titre (ou ébauche absorbée) : rien n'est créé sous cet identifiant.
                    raise _Doublon(cours)
                return cours, True
            return mettre_a_jour_cours(obj, ctx.data), False
        except IngestionError as exc:
            raise AdaptateurErreur(f"{ctx.entry['fichier']} : {exc}") from exc

    def porte(self, obj):
        raisons = set()
        if not obj.sections_raw or not (obj.content_markdown or "").strip():
            raisons.add("cours sans section ou sans contenu compilé")
        return raisons


class QuizAdaptateur(_Base):
    type = emp.TYPE_QUIZ
    modele = CompetenceItem

    def retrouver_par_cle(self, cle):
        external_id = str(cle.get("external_id") or "").strip()
        return CompetenceItem.objects.filter(external_id=external_id).first() if external_id else None

    def charger(self, entry, racine_lot):
        data, chemin = _charger_fichier(entry, racine_lot)
        items = data if isinstance(data, list) else [data]
        trouves = [i for i in items if isinstance(i, dict) and str(i.get("external_id") or "").strip() == entry["id_stable"]]
        if len(trouves) != 1:
            raise AdaptateurErreur(f"{entry['fichier']} : item {entry['id_stable']} introuvable ou en double")
        element = copy.deepcopy(trouves[0])
        # Ids de la base LOCALE : ne désignent pas les mêmes exercices en production.
        element.pop("source_exercises", None)
        return Contexte(entry, element, chemin)

    def retrouver(self, ctx):
        external_id = str(ctx.data.get("external_id") or "").strip()
        return CompetenceItem.objects.filter(external_id=external_id).first() if external_id else None

    def projeter(self, obj):
        return proj.projeter_item(obj)

    def _pays(self, ctx):
        try:
            return _resolve_country(_country_code_from_quiz_ingest_path(ctx.chemin_json))
        except IngestionError as exc:
            raise AdaptateurErreur(f"{ctx.entry['fichier']} : {exc}") from exc

    def appliquer(self, ctx, obj, sync):
        pays = self._pays(ctx)
        try:
            if obj is None:
                return ingest_competence_item(ctx.data, pays, source_dir=ctx.source_dir, sync=sync)
            return mettre_a_jour_item(obj, ctx.data, pays, source_dir=ctx.source_dir, sync=sync), False
        except IngestionError as exc:
            raise AdaptateurErreur(f"{ctx.entry['fichier']} : {exc}") from exc

    def porte(self, obj):
        raisons = set()
        if obj.type_reponse == "QCM":
            lettres = {str(c.get("lettre", "")).lower() for c in (obj.choix or []) if isinstance(c, dict)}
            if not lettres or str(obj.reponse_correcte).lower() not in lettres:
                raisons.add("QCM incohérent (réponse correcte absente des choix)")
        return raisons


class LeconAdaptateur(_Base):
    """Une épreuve entière (Lesson). Jamais créée ni modifiée par un lot : seulement retirée (REJETE) ou réintégrée,
    par sa clé naturelle `epreuve_source` (+ `annee` si l'épreuve source est ambiguë)."""

    type = emp.TYPE_LECON
    modele = Lesson

    def retrouver_par_cle(self, cle):
        source = str(cle.get("epreuve_source") or "").strip()
        if not source:
            return None
        qs = Lesson.objects.filter(epreuve_source=source)
        if cle.get("annee"):
            qs = qs.filter(year=int(cle["annee"]))
        trouvees = list(qs[:2])
        return trouvees[0] if len(trouvees) == 1 else None  # ambiguë ou absente : jamais de choix au hasard


class _Doublon(Exception):
    def __init__(self, existant):
        super().__init__("doublon")
        self.existant = existant


ADAPTATEURS = {
    emp.TYPE_EXERCICE: ExerciceAdaptateur(),
    emp.TYPE_COURS: CoursAdaptateur(),
    emp.TYPE_QUIZ: QuizAdaptateur(),
    emp.TYPE_LECON: LeconAdaptateur(),
}

DoublonCours = _Doublon
