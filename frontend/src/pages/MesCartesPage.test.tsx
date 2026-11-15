import { fireEvent, render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const api = vi.hoisted(() => ({ getPaquetsCartes: vi.fn(), getCartesDues: vi.fn(), getCartesCours: vi.fn(), noterCarte: vi.fn() }))
const auth = vi.hoisted(() => ({ isAuthenticated: true, isLoading: false }))
vi.mock("@/api/endpoints", () => api)
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { MesCartesPage } from "./MesCartesPage"

const paquet = (surcharges: Record<string, unknown> = {}) => ({
  slug: "derivees", titre: "Dérivées", total: 4, revues: 3, dues: 0, prochaine: "2026-12-01", ...surcharges,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cartes"]}>
        <Routes>
          <Route path="/cartes" element={<MesCartesPage />} />
          <Route path="/connexion" element={<p>Écran de connexion</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  auth.isAuthenticated = true
  api.getCartesDues.mockResolvedValue({ total: 0, cartes: [] })
  api.getCartesCours.mockResolvedValue({ cartes: [] })
})

describe("MesCartesPage", () => {
  it("liste un paquet par cours, avec ce qui reste à revoir et le lien du cours", async () => {
    api.getPaquetsCartes.mockResolvedValue({ paquets: [paquet({ dues: 2 }), paquet({ slug: "limites", titre: "Limites" })] })
    afficher()

    expect(await screen.findByText("Dérivées")).toBeInTheDocument()
    expect(screen.getByText("2 cartes à revoir")).toBeInTheDocument()
    expect(screen.getByText("À jour")).toBeInTheDocument()
    expect(screen.getAllByRole("link", { name: "Relire le cours" })[0]).toHaveAttribute("href", "/cours/derivees/lire")
  })

  it("dit quand rien n'est à revoir aujourd'hui", async () => {
    api.getPaquetsCartes.mockResolvedValue({ paquets: [paquet()] })
    afficher()

    expect(await screen.findByText(/Aucune carte à revoir aujourd'hui/)).toBeInTheDocument()
  })

  it("« Réviser » ouvre les cartes du cours dans le paquet", async () => {
    api.getPaquetsCartes.mockResolvedValue({ paquets: [paquet({ dues: 1 })] })
    afficher()

    fireEvent.click(await screen.findByRole("button", { name: "Réviser" }))
    expect(api.getCartesCours).toHaveBeenCalledWith("derivees", expect.anything())
  })

  it("sans paquet, explique où trouver les cartes et mène aux cours", async () => {
    api.getPaquetsCartes.mockResolvedValue({ paquets: [] })
    afficher()

    expect(await screen.findByText("Pas encore de carte")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Choisir un cours/ })).toBeInTheDocument()
  })

  it("une panne n'est pas « pas encore de carte »", async () => {
    api.getPaquetsCartes.mockRejectedValue(new Error("réseau"))
    afficher()

    expect(await screen.findByRole("alert")).toBeInTheDocument()
    expect(screen.queryByText("Pas encore de carte")).not.toBeInTheDocument()
  })

  it("montre à un visiteur pourquoi se connecter, avec un lien vers la connexion", () => {
    auth.isAuthenticated = false
    afficher()

    // Un visiteur voit ce que la page contient et pourquoi un compte est nécessaire, puis un lien vers la connexion (plus de redirection sèche).
    expect(screen.getByRole("link", { name: "Se connecter" })).toHaveAttribute("href", "/connexion")
  })
})
