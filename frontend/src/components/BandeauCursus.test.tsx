import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { auth, listCursus } = vi.hoisted(() => ({
  auth: { isAuthenticated: false, user: null as unknown },
  listCursus: vi.fn(),
}))
vi.mock("@/api/endpoints", () => ({ listCursus }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/changerCursusPrepare", () => ({ useChangerCursusPrepare: () => ({ mutate: vi.fn(), isPending: false }) }))
vi.mock("@/components/InviteAutreSousSysteme", () => ({ InviteAutreSousSysteme: () => null }))

import { BandeauCursus } from "./BandeauCursus"

const CURSUS = [{ id: 1, examen: "BEPC", examen_display: "BEPC", series: null, langue: "fr", country: { code: "CM" } }]

function afficher() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={["/cm/epreuves"]}>
        <BandeauCursus />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("BandeauCursus - promesse selon l'état de connexion", () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    listCursus.mockResolvedValue(CURSUS)
  })

  it("un visiteur n'est pas promis une séance du jour : seulement des listes adaptées à son examen", async () => {
    auth.isAuthenticated = false
    auth.user = null
    afficher()
    await waitFor(() => expect(screen.getByRole("region")).toBeTruthy())
    const bandeau = screen.getByRole("region").textContent ?? ""
    expect(bandeau).toContain("les épreuves et cours qui te concernent")
    expect(bandeau).not.toContain("séance du jour")
  })

  it("un élève connecté sans examen est bien promis sa séance du jour", async () => {
    auth.isAuthenticated = true
    auth.user = { id: 1, cursus_prepare: null }
    afficher()
    await waitFor(() => expect(screen.getByRole("region")).toBeTruthy())
    expect(screen.getByRole("region").textContent).toContain("séance du jour")
  })
})

describe("BandeauCursus - place réservée pendant le chargement (décalage de mise en page)", () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    auth.isAuthenticated = false
    auth.user = null
  })

  it("garde sa place tant que la liste des cursus n'est pas arrivée, puis montre le bandeau", async () => {
    let repondre: (liste: unknown) => void = () => {}
    listCursus.mockReturnValue(new Promise((resolve) => { repondre = resolve }))
    afficher()
    // Pas encore de bandeau, mais une réserve d'espace (invisible pour les lecteurs d'écran).
    expect(screen.queryByRole("region")).toBeNull()
    expect(screen.queryByTestId("bandeau-cursus-reserve")).not.toBeNull()
    repondre(CURSUS)
    await waitFor(() => expect(screen.getByRole("region")).toBeTruthy())
    expect(screen.queryByTestId("bandeau-cursus-reserve")).toBeNull()
  })

  it("rend la place quand la liste est vide : pas de trou dans la page", async () => {
    listCursus.mockResolvedValue([])
    afficher()
    await waitFor(() => expect(screen.queryByTestId("bandeau-cursus-reserve")).toBeNull())
    expect(screen.queryByRole("region")).toBeNull()
  })
})
