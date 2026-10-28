"""
Purge des comptes de test listés dans un fichier de périmètre (voir deploy/SPEC-PURGE-DONNEES-TEST.md).

  purger_donnees_test perimetre (--ids 3,4 | --marque)   propose un fichier de périmètre (JSON sur la sortie)
  purger_donnees_test simuler --perimetre f.json         rapport + jeton ; RIEN n'est persisté
  purger_donnees_test executer --perimetre f.json --jeton J --sauvegarde avant-X.dump --confirme-production
  purger_donnees_test verifier --perimetre f.json        après coup : plus aucun compte ciblé

La sortie standard est toujours un rapport (JSON avec --json). Hors DEBUG, `executer` exige : ALLOW_TEST_DATA=1 et
PURGE_SAUVEGARDE_VERIFIEE=<le dump> passés à la commande (`docker compose exec -e ...`, jamais dans le .env ;
la seconde est posée par deploy/purge-test.sh après avoir vérifié le dump, sa copie hors site et sa restauration),
plus --confirme-production.

Codes de sortie : 0 terminé · 1 échec (transaction annulée) · 2 garde refusée ou ambiguïté (rien d'écrit).
"""
import json
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from users import purge_test
from users.management.commands.seed_donnees_test import MARQUE_EMAIL, MARQUE_NOM, RE_EMAIL_TEST
from users.models import User

RE_DUMP = re.compile(r"^[A-Za-z0-9._-]{1,120}\.dump$")


class Command(BaseCommand):
    help = "Purge les comptes de test d'un fichier de périmètre validé (simulation par défaut, voir l'en-tête du module)."

    def add_arguments(self, parser):
        sp = parser.add_subparsers(dest="action", required=True)

        p = sp.add_parser("perimetre", help="Propose un fichier de périmètre à relire (ne supprime rien).")
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--ids", help="Ids de comptes séparés par des virgules.")
        g.add_argument("--marque", action="store_true", help="Les comptes au marqueur strict de seed_donnees_test.")

        for nom in ("simuler", "executer", "verifier"):
            p = sp.add_parser(nom)
            p.add_argument("--perimetre", required=True, help="Fichier JSON de périmètre.")
            p.add_argument("--json", action="store_true", help="Rapport en JSON sur une ligne.")
            if nom == "executer":
                p.add_argument("--jeton", required=True, help="Jeton de la simulation la plus récente.")
                p.add_argument("--sauvegarde", default="", help="Nom du dump (avant-….dump) vérifié par le script serveur.")
                p.add_argument("--confirme-production", action="store_true")

    # ------------------------------------------------------------------ entrées

    @staticmethod
    def _lire_perimetre(chemin):
        try:
            with open(chemin, encoding="utf-8-sig") as f:  # tolère le BOM que PowerShell 5.1 ajoute
                donnees = json.load(f)
        except (OSError, ValueError) as e:
            raise purge_test.Refus(f"Fichier de périmètre illisible ({e}).")
        return purge_test.charger_perimetre(donnees)

    @staticmethod
    def _comptes_marques():
        return [
            u for u in User.objects.filter(email__contains=MARQUE_EMAIL, full_name__startswith=MARQUE_NOM)
            if RE_EMAIL_TEST.match(u.email or "")
        ]

    def _garde_production(self, options):
        if settings.DEBUG:
            return
        if os.environ.get("ALLOW_TEST_DATA") != "1":
            raise purge_test.Refus(
                "Refusé : hors DEBUG, passer ALLOW_TEST_DATA=1 à la commande "
                "(docker compose exec -e ALLOW_TEST_DATA=1 ...), jamais dans le .env."
            )
        if not options["confirme_production"]:
            raise purge_test.Refus("Refusé : --confirme-production est obligatoire hors DEBUG.")
        dump = options["sauvegarde"]
        if not RE_DUMP.match(dump):
            raise purge_test.Refus("Refusé : --sauvegarde doit nommer le dump vérifié (avant-….dump).")
        if os.environ.get("PURGE_SAUVEGARDE_VERIFIEE") != dump:
            raise purge_test.Refus(
                "Refusé : cette sauvegarde n'a pas été vérifiée par deploy/purge-test.sh "
                "(PURGE_SAUVEGARDE_VERIFIEE absent ou différent)."
            )

    # ------------------------------------------------------------------ sorties

    def _afficher(self, rapport, en_json):
        if en_json:
            self.stdout.write(json.dumps(rapport, ensure_ascii=False, sort_keys=True, default=str))
            return
        self.stdout.write(f"Mode : {rapport['mode']} — statut : {rapport['statut']}")
        if "comptes" in rapport:
            c = rapport["comptes"]
            self.stdout.write(
                f"Comptes : {c['cibles']} ciblé(s), {c['presents']} présent(s), "
                f"{len(c['ignores_absents'])} déjà absent(s) (ignorés), {c['supprimes']} supprimé(s)."
            )
            verbe = "supprimées" if rapport["mode"] == "executer" else "qui seraient supprimées (simulation)"
            for modele, n in rapport["lignes_par_modele"].items():
                self.stdout.write(f"  {modele}: {n}")
            self.stdout.write(f"Lignes {verbe} : {sum(rapport['lignes_par_modele'].values())}")
            self.stdout.write(f"Conservés : {rapport['conserves']}")
            for f in rapport["fichiers_d_usage_listes_non_supprimes"]:
                self.stdout.write(f"  fichier d'usage (non supprimé) : {f}")
            for a in rapport["avertissements"]:
                self.stdout.write(self.style.WARNING(f"  avertissement : {a}"))
            for r in rapport["refus"]:
                self.stdout.write(self.style.ERROR(f"  REFUS : {r}"))
            if rapport.get("jeton"):
                self.stdout.write(f"Jeton : {rapport['jeton']}")
        else:
            self.stdout.write(f"Comptes restants : {rapport['comptes_restants']}")

    # ------------------------------------------------------------------ exécution

    def handle(self, *args, **options):
        action = options["action"]
        en_json = options.get("json", False)
        try:
            if action == "perimetre":
                if options["ids"]:
                    try:
                        ids = [int(i) for i in options["ids"].split(",") if i.strip()]
                    except ValueError:
                        raise purge_test.Refus("--ids : entiers séparés par des virgules.")
                    users = list(User.objects.filter(pk__in=ids))
                else:
                    users = self._comptes_marques()
                self.stdout.write(json.dumps(purge_test.proposer_perimetre(users), ensure_ascii=False, indent=2))
                return
            perimetre = self._lire_perimetre(options["perimetre"])
            if action == "simuler":
                rapport = purge_test.simuler(perimetre)
                self._afficher(rapport, en_json)
                if rapport["refus"]:
                    raise CommandError("Simulation refusée : voir les REFUS ci-dessus.", returncode=2)
            elif action == "executer":
                self._garde_production(options)
                rapport = purge_test.executer(perimetre, options["jeton"])
                self._afficher(rapport, en_json)
            else:
                rapport = purge_test.verifier(perimetre)
                self._afficher(rapport, en_json)
                if rapport["statut"] != "ok":
                    raise CommandError("Des comptes ciblés existent encore.", returncode=1)
        except purge_test.Refus as e:
            self.stdout.write(json.dumps({"statut": "refuse", "erreur": str(e)}, ensure_ascii=False))
            raise CommandError(str(e), returncode=2)
        except purge_test.Echec as e:
            self.stdout.write(json.dumps({"statut": "echec", "erreur": str(e)}, ensure_ascii=False))
            raise CommandError(str(e), returncode=1)
