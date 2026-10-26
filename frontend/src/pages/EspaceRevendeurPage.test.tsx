import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getEspaceRevendeur = vi.hoisted(() => vi.fn())
const listVentesRevendeur = vi.hoisted(() => vi.fn())
const listVersementsRevendeur = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true, isLoading: false, user: { id: 1 } }))

vi.mock("@/api/endpoints", () => ({ getEspaceRevendeur, listVentesRevendeur, listVersementsRevendeur }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { ApiError } from "@/api/client"
import type { EspaceRevendeur, VenteRevendeur, VersementRevendeur } from "@/api/types"
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
  seuil_versement: 5000,
  reprises_en_cours: 0,
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

const versement = (id: number, surcharges: Partial<VersementRevendeur> = {}): VersementRevendeur => ({
  id,
  periode: "2026-09",
  montant_brut: 6300,
  montant_reprises: 0,
  montant_net: 6300,
  statut: "PAYE",
  operateur: "ORANGE",
  reference: "MP261026.A1",
  paye_le: "2026-10-05T09:00:00Z",
  ...surcharges,
})

const pasDeVersement = { count: 0, next: null, previous: null, results: [] }

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
  listVersementsRevendeur.mockReset()
  listVersementsRevendeur.mockResolvedValue(pasDeVersement)
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

  it("montre les versements, la référence Mobile Money et le détail des reprises", async () => {
    getEspaceRevendeur.mockResolvedValue(espace())
    listVentesRevendeur.mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    listVersementsRevendeur.mockResolvedValue({
      count: 2, next: null, previous: null,
      results: [
        versement(2, { statut: "PREPARE", reference: "", paye_le: null, periode: "2026-10" }),
        versement(1, { montant_brut: 6300, montant_reprises: 2100, montant_net: 4200 }),
      ],
    })

    rendre()

    expect(await screen.findByText(/MP261026.A1/)).toBeInTheDocument()
    expect(screen.getByText("Versé")).toBeInTheDocument()
    expect(screen.getByText("En préparation")).toBeInTheDocument()
    expect(screen.getByText("6 300 FCFA de commissions − 2 100 FCFA de reprises")).toBeInTheDocument()
  })

  it("explique le versement mensuel et son seuil quand il n'y en a pas encore", async () => {
    getEspaceRevendeur.mockResolvedValue(espace())
    listVentesRevendeur.mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    rendre()

    expect(await screen.findByText("Aucun versement pour l'instant.")).toBeInTheDocument()
    expect(screen.getByText(/dès 5 000 FCFA/)).toBeInTheDocument()
  })

  it("prévient qu'une reprise sera déduite du prochain versement", async () => {
    getEspaceRevendeur.mockResolvedValue(espace({ reprises_en_cours: 2100 }))
    listVentesRevendeur.mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    rendre()

    expect(await screen.findByText(/2 100 FCFA seront déduits/)).toBeInTheDocument()
  })

  it("propose le guide pour accompagner un parent, avec le rappel sur ses données", async () => {
    getEspaceRevendeur.mockResolvedValue(espace())
    listVentesRevendeur.mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    rendre()

    expect(await screen.findByText("Guider un parent, pas à pas")).toBeInTheDocument()
    expect(screen.getByText(/vous l'avancez à vos risques|vous l'avancez à vos risques/i)).toBeInTheDocument()
    expect(screen.getByText(/ne conservez aucun de ses numéros/)).toBeInTheDocument()
  })
})
