import { render, screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { TentativeInediteResult } from "@/api/types"

const completeTentative = vi.hoisted(() => vi.fn())
const completeSimulation = vi.hoisted(() => vi.fn())
const getTentativeInedite = vi.hoisted(() => vi.fn())
const getSimulation = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ user: { a_un_abonnement_actif: true } as { a_un_abonnement_actif: boolean } | null }))
vi.mock("@/api/endpoints", () => ({ completeTentative, completeSimulation, getTentativeInedite, getSimulation }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))

import { InediteResultPage } from "./InediteResultPage"

function resultat(extra: Partial<TentativeInediteResult> = {}): TentativeInediteResult {
  return {
    id: 7, epreuve: 1, epreuve_titre: "Programmation Terminale TI – Épreuve inédite n°1", country: "CM", total_questions: 4, questions_repondues: 3, questions_non_traitees: 1,
    questions_a_noter: 0, score: 63, note: 12.5, bareme: 20, note_sur_20: 12.5, bareme_estime: false,
    definitive: true, mode: "examen", granularite: "question", temps_total_secondes: 3725,
    par_exercice: [
      { numero_exercice: "1", points_possibles: 8, points_obtenus: 7 },
      { numero_exercice: "2", points_possibles: 12, points_obtenus: 5.5 },
    ],
    par_theme: [
      { theme: "suites", theme_id: 11, total: 2, reussies: 2, points_possibles: 8, points_obtenus: 8 },
      { theme: "probabilités", theme_id: 12, total: 2, reussies: 0, points_possibles: 12, points_obtenus: 4.5 },
    ],
    themes_a_reviser: [],
    pertes: { total_perdu: 0, causes: [] },
    temps_par_exercice: null,
    exercice_chronophage: null,
    comparaison: null,
    cursus_id: 4,
    ...extra,
  }
}

function afficher(source: "inedit" | "officielle" = "inedit") {
  const base = source === "officielle" ? "/simulation" : "/inedit/tentative"
  return render(
    <MemoryRouter initialEntries={[`${base}/7/resultat`]}>
      <Routes>
        <Route path={`${base}/:id/resultat`} element={<InediteResultPage source={source} />} />
        <Route path={`${base}/:id`} element={<p>Copie en cours</p>} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  completeTentative.mockReset()
  completeSimulation.mockReset()
  // Par défaut la copie est déjà rendue : la page affiche son résultat.
  getTentativeInedite.mockReset()
  getTentativeInedite.mockResolvedValue({ id: 7, submitted_at: "2026-10-04T09:00:00Z" })
  getSimulation.mockReset()
  getSimulation.mockResolvedValue({ id: 7, submitted_at: "2026-10-04T09:00:00Z" })
  auth.user = { a_un_abonnement_actif: true }
})

describe("InediteResultPage, après l'épreuve offerte", () => {
  it("propose l'abonnement à qui n'en a pas, et le ramène à la liste des inédites ensuite", async () => {
    auth.user = { a_un_abonnement_actif: false }
    completeTentative.mockResolvedValue(resultat())
    afficher()

    const lien = await screen.findByRole("link", { name: "Débloquer les autres épreuves" })
    const params = new URL(lien.getAttribute("href") ?? "", "http://x").searchParams
    expect(params.get("cursus")).toBe("4")
    expect(params.get("retour")).toBe("/cm/epreuves?origine=INEDITE")
  })

  it("n'en parle jamais à un abonné", async () => {
    completeTentative.mockResolvedValue(resultat())
    afficher()

    await screen.findByLabelText("Note : 12,5 sur 20")
    expect(screen.queryByRole("link", { name: "Débloquer les autres épreuves" })).not.toBeInTheDocument()
  })

  it("ni sur une simulation d'annale officielle", async () => {
    auth.user = { a_un_abonnement_actif: false }
    completeSimulation.mockResolvedValue(resultat({ granularite: "exercice" }))
    afficher("officielle")

    await screen.findByLabelText("Note : 12,5 sur 20")
    expect(screen.queryByRole("link", { name: "Débloquer les autres épreuves" })).not.toBeInTheDocument()
  })
})

