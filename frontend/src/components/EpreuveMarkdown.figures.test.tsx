import { render } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { EpreuveMarkdown } from "./EpreuveMarkdown"
import figures from "./__fixtures__/figures-svg.json"

/**
 * Figures SVG des épreuves inédites (skill concepteur-epreuve-inedite, scripts/figures_svg.py) : un <svg> sur une
 * ligne, collé dans le Markdown d'un énoncé ou d'un corrigé. Le texte entre deux balises traverse le même
 * pipeline que le reste du Markdown (italicizeQuotes, remark-gfm...) : ces tests garantissent que la figure
 * ressort STRUCTURELLEMENT identique. Fixtures produites par la bibliothèque du skill (astérisque de
 * multiplicité écrit U+2217 : deux « * » ouvrent une italique qui avale les balises et cassent le dessin).
 */
function structure(el: Element) {
  return [...el.querySelectorAll("*")].map((n) => n.tagName.toLowerCase()).join(",")
}

describe("EpreuveMarkdown : figures SVG intégrées", () => {
  beforeEach(() => {
    // jsdom + React : « The tag <text> is unrecognized in this browser » - bruit propre à jsdom.
    vi.spyOn(console, "error").mockImplementation(() => {})
  })
  afterEach(() => vi.restoreAllMocks())

  for (const [nom, svg] of Object.entries(figures as Record<string, string>)) {
    it(`${nom} : le dessin ressort identique, sans italique ni lien parasite`, () => {
      const { container } = render(
        <MemoryRouter>
          <EpreuveMarkdown markdown={`Avant la figure.\n\n${svg}\n\nAprès la figure.`} />
        </MemoryRouter>,
      )
      const rendu = container.querySelector("svg")
      expect(rendu).not.toBeNull()
      const attendu = document.createElement("div")
      attendu.innerHTML = svg
      const brut = attendu.querySelector("svg")!
      expect(structure(rendu!)).toBe(structure(brut))
      expect(rendu!.textContent).toBe(brut.textContent)
      expect(rendu!.querySelectorAll("em, strong, a, br, code").length).toBe(0)
      // accessibilité : titre, description et rôle conservés
      expect(rendu!.getAttribute("role")).toBe("img")
      expect(rendu!.querySelector("title")?.textContent).toBeTruthy()
      expect(rendu!.querySelector("desc")?.textContent).toBeTruthy()
      // l'attribut style (largeur adaptative) survit à la conversion
      expect(rendu!.getAttribute("style")).toContain("max-width")
    })
  }

  it("les couleurs restent des variables du thème (le mode sombre les remplace)", () => {
    const { container } = render(
      <MemoryRouter>
        <EpreuveMarkdown markdown={(figures as Record<string, string>).res_blocs} />
      </MemoryRouter>,
    )
    const svg = container.querySelector("svg")!
    expect(svg.outerHTML).toContain("var(--foreground")
    expect(svg.outerHTML).not.toMatch(/(fill|stroke)="#[0-9a-f]{3,6}"/i)
  })
})
