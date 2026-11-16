import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { listQuizEssais, lancerQuizGratuit, declarer, trackEvent, etat } = vi.hoisted(() => ({
  listQuizEssais: vi.fn(),
  lancerQuizGratuit: vi.fn(),
  declarer: vi.fn(),
  trackEvent: vi.fn(),
  etat: { choisi: null as null | { id: number; examen: string; examen_display: string; series: null } },
}))
vi.mock("@/api/endpoints", () => ({ listQuizEssais }))
vi.mock("@/lib/quizGratuit", () => ({ lancerQuizGratuit }))
vi.mock("@/lib/analytics", () => ({ trackEvent }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: false, user: null }) }))
vi.mock("@/lib/declarerCursus", () => ({ useDeclarerCursus: () => ({ declarer, enCours: false }) }))
vi.mock("@/lib/cursusAccueil", () => ({ useCursusPrepareDeclare: () => etat.choisi }))
vi.mock("@/lib/cursusLangue", () => ({ useCursusListe: () => ({ data: CURSUS, tous: CURSUS, isPending: false }) }))
// Le menu de changement d'examen et le compte à rebours ont leurs propres tests.
vi.mock("@/components/ChoixExamen", () => ({ SelecteurExamen: ({ children }: { children: React.ReactNode }) => <>{children}</> }))
vi.mock("@/components/CompteAReboursBadge", () => ({ CompteAReboursBadge: () => <span>J-197</span> }))

import { PremiereSeance, choisirEssai } from "./PremiereSeance"

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null }
const CURSUS = [BEPC, { id: 3, examen: "BAC", examen_display: "BAC", series: { code: "A" } }]

const essai = (cursus: number, code: string, label: string, theme: string, nb = 0, total = 0) => ({
  cursus, cursus_display: "BEPC", langue: "fr" as const,
  subject: code.length, subject_label: label, subject_code: code,
  theme: theme.length, theme_name: theme, nb_questions: 5, nb_epreuves: nb, nb_epreuves_matiere: total,
})
const ESSAIS = [
  essai(14, "FRANCAIS", "Français", "connecteurs logiques", 20, 25),
  essai(14, "MATHS", "Mathématiques", "identité remarquable", 12, 28),
  essai(3, "PHILO", "Philosophie", "la conscience", 9, 20),
  essai(3, "ANGLAIS", "Anglais", "tenses", 15, 20),
]

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <PremiereSeance country="cm" />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  etat.choisi = null
  listQuizEssais.mockReset().mockResolvedValue(ESSAIS)
  lancerQuizGratuit.mockReset().mockResolvedValue("/quiz/session/7")
  declarer.mockReset()
  trackEvent.mockReset()
})

describe("choisirEssai : la séance offerte pour un examen", () => {
  it("les mathématiques quand elles existent, sinon le thème tombé dans le plus d'épreuves", () => {
    expect(choisirEssai(ESSAIS, 14)?.subject_code).toBe("MATHS")
    expect(choisirEssai(ESSAIS, 3)?.subject_code).toBe("ANGLAIS")
    expect(choisirEssai(ESSAIS, 99)).toBeNull()
  })
})

describe("PremiereSeance : la carte du hero de l'accueil", () => {
  it("sans examen déclaré : pose la question, et ne demande pas les essais", () => {
    afficher()
    expect(screen.getByRole("heading", { name: /Tu prépares quel examen/ })).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "BAC A" }))
    expect(declarer).toHaveBeenCalledWith(CURSUS[1], undefined, "hero")
    expect(listQuizEssais).not.toHaveBeenCalled()
  })

  it("examen déclaré : montre le thème, la matière, la fréquence, et lance la séance sans compte", async () => {
    etat.choisi = BEPC
    afficher()
    expect(await screen.findByRole("heading", { name: "Identité remarquable" })).toBeInTheDocument()
    expect(screen.getByText("Mathématiques")).toBeInTheDocument()
    expect(screen.getByText("Tombé dans 12 épreuves sur 28")).toBeInTheDocument()
    expect(screen.getByText("J-197")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: /Commencer, sans compte/ }))
    await waitFor(() =>
      expect(lancerQuizGratuit).toHaveBeenCalledWith(expect.objectContaining({ cursus: 14, connecte: false, source: "accueil_seance" })),
    )
    expect(trackEvent).toHaveBeenCalledWith("accueil_bouton_clic", { cible: "premiere_seance" })
  })

  it("une fréquence d'une seule épreuve n'est pas affichée", async () => {
    etat.choisi = BEPC
    listQuizEssais.mockResolvedValue([essai(14, "MATHS", "Mathématiques", "vitesse", 1, 28)])
    afficher()
    expect(await screen.findByRole("heading", { name: "Vitesse" })).toBeInTheDocument()
    expect(screen.queryByText(/Tombé dans/)).toBeNull()
  })

  it("aucun essai pour l'examen : renvoie vers les corrigés gratuits, sans promettre de séance", async () => {
    etat.choisi = BEPC
    listQuizEssais.mockResolvedValue([])
    afficher()
    expect(await screen.findByText(/Pas encore de séance d'essai pour BEPC/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Lire un corrigé gratuit/ })).toHaveAttribute("href", "/cm/epreuves?gratuit=true")
  })
})
