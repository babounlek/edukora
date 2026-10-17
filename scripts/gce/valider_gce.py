"""
Validateur autonome des JSON d'un sujet du GCE avant ingestion (aucune dépendance à Django ni à la base).

Usage :
    D:\\edukora\\venv\\Scripts\\python.exe valider_gce.py <dossier> [--questions N] [--paper 1|2] [--code 0570] [--examen gce_ol|gce_al]

`<dossier>` contient un JSON par exercice (+ les PNG des figures). Code de sortie 0 = aucun défaut bloquant ;
les AVERTISSEMENTS (lignes « warn ») ne bloquent pas mais sont à relire. Reprend les mêmes exigences que
catalog.ingestion (clés obligatoires, QCM cohérents, figures présentes, regles_choix valides) et ajoute des
contrôles de forme propres à ce lot (anglais, pas de tiret cadratin, dollars appariés).
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

# scripts/gce/valider_gce.py -> racine du dépôt (le module choix.py vit dans backend/catalog).
RACINE = Path(__file__).resolve().parents[2] / "backend"


def _charger_choix():
    spec = importlib.util.spec_from_file_location("choix", RACINE / "catalog" / "choix.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.valider_regles_choix


def _charger_referentiel():
    """
    (libellé minuscule -> code GCE_*, code GCE_* -> {niveau: code du Board}) lus dans le code de la plateforme
    (catalog/ingestion.py : MATIERE_MAP ; catalog/models.py : CODES_OFFICIELS_GCE) SANS les importer (pas de Django).
    Une seule source de vérité : un nouveau libellé ou un nouveau code n'exige aucune modification ici.
    """
    import ast

    libelles, codes = {}, {}
    arbre = ast.parse((RACINE / "catalog" / "ingestion.py").read_text(encoding="utf-8"))
    for noeud in ast.walk(arbre):
        if (isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute) and noeud.func.attr == "update"
                and isinstance(noeud.func.value, ast.Name) and noeud.func.value.id == "MATIERE_MAP" and noeud.args):
            libelles.update({k: v for k, v in ast.literal_eval(noeud.args[0]).items() if v.startswith("GCE_")})
    arbre = ast.parse((RACINE / "catalog" / "models.py").read_text(encoding="utf-8"))
    for noeud in arbre.body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, "id", "") == "CODES_OFFICIELS_GCE" for c in noeud.targets):
            codes = ast.literal_eval(noeud.value)
    return libelles, codes


def verifier_matiere_et_code(data, examen):
    """Message d'erreur si matiere / examen / code_matiere ne forment pas une matière officielle du GCE Board, sinon None."""
    libelles, codes = _charger_referentiel()
    matiere = re.sub(r"\s+", " ", str(data.get("matiere") or "")).strip().lower()
    code_gce = libelles.get(matiere)
    if code_gce is None:
        indice = ""
        if matiere in ("pure mathematics", "pure maths"):
            indice = " (« Pure Mathematics » seul n'existe pas : écrire « Pure Mathematics with Mechanics » 0765 ou « ... with Statistics » 0770)"
        return f"matiere {data.get('matiere')!r} inconnue de la plateforme{indice}"
    niveaux = codes.get(code_gce, {})
    niveau = "GCE_OL" if examen == "gce_ol" else "GCE_AL"
    if niveau not in niveaux:
        return f"{data.get('matiere')!r} n'est pas offerte à ce niveau par le Board (niveaux : {sorted(niveaux) or 'aucun'})"
    if data.get("code_matiere") != niveaux[niveau]:
        return f"code_matiere attendu {niveaux[niveau]!r} pour {data.get('matiere')!r} ({niveau}), reçu {data.get('code_matiere')!r}"
    return None


CLES_OBLIGATOIRES = ["pays", "matiere", "examen", "annee", "duree_epreuve", "epreuve_source", "numero_exercice",
                     "numero_paper", "code_matiere", "questions"]
