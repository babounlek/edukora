r"""Verifie le Paper 2 English Language inedit (ecriture dirigee + composition), SANS pouvoir recalculer une redaction :

    D:\edukora\venv\Scripts\python.exe scripts\gce\inedites\verifier_reponses_english_p2.py [ep-....json]

Controles mecaniques (sortie 1 au moindre ecart) :
  1. SECTION A : le modele respecte la consigne (DEUX paragraphes, au plus 150 mots) ; chacun de ses points est repris du texte (phrase du texte retrouvee mot pour mot)
     et aucun point hors sujet (consequences, fabrication du plastique) n'y figure ; texte dans la fourchette des vrais sujets (412-633 mots) ; bareme 14 + 12 + 4 = 30 ;
  2. SECTION B : sept sujets a-g, un modele par sujet de 440 a 510 mots (vrais modeles : 451-499), contraintes propres a chaque sujet (le recit finit par la phrase donnee,
     la lettre porte adresse, date, formule d'appel et de politesse, au moins 5 paragraphes...) ; bareme 12 + 16 + 12 = 40 ;
  3. SESSION : aucun nom, lieu ni mot-cle du Paper 1 ne reparait ;
  4. ORIGINALITE : aucune suite de 7 mots n'est commune a un texte, un sujet ou un modele de l'inedite et a un vrai sujet English O/L (Paper 1 ou 2) ni au Paper 1 inedit.
La relecture de la langue (grammaire, orthographe, ton) et du fond des modeles reste humaine : voir le compte rendu.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import questions_english_p1 as P1  # noqa: E402
import questions_english_p2 as C  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAUT = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm", "ep-cm-gce-ol-english-p2-1-2026-s1.json")
CORPUS = os.path.join(RACINE, "backend", "ingest", "cm")
NOMS_P1 = ["Tabe", "Ma'a", "Nkeng", "Wum", "Mbah", "Bafoussam", "kola", "groundnut", "plantain", "Ayuk", "Ebot", "Kumba", "Douala", "bus park"]
HORS_SUJET_A = ["flood", "malaria", "mosquito", "smoke", "polymer", "hydrocarbon", "tonnes"]
FORMULES_IA = [r"\bit is worth noting\b", r"\bit should be noted\b", r"\bnote that\b", r"\bdelve\b", r"\bin conclusion\b", r"\bfurthermore\b", r"\bmoreover\b",
               r"\bin summary\b", r"\bit is important to note\b"]


def mots(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def nb_mots(t):
    return len(re.findall(r"\S+", t))


def ngrammes(t, n=7):
    m = mots(t)
    return {" ".join(m[i:i + n]) for i in range(len(m) - n + 1)}


def textes_reels():
    for dossier in sorted(glob.glob(os.path.join(CORPUS, "gce-ol-english-*"))):
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
    erreurs, avert = [], []
    ex_a, ex_b = ep["exercices"]
    qa, qb = ex_a["questions"][0], ex_b["questions"][0]

    # 1. Section A
    paragraphes = [p for p in C.MODELE_A.split("\n\n") if p.strip()]
    n_modele = nb_mots(C.MODELE_A)
    print(f"section A : texte {nb_mots(C.PASSAGE_A)} mots (vrais : 412-633), modele {n_modele} mots en {len(paragraphes)} paragraphes (limite : 2 paragraphes, 150 mots)")
    if len(paragraphes) != 2:
        erreurs.append(f"le modele A doit avoir DEUX paragraphes ({len(paragraphes)})")
    if n_modele > C.LIMITE_A:
        erreurs.append(f"le modele A depasse {C.LIMITE_A} mots ({n_modele})")
    if not 412 <= nb_mots(C.PASSAGE_A) <= 633:
        erreurs.append("longueur du texte A hors de la fourchette des vrais sujets")
    for point, preuve in C.POINTS_A:
        if point.lower() not in C.MODELE_A.lower():
            erreurs.append(f"point absent du modele A : {point!r}")
        if preuve not in C.PASSAGE_A:
            erreurs.append(f"phrase du texte introuvable pour le point {point!r} : {preuve!r}")
    for mot in HORS_SUJET_A:
        if mot in C.MODELE_A.lower():
            erreurs.append(f"le modele A contient un point hors sujet : {mot!r}")
    print(f"  {len(C.POINTS_A)} points du modele retrouves dans le texte ; paragraphe a ecarter present : {'hydrocarbons' in C.PASSAGE_A.lower()}")
    if sum(p for _, p in C.CRITERES_A) != 30 or qa["points"] != 30:
        erreurs.append("bareme de la Section A different de 30")

    # 2. Section B
    lettres = [t["lettre"] for t in C.TOPICS]
    if lettres != list("abcdefg"):
        erreurs.append(f"les sujets doivent etre a-g : {lettres}")
    for t in C.TOPICS:
        modele = t["modele"].replace(chr(92) + chr(34), chr(34))
        n = nb_mots(modele)
        paras = len([p for p in modele.split("\n\n") if p.strip()])
        flag = "" if 451 <= n <= 499 else "  (hors des vrais modeles 451-499)"
        print(f"  sujet {t['lettre']}) : modele {n} mots, {paras} paragraphes{flag}")
        if not 440 <= n <= 510:
            erreurs.append(f"modele {t['lettre']}) de {n} mots hors de 440-510")
        if paras < 5:
            erreurs.append(f"modele {t['lettre']}) : moins de 5 paragraphes")
        if f"**{t['lettre']})**" not in qb["enonce_markdown"]:
            erreurs.append(f"sujet {t['lettre']}) absent de l'enonce")
        if f"**Model composition {t['lettre']}) (" not in qb["corrige_markdown"]:
            erreurs.append(f"modele {t['lettre']}) absent du corrige")
        if not 4 <= len(t["plan"]) <= 6:
            erreurs.append(f"plan du sujet {t['lettre']}) : 4 a 6 lignes attendues")
    modele_a = next(t for t in C.TOPICS if t["lettre"] == "a")["modele"]
    if not modele_a.rstrip().endswith("and I have never taken a shortcut since."):
        erreurs.append("le modele a) ne finit pas par la phrase donnee")
    modele_g = next(t for t in C.TOPICS if t["lettre"] == "g")["modele"]
    for attendu in ("P.O. Box 17", "Fundong", "Dear Nsame,", "Your loving cousin"):
        if attendu not in modele_g:
            erreurs.append(f"la lettre g) ne contient pas {attendu!r}")
    if sum(p for _, p in C.CRITERES_B) != 40 or qb["points"] != 40:
        erreurs.append("bareme de la Section B different de 40")
    if [e["numero_exercice"] for e in ep["exercices"]] != ["1", "B1"] or ex_a["groupes"] != ["SECTION A"] or ex_b["groupes"] != ["SECTION B"]:
        erreurs.append("structure des exercices inattendue")
    if "Choose ONE" not in qb["enonce_markdown"]:
        erreurs.append("la consigne « Choose ONE » manque a la Section B")

    # 3. aucune fuite depuis le Paper 1 de la session
    tout = json.dumps(ep, ensure_ascii=False)
    for nom in NOMS_P1:
        if re.search(r"\b" + re.escape(nom), tout, re.I):
            erreurs.append(f"fuite depuis le Paper 1 : {nom!r}")

    # 4. style et originalite
    for f in FORMULES_IA:
        if re.search(f, tout, re.I):
            erreurs.append(f"formule d'IA a proscrire : {f}")
    mes_textes = {"texte A": C.PASSAGE_A, "modele A": C.MODELE_A, "tache A": C.TACHE_A}
    for t in C.TOPICS:
        mes_textes[f"sujet {t['lettre']})"] = t["sujet"].replace(chr(92) + chr(34), chr(34))
        mes_textes[f"modele {t['lettre']})"] = t["modele"].replace(chr(92) + chr(34), chr(34))
    # Gabarit d'examen repris tel quel, pas du contenu : ligne de repartition des points, consigne « Write a story to illustrate the proverb », « your address is P.O. Box ».
    gabarit = (r"mark distribution:[^\n]*", r"write a story to illustrate the proverb", r"and your address is p\.?o\.? box",
               r"selecting relevant [a-z]+ from the passage below, write",
               r"write in two paragraphs of not more than[^.]*\.", r"paying attention to grammar, spelling, punctuation and handwriting")
    for k in list(mes_textes):
        for g in gabarit:
            mes_textes[k] = re.sub(g, " ", mes_textes[k], flags=re.I)
    gram = {k: ngrammes(v) for k, v in mes_textes.items()}
    p1 =P1.LISTENING + "\n" + P1.READING + "\n" + "\n".join(q["stem"] for q in P1.questions())
    sources = list(textes_reels()) + [("paper 1 inedit de la session", p1)]
    nb_communs = 0
    for source, texte in sources:
        g = ngrammes(texte)
        for k, gk in gram.items():
            commun = gk & g
            if commun:
                nb_communs += 1
                erreurs.append(f"originalite : {k} partage une suite de 7 mots avec {source} : {sorted(commun)[:2]}")
    print(f"originalite : {len(mes_textes)} textes compares a {len(sources)} sources ; suites communes : {nb_communs}")
    for e in erreurs:
        print("ERREUR", e)
    for w in avert:
        print("AVERT", w)
    print("OK : aucun ecart" if not erreurs else f"{len(erreurs)} ecart(s)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
