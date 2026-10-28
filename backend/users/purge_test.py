"""
Purge des comptes de test et de leurs données d'usage (voir deploy/SPEC-PURGE-DONNEES-TEST.md).

Principes, dans l'ordre où ils comptent :

- **Liste blanche.** Rien n'est supprimé qui ne figure pas dans un fichier de périmètre validé à la main (ids de
  comptes + empreinte de leur identifiant). Aucune détection par ancienneté, nom ou adresse. Un administrateur n'est
  jamais supprimable, même listé.
- **Refus plutôt que suppression ambiguë.** Revendeur, commission, versement, candidature, parrainage avec un compte
  hors périmètre, paiement d'un compte hors périmètre : la planification refuse (code 2) et rien n'est écrit.
- **Une seule transaction.** La simulation exécute exactement les suppressions de l'exécution dans une transaction
  qu'elle annule toujours (rien n'est persisté, des verrous de ligne durent le temps du calcul) ; l'exécution compare
  ensuite ses comptes réels à ceux de la simulation (le jeton) et au moindre écart annule tout.
- **Aucun fichier supprimé.** Les fichiers d'usage rattachés aux lignes supprimées sont seulement listés.
- **Contenu intact.** Les comptages des modèles pédagogiques, des plans et des réglages sont relevés avant/après : un
  écart annule la transaction.

Les modèles qui n'existent pas dans toutes les versions déployées (revendeurs, parrainage...) sont résolus par
`apps.get_model` : un modèle absent est ignoré et signalé, il ne casse pas la commande.
"""
import hashlib
import json
import re
from collections import Counter

from django.apps import apps
from django.contrib.sessions.models import Session
from django.db import connection, transaction
from django.db.models import Q

from .models import User

VERSION = 1
VERROU_ID_DEFAUT = 727368  # le même que synchro.moteur.VERROU_ID : un lot de synchro et une purge s'excluent
OPTIONS = {"paiements", "paiements_approuves", "quotas", "analytics", "sessions"}
RE_SHA256 = re.compile(r"^[0-9a-f]{64}$")

# Compteurs de contrôle : doivent être strictement identiques avant et après la purge.
MODELES_PROTEGES = [
    "catalog.Country", "catalog.Subject", "catalog.Cursus", "catalog.Tag", "catalog.Lesson", "catalog.Cours",
    "catalog.Exercise", "catalog.Question", "catalog.Figure", "catalog.Temoignage",
    "programme.Module", "programme.Savoir",
    "quiz.CompetenceItem", "quiz.CompetenceItemFigure",
    "inedit.Blueprint", "inedit.EpreuveInedite", "inedit.ExerciceInedite", "inedit.QuestionInedite",
    "subscriptions.Plan", "payments.MobileMoneyAccount", "access.ReglagesTelechargement",
    "synchro.LotSynchro", "synchro.OperationSynchro", "synchro.ContenuSynchro", "admin.LogEntry",
    "recherche.EntreeRecherche", "recherche.RechercheSansResultat", "users.OTPCode",
]

# Champs fichier produits par l'usage : on les liste, on ne les supprime jamais.
CHAMPS_FICHIER_USAGE = [
    ("payments.ManualPayment", "proof", "user_id"),
    ("quiz.QuizSession", "sujet_pdf", "profil__compte_id"),
    ("quiz.QuizSession", "corrige_pdf", "profil__compte_id"),
    ("fiches.FicheGeneree", "sujet_pdf", "owner_id"),
    ("fiches.FicheGeneree", "corrige_pdf", "owner_id"),
]


class Refus(Exception):
    """Garde refusée ou ambiguïté : aucune écriture (code de sortie 2)."""


class Echec(Exception):
    """Écart constaté pendant l'exécution : transaction annulée (code de sortie 1)."""


class _Annulation(Exception):
    """Sert à annuler la transaction d'une simulation."""


def modele(label):
    """Le modèle `app.Nom`, ou None s'il n'existe pas dans cette version du code."""
    try:
        return apps.get_model(label)
    except LookupError:
        return None


