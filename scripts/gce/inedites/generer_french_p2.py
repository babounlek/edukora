"""Genere le blueprint et l'epreuve inedite GCE O Level French Paper 2 n.1 (traduction et redaction).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_french_p2.py [dossier_de_sortie]

Structure des 8 vrais Paper 2 (2019-2026) : Question 1 de 40 points (traduction de l'anglais vers le francais) et Question 2 de 40 points (une redaction de 140 a 150 mots a choisir
parmi trois sujets). Les inedites ne codent pas les choix : la Question 2 est UNE question qui liste les sujets a, b, c et dit « choose ONE », avec un modele pour CHAQUE sujet ;
le sujet c a images des vrais sujets est remplace par un sujet guide sans images. Total 80 points, 120 minutes.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import questions_french_p2 as C  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-french-p2-1"
EP_ID = "ep-cm-gce-ol-french-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-french-p1-1"
TITRE = "French GCE O Level Paper 2 \u2013 Original Paper No. 1"


def mots(t):
    return len(re.findall(r"\S+", t))


def mots_comptes(topic):
    """Mots comptes selon la regle du sujet : sans l'introduction de la lettre, sans la signature (nom et adresse) ni les noms propres."""
    texte = topic["modele"]
    if topic["intro"]:
        texte = texte.replace(topic["intro"], " ", 1)
    lignes = [l for l in texte.split("\n") if l.strip()]
    if topic["lettre"] == "b":
        lignes = [l for l in lignes if l.strip() not in ("Noela", "Collège de Foumban")]
    texte = " ".join(lignes)
    for nom in topic["noms"]:
        texte = re.sub(r"\b" + re.escape(nom) + r"\b", " ", texte)
    return mots(texte)


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_french_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def question_1(cours):
    lignes = "\n".join(f"| {p} | {pi} | {ok} |" for p, pi, ok, _ in C.POINTS_Q1)
    corrige = (
        f"### Rappel de m\u00e9thode\n{C.RAPPEL_Q1}\n\n"
        f"**Model translation**\n\n{C.MODELE_Q1}\n\n"
        f"**Translation points**\n\n| Point | Trap | Correct form |\n|---|---|---|\n{lignes}\n\n{C.NOTE_Q1}\n\n"
        f"### Pi\u00e8ge \u00e0 \u00e9viter\n{C.PIEGE_Q1.replace(chr(92) + chr(34), chr(34))}\n\n### Conseil\n{C.CONSEIL_Q1}"
    )
    return {
        "numero": "1", "ordre": 1, "enonce_markdown": C.ENONCE_Q1, "corrige_markdown": corrige,
        "difficulte_estimee": "moyenne", "type_reponse": "ouverte", "points": 40,
        "criteres_notation": [{"libelle": l, "points": p} for l, p in C.CRITERES_Q1],
        "themes": [C.PREFIXE + "translation into French"],
        "rappels_de_methode": [{
            "id": f"rdi-{EP_ID}-ex1-q1-0", "competence": cours["translation into French"], "contenu_markdown": C.RAPPEL_Q1, "cours_genere": False, "cours_id": None,
        }],
    }


def question_2(cours):
    sujets = "\n\n".join(t["sujet"] for t in C.TOPICS)
    enonce = C.INTRO_Q2 + sujets
    blocs = ["**Choose ONE topic. A model essay is given for every topic: read only the one that matches the topic you chose.**"]
    for t in C.TOPICS:
        blocs.append(
            f"**Topic {t['lettre']}) - Tense chosen:** {t['temps']}\n\n**Model essay {t['lettre']}) ({mots_comptes(t)} words counted with the rule of the paper)**\n\n{t['modele']}"
        )
    corrige = (
        f"### Rappel de m\u00e9thode\n{C.RAPPEL_Q2}\n\n" + "\n\n".join(blocs) + f"\n\n{C.GRILLE_Q2}\n\n"
        f"### Pi\u00e8ge \u00e0 \u00e9viter\n{C.PIEGE_Q2}\n\n### Conseil\n{C.CONSEIL_Q2}"
    )
    themes = [C.PREFIXE + t for t in ("narrative essay", "letter writing", "picture story")]
    return {
        "numero": "1", "ordre": 1, "enonce_markdown": enonce, "corrige_markdown": corrige,
        "difficulte_estimee": "moyenne", "type_reponse": "ouverte", "points": 40,
        "criteres_notation": [{"libelle": l, "points": p} for l, p in C.CRITERES_Q2],
        "themes": themes,
        "rappels_de_methode": [{
            "id": f"rdi-{EP_ID}-ex2-q1-0", "competence": cours["narrative essay"], "contenu_markdown": C.RAPPEL_Q2, "cours_genere": False, "cours_id": None,
        }],
    }


