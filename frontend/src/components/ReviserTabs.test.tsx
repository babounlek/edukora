import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))

import { ReviserTabs } from "./ReviserTabs"
import { useRaccourciRecherche } from "@/lib/useRaccourciRecherche"
import { veutFocusRecherche } from "@/lib/recherche"

function Ecouteur({ ouvrir }: { ouvrir: () => void }) {
  useRaccourciRecherche(ouvrir)
  return null
}

function Lieu() {
  const lieu = useLocation()
  return (
    <div data-testid="lieu" data-focus={String(veutFocusRecherche(lieu.state))}>
      {lieu.pathname}
    </div>
  )
}

function monter(chemin = "/cm/cours") {
  const ouvrir = vi.fn()
  render(
    <MemoryRouter initialEntries={[chemin]}>
      <Ecouteur ouvrir={ouvrir} />
      <Routes>
        <Route path="*" element={<ReviserTabs />} />
      </Routes>
      <Lieu />
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

  it("la recherche est un lien vers la page de recherche, champ prêt à écrire", async () => {
    monter()
    const lien = screen.getByRole("link", { name: "Rechercher sur tout le site" })
    expect(lien).toHaveAttribute("href", "/cm/recherche")
    await userEvent.click(lien)
    expect(screen.getByTestId("lieu")).toHaveTextContent("/cm/recherche")
    expect(screen.getByTestId("lieu")).toHaveAttribute("data-focus", "true")
  })

  it("n'est pas un cinquième onglet : aucun onglet n'est marqué actif pour elle", () => {
    monter()
    expect(screen.getAllByRole("link", { current: "page" })).toHaveLength(1)
  })

  it("est absente de la page de recherche, qui a déjà son grand champ", () => {
    monter("/cm/recherche")
    expect(screen.queryByRole("link", { name: "Rechercher sur tout le site" })).not.toBeInTheDocument()
    expect(screen.getAllByRole("link")).toHaveLength(4)
  })

  it("le raccourci « / » appelle l'ouverture, sauf quand on écrit dans un champ", async () => {
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

  it("Ctrl+K appelle l'ouverture même depuis un champ de saisie", async () => {
    const ouvrir = monter()
    const champ = document.createElement("input")
    document.body.appendChild(champ)
    champ.focus()
    await userEvent.keyboard("{Control>}k{/Control}")
    expect(ouvrir).toHaveBeenCalledTimes(1)
    champ.remove()
  })
})