def empreinte_identifiant(user):
    base = (user.email or user.phone_number or "").strip().lower()
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def masque(user):
    ident = user.email or user.phone_number or ""
    local, arobase, domaine = ident.partition("@")
    return (local[:3] + "***" + arobase + domaine) if ident else "-"


# ---------------------------------------------------------------------------------------------- périmètre


def charger_perimetre(donnees):
    """Valide le fichier de périmètre. Refuse tout champ inconnu : une faute de frappe ne doit pas passer."""
    if not isinstance(donnees, dict) or donnees.get("version") != VERSION:
        raise Refus(f"Périmètre invalide : « version » doit valoir {VERSION}.")
    inconnus = set(donnees) - {"version", "comptes", "options", "commentaire"}
    if inconnus:
        raise Refus(f"Périmètre invalide : champs inconnus {sorted(inconnus)}.")
    comptes = donnees.get("comptes")
    if not isinstance(comptes, list):
        raise Refus("Périmètre invalide : « comptes » doit être une liste (éventuellement vide).")
    vus = set()
    nettoyes = []
    for c in comptes:
        if not isinstance(c, dict) or set(c) - {"user_id", "identifiant_sha256", "motif", "valide_par", "date", "masque"}:
            raise Refus(f"Périmètre invalide : entrée de compte illisible ({c!r}).")
        uid, empreinte = c.get("user_id"), c.get("identifiant_sha256")
        if not isinstance(uid, int) or isinstance(uid, bool) or uid <= 0:
            raise Refus(f"Périmètre invalide : user_id {uid!r}.")
        if not isinstance(empreinte, str) or not RE_SHA256.match(empreinte):
            raise Refus(f"Périmètre invalide : identifiant_sha256 absent ou mal formé pour le compte {uid}.")
        if uid in vus:
            raise Refus(f"Périmètre invalide : compte {uid} listé deux fois.")
        vus.add(uid)
        nettoyes.append({"user_id": uid, "identifiant_sha256": empreinte})
    options = donnees.get("options") or {}
    if not isinstance(options, dict) or set(options) - OPTIONS or any(not isinstance(v, bool) for v in options.values()):
        raise Refus(f"Périmètre invalide : options autorisées (booléens) : {sorted(OPTIONS)}.")
    opts = {"paiements": False, "paiements_approuves": False, "quotas": False, "analytics": False, "sessions": True}
    opts.update(options)
    if opts["paiements_approuves"] and not opts["paiements"]:
        raise Refus("Périmètre invalide : « paiements_approuves » exige « paiements ».")
    return {"comptes": nettoyes, "options": opts}


def proposer_perimetre(users):
    """Fichier de périmètre à relire, jamais appliqué tel quel sans validation humaine."""
    return {
        "version": VERSION,
        "commentaire": "À relire compte par compte. Ajouter motif, valide_par, date. Rien n'est supprimé sans exécution explicite.",
        "comptes": [
            {"user_id": u.pk, "masque": masque(u), "identifiant_sha256": empreinte_identifiant(u),
             "motif": "", "valide_par": "", "date": ""}
            for u in users if not (u.is_staff or u.is_superuser)
        ],
        "options": {"paiements": False, "paiements_approuves": False, "quotas": False, "analytics": False, "sessions": True},
    }


# ---------------------------------------------------------------------------------------------- planification


def _ids_profils(ids):
    return list(modele("users.Profil").objects.filter(compte_id__in=ids).values_list("pk", flat=True))


def _paiements(ids):
    """(ManualPayment qs, Transaction qs ou None) rattachés aux comptes OU à leurs profils."""
    mp = modele("payments.ManualPayment").objects.filter(Q(user_id__in=ids) | Q(profil__compte_id__in=ids))
    tx_model = modele("payments.Transaction")
    tx = tx_model.objects.filter(Q(user_id__in=ids) | Q(profil__compte_id__in=ids)) if tx_model else None
    return mp, tx


