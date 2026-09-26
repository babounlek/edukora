import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getPaiementAReprendre = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true }))

vi.mock("@/api/endpoints", () => ({ getPaiementAReprendre }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))

import { BandeauReprisePaiement } from "./BandeauReprisePaiement"

function afficher(chemin = "/cm") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[chemin]}>
        <BandeauReprisePaiement />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getPaiementAReprendre.mockReset()
  auth.isAuthenticated = true
  sessionStorage.clear()
})

describe("BandeauReprisePaiement", () => {
  it("propose de reprendre un paiement qui n'a pas abouti", async () => {
    getPaiementAReprendre.mockResolvedValue({ a_reprendre: true, montant: 9000, cursus_id: 4, statut: "FAILED" })
    afficher()

    expect(await screen.findByText(/n'a pas abouti/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Reprendre" })).toHaveAttribute("href", "/abonnement?cursus=4")
  })

  it("distingue un paiement jamais confirmé d'un paiement échoué", async () => {
    getPaiementAReprendre.mockResolvedValue({ a_reprendre: true, montant: 9000, cursus_id: 4, statut: "PENDING" })
    afficher()
    expect(await screen.findByText(/n'a pas été confirmé/)).toBeInTheDocument()
  })

  it("ne dit rien quand il n'y a rien à reprendre", async () => {
    getPaiementAReprendre.mockResolvedValue({ a_reprendre: false })
    const { container } = afficher()
    await vi.waitFor(() => expect(getPaiementAReprendre).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("ne s'interpose ni sur la page de paiement ni pendant une lecture", async () => {
    getPaiementAReprendre.mockResolvedValue({ a_reprendre: true, montant: 9000, cursus_id: 4, statut: "FAILED" })
    const { container } = afficher("/abonnement")
    await vi.waitFor(() => expect(getPaiementAReprendre).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("n'appelle même pas l'API pour un visiteur non connecté", () => {
    auth.isAuthenticated = false
    const { container } = afficher()
    expect(getPaiementAReprendre).not.toHaveBeenCalled()
    expect(container).toBeEmptyDOMElement()
  })

  it("se masque pour la visite", async () => {
    getPaiementAReprendre.mockResolvedValue({ a_reprendre: true, montant: 9000, cursus_id: 4, statut: "FAILED" })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: "Masquer ce message" }))

    expect(screen.queryByText(/n'a pas abouti/)).not.toBeInTheDocument()
  })
})
