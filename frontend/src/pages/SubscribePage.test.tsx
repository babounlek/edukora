import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMyInscriptionsInedites = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: { phone_number: "677000000" },
}))

vi.mock("@/api/endpoints", () => ({
  checkPaymentStatus: vi.fn(),
  initiatePayment: vi.fn(),
  listCursus: vi.fn(() => Promise.resolve([])),
  listPlans: vi.fn(() => Promise.resolve([])),
  listProfils: vi.fn(() => Promise.resolve([])),
  listMyInscriptionsInedites,
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/sentry", () => ({ Sentry: { captureException: vi.fn() } }))
vi.mock("@/components/BilanDePeriode", () => ({ BilanDePeriode: () => null }))
vi.mock("@/components/ManualPaymentPanel", () => ({ ManualPaymentPanel: () => null }))

import { SubscribePage } from "./SubscribePage"

const RETOUR = "/cm/epreuves-inedites/maths-bac-d"

function inscription(cursusId: number, actif = true) {
  return { id: 1, cursus: { id: cursusId }, profil: { id: 1, prenom: "Awa" }, expires_at: "2027-06-01T00:00:00Z", is_active: actif }
}

function afficher(url: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]}>
        <Routes>
          <Route path="/abonnement" element={<SubscribePage />} />
          <Route path="/cm/epreuves-inedites/:id" element={<p>Fiche de l'épreuve</p>} />
          <Route path="/connexion" element={<p>Page de connexion</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  listMyInscriptionsInedites.mockReset()
  auth.isAuthenticated = true
  auth.isLoading = false
})

describe("SubscribePage : retour vers l'épreuve qui a motivé l'achat", () => {
  it("ramène un abonné déjà actif sur ce cursus à son épreuve, sans lui montrer d'offre", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(4)])
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent(RETOUR)}`)

    expect(await screen.findByText("Fiche de l'épreuve")).toBeInTheDocument()
  })

  it("reste sur l'offre quand l'abonnement actif porte sur un autre cursus ou est échu", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(9), inscription(4, false)])
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent(RETOUR)}`)

    await waitFor(() => expect(listMyInscriptionsInedites).toHaveBeenCalled())
    expect(screen.queryByText("Fiche de l'épreuve")).not.toBeInTheDocument()
  })

  it("ne redirige jamais sans `retour` : un abonné qui vient prolonger doit voir l'offre", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(4)])
    afficher("/abonnement?cursus=4&duree=examen")

    await screen.findByText(/Paiement sécurisé/)
    expect(listMyInscriptionsInedites).not.toHaveBeenCalled()
    expect(screen.queryByText("Fiche de l'épreuve")).not.toBeInTheDocument()
  })

  it("refuse un `retour` qui sort du site", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(4)])
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent("https://evil.example/x")}`)

    await screen.findByText(/Paiement sécurisé/)
    expect(listMyInscriptionsInedites).not.toHaveBeenCalled()
  })

  it("renvoie un visiteur vers la connexion", async () => {
    auth.isAuthenticated = false
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent(RETOUR)}`)

    expect(await screen.findByText("Page de connexion")).toBeInTheDocument()
    expect(listMyInscriptionsInedites).not.toHaveBeenCalled()
  })
})
