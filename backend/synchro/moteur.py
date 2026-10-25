"""
Moteur de synchronisation des contenus (voir deploy/SPEC-SYNC-CONTENU.md).

Cycle d'un lot : `recevoir` (archive vérifiée, extraite, journalisée) -> `planifier` (simulation,
aucune écriture) -> `appliquer` (un `atomic()` par contenu) -> `statut`. Un lot rejoué ne fait rien ;
`reprendre` n'exécute que les opérations non terminées.

Invariants (testés) :
  - jamais de suppression de ligne pendant un lot (garde `GardeEcritures`) ni de fichier (seul
    `nettoyer`, à part, supprime un fichier, et seulement s'il n'est plus référencé nulle part) ;
  - jamais d'écriture hors de la liste fermée des modèles pédagogiques ;
  - `statut`, `published_at`, `est_vitrine` d'un contenu existant ne sont jamais modifiés par une
    mise à jour (seule l'opération explicite `retirer` / `reintegrer` change le statut) ;
  - un contenu modifié en production par un autre mécanisme n'est jamais écrasé sans décision
    humaine liée à l'empreinte d'état que l'humain a vue ET à la version proposée.
"""
import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.db import connection, models as dj_models, transaction
from django.db.models.functions import Cast
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.db.migrations.recorder import MigrationRecorder
from django.utils import timezone

from catalog.ingestion import ContexteSync, IngestionError
from catalog.models import Lesson, StatutContenu
from catalog.sujet_pdf import generate_sujet_pdf, sujet_pdf_filename

from . import empreintes as emp
from . import projection as proj
from .adaptateurs import ADAPTATEURS, AdaptateurErreur, DoublonCours, chemin_dans_lot
from .models import (
    ContenuSynchro,
    LotSynchro,
    OperationSynchro,
    ResultatOperation as R,
    STATUTS_TERMINES_REUSSIS,
    StatutLot,
)

SCHEMA_SYNC_SUPPORTE = 1
VERROU_ID = 727368  # pg_advisory_lock : un seul lot appliqué à la fois
SEUIL_BATTEMENT = timedelta(seconds=90)
RE_BATCH_ID = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{8}$")
ORDRE_TYPES = {emp.TYPE_EXERCICE: 0, emp.TYPE_COURS: 1, emp.TYPE_QUIZ: 2}

LABELS_ECRITURE_AUTORISES = frozenset({
    "catalog.Exercise", "catalog.Question", "catalog.Figure", "catalog.RappelDeMethode", "catalog.Cours",
    "catalog.Tag", "catalog.Lesson", "quiz.CompetenceItem", "quiz.CompetenceItemFigure",
    "synchro.LotSynchro", "synchro.OperationSynchro", "synchro.ContenuSynchro",
})

# Résultats qui empêchent de déclarer un lot réussi (valeurs : les champs de la base sont des chaînes).
BLOQUANTS = frozenset(r.value for r in (
    R.CONFLIT_VERSION, R.CONFLIT_ETAT, R.CONFLIT_IDENTITE, R.ADOPTION_A_CONFIRMER, R.STRUCTURE_MODIFIEE,
    R.REJETE_VALIDATION, R.CORRECTION_HORS_PERIMETRE, R.ERREUR,
))
APPLIQUES = frozenset(r.value for r in (R.CREE, R.MIS_A_JOUR, R.RETIRE, R.REINTEGRE))
TERMINES = frozenset(R.termines())
# Applications de ce projet dont le texte peut citer l'URL d'une image (instantanés, énoncés compilés...).
APPS_TEXTE = ("catalog", "quiz", "inedit", "fiches", "simulations")


class ErreurLot(Exception):
    """Lot inutilisable (archive, manifeste, SHA-256, schéma) : rien n'est appliqué."""


class ErreurGarde(Exception):
    """Écriture interdite détectée pendant un lot (modèle hors liste fermée, ou suppression)."""


class _Resultat(Exception):
    """Sortie anticipée d'un traitement avec un résultat non nominal (le `atomic()` est annulé)."""

    def __init__(self, resultat, detail=None):
        super().__init__(resultat)
        self.resultat = resultat
        self.detail = detail or {}


# --------------------------------------------------------------------------- garde d'écritures

class GardeEcritures:
    """Enregistre les écritures pendant un traitement et refuse celles qui sortent du périmètre."""

    def __init__(self):
        self.ecrits = set()

    def _save(self, sender, instance, **kwargs):
        if sender._meta.auto_created:
            return
        label = sender._meta.label
        if label not in LABELS_ECRITURE_AUTORISES:
            raise ErreurGarde(f"écriture interdite pendant un lot : {label}")
        self.ecrits.add(label)

    def _delete(self, sender, instance, **kwargs):
        if sender._meta.auto_created:  # lignes de liaison M2M : `set()` les remplace
            return
        raise ErreurGarde(f"suppression interdite pendant un lot : {sender._meta.label}")

    def _m2m(self, sender, instance, action, **kwargs):
        label = instance._meta.label
        if action.startswith("pre_") and label not in LABELS_ECRITURE_AUTORISES:
            raise ErreurGarde(f"modification de relation interdite pendant un lot : {label}")

    def __enter__(self):
        post_save.connect(self._save, weak=False, dispatch_uid=f"synchro-save-{id(self)}")
        post_delete.connect(self._delete, weak=False, dispatch_uid=f"synchro-delete-{id(self)}")
        m2m_changed.connect(self._m2m, weak=False, dispatch_uid=f"synchro-m2m-{id(self)}")
        return self

    def __exit__(self, *exc):
        post_save.disconnect(dispatch_uid=f"synchro-save-{id(self)}")
        post_delete.disconnect(dispatch_uid=f"synchro-delete-{id(self)}")
        m2m_changed.disconnect(dispatch_uid=f"synchro-m2m-{id(self)}")
        return False


# --------------------------------------------------------------------------- verrou

