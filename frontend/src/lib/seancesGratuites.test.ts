import { beforeEach, describe, expect, it } from "vitest"

import { cleSeance, marquerSeancesJouees, scoresDesSeances, seanceJouee, seancesJouees } from "./seancesGratuites"

const CLE = "edukora:seances-jouees"

beforeEach(() => localStorage.clear())

describe("seancesGratuites : les quiz gratuits joués sur cet appareil", () => {
  it("rien de joué : un ensemble vide, aucun record", () => {
    expect(seancesJouees().size).toBe(0)
    expect(seanceJouee(23, 720)).toEqual({ jouee: false, record: null })
  })

  it("garde chaque thème par examen, sans doublon", () => {
    marquerSeancesJouees(23, [720])
    marquerSeancesJouees(23, [720, 31])
    marquerSeancesJouees(14, [720])
    expect([...seancesJouees()].sort()).toEqual([cleSeance(14, 720), cleSeance(23, 31), cleSeance(23, 720)].sort())
  })

  it("ignore un thème absent (question historique sans thème)", () => {
    marquerSeancesJouees(23, [null, undefined])
    expect(seancesJouees().size).toBe(0)
  })

  it("garde le meilleur score, jamais le dernier", () => {
    marquerSeancesJouees(23, [720], { reussies: 3, total: 5 })
    expect(seanceJouee(23, 720)).toEqual({ jouee: true, record: { reussies: 3, total: 5 } })
    marquerSeancesJouees(23, [720], { reussies: 2, total: 5 })
    expect(seanceJouee(23, 720).record).toEqual({ reussies: 3, total: 5 })
    marquerSeancesJouees(23, [720], { reussies: 5, total: 6 })
    expect(seanceJouee(23, 720).record).toEqual({ reussies: 5, total: 6 })
    // Rejouée sans score : toujours jouée, le record reste.
    marquerSeancesJouees(23, [720])
    expect(seanceJouee(23, 720).record).toEqual({ reussies: 5, total: 6 })
  })

  it("un quiz marqué sans score reçoit le premier score connu", () => {
    marquerSeancesJouees(23, [720])
    expect(seanceJouee(23, 720)).toEqual({ jouee: true, record: null })
    marquerSeancesJouees(23, [720], { reussies: 0, total: 5 })
    expect(seanceJouee(23, 720).record).toEqual({ reussies: 0, total: 5 })
  })

  it("lit le premier format (une liste de clés) : joué, score inconnu", () => {
    localStorage.setItem(CLE, JSON.stringify(["23:720"]))
    expect(seanceJouee(23, 720)).toEqual({ jouee: true, record: null })
    marquerSeancesJouees(23, [31], { reussies: 4, total: 5 })
    expect(scoresDesSeances()).toEqual(new Map([["23:720", null], ["23:31", { reussies: 4, total: 5 }]]))
  })

  it("un contenu stocké illisible vaut « rien de joué », et se répare à l'écriture suivante", () => {
    localStorage.setItem(CLE, "pas du json")
    expect(seancesJouees().size).toBe(0)
    localStorage.setItem(CLE, JSON.stringify({ "23:720": "n'importe quoi", "23:31": [1, 0] }))
    expect(scoresDesSeances()).toEqual(new Map([["23:720", null], ["23:31", null]]))
    marquerSeancesJouees(23, [720], { reussies: 1, total: 5 })
    expect(seanceJouee(23, 720).record).toEqual({ reussies: 1, total: 5 })
  })
})
