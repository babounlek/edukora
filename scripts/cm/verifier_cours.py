"""Contrôle des cours d'un dossier francophone avant livraison (stdlib uniquement).

Usage : python verifier_cours.py <dossier_cours_staging> <dossier_exercices_cm> <plan.json>
  - dossier_cours_staging : ex. backend/ingest/_cm_staging_cours/<dossier>/   (fichiers *_cours_*.json)
  - dossier_exercices_cm  : ex. backend/ingest/cm/<dossier>/                  (fichiers *_exercice_*.json)
  - plan.json             : ex. backend/ingest/_cm_plan_cours/<dossier>.json  (clé "a_rediger")
Code de sortie 1 si un défaut BLOQUANT est trouvé.
"""
import glob
import json
import os
import re
import sys

ORDRE = ["accroche", "prerequis", "regle", "exemple_resolu", "erreurs_classiques", "exercices_application", "synthese"]
SANS_ACCENT = re.compile(
    r"\b(systeme|systemes|reseau|reseaux|methode|methodes|donnees|definir|definition|resultat|resultats|"
    r"etape|etapes|ecrire|probleme|modele|precedent|verifier|determiner|caracteristique|caracteristiques|"
    r"generale|utilise|realise|eleve|evenement|requete|selection|proprietes|memoire|numerique|"
    r"specifique|deduire|elaborer|representer)\b", re.I)


def hors_code(s):
    s = re.sub(r"```.*?```", " ", s, flags=re.S)
    return re.sub(r"`[^`\n]*`", " ", s)


