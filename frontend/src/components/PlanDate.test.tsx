import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { PlanDate as PlanDateType } from "@/api/types"
import { PlanDate } from "./PlanDate"

const plan: PlanDateType = {
  jour_j: "2027-06-15",
  themes_a_consolider: 12,
  par_semaine: 2,
  cette_semaine: { debut: "2026-11-09", fin: "2026-11-15", cible: 2, faits: 1 },
  etapes: [
    { date: "2026-12-31", themes: 3 },
    { date: "2027-06-15", themes: 12 },
  ],
  une_seance_de_plus: { couverture_projetee: 0.74 },
}

describe("PlanDate", () => {
  it("dit où en est la semaine, les étapes datées et l'effet d'une séance de plus", () => {
    render(<PlanDate plan={plan} />)

    expect(screen.getByText("Cette semaine : 1 sur 2 thèmes à rendre solides")).toBeInTheDocument()
    expect(screen.getByText("3 thèmes de plus à rendre solides")).toBeInTheDocument()
    expect(screen.getByText("12 thèmes de plus à rendre solides")).toBeInTheDocument()
    expect(screen.getByText(/environ 74 % de l'essentiel/)).toBeInTheDocument()
  })

  it("félicite quand l'objectif de la semaine est atteint", () => {
    render(<PlanDate plan={{ ...plan, cette_semaine: { ...plan.cette_semaine, faits: 3 } }} />)

    expect(screen.getByText(/objectif atteint/)).toBeInTheDocument()
  })

  it("n'invente aucun plan quand l'essentiel est déjà couvert", () => {
    render(<PlanDate plan={{ ...plan, themes_a_consolider: 0, etapes: [] }} />)

    expect(screen.getByText(/déjà couvert l'essentiel/)).toBeInTheDocument()
    expect(screen.queryByText(/Cette semaine/)).not.toBeInTheDocument()
  })
})
