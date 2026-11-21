import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { mettreEnEvidence } from "./cibles"

describe("mettreEnEvidence", () => {
  const defilerFenetre = vi.fn()
  const scrollToDorigine = window.scrollTo

  beforeEach(() => {
    defilerFenetre.mockClear()
    window.scrollTo = defilerFenetre as unknown as typeof window.scrollTo
  })

  afterEach(() => {
    window.scrollTo = scrollToDorigine
    document.body.innerHTML = ""
  })

  it("amène la cible à l'écran en faisant défiler la fenêtre, jamais ses ancêtres", () => {
    // `scrollIntoView` fait aussi défiler une carte en `overflow: hidden` : la carte de séance glissait sur
    // elle-même à l'étape « Ce que contient une séance », et son titre disparaissait jusqu'au rechargement.
    document.body.innerHTML = '<div id="carte" style="overflow: hidden"><div data-guide="seance-parcours">Ton parcours</div></div>'
    const cible = document.querySelector<HTMLElement>('[data-guide="seance-parcours"]')!
    const defilerAncetres = vi.fn()
    cible.scrollIntoView = defilerAncetres

    const retirer = mettreEnEvidence("seance-parcours")

    expect(cible).toHaveAttribute("data-guide-actif", "true")
    expect(defilerFenetre).toHaveBeenCalledTimes(1)
    expect(defilerAncetres).not.toHaveBeenCalled()
    expect(document.getElementById("carte")!.scrollTop).toBe(0)

    retirer()
    expect(cible).not.toHaveAttribute("data-guide-actif")
  })

  it("ne fait rien sans cible à l'écran", () => {
    mettreEnEvidence("absente")()
    mettreEnEvidence(undefined)()
    expect(defilerFenetre).not.toHaveBeenCalled()
  })
})
