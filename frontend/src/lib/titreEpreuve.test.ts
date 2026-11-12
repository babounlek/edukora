import { describe, expect, it } from "vitest"

import { titreEpreuve } from "./titreEpreuve"

describe("titreEpreuve : le mot « corrigé » dans le titre d'une annale corrigée", () => {
  it("l'ajoute à une annale corrigée, dans la langue du contenu", () => {
    expect(titreEpreuve("Mathématiques BEPC 2026", "CORR", "fr")).toBe("Mathématiques BEPC 2026 - corrigé")
    expect(titreEpreuve("Physics GCE O Level 2023", "CORR", "en")).toBe("Physics GCE O Level 2023 - solutions")
  })

  it("ne répète pas le mot et ne touche pas aux autres types", () => {
    expect(titreEpreuve("Maths BEPC 2020 - Corrigé détaillé", "CORR", "fr")).toBe("Maths BEPC 2020 - Corrigé détaillé")
    expect(titreEpreuve("Fiche de révision", "FICHE", "fr")).toBe("Fiche de révision")
    expect(titreEpreuve("Sujet", null, "fr")).toBe("Sujet")
  })
})
