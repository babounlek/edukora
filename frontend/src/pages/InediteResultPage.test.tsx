import { render, screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { TentativeInediteResult } from "@/api/types"

const completeTentative = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ completeTentative }))

import { InediteResultPage } from "./InediteResultPage"

function resultat(extra: Partial<TentativeInediteResult> = {}): TentativeInediteResult {
  return {
    id: 7, epreuve: 1, country: "CM", total_questions: 4, questions_repondues: 3, questions_non_traitees: 1,
    questions_a_noter: 0, score: 63, note: 12.5, bareme: 20, note_sur_20: 12.5, bareme_estime: false,
    definitive: true, temps_total_secondes: 3725,
    par_exercice: [
      { numero_exercice: "1", points_possibles: 8, points_obtenus: 7 },
      { numero_exercice: "2", points_possibles: 12, points_obtenus: 5.5 },
    ],
    par_theme: [
      { theme: "suites", total: 2, reussies: 2, points_possibles: 8, points_obtenus: 8 },
      { theme: "probabilités", total: 2, reussies: 0, points_possibles: 12, points_obtenus: 4.5 },
    ],
    themes_a_reviser: [],
    ...extra,
  }
}

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/inedit/tentative/7/resultat"]}>
      <Routes>
        <Route path="/inedit/tentative/:id/resultat" element={<InediteResultPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => completeTentative.mockReset())

describe("InediteResultPage", () => {
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
    completeTentative.mockResolvedValue(resultat({ themes_a_reviser: [{ theme: "probabilités", echeance: iso }] }))
    afficher()

    expect(await screen.findByText("Ce que tu reverras")).toBeInTheDocument()
    expect(screen.getByText("demain")).toBeInTheDocument()
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
})
