import { afterEach, describe, expect, it } from "vitest"

import { langueDeListe } from "./discipline"
import { definirLangue } from "./i18n"
import { cursusDesTotaux, paramsTotalCours, paramsTotalEpreuves } from "./totauxCatalogue"

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("totaux annoncés par les puces", () => {
  it("épreuves et cours se comptent dans le même périmètre (pays + langue)", () => {
    for (const langue of ["fr", "en", undefined] as const) {
      expect(paramsTotalCours("cm", langue)).toEqual(paramsTotalEpreuves("cm", langue))
    }
  })

  it("suivent la langue de l'interface, jamais toutes les langues par défaut", async () => {
    await definirLangue("en", { persister: false })
    expect(paramsTotalCours("cm", langueDeListe("", false))).toEqual({ country: "cm", langue: "en" })
    expect(paramsTotalEpreuves("cm", langueDeListe("", false))).toEqual({ country: "cm", langue: "en" })
  })

  it("« Toutes les langues » lève le filtre", () => {
    expect(paramsTotalCours("cm", langueDeListe("", true)).langue).toBeUndefined()
    expect(paramsTotalEpreuves("cm", langueDeListe("", true)).langue).toBeUndefined()
  })
})

describe("totaux d'un élève abonné (test élève Gogo : 512 épreuves annoncées pour une liste de 96)", () => {
  it("sans examen à compter, rien ne change : pays + langue", () => {
    expect(paramsTotalEpreuves("cm", "en")).toEqual({ country: "cm", langue: "en" })
    expect(paramsTotalEpreuves("cm", "en", null)).toEqual({ country: "cm", langue: "en" })
    expect(paramsTotalCours("cm", "en", null)).toEqual({ country: "cm", langue: "en" })
  })

  it("avec un examen, épreuves et cours se comptent dans le même périmètre", () => {
    expect(paramsTotalEpreuves("cm", "en", 1414)).toEqual({ country: "cm", langue: "en", cursus: 1414 })
    expect(paramsTotalCours("cm", "en", 1414)).toEqual(paramsTotalEpreuves("cm", "en", 1414))
  })

  it("ne compte l'examen que pour un abonné qui regarde son propre examen", () => {
    expect(cursusDesTotaux(1414, 1414)).toBe(1414)
    expect(cursusDesTotaux(1414, 1416)).toBeNull()
    expect(cursusDesTotaux(1414, undefined)).toBeNull()
    expect(cursusDesTotaux(null, 1414)).toBeNull()
  })
})
