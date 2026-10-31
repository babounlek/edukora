"""Mode AUDIT : cartographie du corpus (étape 1, lecture seule).

Croise l'instantané de la base locale (`extraire_base.py`), les dossiers d'ingestion, les zones de staging,
les PDF téléchargés, la référence de production tenue par la chaîne de lots et le registre des décisions.
Écrit uniquement dans `backend/ingest/_audit/corpus/<date>/`.
"""
import collections
import csv
import json
import os
import re

import referentiel
import registre
from commun import (
    AUDIT, EPREUVES, FAUTES_CONNUES, INGEST, RACINE_DEPOT, analyser_nom_pdf_gce, annee_du_nom,
    dossier_depuis_epreuve_source, epreuve_source_du_dossier, est_dossier_epreuve, lister_dossiers, lister_pdf, normaliser,
)

ETATS = (
    "PUBLIE_PROD", "LOCAL_VALIDE_PROD_INCONNUE", "LOCAL_BROUILLON", "TELECHARGE_NON_INGERE",
    "STAGING_VALIDE_EN_SUSPENS", "ECARTE", "INTROUVABLE_DOCUMENTE", "INEXISTANT", "MANQUANT",
)
RANG = {e: i for i, e in enumerate(ETATS)}


def _dossiers_dans_reference(chemin_reference):
    """Noms de dossiers (cm/<dossier>/...) présents dans la référence de production de la chaîne de lots."""
    if not os.path.isfile(chemin_reference):
        return set()
    with open(chemin_reference, encoding="utf-8") as fh:
        contenus = json.load(fh).get("contenus", {})
    dossiers = set()
    for cle in contenus:
        morceaux = cle.split("|", 1)[-1].split("/")
        if len(morceaux) >= 2:
            dossiers.add(morceaux[1])
    return dossiers


def _examen(lecon):
    examens = {c["examen"] for c in lecon["cursus"] if c.get("examen")}
    return sorted(examens)[0] if examens else None


def _series(lecon):
    series = sorted({c["serie"] for c in lecon["cursus"] if c.get("serie")})
    return series or [""]


def etat_lecon(lecon, en_reference):
    if lecon["statut"] != "VALIDE":
        return "ECARTE"
    return "PUBLIE_PROD" if dossier_depuis_epreuve_source(lecon["epreuve_source"]) in en_reference else "LOCAL_VALIDE_PROD_INCONNUE"


def charger_base(chemin_base):
    with open(chemin_base, encoding="utf-8") as fh:
        return json.load(fh)