def _verrou_libre():
    """True si aucun autre processus ne tient le verrou ; None si la base n'en a pas (SQLite, tests)."""
    if connection.vendor != "postgresql":
        return None
    with connection.cursor() as cur:
        cur.execute("SELECT pg_try_advisory_lock(%s)", [VERROU_ID])
        obtenu = cur.fetchone()[0]
        if obtenu:
            cur.execute("SELECT pg_advisory_unlock(%s)", [VERROU_ID])
    return bool(obtenu)


class Verrou:
    """Verrou consultatif PostgreSQL de session : un seul lot s'applique à la fois."""

    def __enter__(self):
        # SQLite (tests) n'a pas de verrou consultatif : seul PostgreSQL protège de deux lots simultanés.
        self.actif = connection.vendor == "postgresql"
        if self.actif:
            with connection.cursor() as cur:
                cur.execute("SELECT pg_try_advisory_lock(%s)", [VERROU_ID])
                if not cur.fetchone()[0]:
                    raise ErreurLot("un autre lot est en cours d'application (verrou pris)")
        return self

    def __exit__(self, *exc):
        if self.actif:
            with connection.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(%s)", [VERROU_ID])
        return False


# --------------------------------------------------------------------------- réception

def racine_lots():
    return Path(getattr(settings, "SYNC_LOTS_DIR", None) or Path(tempfile.gettempdir()) / "lots")


def _sha_manifeste(manifeste):
    return emp.sha256_octets(emp.canoniser(manifeste, volatiles=()).encode("utf-8", errors="surrogatepass"))


def _extraire(archive, destination):
    """Extraction sûre (aucun chemin absolu, aucun `..`)."""
    destination = Path(destination).resolve()
    with zipfile.ZipFile(archive) as z:
        for nom in z.namelist():
            cible = (destination / nom).resolve()
            if nom.startswith(("/", "\\")) or ".." in Path(nom).parts or destination not in cible.parents:
                raise ErreurLot(f"archive refusée : chemin dangereux {nom!r}")
        z.extractall(destination)


def _lire_sommes(texte):
    attendus = {}
    for ligne in texte.splitlines():
        if ligne.strip():
            sha, _, rel = ligne.partition("  ")
            attendus[rel] = sha
    return attendus


def _verifier_sommes(dossier):
    dossier = Path(dossier)
    fichier = dossier / "SHA256SUMS"
    if not fichier.is_file():
        raise ErreurLot("SHA256SUMS absent du lot")
    attendus = _lire_sommes(fichier.read_text(encoding="utf-8"))
    presents = {
        p.relative_to(dossier).as_posix() for p in dossier.rglob("*") if p.is_file() and p.name != "SHA256SUMS"
    }
    if presents != set(attendus):
        manque = sorted(set(attendus) - presents)[:5]
        extra = sorted(presents - set(attendus))[:5]
        raise ErreurLot(f"contenu du lot incohérent avec SHA256SUMS (manquants {manque}, en trop {extra})")
    for rel, sha in attendus.items():
        if emp.sha256_fichier(dossier / rel) != sha:
            raise ErreurLot(f"SHA-256 différent pour {rel}")


def _verifier_entrees(manifeste, dossier):
    """Recalcule `version_proposee` côté serveur avec le même code que le poste (lot falsifié ou corrompu)."""
    vus = set()
    for entry in manifeste["contenus"]:
        cle = (entry["type"], entry["id_stable"])
        if cle in vus:
            raise ErreurLot(f"contenu en double dans le manifeste : {cle}")
        vus.add(cle)
        if entry["type"] not in ADAPTATEURS:
            raise ErreurLot(f"type de contenu inconnu : {entry['type']}")
        if entry["operation"] in ("create", "update"):
            if not entry.get("fichier"):
                raise ErreurLot(f"{entry['id_stable']} : opération {entry['operation']} sans fichier")
            chemin = chemin_dans_lot(dossier, entry["fichier"])
            data, _ = emp.lire_json(chemin)
            elements = dict(emp.elements(entry["fichier"], data, entry["type"]))
            element = elements.get(entry["id_stable"])
            if element is None:
                raise ErreurLot(f"{entry['id_stable']} introuvable dans {entry['fichier']}")
            shas = []
            for nom in emp.noms_fichiers_declares(element):
                if Path(nom).name != nom:
                    raise ErreurLot(f"{entry['id_stable']} : nom de figure refusé {nom!r}")
                figure = chemin.parent / nom
                if not figure.is_file():
                    raise ErreurLot(f"{entry['id_stable']} : figure déclarée absente du lot ({nom})")
                shas.append(emp.sha256_fichier(figure))
            if emp.empreinte_source(element, shas) != entry["version_proposee"]:
                raise ErreurLot(f"{entry['id_stable']} : empreinte recalculée différente du manifeste")


def _verifier_migrations(manifeste):
    requises = (manifeste.get("application") or {}).get("migrations_min") or {}
    if not requises:
        return
    appliquees = set(MigrationRecorder.Migration.objects.values_list("app", "name"))
    for app_label, prefixe in requises.items():
        if not any(a == app_label and n.startswith(str(prefixe)) for a, n in appliquees):
            raise ErreurLot(f"migration requise absente : {app_label} {prefixe}")


def _rafraichir_approbations(lot, archive):
    """
    Un même lot (même `batch_id`) peut être renvoyé avec des décisions humaines ajoutées dans
    `approbations.json` : tant qu'il n'est ni en cours ni réussi, ce fichier — et lui seul — est remplacé,
    après contrôle de son SHA-256 contre `SHA256SUMS` de l'archive.
    """
    if lot.statut == StatutLot.EN_COURS or lot.statut in STATUTS_TERMINES_REUSSIS:
        return
    with zipfile.ZipFile(archive) as z:
        try:
            contenu = z.read("approbations.json")
            sommes = _lire_sommes(z.read("SHA256SUMS").decode("utf-8"))
        except KeyError:
            return
    if sommes.get("approbations.json") != emp.sha256_octets(contenu):
        raise ErreurLot("approbations.json incohérent avec SHA256SUMS")
    cible = Path(lot.dossier) / "approbations.json"
    if not cible.is_file() or cible.read_bytes() != contenu:
        cible.write_bytes(contenu)


