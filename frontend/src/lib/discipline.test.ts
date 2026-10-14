import { afterEach, describe, expect, it } from "vitest"

import { definirLangue } from "@/lib/i18n"
import { subjectIcon } from "@/lib/subjectIcon"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { codeVisuel, EQUIVALENTS_GCE, langueDeListe } from "./discipline"

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("matières jumelles du GCE", () => {
  it("chaque matière GCE reprend l'icône et la couleur de sa jumelle francophone", () => {
    expect(subjectIcon("GCE_MATHS")).toBe(subjectIcon("MATHS"))
    expect(subjectIcon("GCE_PHYSICS")).toBe(subjectIcon("PHYSIQUE"))
    expect(couleurMatiere("GCE_CHEMISTRY")).toBe(couleurMatiere("CHIMIE"))
    expect(couleurMatiere("GCE_BIOLOGY")).toBe(couleurMatiere("SVT"))
  })

  it("une matière sans jumelle garde son code ; une inconnue garde le visuel par défaut", () => {
    expect(codeVisuel("MATHS")).toBe("MATHS")
    expect(codeVisuel("GCE_RELIGION")).toBe("GCE_RELIGION")
    expect(couleurMatiere("GCE_RELIGION")).toBe(couleurMatiere("INCONNUE"))
  })

  it("toutes les jumelles pointent vers un code que le frontend sait dessiner", () => {
    for (const [gce, fr] of Object.entries(EQUIVALENTS_GCE)) {
      expect(fr, gce).toMatch(/^[A-Z_]+$/)
    }
  })
})

describe("langueDeListe", () => {
  it("suit la langue de l'interface sans examen choisi", async () => {
    expect(langueDeListe("", false)).toBe("fr")
    await definirLangue("en", { persister: false })
    expect(langueDeListe("", false)).toBe("en")
  })

  it("ne filtre pas quand un examen est choisi ou que toutes les langues sont demandées", () => {
    expect(langueDeListe("12", false)).toBeUndefined()
    expect(langueDeListe("", true)).toBeUndefined()
  })
})
