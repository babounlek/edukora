"""
Rétro-remplit le barème exact (points + grille de critères) des questions d'épreuves
inédites déjà en base, puis reporte le même barème dans le JSON source de l'épreuve -
sans ce second geste, une ré-ingestion depuis ingest/_inedit/ ferait revenir la
plateforme au « barème estimé ».

Un fichier de barème par épreuve :

    {"epreuve": "ep-cm-pct-bepc-1-2026-s1",
     "questions": [
        {"exercice": "1", "numero": "1", "points": 1,
         "criteres_notation": [{"libelle": "Définition correcte", "points": 0.5}, ...]},
        ...]}

Toutes les questions de l'épreuve doivent y figurer (jamais un barème à moitié renseigné :
voir inedit.bareme). Rien n'est écrit tant qu'une épreuve a une anomalie ; --dry-run
contrôle sans rien écrire. `--verifier` (sans chemin) contrôle toutes les épreuves publiées.
"""

import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from inedit import bareme
from inedit.models import EpreuveInedite


def _charger(fichier):
    try:
        return json.loads(fichier.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CommandError(f"{fichier} illisible : {exc}") from exc


def _fichiers(chemin):
    chemin = Path(chemin)
    if not chemin.exists():
        raise CommandError(f"Chemin introuvable : {chemin}")
    return [chemin] if chemin.is_file() else sorted(chemin.rglob("*.json"))


def _source_json(external_id):
    racine = Path(settings.BASE_DIR) / "ingest" / "_inedit"
    trouves = [p for p in racine.rglob(f"{external_id}.json") if "_bareme" not in p.parts]
    return trouves[0] if len(trouves) == 1 else None


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="?", help="Fichier ou dossier de fichiers de barème (.json).")
        parser.add_argument("--dry-run", action="store_true", help="Contrôle sans rien écrire.")
        parser.add_argument(
            "--verifier", action="store_true",
            help="Contrôle le barème de toutes les épreuves publiées (aucun fichier attendu).",
        )

    def handle(self, *args, **options):
        if options["verifier"]:
            return self._verifier()
        if not options["path"]:
            raise CommandError("Indiquez un chemin, ou --verifier.")

        erreurs = 0
        for fichier in _fichiers(options["path"]):
            data = _charger(fichier)
            if not isinstance(data, dict) or "epreuve" not in data:
                continue  # autre JSON rangé dans le dossier
            try:
                self._appliquer(data, dry_run=options["dry_run"])
            except (ValueError, CommandError) as exc:
                erreurs += 1
                self.stderr.write(self.style.ERROR(f"{fichier.name} : {exc}"))
        if erreurs:
            raise CommandError(f"{erreurs} épreuve(s) refusée(s), voir ci-dessus - aucune n'a été partiellement écrite.")

    def _appliquer(self, data, *, dry_run):
        external_id = data["epreuve"]
        epreuve = EpreuveInedite.objects.filter(external_id=external_id).first()
        if epreuve is None:
            raise ValueError(f"épreuve {external_id!r} introuvable en base.")

        par_cle = {}
        for entree in data.get("questions") or []:
            cle = (str(entree.get("exercice")), str(entree.get("numero")))
            if cle in par_cle:
                raise ValueError(f"question {cle} en double dans le fichier.")
            par_cle[cle] = entree

        with transaction.atomic():
            questions = []
            for exercice in epreuve.exercices.prefetch_related("questions").order_by("numero_exercice"):
                for question in exercice.questions.all():
                    cle = (exercice.numero_exercice, question.numero)
                    entree = par_cle.pop(cle, None)
                    if entree is None:
                        raise ValueError(f"exercice {cle[0]}, question {cle[1]} : barème absent du fichier.")
                    contexte = f"exercice {cle[0]}, question {cle[1]}"
                    question.points = bareme.lire_points(entree.get("points"), contexte)
                    question.criteres_notation = bareme.normaliser_criteres(entree.get("criteres_notation"), contexte)
                    bareme.verifier_question(
                        question.points, question.criteres_notation, question.type_reponse, contexte,
                    )
                    questions.append(question)
            if par_cle:
                raise ValueError(f"questions inconnues dans le fichier : {sorted(par_cle)}.")

            for exercice in epreuve.exercices.all():
                bareme.verifier_exercice(
                    exercice.points,
                    {q.numero: q.points for q in questions if q.exercice_id == exercice.id},
                    f"exercice {exercice.numero_exercice}",
                )
            for question in questions:
                question.save(update_fields=["points", "criteres_notation"])

            anomalies = bareme.verifier_epreuve(epreuve)
            if anomalies:
                raise ValueError(" | ".join(anomalies))
            if dry_run:
                transaction.set_rollback(True)

        total = sum((q.points for q in questions), Decimal("0"))
        if dry_run:
            self.stdout.write(f"{external_id} : conforme ({len(questions)} questions, {total} pt) - dry-run, rien écrit.")
            return
        self._reporter_dans_la_source(external_id, questions)
        self.stdout.write(self.style.SUCCESS(f"{external_id} : {len(questions)} questions, {total} pt."))

    def _reporter_dans_la_source(self, external_id, questions):
        """Copie le barème dans le JSON source pour qu'une ré-ingestion le retrouve."""
        source = _source_json(external_id)
        if source is None:
            self.stdout.write(self.style.WARNING(f"  {external_id} : JSON source introuvable, non mis à jour."))
            return
        contenu = _charger(source)
        par_cle = {(q.exercice.numero_exercice, q.numero): q for q in questions}
        for exercice in contenu.get("exercices", []):
            for entree in exercice.get("questions", []):
                question = par_cle.get((str(exercice["numero_exercice"]), str(entree["numero"])))
                if question is None:
                    continue
                entree["points"] = float(question.points)
                if question.criteres_notation:
                    entree["criteres_notation"] = question.criteres_notation
                else:
                    entree.pop("criteres_notation", None)
        source.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _verifier(self):
        anomalies = bareme.verifier_epreuves_validees()
        total = EpreuveInedite.objects.filter(statut="VALIDE").count()
        if not anomalies:
            self.stdout.write(self.style.SUCCESS(f"Barème conforme sur les {total} épreuve(s) publiée(s)."))
            return
        for external_id, messages in anomalies.items():
            self.stdout.write(self.style.ERROR(external_id))
            for message in messages:
                self.stdout.write(f"  - {message}")
        raise CommandError(f"{len(anomalies)} épreuve(s) publiée(s) sur {total} avec un barème incomplet ou incohérent.")