def verifier_gardes(perimetre):
    """
    Retourne (users à supprimer, ids absents, refus[], avertissements[]). N'écrit rien.
    `refus` non vide => l'exécution entière est refusée.
    """
    refus, avertissements = [], []
    entrees = perimetre["comptes"]
    ids_demandes = [c["user_id"] for c in entrees]
    users = {u.pk: u for u in User.objects.filter(pk__in=ids_demandes)}
    absents = [i for i in ids_demandes if i not in users]
    for c in entrees:
        u = users.get(c["user_id"])
        if u is None:
            continue
        if u.is_staff or u.is_superuser:
            refus.append(f"Compte {u.pk} : administrateur, jamais supprimable.")
        elif empreinte_identifiant(u) != c["identifiant_sha256"]:
            refus.append(f"Compte {u.pk} : l'identifiant actuel ne correspond pas à celui du périmètre (id réaffecté ou erreur).")
    ids = list(users)
    if not ids:
        return [], absents, refus, avertissements
    opts = perimetre["options"]

    # Revendeur, commission, versement, candidature : jamais supprimés par cette commande.
    for label, filtre, nom in [
        ("revendeurs.Revendeur", Q(user_id__in=ids), "revendeur"),
        ("revendeurs.CandidatureRevendeur", Q(user_id__in=ids), "candidature de revendeur"),
        ("revendeurs.Commission", Q(client_id__in=ids) | Q(revendeur__user_id__in=ids), "commission de revendeur"),
    ]:
        m = modele(label)
        if m is None:
            avertissements.append(f"Modèle {label} absent de cette version : ignoré.")
            continue
        for obj in m.objects.filter(filtre):
            refus.append(f"{nom.capitalize()} #{obj.pk} lié aux comptes ciblés : à traiter à la main, hors purge.")

    mp, tx = _paiements(ids)
    for p in mp:
        if p.user_id not in ids:
            refus.append(f"Paiement manuel #{p.pk} d'un compte hors périmètre sur un profil ciblé.")
    if tx is not None:
        for t in tx:
            if t.user_id not in ids:
                refus.append(f"Transaction #{t.pk} d'un compte hors périmètre sur un profil ciblé.")
    mp_ids = list(mp.values_list("pk", flat=True))
    tx_ids = list(tx.values_list("pk", flat=True)) if tx is not None else []
    if (mp_ids or tx_ids) and not opts["paiements"]:
        refus.append(
            f"{len(mp_ids)} paiement(s) manuel(s) et {len(tx_ids)} transaction(s) rattachés aux comptes ciblés : "
            "activer l'option « paiements » pour les supprimer avec les comptes, sinon retirer les comptes du périmètre."
        )
    if not opts["paiements_approuves"]:
        approuves = list(mp.filter(status="APPROVED").values_list("pk", flat=True))
        if tx is not None:
            approuves += list(tx.filter(status="SUCCESSFUL").values_list("pk", flat=True))
        if approuves and opts["paiements"]:
            refus.append(
                f"{len(approuves)} paiement(s) validé(s)/réussi(s) (ids {approuves}) : "
                "ils ont peut-être été réellement encaissés ; confirmer avec « paiements_approuves »."
            )

    # Parrainage : supprimer un compte supprime le crédit (CASCADE) de l'autre partie.
    par = modele("subscriptions.ParrainageRecompense")
    if par is not None:
        cond = Q(parrain_id__in=ids) | Q(filleul_id__in=ids)
        if mp_ids:
            cond |= Q(manual_payment_id__in=mp_ids)
        if tx_ids:
            cond |= Q(transaction_id__in=tx_ids)
        for r in par.objects.filter(cond):
            if r.parrain_id not in ids or r.filleul_id not in ids:
                refus.append(f"Crédit de parrainage #{r.pk} entre un compte ciblé et un compte hors périmètre : supprimerait le crédit de l'autre partie.")
    else:
        avertissements.append("Modèle subscriptions.ParrainageRecompense absent de cette version : ignoré.")

    parraines = User.objects.filter(referred_by_id__in=ids).exclude(pk__in=ids).count()
    if parraines:
        avertissements.append(f"{parraines} compte(s) hors périmètre ont l'un des comptes ciblés pour parrain : leur lien de parrainage sera mis à vide.")
    return [users[i] for i in ids], absents, refus, avertissements


