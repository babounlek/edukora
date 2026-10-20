r"""Verifie les 50 QCM du Paper 1 English Language inedit, SANS pouvoir les recalculer (une langue ne se recalcule pas) :

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_english_p1.py [ep-....json]

Controles mecaniques (sortie 1 au moindre ecart) :
  1. la cle est l'option qui porte exactement le texte de la bonne reponse, et elle est la seule ; options distinctes ;
  2. ECOUTE et LECTURE : la phrase `preuve` de chaque question se retrouve MOT POUR MOT dans le texte qu'elle commente (la cle s'appuie sur le texte) ;
  3. GRAMMAIRE et VOCABULAIRE a trou : l'enonce rempli avec la bonne option contient la phrase complete ecrite a part ;
  4. ORIGINALITE : aucune suite de 7 mots (textes compris) n'est commune a un texte ou a un enonce de l'inedite et a un vrai sujet English O/L du corpus ;
  5. longueur des textes dans la fourchette des vrais sujets, biais de longueur de la bonne option, mots de remplissage interdits (« all of the above »...).
La relecture du second passage (« existe-t-il une deuxieme option acceptable ? ») reste humaine : voir le compte rendu.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_english_p1 import LISTENING, READING, questions  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAUT = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-english-p1-1-2026-s1.json")
CORPUS = os.path.join(RACINE, "backend", "ingest", "cm")
BLANC = "\\_\\_\\_\\_\\_\\_"
ENTETES = ("**Section C", "**Section D", "**For questions", "**Questions", "**Listening passage", "**Read the passage")


def mots(t):
    return re.findall(r"[a-z0-9']+", t.lower().replace("\\_", " "))


def ngrammes(t, n):
    m = mots(t)
    return {" ".join(m[i:i + n]) for i in range(len(m) - n + 1)}


FORMULES = (r"\(passage for questions 11 to 25[^)]*\)", r"\(listening passage in question 1[^)]*\)", r"is used as a/?an\b")


def sans_entetes(t):
    """Enonce sans les etiquettes de format (« (Passage for questions 11 to 25) », en-tetes de section) et sans la formule imprimee
    « is used as a/an » : le gabarit du sujet, repris tel quel, n'est pas du contenu."""
    t = "\n\n".join(p for p in t.split("\n\n") if not p.startswith(ENTETES))
    for f in FORMULES:
        t = re.sub(f, " ", t, flags=re.I)
    return t


def textes_reels():
    """(source, texte) pour chaque fichier d'un vrai paper English O/L : enonces, options, introductions."""
    for dossier in sorted(glob.glob(os.path.join(CORPUS, "gce-ol-english-*"))):
        for f in glob.glob(os.path.join(dossier, "*.json")):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except ValueError:
                continue
            morceaux = [d.get("introduction_markdown") or "", d.get("enonce_intro_markdown") or ""]
            for q in d.get("questions", []):
                morceaux.append(q.get("enonce_markdown") or "")
                morceaux += [c.get("texte", "") for c in q.get("choix") or []]
            yield os.path.basename(dossier), "\n".join(morceaux)


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf-8"))
    qj = ep["exercices"][0]["questions"]
    qs = questions()
    erreurs, avert = [], []
    assert len(qj) == len(qs) == 50

    # 1. cle unique et options distinctes
    for n, (j, q) in enumerate(zip(qj, qs), start=1):
        textes = {c["lettre"]: c["texte"] for c in j["choix"]}
        egaux = [l for l, t in textes.items() if t == q["ok"]]
        if egaux != [j["reponse_correcte"]]:
            erreurs.append(f"Q{n}: cle {j['reponse_correcte']} mais la bonne option est en {egaux}")
        if len({t.strip().lower() for t in textes.values()}) != 4:
            erreurs.append(f"Q{n}: options en double")
        for t in textes.values():
            if re.search(r"\b(all|none) of the above\b", t, re.I):
                erreurs.append(f"Q{n}: option « all/none of the above » interdite")

    # 2. preuve verbatim dans le texte commente
    for n, q in enumerate(qs, start=1):
        if not q["preuve"]:
            continue
        texte = LISTENING if n <= 10 else READING
        if n > 25:
            erreurs.append(f"Q{n}: une preuve n'a pas de sens hors texte")
            continue
        if q["preuve"] not in texte:
            erreurs.append(f"Q{n}: la preuve n'est pas dans le texte : {q['preuve']!r}")
    sans_preuve = [n for n, q in enumerate(qs, start=1) if n <= 25 and not q["preuve"]]
    print("questions de texte sans phrase preuve (jugement d'ensemble, relues a la main) :", sans_preuve)

    # 3. phrase complete a trou
    n_trous = 0
    for n, (j, q) in enumerate(zip(qj, qs), start=1):
        if n <= 25 or not q["complete"]:
            continue
        dernier = j["enonce_markdown"].split("\n\n")[-1]
        if BLANC not in dernier:
            erreurs.append(f"Q{n}: pas de trou dans le dernier paragraphe")
            continue
        rempli = dernier.replace(BLANC, " " + q["ok"] + " ") if not re.search(r"\w" + re.escape(BLANC), dernier) else dernier.replace(BLANC, q["ok"])
        rempli = re.sub(r"\s+", " ", rempli).replace(" ,", ",").replace(" .", ".").replace(" ?", "?").strip()
        if q["complete"] not in rempli.replace("\\\"", '"'):
            erreurs.append(f"Q{n}: enonce rempli {rempli!r} different de la phrase complete {q['complete']!r}")
        n_trous += 1
    print("phrases completes confrontees a l'enonce rempli :", n_trous)

    # 4. originalite : suites de mots communes avec les vrais sujets
    mes_textes = {
        "texte d'ecoute": (LISTENING, 7),
        "texte de lecture": (READING, 7),
    }
    for n, j in enumerate(qj, start=1):
        if n in (1, 11):
            continue
        mes_textes[f"Q{n} (enonce et options)"] = (sans_entetes(j["enonce_markdown"]) + "\n" + "\n".join(c["texte"] for c in j["choix"]), 7)
    gram5 = {k: ngrammes(v[0], 5) for k, v in mes_textes.items() if v[1] == 5}
    gram7 = {k: ngrammes(v[0], 7) for k, v in mes_textes.items() if v[1] == 7}
    communs = {}
    for source, texte in textes_reels():
        g5, g7 = ngrammes(texte, 5), ngrammes(texte, 7)
        for k, g in gram5.items():
            if g & g5:
                communs.setdefault(k, []).append((source, sorted(g & g5)[:2]))
        for k, g in gram7.items():
            if g & g7:
                communs.setdefault(k, []).append((source, sorted(g & g7)[:2]))
    for k, hits in communs.items():
        for source, ex in hits[:3]:
            erreurs.append(f"originalite : {k} partage une suite de mots avec {source} : {ex}")
    print("textes et questions comparees :", len(mes_textes), "; suites communes avec un vrai sujet :", len(communs))

    # 5. gabarit
    mots_ecoute, mots_lecture = len(mots(LISTENING)), len(mots(READING))
    print(f"texte d'ecoute : {mots_ecoute} mots (vrais sujets : 404-598) ; texte de lecture : {mots_lecture} mots (vrais sujets, avec questions : 455-905)")
    if not 380 <= mots_ecoute <= 620:
        erreurs.append("longueur du texte d'ecoute hors de la fourchette des vrais sujets")
    if not 450 <= mots_lecture <= 900:
        avert.append("longueur du texte de lecture hors de la fourchette des vrais sujets")
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
