import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMySubscriptions = vi.hoisted(() => vi.fn())
const listQuizSubjects = vi.hoisted(() => vi.fn())

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null }
const BAC_C = { id: 20, examen: "BAC", examen_display: "BAC", series: { id: 3, code: "C", label: "Série C" } }

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: {
    id: 1,
    profil_actif: { id: 9 },
    cursus_prepare: { id: 14 } as { id: number } | null,
  },
}))

vi.mock("@/api/endpoints", () => ({
  listMySubscriptions,
  listQuizSubjects,
  getThemesFrequents: vi.fn(() => Promise.resolve({ themes: [], nb_sessions_disponibles: 0 })),
  startQuizSession: vi.fn(),
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { QuizStartPage } from "./QuizStartPage"

const abonnement = (id: number, cursus: typeof BEPC | typeof BAC_C, profilId = 9) => ({
  id,
  cursus,
  profil: { id: profilId },
  is_active: true,
})

function afficher(url = "/quiz") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const arbre = (u: string) => (
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[u]}>
        <QuizStartPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
  const rendu = render(arbre(url))
  return { ...rendu, rerenderPage: () => rendu.rerender(arbre(url)) }
}

describe("QuizStartPage - pastilles d'examen", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    auth.user.cursus_prepare = { id: 14 }
    listMySubscriptions.mockResolvedValue([
      abonnement(253, BAC_C),
      abonnement(258, BEPC),
      abonnement(260, BAC_C, 15), // autre profil du compte : jamais proposé
    ])
    listQuizSubjects.mockResolvedValue([
      { id: 1, code: "MATHS", label: "Mathématiques", country: { code: "CM" }, nb_questions: 1149 },
    ])
  })

  it("ne propose que l'examen préparé quand le profil a payé BEPC et BAC C", async () => {
    afficher()
    expect(await screen.findByRole("button", { name: "BEPC" })).toBeTruthy()
    await waitFor(() => expect(listQuizSubjects).toHaveBeenCalledWith(14))
    expect(screen.queryByRole("button", { name: "BAC C" })).toBeNull()
    expect(listQuizSubjects).not.toHaveBeenCalledWith(20)
  })

  it("suit l'examen préparé quand l'élève le change depuis le bandeau", async () => {
    const { rerenderPage } = afficher()
    expect(await screen.findByRole("button", { name: "BEPC" })).toBeTruthy()

    auth.user.cursus_prepare = { id: 20 }
    rerenderPage()

    expect(await screen.findByRole("button", { name: "BAC C" })).toBeTruthy()
    expect(screen.queryByRole("button", { name: "BEPC" })).toBeNull()
    await waitFor(() => expect(listQuizSubjects).toHaveBeenLastCalledWith(20))
  })

  it("garde un lien direct ?cursus= vers l'autre examen", async () => {
    afficher("/quiz?cursus=20")
    expect(await screen.findByRole("button", { name: "BAC C" })).toBeTruthy()
    expect(screen.getByRole("button", { name: "BEPC" })).toBeTruthy()
    await waitFor(() => expect(listQuizSubjects).toHaveBeenCalledWith(20))
  })

  it("propose tous les abonnements quand aucun examen n'est préparé", async () => {
    auth.user.cursus_prepare = null
    afficher()
    expect(await screen.findByRole("button", { name: "BEPC" })).toBeTruthy()
    expect(screen.getByRole("button", { name: "BAC C" })).toBeTruthy()
  })
})
