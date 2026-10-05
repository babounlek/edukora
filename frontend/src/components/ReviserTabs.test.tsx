import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))

import { ReviserTabs } from "./ReviserTabs"
import { useRaccourciRecherche } from "@/lib/useRaccourciRecherche"

function Ecouteur({ ouvrir }: { ouvrir: () => void }) {
  useRaccourciRecherche(ouvrir)
  return null
}

function monter(chemin = "/cm/cours") {
  const ouvrir = vi.fn()
  render(
    <MemoryRouter initialEntries={[chemin]}>
      <Ecouteur ouvrir={ouvrir} />
      <ReviserTabs />
    </MemoryRouter>,
  )
  return ouvrir
}

describe("ReviserTabs", () => {
  it("garde les quatre onglets et marque celui de la page", () => {
    monter("/cm/cours")
    expect(screen.getByRole("link", { name: "Cours" })).toHaveAttribute("aria-current", "page")
    for (const nom of ["Épreuves", "Thèmes", "Quiz"]) {
      expect(screen.getByRole("link", { name: nom })).not.toHaveAttribute("aria-current")
    }
  })

  it("le bouton de recherche ouvre la palette de recherche", async () => {
    const ouvrir = monter()
    await userEvent.click(screen.getByRole("button", { name: "Rechercher sur tout le site" }))
    expect(ouvrir).toHaveBeenCalledTimes(1)
  })

  it("n'est pas un lien : la recherche n'est pas un cinquième onglet", () => {
    monter()
    expect(screen.getAllByRole("link")).toHaveLength(4)
  })

  it("le raccourci « / » ouvre aussi la palette, sauf quand on écrit dans un champ", async () => {
    const ouvrir = monter()
    await userEvent.keyboard("/")
    expect(ouvrir).toHaveBeenCalledTimes(1)

    const champ = document.createElement("input")
    document.body.appendChild(champ)
    champ.focus()
    await userEvent.keyboard("/")
    expect(ouvrir).toHaveBeenCalledTimes(1)
    champ.remove()
  })
})
