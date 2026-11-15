import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getQuizSession = vi.hoisted(() => vi.fn())
const passerQuizQuestion = vi.hoisted(() => vi.fn())
const completeQuizSession = vi.hoisted(() => vi.fn())
const invite = vi.hoisted(() => ({ actif: false }))

vi.mock("@/api/endpoints", () => ({ getQuizSession, passerQuizQuestion, completeQuizSession }))
vi.mock("@/lib/useEssaiSansCompte", () => ({ useEssaiSansCompte: () => invite.actif }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/retours", () => ({ jouerRetour: vi.fn(), retoursActifs: () => true, definirRetoursActifs: vi.fn() }))
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <div>{markdown}</div> }))
vi.mock("@/components/BoutonPartager", () => ({ BoutonPartager: () => null }))
vi.mock("@/components/ObjectifXp", () => ({ ObjectifXp: () => null }))
vi.mock("@/components/QuizFichePdfButtons", () => ({ QuizFichePdfButtons: () => null }))

import { QuizSessionPage } from "./QuizSessionPage"

const question = (id: number, extra = {}) => ({
  id, ordre: id, enonce_markdown: `Énoncé ${id}`, type_reponse: "QCM", choix: [{ lettre: "a", texte: "Un" }, { lettre: "b", texte: "Deux" }],
  subject_label: "Mathématiques", theme: "Dérivées", ...extra,
})

const session = (questions: unknown[]) => ({
  id: 7, mode: "PRATIQUE", cursus: 14, subject: 1, cursus_display: "BEPC", started_at: "2026-11-15T10:00:00Z", completed_at: null,
  total_questions: questions.length, questions,
})

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/quiz/session/7"]}>
      <Routes>
        <Route path="/quiz/session/:id" element={<QuizSessionPage />} />
        <Route path="/quiz/session/:id/resultat" element={<p>Écran de résultat</p>} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  invite.actif = false
  window.scrollTo = vi.fn()
  passerQuizQuestion.mockImplementation((_s: number, id: number) => Promise.resolve(question(id, { passee: true })))
  completeQuizSession.mockResolvedValue({})
})

describe("QuizSessionPage : passer une question", () => {
  it("passer envoie la demande et avance à la question suivante", async () => {
    getQuizSession.mockResolvedValue(session([question(1), question(2)]))
    afficher()

    fireEvent.click(await screen.findByRole("button", { name: "Passer cette question" }))

    await waitFor(() => expect(passerQuizQuestion).toHaveBeenCalledWith(7, 1))
    expect(await screen.findByText("Énoncé 2")).toBeInTheDocument()
  })

  it("passer la dernière question mène au résultat", async () => {
    getQuizSession.mockResolvedValue(session([question(1, { passee: true }), question(2)]))
    afficher()

    fireEvent.click(await screen.findByRole("button", { name: "Passer cette question" }))

    await waitFor(() => expect(completeQuizSession).toHaveBeenCalledWith(7))
    expect(await screen.findByText("Écran de résultat")).toBeInTheDocument()
  })

  it("à la reprise, on arrive sur la première question ni répondue ni passée", async () => {
    getQuizSession.mockResolvedValue(session([question(1, { passee: true }), question(2)]))
    afficher()

    expect(await screen.findByText("Énoncé 2")).toBeInTheDocument()
  })

  it("avant le corrigé d'une question ouverte, on propose de passer", async () => {
    getQuizSession.mockResolvedValue(session([question(1, { type_reponse: "OUVERTE", choix: [] }), question(2)]))
    afficher()
    expect(await screen.findByRole("button", { name: "Passer cette question" })).toBeInTheDocument()
  })

  it("un invité (quiz gratuit sans compte) ne voit pas le bouton : la route n'est pas ouverte à son jeton", async () => {
    invite.actif = true
    getQuizSession.mockResolvedValue(session([question(1), question(2)]))
    afficher()

    expect(await screen.findByText("Énoncé 1")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Passer cette question" })).not.toBeInTheDocument()
  })
})
