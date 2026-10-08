import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { Accueil, EtapeSeance } from "@/api/types"

const getAccueil = vi.hoisted(() => vi.fn())
const listMyTentativesInedites = vi.hoisted(() => vi.fn())
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
  listMyTentativesInedites,
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
  listMyTentativesInedites.mockReset()
  listMyTentativesInedites.mockResolvedValue([])
  trackEvent.mockReset()
  localStorage.clear()
})

describe("AccueilEleve", () => {
  it("rend toute la page depuis une seule réponse : phrase du coach, bouton, delta, trajectoire", async () => {
    getAccueil.mockResolvedValue(accueil())
    afficher()

    expect(await screen.findByText(/Dérivées est tombé dans 28 des 44/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Commencer :/ })).toHaveAttribute("href", "/cours/cours-derivees/lire")
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
    // Sous le bouton principal, pas avant lui : en tête de carte, elle le repoussait sous le pli.
    const commencer = screen.getByRole("link", { name: /Commencer :/ })
    expect(commencer.compareDocumentPosition(screen.getByText("10 / 20 XP"))).toBe(Node.DOCUMENT_POSITION_FOLLOWING)
    expect(screen.getByText("3 jours de suite")).toBeInTheDocument()
    expect(screen.getAllByRole("img", { name: "Travaillé" })).toHaveLength(2)
  })

  it("dit « Objectif atteint » plutôt que 35 / 20 XP", async () => {
    const base = accueil()
    getAccueil.mockResolvedValue(accueil({
      plan: { ...base.plan, xp: { xp: 35, objectif: 20, atteint: true, objectifs_possibles: [10, 20, 30] } },
    }))
    afficher()
    expect(await screen.findByText("Objectif atteint")).toBeInTheDocument()
    expect(screen.queryByText(/35 \/ 20/)).not.toBeInTheDocument()
  })

  describe("la reprise d'une épreuve inédite", () => {
    const tentative = {
      id: 31, epreuve: 3, epreuve_titre: "Mathématiques BAC D – Épreuve blanche n°1", subject_label: "Mathématiques",
      cursus_display: "BAC - Série D", started_at: "2026-10-03T08:00:00Z", exam_mode_started_at: null, echeance: null,
      submitted_at: null, score_obtenu: null, note_obtenue: null, bareme_snapshot: null,
    }

    it("propose de reprendre la copie en cours, vers la tentative elle-même", async () => {
      getAccueil.mockResolvedValue(accueil())
      listMyTentativesInedites.mockResolvedValue([tentative])
      afficher()

      const lien = await screen.findByRole("link", { name: /Épreuve blanche n°1/ })
      expect(lien).toHaveAttribute("href", "/inedit/tentative/31")
      expect(lien).toHaveTextContent("Reprendre")
    })

    it("dit ce qu'il reste de chrono quand il tourne", async () => {
      getAccueil.mockResolvedValue(accueil())
      listMyTentativesInedites.mockResolvedValue([
        { ...tentative, exam_mode_started_at: "2026-10-04T08:00:00Z", echeance: new Date(Date.now() + 75 * 60_000).toISOString() },
      ])
      afficher()

      expect(await screen.findByText(/Chrono en cours · il te reste 1:1\d:\d\d/)).toBeInTheDocument()
    })

    it("ne propose rien quand toutes les copies sont rendues", async () => {
      getAccueil.mockResolvedValue(accueil())
      listMyTentativesInedites.mockResolvedValue([{ ...tentative, submitted_at: "2026-10-03T09:00:00Z" }])
      afficher()

      await screen.findByText(/Dérivées est tombé dans 28 des 44/)
      expect(screen.queryByText("Reprendre")).not.toBeInTheDocument()
    })
  })

  describe("le bouton principal et le quiz", () => {
    it("nomme l'étape où il mène, et propose le quiz en direct tant qu'il n'est pas ouvert", async () => {
      getAccueil.mockResolvedValue(accueil())
      afficher()
      expect(await screen.findByRole("link", { name: /Commencer : relire la méthode/ })).toBeInTheDocument()
      const express = screen.getByRole("link", { name: /Quiz express/ })
      expect(express).toHaveAttribute("href", expect.stringContaining("/quiz?"))
      expect(express).toHaveAttribute("href", expect.stringContaining("seance=11"))
      expect(express).toHaveTextContent("5 questions · jusqu'à 50 XP")
    })

    it("mène au quiz et n'en double pas l'accès quand c'est la prochaine étape", async () => {
      const base = accueil()
      const etapes = (base.plan.seance!.etapes as EtapeSeance[]).map((e) => ({ ...e, ouverte: e.type !== "quiz" }))
      getAccueil.mockResolvedValue(accueil({
        plan: { ...base.plan, seance: { ...base.plan.seance!, etapes } },
      }))
      afficher()
      expect(await screen.findByRole("link", { name: /Reprendre : faire le quiz/ })).toBeInTheDocument()
      expect(screen.queryByRole("link", { name: /Quiz express/ })).not.toBeInTheDocument()
    })

    it("ne propose plus le quiz express une fois le quiz ouvert", async () => {
      const base = accueil()
      const etapes = (base.plan.seance!.etapes as EtapeSeance[]).map((e) => ({ ...e, ouverte: true }))
      getAccueil.mockResolvedValue(accueil({
        plan: { ...base.plan, seance: { ...base.plan.seance!, etapes } },
      }))
      afficher()
      await screen.findByRole("link", { name: /Reprendre :/ })
      expect(screen.queryByRole("link", { name: /Quiz express/ })).not.toBeInTheDocument()
    })

    it("compte le démarrage une fois, avec l'entrée par le quiz express", async () => {
      getAccueil.mockResolvedValue(accueil())
      afficher()
      await userEvent.click(await screen.findByRole("link", { name: /Quiz express/ }))
      const appel = trackEvent.mock.calls.find(([nom]) => nom === "plan_seance_demarree")
      expect(appel![1]).toMatchObject({ entree: "quiz_express" })
    })

    it("le quiz valide la séance : pas de « J'ai fini » quand il y en a un", async () => {
      getAccueil.mockResolvedValue(accueil())
      afficher()
      await screen.findByRole("link", { name: /Commencer :/ })
      expect(screen.queryByRole("button", { name: /J'ai fini/ })).not.toBeInTheDocument()
    })

    it("garde « J'ai fini » pour une séance sans quiz", async () => {
      const base = accueil()
      const etapes = (base.plan.seance!.etapes as EtapeSeance[]).filter((e) => e.type !== "quiz")
      getAccueil.mockResolvedValue(accueil({
        plan: { ...base.plan, seance: { ...base.plan.seance!, etapes, nb_etapes: etapes.length } },
      }))
      afficher()
      expect(await screen.findByRole("button", { name: /J'ai fini/ })).toBeInTheDocument()
      expect(screen.queryByRole("link", { name: /Quiz express/ })).not.toBeInTheDocument()
    })

    it("le parcours tient sur une ligne, et son détail s'ouvre à la demande", async () => {
      getAccueil.mockResolvedValue(accueil())
      afficher()
      await screen.findByRole("link", { name: /Commencer :/ })
      expect(screen.getByText("Comprendre")).toBeInTheDocument()
      expect(screen.getByText("Vérifier")).toBeInTheDocument()
      expect(screen.queryByText("· valide la séance")).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: "Voir le détail" }))
      expect(screen.getByText("· valide la séance")).toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: "Réduire" }))
      expect(screen.queryByText("· valide la séance")).not.toBeInTheDocument()
    })

    it("le quiz sort du rang dans « Ton parcours » avec l'XP qu'il peut rapporter", async () => {
      getAccueil.mockResolvedValue(accueil())
      afficher()
      await userEvent.click(await screen.findByRole("button", { name: "Voir le détail" }))
      expect(screen.getByText("· valide la séance")).toBeInTheDocument()
      expect(screen.getAllByText("jusqu'à 50 XP").length).toBeGreaterThan(0)
    })

    it("les années ne s'affichent qu'au clic sur la pastille de fréquence", async () => {
      getAccueil.mockResolvedValue(accueil())
      afficher()
      const pastille = await screen.findByRole("button", { name: /Tombé dans 28 épreuves sur 44/ })
      expect(screen.queryByText(/2025 · 2024/)).not.toBeInTheDocument()
      await userEvent.click(pastille)
      expect(screen.getByText(/2025 · 2024/)).toBeInTheDocument()
    })

    it("un vrai compte à rebours garde la grande bande ; une date estimée la réduit à une ligne", async () => {
      getAccueil.mockResolvedValue(accueil())
      const exact = afficher()
      await screen.findByRole("link", { name: /Commencer :/ })
      expect(document.querySelector("section[aria-label=\"Aujourd'hui\"] .bg-gradient-to-br")).not.toBeNull()
      exact.unmount()
      localStorage.clear() // la dernière version connue (cache local) montrerait encore l'ancien compte

      const avant = auth.user.compte_a_rebours
      auth.user.compte_a_rebours = { date_examen: "2027-06-12", jours_restants: 240, session_label: "BAC 2027", estimee: true }
      try {
        // Sans anneau de préparation : il garderait la grande bande à lui seul.
        getAccueil.mockResolvedValue(accueil({ preparation: null, plan: { ...accueil().plan, compte_a_rebours: auth.user.compte_a_rebours } }))
        afficher()
        await screen.findByRole("link", { name: /Commencer :/ })
        expect(document.querySelector("section[aria-label=\"Aujourd'hui\"] .bg-gradient-to-br")).toBeNull()
        expect(screen.getByText(/Bonjour Awa/)).toBeInTheDocument()
        expect(screen.getByText(/Examen vers juin 2027/)).toBeInTheDocument()
      } finally {
        auth.user.compte_a_rebours = avant
      }
    })

    it("la phrase du coach suit le titre du thème, elle n'est pas dans la bande", async () => {
      getAccueil.mockResolvedValue(accueil())
      afficher()
      const phrase = await screen.findByText(/Dérivées est tombé dans 28 des 44/)
      const titre = screen.getByRole("heading", { level: 2, name: /Aujourd'hui/ })
      expect(titre.compareDocumentPosition(phrase)).toBe(Node.DOCUMENT_POSITION_FOLLOWING)
      expect(phrase.closest(".bg-gradient-to-br")).toBeNull()
    })

    it("verrouillée : un seul bouton, celui qui débloque, et le parcours en entier", async () => {
      const base = accueil()
      getAccueil.mockResolvedValue(accueil({
        plan: {
          ...base.plan,
          seance: {
            ...base.plan.seance!,
            verrouillee: true,
            etapes: [
              { type: "cours", libelle: "Relire la méthode", duree_min: 8 },
              { type: "quiz", libelle: "5 questions", duree_min: 5 },
            ],
          },
        },
      }))
      afficher()
      expect(await screen.findByRole("link", { name: /Débloquer ma séance/ })).toHaveAttribute("href", "/tarifs")
      expect(screen.queryByRole("button", { name: /Commencer la séance/ })).not.toBeInTheDocument()
      expect(screen.queryByRole("button", { name: /Voir le détail/ })).not.toBeInTheDocument()
      expect(screen.getByText("· valide la séance")).toBeInTheDocument()
    })

    it("séance faite : « Demain, on continue » n'est dit qu'une fois", async () => {
      const base = accueil()
      getAccueil.mockResolvedValue(accueil({
        plan: { ...base.plan, etat: "deja_fait_aujourdhui", seance: { ...base.plan.seance!, statut: "TERMINEE" } },
        phrase_coach: "Séance faite. Demain, on continue.",
      }))
      afficher()
      expect(await screen.findByRole("button", { name: /Continuer maintenant/ })).toBeInTheDocument()
      expect(screen.queryByText("Prochaine séance demain.")).not.toBeInTheDocument()
    })

    it("montre deux raisons au plus, la plus personnelle d'abord", async () => {
      const base = accueil()
      getAccueil.mockResolvedValue(accueil({
        plan: {
          ...base.plan,
          seance: {
            ...base.plan.seance!,
            raisons: [
              { code: "coefficient", texte: "Mathématiques est coefficient 4 à ton examen." },
              { code: "maitrise", texte: "Tu réussis déjà ce thème : on passe directement à la pratique." },
              { code: "jamais", texte: "Tu ne l'as encore jamais travaillé." },
            ],
          },
        },
      }))
      afficher()
      await screen.findByRole("link", { name: /Commencer :/ })
      const items = screen.getAllByRole("listitem").map((li) => li.textContent)
      const iJamais = items.findIndex((t) => t?.includes("jamais travaillé"))
      const iMaitrise = items.findIndex((t) => t?.includes("Tu réussis déjà"))
      expect(iJamais).toBeGreaterThanOrEqual(0)
      expect(iJamais).toBeLessThan(iMaitrise)
      expect(screen.queryByText(/coefficient 4/)).not.toBeInTheDocument()
    })

    it("ne redit pas un ratage que la phrase du coach énonce déjà", async () => {
      const base = accueil()
      getAccueil.mockResolvedValue(accueil({
        plan: {
          ...base.plan,
          seance: {
            ...base.plan.seance!,
            origine: "REVISION_DUE",
            raisons: [
              { code: "echec", texte: "Tu as raté ce thème hier." },
              { code: "coefficient", texte: "Mathématiques est coefficient 4 à ton examen." },
            ],
          },
        },
        phrase_coach: "Tu as raté Dérivées hier. 25 minutes pour le fixer avant qu'il ne s'efface.",
      }))
      afficher()
      await screen.findByRole("link", { name: /Commencer :/ })
      expect(screen.getAllByText(/Tu as raté/)).toHaveLength(1)
      expect(screen.getByText(/coefficient 4/)).toBeInTheDocument()
    })
  })

  it("n'affiche pas un anneau de préparation à 1 % : il décourage plus qu'il n'informe", async () => {
    getAccueil.mockResolvedValue(accueil({ preparation: { ponderee: 0.01, brute: 0.01, maitrises: 0, exploitables: 18 } }))
    afficher()
    await screen.findByRole("link", { name: /Commencer :/ })
    expect(screen.queryByRole("img", { name: /de ce qui tombe à l'examen est maîtrisé/ })).not.toBeInTheDocument()
  })

  it("affiche l'anneau de préparation dès qu'il a de quoi dire", async () => {
    getAccueil.mockResolvedValue(accueil())
    afficher()
    expect(await screen.findByRole("img", { name: "31 % de ce qui tombe à l'examen est maîtrisé" })).toBeInTheDocument()
  })

  it("ne fait qu'un seul appel : le plan du jour n'est jamais refetché à part", async () => {
    getAccueil.mockResolvedValue(accueil())
    afficher()
    await screen.findByText(/Commencer :/)
    const { getPlanDuJour } = await import("@/api/endpoints")
    expect(getPlanDuJour).not.toHaveBeenCalled()
  })

  it("mesure le délai jusqu'au lancement de la séance", async () => {
    getAccueil.mockResolvedValue(accueil())
    afficher()
    await userEvent.click(await screen.findByRole("link", { name: /Commencer :/ }))
    const appel = trackEvent.mock.calls.find(([nom]) => nom === "plan_seance_demarree")
    expect(appel).toBeDefined()
    expect(typeof appel![1].delai_s).toBe("number")
  })

  it("garde la dernière version connue et l'affiche avant la réponse", async () => {
    getAccueil.mockResolvedValue(accueil())
    const premiere = afficher()
    await screen.findByText(/Commencer :/)
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
    // Sans séance à titrer, le mot du coach reste dans la bande.
    expect(screen.getByText(/C'est demain\. Ce soir/).closest(".bg-gradient-to-br")).not.toBeNull()
    expect(screen.queryByRole("link", { name: /Commencer :/ })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: /Relire dix minutes/ }))
    expect(screen.getByRole("link", { name: /Commencer :/ })).toBeInTheDocument()
  })

  it("le jour J : bonne chance et rien d'autre", async () => {
    getAccueil.mockResolvedValue(accueil({ phase: "jour_j", phrase_coach: "C'est aujourd'hui." }))
    afficher()
    expect(await screen.findByText("Bonne chance")).toBeInTheDocument()
    expect(screen.queryByRole("link", { name: /Commencer :/ })).not.toBeInTheDocument()
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
    expect(await screen.findByRole("link", { name: /Commencer :/ })).toBeInTheDocument()
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