def recevoir(archive, sha256_attendu=None, racine=None):
    """Vérifie, extrait et journalise un lot (idempotent par `batch_id`). Retourne le LotSynchro."""
    archive = Path(archive)
    if not archive.is_file():
        raise ErreurLot(f"archive introuvable : {archive}")
    sha_archive = emp.sha256_fichier(archive)
    if sha256_attendu and sha_archive != sha256_attendu.strip().lower():
        raise ErreurLot("SHA-256 de l'archive différent de celui attendu : transfert corrompu")
    try:
        with zipfile.ZipFile(archive) as z:
            manifeste = json.loads(z.read("manifest.json").decode("utf-8"))
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErreurLot(f"archive illisible ou sans manifeste valide : {exc}") from exc
    if not isinstance(manifeste, dict) or not isinstance(manifeste.get("contenus"), list):
        raise ErreurLot("manifeste invalide")
    batch_id = str(manifeste.get("batch_id", ""))
    if not RE_BATCH_ID.match(batch_id):
        raise ErreurLot(f"batch_id invalide : {batch_id!r}")
    if manifeste.get("schema_sync") != SCHEMA_SYNC_SUPPORTE:
        raise ErreurLot(f"schema_sync {manifeste.get('schema_sync')!r} non pris en charge (attendu {SCHEMA_SYNC_SUPPORTE})")
    sha_man = _sha_manifeste(manifeste)

    dossier = Path(racine or racine_lots()) / batch_id
    existant = LotSynchro.objects.filter(batch_id=batch_id).first()
    if existant is not None:
        if existant.sha256_manifeste != sha_man:
            raise ErreurLot(f"batch_id {batch_id} déjà utilisé avec un autre contenu")
        if not (Path(existant.dossier) / "manifest.json").is_file():  # /tmp vidé par une recréation du conteneur
            if dossier.exists():
                shutil.rmtree(dossier)
            try:
                _extraire(archive, dossier)
                _verifier_sommes(dossier)
            except (OSError, zipfile.BadZipFile) as exc:
                raise ErreurLot(f"extraction impossible : {exc}") from exc
            existant.dossier = str(dossier)
            existant.save(update_fields=["dossier"])
        _rafraichir_approbations(existant, archive)
        return existant

    if dossier.exists():
        shutil.rmtree(dossier)
    dossier.mkdir(parents=True)
    try:
        _extraire(archive, dossier)
        _verifier_sommes(dossier)
        _verifier_migrations(manifeste)
        _verifier_entrees(manifeste, dossier)
    except ErreurLot:
        shutil.rmtree(dossier, ignore_errors=True)
        raise
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, json.JSONDecodeError, AdaptateurErreur) as exc:
        shutil.rmtree(dossier, ignore_errors=True)
        raise ErreurLot(f"lot invalide : {exc}") from exc

    with transaction.atomic():
        lot = LotSynchro.objects.create(
            batch_id=batch_id, nom=manifeste.get("nom", ""), statut=StatutLot.VERIFIE,
            schema_sync=manifeste["schema_sync"], sha256_archive=sha_archive, sha256_manifeste=sha_man,
            dossier=str(dossier), options=manifeste.get("options", {}),
            rapport={"application": manifeste.get("application", {}), "approbation": manifeste.get("approbation")},
        )
        OperationSynchro.objects.bulk_create([
            OperationSynchro(lot=lot, type=e["type"], id_stable=e["id_stable"], operation=e["operation"])
            for e in manifeste["contenus"]
        ])
    return lot


def _manifeste(lot):
    return json.loads((Path(lot.dossier) / "manifest.json").read_text(encoding="utf-8"))


def _approbations(lot):
    chemin = Path(lot.dossier) / "approbations.json"
    if not chemin.is_file():
        return {}
    decisions = json.loads(chemin.read_text(encoding="utf-8")).get("decisions", [])
    return {d["id_stable"]: d for d in decisions}


# --------------------------------------------------------------------------- classification

def _decision_valide(decision, etat, journal, version_proposee):
    """
    `ecraser` n'est valable que pour l'état de production EXACT que l'humain a vu, la version de
    production journalisée qu'il a vue, ET la version proposée qu'il a relue : une décision recopiée
    d'un lot à l'autre n'applique jamais un diff qu'il n'a pas lu.
    """
    if not decision or decision.get("decision") != "ecraser":
        return False
    if decision.get("version_proposee") != version_proposee:
        return False
    if decision.get("empreinte_etat_prod_vue") != etat:
        return False
    if journal is not None and decision.get("version_prod_vue") not in (None, journal.empreinte_source):
        return False
    return True


def classer(adapt, entry, ctx, decisions):
    """
    Classe un contenu SANS rien écrire. Retourne (genre, obj, journal, etat, detail), genre ∈
    {create, update, noop, adoption, garde_prod, conflit_version, conflit_etat, conflit_identite}.
    """
    id_stable = entry["id_stable"]
    obj = adapt.retrouver(ctx)
    journal = ContenuSynchro.objects.filter(type=entry["type"], id_stable=id_stable).first()
    decision = decisions.get(id_stable)
    vref, vprop = entry.get("version_reference"), entry["version_proposee"]

    if journal is None:
        if obj is None:
            return "create", None, None, None, {}
        autre = ContenuSynchro.objects.filter(type=entry["type"], objet_pk=obj.pk).first()
        if autre is not None:
            return "conflit_identite", obj, None, None, {
                "raison": f"cet objet est déjà journalisé sous l'identifiant {autre.id_stable} (fichier renommé ?)",
                "autre_id_stable": autre.id_stable,
            }
        etat = proj.empreinte_etat(adapt.projeter(obj))
        if decision and decision.get("decision") == "garder_prod":
            return "garde_prod", obj, None, etat, {}
        return "adoption", obj, None, etat, {"empreinte_etat_prod_vue": etat}

    objet_journal = adapt.modele.objects.filter(pk=journal.objet_pk).first()
    if objet_journal is None or obj is None or obj.pk != journal.objet_pk:
        if (
            objet_journal is None and obj is None and decision and decision.get("decision") == "recreer"
            and decision.get("objet_pk_absent") == journal.objet_pk and decision.get("version_proposee") == vprop
        ):
            return "create", None, journal, None, {"recree": True}
        return "conflit_identite", obj, journal, None, {
            "journal_objet_pk": journal.objet_pk, "retrouve_pk": getattr(obj, "pk", None),
            "objet_journal_present": objet_journal is not None,
        }
    etat = proj.empreinte_etat(adapt.projeter(objet_journal))
    detail = {"empreinte_etat_prod_vue": etat, "version_prod_vue": journal.empreinte_source}
    if decision and decision.get("decision") == "garder_prod":
        return "garde_prod", objet_journal, journal, etat, detail
    if etat != journal.empreinte_etat:
        if _decision_valide(decision, etat, journal, vprop):
            return "update", objet_journal, journal, etat, {**detail, "ecrase": True}
        return "conflit_etat", objet_journal, journal, etat, detail
    if journal.empreinte_source == vprop:
        return "noop", objet_journal, journal, etat, detail
    if vref != journal.empreinte_source:
        if _decision_valide(decision, etat, journal, vprop):
            return "update", objet_journal, journal, etat, {**detail, "ecrase": True}
        return "conflit_version", objet_journal, journal, etat, {**detail, "version_reference_lot": vref}
    return "update", objet_journal, journal, etat, detail


