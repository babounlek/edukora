import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getQuizHistoriqueDetail = vi.hoisted(() => vi.fn())
const rejouerQuiz = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ getQuizHistoriqueDetail, rejouerQuiz }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: true, isLoading: false, user: { id: 1 } }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <span>{markdown}</span> }))

import { ApiError } from "@/api/client"
import { QuizHistoriquePage } from "./QuizHistoriquePage"

const question = (surcharges = {}) => ({
  id: 1,
  ordre: 1,
  enonce_markdown: "Quelle est la dérivée de x² ?",
  type_reponse: "QCM",
  choix: [
    { lettre: "a", texte: "x" },
    { lettre: "b", texte: "2x" },
  ],
  theme: "dérivées",
  theme_id: 4,
  subject_code: "MATHS",
  subject_label: "Mathématiques",
  reponse_correcte: "b",
  corrige_markdown: "On dérive terme à terme.",
  contenu_disponible: true,
  cle_modifiee: false,
  snapshot_retroactif: false,
  reponse: { reponse_choisie: "a", resultat_declare: "", est_correcte: false, temps_secondes: 10 },
  ...surcharges,
})

const detail = (surcharges = {}) => ({
  id: 12,
  mode: "PRATIQUE",
  cursus: 20,
  cursus_display: "BAC - Série C",
  subject: 1,
  subject_label: "Mathématiques",
  theme: "",
  started_at: "2026-10-20T10:00:00Z",
  completed_at: "2026-10-20T10:05:00Z",
  duree_secondes: 300,
  score: 0,
  total_questions: 1,
  pourcentage: 0,
  rejeu_de: null,
  numero_tentative: 1,
  nb_tentatives: 1,
  snapshot_retroactif: false,
  peut_rejouer: true,
  questions: [question()],
  ...surcharges,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/historique/quiz/12"]}>
        <Routes>
          <Route path="/historique/quiz/:id" element={<QuizHistoriquePage />} />
          <Route path="/quiz/session/:id" element={<p>Session de rejeu</p>} />
          <Route path="/historique" element={<p>Historique</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("QuizHistoriquePage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getQuizHistoriqueDetail.mockResolvedValue(detail())
  })

  it("restitue le score, la question, la réponse donnée et la bonne réponse", async () => {
    afficher()

    expect(await screen.findByText("Quelle est la dérivée de x² ?")).toBeInTheDocument()
    expect(getQuizHistoriqueDetail).toHaveBeenCalledWith(12, expect.anything())
    expect(screen.getByText("0 sur 1")).toBeInTheDocument()
    expect(screen.getByLabelText("Bonne réponse", { selector: "svg" })).toBeInTheDocument()
    expect(screen.getByLabelText("Ta réponse", { selector: "svg" })).toBeInTheDocument()
    expect(screen.getByText("On dérive terme à terme.")).toBeInTheDocument()
  })

  it("signale une clé corrigée depuis et un contenu retiré, sans toucher à la note", async () => {
    getQuizHistoriqueDetail.mockResolvedValue(detail({ questions: [question({ cle_modifiee: true, contenu_disponible: false })] }))
    afficher()

    expect(await screen.findByText(/La bonne réponse a été modifiée depuis ta tentative/)).toBeInTheDocument()
    expect(screen.getByText(/retirée depuis/)).toBeInTheDocument()
    expect(screen.getByText("0 sur 1")).toBeInTheDocument()
  })

  it("prévient quand l'instantané a été rempli après coup", async () => {
    getQuizHistoriqueDetail.mockResolvedValue(detail({ snapshot_retroactif: true }))
    afficher()

    expect(await screen.findByText(/tel qu'il est aujourd'hui/)).toBeInTheDocument()
  })

  it("rejoue : crée la session une seule fois puis ouvre le nouveau quiz", async () => {
    rejouerQuiz.mockResolvedValue({ id: 77 })
    const utilisateur = userEvent.setup()
    afficher()

    const bouton = await screen.findByRole("button", { name: "Rejouer le quiz" })
    await utilisateur.dblClick(bouton)

    expect(await screen.findByText("Session de rejeu")).toBeInTheDocument()
    expect(rejouerQuiz).toHaveBeenCalledTimes(1)
    expect(rejouerQuiz).toHaveBeenCalledWith(12)
  })

  it("affiche l'erreur du serveur si le rejeu est refusé et laisse réessayer", async () => {
    rejouerQuiz.mockRejectedValue(new ApiError(403, { error: "Abonnement requis pour ce cursus." }))
    const utilisateur = userEvent.setup()
    afficher()

    await utilisateur.click(await screen.findByRole("button", { name: "Rejouer le quiz" }))

    expect(await screen.findByRole("alert")).toHaveTextContent("Abonnement requis pour ce cursus.")
    expect(screen.getByRole("button", { name: "Rejouer le quiz" })).toBeEnabled()
  })

  it("une tentative introuvable (autre élève, en cours) ne propose pas de réessayer", async () => {
    getQuizHistoriqueDetail.mockRejectedValue(new ApiError(404, { detail: "Not found." }))
    afficher()

    expect(await screen.findByText("Cette tentative est introuvable.")).toBeInTheDocument()
    await waitFor(() => expect(screen.queryByRole("button", { name: /réessayer/i })).not.toBeInTheDocument())
  })

  it("une panne réseau propose de réessayer", async () => {
    getQuizHistoriqueDetail.mockRejectedValueOnce(new ApiError(500, {})).mockResolvedValue(detail())
    const utilisateur = userEvent.setup()
    afficher()

    await utilisateur.click(await screen.findByRole("button", { name: /réessayer/i }))

    expect(await screen.findByText("Quelle est la dérivée de x² ?")).toBeInTheDocument()
  })
})
