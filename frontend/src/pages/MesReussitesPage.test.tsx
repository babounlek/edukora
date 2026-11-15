import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getReussites = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true, isLoading: false, user: { id: 1 } }))
vi.mock("@/api/endpoints", () => ({ getReussites }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { MesReussitesPage } from "./MesReussitesPage"

const jalon = (code: string, famille: string, cible: number, valeur: number) => ({ code, famille, cible, valeur, obtenu: valeur >= cible })
const donnees = {
  niveau: { rang: 6, xp_total: 1700, seuil: 1600, seuil_suivant: 2400 },
  jalons: [
    jalon("premier_quiz", "quiz", 1, 1),
    jalon("bonnes_100", "quiz", 100, 40),
    jalon("themes_solides_10", "themes", 10, 0),
    jalon("premier_examen_blanc", "examens", 1, 0),
    jalon("serie_7", "serie", 7, 7),
  ],
  prochain: "bonnes_100",
  serie: { actuelle: 3, record: 9, repos_pris: true },
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/reussites"]}>
        <Routes>
          <Route path="/reussites" element={<MesReussitesPage />} />
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

describe("MesReussitesPage", () => {
  it("montre le niveau, le record de série et les jalons, atteints ou non", async () => {
    getReussites.mockResolvedValue(donnees)
    afficher()

    expect(await screen.findByText("Niveau 6 · Stratège")).toBeInTheDocument()
    expect(screen.getByText("Record : 9 jours de suite")).toBeInTheDocument()
    expect(screen.getByText("40 sur 100 · Prochain jalon")).toBeInTheDocument()
    expect(screen.getAllByText("Atteint")).toHaveLength(2)
  })

  it("une panne n'est pas « aucun jalon »", async () => {
    getReussites.mockRejectedValue(new Error("réseau"))
    afficher()

    expect(await screen.findByRole("alert")).toBeInTheDocument()
  })

  it("renvoie un visiteur à la connexion", () => {
    auth.isAuthenticated = false
    afficher()

    expect(screen.getByText("Écran de connexion")).toBeInTheDocument()
  })
})
