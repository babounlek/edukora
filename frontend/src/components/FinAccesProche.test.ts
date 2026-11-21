import { describe, expect, it } from "vitest"

import { JOURS_ANNONCE_FIN, joursAvantFin } from "./FinAccesProche"
import { meilleurScore } from "./PremiereSeance"

describe("joursAvantFin : jours pleins jusqu'au jour où l'accès se termine", () => {
  const maintenant = new Date(2026, 11, 10, 17, 30).getTime()

  it("compte en dates locales, pas en heures écoulées", () => {
    // Fin le 13 à 9 h, vu le 10 à 17 h 30 : trois jours, pas « 2,6 ».
    expect(joursAvantFin(new Date(2026, 11, 13, 9, 0).toISOString(), maintenant)).toBe(3)
    expect(joursAvantFin(new Date(2026, 11, 10, 23, 0).toISOString(), maintenant)).toBe(0)
    expect(joursAvantFin(new Date(2026, 11, 10, 8, 0).toISOString(), maintenant)).toBe(0)
    expect(joursAvantFin(new Date(2026, 11, 9, 23, 0).toISOString(), maintenant)).toBe(-1)
  })

  it("l'annonce commence une semaine avant", () => {
    expect(joursAvantFin(new Date(2026, 11, 17, 9, 0).toISOString(), maintenant)).toBe(JOURS_ANNONCE_FIN)
    expect(joursAvantFin(new Date(2026, 11, 18, 9, 0).toISOString(), maintenant)).toBeGreaterThan(JOURS_ANNONCE_FIN)
  })
})

describe("meilleurScore : ce que le visiteur a fait de mieux pour son examen", () => {
  it("retient la meilleure part de bonnes réponses, pour cet examen seulement", () => {
    const scores = new Map([
      ["14:1", { reussies: 3, total: 5 }],
      ["14:2", { reussies: 5, total: 6 }],
      ["14:3", null],
      ["3:9", { reussies: 6, total: 6 }],
    ])
    expect(meilleurScore(scores, 14)).toEqual({ reussies: 5, total: 6 })
    expect(meilleurScore(scores, 3)).toEqual({ reussies: 6, total: 6 })
  })

  it("rien sans score connu", () => {
    expect(meilleurScore(new Map([["14:3", null]]), 14)).toBeNull()
    expect(meilleurScore(new Map(), 14)).toBeNull()
  })
})
