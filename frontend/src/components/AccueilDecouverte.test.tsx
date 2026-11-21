import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { listQuizEssais, getPlanDuJour, listMySubscriptions, getAccueil, lancerQuizGratuit, trackEvent } = vi.hoisted(() => ({
  listQuizEssais: vi.fn(),
  getPlanDuJour: vi.fn(),
  listMySubscriptions: vi.fn(),
  getAccueil: vi.fn(),
  lancerQuizGratuit: vi.fn(),
  trackEvent: vi.fn(),
}))
vi.mock("@/api/endpoints", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/endpoints")>()),
  listQuizEssais, getPlanDuJour, listMySubscriptions, getAccueil,
}))
vi.mock("@/lib/quizGratuit", () => ({ lancerQuizGratuit }))
vi.mock("@/lib/analytics", () => ({ trackEvent }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { id: 7, cursus_prepare: BAC_C, profil_actif: { id: 45, prenom: "Awa" }, a_un_abonnement_actif: false },
  }),
}))
// Le menu de changement d'examen, le compte à rebours, la ligne des points et le partage aux parents ont leurs propres tests.
vi.mock("@/components/ChoixExamen", () => ({ SelecteurExamen: ({ children }: { children: React.ReactNode }) => <>{children}</> }))
vi.mock("@/components/CompteAReboursBadge", () => ({ CompteAReboursBadge: () => <span>vers mai 2027</span> }))
vi.mock("@/components/LigneJour", () => ({
  LigneJour: ({ etat }: { etat: { xp: number; objectif: number } }) => <div>{etat.xp} / {etat.objectif} points</div>,
}))
vi.mock("@/components/BoutonParents", () => ({ BoutonParents: () => <button type="button">Montrer à mes parents</button> }))
vi.mock("@/components/ReprendreQuiz", () => ({ ReprendreQuiz: () => <p>Quiz en cours</p> }))

import { AccueilDecouverte } from "./AccueilDecouverte"
import { marquerSeancesJouees } from "@/lib/seancesGratuites"

const BAC_C = { id: 20, examen: "BAC", examen_display: "BAC", series: { code: "C" }, country: { code: "CM" } }

const essai = (code: string, label: string, theme: string, nb: number, total: number) => ({
  cursus: 20, cursus_display: "BAC C", langue: "fr" as const,
  subject: code.length, subject_label: label, subject_code: code,
  // Des noms de thème de longueurs différentes : la longueur sert d'identifiant du thème dans ces données.
  theme: theme.length, theme_name: theme, nb_questions: 6, nb_epreuves: nb, nb_epreuves_matiere: total,
})
const ESSAIS = [
  essai("PHILOSOPHIE", "Philosophie", "la conscience", 9, 20),
  essai("MATHS", "Mathématiques", "équation différentielle", 7, 45),
]
const THEME_MATHS = "équation différentielle".length
const THEME_PHILO = "la conscience".length

const PLAN = {
  etat: "plan_pret",
  cursus: BAC_C,
  compte_a_rebours: null,
  xp: { xp: 20, objectif: 50, atteint: false, objectifs_possibles: [30, 50, 80], niveau: { rang: 2, xp_total: 80, seuil: 60, seuil_suivant: 150 } },
  serie: { jours: 1, record: 1, actif_aujourdhui: true, repos_pris: false, semaine: [] },
  seance: {
    id: 323, origine: "PARCOURS", origine_display: "Parcours", verrouillee: true,
    subject: { id: 10, code: "MATHS", label: "Mathématiques" },
    theme: { id: 720, name: "tableau de variation" },
    savoir: null, duree_estimee_min: 25,
    etapes: [
      { type: "cours", libelle: "Relire la méthode", duree_min: 8 },
      { type: "exercice", libelle: "Un exercice tombé à l'examen", duree_min: 12 },
      { type: "quiz", libelle: "5 questions", duree_min: 5 },
    ],
    frequence: { occurrences: 28, epreuves_total: 45, annees: [] },
    raisons: [{ code: "coefficient", texte: "Mathématiques est coefficient 7 à ton examen." }],
  },
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cm"]}>
        <Routes>
          <Route path="/cm" element={<AccueilDecouverte country="cm" />} />
          <Route path="/quiz/session/7" element={<p>Question 1 sur 6</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  localStorage.clear()
  listQuizEssais.mockReset().mockResolvedValue(ESSAIS)
  getPlanDuJour.mockReset().mockResolvedValue(PLAN)
  listMySubscriptions.mockReset().mockResolvedValue([])
  getAccueil.mockReset()
  lancerQuizGratuit.mockReset().mockResolvedValue("/quiz/session/7")
  trackEvent.mockReset()
})

