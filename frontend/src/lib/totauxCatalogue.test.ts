import { afterEach, describe, expect, it } from "vitest"

import { langueDeListe } from "./discipline"
import { definirLangue } from "./i18n"
import { paramsTotalCours, paramsTotalEpreuves } from "./totauxCatalogue"

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
