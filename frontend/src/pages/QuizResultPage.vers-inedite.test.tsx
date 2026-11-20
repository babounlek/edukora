import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const api = vi.hoisted(() => ({
  completeQuizSession: vi.fn(),
  listQuizEssais: vi.fn(),
  refaireLesRatees: vi.fn(),
  rejouerQuiz: vi.fn(),
  startQuizSession: vi.fn(),
}))
vi.mock("@/api/endpoints", () => api)
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ isAuthenticated: true, user: { a_un_abonnement_actif: true }, isLoading: false }),
}))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/retours", () => ({ jouerRetour: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/useCompteur", () => ({ useCompteur: (cible: number) => cible }))
vi.mock("@/components/ReglagesSeance", () => ({ InvitePush: () => <p>Invitation aux rappels</p> }))
vi.mock("@/components/JalonsAtteints", () => ({ JalonsAtteints: () => null }))
vi.mock("@/components/QuizFichePdfButtons", () => ({ QuizFichePdfButtons: () => <p>Fiches PDF</p> }))

import { QuizResultPage } from "./QuizResultPage"

const mini = { id: 3, slug: "mini-maths-bepc-n1", titre: "Mini Maths", country: "cm", meme_matiere: true }
const entiere = { id: 9, slug: "bepc-maths-inedite", titre: "BEPC Maths", country: "cm", meme_matiere: true }

const resultat = (surcharge = {}) => ({
  id: 12, cursus: 4, subject: 5, total_questions: 5, questions_repondues: 5, score: 4, meilleure_serie: 2,
  seances_cette_semaine: 1, par_theme: [], seance_validee: false, mode: "PRATIQUE", nb_ratees: 0,
  xp: { session: { reponses: 40, seance: 0, total: 40 }, jour: { xp: 40, objectif: 30, atteint: true, objectifs_possibles: [10, 30] } },
  ...surcharge,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/quiz/session/12/resultat"]}>
        <Routes>
          <Route path="/quiz/session/:id/resultat" element={<QuizResultPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  Object.values(api).forEach((m) => m.mockReset())
  api.listQuizEssais.mockResolvedValue([])
  sessionStorage.clear()
  localStorage.clear()
})

describe("QuizResultPage : prolongement vers une mini ou une épreuve entière", () => {
  it("propose la mini d'abord, et pas l'épreuve entière en même temps", async () => {
    api.completeQuizSession.mockResolvedValue(resultat({ mini_suggeree: mini, inedite_suggeree: entiere }))
    afficher()

    const bloc = await screen.findByTestId("quiz-vers-mini")
    expect(bloc.querySelector("a")).toHaveAttribute("href", "/cm/epreuves-inedites/mini-maths-bepc-n1")
    expect(screen.queryByTestId("quiz-vers-inedite")).toBeNull()
  })

  it("propose l'épreuve entière quand il n'y a pas de mini", async () => {
    api.completeQuizSession.mockResolvedValue(resultat({ mini_suggeree: null, inedite_suggeree: entiere }))
    afficher()

    const bloc = await screen.findByTestId("quiz-vers-inedite")
    expect(bloc.querySelector("a")).toHaveAttribute("href", "/cm/epreuves-inedites/bepc-maths-inedite")
    expect(screen.queryByTestId("quiz-vers-mini")).toBeNull()
  })

  it("ne propose rien sous 70 %", async () => {
    api.completeQuizSession.mockResolvedValue(resultat({ score: 2, mini_suggeree: mini, inedite_suggeree: entiere }))
    afficher()

    await vi.waitFor(() => expect(api.completeQuizSession).toHaveBeenCalled())
    await screen.findByText("+40 points")
    expect(screen.queryByTestId("quiz-vers-mini")).toBeNull()
    expect(screen.queryByTestId("quiz-vers-inedite")).toBeNull()
  })
})
