r"""Verifie les 50 QCM du Paper 1 French inedit, SANS pouvoir recalculer la grammaire (aucun correcteur de francais n'est installe) :

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_french_p1.py [ep-....json]

Controles mecaniques (sortie 1 au moindre ecart) :
  1. la cle est l'option qui porte exactement le texte de la bonne reponse, et elle est la seule ; options distinctes ; CHAQUE distracteur porte la raison de son erreur
     (le second passage « existe-t-il une deuxieme option acceptable ? » est ecrit dans le corrige) ;
  2. QUESTIONS A TROU : l'enonce rempli avec la bonne option donne exactement la phrase complete ecrite a part ;
  3. TEXTE A TROUS (46-50) : le texte rempli avec les cinq bonnes reponses, dans l'ordre, donne exactement le texte complet ; les cinq cles sont celles du texte ;
  4. ORIGINALITE : aucune suite de 6 mots n'est commune a un enonce, une option ou un texte de l'inedite et a un vrai sujet French O/L du corpus ;
  5. typographie : pas de double espace, pas d'espace avant une virgule ou un point, pas de tiret cadratin, apostrophes toutes droites ; la bonne option n'est pas systematiquement la plus longue.
La correction du francais lui-meme (accords, concordance des temps, orthographe) reste une RELECTURE HUMAINE : voir le compte rendu.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import questions_french_p1 as C  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAUT = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-french-p1-1-2026-s1.json")
CORPUS = os.path.join(RACINE, "backend", "ingest", "cm")
BLANC = "\\_\\_\\_\\_\\_\\_"
ENTETES = ("**Text for questions", "*Read the text below", "(Text for questions", "**Space ")


def mots(t):
    return re.findall(r"[\wàâäçéèêëîïôöùûüÿœæ']+", t.lower().replace("\\_", " "))


def ngrammes(t, n=6):
    m = mots(t)
    return {" ".join(m[i:i + n]) for i in range(len(m) - n + 1)}


def normaliser_phrase(t):
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"' ", "'", t)
    t = re.sub(r" ([,.;:?!])", r"\1", t)
    return t


def sans_entetes(t):
    return "\n\n".join(p for p in t.split("\n\n") if not p.startswith(ENTETES))


def textes_reels():
    for dossier in sorted(glob.glob(os.path.join(CORPUS, "gce-ol-french-*"))):
        for f in glob.glob(os.path.join(dossier, "*.json")):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except ValueError:
                continue
            morceaux = [d.get("introduction_markdown") or "", d.get("enonce_intro_markdown") or ""]
            for q in d.get("questions", []):
                morceaux += [q.get("enonce_markdown") or "", q.get("corrige_markdown") or ""]
                morceaux += [c.get("texte", "") for c in q.get("choix") or []]
            yield os.path.basename(dossier), "\n".join(morceaux)


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf-8"))
    qj = ep["exercices"][0]["questions"]
    qs = C.questions()
    erreurs, avert = [], []
    assert len(qj) == len(qs) == 50

    # 1. cle unique, options distinctes, raisons
    for n, (j, q) in enumerate(zip(qj, qs), start=1):
        textes = {c["lettre"]: c["texte"] for c in j["choix"]}
        egaux = [l for l, t in textes.items() if t == q["ok"]]
        if egaux != [j["reponse_correcte"]]:
            erreurs.append(f"Q{n}: cle {j['reponse_correcte']} mais la bonne option est en {egaux}")
        if len({t.strip().lower() for t in textes.values()}) != 4:
            erreurs.append(f"Q{n}: options en double")
        if len(q["raisons"]) != 3 or not all(len(r) >= 12 for r in q["raisons"]):
            erreurs.append(f"Q{n}: il manque la raison de l'erreur d'un distracteur")
        for r in q["raisons"]:
            if "\u2014" in r:
                erreurs.append(f"Q{n}: tiret cadratin dans une raison")
    # le corrige cite chaque distracteur avec sa raison
    for n, (j, q) in enumerate(zip(qj, qs), start=1):
        for b in q["bad"]:
            if f"*{b}*" not in j["corrige_markdown"]:
                erreurs.append(f"Q{n}: le distracteur {b!r} n'est pas explique dans le corrige")

    # 2. questions a trou : l'enonce rempli donne la phrase complete
    n_trous = 0
    for n, (j, q) in enumerate(zip(qj, qs), start=1):
        if not q["complete"]:
            continue
        derniere = j["enonce_markdown"].split("\n\n")[-1]
        if BLANC not in derniere:
            erreurs.append(f"Q{n}: pas de trou dans l'enonce")
            continue
        rempli = normaliser_phrase(derniere.replace(BLANC, " " + q["ok"] + " "))
        if normaliser_phrase(q["complete"]) not in rempli:
            erreurs.append(f"Q{n}: enonce rempli {rempli!r} different de la phrase complete {q['complete']!r}")
        n_trous += 1
    print("phrases completes confrontees a l'enonce rempli :", n_trous)

    # 3. texte a trous
    corps = [p for p in C.TEXTE.split("\n\n") if p.startswith("Dans le village")][0]
    corps = re.sub(r"\s*\(\d\d\)", "", corps)
    reponses = list(C.REPONSES_TEXTE)
    if corps.count(BLANC) != 5:
        erreurs.append(f"le texte doit porter 5 trous ({corps.count(BLANC)})")
    rempli = corps
    for r in reponses:
        rempli = rempli.replace(BLANC, r, 1)
    if normaliser_phrase(rempli) != normaliser_phrase(C.COMPLET):
        erreurs.append("le texte rempli avec les 5 reponses n'est pas le texte complet")
    for k, (j, q) in enumerate(zip(qj[45:], qs[45:]), start=46):
        if q["ok"] != reponses[k - 46]:
            erreurs.append(f"Q{k}: la bonne option {q['ok']!r} n'est pas la reponse du texte {reponses[k - 46]!r}")
    print("texte a trous rempli :", normaliser_phrase(rempli) == normaliser_phrase(C.COMPLET))

    # 4. originalite
    mes_textes = {"texte a trous": sans_entetes(C.TEXTE)}
    for n, j in enumerate(qj, start=1):
        mes_textes[f"Q{n}"] = sans_entetes(j["enonce_markdown"]) + "\n" + "\n".join(c["texte"] for c in j["choix"])
    gram = {k: ngrammes(v) for k, v in mes_textes.items()}
    sources = list(textes_reels())
    nb_communs = 0
    for source, texte in sources:
        g = ngrammes(texte)
        for k, gk in gram.items():
            commun = gk & g
            if commun:
                nb_communs += 1
                erreurs.append(f"originalite : {k} partage une suite de 6 mots avec {source} : {sorted(commun)[:2]}")
    print(f"originalite : {len(mes_textes)} textes compares a {len(sources)} sources ; suites communes : {nb_communs}")

    # 5. typographie
    tout = json.dumps(ep, ensure_ascii=False)
    if "\u2014" in tout:
        erreurs.append("tiret cadratin dans le contenu")
    if "\u2019" in tout:
        erreurs.append("apostrophe courbe : l'inedite n'emploie que l'apostrophe droite")
    for n, j in enumerate(qj, start=1):
        for champ in (j["enonce_markdown"], *[c["texte"] for c in j["choix"]]):
            plat = re.sub(r"\s*\n\s*", " ", champ)
            if "  " in plat or re.search(r" [,.]", plat):
                avert.append(f"Q{n}: espace a revoir dans {champ[:50]!r}")
    plus_longue = sum(1 for q in qs if len(q["ok"]) > max(len(b) for b in q["bad"]))
    print(f"la bonne option est la plus longue dans {plus_longue}/50 questions (viser moins de 40 %)")
    if plus_longue > 20:
        avert.append("biais de longueur : trop de bonnes options sont les plus longues")
    for e in erreurs:
        print("ERREUR", e)
    for w in avert:
        print("AVERT", w)
    print("OK : aucun ecart" if not erreurs else f"{len(erreurs)} ecart(s)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
