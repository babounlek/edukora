import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getMyProgression = vi.hoisted(() => vi.fn())
const listMyTentativesInedites = vi.hoisted(() => vi.fn())
const listQuizHistorique = vi.hoisted(() => vi.fn())
const listQuizEnCours = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ getMyProgression, listMyTentativesInedites, listQuizHistorique, listQuizEnCours }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ isAuthenticated: true, isLoading: false, user: { id: 1, profil_actif: { id: 9 }, cursus_prepare: { id: 20 } } }),
}))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { HistoriquePage } from "./HistoriquePage"

const ligne = (id: number, surcharges = {}) => ({
  id,
  mode: "PRATIQUE",
  cursus: 20,
  cursus_display: "BAC - Série C",
  subject: 1,
  subject_label: "Mathématiques",
  theme: "",
  started_at: "2026-10-20T10:00:00Z",
  completed_at: "2026-10-20T10:05:00Z",
  duree_secondes: 125,
  score: 2,
  total_questions: 3,
  pourcentage: 67,
  rejeu_de: null,
  numero_tentative: 1,
  nb_tentatives: 1,
  ...surcharges,
})

const page = (results: ReturnType<typeof ligne>[], { count = results.length, next = null as string | null } = {}) => ({
  count, next, previous: null, results,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <HistoriquePage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("HistoriquePage - quiz", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getMyProgression.mockResolvedValue({ lessons: [], cours: [] })
    listMyTentativesInedites.mockResolvedValue([])
    listQuizHistorique.mockResolvedValue(page([]))
    listQuizEnCours.mockResolvedValue([])
  })

  it("sans aucun quiz terminé, explique et renvoie vers les quiz", async () => {
    afficher()

    expect(await screen.findByText(/Tu n'as pas encore terminé de quiz/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Voir les quiz/ })).toHaveAttribute("href", "/quiz")
  })

  it("liste les tentatives avec score, durée et lien vers le détail", async () => {
    listQuizHistorique.mockResolvedValue(page([ligne(5), ligne(6, { rejeu_de: 5, numero_tentative: 2, nb_tentatives: 2, score: 3, pourcentage: 100 })]))
    afficher()

    const premiere = await screen.findByRole("link", { name: /2\/3/ })
    expect(premiere).toHaveAttribute("href", "/historique/quiz/5")
    expect(premiere).toHaveTextContent("2 min 5 s")
    const rejeu = screen.getByRole("link", { name: /3\/3/ })
    expect(rejeu).toHaveAttribute("href", "/historique/quiz/6")
    expect(rejeu).toHaveTextContent("Rejeu")
    expect(rejeu).toHaveTextContent("Tentative 2 sur 2")
  })

  it("charge la page suivante à la demande", async () => {
    listQuizHistorique
      .mockResolvedValueOnce(page([ligne(5)], { count: 2, next: "http://api/quiz/historique/?page=2" }))
      .mockResolvedValueOnce(page([ligne(6)], { count: 2 }))
    const utilisateur = userEvent.setup()
    afficher()

    await utilisateur.click(await screen.findByRole("button", { name: "Voir plus de quiz" }))

    expect(listQuizHistorique).toHaveBeenNthCalledWith(2, 2, expect.anything())
    expect(screen.getAllByRole("link", { name: /2\/3/ })).toHaveLength(2)
    expect(screen.queryByRole("button", { name: "Voir plus de quiz" })).not.toBeInTheDocument()
  })

  it("une panne propose de réessayer au lieu d'afficher un historique vide", async () => {
    listQuizHistorique.mockRejectedValueOnce(new Error("réseau")).mockResolvedValue(page([ligne(5)]))
    const utilisateur = userEvent.setup()
    afficher()

    expect(screen.queryByText(/Tu n'as pas encore terminé de quiz/)).not.toBeInTheDocument()
    await utilisateur.click(await screen.findByRole("button", { name: /réessayer/i }))

    expect(await screen.findByRole("link", { name: /2\/3/ })).toBeInTheDocument()
  })

  it("avec des quiz et des tentatives d'épreuves, propose des onglets", async () => {
    listQuizHistorique.mockResolvedValue(page([ligne(5)]))
    listMyTentativesInedites.mockResolvedValue([
      { id: 3, epreuve_titre: "Maths blanche", cursus_display: "BAC - Série C", started_at: "2026-10-01T10:00:00Z", submitted_at: null, score_obtenu: null, note_obtenue: null, bareme_snapshot: null },
    ])
    afficher()

    expect(await screen.findByRole("tab", { name: "Quiz (1)" })).toBeInTheDocument()
    expect(screen.getByRole("tab", { name: "Tentatives (1)" })).toBeInTheDocument()
  })
})

const enCours = (id: number, surcharges = {}) => ({
  id, mode: "PRATIQUE", cursus: 20, cursus_display: "BAC - Série C", subject: 1, subject_label: "Physique", theme: "",
  started_at: "2026-10-22T10:00:00Z", derniere_reponse_at: "2026-10-22T10:05:00Z", nb_repondues: 2, total_questions: 5,
  a_terminer: false, rejeu_de: null,
  ...surcharges,
})

describe("HistoriquePage - reprendre un quiz", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getMyProgression.mockResolvedValue({ lessons: [], cours: [] })
    listMyTentativesInedites.mockResolvedValue([])
    listQuizHistorique.mockResolvedValue(page([]))
    listQuizEnCours.mockResolvedValue([])
  })

  it("propose « Reprendre le quiz » vers la même session, même sans aucun quiz terminé", async () => {
    listQuizEnCours.mockResolvedValue([enCours(31)])
    afficher()

    const lien = await screen.findByRole("link", { name: /Physique/ })
    expect(lien).toHaveAttribute("href", "/quiz/session/31")
    expect(lien).toHaveTextContent("2 / 5 répondues")
    expect(lien).toHaveTextContent("Reprendre le quiz")
    expect(screen.queryByText(/Tu n'as pas encore terminé de quiz/)).not.toBeInTheDocument()
  })

  it("propose de terminer quand tout est répondu", async () => {
    listQuizEnCours.mockResolvedValue([enCours(31, { nb_repondues: 5, a_terminer: true })])
    afficher()

    expect(await screen.findByRole("link", { name: /Physique/ })).toHaveTextContent("Terminer")
  })

  it("place les quiz en cours avant les quiz terminés, chacun sous son titre", async () => {
    listQuizEnCours.mockResolvedValue([enCours(31)])
    listQuizHistorique.mockResolvedValue(page([ligne(5)]))
    afficher()

    const reprendre = await screen.findByRole("link", { name: /Physique/ })
    const termine = await screen.findByRole("link", { name: /2\/3/ })
    expect(reprendre.compareDocumentPosition(termine) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(screen.getByText("En cours")).toBeInTheDocument()
    expect(screen.getByText("Terminés")).toBeInTheDocument()
  })

  it("n'affiche aucune reprise quand rien n'est en cours, et reste utilisable si la liste est en panne", async () => {
    listQuizEnCours.mockRejectedValue(new Error("réseau"))
    listQuizHistorique.mockResolvedValue(page([ligne(5)]))
    afficher()

    expect(await screen.findByRole("link", { name: /2\/3/ })).toBeInTheDocument()
    expect(screen.queryByText("Reprendre le quiz")).not.toBeInTheDocument()
    expect(screen.queryByRole("alert")).not.toBeInTheDocument()
  })
})
