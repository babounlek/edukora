import { render } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { FiltreLigne, PastilleFiltre } from "./FiltresCatalogue"

function rangee(actifId: string) {
  return (
    <FiltreLigne titre="Matière">
      {["bio", "chem", "maths"].map((id) => (
        <PastilleFiltre key={id} actif={id === actifId} onClick={() => {}}>
          {id}
        </PastilleFiltre>
      ))}
    </FiltreLigne>
  )
}

describe("FiltreLigne : la pastille choisie reste visible", () => {
  const defiler = vi.fn()

  beforeEach(() => {
    defiler.mockReset()
    HTMLElement.prototype.scrollTo = defiler
    vi.spyOn(HTMLElement.prototype, "offsetLeft", "get").mockReturnValue(400)
  })
  afterEach(() => vi.restoreAllMocks())

  it("amène la pastille choisie au centre d'une rangée qui déborde, une seule fois", () => {
    vi.spyOn(HTMLElement.prototype, "scrollWidth", "get").mockReturnValue(700)
    vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(300)
    const { rerender } = render(rangee("maths"))

    expect(defiler).toHaveBeenCalledTimes(1)
    expect(defiler).toHaveBeenCalledWith({ left: 400 })

    // Le même choix, rendu de nouveau : la main reste à l'élève qui fait glisser la rangée.
    rerender(rangee("maths"))
    expect(defiler).toHaveBeenCalledTimes(1)

    rerender(rangee("chem"))
    expect(defiler).toHaveBeenCalledTimes(2)
  })

  it("ne touche à rien quand toute la rangée tient à l'écran", () => {
    vi.spyOn(HTMLElement.prototype, "scrollWidth", "get").mockReturnValue(300)
    vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(300)
    render(rangee("maths"))

    expect(defiler).not.toHaveBeenCalled()
  })
})
