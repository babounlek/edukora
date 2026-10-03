import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { definirRetoursActifs, jouerRetour, retoursActifs } from "./retours"

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