describe("AccueilDecouverte : « Aujourd'hui » pour un élève connecté sans abonnement", () => {
  it("ouvre sur la séance gratuite, qu'il peut faire, et la lance en un toucher", async () => {
    afficher()

    expect(await screen.findByText("Équation différentielle")).toBeInTheDocument()
    expect(screen.getByRole("heading", { level: 1, name: "Aujourd'hui" })).toBeInTheDocument()
    expect(screen.getByText("Bonjour Awa")).toBeInTheDocument()
    // Un quiz commencé se reprend d'ici, avant d'en lancer un autre.
    expect(screen.getByText("Quiz en cours")).toBeInTheDocument()
    expect(screen.getByText("Ta séance gratuite · 1 sur 2")).toBeInTheDocument()
    expect(screen.getByText("Tombé dans 7 épreuves sur 45")).toBeInTheDocument()
    // Plus de « Ta première séance », écrit pour quelqu'un qui n'a pas de compte.
    expect(screen.queryByText(/première séance/i)).toBeNull()

    fireEvent.click(screen.getByRole("button", { name: "Commencer" }))
    expect(await screen.findByText("Question 1 sur 6")).toBeInTheDocument()
    expect(lancerQuizGratuit).toHaveBeenCalledWith(expect.objectContaining({ cursus: 20, connecte: true, source: "accueil_seance" }))
    expect(trackEvent).toHaveBeenCalledWith("accueil_bouton_clic", { cible: "seance_gratuite" })
  })

  it("montre ses points, et la séance complète du jour fermée, avec le prix et un seul bouton", async () => {
    afficher()

    expect(await screen.findByText("20 / 50 points")).toBeInTheDocument()
    expect(await screen.findByText("La séance complète du jour")).toBeInTheDocument()
    expect(screen.getByText("Tableau de variation")).toBeInTheDocument()
    expect(screen.getByText("Tombé dans 28 épreuves sur 45")).toBeInTheDocument()
    for (const temps of ["Comprendre", "S'entraîner", "Vérifier"]) expect(screen.getByText(temps)).toBeInTheDocument()
    expect(screen.getByText("2 000 FCFA par mois, par Mobile Money (Orange ou MTN), sans engagement.")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Débloquer ma séance" })).toHaveAttribute("href", "/tarifs")
    // Jamais abonné : rien à retrouver, donc aucune demande de son historique.
    await waitFor(() => expect(listMySubscriptions).toHaveBeenCalled())
    expect(getAccueil).not.toHaveBeenCalled()
    expect(screen.queryByText(/Tu retrouves/)).toBeNull()
  })

  it("avance à la matière gratuite suivante une fois la première jouée sur cet appareil", async () => {
    marquerSeancesJouees(20, [THEME_MATHS])
    afficher()

    expect(await screen.findByText("La conscience")).toBeInTheDocument()
    expect(screen.getByText("Ta séance gratuite · 2 sur 2")).toBeInTheDocument()
    expect(screen.queryByText("Équation différentielle")).toBeNull()
  })

  it("toutes les séances gratuites jouées : il le lit, peut en refaire une, et la séance complète reste proposée", async () => {
    marquerSeancesJouees(20, [THEME_MATHS, THEME_PHILO])
    afficher()

    expect(await screen.findByText("Tu as fait les 2 séances gratuites")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Refaire une séance gratuite/ })).toHaveAttribute("href", "/quiz?cursus=20")
    expect(screen.queryByRole("button", { name: "Commencer" })).toBeNull()
    expect(await screen.findByRole("link", { name: "Débloquer ma séance" })).toBeInTheDocument()
  })

  it("ancien abonné : la date de fin, ce qu'il retrouve, et un seul bouton qui réabonne le bon profil", async () => {
    listMySubscriptions.mockResolvedValue([
      { is_active: false, expires_at: "2026-11-14T09:08:19+01:00", cursus: { id: 20 }, profil: { id: 45 } },
    ])
    getAccueil.mockResolvedValue({
      erreurs_total: 18,
      resume: [
        { subject_id: 10, en_revision: 9, maitrises: 3, en_cours: 2 },
        { subject_id: 11, en_revision: 3, maitrises: 0, en_cours: 0 },
      ],
    })
    afficher()

    expect(await screen.findByText(/Ton accès a pris fin le 14 novembre 2026/)).toBeInTheDocument()
    expect(await screen.findByText(
      "Tu retrouves ce que tu as construit : 12 thèmes en révision, 3 thèmes maîtrisés et 18 erreurs à refaire.",
    )).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Me réabonner" })).toHaveAttribute("href", "/abonnement?cursus=20&profil=45")
    expect(screen.queryByRole("link", { name: "Débloquer ma séance" })).toBeNull()
    // La séance gratuite reste la première chose de sa page.
    expect(screen.getByRole("button", { name: "Commencer" })).toBeInTheDocument()
  })

  it("ancien abonné sans rien de construit : pas de phrase vide", async () => {
    listMySubscriptions.mockResolvedValue([
      { is_active: false, expires_at: "2026-11-14T09:08:19+01:00", cursus: { id: 20 }, profil: { id: 45 } },
    ])
    getAccueil.mockResolvedValue({ erreurs_total: 0, resume: [{ subject_id: 10, en_revision: 0, maitrises: 0, en_cours: 0 }] })
    afficher()

    expect(await screen.findByRole("link", { name: "Me réabonner" })).toBeInTheDocument()
    await waitFor(() => expect(getAccueil).toHaveBeenCalled())
    expect(screen.queryByText(/Tu retrouves/)).toBeNull()
  })

  it("plan sans séance à proposer : la carte gratuite seule, sans bloc fermé", async () => {
    getPlanDuJour.mockResolvedValue({ ...PLAN, etat: "rien_a_proposer", seance: null })
    afficher()

    expect(await screen.findByText("Équation différentielle")).toBeInTheDocument()
    await waitFor(() => expect(getPlanDuJour).toHaveBeenCalled())
    expect(screen.queryByText("La séance complète du jour")).toBeNull()
  })
})
