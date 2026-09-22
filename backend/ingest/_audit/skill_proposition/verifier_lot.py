"""Auto-contrôle d'un dossier d'épreuve avant livraison (stdlib uniquement).
Usage : python verifier_lot.py <dossier_epreuve>   -> code 1 si un défaut BLOQUANT."""
import glob, json, re, sys, os

EXAMENS = {"bepc", "bfem", "probatoire", "bac", "autre"}
MATIERES_TI = {"Programmation", "Systèmes d'Information", "Réseaux, Internet et Sécurité Informatique"}
# mots courants qui, écrits sans accent, trahissent un texte « désaccentué » (hors code)
SANS_ACCENT = re.compile(
    r"\b(systeme|systemes|reseau|reseaux|methode|methodes|donnees|definir|definition|resultat|resultats|"
    r"etape|etapes|ecrire|probleme|modele|precedent|verifier|determiner|caracteristique|caracteristiques|"
    r"generale|utilise|realise|eleve|evenement|requete|selection|proprietes|periph\w+|memoire|numerique|"
    r"specifique|deduire|elaborer|representer|identifier_)\b", re.I)


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


def main(d):
    bloq, alertes = [], []
    rappel_ids = set()
    exos = sorted(glob.glob(os.path.join(d, "*_exercice_[0-9]*.json")))
    coursf = sorted(glob.glob(os.path.join(d, "*_cours_*.json")))
    for f in exos:
        j = json.load(open(f, encoding="utf-8")); n = os.path.basename(f)
        if j.get("examen") not in EXAMENS:
            bloq.append("%s : examen=%r hors liste (contrôle/devoir/composition → niveau visé + origine « etablissement »)" % (n, j.get("examen")))
        serie = str(j.get("serie") or "")
        if re.search(r"\bTI\b", serie) and j.get("matiere") not in MATIERES_TI:
            bloq.append("%s : série TI mais matiere=%r (Programmation | Systèmes d'Information | Réseaux, Internet et Sécurité Informatique)" % (n, j.get("matiere")))
        if re.search(r"\bA[1-5]\b", serie) and j.get("pays") == "cm":
            bloq.append("%s : Cameroun, série %r → le code est « A » (jamais A1..A5)" % (n, serie))
        for q in j.get("questions", []):
            rds = q.get("rappels_de_methode") or []
            c = q.get("corrige_markdown") or ""
            titres = len(re.findall(r"^###\s*Rappel de m[eé]thode\s*$", c, flags=re.M))
            for r in rds: rappel_ids.add(r.get("id"))
            if re.search(r"\*\*Rappel de m[eé]thode\.?\*\*", c):
                bloq.append("%s q%s : « **Rappel de méthode.** » en ligne → titre « ### Rappel de méthode » exigé" % (n, q.get("numero")))
            if len(rds) != titres:
                bloq.append("%s q%s : %d rappel(s) déclaré(s) mais %d titre(s) « ### Rappel de méthode » dans le corrigé" % (n, q.get("numero"), len(rds), titres))
            blocs = [re.sub(r"\A###\s*Rappel de m[eé]thode\s*\n+", "", m.group(0)).strip()
                     for m in re.finditer(r"###\s*Rappel de m[eé]thode\s*\n+.*?(?=\n{2,}|\n#{1,6}[ \t]|\n---|\Z)", c, flags=re.S | re.I)]
            for r in rds:
                ct = (r.get("contenu_markdown") or "").strip()
                if blocs and not any(ct and (ct.startswith(b) or b.startswith(ct)) for b in blocs):
                    bloq.append("%s q%s : rappel %s - contenu_markdown n'est pas la copie littérale d'un bloc du corrigé (lien « Voir le cours complet » rejeté en fin d'exercice)" % (n, q.get("numero"), r.get("id")))
            if not q.get("themes"):
                bloq.append("%s q%s : aucun thème" % (n, q.get("numero")))
        sa = sum(len(SANS_ACCENT.findall(hors_code(t))) for _, t in textes(j) if len(t) > 30)
        if sa > 3: alertes.append("%s : %d mot(s) courant(s) sans accent hors code (texte désaccentué ?)" % (n, sa))
    for f in coursf:
        c = json.load(open(f, encoding="utf-8")); n = os.path.basename(f)
        m, s = c.get("meta") or {}, c.get("source") or {}
        if not (c.get("cours_id") and m.get("titre") and m.get("matiere")):
            bloq.append("%s : cours_id / meta.titre / meta.matiere manquant (même pour un squelette)" % n)
        if not s.get("rappel_id"):
            bloq.append("%s : source.rappel_id nul" % n)
        elif rappel_ids and s["rappel_id"] not in rappel_ids:
            bloq.append("%s : source.rappel_id=%r absent des exercices du dossier" % (n, s["rappel_id"]))
        if str(m.get("serie") or "") == "TI" and m.get("matiere") == "Informatique":
            bloq.append("%s : série TI et matiere « Informatique »" % n)
        if not c.get("sections"):
            alertes.append("%s : squelette (sections vides) - valable seulement si le titre est IDENTIQUE, accents compris, à un titre du catalogue" % n)
        if SANS_ACCENT.search(m.get("titre") or ""):
            alertes.append("%s : titre sans accents" % n)
        for chemin, t in textes(c):
            if re.search(r"(?<![\$`])\$(?!\$)", hors_code(t)) and hors_code(t).count("$") % 2:
                alertes.append("%s %s : `$` littéral hors code" % (n, chemin)); break
    print("Dossier %s : %d exercice(s), %d cours" % (d, len(exos), len(coursf)))
    for b in bloq: print("[BLOQUANT]", b)
    for a in alertes: print("[ALERTE]", a)
    print("LOT PROPRE" if not bloq else "LOT À CORRIGER")
    return 1 if bloq else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
