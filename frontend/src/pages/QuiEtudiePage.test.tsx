import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listProfils = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  login: vi.fn(),
  user: { id: 1, pin_parent_actif: false } as Record<string, unknown>,
}))

vi.mock("@/api/endpoints", () => ({ listProfils }))
vi.mock("@/lib/changerProfilActif", () => ({ activerProfilProtege: vi.fn() }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "CM" }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { QuiEtudiePage } from "./QuiEtudiePage"

const PROFILS = [
  { id: 1, prenom: "Aînée", pin_actif: false },
  { id: 2, prenom: "Cadet", pin_actif: false },
]

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/qui-etudie"]}>
      <QuiEtudiePage />
    </MemoryRouter>,
  )
}

describe("QuiEtudiePage - rappel du code parent", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    auth.user = { id: 1, pin_parent_actif: false }
    listProfils.mockResolvedValue(PROFILS)
  })

  it("rappelle qu'un code parent protège les autres enfants, avec un lien vers la sécurité de Mes accès", async () => {
    afficher()

    expect(await screen.findByText(/Chaque enfant peut voir les abonnements des autres/)).toBeTruthy()
    const lien = screen.getByRole("link", { name: "Protéger avec un code parent" })
    expect(lien.getAttribute("href")).toBe("/mes-acces#securite")
  })

  it("« Plus tard » masque le rappel et s'en souvient", async () => {
    const { unmount } = afficher()
    fireEvent.click(await screen.findByRole("button", { name: "Plus tard" }))
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
    unmount()

    afficher()
    await screen.findByText("Cadet")
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
  })

  it("n'affiche rien quand un code parent est déjà défini", async () => {
    auth.user = { id: 1, pin_parent_actif: true }
    afficher()

    await screen.findByText("Cadet")
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
  })

  it("n'affiche rien quand un enfant a déjà son propre code", async () => {
    listProfils.mockResolvedValue([{ ...PROFILS[0], pin_actif: true }, PROFILS[1]])
    afficher()

    await waitFor(() => expect(screen.getByText("Cadet")).toBeTruthy())
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
  })
})
