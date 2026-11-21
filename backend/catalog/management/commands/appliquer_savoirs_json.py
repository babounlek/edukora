"""
Applique aux Question DÉJÀ en base le seul champ `savoir_officiel` lu dans les JSON d'ingestion.

Pourquoi une commande à part : la chaîne de lots (edukora.ps1 / sync_contenu) pousse un exercice
ENTIER. Quand les JSON locaux diffèrent de la production par autre chose (thèmes normalisés autrement,
figures nettoyées, corrigés retouchés), le rattachement au programme officiel reste bloqué derrière
ces écarts. Ici, un seul champ voyage : ni thèmes, ni figures, ni énoncés, ni corrigés, ni points.

Garanties :
- SIMULATION par défaut ; rien n'est écrit sans `--ecrire`.
- Ne remplit que les savoirs VIDES : un rattachement existant, même différent du JSON, n'est jamais
  touché (il est seulement signalé).
- Même clé d'identification que l'ingestion (`chercher_exercice_existant`, puis le numéro de la
  question) : jamais de création, jamais de rapprochement approximatif.
- Une référence qui ne se résout pas dans le référentiel (`_resolve_savoir_officiel`) est signalée
  et ignorée, jamais devinée.
- `--exporter-vers FICHIER` n'écrit rien en base : il produit un petit fichier (identifiants + savoirs seulement) à envoyer
  au serveur, qui n'a pas les JSON d'ingestion. La commande lit indifféremment un dossier de JSON ou ce fichier d'export.
- `--lier-themes` (facultatif) fait aussi progresser Tag.savoir_officiel comme le fait l'ingestion,
  avec les mêmes gardes ; il ne lit que les thèmes DÉJÀ posés sur la question en base.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.ingestion import (
    IngestionError, _country_code_from_path, _link_tags_to_savoir, _resolve_country, _resolve_savoir_officiel,
    _resolve_subject, chercher_exercice_existant,
)


def _matiere_du_referentiel(subject, brut):
    """Matière sous laquelle le référentiel range ce module. Les épreuves dont la matière est « Histoire-Géographie » (HISTOIRE_GEO)
    n'ont aucun module : le référentiel range l'Histoire sous HISTOIRE (modules H…) et la Géographie sous GEOGRAPHIE (modules G…).
    Le préfixe du module décide, jamais autre chose ; sans préfixe reconnu, la matière de l'exercice reste inchangée."""
    from catalog.models import Subject

    if subject.code != "HISTOIRE_GEO" or not isinstance(brut, dict):
        return subject
    code = {"H": "HISTOIRE", "G": "GEOGRAPHIE"}.get(str(brut.get("module_numero") or "").strip()[:1].upper())
    if code is None:
        return subject
    return Subject.objects.filter(country=subject.country, code=code).first() or subject