PLACEHOLDER = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
# « $$ ... \tag{n}$$ » sur UNE ligne : remark-math la lit comme formule en ligne et KaTeX refuse \tag (tunnel en échec).
# Backslash construit par chr(92) : un script écrit par un outil peut altérer « \\ ».
TAG_UNE_LIGNE = re.compile("^[$][$][^" + chr(10) + "]*" + re.escape(chr(92)) + "tag[^" + chr(10) + "]*[$][$][ ]*$", re.M)


def dollars_desequilibres(texte):
    sans_echappes = texte.replace("\\$", "")
    return sans_echappes.count("$") % 2 == 1


def valider(dossier, attendu_questions, paper, code, examen="gce_ol"):
    erreurs, avertissements = [], []
    valider_regles = _charger_choix()
    fichiers = sorted(p for p in dossier.glob("*.json"))
    if not fichiers:
        return [f"aucun JSON dans {dossier}"], []

    numeros_vus, total_questions, toutes_numeros = set(), 0, []
    for fichier in fichiers:
        nom = fichier.name
        try:
            data = json.loads(fichier.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            erreurs.append(f"{nom}: JSON illisible ({e})")
            continue
        for cle in CLES_OBLIGATOIRES:
            if data.get(cle) in (None, "", []):
                erreurs.append(f"{nom}: clé obligatoire manquante ou vide : {cle}")
        if data.get("examen") != examen:
            erreurs.append(f"{nom}: examen doit valoir « {examen} » (reçu {data.get('examen')!r})")
        if data.get("pays") != "cm":
            erreurs.append(f"{nom}: pays doit valoir « cm »")
        if data.get("epreuve_source") != dossier.name + ".pdf":
            erreurs.append(f"{nom}: epreuve_source doit valoir {dossier.name + '.pdf'!r} (reçu {data.get('epreuve_source')!r})")
        if paper and data.get("numero_paper") != paper:
            erreurs.append(f"{nom}: numero_paper attendu {paper}, reçu {data.get('numero_paper')!r}")
        if code and data.get("code_matiere") != code:
            erreurs.append(f"{nom}: code_matiere attendu {code!r}, reçu {data.get('code_matiere')!r}")
        incoherence = verifier_matiere_et_code(data, examen)
        if incoherence:
            erreurs.append(f"{nom}: {incoherence}")
        if not fichier.stem.startswith(dossier.name + "_exercice_"):
            avertissements.append(f"{nom}: nom conseillé {dossier.name}_exercice_<numero>.json")
        numero = str(data.get("numero_exercice"))
        if numero in numeros_vus:
            erreurs.append(f"{nom}: numero_exercice {numero!r} déjà utilisé par un autre fichier")
        numeros_vus.add(numero)

        try:
            valider_regles(data.get("regles_choix"))
        except ValueError as e:
            erreurs.append(f"{nom}: regles_choix invalide : {e}")

        figures = [f for f in (data.get("figures") or []) if isinstance(f, dict)]
        fichiers_figures = {f.get("fichier") for f in figures}
        for f in figures:
            if not f.get("fichier"):
                erreurs.append(f"{nom}: figure sans « fichier »")
            elif not (dossier / f["fichier"]).is_file():
                erreurs.append(f"{nom}: figure introuvable : {f['fichier']}")
        references = set()

        def verifier_texte(etiquette, texte):
            if not isinstance(texte, str):
                return
            if "\u2014" in texte or "\u2013" in texte:
                avertissements.append(f"{nom} {etiquette}: tiret cadratin/demi-cadratin (retiré à l'ingestion, préférer « - »)")
            if dollars_desequilibres(texte):
                erreurs.append(f"{nom} {etiquette}: nombre impair de $ (formule non fermée)")
            if TAG_UNE_LIGNE.search(texte):
                erreurs.append(f"{nom} {etiquette}: équation numérotée (tag) sur une seule ligne : l'écrire sur trois lignes ($$, la formule, $$)")
            for ref in PLACEHOLDER.findall(texte):
                references.add(ref)
                if not (dossier / ref).is_file():
                    erreurs.append(f"{nom} {etiquette}: image référencée introuvable : {ref}")
            if re.search(r"[À-ÿ]{1}", texte) and re.search(r"\b(le|la|les|des|est|une|pour)\b", texte) and not re.search(r"\b(the|is|of|and|to)\b", texte):
                avertissements.append(f"{nom} {etiquette}: texte qui semble en français (le lot est en anglais)")

        verifier_texte("enonce_intro_markdown", data.get("enonce_intro_markdown"))
        verifier_texte("introduction_markdown", data.get("introduction_markdown"))
        questions = data.get("questions") or []
        vus_q = set()
        for i, q in enumerate(questions, start=1):
            etiquette = f"q#{q.get('numero', i)}"
            for cle in ("numero", "enonce_markdown", "corrige_markdown"):
                if not q.get(cle):
                    erreurs.append(f"{nom} {etiquette}: « {cle} » manquant")
            if str(q.get("numero")) in vus_q:
                erreurs.append(f"{nom} {etiquette}: numéro de question dupliqué")
            vus_q.add(str(q.get("numero")))
            toutes_numeros.append(str(q.get("numero")))
            if not q.get("themes") or not all(isinstance(t, str) and t.strip() for t in q["themes"]):
                erreurs.append(f"{nom} {etiquette}: « themes » doit être une liste non vide de textes")
            verifier_texte(etiquette + " enonce", q.get("enonce_markdown"))
            verifier_texte(etiquette + " corrige", q.get("corrige_markdown"))
            if q.get("difficulte_estimee") not in ("faible", "moyenne", "elevee", "", None):
                erreurs.append(f"{nom} {etiquette}: difficulte_estimee invalide : {q.get('difficulte_estimee')!r}")
            pts = q.get("points")
            if pts is not None and not (isinstance(pts, int) and not isinstance(pts, bool) and pts >= 0):
                erreurs.append(f"{nom} {etiquette}: points doit être un entier ou null")
            if str(q.get("type_reponse", "")).lower() == "qcm":
                choix = q.get("choix") or []
                lettres = [c.get("lettre") for c in choix if isinstance(c, dict)]
                if len(choix) < 3 or len(set(lettres)) != len(lettres) or not all(lettres):
                    erreurs.append(f"{nom} {etiquette}: QCM avec choix invalides")
                if q.get("reponse_correcte") not in lettres:
                    erreurs.append(f"{nom} {etiquette}: reponse_correcte {q.get('reponse_correcte')!r} absente des choix {lettres}")
                if any(not str(c.get("texte", "")).strip() for c in choix if isinstance(c, dict)):
                    erreurs.append(f"{nom} {etiquette}: un choix a un texte vide (mettre la lettre si le choix est une image)")
        for ref in references - fichiers_figures:
            avertissements.append(f"{nom}: image {ref} utilisée mais absente de « figures »")
        for f in fichiers_figures - references - {None}:
            avertissements.append(f"{nom}: figure {f} déclarée mais jamais référencée par ![...]({f})")
        total_questions += len(questions)

    if attendu_questions is not None and total_questions != attendu_questions:
        erreurs.append(f"{total_questions} question(s) transcrite(s), {attendu_questions} attendue(s)")
    if paper == 1:
        try:
            numeros = sorted(int(n) for n in toutes_numeros)
            manquants = sorted(set(range(1, (attendu_questions or max(numeros)) + 1)) - set(numeros))
            if manquants:
                erreurs.append(f"numéros de QCM manquants : {manquants}")
        except ValueError:
            avertissements.append("numéros de question non numériques (Paper 1)")
    print(f"{len(fichiers)} fichier(s), {total_questions} question(s)")
    return erreurs, avertissements


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dossier")
    parser.add_argument("--questions", type=int, default=None, help="nombre total de questions attendu")
    parser.add_argument("--paper", type=int, default=None)
    parser.add_argument("--code", default=None)
    parser.add_argument("--examen", default="gce_ol", choices=["gce_ol", "gce_al"], help="niveau du sujet (défaut gce_ol)")
    args = parser.parse_args()
    erreurs, avertissements = valider(Path(args.dossier), args.questions, args.paper, args.code, args.examen)
    for a in avertissements:
        print("warn ", a)
    for e in erreurs:
        print("ERREUR", e)
    print("OK" if not erreurs else f"ECHEC ({len(erreurs)} erreur(s))")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
