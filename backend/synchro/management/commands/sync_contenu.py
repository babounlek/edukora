"""
Synchronisation des contenus pédagogiques par lots (voir deploy/SPEC-SYNC-CONTENU.md).

  sync_contenu recevoir <archive.zip> [--sha256 X]   vérifie, extrait et journalise un lot (idempotent)
  sync_contenu planifier <batch_id>                  SIMULATION : classement, diff, porte de validation
  sync_contenu appliquer <batch_id> --confirme       applique (un atomic par contenu)
  sync_contenu reprendre <batch_id> --confirme       relance les seules opérations non terminées
  sync_contenu statut [<batch_id>] [--json]          état d'un lot (répond sans rien rejouer)
  sync_contenu post-traiter <batch_id>               PDF de sujet, index de recherche, fréquences (reprenable)
  sync_contenu exporter-reference [--sortie f]       empreintes appliquées en production
  sync_contenu rafraichir-journal [--confirme]       recalcule les empreintes d'état (après un changement de rendu)
  sync_contenu verifier-fichiers [--sha]             références sans fichier, SHA divergents (rapport seul)
  sync_contenu nettoyer [--apres-jours N] [--appliquer]   anciens fichiers remplacés (jamais s'ils sont référencés)

Codes de sortie : 0 succès · 1 échec certain · 2 usage · 3 indéterminé (a_verifier / en cours) · 4 conflits
ou contenus rejetés · 5 approbation ou confirmation manquante.
"""
import json
import sys

from django.core.management.base import BaseCommand, CommandError

from synchro import moteur
from synchro.models import LotSynchro, ResultatOperation as R, StatutLot

SORTIE_OK, SORTIE_ECHEC, SORTIE_USAGE, SORTIE_INDETERMINE, SORTIE_CONFLITS, SORTIE_APPROBATION = 0, 1, 2, 3, 4, 5


def _json_defaut(valeur):
    return str(valeur)


