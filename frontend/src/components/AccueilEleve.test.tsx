import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { Accueil } from "@/api/types"

const getAccueil = vi.hoisted(() => vi.fn())
const trackEvent = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  user: {
    id: 7,
    pseudo: "Awa",
    full_name: "Awa N.",
    cursus_prepare: { id: 4, examen: "BAC", examen_display: "BAC", series: { id: 1, code: "D", label: "Série D" }, country: { code: "CM" } },
    compte_a_rebours: { date_examen: "2027-06-12", jours_restants: 142, session_label: "BAC 2027", estimee: false },
    a_un_abonnement_actif: true,
    rappels_actifs: true,
    rappels_invite_refusee: false,
  },
}))

vi.mock("@/api/endpoints", () => ({
  getAccueil,
  getPlanDuJour: vi.fn(),
  terminerSeanceDuJour: vi.fn(),
  continuerSeanceDuJour: vi.fn(),
  proposerAutreChose: vi.fn(),
  ajusterDureeSeance: vi.fn(),
  definirObjectifMatiere: vi.fn(),
  retirerObjectifMatiere: vi.fn(),
  marquerEtapeOuverte: vi.fn(() => Promise.resolve()),
  startSimulation: vi.fn(),
  listEpreuvesInedites: vi.fn(() => Promise.resolve({ count: 0, results: [] })),
  listEpreuves: vi.fn(() => Promise.resolve({ count: 0, results: [] })),
  listCursus: vi.fn(() => Promise.resolve([])),
  listMySubscriptions: vi.fn(() => Promise.resolve([])),
}))
vi.mock("@/lib/analytics", () => ({ trackEvent }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/cursusAccueil", () => ({
  useCursusAccueil: () => 4,
  useInedites: () => ({ data: { count: 0, results: [] } }),
  requeteInedites: () => "",
}))

import { AccueilEleve } from "./AccueilEleve"

function accueil(surcharge: Partial<Accueil> = {}): Accueil {
  return {
    plan: {
      etat: "plan_pret",
      cursus: auth.user.cursus_prepare as never,
      compte_a_rebours: auth.user.compte_a_rebours,
      seances_cette_semaine: 2,
      serie: { jours: 3, record: 5, actif_aujourdhui: false, repos_pris: false },
      matieres_objectif: [],
      objectif_matiere: null,
      seance: {
        id: 11,
        origine: "PARCOURS",
        origine_display: "Parcours",
        subject: { id: 1, code: "MATHS", label: "Mathématiques", country: { id: 1, code: "CM", label: "Cameroun", dial_code: "+237", currency: "XAF", has_lessons: true } },
        theme: { id: 9, name: "dérivées" },
        savoir: null,
        duree_estimee_min: 25,
        budget_minutes: 25,
        budgets_possibles: [10, 25, 45],
        nb_etapes: 2,
        etapes: [
          { type: "cours", libelle: "Relire la méthode", slug: "cours-derivees", titre: "Dérivées", duree_min: 8, cle: "cours:cours-derivees", ouverte: false },
          { type: "quiz", libelle: "5 questions", mode: "PRATIQUE", n: 5, duree_min: 5, cle: "quiz", ouverte: false },
        ],
        frequence: { occurrences: 28, epreuves_total: 44, annees: [2025, 2024] },
        raisons: [],
        prochaine_revision: null,
        exercices_total: 3,
        statut: "PROPOSEE",
        score: null,
        verrouillee: false,
      },
    },
    phase: "normal",
    absence_jours: 0,
    premiers_pas: false,
    nouvelle_visite: true,
    phrase_coach: "Dérivées est tombé dans 28 des 44 dernières épreuves. 25 minutes pour ne pas le découvrir le jour J.",
    depuis: {
      depuis: "2026-09-27",
      seances: 2,
      questions: 12,
      themes_consolides_total: 1,
      themes_consolides: [{ theme: "limites", subject_label: "Mathématiques" }],
      matiere_en_hausse: { subject_id: 2, subject_label: "Chimie", gain: 8 },
      revisions_tenues: 1,
    },
    trajectoire: {
      jours_restants: 142,
      fenetre_jours: 21,
      seances_fenetre: 6,
      seances_par_semaine: 2,
      couverture_actuelle: 0.31,
      couverture_projetee: 0.62,
      cible: 0.8,
      suffisant: false,
      seances_de_plus_par_semaine: 1,
      atteignable: true,
    },
    resume: [
      { subject_id: 1, subject_code: "MATHS", subject_label: "Mathématiques", total: 10, maitrises: 3, en_revision: 1, en_cours: 2, a_decouvrir: 4, sans_contenu: 0, poids_total: 20, poids_maitrise: 7 },
      { subject_id: 2, subject_code: "CHIMIE", subject_label: "Chimie", total: 8, maitrises: 1, en_revision: 0, en_cours: 1, a_decouvrir: 6, sans_contenu: 0, poids_total: 8, poids_maitrise: 1 },
    ],
    preparation: { ponderee: 0.31, brute: 0.22, maitrises: 4, exploitables: 18 },
    revisions: [
      { id: 1, theme: "probabilités", theme_id: 5, subject_id: 1, subject_label: "Mathématiques", cursus: 4, jours_retard: 2 },
    ],
    lecture: { slug: "bac-d-maths-2024", title: "BAC D Maths 2024", country: "cm" },
    simulation_suggeree: null,
    bilan_semaine: null,
    ...surcharge,
  }
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cm"]}>
        <AccueilEleve country="cm" />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getAccueil.mockReset()
  trackEvent.mockReset()
  localStorage.clear()
})

