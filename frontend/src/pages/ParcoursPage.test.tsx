import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMySubscriptions = vi.hoisted(() => vi.fn())
const getResumeParcours = vi.hoisted(() => vi.fn())

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null }
const BAC_C = { id: 20, examen: "BAC", examen_display: "BAC", series: { id: 3, code: "C", label: "Série C" } }

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: {
    id: 1,
    profil_actif: { id: 9 },
    cursus_prepare: { id: 14, examen_display: "BEPC", series: null } as unknown,
  },
}))

vi.mock("@/api/endpoints", () => ({ listMySubscriptions, getResumeParcours }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { ParcoursPage } from "./ParcoursPage"

const abonnement = (id: number, cursus: typeof BEPC | typeof BAC_C, profilId = 9) => ({
  id,
  cursus,
  profil: { id: profilId },
  is_active: true,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const arbre = () => (
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/parcours"]}>
        <ParcoursPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
  const rendu = render(arbre())
  return { ...rendu, rerenderPage: () => rendu.rerender(arbre()) }
}

describe("ParcoursPage (Ma progression) - pastilles d'examen", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    auth.user.cursus_prepare = { id: 14, examen_display: "BEPC", series: null }
    listMySubscriptions.mockResolvedValue([
      abonnement(253, BAC_C),
      abonnement(258, BEPC),
      abonnement(260, BAC_C, 15), // autre profil du compte : jamais proposé
    ])
    getResumeParcours.mockResolvedValue([])
  })

  it("ne montre que l'examen préparé quand le profil a payé BEPC et BAC C", async () => {
    afficher()
    await waitFor(() => expect(getResumeParcours).toHaveBeenCalledWith(14))
    expect(await screen.findByText("BEPC")).toBeTruthy()
    expect(screen.queryByText("BAC C")).toBeNull()
    expect(getResumeParcours).not.toHaveBeenCalledWith(20)
  })

  it("suit l'examen préparé quand l'élève le change depuis le bandeau", async () => {
    const { rerenderPage } = afficher()
    expect(await screen.findByText("BEPC")).toBeTruthy()

    auth.user.cursus_prepare = { id: 20, examen_display: "BAC", series: { id: 3, code: "C", label: "Série C" } }
    rerenderPage()

    expect(await screen.findByText("BAC C")).toBeTruthy()
    expect(screen.queryByText("BEPC")).toBeNull()
    await waitFor(() => expect(getResumeParcours).toHaveBeenLastCalledWith(20))
  })

  it("garde le sélecteur quand aucun examen n'est préparé", async () => {
    auth.user.cursus_prepare = null
    afficher()
    expect(await screen.findByRole("button", { name: "BEPC" })).toBeTruthy()
    expect(screen.getByRole("button", { name: "BAC C" })).toBeTruthy()
  })
})
