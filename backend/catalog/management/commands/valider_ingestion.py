"""
Tunnel de validation post-ingestion (côté base). À lancer après CHAQUE round
d'ingestion (correction-experte, concepteur-quiz-competence, concepteur-epreuve-inedite).

    python manage.py valider_ingestion --since 2h
    python manage.py valider_ingestion --since 2026-09-18T10:00 --strict

Enchaîne trois portes sur le contenu créé/modifié depuis --since : structure (Question
sans thème, QCM incohérent), vocabulaire de thèmes (quasi-doublons de Tag, thèmes
partagés entre matières) et delta de couverture (quiz/cours manquants). Écrit aussi le
dump de rendu restreint à ce périmètre (--dump) pour la 4e porte, le vrai moteur KaTeX,
qui tourne côté frontend : utiliser scripts/tunnel_validation.sh qui enchaîne les deux.

Code de sortie != 0 s'il reste un BLOQUANT (ou une ALERTE avec --strict).
"""

import json
import os

from django.core.management.base import BaseCommand, CommandError

from catalog.tunnel import ALERTE, BLOQUANT, collect_rendering_records, parse_since, run_db_gates


MAX_LIGNES = 15


class Command(BaseCommand):
    help = "Valide le contenu ingéré depuis --since (structure, thèmes, couverture) et écrit le dump de rendu associé."

    def add_arguments(self, parser):
        parser.add_argument("--since", required=True, help="90m, 2h, 1d ou datetime ISO 8601.")
        parser.add_argument("--strict", action="store_true", help="Les ALERTE font aussi échouer la commande.")
        parser.add_argument(
            "--dump", default="/app/ingest/_audit/rendu_tunnel.json",
            help="Dump de rendu restreint au périmètre, pour vitest (défaut : dossier _audit, hors corpus).",
        )

    def handle(self, *args, **options):
        try:
            since = parse_since(options["since"])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        findings, counts = run_db_gates(since)

        self.stdout.write(f"Périmètre : contenu modifié depuis {since:%Y-%m-%d %H:%M} - " + ", ".join(f"{n} {k}" for k, n in counts.items()))
        if not any(counts.values()):
            raise CommandError("Périmètre vide : rien n'a été créé/modifié depuis cet instant (--since trop récent ?).")

        for severity in (BLOQUANT, ALERTE, "INFO"):
            style = {BLOQUANT: self.style.ERROR, ALERTE: self.style.WARNING}.get(severity, str)
            lignes = [f"[{severity}] ({f.gate}) {f.message}" for f in findings if f.severity == severity]
            for ligne in lignes[:MAX_LIGNES]:
                self.stdout.write(style(ligne))
            if len(lignes) > MAX_LIGNES:
                self.stdout.write(style(f"[{severity}] ... +{len(lignes) - MAX_LIGNES} autre(s), non affiché(s)"))

        records = collect_rendering_records(since)
        os.makedirs(os.path.dirname(options["dump"]), exist_ok=True)
        with open(options["dump"], "w", encoding="utf-8") as fh:
            json.dump(records, fh, ensure_ascii=False, indent=2)
        self.stdout.write(f"Dump de rendu : {len(records)} enregistrement(s) -> {options['dump']}")

        bloquants = [f for f in findings if f.severity == BLOQUANT or (options["strict"] and f.severity == ALERTE)]
        if bloquants:
            raise CommandError(f"{len(bloquants)} point(s) bloquant(s) - tunnel NON validé.")
        self.stdout.write(self.style.SUCCESS("Portes base OK (le rendu KaTeX reste à valider : scripts/tunnel_validation.sh)."))