class Command(BaseCommand):
    help = "Applique le seul champ savoir_officiel des JSON d'ingestion aux questions déjà en base (simulation par défaut)."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Fichier JSON ou dossier (recherche récursive, dossiers « _ » exclus).")
        parser.add_argument("--ecrire", action="store_true", help="Écrit réellement. Sans cette option : simulation.")
        parser.add_argument("--lier-themes", action="store_true", help="Lie aussi les thèmes de la question au savoir (mêmes gardes que l'ingestion).")
        parser.add_argument("--rapport-json", help="Écrit le rapport détaillé dans ce fichier JSON.")
        parser.add_argument("--exporter-vers", help="N'applique rien : écrit dans ce fichier l'export compact (identifiants + savoirs) des JSON lus.")

    def handle(self, *args, **options):
        racine = Path(options["path"])
        if not racine.exists():
            raise CommandError(f"Chemin introuvable : {racine}")
        ecrire = options["ecrire"]
        fichiers = (
            [racine] if racine.is_file()
            else sorted(
                f for f in racine.rglob("*.json")
                if not any(part.startswith("_") for part in f.relative_to(racine).parts)
            )
        )
        _resolve_country.cache_clear()
        _resolve_subject.cache_clear()
        if options["exporter_vers"]:
            return self._exporter(racine, fichiers, options["exporter_vers"])

        compteurs = {
            "fichiers": 0, "exercices_introuvables": 0, "questions_vides_json": 0, "appliquees": 0,
            "deja_ok": 0, "conserve_different": 0, "question_introuvable": 0, "reference_invalide": 0, "themes_lies": 0,
        }
        details = []
        for fichier in fichiers:
            try:
                brut = json.loads(fichier.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                details.append({"fichier": str(fichier), "probleme": "JSON illisible"})
                continue
            for data in brut if isinstance(brut, list) else [brut]:
                # Un exercice porte `questions` ; un cours porte `sections` (jamais traité ici).
                if not isinstance(data, dict) or "sections" in data or not isinstance(data.get("questions"), list):
                    continue
                compteurs["fichiers"] += 1
                self._traiter(fichier, data, ecrire, options["lier_themes"], compteurs, details)

        mode = "ÉCRITURE" if ecrire else "SIMULATION (rien n'est écrit)"
        self.stdout.write(self.style.MIGRATE_HEADING(f"appliquer_savoirs_json : {mode}"))
        for cle, valeur in compteurs.items():
            self.stdout.write(f"  {cle:24} {valeur}")
        if options["rapport_json"]:
            Path(options["rapport_json"]).write_text(
                json.dumps({"mode": "ecriture" if ecrire else "simulation", "compteurs": compteurs, "details": details},
                           ensure_ascii=False, indent=1),
                encoding="utf-8",
            )

    def _exporter(self, racine, fichiers, sortie):
        """Export compact : de quoi RETROUVER chaque exercice et poser ses savoirs, rien d'autre (pas de texte)."""
        export = []
        for fichier in fichiers:
            try:
                brut = json.loads(fichier.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            pays = _country_code_from_path(fichier)
            for data in brut if isinstance(brut, list) else [brut]:
                if not isinstance(data, dict) or "sections" in data or not isinstance(data.get("questions"), list):
                    continue
                questions = [
                    {"numero": str(q.get("numero") or ordre), "savoir_officiel": q["savoir_officiel"]}
                    for ordre, q in enumerate(data["questions"], start=1) if q.get("savoir_officiel")
                ]
                if not questions or not pays:
                    continue
                entree = {cle: data[cle] for cle in ("epreuve_source", "numero_exercice", "matiere", "annee", "variante_sujet", "numero_paper") if data.get(cle) not in (None, "")}
                export.append({**entree, "pays": pays, "fichier": fichier.name, "questions": questions})
        # Garde-fou : deux fichiers qui désignent le MÊME exercice (même épreuve source, même numéro) mais dont les questions
        # n'ont pas les mêmes numéros sont ambigus - c'est le cas d'une épreuve dont les exercices se répètent sous les numéros
        # 1 et 2. Appliquer l'un des deux poserait un savoir sur la question d'un AUTRE exercice : ils sont exclus et signalés.
        def identite(e):
            return (e["pays"], e.get("epreuve_source"), e.get("matiere"), e.get("annee"), e.get("variante_sujet"), e.get("numero_paper"), e.get("numero_exercice"))

        groupes = {}
        for entree in export:
            groupes.setdefault(identite(entree), []).append(entree)
        ambigus = set()
        for cle, entrees in groupes.items():
            if len(entrees) > 1 and len({tuple(sorted(q["numero"] for q in e["questions"])) for e in entrees}) > 1:
                ambigus.update(id(e) for e in entrees)
                self.stdout.write(self.style.WARNING(
                    f"AMBIGU (même exercice, questions différentes), exclu de l'export : {[e['fichier'] for e in entrees]}"))
        export = [e for e in export if id(e) not in ambigus]
        Path(sortie).write_text(json.dumps(export, ensure_ascii=False), encoding="utf-8")
        self.stdout.write(f"Export : {len(export)} exercice(s) avec au moins un savoir -> {sortie} ({len(ambigus)} exclu(s) pour ambiguïté)")

    def _lier_themes(self, question, savoir, ecrire, compteurs):
        """Propage le savoir aux THÈMES (Tag) de la question, avec les gardes de l'ingestion (jamais d'écrasement, tags structurels, tags
        partagés entre cursus, conflit avec un autre savoir). Ce sont eux que lisent les écrans de l'élève (cours proposé, chapitre,
        parcours). En simulation, la liaison est faite puis ANNULÉE : le compteur dit ce qui serait lié, rien n'est écrit."""
        tags = list(question.themes.all())
        sans_savoir = {t.pk for t in tags if t.savoir_officiel_id is None}
        if not sans_savoir:
            return
        point = transaction.savepoint()
        _link_tags_to_savoir(tags, savoir, exclude_question=question)
        compteurs["themes_lies"] += sum(1 for t in tags if t.pk in sans_savoir and t.savoir_officiel_id is not None)
        if ecrire:
            transaction.savepoint_commit(point)
        else:
            transaction.savepoint_rollback(point)

    def _traiter(self, fichier, data, ecrire, lier_themes, compteurs, details):
        pays = data.get("pays") or _country_code_from_path(fichier)
        try:
            exercice = chercher_exercice_existant(data, fichier, pays=pays)
            country = _resolve_country(pays)
            subject = _resolve_subject(data["matiere"], country)
        except (IngestionError, KeyError, ValueError) as exc:
            compteurs["exercices_introuvables"] += 1
            details.append({"fichier": fichier.name, "probleme": f"exercice non identifiable : {exc}"})
            return
        if exercice is None:
            compteurs["exercices_introuvables"] += 1
            details.append({"fichier": fichier.name, "probleme": "exercice absent de la base"})
            return

        with transaction.atomic():
            for ordre, q_data in enumerate(data["questions"], start=1):
                brut = q_data.get("savoir_officiel")
                if not brut:
                    compteurs["questions_vides_json"] += 1
                    continue
                try:
                    savoir = _resolve_savoir_officiel(brut, _matiere_du_referentiel(subject, brut))
                except IngestionError as exc:
                    compteurs["reference_invalide"] += 1
                    details.append({"fichier": fichier.name, "question": str(q_data.get("numero") or ordre), "probleme": str(exc)[:200]})
                    continue
                numero = str(q_data.get("numero") or ordre)
                question = exercice.questions.filter(numero=numero).first()
                if question is None:
                    compteurs["question_introuvable"] += 1
                    details.append({"fichier": fichier.name, "question": numero, "probleme": "question absente de la base"})
                    continue
                if question.savoir_officiel_id == savoir.pk:
                    compteurs["deja_ok"] += 1
                    if lier_themes:
                        self._lier_themes(question, savoir, ecrire, compteurs)
                    continue
                if question.savoir_officiel_id is not None:
                    compteurs["conserve_different"] += 1
                    details.append({"fichier": fichier.name, "question": numero, "probleme": "savoir déjà posé, différent du JSON : conservé"})
                    continue
                compteurs["appliquees"] += 1
                if ecrire:
                    question.savoir_officiel = savoir
                    question.save(update_fields=["savoir_officiel", "updated_at"])
                if lier_themes:
                    self._lier_themes(question, savoir, ecrire, compteurs)
