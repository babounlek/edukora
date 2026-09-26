import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { NotationResume, TentativeInedite, TentativeInediteQuestion } from "@/api/types"

const api = vi.hoisted(() => ({
  answerTentativeQuestion: vi.fn(),
  completeTentative: vi.fn(),
  downloadSujetPdf: vi.fn(),
  getTentativeInedite: vi.fn(),
  noterTentativeQuestion: vi.fn(),
  startExamMode: vi.fn(),
  toggleQuestionMarquee: vi.fn(),
}))
const toast = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }))

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
    exam_mode_started_at: null, submitted_at: null, score_obtenu: null, note_obtenue: null, bareme_snapshot: null,
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

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/inedit/tentative/7"]}>
      <Routes>
        <Route path="/inedit/tentative/:id" element={<InediteTentativePage />} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  Object.values(api).forEach((mock) => mock.mockReset())
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
    api.noterTentativeQuestion.mockRejectedValue(new Error("réseau"))
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
})
