import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { installerIndiceDefilementFormules } from "@/lib/indiceDefilementFormules"

/** jsdom ne fait aucune mise en page : on pose les mesures à la main. */
function formule(scrollWidth: number, clientWidth: number, scrollLeft = 0): HTMLElement {
  const el = document.createElement("div")
  el.className = "katex-display"
  Object.defineProperty(el, "scrollWidth", { value: scrollWidth, configurable: true })
  Object.defineProperty(el, "clientWidth", { value: clientWidth, configurable: true })
  el.scrollLeft = scrollLeft
  document.body.appendChild(el)
  return el
}

describe("indice de défilement des formules larges", () => {
  let arreter: () => void

  beforeEach(() => {
    vi.stubGlobal("requestAnimationFrame", (rappel: FrameRequestCallback) => {
      rappel(0)
      return 0
    })
    document.body.innerHTML = ""
  })

  afterEach(() => {
    arreter?.()
    vi.unstubAllGlobals()
  })

  it("marque une formule plus large que son bloc : il en reste à droite", () => {
    const el = formule(565, 270)
    arreter = installerIndiceDefilementFormules()

    expect(el.dataset.defile).toBe("droite")
  })

  it("ne marque pas une formule qui tient", () => {
    const el = formule(150, 270)
    arreter = installerIndiceDefilementFormules()

    expect(el.dataset.defile).toBeUndefined()
  })

  it("suit le défilement : au milieu des deux côtés, au bout seulement à gauche", () => {
    const el = formule(565, 270)
    arreter = installerIndiceDefilementFormules()

    el.scrollLeft = 100
    el.dispatchEvent(new Event("scroll"))
    expect(el.dataset.defile).toBe("les-deux")

    el.scrollLeft = 295
    el.dispatchEvent(new Event("scroll"))
    expect(el.dataset.defile).toBe("gauche")
  })

  it("marque une formule ajoutée après coup", async () => {
    arreter = installerIndiceDefilementFormules()
    const el = formule(565, 270)

    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(el.dataset.defile).toBe("droite")
  })
})
