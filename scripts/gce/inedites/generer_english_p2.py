"""Genere le blueprint et l'epreuve inedite GCE O Level English Language Paper 2 n.1 (ecriture dirigee et composition).

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\generer_english_p2.py [dossier_de_sortie]

Structure des 8 vrais Paper 2 (2019-2026) : Section A = ecriture dirigee de 30 points sur un texte ; Section B = une composition de 40 points a choisir parmi 8 sujets.
Les inedites ne codent pas les regles de choix : la Section B est UNE question de 40 points qui liste sept sujets (a-g, le sujet h a partir d'images est omis) et
dit « choose ONE », avec un plan et un modele de composition pour CHAQUE sujet. Total 70 points, 120 minutes.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import questions_english_p2 as C  # noqa: E402

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SORTIE = os.path.join(RACINE, "backend", "ingest", "_inedit", "cm")
BP_ID = "bp-cm-gce-ol-english-p2-1"
EP_ID = "ep-cm-gce-ol-english-p2-1-2026-s1"
BP_P1 = "bp-cm-gce-ol-english-p1-1"
TITRE = "English Language GCE O Level Paper 2 \u2013 Original Paper No. 1"


def mots(t):
    return len(re.findall(r"\S+", t))


def titres_cours():
    with open(os.path.join(os.path.dirname(__file__), "cours_titres_gce_english_ol.json"), encoding="utf8") as fh:
        return json.load(fh)


def competence(theme, cours):
    return cours.get(theme, theme.capitalize())


def question_a(cours):
    rappel_comp = competence("directed writing", cours)
    corrige = (
        f"### Rappel de m\u00e9thode\n{C.RAPPEL_A}\n\n"
        f"**Model answer (two paragraphs, {mots(C.MODELE_A)} words)**\n\n{C.MODELE_A}\n\n{C.POURQUOI_A}\n\n{C.GRILLE_A}\n\n"
        f"### Pi\u00e8ge \u00e0 \u00e9viter\n{C.PIEGE_A}\n\n### Conseil\n{C.CONSEIL_A}"
    )
    return {
        "numero": "1", "ordre": 1, "enonce_markdown": C.TACHE_A + "\n\n" + C.PASSAGE_A, "corrige_markdown": corrige,
        "difficulte_estimee": "moyenne", "type_reponse": "ouverte", "points": 30,
        "criteres_notation": [{"libelle": l, "points": p} for l, p in C.CRITERES_A],
        "themes": [C.PREFIXE + "directed writing"],
        "rappels_de_methode": [{
            "id": f"rdi-{EP_ID}-ex1-q1-0", "competence": rappel_comp, "contenu_markdown": C.RAPPEL_A, "cours_genere": False, "cours_id": None,
        }],
    }


def question_b(cours):
    sujets = "\n\n".join(f"**{t['lettre']})** {t['sujet'].replace(chr(92) + chr(34), chr(34))}" for t in C.TOPICS)
    enonce = C.PLAN_ENONCE_B + sujets
    morceaux = [
        "**Choose ONE topic. A plan and a model composition are given for every topic: read only the one that matches the topic you chose.**"
    ]
    for t in C.TOPICS:
        plan = "\n".join(f"{i}. {ligne}" for i, ligne in enumerate(t["plan"], start=1))
        modele = t["modele"].replace(chr(92) + chr(34), chr(34))
        morceaux.append(f"**Topic {t['lettre']}) - Plan**\n\n{plan}\n\n**Model composition {t['lettre']}) ({mots(modele)} words)**\n\n{modele}")
    pieges = " ".join(t["piege"] for t in C.TOPICS)
    corrige = (
        f"### Rappel de m\u00e9thode\n{C.RAPPEL_B}\n\n" + "\n\n".join(morceaux) + f"\n\n{C.GRILLE_B}\n\n"
        f"### Pi\u00e8ge \u00e0 \u00e9viter\n{C.PIEGE_B_GENERAL} {pieges}\n\n### Conseil\n{C.CONSEIL_B}"
    )
    themes = [C.PREFIXE + t for t in ("narrative composition", "descriptive composition", "argumentative composition", "informal letter")]
    return {
        "numero": "1", "ordre": 1, "enonce_markdown": enonce, "corrige_markdown": corrige,
        "difficulte_estimee": "moyenne", "type_reponse": "ouverte", "points": 40,
        "criteres_notation": [{"libelle": l, "points": p} for l, p in C.CRITERES_B],
        "themes": themes,
        "rappels_de_methode": [{
            "id": f"rdi-{EP_ID}-exB1-q1-0", "competence": competence("narrative composition", cours), "contenu_markdown": C.RAPPEL_B,
            "cours_genere": False, "cours_id": None,
        }],
    }


def construire():
    cours = titres_cours()
    qa, qb = question_a(cours), question_b(cours)
    assert sum(c["points"] for c in qa["criteres_notation"]) == qa["points"] == 30
    assert sum(c["points"] for c in qb["criteres_notation"]) == qb["points"] == 40
    competences = qa["themes"] + [t for t in qb["themes"] if t not in qa["themes"]]
    blueprint = {
        "type": "blueprint", "external_id": BP_ID, "titre": TITRE, "matiere": "English Language",
        "cursus": [{"examen": "gce_ol", "serie": ""}], "competences": competences,
        "sections_plan": [
            {
                "exercice": "1", "titre": "Section A - Directed writing", "points": 30, "difficulte": "moyenne", "nombre_questions": 1,
                "competences": qa["themes"], "groupes": ["SECTION A"],
                "format": "une consigne de role et de destinataire, un texte d'environ 480 mots (6 paragraphes dont un a ecarter), une reponse en DEUX paragraphes d'au plus 150 mots, "
                          "orientee pour convaincre ; bareme reel 14 (contenu) + 12 (expression et correction) + 4 (orientation persuasive)",
                "ordre": "Section A d'abord, comme les 8 vrais Paper 2 (2019-2026)",
                "corrige": "modele de 127-148 mots, pourquoi il fonctionne (selection et orientation), grille de notation, erreurs courantes",
                "repartition_difficulte": {"faible": 0, "moyenne": 1, "elevee": 0}, "figures_prevues": 0,
            },
            {
                "exercice": "B1", "titre": "Section B - Composition", "points": 40, "difficulte": "moyenne", "nombre_questions": 1,
                "competences": qb["themes"], "groupes": ["SECTION B"],
                "format": "une composition de 40 points (12 contenu et organisation, 16 expression, 12 correction) a choisir parmi sept sujets a-g : recit termine par une phrase donnee, "
                          "description, sujet en un mot, discussion « do you agree? », recit illustrant un proverbe, expose sur un probleme et ses solutions, lettre informelle",
                "regle_reelle": "dans le vrai sujet : 8 sujets a-h dont un a partir d'images, UN SEUL a traiter ; ici la regle est dite dans l'enonce (« choose ONE ») car la plateforme "
                                "ne code pas les choix des inedites ; le sujet h (images) est omis",
                "corrige": "un plan et un modele de composition de 450 a 500 mots pour CHAQUE sujet (longueur des modeles reels : 451-499 mots), grille, erreurs courantes",
                "repartition_difficulte": {"faible": 0, "moyenne": 1, "elevee": 0}, "figures_prevues": 0,
            },
        ],
        "duree_minutes": 120, "bareme_total": 70,
        "session": {"papier_jumeau": BP_P1, "numero_session": 1,
                    "regle": "aucun texte, personnage, lieu ni sujet partages entre les deux papers de la session : aucun nom, mot-cle ni phrase du Paper 1 (Tabe, Ma'a, Pa Nkeng, Wum, Bafoussam, kola, groundnuts) ne reparait ici"},
    }
    epreuve = {
        "type": "epreuve", "external_id": EP_ID, "titre": TITRE, "blueprint_external_id": BP_ID,
        "exercices": [
            {"numero_exercice": "1", "points": "30", "groupes": ["SECTION A"], "enonce_intro_markdown": C.CONSIGNES_GENERALES, "questions": [qa]},
            {"numero_exercice": "B1", "points": "40", "groupes": ["SECTION B"], "enonce_intro_markdown": "", "questions": [qb]},
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
    print("modele A :", mots(C.MODELE_A), "mots ; texte A :", mots(C.PASSAGE_A), "mots ; modeles B :",
          {t["lettre"]: mots(t["modele"].replace(chr(92) + chr(34), chr(34))) for t in C.TOPICS})


if __name__ == "__main__":
    main()