def construire():
    cours = titres_cours()
    q1, q2 = question_1(cours), question_2(cours)
    assert sum(c["points"] for c in q1["criteres_notation"]) == 40 and sum(c["points"] for c in q2["criteres_notation"]) == 40
    competences = q1["themes"] + q2["themes"]
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "French",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [
            {
                "exercice": "1", "titre": "Question 1 - Translation into French", "points": 40, "difficulte": "moyenne", "nombre_questions": 1,
                "competences": q1["themes"], "groupes": ["QUESTION 1"],
                "format": "un texte anglais de quatre paragraphes (environ 130 mots) a traduire en francais ; bareme 40 points sur le sens complet, les temps, les accords et le naturel",
                "ordre": "Question 1 d'abord, comme les 8 vrais Paper 2 (2019-2026)",
                "corrige": "traduction modele, tableau des pieges (forme fautive, forme correcte), note de notation, erreurs courantes",
                "repartition_difficulte": {"faible": 0, "moyenne": 1, "elevee": 0}, "figures_prevues": 0,
            },
            {
                "exercice": "2", "titre": "Question 2 - Composition", "points": 40, "difficulte": "moyenne", "nombre_questions": 1,
                "competences": q2["themes"], "groupes": ["QUESTION 2"],
                "format": "une redaction de 140 a 150 mots a choisir parmi trois sujets : (a) recit guide en trois points, (b) lettre avec nom NOELA et adresse Collège de Foumban imposes, "
                          "(c) description guidee en trois points ; bareme 40 points (exactitude 16, expressions 6, verbes 6, vocabulaire et idiomes 6, pertinence et longueur 6)",
                "regle_reelle": "dans les vrais sujets : trois sujets a, b, c dont le sujet c est fonde sur des images, UN SEUL a traiter ; ici la regle est dite dans l'enonce (« choose ONE ») car "
                                "la plateforme ne code pas les choix des inedites ; le sujet c a images est remplace par un sujet guide sans images",
                "corrige": "un modele de 140 a 150 mots (regle de comptage du sujet) pour CHAQUE sujet, le temps choisi, la grille, les erreurs courantes",
                "repartition_difficulte": {"faible": 0, "moyenne": 1, "elevee": 0}, "figures_prevues": 0,
            },
        ],
        "duree_minutes": 120, "bareme_total": 80,
        "session": {"papier_jumeau": BP_P1, "numero_session": 1,
                    "regle": "aucun texte, nom, lieu ni phrase partages entre les deux papers de la session (Ngoumou, Limbe, Bamenda, Awa, Marie et les phrases du Paper 1 ne reparaissent pas ici)"},
    }
    epreuve = {
        "type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
        "exercices": [
            {"numero_exercice": "1", "points": "40", "groupes": ["QUESTION 1"], "enonce_intro_markdown": C.CONSIGNES_GENERALES, "questions": [q1]},
            {"numero_exercice": "2", "points": "40", "groupes": ["QUESTION 2"], "enonce_intro_markdown": "", "questions": [q2]},
        ],
    }
    return blueprint, epreuve


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else SORTIE
    os.makedirs(sortie, exist_ok=True)
    bp, ep = construire()
    for nom, obj in ((BP_ID, bp), (EP_ID, ep)):
        chemin = os.path.join(sortie, nom + ".json")
        with open(chemin, "w", encoding="utf8", newline="\n") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("ecrit", chemin)
    print("traduction : source", mots(re.sub(r"[>*]", "", C.ENONCE_Q1.split("\n\n", 1)[1])), "mots, modele", mots(C.MODELE_Q1), "mots ; redactions (mots comptes) :",
          {t["lettre"]: mots_comptes(t) for t in C.TOPICS})


if __name__ == "__main__":
    main()