describe("InediteResultPage", () => {
  it("dit de quelle épreuve on lit le résultat", async () => {
    completeTentative.mockResolvedValue(resultat())
    afficher()

    expect(await screen.findByText("Programmation Terminale TI – Épreuve inédite n°1")).toBeInTheDocument()
  })

  it("ne clôture jamais une copie encore en cours : elle retourne à l'épreuve", async () => {
    getTentativeInedite.mockResolvedValue({ id: 7, submitted_at: null })
    afficher()

    expect(await screen.findByText("Copie en cours")).toBeInTheDocument()
    expect(completeTentative).not.toHaveBeenCalled()
  })

  it("fait de même pour une simulation d'annale en cours", async () => {
    getSimulation.mockResolvedValue({ id: 7, submitted_at: null })
    afficher("officielle")

    expect(await screen.findByText("Copie en cours")).toBeInTheDocument()
    expect(completeSimulation).not.toHaveBeenCalled()
  })

  it("affiche la note sur le barème, définitive, avec le détail par exercice", async () => {
    completeTentative.mockResolvedValue(resultat())
    afficher()

    expect(await screen.findByLabelText("Note : 12,5 sur 20")).toBeInTheDocument()
    expect(screen.getByText("Note définitive")).toBeInTheDocument()
    expect(screen.getByText(/1 question non traitée a compté 0 point/)).toBeInTheDocument()
    expect(screen.getByText("7 / 8")).toBeInTheDocument()
    expect(screen.queryByText("Terminer ma notation")).not.toBeInTheDocument()
  })

  it("classe les compétences de la plus fragile à la plus solide", async () => {
    completeTentative.mockResolvedValue(resultat())
    afficher()

    const competences = await screen.findAllByText(/pts$/)
    expect(competences[0]).toHaveTextContent("4,5 / 12 pts")
    expect(competences[1]).toHaveTextContent("8 / 8 pts")
  })

  it("propose de terminer la notation tant que la note est provisoire", async () => {
    completeTentative.mockResolvedValue(resultat({ definitive: false, questions_a_noter: 2 }))
    afficher()

    expect(await screen.findByText("Note provisoire")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Terminer ma notation" })).toHaveAttribute(
      "href", "/inedit/tentative/7?noter=1",
    )
  })

  it("dit quels thèmes reviennent dans la séance du jour, et quand", async () => {
    const demain = new Date()
    demain.setDate(demain.getDate() + 1)
    const iso = `${demain.getFullYear()}-${String(demain.getMonth() + 1).padStart(2, "0")}-${String(demain.getDate()).padStart(2, "0")}`
    completeTentative.mockResolvedValue(resultat({ themes_a_reviser: [{ theme: "probabilités", theme_id: 12, echeance: iso }] }))
    afficher()

    expect(await screen.findByText("Ce que tu reverras")).toBeInTheDocument()
    expect(screen.getByText("demain")).toBeInTheDocument()
    // De quoi s'y mettre tout de suite : un quiz et les cours de ce thème.
    expect(screen.getByRole("link", { name: "Quiz" })).toHaveAttribute("href", "/quiz?cursus=4&theme=12")
    expect(screen.getByRole("link", { name: "Cours" })).toHaveAttribute("href", "/cm/cours?theme=12")
  })

  it("répartit les points perdus par cause", async () => {
    completeTentative.mockResolvedValue(
      resultat({
        pertes: {
          total_perdu: 7.5,
          causes: [
            { cause: "CALCUL", libelle: "Erreur de calcul", points: 4.5, part: 60 },
            { cause: "NON_TRAITEE", libelle: "Questions non traitées", points: 3, part: 40 },
          ],
        },
      }),
    )
    afficher()

    expect(await screen.findByText("Où sont passés tes points")).toBeInTheDocument()
    expect(screen.getByText(/Tu as perdu 7,5 points/)).toBeInTheDocument()
    expect(screen.getByText("Erreur de calcul")).toBeInTheDocument()
    expect(screen.getByText("4,5 pts · 60 %")).toBeInTheDocument()
  })

  it("félicite quand aucun point n'est perdu", async () => {
    completeTentative.mockResolvedValue(resultat())
    afficher()
    expect(await screen.findByText(/Tu n'as perdu aucun point/)).toBeInTheDocument()
  })

  it("montre le temps par exercice et signale l'exercice chronophage", async () => {
    completeTentative.mockResolvedValue(
      resultat({
        temps_par_exercice: [
          { numero_exercice: "1", secondes: 900, part_du_temps: 15, part_des_points: 40 },
          { numero_exercice: "2", secondes: 5100, part_du_temps: 85, part_des_points: 60 },
        ],
        exercice_chronophage: "2",
      }),
    )
    afficher()

    expect(await screen.findByText("Ton temps")).toBeInTheDocument()
    expect(screen.getByText("15 min · 15 % du temps")).toBeInTheDocument()
    expect(screen.getByText(/L'exercice 2 a pris 85 % de ton temps pour 60 % des points/)).toBeInTheDocument()
  })

  it("n'affiche pas le temps sans estimation (entraînement libre)", async () => {
    completeTentative.mockResolvedValue(resultat())
    afficher()
    await screen.findByLabelText("Note : 12,5 sur 20")
    expect(screen.queryByText("Ton temps")).not.toBeInTheDocument()
    expect(screen.queryByText("Ta position")).not.toBeInTheDocument()
  })

  it("situe l'élève parmi les autres candidats quand l'effectif le permet", async () => {
    completeTentative.mockResolvedValue(resultat({ comparaison: { effectif: 42, percentile: 73, moyenne: 9.5 } }))
    afficher()

    expect(await screen.findByText("Ta position")).toBeInTheDocument()
    expect(screen.getByText("73 %")).toBeInTheDocument()
    expect(screen.getByText(/42 candidats/)).toBeInTheDocument()
  })

  it("dit comment l'épreuve a été passée", async () => {
    completeTentative.mockResolvedValue(resultat({ mode: "libre" }))
    afficher()

    expect(await screen.findByText("Entraînement libre")).toBeInTheDocument()
  })

  it("n'affiche pas la section quand rien ne revient", async () => {
    completeTentative.mockResolvedValue(resultat())
    afficher()

    await screen.findByLabelText("Note : 12,5 sur 20")
    expect(screen.queryByText("Ce que tu reverras")).not.toBeInTheDocument()
  })

  it("donne l'équivalent sur 20 quand le barème est différent", async () => {
    completeTentative.mockResolvedValue(resultat({ note: 24, bareme: 40, note_sur_20: 12 }))
    afficher()

    expect(await screen.findByText("12 / 20")).toBeInTheDocument()
  })

  describe("annale officielle", () => {
    it("charge le résultat de la simulation et parle d'exercices", async () => {
      completeSimulation.mockResolvedValue(
        resultat({ granularite: "exercice", questions_repondues: 2, total_questions: 3, questions_non_traitees: 1 }),
      )
      afficher("officielle")

      expect(await screen.findByLabelText("Note : 12,5 sur 20")).toBeInTheDocument()
      expect(completeTentative).not.toHaveBeenCalled()
      expect(screen.getByText(/2 exercices traités sur 3/)).toBeInTheDocument()
      expect(screen.getByText(/1 exercice non traité a compté 0 point/)).toBeInTheDocument()
    })

    it("renvoie vers la simulation et le catalogue des annales", async () => {
      completeSimulation.mockResolvedValue(resultat({ granularite: "exercice", definitive: false, questions_a_noter: 1 }))
      afficher("officielle")

      expect(await screen.findByRole("link", { name: "Revoir ma copie corrigée" })).toHaveAttribute("href", "/simulation/7")
      expect(screen.getByRole("link", { name: "Terminer ma notation" })).toHaveAttribute("href", "/simulation/7?noter=1")
      expect(screen.getByRole("link", { name: "Voir les épreuves" })).toHaveAttribute("href", "/cm/epreuves")
    })

    it("n'offre pas de quiz quand aucun cursus n'est connu", async () => {
      completeSimulation.mockResolvedValue(
        resultat({ granularite: "exercice", cursus_id: null, themes_a_reviser: [{ theme: "suites", theme_id: 5, echeance: "2099-01-01" }] }),
      )
      afficher("officielle")

      await screen.findByText("Ce que tu reverras")
      expect(screen.queryByRole("link", { name: "Quiz" })).not.toBeInTheDocument()
      expect(screen.getByRole("link", { name: "Cours" })).toBeInTheDocument()
    })
  })
})
