import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  user: { cursus_prepare: { id: 1414, examen: "GCE_OL", examen_display: "GCE O Level", series: null, langue: "en" } } as unknown,
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm", countries: [] }) }))
vi.mock("@/api/endpoints", () => ({
  getPlatformStats: vi.fn(() => Promise.resolve({ corriges_disponibles: 512, cours_disponibles: 785 })),
  listCursus: vi.fn(() => Promise.resolve([])),
}))
vi.mock("@/components/CompteAReboursBadge", () => ({ CompteAReboursBadge: () => <span data-testid="pilule" /> }))

import { BottomTabBar } from "./BottomTabBar"
import { Footer } from "./Footer"

function afficher(ui: React.ReactNode, chemin: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[chemin]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("Footer : absent pendant un quiz", () => {
  it("ne s'affiche ni sur une séance de quiz ni sur un essai (test élève Gogo : pied de page marketing sous « Question suivante »)", () => {
    for (const chemin of ["/quiz/session/460", "/quiz/essai", "/quiz/essai/resultat"]) {
      const { container, unmount } = afficher(<Footer />, chemin)
      expect(container).toBeEmptyDOMElement()
      unmount()
    }
  })

  it("reste affiché ailleurs", () => {
    afficher(<Footer />, "/quiz")

    expect(screen.getByRole("contentinfo")).toBeInTheDocument()
  })
})

describe("BottomTabBar : pastille du compte à rebours", () => {
  it("n'est pas posée sur les réponses d'un quiz en cours", () => {
    afficher(<BottomTabBar />, "/quiz/session/460")

    expect(screen.getByRole("navigation")).toBeInTheDocument()
    expect(screen.queryByTestId("pilule")).not.toBeInTheDocument()
  })

  it("reste visible sur les autres pages de révision", () => {
    afficher(<BottomTabBar />, "/cm/epreuves")

    expect(screen.getByTestId("pilule")).toBeInTheDocument()
  })
})
