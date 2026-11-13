import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const api = vi.hoisted(() => ({
  completeQuizSession: vi.fn(),
  listQuizEssais: vi.fn(),
  refaireLesRatees: vi.fn(),
  rejouerQuiz: vi.fn(),
  startQuizSession: vi.fn(),
}))
vi.mock("@/api/endpoints", () => api)
const auth = vi.hoisted(() => ({ user: null as unknown }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: auth.user !== null, user: auth.user, isLoading: false }) }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/retours", () => ({ jouerRetour: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/useCompteur", () => ({ useCompteur: (cible: number) => cible }))
// Les enfants qui parlent au serveur de leur côté : hors sujet ici.
vi.mock("@/components/ReglagesSeance", () => ({ InvitePush: () => <p>Invitation aux rappels</p> }))
vi.mock("@/components/QuizFichePdfButtons", () => ({ QuizFichePdfButtons: () => <p>Fiches PDF</p> }))

import { clearJetonInvite, setJetonInvite } from "@/lib/invite"
import { memoriserDefi } from "@/lib/defiEssai"
import { QuizResultPage } from "./QuizResultPage"

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
  api.completeQuizSession.mockResolvedValue(resultat())
  api.listQuizEssais.mockResolvedValue([])
  sessionStorage.clear()
  auth.user = null
})
afterEach(() => clearJetonInvite())

describe("QuizResultPage : un visiteur qui a joué avec un compte invité", () => {
  beforeEach(() => setJetonInvite("jeton-invite"))

  it("voit ses vrais points et la carte pour garder son quiz en créant un compte", async () => {
    afficher()

    expect(await screen.findByText("Garde ton quiz et tes points.")).toBeInTheDocument()
    expect(screen.getByText("+40 points")).toBeInTheDocument()
    const creer = screen.getByRole("link", { name: "Créer mon compte gratuit" })
    expect(creer).toHaveAttribute("href", "/connexion")
  })

  it("ne voit rien de ce qui appartient à un compte : rythme, partage de score, rappels, parcours, mon compte", async () => {
    afficher()
    await screen.findByText("Garde ton quiz et tes points.")

    expect(screen.queryByText(/Changer de rythme|rythme/i)).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /Partager mon score/i })).not.toBeInTheDocument()
    expect(screen.queryByText("Invitation aux rappels")).not.toBeInTheDocument()
    expect(screen.queryByRole("link", { name: "Mon compte" })).not.toBeInTheDocument()
    expect(screen.queryByRole("link", { name: /parcours/i })).not.toBeInTheDocument()
  })

  it("garde de quoi relire ses réponses et refaire un quiz", async () => {
    afficher()
    await screen.findByText("Garde ton quiz et tes points.")

    expect(screen.getByRole("link", { name: /voir mes réponses/i })).toHaveAttribute("href", "/historique/quiz/12")
  })

  it("compare le résultat au défi d'un lien, mémorisé pour cette séance", async () => {
    memoriserDefi({ reussies: 2, total: 5 }, 12)
    afficher()

    expect(await screen.findByText("Défi relevé : tu fais mieux que ton camarade (4/5 contre 2/5) !")).toBeInTheDocument()
  })

  it("ignore le défi d'une autre séance", async () => {
    memoriserDefi({ reussies: 2, total: 5 }, 99)
    afficher()

    await screen.findByText("Garde ton quiz et tes points.")
    expect(screen.queryByText(/Défi relevé/)).not.toBeInTheDocument()
  })
})

describe("QuizResultPage : un connecté", () => {
  it("garde son compte, ses réglages et ses rappels, sans la carte « garde ton quiz »", async () => {
    auth.user = { id: 1, referral_code: "ABC" }
    afficher()

    expect(await screen.findByText("Invitation aux rappels")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Mon compte" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Partager mon score/i })).toBeInTheDocument()
    expect(screen.queryByText("Garde ton quiz et tes points.")).not.toBeInTheDocument()
  })
})
