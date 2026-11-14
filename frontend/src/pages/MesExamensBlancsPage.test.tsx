import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMySimulations = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true, isLoading: false, user: { id: 1, cursus_prepare: { id: 14 } } }))
vi.mock("@/api/endpoints", () => ({ listMySimulations }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { MesExamensBlancsPage } from "./MesExamensBlancsPage"

const copie = (surcharges: Record<string, unknown>) => ({
  id: 1, epreuve: 5, epreuve_titre: "Maths BEPC 2025", epreuve_slug: "maths-bepc-2025", matiere: "Mathématiques", pays: "cm",
  started_at: "2026-11-01T08:00:00Z", submitted_at: "2026-11-01T10:00:00Z", chrono_en_cours: false,
  note_obtenue: 10, bareme_snapshot: 20, score_obtenu: 50, ...surcharges,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/examens-blancs"]}>
        <Routes>
          <Route path="/examens-blancs" element={<MesExamensBlancsPage />} />
          <Route path="/connexion" element={<p>Écran de connexion</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  auth.isAuthenticated = true
})

describe("MesExamensBlancsPage", () => {
  it("met la copie dont le chrono tourne en tête, avec de quoi la reprendre", async () => {
    listMySimulations.mockResolvedValue([
      copie({ id: 9, epreuve_titre: "Physique BEPC 2024", submitted_at: null, note_obtenue: null, bareme_snapshot: null, chrono_en_cours: true }),
    ])
    afficher()

    const lien = await screen.findByRole("link", { name: /Physique BEPC 2024/ })
    expect(lien).toHaveAttribute("href", "/simulation/9")
    expect(lien).toHaveTextContent("Reprendre")
    expect(screen.queryByText("Aucun examen blanc pour l'instant")).not.toBeInTheDocument()
  })

  it("liste les notes rendues, la meilleure et l'évolution depuis le premier", async () => {
    listMySimulations.mockResolvedValue([
      copie({ id: 3, note_obtenue: 15, submitted_at: "2026-11-10T10:00:00Z" }),
      copie({ id: 2, note_obtenue: 12, submitted_at: "2026-11-05T10:00:00Z" }),
      copie({ id: 1, note_obtenue: 8, submitted_at: "2026-11-01T10:00:00Z" }),
    ])
    afficher()

    expect(await screen.findByText("75 %", { selector: "p" })).toBeInTheDocument()
    expect(screen.getByText("3 examens blancs passés")).toBeInTheDocument()
    expect(screen.getByText(/\+35/)).toBeInTheDocument()
    expect(screen.getAllByRole("link", { name: /Maths BEPC 2025/ })[0]).toHaveAttribute("href", "/simulation/3/resultat")
  })

  it("une seule copie rendue : pas de tendance inventée", async () => {
    listMySimulations.mockResolvedValue([copie({})])
    afficher()

    expect(await screen.findByText("1 examen blanc passé")).toBeInTheDocument()
    expect(screen.queryByText(/^\+/)).not.toBeInTheDocument()
  })

  it("sans copie, explique comment en passer une et mène aux annales", async () => {
    listMySimulations.mockResolvedValue([])
    afficher()

    expect(await screen.findByText("Aucun examen blanc pour l'instant")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Choisir une annale/ })).toHaveAttribute("href", "/cm/epreuves")
  })

  it("une panne n'est pas « aucun examen blanc »", async () => {
    listMySimulations.mockRejectedValue(new Error("réseau"))
    afficher()

    expect(await screen.findByRole("alert")).toBeInTheDocument()
    expect(screen.queryByText("Aucun examen blanc pour l'instant")).not.toBeInTheDocument()
  })

  it("renvoie un visiteur à la connexion", () => {
    auth.isAuthenticated = false
    afficher()

    expect(screen.getByText("Écran de connexion")).toBeInTheDocument()
  })
})
