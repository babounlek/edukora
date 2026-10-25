"""
Outil en ligne de commande de la chaîne de synchronisation, côté poste (appelé par scripts/edukora.ps1).

Bibliothèque standard seule, aucun accès réseau, aucune base. Quatre sous-commandes :

  controler <ingest> <unité>...      contrôles statiques d'unités (JSON, identifiants, fichiers déclarés)
  empreinte <ingest> <unité>         empreinte d'une unité (sert aux enregistrements de validation)
  inventaire <repo> --sortie <dir>   contenus ingérables NON suivis par git, regroupés par unité
  preparer ...                       construit un lot (dossier + archive + SHA-256) après contrôles

Les sorties détaillées vont dans des fichiers ; stdout ne reçoit qu'un résumé JSON court, que
PowerShell relit. Codes de sortie : 0 ok · 1 contenu invalide ou validation absente · 2 usage ·
5 approbation humaine manquante.

Lancer avec `python -I` : les imports voisins sont chargés par chemin, pas par sys.path.
"""
import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys
import time
import zipfile

_ICI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("synchro_empreintes", os.path.join(_ICI, "empreintes.py"))
emp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(emp)

SCHEMA_SYNC = 1
CLES_REQUISES = {
    emp.TYPE_EXERCICE: ("epreuve_source", "numero_exercice", "questions"),
    emp.TYPE_COURS: ("cours_id", "meta", "sections"),
    emp.TYPE_QUIZ: ("external_id", "theme", "enonce_markdown", "corrige_markdown"),
}


def _sortie_utf8():
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def _rel(ingest, chemin):
    return os.path.relpath(chemin, ingest).replace("\\", "/")


def _json_ecrire(chemin, data):
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def fichiers_json_de_unite(ingest, unite):
    """Chemins absolus des JSON d'une unité (dossier récursif, ou fichier de quiz)."""
    base = os.path.join(ingest, *unite.split("/"))
    if unite.lower().endswith(".json"):
        return [base] if os.path.isfile(base) else []
    trouves = []
    for racine, dirs, fichiers in os.walk(base):
        dirs[:] = [d for d in dirs if not d.startswith("_")]
        for nom in fichiers:
            if nom.lower().endswith(".json"):
                trouves.append(os.path.join(racine, nom))
    return sorted(trouves)


def analyser_unite(ingest, unite, calculer_shas=True):
    """
    Analyse statique d'une unité. Retourne
    {"unite", "elements": [...], "ignores": [...], "erreurs": [...], "avertissements": [...], "fichiers": {rel: sha}}.
    Chaque élément : id_stable, type, fichier (rel), index (quiz), cle_naturelle, empreinte_source, fichiers[].
    """
    res = {"unite": unite, "elements": [], "ignores": [], "erreurs": [], "avertissements": [], "fichiers": {}}
    chemins = fichiers_json_de_unite(ingest, unite)
    if not chemins:
        res["erreurs"].append(f"{unite} : aucun fichier JSON trouvé")
        return res
    vus = {}
    for chemin in chemins:
        rel = _rel(ingest, chemin)
        if not emp.est_chemin_ingerable(rel):
            res["ignores"].append(f"{rel} : hors périmètre ingérable")
            continue
        try:
            data, avert = emp.lire_json(chemin)
        except ValueError as exc:
            res["erreurs"].append(f"{rel} : {exc}")
            continue
        res["avertissements"].extend(f"{rel} : {a}" for a in avert)
        type_c = emp.type_de_contenu(rel, data)
        if type_c not in emp.TYPES_V1:
            res["ignores"].append(f"{rel} : type '{type_c}' hors périmètre v1")
            continue
        if calculer_shas:
            res["fichiers"][rel] = emp.sha256_fichier(chemin)
        for index, (id_stable, element) in enumerate(emp.elements(rel, data, type_c)):
            if not id_stable:
                res["erreurs"].append(f"{rel} : élément {index} sans identifiant stable (external_id/cours_id)")
                continue
            if not isinstance(element, dict):
                res["erreurs"].append(f"{rel} : élément {index} n'est pas un objet")
                continue
            manquantes = [k for k in CLES_REQUISES[type_c] if element.get(k) in (None, "", [], {})]
            if manquantes:
                res["erreurs"].append(f"{rel} [{id_stable}] : champs obligatoires manquants {manquantes}")
            cle = (type_c, id_stable)
            if cle in vus:
                res["erreurs"].append(f"{rel} [{id_stable}] : identifiant stable déjà vu dans {vus[cle]}")
                continue
            vus[cle] = rel
            declares = []
            shas = []
            for nom in emp.noms_fichiers_declares(element):
                chemin_fig = os.path.join(os.path.dirname(chemin), nom)
                rel_fig = _rel(ingest, chemin_fig)
                if not os.path.isfile(chemin_fig):
                    res["erreurs"].append(f"{rel} [{id_stable}] : fichier déclaré introuvable {rel_fig}")
                    continue
                sha = emp.sha256_fichier(chemin_fig) if calculer_shas else ""
                declares.append({"nom": nom, "chemin": rel_fig, "sha256": sha, "taille": os.path.getsize(chemin_fig)})
                shas.append(sha)
                if calculer_shas:
                    res["fichiers"][rel_fig] = sha
            res["elements"].append({
                "id_stable": id_stable,
                "type": type_c,
                "fichier": rel,
                "index": index,
                "cle_naturelle": emp.cle_naturelle(type_c, rel, element),
                "empreinte_source": emp.empreinte_source(element, shas) if calculer_shas else "",
                "fichiers": declares,
            })
    return res


