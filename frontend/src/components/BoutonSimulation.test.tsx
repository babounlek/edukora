import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"

const startSimulation = vi.hoisted(() => vi.fn())
const listMySimulations = vi.hoisted(() => vi.fn())
const toast = vi.hoisted(() => ({ error: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ startSimulation, listMySimulations }))
vi.mock("sonner", () => ({ toast }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import { BoutonSimulation } from "./BoutonSimulation"

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cm/epreuves/maths"]}>
        <Routes>
          <Route path="/cm/epreuves/maths" element={<BoutonSimulation epreuveId={42} />} />
          <Route path="/simulation/:id" element={<p>Écran de la simulation</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

const simulation = (surcharges: Record<string, unknown>) => ({
  id: 1, epreuve: 42, epreuve_titre: "Maths", started_at: "2026-11-01T08:00:00Z", submitted_at: "2026-11-01T10:00:00Z",
  note_obtenue: 12.5, bareme_snapshot: 20, score_obtenu: 63, ...surcharges,
})

beforeEach(() => {
  startSimulation.mockReset()
  listMySimulations.mockReset()
  listMySimulations.mockResolvedValue([])
  toast.error.mockReset()
})

describe("BoutonSimulation", () => {
  it("ouvre la simulation puis conduit à son briefing", async () => {
    startSimulation.mockResolvedValue({ id: 9 })
    afficher()

    await userEvent.click(screen.getByRole("button", { name: /Passer en conditions d'examen/ }))

    await waitFor(() => expect(startSimulation).toHaveBeenCalledWith(42))
    expect(await screen.findByText("Écran de la simulation")).toBeInTheDocument()
  })

  it("dit pourquoi la simulation ne peut pas démarrer", async () => {
    startSimulation.mockRejectedValue(new ApiError(403, { error: "Abonnement requis pour simuler cette épreuve." }))
    afficher()

    await userEvent.click(screen.getByRole("button", { name: /Passer en conditions d'examen/ }))

    await waitFor(() => expect(toast.error).toHaveBeenCalledWith("Abonnement requis pour simuler cette épreuve."))
    expect(screen.getByRole("button", { name: /Passer en conditions d'examen/ })).toBeEnabled()
  })

  it("rappelle la dernière note obtenue sur cette épreuve, pas celle d'une autre ni d'une copie non rendue", async () => {
    listMySimulations.mockResolvedValue([
      simulation({ id: 5, submitted_at: null, note_obtenue: null, bareme_snapshot: null }),
      simulation({ id: 4, epreuve: 7, note_obtenue: 18 }),
      simulation({ id: 3, note_obtenue: 12.5 }),
      simulation({ id: 2, note_obtenue: 8 }),
    ])
    afficher()

    expect(await screen.findByText("Dernière note : 12,5 / 20")).toBeInTheDocument()
  })

  it("reste utilisable, sans pastille, quand la liste des simulations échoue", async () => {
    listMySimulations.mockRejectedValue(new Error("réseau"))
    startSimulation.mockResolvedValue({ id: 9 })
    afficher()

    await userEvent.click(screen.getByRole("button", { name: /Passer en conditions d'examen/ }))

    expect(await screen.findByText("Écran de la simulation")).toBeInTheDocument()
    expect(screen.queryByText(/Dernière note/)).not.toBeInTheDocument()
  })
})