def empreinte_protegee():
    """Comptages à conserver à l'identique : contenu, réglages, journaux, comptes administrateurs."""
    releve = {}
    for label in MODELES_PROTEGES:
        m = modele(label)
        releve[label] = m.objects.count() if m is not None else None
    admins = list(User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by("pk").values_list("pk", flat=True))
    releve["admins"] = admins
    return releve


def fichiers_d_usage(ids):
    """Liste (jamais de suppression) des fichiers d'usage rattachés aux comptes ciblés."""
    trouves = []
    for label, champ, chemin in CHAMPS_FICHIER_USAGE:
        m = modele(label)
        if m is None:
            continue
        for nom in m.objects.filter(**{f"{chemin}__in": ids}).exclude(**{champ: ""}).exclude(
            **{f"{champ}__isnull": True}
        ).values_list(champ, flat=True):
            trouves.append(f"{label}.{champ}: {nom}")
    return trouves


# ---------------------------------------------------------------------------------------------- application


def _supprimer(qs, comptes):
    """Supprime `qs` et ajoute les comptes réels (cascades comprises) à `comptes`."""
    _, detail = qs.delete()
    comptes.update(detail)


def _sessions_des_comptes(ids):
    cibles = {str(i) for i in ids}
    return [s.session_key for s in Session.objects.all() if str(s.get_decoded().get("_auth_user_id")) in cibles]


def _appliquer(users, perimetre):
    """
    Les suppressions, dans l'ordre qui respecte les PROTECT. Doit être appelée dans une transaction.
    Retourne un Counter {modèle: lignes supprimées}, cascades comprises (celles que `delete()` rapporte).
    """
    ids = [u.pk for u in users]
    opts = perimetre["options"]
    comptes = Counter()
    if not ids:
        return comptes
    profils = _ids_profils(ids)

    if opts["paiements"]:
        mp, tx = _paiements(ids)
        _supprimer(mp, comptes)
        if tx is not None:
            _supprimer(tx, comptes)
    if opts["analytics"]:
        ev = modele("analytics.AnalyticsEvent")
        if ev is not None:
            _supprimer(ev.objects.filter(user_id__in=ids), comptes)
    if opts["quotas"]:
        cles = [f"p:{p}" for p in profils] + [f"c:{i}" for i in ids]
        compteur = modele("access.CompteurQuota")
        journal = modele("access.TelechargementPdf")
        if compteur is not None:
            _supprimer(compteur.objects.filter(portee="demandeur", cle__in=cles), comptes)
        if journal is not None:
            _supprimer(journal.objects.filter(demandeur__in=cles), comptes)
    if opts["sessions"]:
        cles_sessions = _sessions_des_comptes(ids)
        if cles_sessions:
            _supprimer(Session.objects.filter(session_key__in=cles_sessions), comptes)
    _supprimer(User.objects.filter(pk__in=ids), comptes)
    return comptes


def _jeton(perimetre, comptes_supprimes, absents):
    corps = {
        "version": VERSION,
        "comptes": sorted((c["user_id"], c["identifiant_sha256"]) for c in perimetre["comptes"]),
        "options": perimetre["options"],
        "absents": sorted(absents),
        "suppressions": sorted(comptes_supprimes.items()),
    }
    return hashlib.sha256(json.dumps(corps, sort_keys=True).encode("utf-8")).hexdigest()[:20]


class VerrouPris(Refus):
    pass