def empreinte_unite(analyse):
    """Empreinte de l'unité telle qu'elle sera livrée : tous ses JSON + les fichiers déclarés."""
    lignes = sorted(f"{rel}:{sha}" for rel, sha in analyse["fichiers"].items())
    return emp.sha256_octets("\n".join(lignes).encode("utf-8"))


def slug_unite(unite):
    return unite.replace("/", "__")


# --------------------------------------------------------------------------- controler / empreinte

def cmd_controler(args):
    total_err = 0
    rapport = []
    for unite in args.unites:
        a = analyser_unite(args.ingest, unite)
        total_err += len(a["erreurs"])
        rapport.append({k: a[k] for k in ("unite", "erreurs", "avertissements", "ignores")}
                       | {"elements": len(a["elements"]), "empreinte_unite": empreinte_unite(a)})
    if args.sortie:
        _json_ecrire(args.sortie, rapport)
    print(json.dumps({"unites": len(rapport), "erreurs": total_err,
                      "elements": sum(r["elements"] for r in rapport),
                      "detail": rapport if not args.sortie else None}, ensure_ascii=False))
    return 0 if total_err == 0 else 1


def cmd_empreinte(args):
    a = analyser_unite(args.ingest, args.unite)
    print(json.dumps({"unite": args.unite, "empreinte_unite": empreinte_unite(a),
                      "elements": len(a["elements"]), "erreurs": a["erreurs"]}, ensure_ascii=False))
    return 0 if not a["erreurs"] else 1


# --------------------------------------------------------------------------- inventaire

def _git(repo, *params):
    sortie = subprocess.run(["git", "-C", repo, *params], capture_output=True, check=True).stdout
    return [p for p in sortie.decode("utf-8", errors="replace").split("\0") if p]