def analyser(base, chemin_reference, dossier_ingest=INGEST):
    """Retourne un dict `carte` : cellules, incohérences, staging, téléchargements, synthèses."""
    en_reference = _dossiers_dans_reference(chemin_reference)
    dossiers_cm = set(lister_dossiers(os.path.join(dossier_ingest, "cm")))
    dossiers_cm_epreuves = {d for d in dossiers_cm if est_dossier_epreuve(d)}
    staging = {}
    for nom in ("_gce_staging", "_cm_staging"):
        for d in lister_dossiers(os.path.join(dossier_ingest, nom)):
            staging.setdefault(d, nom)

    # --- cellules observées (épreuves OFFICIELLES comptent pour la couverture ; D2) ------------------
    observees = collections.defaultdict(list)        # clé de cellule -> [leçons]
    hors_couverture = []                             # blancs, zéro, établissement
    for l in base:
        langue = "en" if l.get("langue") == "en" else "fr"
        examen = _examen(l)
        annee = l.get("annee") or annee_du_nom(l.get("epreuve_source"))
        if l.get("origine") != "OFFICIEL":
            hors_couverture.append(l)
            continue
        if langue == "fr" and referentiel.hors_perimetre(l.get("matiere")):
            continue
        if langue == "en":
            observees[("en", examen, "", l["matiere"], annee, l.get("paper"))].append(l)
        else:
            for serie in _series(l):
                observees[("fr", examen, serie, l["matiere"], annee, None)].append(l)

    # --- attendu ------------------------------------------------------------------------------------
    attendues = {}
    # GCE : liste officielle du Board x période x papers observés
    papers_vus = collections.defaultdict(lambda: collections.defaultdict(set))
    for (sys_, examen, _s, matiere, annee, paper), lecons in observees.items():
        if sys_ == "en" and annee and paper:
            papers_vus[(examen, matiere)][paper].add(annee)
    debut, fin = referentiel.PERIODE_DEFAUT
    for niveau in ("GCE_OL", "GCE_AL"):
        for matiere in referentiel.matieres_gce(niveau):
            papiers = {p for p, ans in papers_vus[(niveau, matiere)].items()
                       if len({a for a in ans if debut <= a <= fin}) >= 2} or set()
            pratique = matiere in referentiel.P3_PRATIQUES
            if not papiers:
                papiers = {1, 2}  # matière absente ou presque : papers usuels, signalée « matière absente »
            for annee in range(debut, referentiel.SESSION_EN_COURS + 1):
                for paper in sorted(papiers):
                    attendues[("en", niveau, "", matiere, annee, paper)] = {
                        "pratique": pratique and paper >= 3,
                        "matiere_absente": not papers_vus[(niveau, matiere)],
                    }
    obs_fr = []
    for (sys_, examen, serie, matiere, annee, _p) in observees:
        if sys_ == "fr":
            obs_fr.append((examen, serie, matiere, annee))
    for (examen, serie, matiere, annee) in referentiel.grille_francophone(obs_fr):
        attendues[("fr", examen, serie, matiere, annee, None)] = {"pratique": False, "matiere_absente": False}

    # --- états --------------------------------------------------------------------------------------
    decisions = registre.etat_des_cibles()
    cellules = []
    toutes = set(observees) | set(attendues)
    for cle in sorted(toutes, key=lambda c: tuple(str(x) for x in c)):
        sys_, examen, serie, matiere, annee, paper = cle
        lecons = observees.get(cle, [])
        if lecons:
            etat = min((etat_lecon(l, en_reference) for l in lecons), key=lambda e: RANG[e])
        else:
            if sys_ == "en":
                ident = registre.cle_cible_gce(examen, matiere, annee, paper)
            else:
                ident = registre.cle_cible_fr(examen, serie, matiere, annee)
            fait = decisions.get(ident)
            etat = {"introuvable": "INTROUVABLE_DOCUMENTE", "ecarte": "ECARTE", "inexistant": "INEXISTANT"}.get(
                fait["resultat"] if fait else None, "MANQUANT")
        cellules.append({
            "systeme": sys_, "examen": examen, "serie": serie, "matiere": matiere, "annee": annee,
            "paper": paper, "attendue": cle in attendues, "etat": etat,
            "nb_lecons": len(lecons), "ids": [l["id"] for l in lecons],
            "pratique": attendues.get(cle, {}).get("pratique", False),
            "matiere_absente": attendues.get(cle, {}).get("matiere_absente", False),
        })

    # équivalences de matière (HISTOIRE_GEO / HISTOIRE + GEOGRAPHIE, SVT / SCIENCES) : cellule satisfaite
    presentes = {(c["systeme"], c["examen"], c["serie"], c["matiere"], c["annee"], c["paper"])
                 for c in cellules if c["etat"] in ("PUBLIE_PROD", "LOCAL_VALIDE_PROD_INCONNUE")}
    for c in cellules:
        if c["attendue"] and c["etat"] == "MANQUANT" and c["matiere"] in referentiel.EQUIVALENCES:
            equivalentes = referentiel.EQUIVALENCES[c["matiere"]]
            if any((c["systeme"], c["examen"], c["serie"], m, c["annee"], c["paper"]) in presentes for m in equivalentes):
                c["attendue"] = False
                c["etat"] = "MANQUANT"
                c["equivalence"] = True

    # --- incohérences -------------------------------------------------------------------------------
    incoherences = []
    noms_base = set()
    sources_des_dossiers = {d: epreuve_source_du_dossier(os.path.join(dossier_ingest, "cm", d)) for d in dossiers_cm_epreuves}
    sources_connues = {s for s in sources_des_dossiers.values() if s}
    for l in base:
        nom = dossier_depuis_epreuve_source(l["epreuve_source"])
        noms_base.add(nom)
        if nom not in dossiers_cm and nom not in sources_connues:
            incoherences.append(("base_sans_dossier", l["id"], nom, "aucun dossier cm/ ne porte ce nom ni cet epreuve_source"))
        annee_nom = annee_du_nom(nom)
        if l.get("annee") is None:
            incoherences.append(("annee_manquante", l["id"], nom, "Lesson.year vide" + (
                " (nom : %s)" % annee_nom if annee_nom else "")))
        elif annee_nom and annee_nom != l["annee"]:
            incoherences.append(("annee_base_vs_nom", l["id"], nom, "base %s, nom %s" % (l["annee"], annee_nom)))
        if any(f in nom for f in FAUTES_CONNUES):
            incoherences.append(("epreuve_source_fautif", l["id"], nom, "faute de frappe connue dans le nom"))
        bas = nom.lower()
        if ("-zero" in bas or "epreuve-zero" in bas) and l.get("origine") == "OFFICIEL":
            incoherences.append(("origine_vs_nom", l["id"], nom, "nom « zéro » mais origine OFFICIEL"))
        if ("-blanc" in bas or "blanc-" in bas) and l.get("origine") == "OFFICIEL":
            incoherences.append(("origine_vs_nom", l["id"], nom, "nom « blanc » mais origine OFFICIEL"))
        if l.get("langue") == "en" and not l.get("paper"):
            incoherences.append(("paper_manquant", l["id"], nom, "GCE sans numero_paper"))
        if l["statut"] != "VALIDE":
            incoherences.append(("statut_" + l["statut"].lower(), l["id"], nom, "épreuve non VALIDE en base"))
        if l.get("sujet_pdf_existe") is False:
            incoherences.append(("sujet_pdf_sans_fichier", l["id"], nom, l.get("sujet_pdf") or ""))
        if l.get("figures_sans_fichier"):
            incoherences.append(("figures_sans_fichier", l["id"], nom, "%s figure(s)" % l["figures_sans_fichier"]))
        if l["nb_exercices"] == 0:
            incoherences.append(("epreuve_sans_exercice", l["id"], nom, ""))
    for d in sorted(dossiers_cm_epreuves):
        if d not in noms_base and sources_des_dossiers.get(d) not in noms_base:
            incoherences.append(("dossier_sans_base", "", d, "dossier cm/ sans Lesson (ni par nom ni par epreuve_source)"))
    for d, zone in sorted(staging.items()):
        if d not in noms_base:
            incoherences.append(("staging_non_ingere", "", d, zone))

    # --- téléchargements non ingérés ----------------------------------------------------------------
    telecharges = []
    racine_non_traites = os.path.join(EPREUVES, "non_traites")
    dossiers_pdf = [
        os.path.join(racine_non_traites, "anglophone", "avant_2019"),
        os.path.join(racine_non_traites, "anglophone", "avant_2019", "_a_verifier"),
        os.path.join(racine_non_traites, "anglophone", "_a_verifier"),
        os.path.join(racine_non_traites, "anglophone", "avant_2019", "_hors_cible"),
    ] + [os.path.join(dossier_ingest, d) for d in os.listdir(dossier_ingest) if d.startswith("_telechargements_")]
    for dossier_pdf in dossiers_pdf:
        for nom in lister_pdf(dossier_pdf):
            info = analyser_nom_pdf_gce(nom)
            telecharges.append({"dossier": dossier_pdf, "fichier": nom, "gce": info})

    return {
        "cellules": cellules, "incoherences": incoherences, "telecharges": telecharges,
        "hors_couverture": hors_couverture, "nb_lecons": len(base),
        "dossiers_cm": len(dossiers_cm_epreuves), "en_reference": len(en_reference),
        "staging": staging,
    }


