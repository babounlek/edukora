import { describe, expect, it } from "vitest"

import type { BilanPeriode } from "@/api/types"
import { jalonsAtteints, prochainJalon } from "./jalons"

function bilan(jalons: Partial<BilanPeriode["jalons"]>): BilanPeriode {
  return {
    debut: "2026-09-20", fin: "2026-09-26", expire_le: "2026-10-30", abonnement_actif: true,
    seances: 0, jours_actifs: 0, questions: 0, taux_reussite: null, taux_avant: null, meilleure_serie: 0,
    themes_travailles: 0, themes_consolides_total: 0, themes_consolides: [], matieres: [], a_de_l_activite: true,
    jalons: {
      seances_total: 0, seances_avant: 0, questions_total: 0, questions_avant: 0, solides_total: 0, solides_avant: 0,
      ...jalons,
    },
  }
}

describe("jalonsAtteints", () => {
  it("retient un palier franchi pendant la fenêtre", () => {
    const atteints = jalonsAtteints(bilan({ seances_avant: 3, seances_total: 5 }))
    expect(atteints.map((j) => j.libelle)).toEqual(["5 séances terminées"])
  })

  it("ne rejoue pas un palier déjà franchi avant la fenêtre", () => {
    expect(jalonsAtteints(bilan({ seances_avant: 5, seances_total: 8 }))).toEqual([])
  })

  it("ne garde que le palier le plus haut d'un même genre", () => {
    const atteints = jalonsAtteints(bilan({ questions_avant: 5, questions_total: 120 }))
    expect(atteints.map((j) => j.palier)).toEqual([100])
  })

  it("nomme le tout premier palier au singulier", () => {
    const atteints = jalonsAtteints(bilan({ solides_avant: 0, solides_total: 1 }))
    expect(atteints[0].libelle).toBe("Premier thème solide")
  })
})

describe("prochainJalon", () => {
  it("choisit le palier le plus proche d'être atteint", () => {
    // 9 séances sur 10 (90 %) devance 40 questions sur 50 (80 %).
    const prochain = prochainJalon(bilan({ seances_total: 9, questions_total: 40 }))
    expect(prochain).toMatchObject({ genre: "seances", palier: 10, actuel: 9 })
  })

  it("renvoie null quand tous les paliers sont dépassés", () => {
    expect(prochainJalon(bilan({ seances_total: 500, questions_total: 5000, solides_total: 100 }))).toBeNull()
  })
})
