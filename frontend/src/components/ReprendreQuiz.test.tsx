import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listQuizEnCours = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ user: { id: 3, profil_actif: { id: 8 } } as unknown }))

vi.mock("@/api/endpoints", () => ({ listQuizEnCours }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))

import { ReprendreQuiz } from "./ReprendreQuiz"
import { lireQuizIgnores } from "@/lib/quizEnCours"

const CLE = "edukora:quiz-ignores:3:8"

function ligne(extra: Record<string, unknown> = {}) {
  return {
    id: 41, mode: "PRATIQUE", cursus: 1, cursus_display: "BAC - Série C", subject: 2, subject_label: "Mathématiques", theme: "",
    started_at: "2026-10-12T10:00:00Z", derniere_reponse_at: "2026-10-12T10:05:00Z", nb_repondues: 2, total_questions: 5,
    a_terminer: false, rejeu_de: null,
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
  listQuizEnCours.mockReset()
  localStorage.clear()
  auth.user = { id: 3, profil_actif: { id: 8 } }
})

describe("ReprendreQuiz", () => {
  it("ne propose rien quand aucun quiz n'est en cours", async () => {
    listQuizEnCours.mockResolvedValue([])
    afficher()

    await vi.waitFor(() => expect(listQuizEnCours).toHaveBeenCalled())
    expect(screen.queryByRole("link")).not.toBeInTheDocument()
  })

  it("propose de reprendre le quiz le plus récent, avec sa progression, sans rien stocker sur l'appareil", async () => {
    listQuizEnCours.mockResolvedValue([ligne(), ligne({ id: 40 })])
    afficher()

    const lien = await screen.findByRole("link", { name: /Quiz en cours/ })
    expect(lien).toHaveAttribute("href", "/quiz/session/41")
    expect(lien).toHaveTextContent("2 / 5 répondues")
    expect(lien).toHaveTextContent("Reprendre")
    expect(localStorage.length).toBe(0)
  })

  it("propose de terminer quand tout est répondu", async () => {
    listQuizEnCours.mockResolvedValue([ligne({ nb_repondues: 5, a_terminer: true })])
    afficher()

    expect(await screen.findByText("Terminer")).toBeInTheDocument()
  })

  it("nomme un rejeu en cours et un test de niveau pour ce qu'ils sont", async () => {
    listQuizEnCours.mockResolvedValue([ligne({ rejeu_de: 12 })])
    afficher()
    expect(await screen.findByRole("link", { name: /Rejeu en cours/ })).toBeInTheDocument()
  })

  it("passe au quiz suivant quand l'élève écarte celui-ci, et le retient sur l'appareil", async () => {
    listQuizEnCours.mockResolvedValue([ligne(), ligne({ id: 40, nb_repondues: 1 })])
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: /Ne plus proposer/ }))

    expect(await screen.findByRole("link", { name: /1 \/ 5 répondues/ })).toHaveAttribute("href", "/quiz/session/40")
    expect(lireQuizIgnores(CLE)).toEqual([41])
  })

  it("ne propose plus un quiz écarté, même après rechargement", async () => {
    localStorage.setItem(CLE, JSON.stringify([41]))
    listQuizEnCours.mockResolvedValue([ligne()])
    afficher()

    await vi.waitFor(() => expect(listQuizEnCours).toHaveBeenCalled())
    expect(screen.queryByRole("link")).not.toBeInTheDocument()
  })

  it("ne mélange pas les élèves d'un même appareil", async () => {
    localStorage.setItem("edukora:quiz-ignores:3:9", JSON.stringify([41]))
    listQuizEnCours.mockResolvedValue([ligne()])
    afficher()

    expect(await screen.findByRole("link", { name: /Quiz en cours/ })).toBeInTheDocument()
  })

  it("garde la page silencieuse quand le serveur est injoignable", async () => {
    listQuizEnCours.mockRejectedValue(new TypeError("Failed to fetch"))
    afficher()

    await vi.waitFor(() => expect(listQuizEnCours).toHaveBeenCalled())
    expect(screen.queryByRole("link")).not.toBeInTheDocument()
    expect(screen.queryByRole("alert")).not.toBeInTheDocument()
  })
})
