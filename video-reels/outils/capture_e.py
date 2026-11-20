"""Captures réelles pour la vidéo E (parents : prix et paiement). Site public, aucune action de paiement.
Sorties : sources/captures/e-*.png (390 px CSS de large, échelle 3)."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "sources" / "captures"
OUT.mkdir(parents=True, exist_ok=True)
CACHER = ("*{scroll-behavior:auto!important;animation:none!important;transition:none!important}"
          "[class*=fixed],[class*=sticky]{position:static!important}")
# la date « Accès jusqu'au … » dépend du jour de la capture : on la masque
JS_MASQUER_DATE = r"""() => { for (const e of document.querySelectorAll('p,div,span')) {
  if (e.children.length === 0 && /^Acc.s jusqu'au/.test(e.textContent.trim())) e.style.visibility = 'hidden'; } }"""
JS_RECT = r"""(txt) => { const els=[...document.querySelectorAll('h1,h2,h3,p,div,span,button,a')]
  .filter(e=>e.innerText && e.innerText.trim().includes(txt) && e.innerText.length < 400 && e.getBoundingClientRect().width>0);
  if(!els.length) return null;
  els.sort((a,b)=>a.getBoundingClientRect().width*a.getBoundingClientRect().height-b.getBoundingClientRect().width*b.getBoundingClientRect().height);
  const r=els[0].getBoundingClientRect(); return {x:r.left,y:r.top+scrollY,w:r.width,h:r.height}; }"""


def clip(page, nom, y0, y1):
    page.screenshot(path=OUT / nom, full_page=True,
                    clip={"x": 0, "y": max(y0, 0), "width": 390, "height": y1 - y0})


with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 900}, device_scale_factor=3, locale="fr-FR")
    page = ctx.new_page()

    # --- page des tarifs, BEPC choisi (3 mois par défaut) ---
    page.goto("https://edukora.africa/tarifs")
    page.wait_for_load_state("networkidle"); page.wait_for_timeout(1800)
    page.add_style_tag(content=CACHER)
    page.get_by_role("button", name="BEPC", exact=True).first.click()
    page.wait_for_timeout(1800)
    page.evaluate(JS_MASQUER_DATE)
    page.mouse.move(2, 2)
    clip(page, "e-01-prix.png", 0, 380)
    r_mois = page.evaluate(JS_RECT, "Pour combien de mois")
    r_cont = page.evaluate(JS_RECT, "Pas encore sûr")
    print("mois", r_mois, "fin récap", r_cont)
    clip(page, "e-02-mois-total.png", int(r_mois["y"]) - 24, int(r_cont["y"]) - 8)
    r_comment = page.evaluate(JS_RECT, "Comment ça se passe")
    r_dern = page.evaluate(JS_RECT, "Notre équipe vérifie")
    print("comment", r_comment, "dernière étape", r_dern)
    clip(page, "e-03-etapes.png", int(r_comment["y"]) - 16, int(r_dern["y"] + r_dern["h"]) + 16)

    # --- accueil : bloc « Tu es parent ? » ---
    page.goto("https://edukora.africa/cm")
    page.wait_for_load_state("networkidle"); page.wait_for_timeout(1800)
    page.add_style_tag(content=CACHER)
    page.mouse.move(2, 2)
    r_par = page.evaluate(JS_RECT, "Tu es parent")
    r_btn = page.evaluate(JS_RECT, "Comment payer")
    print("parent", r_par, "bouton", r_btn)
    clip(page, "e-04-parent.png", int(r_par["y"]) - 24, int(r_btn["y"] + r_btn["h"]) + 24)
    nav.close()
