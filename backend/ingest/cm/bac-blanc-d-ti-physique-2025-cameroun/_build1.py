# -*- coding: utf-8 -*-
import json, os

OUTDIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-blanc-d-ti-physique-2025-cameroun"
EPREUVE_SOURCE = "bac-blanc-d-ti-physique-2025-cameroun.pdf"
EPREUVE_SLUG = "bac-blanc-d-ti-physique-2025-cameroun"
EPREUVE_ID = "bac-blanc-d-ti-physique-2025-cameroun"
EPREUVE_TITRE = "Baccalaureat blanc D et TI - Physique - Session 2025 (DRES-NORD, evaluations harmonisees regionales)"

def build_question(numero, enonce_markdown, themes, difficulte, rappel_competence,
                    rappel_text, corps_text, piege_text=None, conseil_text=None,
                    type_reponse="ouverte", choix=None, reponse_correcte=None,
                    rappel_id_suffix="0", exercice_numero="1"):
    parts = ["### Rappel de méthode", rappel_text.strip(), "", "### Corrigé", corps_text.strip()]
    if piege_text:
        parts += ["", "### Piège à éviter", piege_text.strip()]
    if conseil_text:
        parts += ["", "### Conseil", conseil_text.strip()]
    corrige_markdown = "\n".join(parts)

    rappel_id = f"rdm-{EPREUVE_SLUG}-ex{exercice_numero}-q{numero}-{rappel_id_suffix}"
    rappel_obj = {
        "id": rappel_id,
        "competence": rappel_competence,
        "contenu_markdown": rappel_text.strip(),
        "cours_genere": True,
        "cours_id": None  # filled later
    }
    q = {
        "numero": numero,
        "enonce_markdown": enonce_markdown.strip(),
        "corrige_markdown": corrige_markdown,
        "themes": themes,
        "difficulte_estimee": difficulte,
        "type_reponse": type_reponse,
        "choix": choix if choix is not None else [],
        "reponse_correcte": reponse_correcte if reponse_correcte is not None else "",
        "rappels_de_methode": [rappel_obj]
    }
    return q

print("Module de construction charge.")
