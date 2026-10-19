#!/usr/bin/env python3
"""Photographie une page HTML (ou des figures SVG) en PNG pour les REGARDER avant de livrer.

    python rendre_figures.py planche.html planche.png [largeur]
    python rendre_figures.py epreuve.json            # extrait chaque <svg> du JSON, écrit un PNG par figure

Moteurs essayés dans l'ordre : Playwright (Chromium), cairosvg, rsvg-convert. Aucun n'est disponible :
le script le dit et sort en erreur - dans ce cas ne livre PAS de figure non vérifiée (voir SKILL.md).
Le PNG produit sert uniquement au contrôle visuel, il n'est jamais livré avec l'épreuve."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CSS_CLAIR = ":root{--foreground:#161d1a;--muted-foreground:#5b6560;--border:#dde3df;--background:#faf9f5;--card:#fff;--primary:#0f6b4f;--info:#2a6fba;--gold:#d9a21f;--destructive:#c4352e;--success:#1a7a36;--accent:#e4f3ec}"


def photographier_html(src, dest, largeur=1300):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": largeur, "height": 900})
        page.goto(Path(src).resolve().as_uri())
        page.screenshot(path=dest, full_page=True)
        b.close()
    return True


def svg_vers_png(svg_text, dest):
    """Un SVG isolé, avec les variables de thème clair définies."""
    if photographier_html is None:
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(f"<!doctype html><meta charset='utf-8'><style>{CSS_CLAIR}body{{margin:0;padding:12px;background:#faf9f5;width:640px}}</style>{svg_text}")
    if photographier_html(tmp.name, dest, 680):
        return True
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(bytestring=svg_text.replace("var(--foreground,#161d1a)", "#161d1a").encode(), write_to=dest)
        return True
    except ImportError:
        pass
    if shutil.which("rsvg-convert"):
        Path(dest).with_suffix(".svg").write_text(svg_text, encoding="utf-8")
        subprocess.run(["rsvg-convert", "-o", dest, str(Path(dest).with_suffix(".svg"))], check=True)
        return True
    return False


def svgs_du_json(chemin):
    texte = Path(chemin).read_text(encoding="utf-8")
    donnees = json.loads(texte)
    trouves = []

    def parcourir(o, ch=""):
        if isinstance(o, dict):
            for k, v in o.items():
                parcourir(v, f"{ch}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                parcourir(v, f"{ch}[{i}]")
        elif isinstance(o, str):
            for i, m in enumerate(re.finditer(r"<svg\b.*?</svg>", o, re.S)):
                trouves.append((f"{ch}#{i + 1}", m.group(0)))

    parcourir(donnees)
    return trouves


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    if src.endswith(".json"):
        figs = svgs_du_json(src)
        if not figs:
            sys.exit("Aucun <svg> dans ce JSON.")
        base = Path(src).with_suffix("")
        for i, (ref, svg) in enumerate(figs, 1):
            dest = f"{base}_fig{i}.png"
            if not svg_vers_png(svg, dest):
                sys.exit("Aucun moteur de rendu disponible (Playwright, cairosvg, rsvg-convert) : figure NON vérifiée.")
            print(dest, "<-", ref)
    else:
        dest = sys.argv[2] if len(sys.argv) > 2 else str(Path(src).with_suffix(".png"))
        if not photographier_html(src, dest, int(sys.argv[3]) if len(sys.argv) > 3 else 1300):
            sys.exit("Playwright indisponible : impossible de photographier la page.")
        print(dest)