describe("AccueilEleve", () => {
  it("rend toute la page depuis une seule réponse : phrase du coach, bouton, delta, trajectoire", async () => {
    getAccueil.mockResolvedValue(accueil())
    afficher()

    expect(await screen.findByText(/Dérivées est tombé dans 28 des 44/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Commencer la séance/ })).toHaveAttribute("href", "/cours/cours-derivees/lire")
    expect(screen.getByText(/Bonjour Awa/)).toBeInTheDocument()
    expect(screen.getByText("142")).toBeInTheDocument()
    // Depuis la dernière fois.
    expect(screen.getByText(/Depuis/)).toBeInTheDocument()
    expect(screen.getByText("Limites")).toBeInTheDocument()
    expect(screen.getByText(/monte de/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Probabilités/ })).toHaveAttribute("href", "/quiz?cursus=4&theme=5")
    expect(screen.getByRole("link", { name: /BAC D Maths 2024/ })).toHaveAttribute("href", "/cm/epreuves/bac-d-maths-2024/lire")
    // Trajectoire.
    expect(screen.getByText(/tu couvres 62 % de l'essentiel le jour J\. Une séance de plus par semaine/)).toBeInTheDocument()
    // Anneau pondéré : 31 %, pas le comptage brut (22 %).
    expect(screen.getAllByText("31").length).toBeGreaterThan(0)
    expect(getAccueil).toHaveBeenCalledTimes(1)
  })

  it("montre l'objectif d'XP du jour et la semaine de série", async () => {
    const base = accueil()
    getAccueil.mockResolvedValue(accueil({
      plan: {
        ...base.plan,
        xp: { xp: 10, objectif: 20, atteint: false, objectifs_possibles: [10, 20, 30] },
        serie: {
          jours: 3, record: 5, actif_aujourdhui: false, repos_pris: false,
          semaine: Array.from({ length: 7 }, (_, i) => ({ date: `2026-09-${28 + i}`, fait: i < 2, aujourdhui: i === 2 })),
        },
      },
    }))
    afficher()

    expect(await screen.findByText("10 / 20 XP")).toBeInTheDocument()
    expect(screen.getByText("Série de 3 jours")).toBeInTheDocument()
    expect(screen.getAllByRole("img", { name: "Travaillé" })).toHaveLength(2)
  })

  it("ne fait qu'un seul appel : le plan du jour n'est jamais refetché à part", async () => {
    getAccueil.mockResolvedValue(accueil())
    afficher()
    await screen.findByText(/Commencer la séance/)
    const { getPlanDuJour } = await import("@/api/endpoints")
    expect(getPlanDuJour).not.toHaveBeenCalled()
  })

  it("mesure le délai jusqu'au lancement de la séance", async () => {
    getAccueil.mockResolvedValue(accueil())
    afficher()
    await userEvent.click(await screen.findByRole("link", { name: /Commencer la séance/ }))
    const appel = trackEvent.mock.calls.find(([nom]) => nom === "plan_seance_demarree")
    expect(appel).toBeDefined()
    expect(typeof appel![1].delai_s).toBe("number")
  })

  it("garde la dernière version connue et l'affiche avant la réponse", async () => {
    getAccueil.mockResolvedValue(accueil())
    const premiere = afficher()
    await screen.findByText(/Commencer la séance/)
    premiere.unmount()

    // Deuxième ouverture : la réponse tarde, la page est déjà là.
    getAccueil.mockReturnValue(new Promise(() => {}))
    afficher()
    expect(screen.getByText(/Dérivées est tombé dans 28 des 44/)).toBeInTheDocument()
  })

  it("la veille : une checklist, pas de séance imposée", async () => {
    getAccueil.mockResolvedValue(accueil({ phase: "veille", phrase_coach: "C'est demain. Ce soir, on ne découvre rien : on relit, et on dort tôt." }))
    afficher()
    expect(await screen.findByText(/on prépare le sac/)).toBeInTheDocument()
    expect(screen.queryByRole("link", { name: /Commencer la séance/ })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: /Relire dix minutes/ }))
    expect(screen.getByRole("link", { name: /Commencer la séance/ })).toBeInTheDocument()
  })

  it("le jour J : bonne chance et rien d'autre", async () => {
    getAccueil.mockResolvedValue(accueil({ phase: "jour_j", phrase_coach: "C'est aujourd'hui." }))
    afficher()
    expect(await screen.findByText("Bonne chance")).toBeInTheDocument()
    expect(screen.queryByRole("link", { name: /Commencer la séance/ })).not.toBeInTheDocument()
  })

  it("après l'examen : on demande comment ça s'est passé, une seule fois", async () => {
    getAccueil.mockResolvedValue(accueil({
      phase: "apres",
      plan: { etat: "examen_passe", cursus: null, compte_a_rebours: null, seance: null },
      trajectoire: null,
    }))
    afficher()
    await userEvent.click(await screen.findByRole("button", { name: "Plutôt bien" }))
    expect(trackEvent).toHaveBeenCalledWith("examen_ressenti", { ressenti: "bien" })
    expect(screen.getByText("Merci")).toBeInTheDocument()
  })

  it("à un mois : l'annale suggérée en action secondaire", async () => {
    getAccueil.mockResolvedValue(accueil({
      phase: "simulation",
      simulation_suggeree: { id: 3, slug: "bac-d-maths-2025", title: "BAC D Maths 2025", subject_label: "Mathématiques", year: 2025 },
    }))
    afficher()
    expect(await screen.findByRole("button", { name: /conditions d'examen/ })).toBeInTheDocument()
    expect(screen.getByText(/Annale suggérée : Mathématiques 2025/)).toBeInTheDocument()
    expect(screen.getByText("Mois des annales")).toBeInTheDocument()
  })

  it("premiers pas : ni delta ni révisions inventées, la séance seulement", async () => {
    getAccueil.mockResolvedValue(accueil({ premiers_pas: true, depuis: null, trajectoire: null, revisions: [], lecture: null }))
    afficher()
    expect(await screen.findByRole("link", { name: /Commencer la séance/ })).toBeInTheDocument()
    expect(screen.queryByText(/Depuis/)).not.toBeInTheDocument()
    expect(screen.queryByText(/D'ici le jour J/)).not.toBeInTheDocument()
  })

  it("un moment se montre une fois puis se ferme", async () => {
    getAccueil.mockResolvedValue(accueil({
      plan: { ...accueil().plan, serie: { jours: 7, record: 7, actif_aujourdhui: true, repos_pris: false } },
    }))
    afficher()
    // Le bandeau du coach dit aussi "7 jours de suite" : on vise le moment lui-même.
    expect(await screen.findByRole("region", { name: "7 jours de suite" })).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Fermer" }))
    expect(screen.queryByRole("region", { name: "7 jours de suite" })).not.toBeInTheDocument()
  })
})
