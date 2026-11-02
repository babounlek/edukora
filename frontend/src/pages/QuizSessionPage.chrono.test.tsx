import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"

const getQuizSession = vi.hoisted(() => vi.fn())
const answerQuizQuestion = vi.hoisted(() => vi.fn())
const completeQuizSession = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({
  getQuizSession,
  answerQuizQuestion,
  completeQuizSession,
  revealQuizCorrige: vi.fn(),
  answerQuizEssai: vi.fn(),
  revealQuizEssaiCorrige: vi.fn(),
}))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/retours", () => ({ jouerRetour: vi.fn(), retoursActifs: () => true, definirRetoursActifs: vi.fn() }))
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <div>{markdown}</div> }))
vi.mock("@/components/BoutonPartager", () => ({ BoutonPartager: () => null }))
vi.mock("@/components/ObjectifXp", () => ({ ObjectifXp: () => <p>objectif du jour</p> }))
vi.mock("@/components/QuizFichePdfButtons", () => ({ QuizFichePdfButtons: () => null }))

import { QuizSessionPage } from "./QuizSessionPage"

const MAINTENANT = new Date("2026-11-02T10:00:00Z")

function session(extra = {}) {
  return {
    id: 5,
    mode: "PRATIQUE",
    cursus: 14,
    subject: 1,
    cursus_display: "BEPC",
    started_at: "2026-11-02T09:55:00Z",
    completed_at: null,
    total_questions: 2,
    xp_jour: { xp: 0, objectif: 20, atteint: false },
    chrono_actif: true,
    duree_limite_secondes: 600,
    temps_additionnel_pct: 0,
    // Cinq minutes après « maintenant ».
    echeance: "2026-11-02T10:05:00Z",
    chrono_ecoule: false,
    questions: [1, 2].map((id) => ({
      id,
      ordre: id,
      enonce_markdown: `Énoncé ${id}`,
      type_reponse: "QCM",
      choix: [
        { lettre: "a", texte: "faux" },
        { lettre: "b", texte: "juste" },
      ],
      subject_label: "Mathématiques",
      theme: "Pythagore",
    })),
    ...extra,
  }
}

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/quiz/session/5"]}>
      <Routes>
        <Route path="/quiz/session/:id" element={<QuizSessionPage />} />
        <Route path="/quiz/session/:id/resultat" element={<p>Page de résultat</p>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe("QuizSessionPage - quiz chronométré", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers({ toFake: ["Date", "setInterval", "clearInterval"] })
    vi.setSystemTime(MAINTENANT)
    localStorage.clear()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it("affiche le temps restant calculé depuis l'échéance du serveur", async () => {
    getQuizSession.mockResolvedValue(session())
    afficher()

    expect(await screen.findByRole("timer")).toHaveTextContent("05:00")
  })

  it("n'affiche aucun chrono sur un quiz libre", async () => {
    getQuizSession.mockResolvedValue(session({ chrono_actif: false, echeance: null, duree_limite_secondes: null }))
    afficher()

    await screen.findByText("Énoncé 1")
    expect(screen.queryByRole("timer")).toBeNull()
    expect(screen.getByText("objectif du jour")).toBeInTheDocument()
  })

  it("cache l'objectif d'XP : un quiz chronométré ne rapporte pas de points", async () => {
    getQuizSession.mockResolvedValue(session())
    afficher()

    await screen.findByText("Énoncé 1")
    expect(screen.queryByText("objectif du jour")).toBeNull()
  })

  it("envoie le temps passé sur la question avec la réponse", async () => {
    getQuizSession.mockResolvedValue(session())
    answerQuizQuestion.mockResolvedValue({
      ...session().questions[0],
      reponse: { reponse_choisie: "b", resultat_declare: "", est_correcte: true, xp_gagne: 0 },
    })
    afficher()
    await screen.findByText("Énoncé 1")

    vi.setSystemTime(new Date(MAINTENANT.getTime() + 7_000))
    fireEvent.click(screen.getByRole("button", { name: /juste/ }))

    await waitFor(() => expect(answerQuizQuestion).toHaveBeenCalledTimes(1))
    expect(answerQuizQuestion).toHaveBeenCalledWith(5, 1, { reponse_choisie: "b", temps_secondes: 7 })
  })

  it("fin douce : temps écoulé, plus de réponse possible, mais on peut rendre sa copie", async () => {
    getQuizSession.mockResolvedValue(session({ echeance: "2026-11-02T09:59:00Z", chrono_ecoule: true }))
    completeQuizSession.mockResolvedValue({ id: 5 })
    afficher()

    expect(await screen.findByRole("alert")).toHaveTextContent("Le temps est écoulé")
    expect(screen.getByRole("button", { name: /juste/ })).toBeDisabled()

    fireEvent.click(screen.getByRole("button", { name: /Rendre ma copie/ }))

    expect(await screen.findByText("Page de résultat")).toBeInTheDocument()
    expect(completeQuizSession).toHaveBeenCalledWith(5)
  })

  it("se fige aussi quand le serveur refuse la réponse, même si l'horloge du navigateur retarde", async () => {
    getQuizSession.mockResolvedValue(session())
    answerQuizQuestion.mockRejectedValue(new ApiError(409, { error: "Le temps est écoulé", code: "chrono_ecoule" }))
    afficher()
    await screen.findByText("Énoncé 1")

    fireEvent.click(screen.getByRole("button", { name: /juste/ }))

    expect(await screen.findByRole("alert")).toHaveTextContent("Le temps est écoulé")
    expect(screen.getByRole("button", { name: /Rendre ma copie/ })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /juste/ })).toBeDisabled()
  })

  it("cache et réaffiche le chrono sans l'arrêter", async () => {
    getQuizSession.mockResolvedValue(session())
    afficher()
    await screen.findByRole("timer")

    fireEvent.click(screen.getByRole("button", { name: "Masquer le chrono" }))

    expect(screen.getByRole("timer")).toHaveTextContent("--:--")
    fireEvent.click(screen.getByRole("button", { name: "Afficher le chrono" }))
    expect(screen.getByRole("timer")).toHaveTextContent("05:00")
  })
})
