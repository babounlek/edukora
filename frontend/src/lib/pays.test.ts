import { afterEach, describe, expect, it } from "vitest"

import { definirLangue } from "@/lib/i18n"
import { libellePays, nomPays } from "./pays"

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("libellePays", () => {
  it("en français : le libellé du serveur, tel quel", () => {
    expect(libellePays("CM", "Cameroun")).toBe("Cameroun")
    expect(libellePays("SN", "Sénégal")).toBe("Sénégal")
  })

  it("en anglais : le nom du pays en anglais", async () => {
    await definirLangue("en", { persister: false })
    expect(libellePays("CM", "Cameroun")).toBe("Cameroon")
    expect(libellePays("cm", "Cameroun")).toBe("Cameroon")
    expect(libellePays("CI", "Côte d'Ivoire")).toBe("Côte d’Ivoire")
    expect(libellePays("SN", "Sénégal")).toBe("Senegal")
  })

  it("en anglais : un code inconnu retombe sur le libellé du serveur", async () => {
    await definirLangue("en", { persister: false })
    expect(libellePays("ZZZ", "Pays inventé")).toBe("Pays inventé")
    expect(libellePays("", "Sans code")).toBe("Sans code")
  })
})

describe("nomPays", () => {
  const pays = [{ code: "CM", label: "Cameroun" }, { code: "SN", label: "Sénégal" }]

  it("retrouve le pays par son code d'URL (minuscule) et le nomme dans la langue courante", async () => {
    expect(nomPays(pays, "cm")).toBe("Cameroun")
    await definirLangue("en", { persister: false })
    expect(nomPays(pays, "cm")).toBe("Cameroon")
  })

  it("pays inconnu ou liste pas encore chargée : undefined", () => {
    expect(nomPays(pays, "xx")).toBeUndefined()
    expect(nomPays([], "cm")).toBeUndefined()
    expect(nomPays(pays, undefined)).toBeUndefined()
  })
})
