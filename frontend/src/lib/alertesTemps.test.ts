import { describe, expect, it } from "vitest"

import { messageAlerte, reperesFranchis, type CleAlerte } from "./alertesTemps"

const DEUX_HEURES = 120 * 60
const aucun = new Set<CleAlerte>()

describe("reperesFranchis", () => {
  it("ne dit rien au début de l'épreuve", () => {
    expect(reperesFranchis(DEUX_HEURES - 10, DEUX_HEURES, aucun)).toEqual([])
  })

  it("annonce la mi-parcours quand la moitié du temps est écoulée", () => {
    expect(reperesFranchis(60 * 60, DEUX_HEURES, aucun)).toEqual(["mi-parcours"])
    expect(reperesFranchis(60 * 60 + 1, DEUX_HEURES, aucun)).toEqual([])
  })

  it("n'annonce jamais deux fois le même repère", () => {
    expect(reperesFranchis(60 * 60, DEUX_HEURES, new Set<CleAlerte>(["mi-parcours"]))).toEqual([])
  })

  it("annonce tous les repères passés d'un coup à la reprise d'une épreuve avancée", () => {
    expect(reperesFranchis(4 * 60, DEUX_HEURES, aucun)).toEqual(["mi-parcours", "quinze-minutes", "cinq-minutes"])
  })

  it("les repères se suivent dans l'ordre jusqu'à la dernière minute", () => {
    expect(reperesFranchis(30, DEUX_HEURES, aucun)).toEqual(["mi-parcours", "quinze-minutes", "cinq-minutes", "une-minute"])
  })

  it("adapte les repères à une épreuve courte", () => {
    const trenteMinutes = 30 * 60
    expect(reperesFranchis(15 * 60, trenteMinutes, aucun)).toEqual(["mi-parcours"])
    expect(reperesFranchis(4 * 60, trenteMinutes, aucun)).toEqual(["mi-parcours", "cinq-minutes"])
    // Douze minutes : ni mi-parcours ni « 5 minutes » n'ont de sens, seule la dernière minute reste.
    expect(reperesFranchis(30, 12 * 60, aucun)).toEqual(["une-minute"])
  })

  it("n'annonce rien sur une épreuve trop courte pour avoir des repères", () => {
    expect(reperesFranchis(10, 8 * 60, aucun)).toEqual([])
  })
})

describe("messageAlerte", () => {
  it("dit où en est l'élève à mi-parcours, sans le juger", () => {
    expect(messageAlerte("mi-parcours", { traitees: 6, total: 15 })).toBe("Mi-parcours : 6 questions traitées sur 15.")
    expect(messageAlerte("mi-parcours", { traitees: 1, total: 15 })).toBe("Mi-parcours : 1 question traitée sur 15.")
  })

  it("rappelle de cocher les questions traitées avant la fin", () => {
    expect(messageAlerte("cinq-minutes", { traitees: 0, total: 3 })).toContain("cocher")
  })
})
