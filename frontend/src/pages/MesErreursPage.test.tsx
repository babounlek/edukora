import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"

const getErreurs = vi.hoisted(() => vi.fn())
const refaireErreurs = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: { id: 1, cursus_prepare: { id: 14 } as { id: number } | null },
}))

vi.mock("@/api/endpoints", () => ({ getErreurs, refaireErreurs }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { MesErreursPage } from "./MesErreursPage"

const banque = {
  total: 14,
  paquet: 10,
  plus_ancienne: "2026-11-02",
  matieres: [
    {
      subject_id: 10, subject_code: "MATHS", subject_label: "Mathématiques", nb: 11, themes_total: 5,
      themes: [
        { theme_id: 1, theme: "factorisation", nb: 4 },
        { theme_id: 2, theme: "radicaux", nb: 3 },
        { theme_id: 3, theme: "théorème de Thalès", nb: 1 },
      ],
    },
    {
      subject_id: 12, subject_code: "SVT", subject_label: "Sciences de la Vie et de la Terre", nb: 3, themes_total: 1,
      themes: [{ theme_id: 9, theme: "digestion", nb: 3 }],
    },
  ],
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/erreurs"]}>
        <Routes>
          <Route path="/erreurs" element={<MesErreursPage />} />
          <Route path="/quiz/session/:id" element={<p>Quiz des erreurs</p>} />
          <Route path="/connexion" element={<p>Écran de connexion</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  auth.isAuthenticated = true
  auth.user.cursus_prepare = { id: 14 }
  getErreurs.mockResolvedValue(banque)
})

describe("MesErreursPage", () => {
  it("dit combien de questions sont à refaire, par matière, avec les thèmes où elles se concentrent", async () => {
    afficher()

    expect(await screen.findByText("14 questions à refaire")).toBeInTheDocument()
    expect(getErreurs).toHaveBeenCalledWith(14, expect.anything())
    expect(screen.getByText("Mathématiques")).toBeInTheDocument()
    expect(screen.getByText("11 erreurs")).toBeInTheDocument()
    expect(screen.getByText(/Factorisation/)).toBeInTheDocument()
    expect(screen.getByText("+ 2 autres thèmes")).toBeInTheDocument()
    expect(screen.getByText("3 erreurs")).toBeInTheDocument()
  })

  it("refaire ouvre un quiz du paquet annoncé et y conduit", async () => {
    refaireErreurs.mockResolvedValue({ id: 77 })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: "Refaire 10 erreurs" }))

    await waitFor(() => expect(refaireErreurs).toHaveBeenCalledWith({ cursus: 14 }))
    expect(await screen.findByText("Quiz des erreurs")).toBeInTheDocument()
  })

  it("refaire une seule matière vise cette matière", async () => {
    refaireErreurs.mockResolvedValue({ id: 78 })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: "Refaire mes erreurs en Mathématiques" }))

    await waitFor(() => expect(refaireErreurs).toHaveBeenCalledWith({ cursus: 14, subject: 10 }))
  })

  it("sans abonnement, le refus du serveur mène aux prix et le bouton reste utilisable", async () => {
    refaireErreurs.mockRejectedValue(new ApiError(403, { error: "Abonnement requis pour ce cursus." }))
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: "Refaire 10 erreurs" }))

    expect(await screen.findByRole("alert")).toHaveTextContent("Abonnement requis pour ce cursus.")
    expect(screen.getByRole("link", { name: "Voir les prix" })).toHaveAttribute("href", "/tarifs")
    expect(screen.getByRole("button", { name: "Refaire 10 erreurs" })).toBeEnabled()
  })

  it("sans erreur, le dit et propose un quiz", async () => {
    getErreurs.mockResolvedValue({ total: 0, paquet: 0, plus_ancienne: null, matieres: [] })
    afficher()

    expect(await screen.findByText("Aucune erreur en attente")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Faire un quiz/ })).toHaveAttribute("href", "/quiz")
    expect(screen.queryByRole("button", { name: /Refaire/ })).not.toBeInTheDocument()
  })

  it("une panne n'est pas « aucune erreur »", async () => {
    getErreurs.mockRejectedValue(new Error("réseau"))
    afficher()

    expect(await screen.findByRole("alert")).toBeInTheDocument()
    expect(screen.queryByText("Aucune erreur en attente")).not.toBeInTheDocument()
  })

  it("sans examen préparé, demande de le choisir sans interroger le serveur", () => {
    auth.user.cursus_prepare = null
    afficher()

    expect(screen.getByRole("link", { name: "Choisir mon cursus" })).toHaveAttribute("href", "/compte")
    expect(getErreurs).not.toHaveBeenCalled()
  })

  it("renvoie à la connexion un visiteur", () => {
    auth.isAuthenticated = false
    afficher()

    expect(screen.getByText("Écran de connexion")).toBeInTheDocument()
  })
})
