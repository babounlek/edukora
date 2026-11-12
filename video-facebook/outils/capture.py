"""Captures réelles du site (lecture seule, aucun compte, aucune donnée personnelle).

Sorties dans sources/captures/ :
  page-haut.png       haut de la page du corrigé (mise en page bureau)
  exercice.png        carte de l'exercice choisi (mise en page étroite, formules KaTeX)
  exercice.json       positions (px CSS, relatives à exercice.png) des blocs à mettre en valeur
  bandeau-examens.png barre « Choisis ton examen » de l'accueil
Usage : python outils/capture.py
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
CFG = json.loads((RACINE / "config.json").read_text(encoding="utf-8"))
SORTIE = RACINE / "sources" / "captures"
SORTIE.mkdir(parents=True, exist_ok=True)
BASE = CFG["url_site"]
SLUG = CFG["corrige"]["slug"]
EXO = CFG["corrige"]["exercice"]

CACHER_FIXES = """
*{scroll-behavior:auto !important;animation:none !important;transition:none !important}
[class*="fixed"],[class*="sticky"]{position:static !important}
"""

# Blocs à repérer : (clé, textes qui doivent tous apparaître dans le bloc)
CIBLES = [
    ("q1_enonce", ["Développe, réduis et ordonne"]),
    ("q1_rappel", ["Rappel de méthode", "Pour développer, réduire"]),
    ("q1_developpement", ["Développement de", "double distributivité"]),
    ("q1_regroupement", ["Regroupement par degré"]),
    ("q1_conclusion", ["Conclusion (ordre croissant)"]),
    ("q2_enonce", ["Écris", "sous la forme d'un produit de facteurs"]),
    ("q2_rappel", ["Rappel de méthode", "Pour factoriser un polynôme"]),
    ("q2_verification", ["Vérification", "correspond bien"]),
    ("q2_conclusion", ["Conclusion.", "(4x−5)(7x+6)"]),
]

JS_BBOX = """
([sel, cibles]) => {
  const racine = document.querySelector(sel);
  const r0 = racine.getBoundingClientRect();
  const norm = s => s.replace(/\\s+/g, ' ');
  const out = {racine: {w: r0.width, h: r0.height}};
  for (const [cle, textes] of cibles) {
    let meilleur = null, aire = Infinity;
    for (const el of racine.querySelectorAll('div,p,section,li')) {
      const t = norm(el.textContent || '');
      if (!textes.every(x => t.includes(x))) continue;
      const b = el.getBoundingClientRect();
      const a = b.width * b.height;
      if (a < aire && a > 0) { aire = a; meilleur = b; }
    }
    out[cle] = meilleur ? {x: meilleur.left - r0.left, y: meilleur.top - r0.top, w: meilleur.width, h: meilleur.height} : null;
  }
  return out;
}
"""


def attendre_page(page):
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(800)


def main():
    with sync_playwright() as p:
        nav = p.chromium.launch()

        # 1. Haut de la page du corrigé, mise en page bureau
        ctx = nav.new_context(viewport={"width": 900, "height": 1000}, device_scale_factor=2, locale="fr-FR")
        page = ctx.new_page()
        page.goto(f"{BASE}/cm/epreuves/{SLUG}/lire")
        page.wait_for_selector(".katex", timeout=30000)
        attendre_page(page)
        page.add_style_tag(content=CACHER_FIXES)
        page.screenshot(path=SORTIE / "page-haut.png", clip={"x": 0, "y": 0, "width": 900, "height": 1900}, full_page=True)
        ctx.close()

        # 2. Carte de l'exercice, mise en page étroite (texte plus gros une fois cadré)
        ctx = nav.new_context(viewport={"width": 440, "height": 900}, device_scale_factor=3, locale="fr-FR")
        page = ctx.new_page()
        page.goto(f"{BASE}/cm/epreuves/{SLUG}/lire")
        page.wait_for_selector(".katex", timeout=30000)
        attendre_page(page)
        page.add_style_tag(content=CACHER_FIXES)
        sel = f"#exercice-{EXO}"
        page.locator(sel).scroll_into_view_if_needed()
        page.wait_for_timeout(1500)
        page.locator(sel).screenshot(path=SORTIE / "exercice.png")
        page.wait_for_timeout(500)
        boites = page.evaluate(JS_BBOX, [sel, CIBLES])
        (SORTIE / "exercice.json").write_text(json.dumps(boites, indent=1), encoding="utf-8")
        erreurs = page.evaluate("document.querySelectorAll('.katex-error').length")
        print("katex-error dans la page :", erreurs)
        ctx.close()

        # 3. Barre « Choisis ton examen » (accueil)
        ctx = nav.new_context(viewport={"width": 900, "height": 900}, device_scale_factor=2, locale="fr-FR")
        page = ctx.new_page()
        page.goto(f"{BASE}/cm")
        page.locator("span:visible", has_text="Choisis ton examen").first.wait_for(timeout=30000)
        attendre_page(page)
        page.add_style_tag(content=CACHER_FIXES)
        b = page.evaluate(
            """() => { const t=[...document.querySelectorAll('*')].find(e=>e.children.length===0 && /Choisis ton examen/.test(e.textContent) && e.getBoundingClientRect().width>0);
            let n=t; for(let i=0;i<6 && n.parentElement;i++){ n=n.parentElement; if(n.textContent.includes('BAC') && n.textContent.includes('Probatoire') && n.getBoundingClientRect().height>60) break;}
            const r=n.getBoundingClientRect(); return {x:r.left,y:r.top+scrollY,w:r.width,h:r.height}; }"""
        )
        print("bandeau", b)
        page.screenshot(path=SORTIE / "bandeau-examens.png",
                        clip={"x": max(b["x"] - 12, 0), "y": max(b["y"] - 12, 0), "width": min(b["w"] + 24, 900), "height": b["h"] + 24},
                        full_page=True)
        ctx.close()
        nav.close()


main()
