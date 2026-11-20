"""Captures réelles pour la vidéo B (« Un exercice, expliqué », épisode 1) : Mathématiques BEPC 2026,
exercice 4 (corrigé en accès libre). Site public, visiteur anonyme.
Sorties : sources/captures/b-exercice.png (+ b-exercice.json : positions des blocs, px CSS)."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "sources" / "captures"
OUT.mkdir(parents=True, exist_ok=True)
SLUG, EXO = "mathematiques-bepc-2026", 4
CACHER = ("*{scroll-behavior:auto!important;animation:none!important;transition:none!important}"
          "[class*=fixed],[class*=sticky]{position:static!important}")
CIBLES = [
    ("q1_enonce", ["1. Détermine les distances"]),
    ("q1_rappel", ["Rappel de méthode", "Dans un triangle rectangle, si l'on connaît l'hypoténuse"]),
    ("q1_calcul_ab", ["Calcul de", "(côté adjacent)"]),
    ("q1_calcul_bc", ["Calcul de", "(côté opposé)"]),
    ("q1_conclusion", ["Conclusion.", "6,93"]),
    ("q1_piege", ["Piège à éviter", "adjacent"]),
    ("q2_enonce", ["Les droites", "sont parallèles", "Calcule la distance"]),
]
JS = r"""([sel, cibles]) => {
  const racine = document.querySelector(sel); const r0 = racine.getBoundingClientRect();
  const norm = s => s.replace(/\s+/g, ' ');
  const out = {racine: {w: r0.width, h: r0.height}};
  for (const [cle, textes] of cibles) {
    let meilleur = null, aire = Infinity;
    for (const el of racine.querySelectorAll('div,p,section,li')) {
      const t = norm(el.textContent || '');
      if (!textes.every(x => t.includes(x))) continue;
      const b = el.getBoundingClientRect(); const a = b.width * b.height;
      if (a < aire && a > 0) { aire = a; meilleur = b; }
    }
    out[cle] = meilleur ? {x: meilleur.left - r0.left, y: meilleur.top - r0.top, w: meilleur.width, h: meilleur.height} : null;
  }
  return out; }"""

with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 440, "height": 900}, device_scale_factor=3, locale="fr-FR")
    page = ctx.new_page()
    page.goto(f"https://edukora.africa/cm/epreuves/{SLUG}/lire")
    page.wait_for_selector(".katex", timeout=30000)
    page.wait_for_load_state("networkidle"); page.wait_for_timeout(1500)
    page.add_style_tag(content=CACHER)
    sel = f"#exercice-{EXO}"
    page.locator(sel).scroll_into_view_if_needed(); page.wait_for_timeout(1500)
    page.locator(sel).screenshot(path=OUT / "b-exercice.png")
    page.wait_for_timeout(500)
    boites = page.evaluate(JS, [sel, CIBLES])
    (OUT / "b-exercice.json").write_text(json.dumps(boites, indent=1), encoding="utf-8")
    print("katex-error :", page.evaluate("document.querySelectorAll('.katex-error').length"))
    for k, v in boites.items():
        print(k, v)
    nav.close()
