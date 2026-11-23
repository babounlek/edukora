import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it, vi } from "vitest"

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

describe("Footer : bandeau d'invitation", () => {
  // `auth` est partagé avec les tests suivants (élève connecté) : on le remet comme on l'a trouvé.
  const connecte = { isAuthenticated: auth.isAuthenticated, user: auth.user }
  afterEach(() => {
    auth.isAuthenticated = connecte.isAuthenticated
    auth.user = connecte.user
  })

  it("ne propose pas « Voir les prix » depuis la page des prix", () => {
    auth.isAuthenticated = false
    auth.user = null
    afficher(<Footer />, "/tarifs")

    expect(screen.getByRole("contentinfo")).toBeInTheDocument()
    expect(screen.queryByText("Créer mon compte")).not.toBeInTheDocument()
    expect(screen.queryByText("Voir les prix")).not.toBeInTheDocument()
  })

  it("reste proposé à un visiteur sur les autres pages", () => {
    auth.isAuthenticated = false
    auth.user = null
    afficher(<Footer />, "/cm/epreuves")

    expect(screen.getByText("Créer mon compte")).toBeInTheDocument()
    expect(screen.getByText("Voir les prix")).toBeInTheDocument()
  })
})

describe("Footer : pas d'invitation pour un abonné actif", () => {
  it("ne montre ni « Faire ma séance » ni « Encore un quiz » à un abonné, mais garde le pied de page", () => {
    auth.isAuthenticated = true
    auth.user = { a_un_abonnement_actif: true, cursus_prepare: { id: 1, examen: "BEPC", examen_display: "BEPC", series: null, langue: "fr" } }
    afficher(<Footer />, "/carnet")

    expect(screen.getByRole("contentinfo")).toBeInTheDocument()
    expect(screen.queryByText("Faire ma séance")).not.toBeInTheDocument()
    expect(screen.queryByText(/Encore un quiz/)).not.toBeInTheDocument()
  })
})

describe("Footer : l'éditeur et ses moyens de contact", () => {
  it("nomme l'éditeur et sa ville, et écrit le numéro WhatsApp et l'adresse e-mail en clair", () => {
    afficher(<Footer />, "/cm/epreuves")

    expect(screen.getByText("Édité par Kora SARL")).toBeInTheDocument()
    expect(screen.getByText("Yaoundé, Cameroun")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /WhatsApp \+237/ })).toHaveAttribute("href", expect.stringContaining("wa.me/"))
    expect(screen.getByRole("link", { name: /^contact@/ })).toHaveAttribute("href", expect.stringMatching(/^mailto:contact@/))
  })

  it("ne répète plus les chiffres de la plateforme, que l'accueil dit déjà", () => {
    afficher(<Footer />, "/cm/epreuves")

    expect(screen.queryByText("512")).not.toBeInTheDocument()
    expect(screen.queryByText(/cours et fiches/)).not.toBeInTheDocument()
  })

  it("laisse « À propos » et le centre d'aide lisibles sans ouvrir de tiroir", () => {
    afficher(<Footer />, "/cm/epreuves")

    for (const nom of ["À propos", "Centre d'aide"]) {
      expect(screen.getByRole("link", { name: nom }).closest("details")).toBeNull()
    }
  })
})

describe("Footer : pas d'invitation sur l'accueil d'un visiteur", () => {
  const connecte = { isAuthenticated: auth.isAuthenticated, user: auth.user }
  afterEach(() => {
    auth.isAuthenticated = connecte.isAuthenticated
    auth.user = connecte.user
  })

  it("la vitrine se termine déjà par son appel : le pied de page ne le répète pas", () => {
    auth.isAuthenticated = false
    auth.user = null
    afficher(<Footer />, "/cm")

    expect(screen.getByRole("contentinfo")).toBeInTheDocument()
    expect(screen.queryByText("Créer mon compte")).not.toBeInTheDocument()
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