def textes(o, chemin=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from textes(v, chemin + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from textes(v, "%s[%d]" % (chemin, i))
    elif isinstance(o, str):
        yield chemin, o


def main(dcours, dexos, plan_path):
    bloq, alertes = [], []
    plan = json.load(open(plan_path, encoding="utf-8"))
    attendus = {e["cours_id"]: e for e in plan.get("a_rediger", [])}
    squelettes = {e["cours_id"]: e for e in plan.get("squelettes", [])}
    n_squelettes = 0
    rappels = {}
    for f in glob.glob(os.path.join(dexos, "*_exercice_[0-9]*.json")):
        j = json.load(open(f, encoding="utf-8"))
        for q in j["questions"]:
            for r in q.get("rappels_de_methode") or []:
                rappels[r["id"]] = j
    vus = set()
    fichiers = sorted(glob.glob(os.path.join(dcours, "*_cours_*.json")))
    for f in fichiers:
        n = os.path.basename(f)
        try:
            c = json.load(open(f, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            bloq.append("%s : JSON illisible (%s)" % (n, e)); continue
        cid = c.get("cours_id"); m = c.get("meta") or {}; s = c.get("source") or {}
        if cid in squelettes and c.get("sections") == []:
            sq = squelettes[cid]
            if m.get("titre") != sq["titre_exact"] or s.get("rappel_id") != sq["rappel_id"]:
                bloq.append("%s : squelette différent du plan" % n)
            n_squelettes += 1
            continue
        att = attendus.get(cid)
        if not att:
            bloq.append("%s : cours_id %r absent du plan (a_rediger)" % (n, cid)); continue
        vus.add(cid)
        if m.get("titre") != att["titre_exact"]:
            bloq.append("%s : meta.titre %r doit être EXACTEMENT %r" % (n, m.get("titre"), att["titre_exact"]))
        if s.get("rappel_id") != att["rappel_id"]:
            bloq.append("%s : source.rappel_id %r doit être %r" % (n, s.get("rappel_id"), att["rappel_id"]))
        if s.get("rappel_id") not in rappels:
            bloq.append("%s : source.rappel_id absent des exercices du dossier" % n)
        if sorted(s.get("rappels_lies") or []) != sorted(att["rappels_lies"]):
            bloq.append("%s : source.rappels_lies différent du plan" % n)
        ex = rappels.get(att["rappel_id"]) or {}
        if m.get("matiere") != att["matiere"]:
            bloq.append("%s : meta.matiere %r doit être %r" % (n, m.get("matiere"), att["matiere"]))
        if m.get("pays") != "cm":
            bloq.append("%s : meta.pays doit être 'cm'" % n)
        if (m.get("serie") or None) != (att["serie"] or None):
            bloq.append("%s : meta.serie %r doit être %r" % (n, m.get("serie"), att["serie"]))
        if m.get("statut") != "brouillon":
            bloq.append("%s : meta.statut doit être 'brouillon'" % n)
        if not (3 <= len(m.get("tags") or []) <= 6):
            bloq.append("%s : meta.tags doit contenir 3 à 6 tags" % n)
        if not m.get("sous_theme") or not m.get("niveau") or not m.get("duree_estimee_min"):
            bloq.append("%s : meta.sous_theme / niveau / duree_estimee_min manquant" % n)
        if re.search(r"\bTI\b", str(att["serie"] or "")) and att["matiere"] == "Informatique":
            bloq.append("%s : série TI et matière Informatique interdit" % n)
        types = [x.get("type") for x in c.get("sections") or []]
        if types != ORDRE:
            bloq.append("%s : sections %s, attendu %s" % (n, types, ORDRE))
        else:
            sec = {x["type"]: x for x in c["sections"]}
            if not (sec["accroche"].get("contenu_markdown") or "").strip():
                bloq.append("%s : accroche vide" % n)
            if not sec["prerequis"].get("items"):
                bloq.append("%s : prérequis vides" % n)
            if not (sec["regle"].get("contenu_markdown") or "").strip():
                bloq.append("%s : règle vide" % n)
            e = sec["exemple_resolu"]
            if not e.get("enonce_markdown") or len(e.get("etapes") or []) < 2 or not e.get("conclusion_markdown"):
                bloq.append("%s : exemple résolu incomplet (énoncé, >= 2 étapes, conclusion)" % n)
            for et in e.get("etapes") or []:
                if not (et.get("action") and et.get("justification") and et.get("resultat_markdown")):
                    bloq.append("%s : étape %s de l'exemple incomplète" % (n, et.get("numero"))); break
            ec = sec["erreurs_classiques"].get("items") or []
            if not 2 <= len(ec) <= 4 or any(not (i.get("erreur_markdown") and i.get("pourquoi_faux") and i.get("correction_markdown")) for i in ec):
                bloq.append("%s : erreurs classiques : 2 à 4 items complets exigés" % n)
            ea = sec["exercices_application"].get("items") or []
            if [i.get("difficulte") for i in ea] != ["facile", "moyen", "approfondissement"]:
                bloq.append("%s : exercices d'application : facile, moyen, approfondissement exigés" % n)
            for i in ea:
                if not (i.get("enonce_markdown") or "").strip() or len((i.get("solution_markdown") or "").strip()) < 40:
                    bloq.append("%s : exercice %s sans énoncé ou sans solution complète" % (n, i.get("numero")))
            if not 4 <= len(sec["synthese"].get("items_markdown") or []) <= 6:
                bloq.append("%s : synthèse : 4 à 6 points exigés" % n)
        for chemin, t in textes(c):
            if "—" in t or "–" in t:
                bloq.append("%s %s : tiret cadratin ou demi-cadratin" % (n, chemin)); break
        for chemin, t in textes(c):
            if "\t" in t or "\x08" in t or "\x0c" in t:
                bloq.append("%s %s : caractère de contrôle (backslash LaTeX non doublé ?)" % (n, chemin)); break
        for chemin, t in textes(c):
            h = hors_code(t)
            if h.count("$") % 2 and not re.search(r"\$\$", h):
                alertes.append("%s %s : nombre impair de `$` hors code" % (n, chemin)); break
        sa = sum(len(SANS_ACCENT.findall(hors_code(t))) for _, t in textes(c) if len(t) > 30)
        if sa > 3:
            alertes.append("%s : %d mot(s) courant(s) sans accent hors code" % (n, sa))
    for cid, att in attendus.items():
        if cid not in vus:
            bloq.append("cours manquant : %s (%s)" % (att["titre_exact"], cid))
    print("Dossier %s : %d cours livrés / %d attendus (+ %d squelettes)" % (dcours, len(fichiers) - n_squelettes, len(attendus), n_squelettes))
    for b in bloq: print("[BLOQUANT]", b)
    for a in alertes: print("[ALERTE]", a)
    print("COURS PROPRES" if not bloq else "COURS A CORRIGER")
    return 1 if bloq else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
