import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getPlanDuJour = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true, user: { cursus_prepare: { id: 1 } } as { cursus_prepare: unknown } | null }))
vi.mock("@/api/endpoints", () => ({ getPlanDuJour }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))

import { FlammeSerie } from "./FlammeSerie"

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <FlammeSerie />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getPlanDuJour.mockReset()
  auth.isAuthenticated = true
  auth.user = { cursus_prepare: { id: 1 } }
})

describe("FlammeSerie", () => {
  it("montre le nombre de jours de suite, avec un lien vers l'accueil", async () => {
    getPlanDuJour.mockResolvedValue({ serie: { jours: 4 } })
    afficher()

    const lien = await screen.findByRole("link", { name: "4 jours de suite" })
    expect(lien).toHaveAttribute("href", "/cm")
    expect(lien).toHaveTextContent("4")
  })

  it("dit « Jour 1 : bien parti ! » au premier jour", async () => {
    getPlanDuJour.mockResolvedValue({ serie: { jours: 1 } })
    afficher()

    expect(await screen.findByRole("link", { name: "Jour 1 : bien parti !" })).toBeInTheDocument()
  })

  it("ne montre rien à 0 jour : une flamme éteinte culpabiliserait", async () => {
    getPlanDuJour.mockResolvedValue({ serie: { jours: 0 } })
    const { container } = afficher()

    await vi.waitFor(() => expect(getPlanDuJour).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("ne demande rien à un visiteur", () => {
    auth.isAuthenticated = false
    const { container } = afficher()

    expect(getPlanDuJour).not.toHaveBeenCalled()
    expect(container).toBeEmptyDOMElement()
  })
})
