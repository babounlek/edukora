import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getReussites = vi.hoisted(() => vi.fn())
const jouerRetour = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getReussites }))
vi.mock("@/lib/retours", () => ({ jouerRetour }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ user: { profil_actif: { id: 7 } } }) }))

import { nouveauxJalons } from "@/lib/jalonsVus"
import { JalonsAtteints } from "./JalonsAtteints"

const jalon = (code: string, obtenu: boolean) => ({ code, famille: "quiz", cible: 1, valeur: obtenu ? 1 : 0, obtenu })
const reussites = (...obtenus: string[]) => ({
  niveau: { rang: 1, xp_total: 0, seuil: 0, seuil_suivant: 60 },
  jalons: ["premier_quiz", "bonnes_10", "sans_faute_1"].map((code) => jalon(code, obtenus.includes(code))),
  prochain: null,
  serie: { actuelle: 0, record: 0, repos_pris: false },
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter><JalonsAtteints /></MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("JalonsAtteints", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it("fête le jalon que le quiz vient d'ouvrir, avec son son", async () => {
    nouveauxJalons(7, ["premier_quiz"]) // déjà montré avant ce quiz
    getReussites.mockResolvedValue(reussites("premier_quiz", "sans_faute_1"))
    afficher()

    expect(await screen.findByText("Premier quiz sans faute")).toBeTruthy()
    expect(screen.getByText("Jalon atteint")).toBeTruthy()
    expect(screen.queryByText("Première réponse")).toBeNull()
    expect(jouerRetour).toHaveBeenCalledWith("palier")
    expect(screen.getByRole("link", { name: "Tous mes jalons" }).getAttribute("href")).toBe("/parcours")
  })

  it("n'affiche rien quand le quiz n'a ouvert aucun jalon", async () => {
    nouveauxJalons(7, ["premier_quiz"])
    getReussites.mockResolvedValue(reussites("premier_quiz"))
    const { container } = afficher()

    await waitFor(() => expect(getReussites).toHaveBeenCalled())
    await waitFor(() => expect(container.querySelector("ul")).toBeNull())
    expect(jouerRetour).not.toHaveBeenCalled()
  })
})