# --------------------------------------------------------------------------- exécution d'un contenu

def _executer(adapt, ctx, entry, obj, journal, lot, simulation, annuler=True, etat_attendu=None):
    """
    Applique (ou simule) un contenu dans UN `atomic()`. En simulation, aucun fichier n'est écrit.
    Retourne un dict de résultat ; lève `_Resultat` pour une sortie non nominale (transaction annulée).
    `annuler=False` (plan d'un lot entier) : la simulation n'est pas annulée contenu par contenu, c'est
    l'appelant qui annule tout à la fin ; un cours ou un quiz voit ainsi l'exercice simulé juste avant lui.
    `etat_attendu` : l'objet est relu SOUS VERROU de ligne dans la transaction et son état comparé à
    celui sur lequel la décision a été prise (une modification d'admin entre-temps n'est pas écrasée).
    """
    sync = ContexteSync(simulation=simulation, mise_a_jour=obj is not None)
    try:
        with GardeEcritures(), transaction.atomic():
            if obj is not None:
                obj = adapt.modele.objects.select_for_update().get(pk=obj.pk)
                if etat_attendu is not None and proj.empreinte_etat(adapt.projeter(obj)) != etat_attendu:
                    raise _Resultat(R.CONFLIT_ETAT, {"raison": "modifié pendant le traitement"})
            avant = adapt.projeter(obj) if obj is not None else None
            if obj is not None:
                problemes = adapt.structure_modifiee(obj, ctx)
                if problemes:
                    raise _Resultat(R.STRUCTURE_MODIFIEE, {"structure": problemes})
            porte_avant = adapt.porte(obj) if obj is not None else set()
            try:
                obj2, cree = adapt.appliquer(ctx, obj, sync)
            except DoublonCours as doublon:
                # Le cours existe déjà sous un autre identifiant : rien n'est créé, mais le rattachement
                # du rappel au cours existant (fait par l'ingestion) est conservé.
                if simulation and annuler:
                    transaction.set_rollback(True)
                return {"resultat_force": R.IGNORE_DEDOUBLONNE, "detail": {"existant_pk": doublon.existant.pk},
                        "diff": None, "cree": False, "fichiers": {}, "anciens_fichiers": [], "lessons": []}
            if obj is not None and (cree or obj2.pk != obj.pk):
                raise _Resultat(R.CONFLIT_IDENTITE, {
                    "raison": "l'ingestion a désigné un autre objet que celui du journal (doublon de clé naturelle ?)",
                    "attendu_pk": obj.pk, "obtenu_pk": obj2.pk,
                })
            if obj is None and not cree:
                raise _Resultat(R.CONFLIT_IDENTITE, {"raison": "un objet correspondant existe déjà", "obtenu_pk": obj2.pk})
            nouvelles = adapt.porte(obj2) - porte_avant
            if nouvelles:
                raise _Resultat(R.REJETE_VALIDATION, {"raisons": sorted(nouvelles)})
            # Empreinte calculée sur l'objet RELU : ce que la base renvoie, pas ce que l'application a en mémoire.
            apres = adapt.projeter(adapt.modele.objects.get(pk=obj2.pk))
            diff = proj.difference(avant, apres) if avant is not None else None
            if (
                avant is not None and journal is not None and diff == []
                and journal.empreinte_source != entry["version_proposee"]
            ):
                raise _Resultat(R.CORRECTION_HORS_PERIMETRE, {
                    "raison": "le JSON a changé mais aucun champ synchronisé n'est modifié (ex. consigne ou durée de "
                              "l'épreuve, rappel d'un autre exercice) : à corriger dans l'admin",
                })
            etat_apres = proj.empreinte_etat(apres)
            sortie = {
                "obj": obj2, "cree": cree, "diff": diff, "etat_apres": etat_apres,
                "anciens_fichiers": list(sync.anciens_fichiers),
                "fichiers": sync.fichiers, "lessons": sorted(adapt.lessons_touchees(obj2)),
            }
            if simulation:
                if annuler:
                    transaction.set_rollback(True)
            else:
                version = (journal.version + 1) if journal is not None else 1
                ContenuSynchro.objects.update_or_create(
                    type=entry["type"], id_stable=entry["id_stable"],
                    defaults={
                        "cle_naturelle": entry.get("cle_naturelle") or {}, "objet_pk": obj2.pk,
                        "empreinte_source": entry["version_proposee"], "empreinte_etat": etat_apres,
                        "version": version, "fichiers": sync.fichiers, "dernier_lot": lot, "applique_le": timezone.now(),
                    },
                )
            return sortie
    except Exception as exc:
        # Fichiers déjà écrits par cet appel : orphelins si la transaction est annulée (voir `nettoyer`).
        exc.fichiers_ecrits = list(sync.nouveaux_fichiers)
        raise


