"""
Photographie chaque vue de <semaine>/sources/pages.html en PNG (images/4x5, images/9x16), réduit le texte d'une vue
qui déborde et le signale, puis assemble les vues 4:5 en un PDF pour l'enseignant.

    python photographier.py <dossier de la semaine>

Il faut Playwright (le venv de video-facebook l'a) : ..\\..\\video-facebook\\.venv\\Scripts\\python.exe
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

if len(sys.argv) != 2 or not (Path(sys.argv[1]) / "sources" / "pages.html").exists():
    sys.exit("Usage : python photographier.py <dossier de la semaine> (lancer d'abord node construire.mjs)")
SEMAINE = Path(sys.argv[1]).resolve()
PAGES = SEMAINE / "sources" / "pages.html"
SORTIE = SEMAINE / "images"

AJUSTER = """el => {
  const main = el.querySelector('main'), c = el.querySelector('.contenu')
  const dispo = () => main.clientHeight - 56
  // Un bout de texte (formule, ponctuation qui la suit) qui dépasse le contenu ou l'encadré qui le contient.
  // On mesure le texte visible seulement : la copie MathML des formules (pour les lecteurs d'écran) est hors champ.
  const depasse = (boite, limite) => {
    const w = document.createTreeWalker(boite, NodeFilter.SHOW_TEXT), r = document.createRange()
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!n.textContent.trim() || n.parentElement.closest('.katex-mathml')) continue
      r.selectNodeContents(n)
      for (const x of r.getClientRects()) if (x.width > 0 && x.right > limite + 2) return true
    }
    return false
  }
  const interieur = b => b.getBoundingClientRect().right - parseFloat(getComputedStyle(b).paddingRight)
  const deborde = () => c.offsetHeight > dispo() ||
    [...c.querySelectorAll('*')].some(n => !n.closest('.katex') && n.scrollWidth > n.clientWidth + 2 && n.clientWidth > 0) ||
    depasse(c, c.getBoundingClientRect().right) ||
    [...c.querySelectorAll('.reponse, .piege, .invitation')].some(b => depasse(b, interieur(b)))
  let t = 44
  // Une vue peu remplie grossit un peu, une vue chargée rétrécit.
  while (t < 54 && c.offsetHeight < dispo() * 0.7) { c.style.fontSize = (++t) + 'px' }
  while (t > 24 && deborde()) { c.style.fontSize = (--t) + 'px' }
  // Le bandeau tient sur une ligne : sinon il est trop long (une série en trop dans le bandeau).
  const b = el.querySelector('.bandeau')
  return { taille: t, deborde: deborde(), bandeau_sur_deux_lignes: b.getClientRects().length > 1 || b.offsetHeight > 75 }
}"""

with sync_playwright() as p:
    navigateur = p.chromium.launch()
    onglet = navigateur.new_page(viewport={"width": 1080, "height": 1920})
    onglet.goto(PAGES.as_uri())
    onglet.evaluate("document.fonts.ready")
    onglet.wait_for_load_state("networkidle")
    vues = onglet.query_selector_all("section.page")
    # Les vues de rechange (data-variante-de) passent après : on ne les prend que si la vue qu'elles remplacent est trop
    # chargée (texte qui déborde ou sous 30 px) ; celle-ci n'est alors pas gardée.
    vues = sorted(vues, key=lambda v: v.get_attribute("data-variante-de") is not None)
    petites, faites, coupees = [], set(), set()
    for vue in vues:
        nom = vue.get_attribute("data-nom")
        parent = vue.get_attribute("data-variante-de")
        if parent is not None and parent not in coupees:
            continue
        etat = vue.evaluate(AJUSTER)
        if parent is None and vue.evaluate("el => !!document.querySelector(`[data-variante-de='${el.dataset.nom}']`)") \
                and (etat["deborde"] or etat["taille"] < 30):
            coupees.add(nom)
            petites.append((nom, {"coupee_en_deux": True}))
            continue
        if etat["deborde"] or etat["taille"] < 36 or etat["bandeau_sur_deux_lignes"]:
            petites.append((nom, {k: v for k, v in etat.items() if v}))
        cible = SORTIE / f"{nom}.png"
        cible.parent.mkdir(parents=True, exist_ok=True)
        image = vue.screenshot()
        # Sous Windows, une image ouverte ou en cours d'aperçu peut refuser l'écriture un instant.
        for essai in range(10):
            try:
                cible.write_bytes(image)
                break
            except OSError:
                if essai == 9:
                    raise
                time.sleep(1)
        faites.add(cible.resolve())

    # Une image qui n'est plus produite (clé de fiche changée) ne doit pas rester à côté des autres.
    obsoletes = [i for i in SORTIE.rglob("*.png") if i.resolve() not in faites]
    for i in obsoletes:
        i.unlink()
    print(len(faites), "images ;", len(obsoletes), "obsolètes supprimées ; à surveiller :", petites or "aucune")
    print("  (à surveiller = texte sous 36 px, qui déborde, ou bandeau sur deux lignes : regarder l'image ;"
          " sous 36 px sans débordement, c'est souvent lisible ; un bandeau sur deux lignes se raccourcit dans semaine.json)")

    # Un PDF des vues 4:5, à montrer à l'enseignant.
    images = sorted((SORTIE / "4x5").glob("*.png"))
    planche = SEMAINE / "sources" / "planche.html"
    planche.write_text(
        "<style>@page{size:A4;margin:8mm}body{margin:0;display:grid;grid-template-columns:1fr 1fr;gap:4mm}"
        "img{width:100%;border:1px solid #bbb;break-inside:avoid}</style>"
        + "".join(f'<img src="{i.as_uri()}">' for i in images),
        encoding="utf-8",
    )
    onglet.goto(planche.as_uri())
    onglet.wait_for_load_state("networkidle")
    onglet.pdf(path=str(SEMAINE / "a-montrer-a-l-enseignant.pdf"), prefer_css_page_size=True, print_background=True)
    planche.unlink()
    navigateur.close()
