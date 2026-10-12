import { describe, expect, it } from "vitest"

import { estDore, PLANCHER_OR, seuilOr } from "./frequenceOr"

describe("seuilOr", () => {
  it("ne dore rien sans fréquence connue (programme classique)", () => {
    expect(seuilOr([null, undefined, undefined, null, undefined])).toBeNull()
  })

  it("ne dore rien avec moins de quatre fréquences", () => {
    expect(seuilOr([90, 80, 70])).toBeNull()
  })

  it("retient le quart supérieur", () => {
    expect(seuilOr([90, 80, 70, 60, 50, 40, 35, 31])).toBe(80)
  })

  it("ne descend pas sous le plancher", () => {
    expect(seuilOr([20, 15, 10, 5, 4, 3, 2, 1])).toBe(PLANCHER_OR)
  })
})

describe("estDore", () => {
  it("compare à un seuil", () => {
    expect(estDore(80, 80)).toBe(true)
    expect(estDore(79, 80)).toBe(false)
    expect(estDore(null, 80)).toBe(false)
    expect(estDore(90, null)).toBe(false)
  })
})