def _resultat_apres_execution(sortie):
    if sortie.get("resultat_force"):
        return sortie["resultat_force"]
    if sortie["cree"]:
        return R.CREE
    if sortie["diff"] == []:
        return R.INCHANGE
    return R.MIS_A_JOUR


def _journaliser_sans_ecriture(entry, obj, etat, lot):
    """Contenu existant identique à la source : on mémorise son identité sans toucher au contenu."""
    with GardeEcritures(), transaction.atomic():
        ContenuSynchro.objects.update_or_create(
            type=entry["type"], id_stable=entry["id_stable"],
            defaults={
                "cle_naturelle": entry.get("cle_naturelle") or {}, "objet_pk": obj.pk,
                "empreinte_source": entry["version_proposee"], "empreinte_etat": etat, "version": 1,
                "fichiers": {}, "dernier_lot": lot, "applique_le": timezone.now(),
            },
        )


def _traiter(lot, entry, racine_lot, options, decisions, simulation, annuler=True):
    """Traite un contenu. Retourne (resultat, detail, lessons)."""
    adapt = ADAPTATEURS[entry["type"]]
    operation = entry["operation"]
    detail = {}
    try:
        if operation in ("retirer", "reintegrer"):
            return _traiter_statut(adapt, entry, lot, options, simulation)
        ctx = adapt.charger(entry, racine_lot) if entry.get("fichier") else None
        if ctx is None:
            journal = ContenuSynchro.objects.filter(type=entry["type"], id_stable=entry["id_stable"]).first()
            if operation == "noop" and journal is not None and journal.empreinte_source == entry["version_proposee"]:
                return R.INCHANGE, {"classe": "noop"}, set()
            return R.CONFLIT_VERSION, {"classe": "noop_sans_fichier",
                                       "raison": "le lot ne porte pas ce contenu et le serveur n'a pas cette version"}, set()
        genre, obj, journal, etat, info = classer(adapt, entry, ctx, decisions)
        detail = {"classe": genre, **info}
        if genre == "noop":
            return R.INCHANGE, detail, set()
        if genre == "garde_prod":
            if journal is None and obj is not None:
                # Contenu historique que l'humain choisit de CONSERVER tel quel : on le prend pour base. La
                # version proposée est tenue pour acceptée (elle ne sera plus proposée en adoption) et une
                # correction ultérieure s'appliquera proprement par-dessus l'état actuel de la production.
                detail["baseline"] = True
                if not simulation:
                    _journaliser_sans_ecriture(entry, obj, etat, lot)
            return R.GARDE_PROD, detail, set()
        if genre in ("conflit_version", "conflit_etat", "conflit_identite"):
            return {"conflit_version": R.CONFLIT_VERSION, "conflit_etat": R.CONFLIT_ETAT,
                    "conflit_identite": R.CONFLIT_IDENTITE}[genre], detail, set()
        if genre == "adoption":
            essai = _executer(adapt, ctx, entry, obj, None, None, simulation=True)
            detail["diff"] = essai["diff"]
            if not proj.diff_significatif(essai["diff"]):
                # Déjà identique à la production (hors recompilation) : on journalise sans toucher au contenu.
                if not simulation:
                    _journaliser_sans_ecriture(entry, obj, etat, lot)
                return R.INCHANGE, detail, set()
            if not (options.get("adopter") and _decision_valide(
                    decisions.get(entry["id_stable"]), etat, None, entry["version_proposee"])):
                return R.ADOPTION_A_CONFIRMER, detail, set()
            # Adoption approuvée sur l'état exact que l'humain a vu : on applique et on journalise.
        attendu = etat if genre in ("update", "adoption") else None
        if simulation:
            essai = _executer(adapt, ctx, entry, obj, journal, None, simulation=True, annuler=annuler, etat_attendu=attendu)
            detail["diff"] = essai["diff"]
            detail["fichiers"] = sorted(essai["fichiers"])
            if essai.get("detail"):
                detail.update(essai["detail"])
            return _resultat_apres_execution(essai), detail, set()
        reel = _executer(adapt, ctx, entry, obj, journal, lot, simulation=False, etat_attendu=attendu)
        detail["diff"] = reel["diff"]
        if reel.get("resultat_force"):
            detail.update(reel["detail"])
            return reel["resultat_force"], detail, set()
        detail["fichiers"] = reel["fichiers"]
        detail["a_supprimer"] = reel["anciens_fichiers"]
        detail["lessons"] = reel["lessons"]
        detail["version"] = ContenuSynchro.objects.get(type=entry["type"], id_stable=entry["id_stable"]).version
        return _resultat_apres_execution(reel), detail, set(reel["lessons"])
    except _Resultat as r:
        return r.resultat, {**detail, **r.detail, **_orphelins(r)}, set()
    except (AdaptateurErreur, IngestionError) as exc:
        return R.ERREUR, {**detail, "erreur": str(exc), **_orphelins(exc)}, set()
    except ErreurGarde as exc:
        return R.ERREUR, {**detail, "erreur": str(exc), "garde": True, **_orphelins(exc)}, set()
    except Exception as exc:  # une erreur imprévue sur un contenu ne doit pas arrêter les autres
        return R.ERREUR, {**detail, "erreur": f"{type(exc).__name__}: {exc}", **_orphelins(exc)}, set()


def _orphelins(exc):
    ecrits = getattr(exc, "fichiers_ecrits", None)
    return {"orphelins": ecrits} if ecrits else {}


def _traiter_statut(adapt, entry, lot, options, simulation):
    journal = ContenuSynchro.objects.filter(type=entry["type"], id_stable=entry["id_stable"]).first()
    if journal is None:
        return R.ERREUR, {"erreur": "contenu non journalisé : retrait/réintégration impossible"}, set()
    obj = adapt.modele.objects.filter(pk=journal.objet_pk).first()
    if obj is None:
        return R.CONFLIT_IDENTITE, {"classe": "objet_disparu"}, set()
    cible = StatutContenu.REJETE if entry["operation"] == "retirer" else StatutContenu.VALIDE
    reussi = R.RETIRE if cible == StatutContenu.REJETE else R.REINTEGRE
    if obj.statut == cible:
        return R.INCHANGE, {"classe": entry["operation"]}, set()
    confirme = bool(options.get("retraits_confirmes"))
    if simulation:
        # Le plan ne peut pas être « bloquant » à cause d'une confirmation qui se donne à l'application.
        return reussi, {"classe": entry["operation"], "confirmation_requise": not confirme}, set()
    if not confirme:
        return R.ERREUR, {"erreur": "retrait non confirmé (--confirme-retraits <batch_id>)"}, set()
    with GardeEcritures(), transaction.atomic():
        (adapt.retirer if cible == StatutContenu.REJETE else adapt.reintegrer)(obj)
    return reussi, {"classe": entry["operation"], "lessons": sorted(adapt.lessons_touchees(obj))}, set(adapt.lessons_touchees(obj))


