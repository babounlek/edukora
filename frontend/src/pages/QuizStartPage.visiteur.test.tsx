import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const auth = vi.hoisted(() => ({
  isAuthenticated: false,
  isLoading: false,
  user: null as { cursus_prepare: { id: number } | null } | null,
}))

vi.mock("@/api/endpoints", () => ({
  listMySubscriptions: vi.fn(() => Promise.resolve([])),
  listQuizSubjects: vi.fn(() => Promise.resolve([])),
  getThemesFrequents: vi.fn(() => Promise.resolve({ themes: [], nb_sessions_disponibles: 0 })),
  startQuizSession: vi.fn(),
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
// Seule la valeur reçue en `cursusInitial` compte ici : le composant réel appelle l'API des essais.
vi.mock("@/components/EssaisGratuitsQuiz", () => ({
  EssaisGratuitsQuiz: ({ cursusInitial }: { cursusInitial?: number | null }) => (
    <p data-testid="essais">{String(cursusInitial ?? "aucun")}</p>
  ),
}))

import { memoriserCursusPrepareEnAttente, oublierCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { QuizStartPage } from "./QuizStartPage"

function afficher(url = "/quiz") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]}>
        <QuizStartPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("QuizStartPage - visiteur sans compte", () => {
  beforeEach(() => {
    auth.isAuthenticated = false
    auth.user = null
    oublierCursusPrepareEnAttente()
  })
  afterEach(() => oublierCursusPrepareEnAttente())

  it("ouvre les essais gratuits sur l'examen que le visiteur a déclaré", async () => {
    memoriserCursusPrepareEnAttente(20)
    afficher()

    expect(await screen.findByTestId("essais")).toHaveTextContent("20")
  })

  it("sans examen déclaré, ne force aucun cursus", async () => {
    afficher()

    expect(await screen.findByTestId("essais")).toHaveTextContent("aucun")
  })

  it("l'examen demandé dans l'URL l'emporte sur celui du visiteur", async () => {
    memoriserCursusPrepareEnAttente(20)
    afficher("/quiz?cursus=14")

    expect(await screen.findByTestId("essais")).toHaveTextContent("14")
  })
})
