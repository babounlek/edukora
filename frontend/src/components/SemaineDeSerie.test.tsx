import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { EtatXp, SerieDeJours } from "@/api/types"
import { ObjectifXp } from "./ObjectifXp"
import { SemaineDeSerie } from "./SemaineDeSerie"

function semaine(faits: number[], aujourdhui: number): SerieDeJours["semaine"] {
  return Array.from({ length: 7 }, (_, i) => ({
    date: `2026-09-${String(28 + i).padStart(2, "0")}`,
    fait: faits.includes(i),
    aujourdhui: i === aujourdhui,
  }))
}

const serie = (surcharge: Partial<SerieDeJours> = {}): SerieDeJours => ({
  jours: 3, record: 5, actif_aujourdhui: false, repos_pris: false, semaine: semaine([0, 1], 2), ...surcharge,
})

describe("SemaineDeSerie", () => {
  it("affiche sept jours, les jours travaillés et le jour courant", () => {
    render(<SemaineDeSerie serie={serie()} />)
    expect(screen.getByText("Série de 3 jours")).toBeInTheDocument()
    expect(screen.getAllByRole("img", { name: "Travaillé" })).toHaveLength(2)
    expect(screen.getAllByRole("img", { name: "Non travaillé" })).toHaveLength(4)
    expect(screen.getAllByRole("img", { name: "Aujourd'hui, pas encore" })).toHaveLength(1)
  })

  it("dit que l'objectif du jour prolonge la série tant qu'aujourd'hui n'est pas fait", () => {
    render(<SemaineDeSerie serie={serie()} />)
    expect(screen.getByText(/ton objectif du jour la prolonge/)).toBeInTheDocument()
  })

  it("ne culpabilise pas et reste sobre avant deux jours de suite", () => {
    render(<SemaineDeSerie serie={serie({ jours: 1, actif_aujourdhui: true })} />)
    expect(screen.getByText("Ta semaine")).toBeInTheDocument()
    expect(screen.queryByText(/la prolonge/)).not.toBeInTheDocument()
  })

  it("n'affiche rien sans semaine (ancienne réponse du serveur)", () => {
    const { container } = render(<SemaineDeSerie serie={serie({ semaine: undefined })} />)
    expect(container).toBeEmptyDOMElement()
  })
})

describe("ObjectifXp", () => {
  const etat = (surcharge: Partial<EtatXp> = {}): EtatXp => ({
    xp: 12, objectif: 20, atteint: false, objectifs_possibles: [10, 20, 30], ...surcharge,
  })

  it("montre la progression vers l'objectif", () => {
    render(<ObjectifXp etat={etat()} />)
    expect(screen.getByText("12 / 20 points")).toBeInTheDocument()
    expect(screen.getByRole("progressbar", { name: "Objectif de points du jour" })).toHaveAttribute("aria-valuenow", "12")
  })

  it("dit ce qu'il reste en bonnes réponses, sans le dire une fois l'objectif atteint ni dans l'en-tête", () => {
    const { rerender } = render(<ObjectifXp etat={etat()} />)
    // 8 points restants : une bonne réponse (10 points) suffit.
    expect(screen.getByText(/Encore environ 1 bonne réponse pour atteindre/)).toBeInTheDocument()

    rerender(<ObjectifXp etat={etat({ xp: 0 })} />)
    expect(screen.getByText(/Encore environ 2 bonnes réponses pour atteindre/)).toBeInTheDocument()

    rerender(<ObjectifXp etat={etat({ xp: 25, atteint: true })} />)
    expect(screen.queryByText(/Encore environ/)).not.toBeInTheDocument()

    rerender(<ObjectifXp etat={etat()} compact />)
    expect(screen.queryByText(/Encore environ/)).not.toBeInTheDocument()
  })

  it("plafonne la barre une fois l'objectif dépassé", () => {
    render(<ObjectifXp etat={etat({ xp: 35, atteint: true })} />)
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "20")
    expect(screen.getByText("35 / 20 points")).toBeInTheDocument()
  })
})