class Command(BaseCommand):
    help = "Synchronise des lots de contenus (création et mise à jour sur place, sans suppression)."

    def add_arguments(self, parser):
        sp = parser.add_subparsers(dest="action", required=True)

        p = sp.add_parser("recevoir")
        p.add_argument("archive")
        p.add_argument("--sha256", default=None)

        for nom in ("planifier", "statut"):
            p = sp.add_parser(nom)
            p.add_argument("batch_id", nargs="?" if nom == "statut" else None)
            p.add_argument("--json", action="store_true")
            if nom == "statut":
                p.add_argument("--detail", action="store_true")

        for nom in ("appliquer", "reprendre"):
            p = sp.add_parser(nom)
            p.add_argument("batch_id")
            p.add_argument("--confirme", action="store_true", help="Obligatoire : sans lui, rien n'est écrit.")
            p.add_argument("--confirme-retraits", default=None, metavar="BATCH_ID",
                           help="Doit répéter le batch_id : autorise les opérations retirer/reintegrer.")
            p.add_argument("--sans-post-traitement", action="store_true",
                           help="Ne régénère pas les PDF, l'index de recherche ni les fréquences.")
            p.add_argument("--json", action="store_true")

        p = sp.add_parser("post-traiter")
        p.add_argument("batch_id")

        p = sp.add_parser("rafraichir-journal")
        p.add_argument("--confirme", action="store_true", help="Sans lui : liste seulement ce qui changerait.")

        p = sp.add_parser("exporter-reference")
        p.add_argument("--sortie", default=None)

        p = sp.add_parser("verifier-fichiers")
        p.add_argument("--sha", action="store_true")

        p = sp.add_parser("nettoyer")
        p.add_argument("--apres-jours", type=int, default=7)
        p.add_argument("--appliquer", action="store_true")

    # ------------------------------------------------------------------ sortie

    def _emettre(self, data, as_json=True):
        self.stdout.write(json.dumps(data, ensure_ascii=False, default=_json_defaut, indent=None if as_json else 2))

    def _sortir(self, code):
        if code:
            sys.exit(code)

    def _lot(self, batch_id):
        lot = LotSynchro.objects.filter(batch_id=batch_id).first()
        if lot is None:
            raise CommandError(f"lot inconnu : {batch_id} (utiliser d'abord `recevoir`)")
        return lot

    # ------------------------------------------------------------------ actions

    def handle(self, *args, **options):
        action = options["action"].replace("-", "_")
        try:
            return getattr(self, f"_{action}")(options)
        except moteur.ErreurLot as exc:
            self.stderr.write(f"ERREUR : {exc}")
            self._emettre({"statut": "refuse", "erreur": str(exc)})
            self._sortir(SORTIE_ECHEC)

    def _recevoir(self, o):
        lot = moteur.recevoir(o["archive"], sha256_attendu=o["sha256"])
        self._emettre({"batch_id": lot.batch_id, "statut": lot.statut, "operations": lot.operations.count(),
                       "dossier": lot.dossier})

    def _planifier(self, o):
        resultat = moteur.planifier(self._lot(o["batch_id"]))
        self._emettre(resultat)
        self._sortir(SORTIE_CONFLITS if resultat["bloquants"] else SORTIE_OK)

    def _statut(self, o):
        res = moteur.statut(o["batch_id"], detail=o.get("detail", False))
        self._emettre(res)
        if isinstance(res, dict):
            if res["statut"] in (StatutLot.A_VERIFIER, StatutLot.EN_COURS):
                self._sortir(SORTIE_INDETERMINE)
            if res["statut"] in (StatutLot.ECHOUE, StatutLot.PARTIEL, "inconnu"):
                self._sortir(SORTIE_ECHEC if res["statut"] != StatutLot.PARTIEL else SORTIE_CONFLITS)

    def _appliquer(self, o, reprise=False):
        if not o["confirme"]:
            self._emettre({"statut": "refuse", "erreur": "--confirme est obligatoire"})
            self._sortir(SORTIE_APPROBATION)
        lot = self._lot(o["batch_id"])
        confirme_retraits = o.get("confirme_retraits")
        if confirme_retraits is not None and confirme_retraits != lot.batch_id:
            raise moteur.ErreurLot("--confirme-retraits doit répéter exactement le batch_id")
        resultat = moteur.appliquer(
            lot, reprise=reprise, confirme_retraits=bool(confirme_retraits),
            post_traitement=not o["sans_post_traitement"],
        )
        self._emettre(resultat)
        statut = resultat["statut"]
        if statut in (StatutLot.PARTIEL,):
            self._sortir(SORTIE_CONFLITS)
        elif statut == StatutLot.ECHOUE:
            comp = resultat.get("compteurs", {})
            conflits = sum(comp.get(r, 0) for r in moteur.BLOQUANTS if r != R.ERREUR.value)
            self._sortir(SORTIE_CONFLITS if conflits else SORTIE_ECHEC)

    def _reprendre(self, o):
        self._appliquer(o, reprise=True)

    def _post_traiter(self, o):
        resultat = moteur.post_traiter(self._lot(o["batch_id"]))
        self._emettre(resultat)
        self._sortir(SORTIE_ECHEC if resultat["avertissements"] else SORTIE_OK)

    def _rafraichir_journal(self, o):
        self._emettre(moteur.rafraichir_journal(confirme=o["confirme"]))

    def _exporter_reference(self, o):
        ref = moteur.exporter_reference()
        if o["sortie"]:
            with open(o["sortie"], "w", encoding="utf-8", newline="\n") as f:
                json.dump(ref, f, ensure_ascii=False, indent=2)
            self._emettre({"sortie": o["sortie"], "contenus": len(ref["contenus"])})
        else:
            self._emettre(ref)

    def _verifier_fichiers(self, o):
        res = moteur.verifier_fichiers(avec_sha=o["sha"])
        self._emettre(res)
        self._sortir(SORTIE_ECHEC if res["references_sans_fichier"] or res["sha_divergents"] else SORTIE_OK)

    def _nettoyer(self, o):
        self._emettre(moteur.nettoyer(o["apres_jours"], appliquer_suppression=o["appliquer"]))