# --------------------------------------------------------------------------- planifier / appliquer

def _entrees_triees(manifeste):
    return sorted(
        manifeste["contenus"],
        key=lambda e: (e["operation"] in ("retirer", "reintegrer"), ORDRE_TYPES.get(e["type"], 9), e["id_stable"]),
    )


def _ecrire_operation(lot, entry, resultat, detail):
    OperationSynchro.objects.filter(lot=lot, type=entry["type"], id_stable=entry["id_stable"]).update(
        resultat=resultat, detail=detail, fin_le=timezone.now(),
    )


def _plan_complet(lot, manifeste, options, decisions):
    """
    Simulation de TOUT le lot dans une seule transaction annulée à la fin : chaque contenu voit ceux
    qui le précèdent (un cours dépend de l'exercice dont il dérive, un quiz de ses thèmes), comme
    pendant l'application. Aucune écriture en base, aucun fichier écrit.
    """
    plan, compteurs = [], {}
    with GardeEcritures(), transaction.atomic():
        for entry in _entrees_triees(manifeste):
            resultat, detail, _ = _traiter(lot, entry, lot.dossier, options, decisions, simulation=True, annuler=False)
            compteurs[resultat] = compteurs.get(resultat, 0) + 1
            plan.append({"type": entry["type"], "id_stable": entry["id_stable"], "operation": entry["operation"],
                         "resultat_prevu": resultat, "detail": detail})
        transaction.set_rollback(True)
    bloquants = sum(n for r, n in compteurs.items() if r in BLOQUANTS)
    return {"compteurs": compteurs, "bloquants": bloquants, "plan": plan}


def planifier(lot):
    """Simulation complète : classement, diff et porte de validation de chaque contenu. Aucune écriture."""
    manifeste = _manifeste(lot)
    options = {**manifeste.get("options", {}), **(lot.options or {})}
    essai = _plan_complet(lot, manifeste, options, _approbations(lot))
    lot.rapport = {**(lot.rapport or {}), "plan": essai["plan"], "plan_compteurs": essai["compteurs"],
                   "plan_bloquants": essai["bloquants"]}
    if lot.statut in (StatutLot.RECU, StatutLot.VERIFIE) and not essai["bloquants"]:
        lot.statut = StatutLot.PRET
    lot.save(update_fields=["rapport", "statut"])
    return {"batch_id": lot.batch_id, **essai}


