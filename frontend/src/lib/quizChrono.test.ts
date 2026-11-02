import { afterEach, describe, expect, it, vi } from "vitest"

import { chronoEstMasque, dureeEstimeeSecondes, memoriserChronoMasque, secondesRestantes } from "@/lib/quizChrono"

const MAINTENANT = Date.parse("2026-11-02T10:00:00Z")

describe("secondesRestantes", () => {
  it("compte depuis l'échéance, arrondi au-dessus", () => {
    expect(secondesRestantes("2026-11-02T10:05:00Z", MAINTENANT)).toBe(300)
    expect(secondesRestantes("2026-11-02T10:00:00.400Z", MAINTENANT)).toBe(1)
  })

  it("ne descend jamais sous zéro une fois l'échéance passée", () => {
    expect(secondesRestantes("2026-11-02T09:00:00Z", MAINTENANT)).toBe(0)
  })
})

describe("dureeEstimeeSecondes", () => {
  it("applique la majoration comme le serveur, arrondie au-dessus", () => {
    expect(dureeEstimeeSecondes(10, 60, 0)).toBe(600)
    expect(dureeEstimeeSecondes(10, 60, 50)).toBe(900)
    expect(dureeEstimeeSecondes(5, 60, 25)).toBe(375)
    expect(dureeEstimeeSecondes(3, 45, 25)).toBe(169)
  })
})

describe("chrono masqué", () => {
  afterEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it("se mémorise sur l'appareil", () => {
    expect(chronoEstMasque()).toBe(false)
    memoriserChronoMasque(true)
    expect(chronoEstMasque()).toBe(true)
    memoriserChronoMasque(false)
    expect(chronoEstMasque()).toBe(false)
  })

  it("ne casse pas quand le stockage est bloqué", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("bloqué")
    })
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("bloqué")
    })

    expect(chronoEstMasque()).toBe(false)
    expect(() => memoriserChronoMasque(true)).not.toThrow()
  })
})
