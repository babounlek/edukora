r"""Verifie le Paper 2 French inedit (traduction + redaction), SANS pouvoir corriger le francais lui-meme :

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_french_p2.py [ep-....json]

Controles mecaniques (sortie 1 au moindre ecart) :
  1. QUESTION 1 : le texte a traduire et la traduction modele ont le meme nombre de paragraphes ET de phrases (rien d'oublie) ; chaque ligne du tableau des pieges retrouve sa bonne forme
     mot pour mot dans la traduction modele ; bareme 12 + 10 + 10 + 8 = 40 ;
  2. QUESTION 2 : trois sujets a-c de trois points chacun ; chaque modele compte de 140 a 150 mots selon la regle du sujet (sans l'introduction de la lettre ni la signature, ni les noms
     propres) ; chaque point du sujet est couvert par un extrait du modele retrouve mot pour mot ; la lettre porte une introduction de 20 mots au plus, la signature Noela et l'adresse
     Collège de Foumban ; bareme 16 + 6 + 6 + 6 + 6 = 40 ;
  3. SESSION : aucun nom, lieu ni phrase du Paper 1 ne reparait ;
  4. ORIGINALITE : aucune suite de 6 mots n'est commune a un texte, un sujet ou un modele de l'inedite et a un vrai sujet French O/L (Paper 1 ou 2) ni au Paper 1 inedit (les consignes imprimees
     de l'examen sont ecartees) ; typographie (pas de tiret cadratin, apostrophes droites).
La correction du francais des modeles (temps, accords, orthographe, naturel) reste une RELECTURE HUMAINE : voir le compte rendu.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import generer_french_p2 as G  # noqa: E402
import questions_french_p1 as P1  # noqa: E402
import questions_french_p2 as C  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAUT = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-french-p2-1-2026-s1.json")
CORPUS = os.path.join(RACINE, "backend", "ingest", "cm")
NOMS_P1 = ["Ngoumou", "Limbe", "Bamenda", "Awa", "Marie", "Jacqueline", "Koume"]
GABARIT = (
    r"using a tense suitable to your chosen topic[^.]*\.", r"if you choose topic \(b\)[^.]*\.", r"the usual introduction to the letter[^.]*\.",
    r"credit will be given for[^.]*\.", r"off-topic material will earn no marks\.", r"answer both questions[^.]*\.", r"you are reminded of the necessity[^.]*\.",
    r"use of a different name[^.]*\.", r"translate into french", r"do not write on more than one topic\.",
)
FORMULES_IA = [r"\bit is worth noting\b", r"\bnote that\b", r"\bdelve\b", r"\bin conclusion\b", r"\bfurthermore\b", r"\bmoreover\b", r"\bin summary\b"]


def mots(t):
    return re.findall(r"[\wàâäçéèêëîïôöùûüÿœæ']+", t.lower())


def ngrammes(t, n=6):
    m = mots(t)
    return {" ".join(m[i:i + n]) for i in range(len(m) - n + 1)}


def phrases(t):
    return len([p for p in re.split(r"(?<=[.!?])\s+", re.sub(r"[>*]", "", t).strip()) if p.strip()])


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


def sans_gabarit(t):
    for g in GABARIT:
        t = re.sub(g, " ", t, flags=re.I)
    return t


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else DEFAUT
    ep = json.load(open(chemin, encoding="utf-8"))
    erreurs, avert = [], []
    ex1, ex2 = ep["exercices"]
    q1, q2 = ex1["questions"][0], ex2["questions"][0]

    # 1. Question 1
    source = C.ENONCE_Q1.split("\n\n", 1)[1]
    p_src = [p for p in source.split("\n\n") if p.strip()]
    p_mod = [p for p in C.MODELE_Q1.split("\n\n") if p.strip()]
    print(f"question 1 : source {len(p_src)} paragraphes / {phrases(source)} phrases, modele {len(p_mod)} paragraphes / {phrases(C.MODELE_Q1)} phrases")
    if len(p_src) != len(p_mod):
        erreurs.append(f"la traduction a {len(p_mod)} paragraphes pour {len(p_src)} dans le texte")
    for i, (a, b) in enumerate(zip(p_src, p_mod), start=1):
        if phrases(a) != phrases(b):
            erreurs.append(f"paragraphe {i} : {phrases(a)} phrases dans le texte, {phrases(b)} dans la traduction modele")
    for point, piege, ok, extrait in C.POINTS_Q1:
        if extrait not in C.MODELE_Q1:
            erreurs.append(f"le point {point} : la bonne forme {extrait!r} est absente de la traduction modele")
        if f"| {point} |" not in q1["corrige_markdown"]:
            erreurs.append(f"le point {point} est absent du tableau du corrige")
    print(f"  {len(C.POINTS_Q1)} points du tableau retrouves dans le modele")
    if sum(p for _, p in C.CRITERES_Q1) != 40 or q1["points"] != 40:
        erreurs.append("bareme de la Question 1 different de 40")

    # 2. Question 2
    lettres = [t["lettre"] for t in C.TOPICS]
    if lettres != ["a", "b", "c"]:
        erreurs.append(f"les sujets doivent etre a, b, c : {lettres}")
    for t in C.TOPICS:
        n = G.mots_comptes(t)
        print(f"  sujet {t['lettre']}) : {n} mots comptes (140-150)")
        if not 140 <= n <= 150:
            erreurs.append(f"modele {t['lettre']}) : {n} mots comptes hors de 140-150")
        if t["sujet"].count("\n- ") + t["sujet"].count("\n\n- ") < 3 and t["sujet"].count("- ") < 3:
            erreurs.append(f"sujet {t['lettre']}) : trois points attendus")
        if len(t["couverture"]) != 3:
            erreurs.append(f"sujet {t['lettre']}) : trois points a couvrir")
        for point, extrait in t["couverture"]:
            if extrait not in t["modele"]:
                erreurs.append(f"sujet {t['lettre']}) : le point « {point} » n'est pas couvert (extrait absent) : {extrait!r}")
        if f"**Model essay {t['lettre']})" not in q2["corrige_markdown"]:
            erreurs.append(f"modele {t['lettre']}) absent du corrige")
    lettre = next(t for t in C.TOPICS if t["lettre"] == "b")
    if len(mots(lettre["intro"])) > 20:
        erreurs.append(f"introduction de la lettre : {len(mots(lettre['intro']))} mots (20 au plus)")
    for attendu in ("Noela", "Collège de Foumban"):
        if not lettre["modele"].rstrip().endswith("Noela\nCollège de Foumban"):
            erreurs.append("la lettre doit se terminer par la signature Noela et l'adresse Collège de Foumban")
            break
    if "NOELA" not in q2["enonce_markdown"] or "Collège de Foumban" not in q2["enonce_markdown"]:
        erreurs.append("le nom et l'adresse imposes manquent a l'enonce")
    if "Choose ONE" not in C.INTRO_Q2 and "ONE of the following topics" not in C.INTRO_Q2:
        erreurs.append("la consigne de choix manque")
    if sum(p for _, p in C.CRITERES_Q2) != 40 or q2["points"] != 40:
        erreurs.append("bareme de la Question 2 different de 40")
    if [e["numero_exercice"] for e in ep["exercices"]] != ["1", "2"] or ex1["groupes"] != ["QUESTION 1"] or ex2["groupes"] != ["QUESTION 2"]:
        erreurs.append("structure des exercices inattendue")

    # 3. fuite depuis le Paper 1
    tout = json.dumps(ep, ensure_ascii=False)
    for nom in NOMS_P1:
        if re.search(r"\b" + re.escape(nom) + r"\b", tout):
            erreurs.append(f"fuite depuis le Paper 1 : {nom!r}")

    # 4. style et originalite
    if "\u2014" in tout:
        erreurs.append("tiret cadratin dans le contenu")
    if "\u2019" in tout:
        erreurs.append("apostrophe courbe : l'inedite n'emploie que l'apostrophe droite")
    for f in FORMULES_IA:
        if re.search(f, tout, re.I):
            erreurs.append(f"formule d'IA a proscrire : {f}")
    mes = {"consignes": sans_gabarit(C.CONSIGNES_GENERALES), "enonce Q1": sans_gabarit(C.ENONCE_Q1), "modele Q1": C.MODELE_Q1, "intro Q2": sans_gabarit(C.INTRO_Q2)}
    for t in C.TOPICS:
        mes[f"sujet {t['lettre']})"] = t["sujet"]
        mes[f"modele {t['lettre']})"] = t["modele"]
    gram = {k: ngrammes(v) for k, v in mes.items()}
    p1 = "\n".join(q["stem"] + " " + " ".join([q["ok"]] + q["bad"]) for q in P1.questions()) + "\n" + P1.COMPLET
    sources = list(textes_reels()) + [("paper 1 inedit de la session", p1)]
    nb = 0
    for source_nom, texte in sources:
        g = ngrammes(sans_gabarit(texte))
        for k, gk in gram.items():
            commun = gk & g
            if commun:
                nb += 1
                erreurs.append(f"originalite : {k} partage une suite de 6 mots avec {source_nom} : {sorted(commun)[:2]}")
    print(f"originalite : {len(mes)} textes compares a {len(sources)} sources ; suites communes : {nb}")
    for e in erreurs:
        print("ERREUR", e)
    for w in avert:
        print("AVERT", w)
    print("OK : aucun ecart" if not erreurs else f"{len(erreurs)} ecart(s)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
