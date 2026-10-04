import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMySubscriptions = vi.hoisted(() => vi.fn())
const getParcours = vi.hoisted(() => vi.fn())

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null, country: { code: "CM" } }
const BAC_C = { id: 20, examen: "BAC", examen_display: "BAC", series: { id: 3, code: "C", label: "Série C" }, country: { code: "CM" } }

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: {
    id: 1,
    profil_actif: { id: 9 },
    cursus_prepare: { id: 14 } as unknown,
  },
}))

vi.mock("@/api/endpoints", () => ({
  listMySubscriptions,
  getParcours,
  listSubjects: vi.fn(() => Promise.resolve([])),
  startQuizSession: vi.fn(),
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import { ParcoursSubjectPage } from "./ParcoursSubjectPage"

const abonnement = (id: number, cursus: typeof BEPC | typeof BAC_C, profilId = 9) => ({
  id,
  cursus,
  profil: { id: profilId },
  is_active: true,
})

function afficher(url: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const arbre = () => (
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]}>
        <Routes>
          <Route path="/parcours/:subjectId" element={<ParcoursSubjectPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
  const rendu = render(arbre())
  return { ...rendu, rerenderPage: () => rendu.rerender(arbre()) }
}

describe("ParcoursSubjectPage - pastilles d'examen", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    auth.user.cursus_prepare = { id: 14 }
    listMySubscriptions.mockResolvedValue([abonnement(253, BAC_C), abonnement(258, BEPC)])
    getParcours.mockResolvedValue([])
  })

  it("ne montre que l'examen préparé quand le profil a payé BEPC et BAC C", async () => {
    afficher("/parcours/5")
    await waitFor(() => expect(getParcours).toHaveBeenCalledWith(14, 5))
    expect(await screen.findByText("BEPC")).toBeTruthy()
    expect(screen.queryByText("BAC C")).toBeNull()
    expect(getParcours).not.toHaveBeenCalledWith(20, 5)
  })

  it("garde un lien direct ?cursus= vers l'autre examen", async () => {
    afficher("/parcours/5?cursus=20")
    await waitFor(() => expect(getParcours).toHaveBeenCalledWith(20, 5))
    expect(await screen.findByRole("button", { name: "BAC C" })).toBeTruthy()
  })

  it("quitte le cursus du lien direct quand l'élève change d'examen depuis le bandeau", async () => {
    const { rerenderPage } = afficher("/parcours/5?cursus=14")
    await waitFor(() => expect(getParcours).toHaveBeenCalledWith(14, 5))

    auth.user.cursus_prepare = { id: 20 }
    rerenderPage()

    await waitFor(() => expect(getParcours).toHaveBeenLastCalledWith(20, 5))
    expect(screen.queryByText("BEPC")).toBeNull()
  })
})
