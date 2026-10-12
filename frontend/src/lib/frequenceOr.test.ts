import { describe, expect, it } from "vitest"

import { centre, estDore, frontiere, HAUTEUR_LIGNE, LARGEUR, PLANCHER_OR, RAYON, seuilOr, trace } from "./cheminParcours"

describe("centre", () => {
  it("serpente autour de l'axe puis recommence", () => {
    const xs = Array.from({ length: 9 }, (_, i) => centre(i).x - LARGEUR / 2)
    expect(xs).toEqual([0, 48, 76, 48, 0, -48, -76, -48, 0])
  })

  it("descend d'une ligne par nœud", () => {
    expect(centre(0).y).toBe(RAYON)
    expect(centre(3).y).toBe(3 * HAUTEUR_LIGNE + RAYON)
  })

  it("garde chaque nœud et son étiquette dans la largeur", () => {
    for (let i = 0; i < 8; i++) expect(Math.abs(centre(i).x - LARGEUR / 2) + 70).toBeLessThanOrEqual(LARGEUR / 2)
  })
})

describe("trace", () => {
  it("ne trace rien sans segment", () => {
    expect(trace(2, 2)).toBe("")
    expect(trace(3, 1)).toBe("")
  })

  it("part du centre du premier nœud et arrive au centre du dernier", () => {
    const d = trace(0, 2)
    expect(d.startsWith(`M ${centre(0).x} ${centre(0).y}`)).toBe(true)
    expect(d.endsWith(`${centre(2).x} ${centre(2).y}`)).toBe(true)
    expect(d.match(/C/g)).toHaveLength(2)
  })
})

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

describe("frontiere", () => {
  it("est le premier nœud non maîtrisé après la série du début", () => {
    expect(frontiere([true, true, false, true])).toBe(2)
    expect(frontiere([false, true])).toBe(0)
  })

  it("est le dernier nœud quand tout est maîtrisé", () => {
    expect(frontiere([true, true, true])).toBe(2)
  })
})
