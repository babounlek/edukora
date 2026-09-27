import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"
import type { NotationResume, TentativeInedite, TentativeInediteQuestion } from "@/api/types"

const api = vi.hoisted(() => ({
  answerTentativeQuestion: vi.fn(),
  completeTentative: vi.fn(),
  downloadSujetPdf: vi.fn(),
  getTentativeInedite: vi.fn(),
  noterTentativeQuestion: vi.fn(),
  startExamMode: vi.fn(),
  toggleQuestionMarquee: vi.fn(),
  getSimulation: vi.fn(),
  startSimulationExam: vi.fn(),
  noterSimulationExercice: vi.fn(),
  marquerSimulationExercice: vi.fn(),
  completeSimulation: vi.fn(),
}))
// toast est aussi appelable directement (repères de temps, hors connexion), pas seulement toast.error.
const toast = vi.hoisted(() => Object.assign(vi.fn(), { error: vi.fn(), success: vi.fn() }))

vi.mock("@/api/endpoints", () => api)
vi.mock("sonner", () => ({ toast }))
// Le rendu Markdown/KaTeX n'est pas ce qui est testé ici (voir audit-rendu.test.ts).
vi.mock("@/components/EpreuveMarkdown", () => ({
  EpreuveMarkdown: ({ markdown }: { markdown: string }) => <div>{markdown}</div>,
}))

import { InediteTentativePage } from "./InediteTentativePage"

function question(id: number, numero: string, extra: Partial<TentativeInediteQuestion> = {}): TentativeInediteQuestion {
  return {
    id, numero, ordre: id, groupe_local: "", enonce_markdown: `Énoncé ${numero}`, type_reponse: "OUVERTE",
    choix: [], traitee: false, points: 4, bareme_estime: false, ...extra,
  }
}

function notation(extra: Partial<NotationResume> = {}): NotationResume {
  return {
    note: 0, bareme: 8, note_sur_20: 0, bareme_estime: false, questions_total: 2, questions_traitees: 0,
    questions_non_traitees: 2, questions_a_noter: 0, definitive: false, ...extra,
  }
}

function tentative(extra: Partial<TentativeInedite> = {}): TentativeInedite {
  return {
    id: 7, epreuve: 1, epreuve_titre: "Épreuve", country: "CM", cursus_display: "BAC - Série C",
    duree_minutes: 120, sujet_pdf_disponible: false, started_at: "2026-09-26T10:00:00Z",
    exam_mode_started_at: null, mode_papier: false, submitted_at: null, score_obtenu: null, note_obtenue: null, bareme_snapshot: null,
    bareme: 8, bareme_estime: false, notation: notation(), correction_disponible: true, questions_marquees: [],
    exercices: [{
      id: 1, numero_exercice: "1", points: "8", groupes: [], enonce_intro_markdown: "",
      questions: [
        question(1, "1", { corrige_markdown: "Corrigé 1", criteres_notation: [] }),
        question(2, "2", { corrige_markdown: "Corrigé 2", criteres_notation: [] }),
      ],
    }],
    ...extra,
  }
}

function afficher(source: "inedit" | "officielle" = "inedit") {
  const chemin = source === "officielle" ? "/simulation/7" : "/inedit/tentative/7"
  return render(
    <MemoryRouter initialEntries={[chemin]}>
      <Routes>
        <Route path={source === "officielle" ? "/simulation/:id" : "/inedit/tentative/:id"} element={<InediteTentativePage source={source} />} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  Object.values(api).forEach((mock) => mock.mockReset())
  toast.mockReset()
  sessionStorage.clear()
  toast.error.mockReset()
  window.scrollTo = vi.fn()
})

