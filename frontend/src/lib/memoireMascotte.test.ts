import { beforeEach, describe, expect, it } from "vitest"

import { lireSouvenir, memoriserPresentee, memoriserSouvenir, pasEncorePresentee } from "./memoireMascotte"

beforeEach(() => localStorage.clear())

describe("mémoire de Kora", () => {
  it("ne sait rien au départ", () => {
    expect(lireSouvenir()).toBeNull()
  })

  it("retient le dernier résultat et compte les jours écoulés", () => {
    const hier = Date.UTC(2026, 10, 1, 12)
    memoriserSouvenir(60, hier)
    expect(lireSouvenir(hier + 3 * 24 * 3600 * 1000 + 1000)).toEqual({ pourcentage: 60, jours: 3 })
    expect(lireSouvenir(hier)).toEqual({ pourcentage: 60, jours: 0 })
  })

  it("ignore un contenu abîmé", () => {
    localStorage.setItem("edukora:mascotte-memoire", "{pas du json")
    expect(lireSouvenir()).toBeNull()
  })

  it("ne se présente qu'une fois", () => {
    expect(pasEncorePresentee()).toBe(true)
    memoriserPresentee()
    expect(pasEncorePresentee()).toBe(false)
  })
})
