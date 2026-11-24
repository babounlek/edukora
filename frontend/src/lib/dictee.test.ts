import { describe, expect, it } from "vitest"

import { ajouterALaSuite } from "./dictee"

describe("ajouterALaSuite", () => {
  it("met le texte dicté à la suite, avec une espace, sans doublon d'espaces", () => {
    expect(ajouterALaSuite("", "la démocratie")).toBe("la démocratie")
    expect(ajouterALaSuite("Définition :", " le pouvoir du peuple ")).toBe("Définition : le pouvoir du peuple")
    expect(ajouterALaSuite("Ligne\n", "suite")).toBe("Ligne\nsuite")
  })

  it("ne change rien quand rien n'a été dicté", () => {
    expect(ajouterALaSuite("déjà écrit", "   ")).toBe("déjà écrit")
  })
})
