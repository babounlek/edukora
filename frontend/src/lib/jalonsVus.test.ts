import { beforeEach, describe, expect, it } from "vitest"

import { marquerJalonsVus, nouveauxJalons } from "./jalonsVus"

describe("jalons déjà montrés sur l'appareil", () => {
  beforeEach(() => localStorage.clear())

  it("fête les premiers jalons d'un élève qui débute, une seule fois", () => {
    expect(nouveauxJalons(7, ["premier_quiz", "sans_faute_1"])).toEqual(["premier_quiz", "sans_faute_1"])
    expect(nouveauxJalons(7, ["premier_quiz", "sans_faute_1"])).toEqual([])
  })

  it("ne fête ensuite que ce qui vient d'être franchi", () => {
    nouveauxJalons(7, ["premier_quiz"])
    expect(nouveauxJalons(7, ["premier_quiz", "bonnes_10"])).toEqual(["bonnes_10"])
  })

  it("ne fête pas en rafale les jalons d'un compte ancien sur un nouvel appareil", () => {
    expect(nouveauxJalons(7, ["premier_quiz", "bonnes_10", "bonnes_50", "serie_3"])).toEqual([])
    // Mais ce qui arrive après est bien une nouveauté.
    expect(nouveauxJalons(7, ["premier_quiz", "bonnes_10", "bonnes_50", "serie_3", "serie_7"])).toEqual(["serie_7"])
  })

  it("un jalon déjà vu dans « Ma progression » n'est plus fêté", () => {
    nouveauxJalons(7, ["premier_quiz"])
    marquerJalonsVus(7, ["premier_quiz", "cartes_10"])
    expect(nouveauxJalons(7, ["premier_quiz", "cartes_10"])).toEqual([])
  })

  it("chaque enfant du compte a sa mémoire", () => {
    nouveauxJalons(7, ["premier_quiz"])
    expect(nouveauxJalons(8, ["premier_quiz"])).toEqual(["premier_quiz"])
  })
})
