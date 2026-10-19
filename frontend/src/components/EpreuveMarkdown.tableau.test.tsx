import { fireEvent, render, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it, vi } from "vitest"

vi.mock("@/api/endpoints", () => ({ getCoursTitres: vi.fn(() => Promise.resolve({})) }))

import { EpreuveMarkdown } from "./EpreuveMarkdown"

const TABLEAU = "| x | −∞ | 3 | +∞ |\n|---|---|---|---|\n| f | ↘ | ↗ | ↘ |"

/** jsdom ne fait aucune mise en page : on fixe à la main la largeur du cadre et celle de son contenu. */
function mesures(scrollWidth: number, clientWidth: number) {
  vi.spyOn(HTMLElement.prototype, "scrollWidth", "get").mockReturnValue(scrollWidth)
  vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(clientWidth)
}

function afficher() {
  return render(
    <MemoryRouter>
      <EpreuveMarkdown markdown={TABLEAU} />
    </MemoryRouter>,
  )
}

afterEach(() => vi.restoreAllMocks())

describe("EpreuveMarkdown : indice de défilement des tableaux", () => {
  it("signale la suite d'un tableau plus large que son cadre", async () => {
    mesures(560, 300)
    const { container } = afficher()

    await waitFor(() => expect(container.querySelector("[data-indice-defilement]")).not.toBeNull())
  })

  it("ne montre rien quand le tableau tient entièrement", () => {
    mesures(300, 300)
    const { container } = afficher()

    expect(container.querySelector("[data-indice-defilement]")).toBeNull()
  })

  it("disparaît une fois le bord droit atteint", async () => {
    mesures(560, 300)
    const { container } = afficher()
    await waitFor(() => expect(container.querySelector("[data-indice-defilement]")).not.toBeNull())

    const cadre = container.querySelector("table")!.parentElement as HTMLElement
    cadre.scrollLeft = 260
    fireEvent.scroll(cadre)

    await waitFor(() => expect(container.querySelector("[data-indice-defilement]")).toBeNull())
  })
})