describe("InediteTentativePage", () => {
  it("marque une question traitée : appel serveur, avancement et note mis à jour", async () => {
    api.getTentativeInedite.mockResolvedValue(tentative())
    api.noterTentativeQuestion.mockResolvedValue({
      ...question(1, "1", { traitee: true, corrige_markdown: "Corrigé 1", criteres_notation: [] }),
      reponse: { reponse_choisie: "", resultat_declare: "", notee: false },
      notation: notation({ questions_traitees: 1, questions_non_traitees: 1, questions_a_noter: 1 }),
    })
    afficher()

    const boutons = await screen.findAllByRole("checkbox", { name: /J'ai traité cette question/ })
    await userEvent.click(boutons[0])

    await waitFor(() => expect(api.noterTentativeQuestion).toHaveBeenCalledWith(7, 1, { traitee: true }))
    expect(await screen.findByText("1 / 2 traitées")).toBeInTheDocument()
  })

  it("annule le geste et prévient l'élève quand l'enregistrement échoue", async () => {
    api.getTentativeInedite.mockResolvedValue(tentative())
    api.noterTentativeQuestion.mockRejectedValue(new ApiError(500, { error: "Erreur serveur" }))
    afficher()

    const boutons = await screen.findAllByRole("checkbox", { name: /J'ai traité cette question/ })
    await userEvent.click(boutons[0])

    await waitFor(() => expect(toast.error).toHaveBeenCalled())
    expect(screen.getByText("0 / 2 traitées")).toBeInTheDocument()
    expect(screen.getAllByRole("checkbox", { name: /J'ai traité cette question/ })).toHaveLength(2)
  })

  it("demande confirmation avant de rendre la copie et liste les questions non traitées", async () => {
    api.getTentativeInedite.mockResolvedValue(tentative())
    api.completeTentative.mockResolvedValue({})
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: /Terminer/ }))

    const dialogue = await screen.findByRole("dialog")
    expect(within(dialogue).getByText(/2 questions non traitées valent 0 point/)).toBeInTheDocument()
    expect(within(dialogue).getByRole("button", { name: "Ex. 1 · Q1" })).toBeInTheDocument()
    expect(api.completeTentative).not.toHaveBeenCalled()

    api.getTentativeInedite.mockResolvedValue(
      tentative({ submitted_at: "2026-09-26T11:00:00Z", notation: notation({ definitive: true }) }),
    )
    await userEvent.click(within(dialogue).getByRole("button", { name: /Terminer et voir le corrigé/ }))

    await waitFor(() => expect(api.completeTentative).toHaveBeenCalledWith(7))
    // Aucune question traitée : la note est définitive (0), sans rien à noter.
    expect(await screen.findByText(/Aucune question traitée · ta note/)).toBeInTheDocument()
  })

  it("ne cache jamais le corrigé ni la note en plein mode examen", async () => {
    api.getTentativeInedite.mockResolvedValue(
      tentative({
        exam_mode_started_at: new Date().toISOString(), correction_disponible: false, notation: null,
        exercices: [{
          id: 1, numero_exercice: "1", points: "8", groupes: [], enonce_intro_markdown: "",
          questions: [question(1, "1"), question(2, "2")],
        }],
      }),
    )
    afficher()

    await screen.findAllByRole("checkbox", { name: /J'ai traité cette question/ })

    expect(screen.queryByText(/Corrigé 1/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Provisoire/)).not.toBeInTheDocument()
    expect(screen.getByRole("timer")).toBeInTheDocument()
  })

  it("note une question sans grille par niveau rapide, une fois le corrigé ouvert", async () => {
    const traitee = (extra: Partial<TentativeInediteQuestion> = {}) =>
      question(1, "1", {
        traitee: true, corrige_markdown: "Corrigé 1", criteres_notation: [],
        reponse: { reponse_choisie: "", resultat_declare: "", notee: false }, ...extra,
      })
    api.getTentativeInedite.mockResolvedValue(
      tentative({
        submitted_at: "2026-09-26T11:00:00Z",
        notation: notation({ questions_traitees: 1, questions_non_traitees: 1, questions_a_noter: 1 }),
        exercices: [{
          id: 1, numero_exercice: "1", points: "8", groupes: [], enonce_intro_markdown: "",
          questions: [traitee(), question(2, "2", { corrige_markdown: "Corrigé 2" })],
        }],
      }),
    )
    api.noterTentativeQuestion.mockResolvedValue({
      ...traitee({ reponse: { reponse_choisie: "", resultat_declare: "REUSSI", notee: true, points_obtenus: 4 } }),
      notation: notation({ note: 4, questions_traitees: 1, questions_non_traitees: 1, definitive: true }),
    })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: /Réussi/ }))

    await waitFor(() => expect(api.noterTentativeQuestion).toHaveBeenCalledWith(7, 1, { points_obtenus: 4 }))
    expect(await screen.findByText(/Notation terminée/)).toBeInTheDocument()
  })

  it("coche des critères et envoie leurs indices", async () => {
    const grille = [{ libelle: "Cite la formule", points: 1 }, { libelle: "Calcule juste", points: 3 }]
    api.getTentativeInedite.mockResolvedValue(
      tentative({
        submitted_at: "2026-09-26T11:00:00Z",
        notation: notation({ questions_traitees: 1, questions_a_noter: 1 }),
        exercices: [{
          id: 1, numero_exercice: "1", points: "4", groupes: [], enonce_intro_markdown: "",
          questions: [question(1, "1", {
            traitee: true, corrige_markdown: "Corrigé 1", criteres_notation: grille,
            reponse: { reponse_choisie: "", resultat_declare: "", notee: false },
          })],
        }],
      }),
    )
    api.noterTentativeQuestion.mockResolvedValue({
      ...question(1, "1", { traitee: true, criteres_notation: grille }),
      reponse: { reponse_choisie: "", resultat_declare: "PARTIEL", notee: true, criteres_valides: [1], points_obtenus: 3 },
      notation: notation({ note: 3, definitive: true }),
    })
    afficher()

    await userEvent.click(await screen.findByRole("checkbox", { name: /Calcule juste/ }))

    await waitFor(() => expect(api.noterTentativeQuestion).toHaveBeenCalledWith(7, 1, { criteres_valides: [1] }))
  })

  describe("salle d'examen", () => {
    const enExamen = (extra: Partial<TentativeInedite> = {}) =>
      tentative({
        exam_mode_started_at: new Date().toISOString(), correction_disponible: false, notation: null,
        exercices: [{
          id: 1, numero_exercice: "1", points: "8", groupes: [], enonce_intro_markdown: "",
          questions: [question(1, "1"), question(2, "2")],
        }],
        ...extra,
      })

    it("propose le briefing tant que rien n'est engagé, puis le laisse partir en entraînement libre", async () => {
      api.getTentativeInedite.mockResolvedValue(tentative({ sujet_pdf_disponible: true }))
      afficher()

      expect(await screen.findByRole("heading", { name: "Comment veux-tu la passer ?" })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /Conditions réelles/ })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /Sur papier/ })).toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /Entraînement libre/ }))

      expect(screen.queryByRole("heading", { name: "Comment veux-tu la passer ?" })).not.toBeInTheDocument()
    })

    it("ne propose le papier que quand un sujet PDF existe", async () => {
      api.getTentativeInedite.mockResolvedValue(tentative({ sujet_pdf_disponible: false }))
      afficher()

      await screen.findByRole("heading", { name: "Comment veux-tu la passer ?" })
      expect(screen.queryByRole("button", { name: /Sur papier/ })).not.toBeInTheDocument()
    })

    it("lance le chrono en conditions réelles seulement après confirmation", async () => {
      api.getTentativeInedite.mockResolvedValue(tentative())
      api.startExamMode.mockResolvedValue(enExamen())
      afficher()

      await userEvent.click(await screen.findByRole("button", { name: /Conditions réelles/ }))
      expect(api.startExamMode).not.toHaveBeenCalled()

      await userEvent.click(await screen.findByRole("button", { name: "Lancer le chrono" }))

      await waitFor(() => expect(api.startExamMode).toHaveBeenCalledWith(7, { papier: false }))
      expect(await screen.findByRole("timer")).toBeInTheDocument()
    })

    it("lance le mode papier et n'affiche plus les énoncés que dans un repli", async () => {
      api.getTentativeInedite.mockResolvedValue(tentative({ sujet_pdf_disponible: true }))
      api.startExamMode.mockResolvedValue(enExamen({ mode_papier: true, sujet_pdf_disponible: true }))
      afficher()

      await userEvent.click(await screen.findByRole("button", { name: /Sur papier/ }))
      await userEvent.click(await screen.findByRole("button", { name: "Lancer le chrono" }))

      await waitFor(() => expect(api.startExamMode).toHaveBeenCalledWith(7, { papier: true }))
      expect(await screen.findByText(/Tu composes sur papier/)).toBeInTheDocument()
      expect(screen.getAllByText("Voir l'énoncé à l'écran")).toHaveLength(2)
    })

    it("prévient qu'un chrono ne s'arrête pas quand on quitte l'épreuve", async () => {
      api.getTentativeInedite.mockResolvedValue(enExamen())
      afficher()

      await userEvent.click(await screen.findByRole("link", { name: /Quitter l'épreuve/ }))

      expect(await screen.findByText(/Le chrono continue de tourner/)).toBeInTheDocument()
    })

    it("allume la salle d'examen pendant le chrono et l'éteint en sortant", async () => {
      const { useModeExamen } = await import("@/lib/modeExamen")
      let vu = false
      function Sonde() {
        vu = useModeExamen()
        return null
      }
      api.getTentativeInedite.mockResolvedValue(enExamen())
      const { unmount } = render(
        <MemoryRouter initialEntries={["/inedit/tentative/7"]}>
          <Sonde />
          <Routes>
            <Route path="/inedit/tentative/:id" element={<InediteTentativePage />} />
          </Routes>
        </MemoryRouter>,
      )

      await screen.findAllByRole("checkbox", { name: /J'ai traité cette question/ })
      await waitFor(() => expect(vu).toBe(true))

      unmount()
      const { definirModeExamen } = await import("@/lib/modeExamen")
      expect(typeof definirModeExamen).toBe("function")
    })

    it("garde la case cochée hors connexion et l'envoie au retour du réseau", async () => {
      api.getTentativeInedite.mockResolvedValue(enExamen())
      api.noterTentativeQuestion.mockRejectedValueOnce(new TypeError("Failed to fetch"))
      afficher()

      const cases = await screen.findAllByRole("checkbox", { name: /J'ai traité cette question/ })
      await userEvent.click(cases[0])

      expect(await screen.findByText(/1 changement en attente/)).toBeInTheDocument()
      expect(screen.getByText("1 / 2 traitées")).toBeInTheDocument()
      expect(toast.error).not.toHaveBeenCalled()

      api.noterTentativeQuestion.mockResolvedValue({
        ...question(1, "1", { traitee: true }),
        reponse: { reponse_choisie: "", resultat_declare: "", notee: false },
        notation: null,
      })
      window.dispatchEvent(new Event("online"))

      await waitFor(() => expect(api.noterTentativeQuestion).toHaveBeenCalledTimes(2))
      await waitFor(() => expect(screen.queryByText(/changement en attente/)).not.toBeInTheDocument())
    })

    it("la carte de l'épreuve montre l'état de chaque question et y conduit", async () => {
      api.getTentativeInedite.mockResolvedValue(
        enExamen({
          exercices: [{
            id: 1, numero_exercice: "1", points: "8", groupes: [], enonce_intro_markdown: "",
            questions: [question(1, "1", { traitee: true }), question(2, "2")],
          }],
        }),
      )
      afficher()

      await screen.findAllByRole("checkbox", { name: /J'ai traité cette question|Question traitée/ })
      const traitee = screen.getAllByRole("button", { name: "Exercice 1, question 1, traitée" })[0]
      const pasTraitee = screen.getAllByRole("button", { name: "Exercice 1, question 2, pas encore traitée" })[0]
      expect(traitee).toBeInTheDocument()
      expect(pasTraitee).toBeInTheDocument()

      const cible = document.getElementById("question-2")!
      cible.scrollIntoView = vi.fn()
      await userEvent.click(pasTraitee)
      expect(cible.scrollIntoView).toHaveBeenCalled()
    })
  })

  describe("cause de la perte", () => {
    const rendue = (questions: TentativeInediteQuestion[]) =>
      tentative({
        submitted_at: "2026-09-26T11:00:00Z",
        notation: notation({ questions_traitees: 1, questions_non_traitees: 1, definitive: true }),
        exercices: [{
          id: 1, numero_exercice: "1", points: "8", groupes: [], enonce_intro_markdown: "", questions,
        }],
      })

    it("propose de dire pourquoi quand une question traitée n'a pas tous ses points", async () => {
      api.getTentativeInedite.mockResolvedValue(
        rendue([
          question(1, "1", {
            traitee: true, corrige_markdown: "Corrigé 1", criteres_notation: [],
            reponse: { reponse_choisie: "", resultat_declare: "PARTIEL", notee: true, points_obtenus: 2 },
          }),
        ]),
      )
      api.noterTentativeQuestion.mockResolvedValue({
        ...question(1, "1", { traitee: true }),
        reponse: { reponse_choisie: "", resultat_declare: "PARTIEL", notee: true, points_obtenus: 2, cause_perte: "CALCUL" },
        notation: notation(),
      })
      afficher()

      await userEvent.click(await screen.findByRole("button", { name: "Erreur de calcul" }))

      await waitFor(() => expect(api.noterTentativeQuestion).toHaveBeenCalledWith(7, 1, { cause_perte: "CALCUL" }))
    })

    it("ne le propose pas quand tous les points sont là", async () => {
      api.getTentativeInedite.mockResolvedValue(
        rendue([
          question(1, "1", {
            traitee: true, corrige_markdown: "Corrigé 1", criteres_notation: [],
            reponse: { reponse_choisie: "", resultat_declare: "REUSSI", notee: true, points_obtenus: 4 },
          }),
        ]),
      )
      afficher()

      await screen.findByText("Corrigé 1")
      expect(screen.queryByText(/Pourquoi as-tu perdu des points/)).not.toBeInTheDocument()
    })

    it("propose une cause aux questions non traitées, avec moins de choix", async () => {
      api.getTentativeInedite.mockResolvedValue(rendue([question(1, "1", { corrige_markdown: "Corrigé 1" })]))
      afficher()

      expect(await screen.findByText(/Pourquoi ne l'as-tu pas traitée/)).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Manque de temps" })).toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Erreur de calcul" })).not.toBeInTheDocument()
    })
  })

  describe("annale officielle (simulation, un exercice = un bloc)", () => {
    const annale = (extra: Partial<TentativeInedite> = {}) =>
      tentative({
        source: "officielle", granularite: "exercice", epreuve_titre: "Maths BAC C 2019", sujet_pdf_url: "/media/x.pdf", sujet_pdf_disponible: true,
        exercices: [
          {
            id: 10, numero_exercice: "1", points: "6", groupes: [], enonce_intro_markdown: "",
            questions: [question(10, "1", { points: 6, corrige_markdown: "Corrigé A", criteres_notation: [] })],
          },
          {
            id: 11, numero_exercice: "2", points: "14", groupes: [], enonce_intro_markdown: "",
            questions: [question(11, "2", { points: 14, corrige_markdown: "Corrigé B", criteres_notation: [] })],
          },
        ],
        ...extra,
      })

    it("charge la simulation, parle d'exercices et non de questions", async () => {
      api.getSimulation.mockResolvedValue(annale())
      afficher("officielle")

      expect(await screen.findAllByRole("checkbox", { name: "J'ai traité cet exercice" })).toHaveLength(2)
      expect(api.getSimulation).toHaveBeenCalledWith(7)
      expect(api.getTentativeInedite).not.toHaveBeenCalled()
      expect(screen.queryByText("Question 1")).not.toBeInTheDocument()
      expect(screen.getByText("0 / 2 traités")).toBeInTheDocument()
      // Les points sont dans l'en-tête de l'exercice, pas répétés sous forme de pastille.
      expect(screen.getByText("6 pts")).toBeInTheDocument()
      expect(screen.queryByText(/pour cet exercice/)).not.toBeInTheDocument()
    })

    it("déclare un exercice traité auprès de l'API des simulations", async () => {
      api.getSimulation.mockResolvedValue(annale())
      api.noterSimulationExercice.mockResolvedValue({
        ...question(10, "1", { traitee: true, points: 6 }),
        reponse: { reponse_choisie: "", resultat_declare: "", notee: false },
        notation: notation({ questions_traitees: 1, questions_non_traitees: 1, questions_a_noter: 1 }),
      })
      afficher("officielle")

      const cases = await screen.findAllByRole("checkbox", { name: "J'ai traité cet exercice" })
      await userEvent.click(cases[0])

      await waitFor(() => expect(api.noterSimulationExercice).toHaveBeenCalledWith(7, 10, { traitee: true }))
      expect(api.noterTentativeQuestion).not.toHaveBeenCalled()
      expect(await screen.findByText("1 / 2 traités")).toBeInTheDocument()
    })

    it("liste les exercices non traités avant de rendre la copie, puis termine via l'API des simulations", async () => {
      api.getSimulation.mockResolvedValue(annale())
      api.completeSimulation.mockResolvedValue({})
      afficher("officielle")

      await userEvent.click(await screen.findByRole("button", { name: /Terminer/ }))

      const dialogue = await screen.findByRole("dialog")
      expect(within(dialogue).getByText(/2 exercices non traités valent 0 point/)).toBeInTheDocument()
      expect(within(dialogue).getByRole("button", { name: "Exercice 1" })).toBeInTheDocument()

      api.getSimulation.mockResolvedValue(annale({ submitted_at: "2026-09-26T11:00:00Z", notation: notation({ definitive: true }) }))
      await userEvent.click(within(dialogue).getByRole("button", { name: /Terminer et voir le corrigé/ }))

      await waitFor(() => expect(api.completeSimulation).toHaveBeenCalledWith(7))
      const liens = await screen.findAllByRole("link", { name: "Voir mon résultat" })
      expect(liens.map((lien) => lien.getAttribute("href"))).toEqual(["/simulation/7/resultat", "/simulation/7/resultat"])
    })

    it("la carte de l'épreuve compte les exercices", async () => {
      api.getSimulation.mockResolvedValue(annale())
      afficher("officielle")

      await screen.findAllByRole("checkbox", { name: "J'ai traité cet exercice" })
      expect(screen.getAllByRole("button", { name: "Exercices, exercice 1, pas encore traité" }).length).toBeGreaterThan(0)
    })

    it("ouvre le sujet PDF dans un nouvel onglet", async () => {
      api.getSimulation.mockResolvedValue(annale())
      const ouvrir = vi.spyOn(window, "open").mockReturnValue(null)
      afficher("officielle")

      await userEvent.click(await screen.findByRole("button", { name: "Ouvrir l'épreuve en PDF" }))

      expect(ouvrir).toHaveBeenCalledWith("/media/x.pdf", "_blank", "noopener,noreferrer")
      ouvrir.mockRestore()
    })

    it("dit que la durée est estimée quand l'annale n'annonce pas la sienne", async () => {
      api.getSimulation.mockResolvedValue(annale({ duree_estimee: true }))
      afficher("officielle")

      expect(await screen.findByText(/Durée estimée : cette annale n'annonce pas sa durée/)).toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /Conditions réelles/ }))
      const dialogue = await screen.findByRole("dialog")

      expect(within(dialogue).getByText(/Cette annale n'annonce pas sa durée : estimée d'après ses autres sessions\./)).toBeInTheDocument()
    })

    it("ne mentionne rien quand la durée est celle de l'épreuve elle-même", async () => {
      api.getSimulation.mockResolvedValue(annale({ duree_estimee: false }))
      afficher("officielle")

      await screen.findAllByRole("checkbox", { name: "J'ai traité cet exercice" })
      expect(screen.queryByText(/Durée estimée/)).not.toBeInTheDocument()
    })
  })
})
