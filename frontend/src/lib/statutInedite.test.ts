import { describe, expect, it } from "vitest"

import type { MesTentatives } from "@/api/types"

import { actionInedite, libelleFaite } from "./statutInedite"

const mes = (surcharge: Partial<MesTentatives>): MesTentatives => ({
  en_cours: false, nb_terminees: 0, meilleure_note: null, bareme: null, ...surcharge,
})

describe("actionInedite", () => {
  it("compose une épreuve jamais ouverte", () => {
    expect(actionInedite(null)).toBe("composer")
    expect(actionInedite(undefined)).toBe("composer")
  })

  it("reprend une copie en cours, même si une autre est déjà rendue", () => {
    expect(actionInedite(mes({ en_cours: true, nb_terminees: 2 }))).toBe("reprendre")
  })

  it("refait une épreuve dont toutes les copies sont rendues", () => {
    expect(actionInedite(mes({ nb_terminees: 1 }))).toBe("refaire")
  })
})

describe("libelleFaite", () => {
  it("donne la note sur son barème", () => {
    expect(libelleFaite(mes({ nb_terminees: 2, meilleure_note: 12.5, bareme: 20 }))).toBe("Faite · 12,5 / 20")
  })

  it("se contente de « Faite » sans note", () => {
    expect(libelleFaite(mes({ nb_terminees: 1 }))).toBe("Faite")
  })

  it("ne dit rien d'une épreuve jamais rendue", () => {
    expect(libelleFaite(mes({ en_cours: true }))).toBeNull()
    expect(libelleFaite(null)).toBeNull()
  })
})