def synthese(carte):
    """Couverture par (système, examen) avec dénominateur explicite : attendu, présent, manquant, taux."""
    lignes = collections.OrderedDict()
    for c in carte["cellules"]:
        if not c["attendue"] or c["pratique"]:
            continue
        cle = (c["systeme"], c["examen"])
        s = lignes.setdefault(cle, collections.Counter())
        s["attendu"] += 1
        present = c["etat"] in ("PUBLIE_PROD", "LOCAL_VALIDE_PROD_INCONNUE")
        s["present"] += 1 if present else 0
        s["manquant"] += 0 if present else 1
        s["publie_chaine"] += 1 if c["etat"] == "PUBLIE_PROD" else 0
    return lignes


def ecrire_sorties(carte, dossier_sortie):
    os.makedirs(dossier_sortie, exist_ok=True)
    chemin_matrice = os.path.join(dossier_sortie, "matrice_corpus.tsv")
    with open(chemin_matrice, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["systeme", "examen", "serie", "matiere", "annee", "paper", "attendue", "etat", "nb_epreuves", "ids", "p3_pratique", "matiere_absente"])
        for c in carte["cellules"]:
            w.writerow([c["systeme"], c["examen"], c["serie"], c["matiere"], c["annee"], c["paper"] or "",
                        "oui" if c["attendue"] else "non", c["etat"], c["nb_lecons"],
                        ",".join(map(str, c["ids"])), "oui" if c["pratique"] else "", "oui" if c["matiere_absente"] else ""])
    chemin_inco = os.path.join(dossier_sortie, "incoherences.tsv")
    with open(chemin_inco, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["type", "lesson_id", "objet", "detail"])
        for ligne in carte["incoherences"]:
            w.writerow(ligne)
    return chemin_matrice, chemin_inco