def _vivant(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def diagnostiquer(lot):
    """
    Un lot `en_cours` devient `a_verifier` quand son battement est périmé ET qu'aucun processus ne le
    tient : verrou consultatif libre (PostgreSQL), ou à défaut processus disparu. Le verrou est plus
    fiable que le PID, réutilisé après le redémarrage d'un conteneur.
    """
    if lot.statut == StatutLot.EN_COURS:
        battement = lot.battement_le
        perime = battement is None or timezone.now() - battement > SEUIL_BATTEMENT
        libre = _verrou_libre()
        mort = (not _vivant(lot.pid)) if libre is None else libre
        if perime and mort:
            lot.statut = StatutLot.A_VERIFIER
            lot.save(update_fields=["statut"])
    return lot


def appliquer(lot, reprise=False, confirme_retraits=False, post_traitement=True):
    """
    Applique un lot. `reprise=True` (commande `reprendre`) n'exécute que les opérations non
    terminées ou bloquées. Un lot déjà réussi ne fait rien.
    """
    lot = diagnostiquer(lot)
    if lot.statut in STATUTS_TERMINES_REUSSIS:
        return {"batch_id": lot.batch_id, "statut": lot.statut, "deja_applique": True}
    if lot.statut == StatutLot.EN_COURS:
        raise ErreurLot("lot en cours d'application par un processus vivant")
    if lot.statut in (StatutLot.PARTIEL, StatutLot.ECHOUE, StatutLot.A_VERIFIER) and not reprise:
        raise ErreurLot(f"lot {lot.statut} : vérifier son état puis utiliser `reprendre`")
    if confirme_retraits:
        lot.options = {**(lot.options or {}), "retraits_confirmes": True}

    with Verrou():
        manifeste = _manifeste(lot)
        options = {**manifeste.get("options", {}), **(lot.options or {})}
        decisions = _approbations(lot)
        lot.statut, lot.pid, lot.debut_le = StatutLot.EN_COURS, os.getpid(), lot.debut_le or timezone.now()
        lot.battement_le, lot.options = timezone.now(), options
        lot.save(update_fields=["statut", "pid", "debut_le", "battement_le", "options"])

        if options.get("tout_ou_rien"):
            essai = _plan_complet(lot, manifeste, options, decisions)
            if essai["bloquants"]:
                lot.statut, lot.fin_le = StatutLot.ECHOUE, timezone.now()
                lot.erreur = "tout_ou_rien : au moins un contenu est bloquant, rien n'a été appliqué"
                lot.compteurs = essai["compteurs"]
                lot.save(update_fields=["statut", "fin_le", "erreur", "compteurs"])
                for p in essai["plan"]:
                    if p["resultat_prevu"] in BLOQUANTS:
                        _ecrire_operation(lot, p, p["resultat_prevu"], p["detail"])
                return {"batch_id": lot.batch_id, "statut": lot.statut, "compteurs": essai["compteurs"]}

        ops = {(o.type, o.id_stable): o for o in lot.operations.all()}
        for entry in _entrees_triees(manifeste):
            op = ops[(entry["type"], entry["id_stable"])]
            if op.resultat in TERMINES and op.resultat not in BLOQUANTS:
                continue  # déjà terminée lors d'un passage précédent
            if op.resultat in BLOQUANTS and not reprise:
                continue
            resultat, detail, _ = _traiter(lot, entry, lot.dossier, options, decisions, simulation=False)
            _ecrire_operation(lot, entry, resultat, detail)
            lot.battement_le = timezone.now()
            lot.save(update_fields=["battement_le"])

        res = _cloturer(lot)
        if post_traitement:
            res = post_traiter(lot)
        else:
            lot.rapport = {**(lot.rapport or {}), "post_traitement": {**(lot.rapport or {}).get("post_traitement", {}), "differe": True}}
            lot.save(update_fields=["rapport"])
        return res


def _cloturer(lot):
    compteurs = {}
    for op in lot.operations.all():
        compteurs[op.resultat] = compteurs.get(op.resultat, 0) + 1
    bloquants = sum(n for r, n in compteurs.items() if r in BLOQUANTS)
    attente = compteurs.get(R.EN_ATTENTE.value, 0)
    appliques = sum(n for r, n in compteurs.items() if r in APPLIQUES)
    avertissements = (lot.rapport or {}).get("post_traitement", {}).get("avertissements", [])
    if bloquants or attente:
        lot.statut = StatutLot.PARTIEL if appliques else StatutLot.ECHOUE
    elif avertissements:
        lot.statut = StatutLot.REUSSI_AVEC_AVERTISSEMENTS
    else:
        lot.statut = StatutLot.REUSSI
    lot.compteurs, lot.fin_le = compteurs, timezone.now()
    lot.save(update_fields=["statut", "compteurs", "fin_le"])
    return {"batch_id": lot.batch_id, "statut": lot.statut, "compteurs": compteurs, "avertissements": avertissements}


# --------------------------------------------------------------------------- post-traitement

def _regenerer_pdf(lesson):
    """
    Nouveau PDF de sujet sous un nom adressé par son contenu, référence commutée, ancien fichier CONSERVÉ
    (retourné pour `nettoyer`) : jamais de suppression avant que le nouveau soit écrit, jamais de
    référence vers un fichier absent.
    """
    octets = generate_sujet_pdf(lesson)
    ancien = lesson.sujet_pdf.name if lesson.sujet_pdf else ""
    base = Path(sujet_pdf_filename(lesson))
    nom = f"{base.parent.as_posix()}/{base.stem}-{hashlib.sha256(octets).hexdigest()[:8]}{base.suffix}"
    lesson.sujet_pdf.save(nom, ContentFile(octets), save=True)
    return ancien if ancien and ancien != lesson.sujet_pdf.name else ""


def post_traiter(lot):
    """
    PDF de sujet des leçons touchées, index de recherche, fréquences : hors transaction, un échec n'invalide
    pas le contenu. Reprenable : seules les leçons pas encore traitées le sont, et un lot réussi avec
    avertissements redevient `reussi` quand tout passe.
    """
    rapport = dict(lot.rapport or {})
    fait = set(rapport.get("post_traitement", {}).get("lessons_faites", []))
    a_traiter = set()
    for op in lot.operations.filter(resultat__in=APPLIQUES):
        a_traiter |= set((op.detail or {}).get("lessons", []))
    a_traiter -= fait

    avertissements, a_supprimer = [], list(rapport.get("a_supprimer", []))
    if a_traiter:
        from io import StringIO

        for lesson in Lesson.objects.filter(pk__in=a_traiter, statut=StatutContenu.VALIDE).select_related("subject__country"):
            try:
                ancien = _regenerer_pdf(lesson)
                if ancien:
                    a_supprimer.append(ancien)
                fait.add(lesson.pk)
            except Exception as exc:
                avertissements.append(f"PDF de sujet de la leçon {lesson.pk} : {type(exc).__name__}: {exc}")
        fait |= a_traiter - set(Lesson.objects.filter(pk__in=a_traiter, statut=StatutContenu.VALIDE).values_list("pk", flat=True))

    # Index de recherche et fréquences : dès qu'une opération a été appliquée, y compris un lot de cours ou de
    # quiz seuls (aucune leçon touchée). Le sitemap n'a rien à rafraîchir : il est reconstruit à chaque requête.
    # `index_fait` n'est posé qu'en cas de succès : un échec se rejoue, comme celui des PDF.
    index_fait = bool(rapport.get("post_traitement", {}).get("index_fait", False))
    if not index_fait and lot.operations.filter(resultat__in=APPLIQUES).exists():
        from io import StringIO

        index_fait = True
        for nom in ("indexer_recherche", "calculer_frequences_cours"):
            try:
                call_command(nom, stdout=StringIO(), stderr=StringIO())
            except Exception as exc:
                index_fait = False
                avertissements.append(f"{nom} : {type(exc).__name__}: {exc}")
    rapport["a_supprimer"] = a_supprimer
    rapport["post_traitement"] = {
        "fait": True, "avertissements": avertissements, "lessons_faites": sorted(fait), "index_fait": index_fait,
        "le": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    lot.rapport = rapport
    lot.save(update_fields=["rapport"])
    if lot.statut in STATUTS_TERMINES_REUSSIS:
        lot.statut = StatutLot.REUSSI_AVEC_AVERTISSEMENTS if avertissements else StatutLot.REUSSI
        lot.save(update_fields=["statut"])
    return {"batch_id": lot.batch_id, "statut": lot.statut, "compteurs": lot.compteurs, "avertissements": avertissements}


# --------------------------------------------------------------------------- consultation

def statut(batch_id=None, detail=False):
    if batch_id is None:
        return [{"batch_id": l.batch_id, "statut": diagnostiquer(l).statut, "compteurs": l.compteurs, "fin_le": l.fin_le}
                for l in LotSynchro.objects.all()[:50]]
    lot = LotSynchro.objects.filter(batch_id=batch_id).first()
    if lot is None:
        return {"batch_id": batch_id, "statut": "inconnu"}
    lot = diagnostiquer(lot)
    res = {"batch_id": lot.batch_id, "statut": lot.statut, "compteurs": lot.compteurs, "erreur": lot.erreur,
           "pid": lot.pid, "battement_le": lot.battement_le, "debut_le": lot.debut_le, "fin_le": lot.fin_le,
           "avertissements": (lot.rapport or {}).get("post_traitement", {}).get("avertissements", []),
           "post_traitement_fait": (lot.rapport or {}).get("post_traitement", {}).get("fait", False)}
    if detail:
        res["operations"] = [
            {"type": o.type, "id_stable": o.id_stable, "operation": o.operation, "resultat": o.resultat, "detail": o.detail}
            for o in lot.operations.all()
        ]
    return res


def exporter_reference():
    """Empreintes appliquées en production : le poste s'en sert pour classer create/update/noop."""
    return {
        "genere_le": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contenus": {
            f"{c.type}|{c.id_stable}": {
                "empreinte_source": c.empreinte_source, "empreinte_etat": c.empreinte_etat, "version": c.version,
            }
            for c in ContenuSynchro.objects.all()
        },
    }


def rafraichir_journal(confirme=False):
    """
    Recalcule l'empreinte d'état de TOUS les contenus journalisés d'après l'état actuel de la base.
    À n'utiliser qu'après un changement du code de compilation / de rendu qui modifie légitimement les
    champs compilés : toute retouche manuelle faite avant serait alors acceptée comme référence.
    Sans `confirme`, liste seulement ce qui changerait.
    """
    changes = []
    for c in ContenuSynchro.objects.all():
        adapt = ADAPTATEURS.get(c.type)
        obj = adapt.modele.objects.filter(pk=c.objet_pk).first() if adapt else None
        if obj is None:
            continue
        etat = proj.empreinte_etat(adapt.projeter(obj))
        if etat != c.empreinte_etat:
            changes.append(f"{c.type}:{c.id_stable}")
            if confirme:
                c.empreinte_etat = etat
                c.save(update_fields=["empreinte_etat"])
    return {"differents": changes, "appliques": confirme}


# --------------------------------------------------------------------------- fichiers

def _champs_fichiers():
    for modele in apps.get_models():
        for champ in modele._meta.get_fields():
            if isinstance(champ, dj_models.FileField):
                yield modele, champ


def verifier_fichiers(avec_sha=False):
    """Références sans fichier et empreintes divergentes. Rapport seulement : rien n'est supprimé."""
    sans_fichier, sha_divergent = [], []
    for modele, champ in _champs_fichiers():
        for pk, nom in modele._default_manager.exclude(**{champ.name: ""}).values_list("pk", champ.name):
            if nom and not champ.storage.exists(nom):
                sans_fichier.append(f"{modele._meta.label}#{pk}.{champ.name} -> {nom}")
    if avec_sha:
        for c in ContenuSynchro.objects.exclude(fichiers={}):
            for fig_id, info in c.fichiers.items():
                if not default_storage.exists(info["chemin"]):
                    sans_fichier.append(f"{c.type}:{c.id_stable} {fig_id} -> {info['chemin']}")
                    continue
                with default_storage.open(info["chemin"], "rb") as f:
                    if hashlib.sha256(f.read()).hexdigest() != info["sha256"]:
                        sha_divergent.append(f"{c.type}:{c.id_stable} {fig_id} -> {info['chemin']}")
    return {"references_sans_fichier": sans_fichier, "sha_divergents": sha_divergent}


def _reference_champ_existe(chemin):
    for modele, champ in _champs_fichiers():
        if modele._default_manager.filter(**{champ.name: chemin}).exists():
            return True
    return False


def _reference_texte_existe(chemin):
    """
    Une image est aussi citée par son URL dans des TEXTES : énoncés et corrigés réécrits à l'ingestion,
    contenus compilés, et surtout les instantanés de quiz déjà joués (QuizQuestion.snapshot). La
    supprimer casserait définitivement la relecture de l'historique d'un élève.
    """
    for modele in apps.get_models():
        if modele._meta.app_label not in APPS_TEXTE or modele._meta.abstract:
            continue
        for champ in modele._meta.get_fields():
            if isinstance(champ, (dj_models.TextField, dj_models.JSONField)) and getattr(champ, "column", None):
                texte = Cast(champ.name, output_field=dj_models.TextField())
                if modele._default_manager.annotate(_t=texte).filter(_t__icontains=chemin).exists():
                    return True
    return False


def nettoyer(apres_jours=7, appliquer_suppression=False):
    """
    Anciens fichiers remplacés (lots réussis) et fichiers orphelins d'un traitement annulé (lots réussis,
    partiels ou échoués), plus anciens que `apres_jours`. Un fichier encore référencé — par un champ
    fichier OU par son URL dans un texte — n'est JAMAIS supprimé. Par défaut : liste seulement.
    """
    limite = timezone.now() - timedelta(days=apres_jours)
    proposes = set()
    lots_ok = LotSynchro.objects.filter(statut__in=STATUTS_TERMINES_REUSSIS, fin_le__lt=limite)
    for lot in lots_ok:
        proposes.update((lot.rapport or {}).get("a_supprimer", []))
    for op in OperationSynchro.objects.filter(lot__in=lots_ok):
        proposes.update((op.detail or {}).get("a_supprimer", []))
    lots_orphelins = LotSynchro.objects.filter(
        statut__in=[*STATUTS_TERMINES_REUSSIS, StatutLot.PARTIEL, StatutLot.ECHOUE], fin_le__lt=limite)
    for op in OperationSynchro.objects.filter(lot__in=lots_orphelins):
        proposes.update((op.detail or {}).get("orphelins", []))

    candidats, supprimes, conserves = [], [], []
    for chemin in sorted(p for p in proposes if p):
        if not default_storage.exists(chemin):
            continue
        if _reference_champ_existe(chemin) or _reference_texte_existe(chemin):
            conserves.append(chemin)
            continue
        candidats.append(chemin)
        if appliquer_suppression:
            default_storage.delete(chemin)
            supprimes.append(chemin)
    return {"candidats": candidats, "supprimes": supprimes, "conserves_car_references": conserves}
