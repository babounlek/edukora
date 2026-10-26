import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getEspaceRevendeur = vi.hoisted(() => vi.fn())
const listVentesRevendeur = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true, isLoading: false, user: { id: 1 } }))

vi.mock("@/api/endpoints", () => ({ getEspaceRevendeur, listVentesRevendeur }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { ApiError } from "@/api/client"
import type { EspaceRevendeur, VenteRevendeur } from "@/api/types"
import { EspaceRevendeurPage } from "./EspaceRevendeurPage"

const espace = (surcharges: Partial<EspaceRevendeur> = {}): EspaceRevendeur => ({
  nom_affiche: "Marie Tutorat",
  type: "REPETITEUR",
  code: "DEMO42",
  statut: "ACTIF",
  taux_base_pct: 14,
  palier: null,
  ventes_du_mois: 3,
  nb_clients: 5,
  montants: { en_attente: 2100, acquise: 4200, retenue: 0, payee: 10500 },
  ...surcharges,
})

const vente = (id: number, surcharges: Partial<VenteRevendeur> = {}): VenteRevendeur => ({
  id,
  created_at: "2026-10-20T10:00:00Z",
  client: "A. N. ••3456",
  plan: "Jusqu'à l'examen",
  base_fcfa: 15000,
  taux_pct: 14,
  montant_fcfa: 2100,
  etat: "EN_ATTENTE",
  ...surcharges,
})

function rendre() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <EspaceRevendeurPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getEspaceRevendeur.mockReset()
  listVentesRevendeur.mockReset()
  auth.isAuthenticated = true
})

describe("EspaceRevendeurPage", () => {
  it("montre le code, le lien, les montants par état et les ventes", async () => {
    getEspaceRevendeur.mockResolvedValue(espace())
    listVentesRevendeur.mockResolvedValue({
      count: 2, next: null, previous: null,
      results: [vente(1), vente(2, { etat: "RETENUE", client: "B. ••1111" })],
    })

    rendre()

    expect(await screen.findByText("DEMO42")).toBeInTheDocument()
    expect(screen.getByText(`${window.location.origin}/?rev=DEMO42`)).toBeInTheDocument()
    expect(screen.getByText("4 200")).toBeInTheDocument()
    expect(screen.getByText("10 500")).toBeInTheDocument()
    expect(await screen.findByText("A. N. ••3456")).toBeInTheDocument()
    expect(screen.getByText("Retenue")).toBeInTheDocument()
  })

  it("annonce le palier d'un commercial", async () => {
    getEspaceRevendeur.mockResolvedValue(espace({ type: "COMMERCIAL", palier: { seuil: 30, taux_pct: 17 } }))
    listVentesRevendeur.mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    rendre()

    expect(await screen.findByText(/Au-delà de 30 ventes/)).toHaveTextContent("17 %")
  })

  it("prévient quand le compte est suspendu", async () => {
    getEspaceRevendeur.mockResolvedValue(espace({ statut: "SUSPENDU" }))
    listVentesRevendeur.mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    rendre()

    expect(await screen.findByRole("status")).toHaveTextContent(/suspendu/i)
  })

  it("explique qu'il n'y a pas encore de vente", async () => {
    getEspaceRevendeur.mockResolvedValue(espace())
    listVentesRevendeur.mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    rendre()

    expect(await screen.findByText("Aucune vente pour l'instant.")).toBeInTheDocument()
  })

  it("charge la page suivante à la demande", async () => {
    getEspaceRevendeur.mockResolvedValue(espace())
    listVentesRevendeur
      .mockResolvedValueOnce({ count: 2, next: "http://x/?page=2", previous: null, results: [vente(1)] })
      .mockResolvedValueOnce({ count: 2, next: null, previous: null, results: [vente(2, { client: "C. ••9999" })] })
    const user = userEvent.setup()

    rendre()
    await user.click(await screen.findByRole("button", { name: /voir plus/i }))

    expect(await screen.findByText("C. ••9999")).toBeInTheDocument()
    expect(listVentesRevendeur).toHaveBeenLastCalledWith(2, expect.anything())
  })

  it("dit qu'un compte ordinaire n'est pas revendeur", async () => {
    getEspaceRevendeur.mockRejectedValue(new ApiError(404, { code: "pas_revendeur" }))

    rendre()

    expect(await screen.findByText("Cette page est réservée aux revendeurs Edukora.")).toBeInTheDocument()
    expect(listVentesRevendeur).not.toHaveBeenCalled()
  })
})