def rapport_markdown(carte, date):
    s = synthese(carte)
    lignes = ["# Cartographie du corpus EduKora - %s" % date, "",
              "Lecture seule. Base locale : %d épreuves ; dossiers `cm/` : %d ; dossiers présents dans la référence de "
              "production de la chaîne de lots : %d." % (carte["nb_lecons"], carte["dossiers_cm"], carte["en_reference"]), "",
              "> `PUBLIE_PROD` = passé par la chaîne de lots. Le contenu publié avant la chaîne n'est pas lisible depuis "
              "ici (pas d'accès direct à la production) : il apparaît `LOCAL_VALIDE_PROD_INCONNUE`.", ""]

    lignes += ["## Session 2026 (priorité 1)", ""]
    s26 = [c for c in carte["cellules"] if c["annee"] == referentiel.SESSION_EN_COURS and c["attendue"] and not c["pratique"]]
    parser = collections.Counter((c["systeme"], c["examen"], c["etat"]) for c in s26)
    for (sys_, ex, etat), n in sorted(parser.items()):
        lignes.append("- %s %s : %d cellule(s) `%s`" % (sys_, ex, n, etat))
    manquants26 = [c for c in s26 if c["etat"] not in ("PUBLIE_PROD", "LOCAL_VALIDE_PROD_INCONNUE")]
    lignes += ["", "Manquants en 2026 (%d) :" % len(manquants26), ""]
    for c in sorted(manquants26, key=lambda c: (c["systeme"], c["examen"], c["matiere"], c["serie"], c["paper"] or 0)):
        lignes.append("- %s %s %s%s%s" % (c["systeme"], c["examen"], c["matiere"],
                      " série %s" % c["serie"] if c["serie"] else "", " P%s" % c["paper"] if c["paper"] else ""))
    lignes.append("")

    lignes += ["## Couverture (%d-%d, session en cours incluse, épreuves officielles, P3 pratiques exclus)" % (referentiel.PERIODE_DEFAUT[0], referentiel.SESSION_EN_COURS), "",
               "| Système | Examen | Attendu | Présent | Manquant | Taux | Dont publié par la chaîne |", "|---|---|---|---|---|---|---|"]
    for (sys_, ex), c in s.items():
        taux = 100.0 * c["present"] / c["attendu"] if c["attendu"] else 0.0
        lignes.append("| %s | %s | %d | %d | %d | %.0f %% | %d |" % (sys_, ex, c["attendu"], c["present"], c["manquant"], taux, c["publie_chaine"]))
    lignes.append("")

    manquantes = [c for c in carte["cellules"] if c["attendue"] and not c["pratique"]
                  and c["etat"] not in ("PUBLIE_PROD", "LOCAL_VALIDE_PROD_INCONNUE")]
    lignes += ["## Lacunes (%d cellules attendues manquantes)" % len(manquantes), ""]
    groupes = collections.defaultdict(list)
    for c in manquantes:
        groupes[(c["systeme"], c["examen"], c["matiere"], c["serie"])].append((c["annee"], c["paper"], c["etat"]))
    for (sys_, ex, matiere, serie), items in sorted(groupes.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        annees = ", ".join("%s%s" % (a, "/P%s" % p if p else "") for a, p, _e in sorted(items))
        lignes.append("- %s %s %s%s : %s" % (sys_, ex, matiere, " série %s" % serie if serie else "", annees))
    lignes.append("")

    c3 = [c for c in carte["cellules"] if c["attendue"] and c["pratique"]]
    lignes += ["## P3 pratiques GCE (comptés à part)", "",
               "%d cellules attendues, dont %d présentes." % (
                   len(c3), sum(1 for c in c3 if c["etat"] in ("PUBLIE_PROD", "LOCAL_VALIDE_PROD_INCONNUE"))), ""]

    lignes += ["## Épreuves hors couverture (blancs, sujets zéro, établissement)", "",
               "%d épreuves, jamais comptées dans la couverture officielle (D2)." % len(carte["hors_couverture"]), ""]

    lignes += ["## Téléchargés ou en staging, pas ingérés", ""]
    lignes.append("- PDF dans les zones de dépôt : %d" % len(carte["telecharges"]))
    lignes.append("- dossiers de staging sans épreuve en base : %d" % sum(
        1 for ligne in carte["incoherences"] if ligne[0] == "staging_non_ingere"))
    lignes.append("")

    compte = collections.Counter(ligne[0] for ligne in carte["incoherences"])
    lignes += ["## Incohérences (%d)" % len(carte["incoherences"]), "", "| Type | Nombre |", "|---|---|"]
    for t, n in compte.most_common():
        lignes.append("| %s | %d |" % (t, n))
    lignes.append("")
    lignes.append("Détail ligne à ligne : `incoherences.tsv`. Matrice complète : `matrice_corpus.tsv`.")
    lignes.append("")
    return "\n".join(lignes)
