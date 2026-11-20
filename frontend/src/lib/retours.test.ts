import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { definirRetoursActifs, jouerRetour, retoursActifs, transposition } from "./retours"

describe("retours sensoriels", () => {
  beforeEach(() => localStorage.clear())
  afterEach(() => vi.restoreAllMocks())

  it("sont activés par défaut", () => {
    expect(retoursActifs()).toBe(true)
  })

  it("se désactivent et se réactivent", () => {
    definirRetoursActifs(false)
    expect(retoursActifs()).toBe(false)
    definirRetoursActifs(true)
    expect(retoursActifs()).toBe(true)
  })

  it("font vibrer quand ils sont actifs, sans planter faute de Web Audio", () => {
    const vibrate = vi.fn()
    Object.defineProperty(navigator, "vibrate", { value: vibrate, configurable: true })
    expect(() => jouerRetour("juste")).not.toThrow()
    expect(vibrate).toHaveBeenCalledWith(15)
  })

  it("font monter la note avec la série, jusqu'à l'octave, sans jamais redescendre", () => {
    expect(transposition(1)).toBe(1)
    const facteurs = [1, 2, 3, 4, 5, 6].map(transposition)
    expect([...facteurs].sort((a, b) => a - b)).toEqual(facteurs)
    expect(transposition(6)).toBeCloseTo(2)
    expect(transposition(40)).toBeCloseTo(2)
    // Une série nulle (réponse partielle) ou absurde sonne comme une première bonne réponse.
    expect(transposition(0)).toBe(1)
    expect(transposition(Number.NaN)).toBe(1)
  })

  it("ont une vibration à part pour un palier de série", () => {
    const vibrate = vi.fn()
    Object.defineProperty(navigator, "vibrate", { value: vibrate, configurable: true })
    jouerRetour("palier")
    expect(vibrate).toHaveBeenCalledWith([15, 30, 15, 30, 30])
  })

  it("ne font rien quand ils sont désactivés", () => {
    const vibrate = vi.fn()
    Object.defineProperty(navigator, "vibrate", { value: vibrate, configurable: true })
    definirRetoursActifs(false)
    jouerRetour("objectif")
    expect(vibrate).not.toHaveBeenCalled()
  })

  it("ignorent une vibration qui lève une erreur", () => {
    Object.defineProperty(navigator, "vibrate", {
      value: () => { throw new Error("refusé") }, configurable: true,
    })
    expect(() => jouerRetour("faux")).not.toThrow()
  })
})
