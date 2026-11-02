import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes, useLocation, useNavigate } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMySubscriptions = vi.hoisted(() => vi.fn())
const listQuizSubjects = vi.hoisted(() => vi.fn())
const getThemesFrequents = vi.hoisted(() => vi.fn(() => Promise.resolve({ themes: [], nb_sessions_disponibles: 0 })))

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
  getThemesFrequents,
  startQuizSession: vi.fn(),
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { startQuizSession } from "@/api/endpoints"
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
    getThemesFrequents.mockResolvedValue({ themes: [], nb_sessions_disponibles: 0 })
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

  it("affiche « vues/total » sur la matière dès qu'une question a été vue, le total seul sinon", async () => {
    listQuizSubjects.mockResolvedValue([
      { id: 1, code: "MATHS", label: "Mathématiques", country: { code: "CM" }, nb_questions: 30, nb_vues: 12 },
      { id: 2, code: "SVT", label: "SVT", country: { code: "CM" }, nb_questions: 20, nb_vues: 0 },
    ])
    afficher()

    const vues = await screen.findByText("12/30")
    expect(vues.getAttribute("title")).toMatch(/12.*30/)
    expect(screen.queryByText("0/20")).toBeNull()
  })

  it("repart à zéro quand le tour d'une matière est terminé, en le disant au survol", async () => {
    listQuizSubjects.mockResolvedValue([
      { id: 1, code: "MATHS", label: "Mathématiques", country: { code: "CM" }, nb_questions: 30, nb_vues: 0, nb_tours: 1 },
    ])
    afficher()

    const tour = await screen.findByText("0/30")
    expect(tour.getAttribute("title")).toMatch(/Tour terminé.*1 tour terminé/)
  })

  it("montre l'avancement du thème sur sa carte quand le profil a déjà répondu", async () => {
    getThemesFrequents.mockResolvedValue({
      disponible: true,
      has_access: true,
      nb_sessions_disponibles: 10,
      nb_themes_verrouilles: 0,
      themes: [
        { id: 5, tag: "dérivation", nb_epreuves: 8, frequence_pct: 80, quiz_disponible: true, quiz_total: 30, quiz_vues: 12, quiz_tours: 2 },
        { id: 6, tag: "limites", nb_epreuves: 5, frequence_pct: 50, quiz_disponible: true, quiz_total: 20, quiz_vues: 0, quiz_tours: 0 },
      ],
    })
    afficher()

    const carte = await screen.findByText(/12\/30/)
    expect(carte.getAttribute("title")).toMatch(/12.*30.*2 tours terminés/)
    expect(screen.queryByText(/0\/20/)).toBeNull()
  })

  it("propose tous les abonnements quand aucun examen n'est préparé", async () => {
    auth.user.cursus_prepare = null
    afficher()
    expect(await screen.findByRole("button", { name: "BEPC" })).toBeTruthy()
    expect(screen.getByRole("button", { name: "BAC C" })).toBeTruthy()
  })
})

describe("QuizStartPage - lancement automatique depuis un lien", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    auth.user.cursus_prepare = { id: 14 }
    getThemesFrequents.mockResolvedValue({ themes: [], nb_sessions_disponibles: 0 })
    listMySubscriptions.mockResolvedValue([abonnement(258, BEPC)])
    listQuizSubjects.mockResolvedValue([])
    vi.mocked(startQuizSession).mockResolvedValue({ id: 467 } as never)
  })

  function Seance() {
    const navigate = useNavigate()
    const lieu = useLocation()
    return (
      <div>
        <p data-testid="lieu">{lieu.pathname}</p>
        <button type="button" onClick={() => navigate(-1)}>Retour</button>
      </div>
    )
  }

  it("« Retour » depuis la séance lancée par un lien sort du quiz au lieu de relancer une séance", async () => {
    // Test élève Gogo : /quiz/session/467 puis Retour donnait /quiz/session/468 (la page relais relançait une séance).
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={["/recherche", "/quiz?cursus=14&theme=7"]} initialIndex={1}>
          <Routes>
            <Route path="/quiz" element={<QuizStartPage />} />
            <Route path="/quiz/session/:id" element={<Seance />} />
            <Route path="/recherche" element={<Seance />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent("/quiz/session/467"))
    expect(startQuizSession).toHaveBeenCalledTimes(1)

    screen.getByRole("button", { name: "Retour" }).click()

    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent("/recherche"))
    expect(startQuizSession).toHaveBeenCalledTimes(1)
  })
})
