import { describe, expect, it } from "vitest"

import { cibleApresChangementCursus } from "./pageApresChangementCursus"

describe("cibleApresChangementCursus", () => {
  it("reste sur une page de liste sans filtre", () => {
    expect(cibleApresChangementCursus("/cm/epreuves", "", "cm")).toEqual({ chemin: null, seanceEnCours: false })
    expect(cibleApresChangementCursus("/parcours", "", "cm").chemin).toBeNull()
  })

  it("retire les filtres liés à l'ancien examen mais garde les autres", () => {
    const c = cibleApresChangementCursus("/cm/epreuves", "?cursus=3&subject=7&search=suites", "cm")
    expect(c.chemin).toBe("/cm/epreuves?search=suites")
  })

  it("remonte d'une épreuve ou d'une inédite à la liste", () => {
    expect(cibleApresChangementCursus("/cm/epreuves/maths-2024/lire", "", "cm").chemin).toBe("/cm/epreuves")
    expect(cibleApresChangementCursus("/cm/epreuves-inedites/12", "", "cm").chemin).toBe("/cm/epreuves")
    expect(cibleApresChangementCursus("/epreuves/ancienne-url", "", "cm").chemin).toBe("/cm/epreuves")
  })

  it("remonte d'un cours, d'un thème, d'une matière du parcours, d'une page d'examen", () => {
    expect(cibleApresChangementCursus("/cours/limites/lire", "", "cm").chemin).toBe("/cm/cours")
    expect(cibleApresChangementCursus("/cm/themes-frequents/4/exercices/9", "", "cm").chemin).toBe("/cm/themes-frequents")
    expect(cibleApresChangementCursus("/parcours/5", "", "cm").chemin).toBe("/parcours")
    expect(cibleApresChangementCursus("/cm/examens/bepc", "", "cm").chemin).toBe("/cm")
  })

  it("demande confirmation pour une séance en cours, pas pour un résultat", () => {
    expect(cibleApresChangementCursus("/quiz/session/8", "", "cm")).toEqual({ chemin: "/quiz", seanceEnCours: true })
    expect(cibleApresChangementCursus("/simulation/3", "", "cm").seanceEnCours).toBe(true)
    expect(cibleApresChangementCursus("/quiz/session/8/resultat", "", "cm")).toEqual({ chemin: null, seanceEnCours: false })
  })

  it("suit le pays du nouvel examen", () => {
    expect(cibleApresChangementCursus("/cm/cours", "", "sn").chemin).toBe("/sn/cours")
    expect(cibleApresChangementCursus("/cm/epreuves/x", "", "sn").chemin).toBe("/sn/epreuves")
  })
})