class Verrou:
    """Verrou consultatif PostgreSQL de session, le même que celui des lots de synchronisation."""

    def __enter__(self):
        self.pris = None
        if connection.vendor != "postgresql":
            return self
        try:
            from synchro.moteur import VERROU_ID
        except ImportError:
            VERROU_ID = VERROU_ID_DEFAUT
        self.id = VERROU_ID
        with connection.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s)", [self.id])
            self.pris = cur.fetchone()[0]
        if not self.pris:
            raise VerrouPris("Un lot de synchronisation ou une autre purge est en cours (verrou pris).")
        return self

    def __exit__(self, *exc):
        if self.pris:
            with connection.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(%s)", [self.id])
        return False


def _rapport(perimetre, users, absents, refus, avertissements, supprimes, mode, jeton, fichiers=()):
    opts = perimetre["options"]
    ids = [u.pk for u in users]
    paiements_conserves = 0
    if ids and not opts["paiements"]:
        mp, tx = _paiements(ids)
        paiements_conserves = mp.count() + (tx.count() if tx is not None else 0)
    return {
        "mode": mode,
        "statut": "refuse" if refus else "ok",
        "jeton": jeton,
        "comptes": {
            "cibles": len(perimetre["comptes"]),
            "presents": len(users),
            "ignores_absents": sorted(absents),
            "supprimes": supprimes.get("users.User", 0) if mode == "executer" else 0,
        },
        "lignes_par_modele": dict(sorted(supprimes.items())),
        "conserves": {"paiements_non_cibles": paiements_conserves},
        "fichiers_d_usage_listes_non_supprimes": list(fichiers),
        "refus": refus,
        "avertissements": avertissements,
        "erreurs": [],
    }


def simuler(perimetre):
    """Rapport + jeton. Aucune donnée n'est persistée : les suppressions réelles sont annulées."""
    with Verrou():
        users, absents, refus, avertissements = verifier_gardes(perimetre)
        if refus:
            return _rapport(perimetre, users, absents, refus, avertissements, Counter(), "simuler", None)
        avant = empreinte_protegee()
        fichiers = fichiers_d_usage([u.pk for u in users])  # avant la suppression des lignes qui les référencent
        try:
            with transaction.atomic():
                comptes = _appliquer(users, perimetre)
                if empreinte_protegee() != avant:
                    raise Echec("La simulation a modifié des données protégées : arrêt.")
                raise _Annulation()
        except _Annulation:
            pass
        return _rapport(perimetre, users, absents, refus, avertissements, comptes, "simuler", _jeton(perimetre, comptes, absents), fichiers)


def executer(perimetre, jeton):
    """
    Refait la simulation dans la transaction réelle, compare au jeton, applique, vérifie le contenu, puis commit.
    Lève Refus (code 2) ou Echec (code 1) : dans les deux cas rien n'est écrit.
    """
    with Verrou():
        with transaction.atomic():
            users, absents, refus, avertissements = verifier_gardes(perimetre)
            if refus:
                raise Refus("; ".join(refus))
            avant = empreinte_protegee()
            fichiers = fichiers_d_usage([u.pk for u in users])
            comptes = _appliquer(users, perimetre)
            attendu = _jeton(perimetre, comptes, absents)
            if attendu != jeton:
                raise Refus(
                    "Le jeton ne correspond plus : les données ont changé depuis la simulation "
                    "(ou le périmètre est différent). Relancer la simulation."
                )
            if empreinte_protegee() != avant:
                raise Echec("Des données protégées ont changé pendant la purge : transaction annulée.")
            if User.objects.filter(pk__in=[u.pk for u in users]).exists():
                raise Echec("Des comptes ciblés existent encore après suppression : transaction annulée.")
        return _rapport(perimetre, users, absents, [], avertissements, comptes, "executer", attendu, fichiers)


def verifier(perimetre):
    """Après coup : aucun compte ciblé ne subsiste. Retourne un rapport ; `statut` vaut « ok » ou « echec »."""
    ids = [c["user_id"] for c in perimetre["comptes"]]
    restes = list(User.objects.filter(pk__in=ids).values_list("pk", flat=True))
    return {"mode": "verifier", "statut": "echec" if restes else "ok", "comptes_restants": restes,
            "empreinte_protegee": empreinte_protegee()}
