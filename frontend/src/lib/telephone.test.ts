import { describe, expect, it } from "vitest"

import { chiffresNumeroLocal } from "./telephone"

describe("chiffresNumeroLocal", () => {
  it("garde un numéro local tel quel", () => {
    expect(chiffresNumeroLocal("677123456")).toBe("677123456")
  })

  it("retire tout ce qui n'est pas un chiffre", () => {
    expect(chiffresNumeroLocal("6 77-12.34 56")).toBe("677123456")
  })

  it("retire le préfixe +237 d'un collage", () => {
    expect(chiffresNumeroLocal("+237 677 12 34 56")).toBe("677123456")
    expect(chiffresNumeroLocal("+237677123456")).toBe("677123456")
  })

  it("retire le préfixe 237 ou 00237", () => {
    expect(chiffresNumeroLocal("237677123456")).toBe("677123456")
    expect(chiffresNumeroLocal("00237677123456")).toBe("677123456")
  })

  it("ne mange pas un début de numéro qui ressemble à l'indicatif", () => {
    expect(chiffresNumeroLocal("237")).toBe("237")
    expect(chiffresNumeroLocal("23767712")).toBe("23767712")
    // 9 chiffres exactement : c'est un numéro local, pas un indicatif suivi de rien.
    expect(chiffresNumeroLocal("237123456")).toBe("237123456")
  })

  it("tronque à 9 chiffres", () => {
    expect(chiffresNumeroLocal("67712345678")).toBe("677123456")
  })

  it("renvoie une chaîne vide pour une saisie sans chiffre", () => {
    expect(chiffresNumeroLocal("abc")).toBe("")
  })
})