def cmd_inventaire(args):
    repo = os.path.abspath(args.repo)
    ingest = os.path.join(repo, "backend", "ingest")
    suivis = {p[len("backend/ingest/"):] for p in _git(repo, "ls-files", "-z", "--", "backend/ingest")}
    modifies = set()
    for ligne in _git(repo, "status", "--porcelain=v1", "-z", "--", "backend/ingest"):
        # Format `XY chemin` ; un M dans X (indexé) ou Y (arbre de travail) = fichier suivi modifié.
        if len(ligne) > 3 and "M" in ligne[:2]:
            modifies.add(ligne[3:][len("backend/ingest/"):])
    base = None
    if args.base:
        with open(args.base, encoding="utf-8-sig") as f:
            b = json.load(f)
        base = {"exercice": set(b.get("exercices", [])), "cours": set(b.get("cours", [])), "quiz": set(b.get("items", []))}
    staging = set(os.listdir(os.path.join(ingest, "_gce_staging"))) if os.path.isdir(os.path.join(ingest, "_gce_staging")) else set()

    # Candidats : tous les JSON ingérables présents sur le disque (suivis ou non), regroupés par unité.
    par_unite = {}
    for racine_top in sorted(os.listdir(ingest)):
        top = os.path.join(ingest, racine_top)
        if not os.path.isdir(top) or (racine_top.startswith("_") and racine_top != "_quiz"):
            continue
        for dossier, dirs, fichiers in os.walk(top):
            dirs[:] = [d for d in dirs if not d.startswith("_")]
            for nom in fichiers:
                if not nom.lower().endswith(".json"):
                    continue
                rel = _rel(ingest, os.path.join(dossier, nom))
                if not emp.est_chemin_ingerable(rel):
                    continue
                u = par_unite.setdefault(emp.unite_de(rel), {"suivis": 0, "non_suivis": []})
                if rel in suivis:
                    u["suivis"] += 1
                else:
                    u["non_suivis"].append(rel)

    lignes = []
    totaux = {"unites_avec_non_suivis": 0, "json_non_suivis": 0, "en_base": 0, "absents_base": 0, "erreurs": 0}
    for unite, info in sorted(par_unite.items()):
        if not info["non_suivis"]:
            continue
        compte_types = {}
        en_base = absents = erreurs = 0
        details_erreurs = []
        for rel in info["non_suivis"]:
            try:
                data, _ = emp.lire_json(os.path.join(ingest, *rel.split("/")))
            except ValueError as exc:
                erreurs += 1
                details_erreurs.append(f"{rel} : {exc}")
                continue
            type_c = emp.type_de_contenu(rel, data)
            compte_types[type_c] = compte_types.get(type_c, 0) + 1
            if type_c not in emp.TYPES_V1:
                continue
            for id_stable, element in emp.elements(rel, data, type_c):
                if base is None:
                    continue
                if type_c == emp.TYPE_EXERCICE:
                    present = f"{element.get('epreuve_source')}|{element.get('numero_exercice')}" in base["exercice"]
                else:
                    present = id_stable in base[type_c]
                en_base += 1 if present else 0
                absents += 0 if present else 1
        nom_dossier = unite.split("/")[1] if unite.split("/")[0] != "_quiz" else ""
        if erreurs:
            statut = "erreur"
        elif base is None:
            statut = "base_inconnue"
        elif absents == 0:
            statut = "pret_pour_rattrapage"
        elif en_base == 0:
            statut = "jamais_ingere_en_local"
        else:
            statut = "partiellement_ingere"
        lignes.append({
            "unite": unite, "statut": statut, "json_suivis": info["suivis"],
            "json_non_suivis": len(info["non_suivis"]), "types": compte_types,
            "elements_en_base_locale": en_base, "elements_absents_base_locale": absents,
            "erreurs": details_erreurs, "copie_dans_gce_staging": nom_dossier in staging,
        })
        totaux["unites_avec_non_suivis"] += 1
        totaux["json_non_suivis"] += len(info["non_suivis"])
        totaux["en_base"] += en_base
        totaux["absents_base"] += absents
        totaux["erreurs"] += erreurs

    mod_ingerables = sorted(p for p in modifies if emp.est_chemin_ingerable(p))
    sortie = os.path.abspath(args.sortie)
    os.makedirs(sortie, exist_ok=True)
    _json_ecrire(os.path.join(sortie, "inventaire.json"), {"totaux": totaux, "unites": lignes,
                                                           "modifies_suivis": mod_ingerables})
    with open(os.path.join(sortie, "inventaire-unites.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("unite\tstatut\tjson_non_suivis\tjson_suivis\ten_base\tabsents_base\ttypes\tcopie_staging\n")
        for l in lignes:
            f.write("\t".join(str(x) for x in (
                l["unite"], l["statut"], l["json_non_suivis"], l["json_suivis"], l["elements_en_base_locale"],
                l["elements_absents_base_locale"], json.dumps(l["types"], ensure_ascii=False), l["copie_dans_gce_staging"],
            )) + "\n")
    comptes = {}
    for l in lignes:
        comptes[l["statut"]] = comptes.get(l["statut"], 0) + 1
    print(json.dumps({"totaux": totaux, "par_statut": comptes, "modifies_suivis": len(mod_ingerables),
                      "sortie": sortie}, ensure_ascii=False))
    return 0


# --------------------------------------------------------------------------- preparer

def _charger_json_optionnel(chemin):
    if not chemin:
        return None
    with open(chemin, encoding="utf-8-sig") as f:
        return json.load(f)


def _verifier_validation(validations, unite, empreinte, accepter_sans_tunnel):
    """Retourne (erreur|None, tunnel). Une validation périmée (contenu modifié depuis) est refusée."""
    chemin = os.path.join(validations, slug_unite(unite) + ".json")
    if not os.path.isfile(chemin):
        return f"{unite} : aucune validation locale (lancer `edukora.ps1 ingest-local`)", None
    with open(chemin, encoding="utf-8-sig") as f:
        v = json.load(f)
    if v.get("empreinte_unite") != empreinte:
        return f"{unite} : validation locale périmée (le contenu a changé depuis la validation)", None
    if v.get("locale") != "ok":
        return f"{unite} : validation locale en échec", None
    tunnel = v.get("tunnel")
    if tunnel == "valide":
        return None, "ok"
    if tunnel == "non_rejoue" and accepter_sans_tunnel:
        return None, "non_rejoue"
    return f"{unite} : tunnel de validation non passé (statut '{tunnel}')", None


# Fichiers que le poste écrit dans le dossier du lot pour son propre suivi : ni livrés, ni sommés.
FICHIERS_LOCAUX = frozenset({"etat.json"})


def _sommes_et_archive(racine_lot, archive):
    """(Re)écrit SHA256SUMS puis l'archive déterministe et son .sha256. Retourne le SHA-256 de l'archive."""
    fichiers = []
    for dossier, _, noms in os.walk(racine_lot):
        for nom in noms:
            if nom in FICHIERS_LOCAUX or nom == "SHA256SUMS":
                continue
            fichiers.append(os.path.join(dossier, nom))
    sommes = sorted((_rel(racine_lot, p), emp.sha256_fichier(p)) for p in fichiers)
    with open(os.path.join(racine_lot, "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as f:
        for rel, sha in sommes:
            f.write(f"{sha}  {rel}\n")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in sorted([r for r, _ in sommes] + ["SHA256SUMS"]):
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(os.path.join(racine_lot, *rel.split("/")), "rb") as src:
                z.writestr(info, src.read())
    sha_archive = emp.sha256_fichier(archive)
    with open(archive + ".sha256", "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{sha_archive}  {os.path.basename(archive)}\n")
    return sha_archive


def cmd_preparer(args):
    ingest = os.path.abspath(args.ingest)
    unites = list(args.unites)
    if args.liste:
        with open(args.liste, encoding="utf-8-sig") as f:
            unites += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not unites:
        print(json.dumps({"statut": "usage", "erreur": "aucune unité"}), file=sys.stderr)
        return 2
    unites = sorted(set(unites))
    reference = _charger_json_optionnel(args.reference)
    ref_contenus = (reference or {}).get("contenus", {})

    erreurs, avertissements, analyses = [], [], []
    for unite in unites:
        a = analyser_unite(ingest, unite)
        erreurs += a["erreurs"]
        avertissements += a["avertissements"] + a["ignores"]
        if a["erreurs"]:
            continue
        err, tunnel = _verifier_validation(args.validations, unite, empreinte_unite(a), args.accepter_sans_tunnel)
        if err:
            erreurs.append(err)
        a["tunnel"] = tunnel
        analyses.append(a)
    # Deux fichiers qui désignent le même exercice (même clé naturelle) donneraient deux identités pour un seul
    # objet : le second resterait bloqué pour toujours. Refus dès la préparation.
    vues = {}
    for a in analyses:
        for e in a["elements"]:
            if e["type"] != emp.TYPE_EXERCICE:
                continue
            cle = json.dumps(e["cle_naturelle"], sort_keys=True, ensure_ascii=False)
            if cle in vues and vues[cle] != e["id_stable"]:
                erreurs.append(f"clé naturelle en double : {e['id_stable']} et {vues[cle]} désignent le même exercice")
            vues.setdefault(cle, e["id_stable"])
    if erreurs:
        print(json.dumps({"statut": "refuse", "erreurs": erreurs}, ensure_ascii=False))
        return 1
    retraits = _charger_json_optionnel(args.retraits) or []
    for r in retraits:
        if r.get("type") not in emp.TYPES_V1 or not r.get("id_stable") or not str(r.get("motif") or "").strip():
            erreurs.append(f"retrait invalide (type, id_stable et motif obligatoires) : {r}")
    if erreurs:
        print(json.dumps({"statut": "refuse", "erreurs": erreurs}, ensure_ascii=False))
        return 1

    contenus = []
    for a in analyses:
        for e in a["elements"]:
            ref = ref_contenus.get(f"{e['type']}|{e['id_stable']}")
            if reference is None or not ref:
                operation, version_ref = "create", None
            elif ref.get("empreinte_source") == e["empreinte_source"]:
                operation, version_ref = "noop", ref.get("empreinte_source")
            else:
                operation, version_ref = "update", ref.get("empreinte_source")
            contenus.append({
                "type": e["type"], "id_stable": e["id_stable"], "cle_naturelle": e["cle_naturelle"],
                "operation": operation, "version_reference": version_ref,
                "version_proposee": e["empreinte_source"],
                "fichier": e["fichier"] if operation != "noop" else None, "index": e["index"],
                "fichiers": e["fichiers"] if operation != "noop" else [],
                "validation": {"locale": "ok", "tunnel": a["tunnel"], "relecture_humaine": "non_requise"},
            })
    for r in retraits:
        # Un retrait remplace l'entrée « inchangé » du même contenu ; il est incompatible avec une
        # création ou une mise à jour du même contenu dans le même lot.
        meme = [c for c in contenus if c["type"] == r["type"] and c["id_stable"] == r["id_stable"]]
        if any(c["operation"] != "noop" for c in meme):
            print(json.dumps({"statut": "refuse", "erreurs": [
                f"retrait de {r['id_stable']} incompatible avec sa publication dans le même lot"]}, ensure_ascii=False))
            return 1
        contenus = [c for c in contenus if c not in meme]
        contenus.append({"type": r["type"], "id_stable": r["id_stable"], "operation": "retirer",
                         "motif": r["motif"], "version_reference": None, "version_proposee": None,
                         "fichier": None, "index": 0, "fichiers": [], "cle_naturelle": {},
                         "validation": {"locale": "ok", "tunnel": "non_applicable", "relecture_humaine": "non_requise"}})
    contenus.sort(key=lambda c: (c["type"], c["id_stable"]))

    compteurs = {}
    for c in contenus:
        compteurs[c["operation"]] = compteurs.get(c["operation"], 0) + 1
    resume = {"unites": len(unites), "elements": len(contenus), "operations": compteurs,
              "reference_absente": reference is None, "avertissements": avertissements[:50]}

    if not args.approuve_par:
        print(json.dumps({"statut": "approbation_requise", **resume}, ensure_ascii=False))
        return 5
    if not [c for c in contenus if c["operation"] != "noop"]:
        print(json.dumps({"statut": "rien_a_publier", **resume}, ensure_ascii=False))
        return 0

    h8 = emp.sha256_octets(json.dumps(
        [[c["type"], c["id_stable"], c["operation"], c["version_reference"], c["version_proposee"]] for c in contenus],
        sort_keys=True, ensure_ascii=False).encode("utf-8"))[:8]
    # L'horodatage a la seconde pour résolution : deux préparations identiques dans la même seconde
    # attendent la suivante plutôt que d'écraser ou de refuser.
    for _ in range(5):
        maintenant = datetime.datetime.now(datetime.timezone.utc)
        batch_id = f"{maintenant:%Y%m%d-%H%M%S}-{h8}"
        racine_lot = os.path.join(os.path.abspath(args.lots), batch_id)
        if not os.path.exists(racine_lot):
            break
        time.sleep(1.05)
    else:
        print(json.dumps({"statut": "refuse", "erreurs": [f"{racine_lot} existe déjà"]}), file=sys.stderr)
        return 1

    # Copie octet pour octet des fichiers à livrer (miroir de backend/ingest).
    a_copier = set()
    for c in contenus:
        if c["fichier"]:
            a_copier.add(c["fichier"])
        a_copier.update(f["chemin"] for f in c["fichiers"])
    for rel in sorted(a_copier):
        dest = os.path.join(racine_lot, "ingest", *rel.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(os.path.join(ingest, *rel.split("/")), "rb") as src, open(dest, "wb") as dst:
            dst.write(src.read())

    manifeste = {
        "schema_sync": SCHEMA_SYNC, "version_empreinte": emp.VERSION_EMPREINTE, "batch_id": batch_id,
        "nom": args.nom or "", "cree_le": maintenant.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cree_par": args.machine or "poste",
        "application": {"sha_attendu": args.sha_attendu or None, "migrations_min": {}},
        "reference_prod": (None if reference is None else
                           {"exportee_le": reference.get("genere_le"), "sha256": emp.sha256_fichier(args.reference)}),
        "options": {"tout_ou_rien": bool(args.tout_ou_rien), "adopter": bool(args.adopter),
                    "retraits_confirmes": False, "reference_absente": reference is None},
        "approbation": {"par": args.approuve_par, "le": maintenant.strftime("%Y-%m-%dT%H:%M:%SZ")},
        "contenus": contenus,
    }
    _json_ecrire(os.path.join(racine_lot, "manifest.json"), manifeste)
    _json_ecrire(os.path.join(racine_lot, "approbations.json"), {"decisions": []})
    _json_ecrire(os.path.join(racine_lot, "rapport-prepare.json"), {**resume, "unites_liste": unites})

    archive = os.path.join(os.path.abspath(args.lots), f"lot-{batch_id}.zip")
    sha_archive = _sommes_et_archive(racine_lot, archive)

    print(json.dumps({"statut": "pret", "batch_id": batch_id, "archive": archive, "sha256_archive": sha_archive,
                      "dossier": racine_lot, **resume}, ensure_ascii=False))
    return 0


CLASSES_A_RESOUDRE = ("adoption_a_confirmer", "conflit_etat", "conflit_version", "conflit_identite")


def cmd_resoudre(args):
    """
    Écrit des décisions humaines dans `approbations.json` d'un lot (à partir du plan renvoyé par le serveur)
    puis reconstruit SHA256SUMS et l'archive. Chaque décision `ecraser` cite l'état de production que
    l'humain a vu et la version proposée du manifeste : elle ne vaut que pour eux.
    """
    racine_lot = os.path.abspath(args.lot)
    with open(os.path.join(racine_lot, "manifest.json"), encoding="utf-8-sig") as f:
        manifeste = json.load(f)
    versions = {c["id_stable"]: c["version_proposee"] for c in manifeste["contenus"]}
    with open(args.plan, encoding="utf-8-sig") as f:
        plan = json.load(f)
    if args.decision == "recreer" and not args.ids:
        print(json.dumps({"statut": "usage", "erreur": "recreer exige --ids explicites"}), file=sys.stderr)
        return 2
    if args.decision == "ecraser" and not str(args.motif or "").strip():
        print(json.dumps({"statut": "usage", "erreur": "ecraser exige --motif"}), file=sys.stderr)
        return 2
    ids = set(args.ids or [])
    classes = tuple(args.classes) if args.classes else CLASSES_A_RESOUDRE
    chemin = os.path.join(racine_lot, "approbations.json")
    existantes = {}
    if os.path.isfile(chemin):
        with open(chemin, encoding="utf-8-sig") as f:
            existantes = {d["id_stable"]: d for d in json.load(f).get("decisions", [])}
    maintenant = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    posees, ignorees = [], []
    for p in plan.get("plan", []):
        if p["resultat_prevu"] not in classes or (ids and p["id_stable"] not in ids):
            continue
        d = p.get("detail", {})
        id_stable = p["id_stable"]
        base = {"id_stable": id_stable, "decision": args.decision, "par": args.par, "le": maintenant,
                "motif": args.motif or "", "version_proposee": versions.get(id_stable)}
        if args.decision == "garder_prod":
            if p["resultat_prevu"] == "conflit_identite":
                ignorees.append(f"{id_stable} : garder_prod ne s'applique pas à un conflit d'identité")
                continue
            existantes[id_stable] = base
        elif args.decision == "ecraser":
            if not d.get("empreinte_etat_prod_vue"):
                ignorees.append(f"{id_stable} : pas d'état de production à approuver ({p['resultat_prevu']})")
                continue
            existantes[id_stable] = {**base, "empreinte_etat_prod_vue": d["empreinte_etat_prod_vue"],
                                     "version_prod_vue": d.get("version_prod_vue")}
        elif args.decision == "recreer":
            if p["resultat_prevu"] != "conflit_identite" or d.get("objet_journal_present", True) or not d.get("journal_objet_pk"):
                ignorees.append(f"{id_stable} : recreer ne vaut que pour un contenu purgé en production")
                continue
            existantes[id_stable] = {**base, "objet_pk_absent": d["journal_objet_pk"]}
        posees.append(id_stable)
    _json_ecrire(chemin, {"decisions": sorted(existantes.values(), key=lambda x: x["id_stable"])})
    archive = os.path.join(os.path.dirname(racine_lot), f"lot-{manifeste['batch_id']}.zip")
    sha_archive = _sommes_et_archive(racine_lot, archive)
    print(json.dumps({"statut": "ok", "decision": args.decision, "posees": len(posees), "ignorees": ignorees,
                      "archive": archive, "sha256_archive": sha_archive}, ensure_ascii=False))
    return 0 if posees or not ignorees else 1


def construire_parseur():
    p = argparse.ArgumentParser(prog="outil_lot")
    sp = p.add_subparsers(dest="cmd", required=True)

    c = sp.add_parser("controler")
    c.add_argument("ingest")
    c.add_argument("unites", nargs="+")
    c.add_argument("--sortie")
    c.set_defaults(fn=cmd_controler)

    e = sp.add_parser("empreinte")
    e.add_argument("ingest")
    e.add_argument("unite")
    e.set_defaults(fn=cmd_empreinte)

    i = sp.add_parser("inventaire")
    i.add_argument("repo")
    i.add_argument("--sortie", required=True)
    i.add_argument("--base", help="JSON {exercices, cours, items} exporté de la base locale")
    i.set_defaults(fn=cmd_inventaire)

    r = sp.add_parser("preparer")
    r.add_argument("--ingest", required=True)
    r.add_argument("--lots", required=True)
    r.add_argument("--validations", required=True)
    r.add_argument("--unites", nargs="*", default=[])
    r.add_argument("--liste")
    r.add_argument("--reference")
    r.add_argument("--retraits")
    r.add_argument("--nom")
    r.add_argument("--machine")
    r.add_argument("--sha-attendu")
    r.add_argument("--approuve-par")
    r.add_argument("--accepter-sans-tunnel", action="store_true")
    r.add_argument("--tout-ou-rien", action="store_true")
    r.add_argument("--adopter", action="store_true")
    r.set_defaults(fn=cmd_preparer)

    d = sp.add_parser("resoudre")
    d.add_argument("--lot", required=True, help="dossier du lot (batches/<batch_id>)")
    d.add_argument("--plan", required=True, help="JSON renvoyé par `sync_contenu planifier`")
    d.add_argument("--decision", required=True, choices=["garder_prod", "ecraser", "recreer"])
    d.add_argument("--ids", nargs="*", default=[])
    d.add_argument("--classes", nargs="*", default=[])
    d.add_argument("--par", required=True)
    d.add_argument("--motif", default="")
    d.set_defaults(fn=cmd_resoudre)
    return p


def main(argv=None):
    _sortie_utf8()
    args = construire_parseur().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
