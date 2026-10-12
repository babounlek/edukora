import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"

const getQuizSession = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ user: { id: 3, profil_actif: { id: 8 } } as unknown }))

vi.mock("@/api/endpoints", () => ({ getQuizSession }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))

import { ReprendreQuiz } from "./ReprendreQuiz"
import { lireQuizEnCours, memoriserQuizEnCours } from "@/lib/quizEnCours"

const CLE = "edukora:quiz-en-cours:3:8"

function session(extra: Record<string, unknown> = {}) {
  return {
    id: 41, mode: "PRATIQUE", cursus: 1, subject: 2, cursus_display: "BAC - Série C", started_at: "2026-10-12T10:00:00Z",
    completed_at: null, total_questions: 5,
    questions: [1, 2, 3, 4, 5].map((i) => ({ id: i, reponse: i <= 2 ? { est_correcte: true } : null })),
    ...extra,
  }
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <ReprendreQuiz />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getQuizSession.mockReset()
  localStorage.clear()
  auth.user = { id: 3, profil_actif: { id: 8 } }
})

describe("ReprendreQuiz", () => {
  it("ne propose rien quand aucun quiz n'a été commencé", () => {
    afficher()
    expect(getQuizSession).not.toHaveBeenCalled()
    expect(screen.queryByRole("link")).not.toBeInTheDocument()
  })

  it("propose de reprendre le quiz commencé, avec sa progression", async () => {
    memoriserQuizEnCours(CLE, 41)
    getQuizSession.mockResolvedValue(session())
    afficher()

    const lien = await screen.findByRole("link", { name: /Quiz en cours/ })
    expect(lien).toHaveAttribute("href", "/quiz/session/41")
    expect(lien).toHaveTextContent("2 / 5 répondues")
    expect(lien).toHaveTextContent("Reprendre")
  })

  it("propose de terminer quand tout est répondu", async () => {
    memoriserQuizEnCours(CLE, 41)
    getQuizSession.mockResolvedValue(
      session({ questions: [1, 2, 3, 4, 5].map((i) => ({ id: i, reponse: { est_correcte: true } })) }),
    )
    afficher()
    expect(await screen.findByText("Terminer")).toBeInTheDocument()
  })

  it("oublie un quiz déjà terminé, sans rien afficher", async () => {
    memoriserQuizEnCours(CLE, 41)
    getQuizSession.mockResolvedValue(session({ completed_at: "2026-10-12T10:30:00Z" }))
    afficher()

    await waitFor(() => expect(lireQuizEnCours(CLE)).toBeNull())
    expect(screen.queryByRole("link")).not.toBeInTheDocument()
  })

  it("oublie un quiz que le serveur ne connaît plus", async () => {
    memoriserQuizEnCours(CLE, 41)
    getQuizSession.mockRejectedValue(new ApiError(404, { detail: "Not found" }))
    afficher()

    await waitFor(() => expect(lireQuizEnCours(CLE)).toBeNull())
  })

  it("garde le souvenir quand l'API est seulement injoignable", async () => {
    memoriserQuizEnCours(CLE, 41)
    getQuizSession.mockRejectedValue(new TypeError("Failed to fetch"))
    afficher()

    await waitFor(() => expect(getQuizSession).toHaveBeenCalled())
    expect(lireQuizEnCours(CLE)).toBe(41)
  })

  it("cesse de le proposer quand l'élève le décide", async () => {
    memoriserQuizEnCours(CLE, 41)
    getQuizSession.mockResolvedValue(session())
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: /Ne plus proposer/ }))

    expect(screen.queryByRole("link", { name: /Quiz en cours/ })).not.toBeInTheDocument()
    expect(lireQuizEnCours(CLE)).toBeNull()
  })

  it("ne mélange pas les élèves d'un même appareil", () => {
    memoriserQuizEnCours("edukora:quiz-en-cours:3:9", 99)
    afficher()
    expect(getQuizSession).not.toHaveBeenCalled()
  })
})
