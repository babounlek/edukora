#!/usr/bin/env python3
"""Contrôle les figures SVG d'un ou plusieurs JSON d'épreuve inédite (ou d'un dossier de JSON).

    python verifier_figures.py ep-cm-xxx.json [autre.json | dossier ...]

Code de sortie 1 s'il y a au moins une ERREUR (ne pas ingérer) ; les AVERTISSEMENTS demandent un coup d'œil sur
la figure rendue (voir rendre_figures.py). Ce contrôle ne remplace JAMAIS le contrôle visuel : il attrape ce
qui casse silencieusement le rendu (retour à la ligne, guillemets, dollar, couleur en dur), pas une figure fausse.
"""
import json
import re
import sys
from pathlib import Path

TAILLE_AVERT = 20_000
TAILLE_MAX = 40_000
FONT_MIN = 12
RE_SVG = re.compile(r"<svg\b.*?</svg>", re.S)
RE_COULEUR_DURE = re.compile(r"(#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\()")
RE_TEXT = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)


def attr(chaine, nom):
    m = re.search(rf"\b{nom}='([^']*)'", chaine)
    return m.group(1) if m else None


def champs_markdown(o, chemin=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from champs_markdown(v, f"{chemin}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from champs_markdown(v, f"{chemin}[{i}]")
    elif isinstance(o, str) and "<svg" in o:
        yield chemin, o


def boite_texte(attrs, contenu):
    try:
        x, y = float(attr(attrs, "x")), float(attr(attrs, "y"))
        taille = float(attr(attrs, "font-size") or 14)
    except (TypeError, ValueError):
        return None
    largeur = len(re.sub(r"<[^>]+>", "", contenu)) * taille * 0.56
    ancre = attr(attrs, "text-anchor") or "start"
    x0 = x - largeur / 2 if ancre == "middle" else (x - largeur if ancre == "end" else x)
    return (x0, y - taille * 0.8, x0 + largeur, y + taille * 0.25)


def recouvrement(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0
    return w * h / min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))


def verifier_figure(svg, texte_complet, debut):
    erreurs, avertissements = [], []
    if "\n" in svg or "\r" in svg:
        erreurs.append("retour à la ligne dans le SVG (le rendu PDF y insère un <br> qui le casse) : tout sur UNE ligne")
    if '"' in svg:
        erreurs.append("guillemet droit dans le SVG : la plateforme y fabrique des italiques ; attributs et textes sans guillemets droits")
    if "«" in svg or "»" in svg:
        erreurs.append("guillemets français dans le SVG : même effet, à retirer")
    if "$" in svg:
        erreurs.append("signe dollar dans le SVG : lu comme une formule ; écrire le symbole en toutes lettres")
    texte_nu = re.sub(r"<[^>]+>", " ", svg)
    if "*" in texte_nu:
        erreurs.append("astérisque dans un texte de la figure : le texte entre deux balises est lu comme du Markdown, deux astérisques font une italique qui AVALE les balises et casse la figure (écrire l'opérateur astérisque U+2217, ce que fait figures_svg.py)")
    if re.search(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])|~~|\[[^\]]*\]\(", texte_nu):
        erreurs.append("souligné isolé, ~~ ou lien [..](..) dans un texte de la figure : lu comme du Markdown")
    if re.search(r"https?://\S|www\.", texte_nu):
        avertissements.append("adresse web dans un texte de la figure : la plateforme la transforme en lien cliquable DANS le dessin")
    for balise in ("<script", "<image", "<foreignobject", "<iframe", "<use", "<a ", "<style", "xlink:", "href="):
        if balise in svg.lower():
            erreurs.append(f"{balise.strip('<')} interdit dans une figure")
    if re.search(r"\bon[a-z]+\s*=", svg):
        erreurs.append("gestionnaire d'événement (on...=) interdit")
    if "viewBox='" not in svg:
        erreurs.append("viewBox manquant : la figure ne se réduirait pas sur téléphone")
    if "role='img'" not in svg:
        erreurs.append("role='img' manquant")
    if not re.search(r"<title\b[^>]*>[^<]{4,}</title>", svg) or not re.search(r"<desc\b[^>]*>[^<]{12,}</desc>", svg):
        erreurs.append("<title> et <desc> (texte alternatif) absents ou trop courts")
    nu = RE_COULEUR_DURE.findall(re.sub(r"var\(--[a-z-]+,[^)]*\)", "", svg))
    if nu:
        erreurs.append(f"couleur en dur ({nu[0]}) : utiliser les variables du thème avec repli, sinon illisible en mode sombre")
    taille = len(svg.encode("utf-8"))
    if taille > TAILLE_MAX:
        erreurs.append(f"figure de {taille} octets (> {TAILLE_MAX}) : trop lourde")
    elif taille > TAILLE_AVERT:
        avertissements.append(f"figure de {taille} octets : lourde pour une connexion mobile")
    for m in re.finditer(r"font-size='([\d.]+)'", svg):
        if float(m.group(1)) < FONT_MIN:
            avertissements.append(f"police de {m.group(1)} < {FONT_MIN} : illisible une fois réduite sur téléphone")
            break
    vb = re.search(r"viewBox='0 0 ([\d.]+) ([\d.]+)'", svg)
    if vb and float(vb.group(1)) > 640:
        avertissements.append(f"viewBox de {vb.group(1)} de large : à 375 px d'écran le texte sera réduit de plus de moitié")
    # isolé dans un paragraphe : ligne vide avant et après, hors bloc de code
    avant, apres = texte_complet[:debut], texte_complet[debut + len(svg):]
    if avant and not avant.endswith("\n\n"):
        erreurs.append("pas de ligne vide AVANT la figure (elle doit former son propre paragraphe)")
    if apres and not apres.startswith("\n\n"):
        erreurs.append("pas de ligne vide APRÈS la figure")
    if avant.count("```") % 2 == 1:
        erreurs.append("figure placée dans un bloc de code : elle s'afficherait comme du texte")
    boites = []
    for m in RE_TEXT.finditer(svg):
        b = boite_texte(m.group(1), m.group(2))
        if b:
            boites.append((b, re.sub(r"<[^>]+>", "", m.group(2))))
    for i in range(len(boites)):
        for j in range(i + 1, len(boites)):
            if recouvrement(boites[i][0], boites[j][0]) > 0.3:
                avertissements.append(f"textes qui se recouvrent : {boites[i][1]!r} et {boites[j][1]!r}")
    return erreurs, avertissements


def verifier_fichier(chemin):
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
    nb_err = nb_av = nb_fig = 0
    ids = {}
    for ref, texte in champs_markdown(donnees):
        for m in RE_SVG.finditer(texte):
            nb_fig += 1
            erreurs, avert = verifier_figure(m.group(0), texte, m.start())
            for i in re.findall(r"\bid='([^']+)'", m.group(0)):
                if i in ids and ids[i] != ref:
                    erreurs.append(f"id {i!r} déjà utilisé par une autre figure ({ids[i]}) : deux figures de la même page se mélangeraient")
                ids.setdefault(i, ref)
            for e in erreurs:
                print(f"ERREUR  {Path(chemin).name} {ref} : {e}")
            for a in avert:
                print(f"AVERT.  {Path(chemin).name} {ref} : {a}")
            nb_err += len(erreurs)
            nb_av += len(avert)
        # un <svg ouvert jamais refermé
        if texte.count("<svg") != texte.count("</svg>"):
            print(f"ERREUR  {Path(chemin).name} {ref} : <svg> non refermé")
            nb_err += 1
    return nb_fig, nb_err, nb_av


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    fichiers = []
    for a in sys.argv[1:]:
        p = Path(a)
        fichiers += sorted(p.rglob("*.json")) if p.is_dir() else [p]
    total = [0, 0, 0]
    for f in fichiers:
        try:
            n, e, a = verifier_fichier(f)
        except json.JSONDecodeError as exc:
            print(f"ERREUR  {f.name} : JSON invalide ({exc})")
            total[1] += 1
            continue
        total = [total[0] + n, total[1] + e, total[2] + a]
    print(f"{total[0]} figure(s), {total[1]} erreur(s), {total[2]} avertissement(s)")
    sys.exit(1 if total[1] else 0)
