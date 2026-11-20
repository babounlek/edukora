"""Captures réelles pour la vidéo A (« Ta première séance »), site public, visiteur anonyme.

Le quiz sans compte tire ses questions au hasard : on recommence (6 essais au plus) jusqu'à obtenir
une réponse juste en choisissant la proposition A, pour montrer l'état « Excellent ! ».
Sorties : sources/captures/a-*.png (390 px CSS de large, échelle 3)."""
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "sources" / "captures"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://edukora.africa"
CACHER = "*{scroll-behavior:auto!important;animation:none!important;transition:none!important}"
JS_MASQUER_J = r"""() => { for (const e of document.querySelectorAll('span,div,p')) {
  if (e.children.length === 0 && /^J-\d+$/.test(e.textContent.trim())) e.style.visibility = 'hidden'; } }"""


def calme(page, ms=1200):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(ms)


def essai(nav, tentative):
    ctx = nav.new_context(viewport={"width": 390, "height": 1500}, device_scale_factor=3, locale="fr-FR")
    page = ctx.new_page()
    page.goto(f"{BASE}/cm")
    calme(page, 1800)
    page.add_style_tag(content=CACHER)
    page.mouse.move(2, 2)
    if tentative == 1:
        page.screenshot(path=OUT / "a-01-accueil.png", clip={"x": 0, "y": 0, "width": 390, "height": 900})
    page.get_by_role("button", name="BEPC", exact=True).first.click()
    page.wait_for_timeout(2500)
    page.evaluate(JS_MASQUER_J)
    page.mouse.move(2, 2)
    if tentative == 1:
        page.screenshot(path=OUT / "a-02-theme.png", clip={"x": 0, "y": 0, "width": 390, "height": 900})
        print("badge :", page.get_by_text("Tombé dans").first.inner_text())
    page.get_by_text("Commencer, sans compte").first.click()
    calme(page, 2200)
    page.add_style_tag(content=CACHER)
    page.mouse.move(2, 2)
    page.wait_for_timeout(500)
    page.screenshot(path=OUT / "a-03-question.png", clip={"x": 0, "y": 0, "width": 390, "height": 900})
    page.locator("main button").nth(7).click()          # proposition A
    page.wait_for_timeout(1800)
    page.mouse.move(2, 2)
    if "Excellent" not in page.inner_text("main"):
        ctx.close()
        return False
    page.screenshot(path=OUT / "a-04-reponse.png", clip={"x": 0, "y": 0, "width": 390, "height": 900})
    page.get_by_text("Comprendre la correction").first.click()
    page.wait_for_timeout(1500)
    page.mouse.move(2, 2)
    page.screenshot(path=OUT / "a-05-correction.png")      # fenêtre haute : toute la correction tient
    ctx.close()
    return True


with sync_playwright() as p:
    nav = p.chromium.launch()
    for t in range(1, 7):
        ok = essai(nav, t)
        print("essai", t, "juste" if ok else "raté, on recommence")
        if ok:
            break
    nav.close()
