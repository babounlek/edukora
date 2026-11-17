import { beforeEach, describe, expect, it } from "vitest"

import { cleSeance, marquerSeancesJouees, seancesJouees } from "./seancesGratuites"

beforeEach(() => localStorage.clear())

describe("seancesGratuites : les thèmes joués sur cet appareil", () => {
  it("rien de joué : un ensemble vide", () => {
    expect(seancesJouees().size).toBe(0)
  })

  it("garde chaque thème par examen, sans doublon", () => {
    marquerSeancesJouees(23, [720])
    marquerSeancesJouees(23, [720, 31])
    marquerSeancesJouees(14, [720])
    expect([...seancesJouees()].sort()).toEqual([cleSeance(14, 720), cleSeance(23, 31), cleSeance(23, 720)].sort())
    expect(JSON.parse(localStorage.getItem("edukora:seances-jouees")!)).toHaveLength(3)
  })

  it("ignore un thème absent (question historique sans thème)", () => {
    marquerSeancesJouees(23, [null, undefined])
    expect(seancesJouees().size).toBe(0)
  })

  it("un contenu stocké illisible vaut « rien de joué », et se répare à l'écriture suivante", () => {
    localStorage.setItem("edukora:seances-jouees", "pas du json")
    expect(seancesJouees().size).toBe(0)
    localStorage.setItem("edukora:seances-jouees", JSON.stringify({ a: 1 }))
    expect(seancesJouees().size).toBe(0)
    marquerSeancesJouees(23, [720])
    expect(seancesJouees()).toEqual(new Set([cleSeance(23, 720)]))
  })
})
