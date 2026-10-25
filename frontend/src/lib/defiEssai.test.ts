import { beforeEach, describe, expect, it } from "vitest"

import { comparerDefi, lireDefiDepuis, lireDefiMemorise, memoriserDefi, parametresDefi } from "./defiEssai"

beforeEach(() => sessionStorage.clear())

describe("defiEssai", () => {
  it("met le score à battre dans le lien et le relit", () => {
    const params = parametresDefi(4, 5)
    expect(params).toEqual({ defi: "4-5" })
    expect(lireDefiDepuis(`defi=${params.defi}&ref=ABC`)).toEqual({ reussies: 4, total: 5 })
  })

  it("ignore un défi invraisemblable : le lien vient de n'importe qui", () => {
    for (const valeur of ["", "abc", "6-5", "3-0", "3-99", "-1-5", "3-5-1", "3.5-5"]) {
      expect(lireDefiDepuis(`defi=${valeur}`)).toBeNull()
    }
    expect(lireDefiDepuis("")).toBeNull()
  })

  it("garde le défi le temps de la visite, et l'efface", () => {
    memoriserDefi({ reussies: 3, total: 5 })
    expect(lireDefiMemorise()).toEqual({ reussies: 3, total: 5 })
    memoriserDefi(null)
    expect(lireDefiMemorise()).toBeNull()
  })

  it("compare en proportion, pas en nombre brut", () => {
    expect(comparerDefi({ reussies: 3, total: 5 }, 4, 5)).toBe("gagne")
    expect(comparerDefi({ reussies: 3, total: 5 }, 3, 5)).toBe("egalite")
    expect(comparerDefi({ reussies: 3, total: 5 }, 2, 5)).toBe("perdu")
    expect(comparerDefi({ reussies: 3, total: 5 }, 6, 10)).toBe("egalite")
    expect(comparerDefi({ reussies: 3, total: 5 }, 7, 10)).toBe("gagne")
  })
})
